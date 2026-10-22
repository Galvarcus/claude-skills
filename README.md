# Claude Skills Repository Toolkit

A small, dependency-free toolkit for a repository whose canonical skills live in `skills/<skill-name>/SKILL.md`.

## Included skills

These skills are my own and hold my personal preferences. Use, edit, or delete them in your copy.

| Skill | Purpose |
| --- | --- |
| [`code-comments`](skills/code-comments/SKILL.md) | Rules for code comments in any language. Keeps comments short, because Claude tends to write long ones. |
| [`github-markdown-style`](skills/github-markdown-style/SKILL.md) | Style guide for GitHub Markdown files such as README.md, based on _The Elements of Style_ by Strunk and White. |
| [`handoff`](skills/handoff/SKILL.md) | Writes a handoff file that a fresh agent can resume from, by hand or from a hook when context or usage limits reach 90%. |
| [`token-efficient-execution`](skills/token-efficient-execution/SKILL.md) | Rules for multi-step work that use the fewest tokens, tool calls, and words that still give a correct, verified result. |
| [`vim9script-plugin`](skills/vim9script-plugin/SKILL.md) | My conventions for Vim9script plugins: naming, layout, comments, logging, and tests. |

### Token savings

A benchmark compared runs with and without `token-efficient-execution` on seven tasks for a Vim9script plugin, with three runs of each. Both configurations loaded the other three skills. Token counts are approximate means per run.

| Task | Tokens with | Tokens without | Saved |
| --- | --- | --- | --- |
| Design plan | 360k | 680k | 47% |
| Fix three bugs | 460k | 560k | 18% |
| Add a rename command | 710k | 1,020k | 30% |
| Add project scope | 730k | 1,010k | 28% |
| Add line tracking | 1,130k | 1,600k | 29% |
| Code review | 850k | 1,090k | 22% |
| Final analysis | 720k | 990k | 28% |
| All tasks | 14.9M total | 20.9M total | 29% |

The checks passed at 96.7% with the skill and 94.8% without it. See [the Waypoint benchmark plan](tests/benchmark/waypoint-plan.md) for the method and full results.

### Automatic handoffs

The `handoff` skill can run on its own when the context window, the 5-hour usage limit, or the weekly usage limit reaches 90%. Hooks cannot see usage, but the status line can, so the setup has two parts. Install the skill with `python3 tools/install.py handoff`, then:

1. Pass the status line input to the snapshot script. Add this line to your status line script, after it reads its input:

   ```bash
   echo "$input" | bash ~/.claude/skills/handoff/scripts/save-usage.sh 2>/dev/null
   ```

2. Run the check script as a hook in `~/.claude/settings.json`:

   ```json
   "hooks": {
     "UserPromptSubmit": [
       {"hooks": [{"type": "command", "command": "bash ~/.claude/skills/handoff/scripts/handoff-check.sh"}]}
     ],
     "PostToolUse": [
       {"matcher": "*", "hooks": [{"type": "command", "command": "bash ~/.claude/skills/handoff/scripts/handoff-check.sh"}]}
     ]
   }
   ```

Set `HANDOFF_THRESHOLD` to change the 90% threshold. The scripts need `jq`. Usage limits appear only for Pro and Max plans.

The rest of this document covers the repository toolkit.

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
