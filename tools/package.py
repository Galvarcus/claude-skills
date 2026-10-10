#!/usr/bin/env python3
"""Package one or all skills into dist/<skill>.zip."""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
DIST_DIR = ROOT / "dist"
EXCLUDED_PARTS = {".git", "__pycache__", ".DS_Store"}


def package(skill_dir: Path) -> Path:
    output = DIST_DIR / f"{skill_dir.name}.zip"
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            archive.write(path, Path(skill_dir.name) / path.relative_to(skill_dir))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="package every skill")
    selection.add_argument("skill", nargs="?", help="skill directory name under skills/")
    args = parser.parse_args()

    if args.all:
        dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))
    else:
        candidate = (SKILLS_DIR / args.skill).resolve()
        if candidate.parent != SKILLS_DIR.resolve() or not candidate.is_dir():
            parser.error(f"unknown skill: {args.skill}")
        dirs = [candidate]

    if not dirs:
        print("ERROR: no skills found", file=sys.stderr)
        return 1

    for skill_dir in dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            print(f"ERROR: {skill_dir.name}: missing SKILL.md", file=sys.stderr)
            return 1
    for skill_dir in dirs:
        print(package(skill_dir).relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
