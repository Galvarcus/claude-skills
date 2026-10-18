# Skill benchmark

Task evals that compare each skill against a baseline without it, in the format of skill-creator's benchmark mode. Each eval gives Claude a realistic task in a fixture directory. A grader then checks the result against hidden tests, the diff, the final reply, and, for `token-efficient-execution`, the run's transcript.

The runs themselves need Claude Code with the skill-creator plugin, because each run is a subagent. The scripts here only prepare the fixtures and grade the results.

## Layout

| Path | Purpose |
| --- | --- |
| `evals.json` | Every eval: skill, prompt, fixture, grader, and whether it is active or retired |
| `fixtures/` | Hand-written fixtures, one directory per eval |
| `make_fixtures.py` | Generates the large fixtures that are not committed: the ledger repo, a 6,000-line build log, and a generated bundle |
| `make_ledger.py` | Generates the ledger repo: a 45-file Python project with a 20,000-line log, a vendored library, a stale `build/` copy, and a 20-second integration test |
| `seed.py` | Copies fixtures into a fresh run workspace under `ws/` |
| `grade.py` | Grades every eval except the two ledger evals |
| `grade_ledger.py` | Grades the ledger evals, `fix-issue-214` and `rename-date-format` |

`ws/` and the generated fixtures are in `.gitignore`.

## Run a benchmark

1. Generate the fixtures and seed an iteration:

   ```sh
   cd tests/benchmark
   python3 make_fixtures.py
   python3 seed.py iteration-1 --skill token-efficient-execution --runs 3
   ```

2. Ask Claude Code to run each seeded `outputs/` directory as a subagent task with the eval's prompt. A `with_skill` run reads the skill's `SKILL.md` first. A `without_skill` run must not use the Skill tool or read any `SKILL.md`. Each run writes its final reply to `response.md`.

3. For each finished run, save the subagent's duration as `timing.json` in its `run-<n>/` directory. For transcript checks, also save the path of the subagent's JSONL transcript as `transcript_path.txt` in the same directory.

4. Grade the iteration:

   ```sh
   python3 grade.py iteration-1
   python3 grade_ledger.py iteration-1
   ```

5. Aggregate and review with skill-creator's scripts, from its `skills/skill-creator` directory:

   ```sh
   python3 -m scripts.aggregate_benchmark <ws>/<skill>/iteration-1 --skill-name <skill>
   python3 eval-viewer/generate_review.py <ws>/<skill>/iteration-1 \
     --skill-name <skill> --benchmark <ws>/<skill>/iteration-1/benchmark.json \
     --static review.html
   ```

## Grading notes

- The transcript JSONL logs each assistant message more than once with the same tool call ID. The graders deduplicate by ID. Without that step, every call counts twice and every file looks reread.
- `grade_ledger.py` reports tokens as the sum of input and output tokens for every assistant turn. That figure tracks cost better than the subagent's final context size.
- A run that never wrote `transcript_path.txt` is skipped by `grade_ledger.py` and fails the transcript checks in `grade.py`.

## Results, October 2026

One run per configuration unless noted.

| Skill | Pass rate with skill | Pass rate without | Notes |
| --- | --- | --- | --- |
| `vim9script-plugin` | 100% | 62% | Without the skill, runs leave out the header, the load guard, and named constants. |
| `code-comments` | 100% | 66% | Without the skill, runs leave out `REFERENCE:` lines and block identifiers. |
| `github-markdown-style` | 100% | 93% | Only `tighten-readme` separates the configurations. |
| `token-efficient-execution` | 95.5% ± 4.9 | 88.5% ± 4.7 | Ledger evals, 3 runs each. With the skill, runs take 38 s ± 5 instead of 54 s ± 18 and process 228k ± 5k tokens instead of 249k ± 59k. |

Replies on `rename-date-format` run 140 to 215 words with or without the skill, against a 120-word check. A rule to shorten multi-file summaries did not shorten them, so that rule was reverted.
