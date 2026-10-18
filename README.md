# Claude Skills Repository Toolkit

A small, dependency-free toolkit for a repository whose canonical skills live in `skills/<skill-name>/SKILL.md`.

## Included Skills

These skills are my own and contain my personal preferences. Feel free to use, edit, or delete them from your copy.
* code-comments - Generic rules for code comments. Claude likes to be wordy.
* github-markdown-style - Style guide skill for creating GH markdown files, such as README.md. Based on _The Elements of Style_ by Strunk & White.
* vim9script-plugin - very personal preferences for vim9script plugins.
* token-efficient-execution - My most prized skill. I have seen a 20-50% reduction in token usage with this skill, tested in Opus 5.5 and Sonnet 5.5 with Pro sub. Mileage may vary.

The remainder of this document details project usage.

## Repository layout

```text
claude-skills/
├── skills/
│   └── example-skill/
│       ├── SKILL.md
│       ├── references/       # optional
│       ├── scripts/          # optional
│       └── assets/           # optional
├── tests/
│   └── fixtures/
├── tools/
│   ├── validate.py
│   ├── test.py
│   ├── package.py
│   ├── install.py
│   └── new-skill.py
├── templates/
│   └── SKILL.md
└── .github/workflows/skills.yml
```

The toolkit intentionally uses Python's standard library only. Python 3.10+ is recommended.

## Quick start

From the repository root:

```sh
python3 tools/validate.py
python3 tools/test.py
python3 tools/package.py --all
python3 tools/install.py --all --target personal
```

Install one skill to the current repository instead:

```sh
python3 tools/install.py markdown-style --target project
```

The personal target installs to `~/.claude/skills/`; the project target installs to `./.claude/skills/` under the current working directory. The installer refuses to overwrite an existing skill unless `--force` is supplied.

Create a skill scaffold:

```sh
python3 tools/new-skill.py markdown-style
```

This creates `skills/markdown-style/SKILL.md`. Edit the generated placeholder before committing.

## Skill format

Every skill is a directory directly beneath `skills/`, and must contain a case-sensitive `SKILL.md` file. The frontmatter must include `name` and `description`. The `name` must match the directory name and use lowercase letters, digits, and hyphens; it must not contain `claude` or `anthropic`.

The validator intentionally supports a conservative subset of YAML frontmatter: plain single-line `name:` and `description:` fields. This avoids adding a YAML dependency. Keep these two fields single-line; Markdown body content may be multiline.

## Validation and testing

- `validate.py` validates the catalog and each skill's required metadata, directory naming, and local Markdown links. It skips links inside code blocks and code spans, because those are examples.
- `test.py` runs the validator and Python unit tests.
- `tests/test_skills.py` includes regression checks for discovery metadata, expected fixtures, and packaging output.
- `tests/cases.json` is a lightweight behavior-evaluation plan. It records positive and negative trigger prompts for later manual or model-based evaluation; the included harness does not claim to execute Claude or score model behavior.
- `tests/benchmark/` holds task evals that compare each skill with a baseline that runs without it. Claude Code runs the evals as subagents, and the graders score the results. See [the benchmark README](tests/benchmark/README.md).

Run all checks locally:

```sh
python3 tools/test.py
```

## Packaging

```sh
python3 tools/package.py markdown-style
python3 tools/package.py --all
```

Archives are written to `dist/<skill-name>.zip`. Each archive contains the skill directory itself (for example `markdown-style/SKILL.md`), suitable for uploading as a custom Skill where ZIP upload is supported. `dist/` is generated output and should normally be ignored by Git.

## Versioning policy

Use Semantic Versioning per skill, recorded in Git tags rather than custom frontmatter:

- `skill/<name>/vMAJOR.MINOR.PATCH` — immutable release tag, e.g. `skill/markdown-style/v1.2.0`
- **MAJOR**: incompatible change to the skill's expected inputs, output contract, or workflow.
- **MINOR**: backward-compatible capability or workflow addition.
- **PATCH**: clarifications, typo fixes, or behavior-preserving corrections.

Example:

```sh
git tag -a skill/markdown-style/v1.0.0 -m "markdown-style 1.0.0"
git push origin skill/markdown-style/v1.0.0
```

Do not reuse or move published tags. Keep unreleased work on normal branches; release each skill independently. Repository-wide tooling changes do not require a skill version bump unless they change a skill's behavior or package contents.

## GitHub Actions

The workflow runs validation and tests on pushes and pull requests. It also builds ZIP packages and uploads them as a workflow artifact. It does not publish releases or push tags automatically.

## Security and trust

Review skill instructions and bundled scripts before installing. Skills are instructions that can influence agent behavior, and scripts may be executable. Do not automatically execute a skill's scripts during installation.

## Portability note

`SKILL.md` and its supporting files are portable. Installation paths and upload/distribution workflows differ by Claude surface. This toolkit installs only for Claude Code; package ZIPs for supported upload surfaces.
