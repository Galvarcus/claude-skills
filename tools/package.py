#!/usr/bin/env python3
"""Build fresh ZIP archives from skills/<name>/ directories."""
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
    """Replace dist/<skill>.zip with exactly the current skill contents."""
    output = DIST_DIR / f"{skill_dir.name}.zip"
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Explicitly remove the old archive before rebuilding it.
    output.unlink(missing_ok=True)

    files = [
        path for path in sorted(skill_dir.rglob("*"))
        if path.is_file() and not any(part in EXCLUDED_PARTS for part in path.parts)
    ]
    if not files:
        raise ValueError(f"{skill_dir.name}: no files to package")

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path(skill_dir.name) / path.relative_to(skill_dir))

    # Verify archive integrity before reporting success.
    with zipfile.ZipFile(output, "r") as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            output.unlink(missing_ok=True)
            raise zipfile.BadZipFile(f"archive verification failed at {bad_member}")

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="package every skill")
    group.add_argument("skill", nargs="?", help="skill directory name under skills/")
    args = parser.parse_args()

    if not SKILLS_DIR.is_dir():
        print(f"ERROR: skills directory not found: {SKILLS_DIR}", file=sys.stderr)
        return 1

    if args.all:
        skill_dirs = sorted(
            path for path in SKILLS_DIR.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        )
    else:
        candidate = (SKILLS_DIR / args.skill).resolve()
        if candidate.parent != SKILLS_DIR.resolve() or not candidate.is_dir():
            parser.error(f"unknown skill: {args.skill}")
        skill_dirs = [candidate]

    if not skill_dirs:
        print("ERROR: no skills found", file=sys.stderr)
        return 1

    for skill_dir in skill_dirs:
        if not (skill_dir / "SKILL.md").is_file():
            print(f"ERROR: {skill_dir.name}: missing SKILL.md", file=sys.stderr)
            return 1

    try:
        for skill_dir in skill_dirs:
            output = package(skill_dir)
            print(f"Packaged {skill_dir.name}: {output} ({output.stat().st_size} bytes)")
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
