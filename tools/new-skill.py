#!/usr/bin/env python3
"""Create a new skill directory from templates/SKILL.md."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="lowercase kebab-case skill name")
    parser.add_argument("--title", help="human-readable title; defaults to Title Case")
    args = parser.parse_args()
    if not NAME_RE.fullmatch(args.name) or len(args.name) > 64 or "claude" in args.name or "anthropic" in args.name:
        parser.error("name must be lowercase kebab-case, <=64 chars, and must not contain 'claude' or 'anthropic'")
    target = ROOT / "skills" / args.name
    if target.exists():
        parser.error(f"target already exists: {target}")
    title = args.title or " ".join(part.capitalize() for part in args.name.split("-"))
    template = (ROOT / "templates" / "SKILL.md").read_text(encoding="utf-8")
    template = template.replace("your-skill-name", args.name).replace("Your Skill Title", title)
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(template, encoding="utf-8")
    print(f"Created {target.relative_to(ROOT)}/SKILL.md; edit the placeholder content before validating.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
