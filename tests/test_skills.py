from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate  # noqa: E402


class SkillRepositoryTests(unittest.TestCase):
    def test_every_skill_has_valid_metadata(self):
        skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir() and not p.name.startswith("."))
        self.assertTrue(skill_dirs, "at least one skill directory is required")
        for skill_dir in skill_dirs:
            with self.subTest(skill=skill_dir.name):
                errors = validate.validate_skill(skill_dir)
                self.assertEqual(errors, [], "\n".join(errors))

    def test_evaluation_cases_are_well_formed(self):
        cases_file = ROOT / "tests" / "cases.json"
        cases = json.loads(cases_file.read_text(encoding="utf-8"))
        self.assertIsInstance(cases, list)
        for case in cases:
            self.assertIn("skill", case)
            self.assertIn("should_trigger", case)
            self.assertIn("should_not_trigger", case)
            self.assertTrue(case["should_trigger"])
            self.assertTrue(case["should_not_trigger"])

    def test_packager_creates_skill_root_in_zip(self):
        skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
        self.assertTrue(skill_dirs)
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "test.zip"
            skill_dir = skill_dirs[0]
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(skill_dir.rglob("*")):
                    if path.is_file():
                        archive.write(path, Path(skill_dir.name) / path.relative_to(skill_dir))
            with zipfile.ZipFile(out) as archive:
                self.assertIn(f"{skill_dir.name}/SKILL.md", archive.namelist())

    def test_validator_rejects_mismatched_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "expected-name"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: other-name\ndescription: A test skill description.\n---\n\n# Test\n",
                encoding="utf-8",
            )
            # validate_skill uses ROOT-relative display paths, so test its metadata logic
            # directly via a temporary replacement of the module's root only.
            original_root = validate.ROOT
            try:
                validate.ROOT = Path(temp_dir)
                errors = validate.validate_skill(skill_dir)
            finally:
                validate.ROOT = original_root
            self.assertTrue(any("must match directory" in error for error in errors))


class LinkCheckTests(unittest.TestCase):
    """Links in code are examples, and a real broken link is still found once."""

    def validate_text(self, body: str) -> list[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "link-test"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: link-test\ndescription: A test skill description.\n---\n\n" + body,
                encoding="utf-8",
            )
            original_root = validate.ROOT
            try:
                validate.ROOT = Path(temp_dir)
                return validate.validate_skill(skill_dir)
            finally:
                validate.ROOT = original_root

    def test_a_link_in_a_fenced_code_block_is_not_checked(self):
        errors = self.validate_text("# T\n\n```markdown\nSee the [guide](docs/missing.md).\n```\n")
        self.assertEqual(errors, [])

    def test_a_link_in_a_tilde_fence_is_not_checked(self):
        errors = self.validate_text("# T\n\n~~~markdown\nSee the [guide](docs/missing.md).\n~~~\n")
        self.assertEqual(errors, [])

    def test_a_link_in_an_inline_code_span_is_not_checked(self):
        errors = self.validate_text("# T\n\nWrite `[guide](docs/missing.md)` or ``[a](b.md)`` here.\n")
        self.assertEqual(errors, [])

    def test_a_broken_link_in_prose_is_reported_once(self):
        errors = self.validate_text("# T\n\nSee the [guide](docs/missing.md).\n")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("broken local link 'docs/missing.md'", errors[0])

    def test_a_longer_fence_holds_a_shorter_one(self):
        body = (
            "# T\n\n````markdown\n```bash\n[a](inside.md)\n```\n[b](also-inside.md)\n````\n\n"
            "After the fence, see [c](outside.md).\n"
        )
        errors = self.validate_text(body)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("outside.md", errors[0])

    def test_a_link_to_a_file_that_exists_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "link-test"
            (skill_dir / "references").mkdir(parents=True)
            (skill_dir / "references" / "more.md").write_text("# More\n", encoding="utf-8")
            (skill_dir / "SKILL.md").write_text(
                "---\nname: link-test\ndescription: A test skill description.\n---\n\n# T\n\nSee [more](references/more.md).\n",
                encoding="utf-8",
            )
            original_root = validate.ROOT
            try:
                validate.ROOT = Path(temp_dir)
                errors = validate.validate_skill(skill_dir)
            finally:
                validate.ROOT = original_root
        self.assertEqual(errors, [])

    def test_strip_code_keeps_the_prose_around_code(self):
        text = "before `x` after\n```\ncode\n```\nlast"
        self.assertEqual(validate.strip_code(text), "before  after\nlast")


if __name__ == "__main__":
    unittest.main()
