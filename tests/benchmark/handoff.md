# Waypoint benchmark handoff

Done as of 2026-10-21. All 42 runs are graded, and the results are in the Results section of the plan. This file is kept as a record. The plan is [waypoint-plan.md](waypoint-plan.md).

## State

| Stage | Eval | Runs | Graded |
| --- | --- | --- | --- |
| 1 Design | 10 | 6 of 6 | Yes |
| 2 Debug | 11 | 6 of 6 | Yes |
| 3a Rename | 12 | 6 of 6 | Yes |
| 3b Project scope | 13 | 6 of 6 | Yes |
| 3c Line tracking | 14 | 6 of 6 | No |
| 4 Review | 15 | 0 of 6, seeded | No |
| 5 Analysis | 16 | 0 of 6, seeded | No |

Workspace: `ws/token-efficient-execution/full/`. Runs map to transcripts in `agents.tsv`. `rec.py <agent_id>=<duration_ms>` writes `transcript_path.txt` and `timing.json` for a finished run.

## Results so far

| Stage | Checks with skill | Checks without | Tokens with | Tokens without |
| --- | --- | --- | --- | --- |
| 1 Design | 13, 13, 13 of 15 | 13, 13, 13 of 15 | 298k, 493k, 298k | 883k, 573k, 594k |
| 2 Debug | 21, 22, 22 of 22 | 21, 21, 19 of 22 | 385k, 493k, 486k | 420k, 635k, 614k |
| 3a Rename | 23, 23, 23 of 23 | 23, 23, 23 of 23 | 649k, 674k, 819k | 937k, 1,143k, 992k |
| 3b Scope | 22, 23, 23 of 23 | 23, 23, 23 of 23 | 888k, 615k, 682k | 1,081k, 912k, 1,042k |

Stage 1 fails only the word limits, in every run: design docs run 1,900 to 2,900 words against 1,500, and replies 250 to 390 against 120. Report the actual counts. Don't change the thresholds mid-run.

## Next steps

1. Grade stage 3c: `python3 grade_waypoint.py full`. Grading is slow while runs are active, so run it in the background.
2. Launch stages 4 and 5, 12 runs. Pass each run's `prompt.txt` verbatim as the subagent prompt:
   `ws/token-efficient-execution/full/eval-15-code-review/{with_tee,without_tee}/run-{1,2,3}/prompt.txt` and the same for `eval-16-final-analysis`.
   Launch in waves of 6 to limit the loss if a usage limit hits.
3. As each run finishes, append `<agent_id><TAB><eval-dir>/<config>/run-<n>` to `agents.tsv`, then run `rec.py <agent_id>=<duration_ms>` with the duration from the completion notification.
4. Grade, aggregate, and build the viewer. From skill-creator's `skills/skill-creator` folder:
   `python3 -m scripts.aggregate_benchmark <ws>/full --skill-name token-efficient-execution`, then `generate_review.py ... --static review-full.html`.
5. For stage 4 precision, run skill-creator's grader agent, or review by hand. Stage 4 recall alone did not separate the configurations in the pilot.
6. Write up the results against the success criteria in the plan: at least 15% fewer tokens per passing run, and a pass rate within 5 points.

## Things to know

- **Restart failed runs.** If a usage limit cuts runs off, delete the eval folder, reseed with `python3 seed.py full --skill token-efficient-execution --ids <id> --runs 3`, and relaunch. Never resume a run with SendMessage, because its timing and token counts would no longer be comparable.
- **Git stash.** Early stage-2 runs ran `git stash` and swept up uncommitted repo edits. The edits were reapplied with `git stash apply`. The entry `stash@{0}` is still a backup, and you can drop it once you've checked the files. Every Waypoint run's `outputs/` is now its own git repository, so this can't recur.
- **Grader changes during the run,** applied to every run equally:
  - The global-read check allows one runtime setting read in one place per script, as the vim9script-plugin skill does.
  - The log-dump check counts only commands that print the log.
- **Uncommitted work:** `.gitignore`, `README.md`, `evals.json`, `make_fixtures.py`, and `seed.py` are modified. `grade_waypoint.py`, `waypoint/`, `waypoint-plan.md`, and this file are new.
- **Validation:** `python3 grade_waypoint.py x --validate` must pass after any grader change.
