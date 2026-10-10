#!/usr/bin/env python3
"""Validate skills/<name>/SKILL.md using only the Python standard library."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
MAX_NAME = 64
MAX_DESCRIPTION = 1024


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def strip_code(text: str) -> str:
    """Return text without fenced code blocks and inline code spans.

    A link inside code is an example, not a reference, so link checks skip it.
    """
    kept: list[str] = []
    fence = ""
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if fence:
            # A closing fence repeats the opening character, at least as many
            # times, and holds nothing else. A shorter fence inside is text.
            if (match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence)
                    and line.strip().strip(fence[0]) == ""):
                fence = ""
            continue
        if match:
            fence = match.group(1)
            continue
        kept.append(line)
    return INLINE_CODE_RE.sub("", "\n".join(kept))


def parse_frontmatter(path: Path, errors: list[str]) -> tuple[dict[str, str], str]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        fail(errors, f"{path.relative_to(ROOT)}: cannot read UTF-8 text: {exc}")
        return {}, ""
    if not content.startswith("---\n"):
        fail(errors, f"{path.relative_to(ROOT)}: frontmatter must start on line 1 with ---")
        return {}, content

    end = content.find("\n---\n", 4)
    if end < 0:
        fail(errors, f"{path.relative_to(ROOT)}: missing closing frontmatter delimiter")
        return {}, content

    raw = content[4:end]
    fields: dict[str, str] = {}
    for line_no, line in enumerate(raw.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if not match:
            fail(errors, f"{path.relative_to(ROOT)}:{line_no}: unsupported frontmatter line: {line!r}")
            continue
        key, value = match.groups()
        if key in fields:
            fail(errors, f"{path.relative_to(ROOT)}:{line_no}: duplicate frontmatter key {key!r}")
        fields[key] = value.strip("\"'")
    return fields, content[end + 5:]


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_name = skill_dir.name
    skill_file = skill_dir / "SKILL.md"

    if not NAME_RE.fullmatch(skill_name):
        fail(errors, f"{skill_dir.relative_to(ROOT)}: directory name must be lowercase kebab-case")
    if not skill_file.is_file():
        fail(errors, f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
        return errors

    fields, body = parse_frontmatter(skill_file, errors)
    name = fields.get("name", "")
    description = fields.get("description", "")

    if not name:
        fail(errors, f"{skill_file.relative_to(ROOT)}: missing non-empty 'name' field")
    elif len(name) > MAX_NAME or not NAME_RE.fullmatch(name):
        fail(errors, f"{skill_file.relative_to(ROOT)}: name must be <= {MAX_NAME} chars, lowercase letters, digits, and hyphens")
    elif name != skill_name:
        fail(errors, f"{skill_file.relative_to(ROOT)}: name {name!r} must match directory {skill_name!r}")
    if "claude" in name or "anthropic" in name:
        fail(errors, f"{skill_file.relative_to(ROOT)}: name cannot contain reserved word 'claude' or 'anthropic'")

    if not description:
        fail(errors, f"{skill_file.relative_to(ROOT)}: missing non-empty 'description' field")
    elif len(description) > MAX_DESCRIPTION:
        fail(errors, f"{skill_file.relative_to(ROOT)}: description exceeds {MAX_DESCRIPTION} characters")
    if "<" in description or ">" in description:
        fail(errors, f"{skill_file.relative_to(ROOT)}: description must not contain XML angle brackets")
    if not body.strip():
        fail(errors, f"{skill_file.relative_to(ROOT)}: Markdown body is empty")

    # Check local Markdown links in SKILL.md and supporting Markdown files.
    for md in sorted({skill_file, *skill_dir.rglob("*.md")}):
        if not md.is_file():
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            fail(errors, f"{md.relative_to(ROOT)}: cannot read UTF-8 text: {exc}")
            continue
        for target in LINK_RE.findall(strip_code(text)):
            target = target.strip()
            if not target or target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target_path = target.split("#", 1)[0].split("?", 1)[0]
            if not target_path:
                continue
            resolved = (md.parent / target_path).resolve()
            if not resolved.exists():
                fail(errors, f"{md.relative_to(ROOT)}: broken local link {target!r}")
    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print("ERROR: skills/ directory not found", file=sys.stderr)
        return 2
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skill_dirs:
        print("ERROR: no skill directories found under skills/", file=sys.stderr)
        return 2

    errors: list[str] = []
    for directory in skill_dirs:
        errors.extend(validate_skill(directory))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Validation failed: {len(errors)} error(s).")
        return 1

    print(f"Validation passed: {len(skill_dirs)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
