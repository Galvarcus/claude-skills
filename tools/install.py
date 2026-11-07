#!/usr/bin/env python3
"""Install skills and rules into Claude Code's personal or current-project directory."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
RULES_DIR = ROOT / "rules"


def place(source: Path, destination: Path, force: bool, dry_run: bool) -> None:
    """Copy one skill directory or rules file over its destination."""
    if dry_run:
        print(f"Would install {source.name} -> {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)
    print(f"Installed {source.name} -> {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="install every skill and every rules file")
    selection.add_argument("--rules", action="store_true", help="install every rules file and no skill")
    selection.add_argument("skill", nargs="?", help="skill directory name under skills/")
    parser.add_argument("--target", choices=("personal", "project"), default="personal",
                        help="personal: ~/.claude; project: ./.claude (default: personal)")
    parser.add_argument("--force", action="store_true", help="replace existing installed skills and rules")
    parser.add_argument("--dry-run", action="store_true", help="show actions without copying")
    args = parser.parse_args()

    claude_root = Path.home() / ".claude" if args.target == "personal" else Path.cwd() / ".claude"

    if args.rules:
        selected = []
    elif args.all:
        selected = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))
    else:
        candidate = (SKILLS_DIR / args.skill).resolve()
        if candidate.parent != SKILLS_DIR.resolve() or not candidate.is_dir():
            parser.error(f"unknown skill: {args.skill}")
        selected = [candidate]

    rules = []
    if args.all or args.rules:
        rules = sorted(RULES_DIR.glob("*.md")) if RULES_DIR.is_dir() else []
        if args.rules and not rules:
            print("ERROR: no rules files found under rules/", file=sys.stderr)
            return 1

    if not selected and not rules:
        print("ERROR: no skills found", file=sys.stderr)
        return 1

    for source in selected:
        if not (source / "SKILL.md").is_file():
            print(f"ERROR: {source.name}: missing SKILL.md", file=sys.stderr)
            return 1

    planned = [(source, claude_root / "skills" / source.name) for source in selected]
    planned += [(source, claude_root / "rules" / source.name) for source in rules]

    conflicts = [destination for _, destination in planned if destination.exists() and not args.force]
    if conflicts:
        for path in conflicts:
            print(f"ERROR: already exists: {path} (use --force to replace)", file=sys.stderr)
        return 1

    for source, destination in planned:
        place(source, destination, args.force, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
