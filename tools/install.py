#!/usr/bin/env python3
"""Install skills into Claude Code's personal or current-project directory."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="install every skill")
    selection.add_argument("skill", nargs="?", help="skill directory name under skills/")
    parser.add_argument("--target", choices=("personal", "project"), default="personal",
                        help="personal: ~/.claude/skills; project: ./.claude/skills (default: personal)")
    parser.add_argument("--force", action="store_true", help="replace existing installed skill directories")
    parser.add_argument("--dry-run", action="store_true", help="show actions without copying")
    args = parser.parse_args()

    if args.target == "personal":
        destination_root = Path.home() / ".claude" / "skills"
    else:
        destination_root = Path.cwd() / ".claude" / "skills"

    if args.all:
        selected = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))
    else:
        candidate = (SKILLS_DIR / args.skill).resolve()
        if candidate.parent != SKILLS_DIR.resolve() or not candidate.is_dir():
            parser.error(f"unknown skill: {args.skill}")
        selected = [candidate]

    if not selected:
        print("ERROR: no skills found", file=sys.stderr)
        return 1

    for source in selected:
        if not (source / "SKILL.md").is_file():
            print(f"ERROR: {source.name}: missing SKILL.md", file=sys.stderr)
            return 1

    conflicts = [destination_root / source.name for source in selected
                 if (destination_root / source.name).exists() and not args.force]
    if conflicts:
        for path in conflicts:
            print(f"ERROR: already exists: {path} (use --force to replace)", file=sys.stderr)
        return 1

    for source in selected:
        destination = destination_root / source.name
        if args.dry_run:
            print(f"Would install {source.name} -> {destination}")
            continue
        destination_root.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        print(f"Installed {source.name} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
