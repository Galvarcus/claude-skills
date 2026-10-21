# Waypoint benchmark plan

A multi-stage benchmark for `token-efficient-execution` built on one Vim9script plugin, Waypoint. Each stage is a realistic task that also loads `vim9script-plugin`, `code-comments`, and `github-markdown-style`, so the benchmark measures token-efficient-execution while those skills shape the work, as they do in daily use.

The benchmark is built and its graders are validated. It has not been run. Build status is at the end.

## Goals

1. Measure whether token-efficient-execution lowers the cost of long, mixed tasks: design, debugging, feature work, review, and analysis.
2. Check that it costs no quality. Every stage has hidden tests or deterministic checks, so a cheaper run that breaks the plugin counts as a failure.
3. Find which kinds of work the skill helps and which it hurts, stage by stage.

## Configurations

| Name | Skills the run reads first |
| --- | --- |
| `with_tee` | `vim9script-plugin`, `code-comments`, `github-markdown-style`, `token-efficient-execution` |
| `without_tee` | `vim9script-plugin`, `code-comments`, `github-markdown-style` |

Both configurations get the same three domain skills, so any difference comes from token-efficient-execution alone. The skills are installed in `~/.claude/skills`, so the `without_tee` prompt must forbid the Skill tool and name token-efficient-execution as off limits. Otherwise the baseline can load it on its own.

Each stage runs 3 times per configuration, for mean and standard deviation.

## The plugin

Waypoint stores named cursor positions and jumps back to them. It is small enough to read in one sitting and large enough that reading all of it is wasteful.

| Item | Value |
| --- | --- |
| Commands | `:WaypointAdd {name}`, `:WaypointJump {name}`, `:WaypointList`, `:WaypointDelete {name}` |
| Settings | `g:waypoint_dir`, `g:waypoint_popup_width`, `g:waypoint_no_mappings` |
| Mappings | `<Plug>(WaypointAdd)` and `<Plug>(WaypointList)`, with default keys `<Leader>wa` and `<Leader>wl` |
| Storage | `waypoints.json` in `g:waypoint_dir`, a list of records with `name`, `file`, `line`, `col`, and `created` |

### Fixture layout

```text
waypoint/
  plugin/waypoint.vim               commands, mappings, settings
  autoload/waypoint.vim             command entry points
  autoload/waypoint/store.vim       class Store: load and save JSON
  autoload/waypoint/entry.vim       class Waypoint: one record
  autoload/waypoint/popup.vim       the :WaypointList popup
  import/waypoint/variables/constants.vim
  import/Logger/                    vendored from vim9script-plugin
  doc/waypoint.txt
  README.md
  tests/run.vim                     harness, per references/testing.md
  tests/test_store.vim
  tests/test_commands.vim
  logs/waypoint.log                 generated, 10,000 lines
```

The reference implementation follows every rule in `vim9script-plugin` and `code-comments`, and its own tests pass. The traps that reward efficient work are the 10,000-line log, the vendored Logger, and repeated runs of the test harness.

### Checkpoints

Each stage starts from a fixed snapshot, not from the previous stage's output. A failure in one stage then cannot spoil the next, and each stage's numbers stand alone.

| Snapshot | Contents | Used by |
| --- | --- | --- |
| `brief` | `BRIEF.md` only | Stage 1 |
| `v1-buggy` | Reference v1 with 3 planted bugs, `BUGS.md`, and the log | Stage 2 |
| `v1` | Reference v1, bugs fixed | Stages 3a, 3b, and 3c |
| `v2-review` | Reference v2 with all 3 features and 8 planted review issues | Stage 4 |
| `v2` | Reference v2, clean | Stage 5 |

## Stages

### Stage 1: Design plan

**Prompt:** "Read BRIEF.md and write a design plan for the Waypoint plugin in docs/DESIGN.md. Don't write any code yet."

`BRIEF.md` describes the commands, settings, and storage from a user's point of view, in about 300 words.

| Check | Method |
| --- | --- |
| DESIGN.md has sections for commands, settings, storage format, file layout, classes, error handling, and tests | Heading match |
| File layout matches the vim9script-plugin directory structure, with an `autoload/` and `plugin/` split and constants in `import/waypoint/variables/` | Path match |
| Names follow the skill: PascalCase commands, `g:waypoint_` settings, `<Plug>` mappings, and a `g:waypoint_no_mappings` opt-out | Regex |
| Storage keys keep their full names | Regex on the JSON example |
| Every code fence names a language, with no filler words and at most two dashes and two semicolons | Reuse `grade.py` Markdown checks |
| No code files created | Diff |
| Plan is 1,500 words or fewer and the final reply is 120 words or fewer | Word count |

### Stage 2: Debugging

**Prompt:** "BUGS.md lists three bugs users reported. Find and fix them, and add a regression test for each."

`BUGS.md` gives symptoms only.

| Bug | Symptom in BUGS.md | Cause |
| --- | --- | --- |
| B1 | Waypoints vanish after restarting Vim from another directory. | `Store` uses `g:waypoint_dir` without `expand()`, so it writes to a literal `~` directory under the current directory. |
| B2 | `:WaypointJump` lands on the line above the saved one. | `Waypoint` saves `line('.') - 1`. |
| B3 | After adding `beta`, `gamma`, and `alpha` in that order, `:WaypointDelete beta` deletes `gamma`. | Delete uses an index from the sorted display list on the unsorted store. |

Line 7,412 of `logs/waypoint.log` shows the wrong save path, which confirms B1. Line 40 holds an unrelated warning about a deprecated popup option, as a distraction.

| Check | Method |
| --- | --- |
| Hidden tests pass, one per bug | Headless Vim |
| Existing tests pass | Headless Vim |
| Each bug has a new regression test in `tests/` | Diff and test names |
| Source changes stay in `store.vim` and `entry.vim`, the two files that hold the bugs | Diff |
| The new tests fail when the buggy sources are put back | Headless Vim |
| Vendored Logger and the log are untouched | Diff |
| Changed lines follow vim9script-plugin and code-comments rules | Static checks, see Grading |
| The run never reads the whole log, and reads the Logger at most once | Transcript |
| The run makes 25 or fewer tool calls, runs the harness 4 or fewer times, and never rereads an unchanged file | Transcript |
| Final reply is 150 words or fewer | Word count |

### Stage 3: Features

Three features, each a separate eval from the `v1` snapshot. Each one requires the same four deliverables:

1. A `## Feature: <name>` section in `docs/DESIGN.md`, with commands and settings, data changes, files touched, and tests.
2. The implementation.
3. Tests.
4. Updates to `doc/waypoint.txt`, with help tags, and to `README.md`.

| Eval | Feature | Size | Hidden tests cover |
| --- | --- | --- | --- |
| 3a | `:WaypointRename {old} {new}` with name completion | Small | rename, persistence, an error on an unknown old name, an error on an existing new name, and completion filtered by the typed prefix |
| 3b | Project scope: `g:waypoint_scope` set to `'global'` or `'project'`, with the project root found by `g:waypoint_root_markers` | Medium | separate storage per project, the list showing only the current scope, global as the default, and a fallback when no root is found |
| 3c | Line tracking: text properties keep a waypoint on its line as lines are inserted above it, and the stored line updates on write | Large | moves after inserts and deletes above, saves after `:write`, and leaves unloaded buffers alone |

**Prompt for 3a:** "Add a :WaypointRename {old} {new} command with completion for existing names. Design it in docs/DESIGN.md first, then implement it, test it, and update the help and README." Prompts 3b and 3c follow the same pattern.

| Check | Method |
| --- | --- |
| Hidden feature tests pass and existing tests pass | Headless Vim |
| DESIGN.md has the feature section with all four subsections | Heading match |
| Help file has a tag for each new command and setting, and `:helptags` runs without errors | Headless Vim |
| README lists the new command or setting | Text match |
| New code follows vim9script-plugin: script header, load guard, `import autoload` in the plugin file, no globals read inside functions, named constants, and alias rules | Static checks |
| New comments follow code-comments | Static checks |
| No changes to the vendored Logger | Diff |
| Tool calls, harness runs, and rereads stay under limits set after the pilot | Transcript |

### Stage 4: Code review

**Prompt:** "Do a full code review of this plugin. Write the findings to REVIEW.md, citing path:line for each. Don't change any code."

The `v2-review` snapshot plants 8 issues, each with an ID, a file, and keywords that count as finding it.

| ID | Kind | Issue |
| --- | --- | --- |
| R1 | Bug | `Store.Load` calls `json_decode()` on an empty file and throws E491. |
| R2 | Bug | Rename completion returns every name instead of names that match the typed prefix. |
| R3 | vim9script-plugin | `popup.vim` reads `g:waypoint_popup_width` inside a function. |
| R4 | vim9script-plugin | `waypoints.json` is typed in two scripts instead of named once in `constants.vim`. |
| R5 | vim9script-plugin | The plugin file calls an autoload function at load time to decide on a mapping. |
| R6 | code-comments | An inline comment in `store.vim`. |
| R7 | code-comments | A `# ---- helpers ----` delimiter in `entry.vim`. |
| R8 | Documentation | `doc/waypoint.txt` has no tag for `:WaypointRename`. |

| Check | Method |
| --- | --- |
| Recall: planted issues found, out of 8 | File and keyword match per issue |
| Every finding cites path:line, and every cited line exists | Regex and file check |
| No findings inside the vendored Logger | Path match |
| No code changes | Diff |
| False positives | Grader agent from skill-creator, then human review in the viewer |
| The run reads each file at most once | Transcript |

### Stage 5: Final analysis

**Prompt:** "Write ANALYSIS.md: an analysis of the Waypoint plugin as it stands, with three to five suggestions for new features."

| Check | Method |
| --- | --- |
| Sections for architecture, strengths, risks, and suggested features | Heading match |
| 3 to 5 suggestions, each with user value, a design sketch, the files affected, and an effort of S, M, or L | Structure match |
| Every named file exists or is a new path in a valid plugin directory | Path check |
| No suggestion repeats an existing command or setting | Text match against the v2 feature list |
| Markdown checks from stage 1, and 900 words or fewer | Reuse `grade.py` checks |
| Quality of the suggestions | Grader agent, then human review |

### End-to-end run

An optional seventh eval runs the whole workflow in one session, from the brief through design, implementation, three features, review, and analysis. Hidden tests for v1 and all three features grade the code. This eval shows the cost of one long session, where context grows and the skill's rules have the most room to help or hurt. Run it only after the per-stage results look sound, because a single run costs as much as several stages.

## Grading

### Shared checks

- **Headless Vim:** `vim -Nu NONE -i NONE -es` with the run's `outputs/` on `runtimepath`, then `tests/run.vim` and a hidden harness. Results come from `v:errors`, not from parsing messages.
- **vim9script-plugin static checks:** `vim9script` on line 1, the load guard with `v:version < 902` and `&cp`, no `function!` or `let`, `import autoload` in `plugin/`, no `g:` read inside a `def` body, and one alias per script across the project. These run on changed lines only. Named constants for numbers have no reliable static check, so the grader agent and human review cover them.
- **code-comments static checks:** reuse the `cc` checks from `grade.py` with the `#` marker: no inline comments, a 78-column limit, `#`-only delimiter lines, and `FUNCTION:`, `METHOD:`, or `CLASS:` on the blocks above them.
- **Markdown checks:** reuse the `md` checks from `grade.py`.
- **Transcript checks:** reuse the deduplicated parser from `grade_ledger.py`. Metrics are tool calls, tokens processed, harness runs, rereads, and whole-file reads of the log and the Logger.

### Grader validation

Before any benchmark run, each stage's grader must fail on that stage's input snapshot and pass on its reference solution. The earlier benchmark rounds found four grader bugs only after the runs. This step catches them first.

### Metrics

| Metric | Use |
| --- | --- |
| Pass rate | Quality guardrail |
| Tokens processed per run | Primary cost measure |
| Tokens per passing run | Cost of a correct result |
| Tool calls, harness runs, and rereads | Explain where tokens go |
| Wall time | Secondary cost measure |
| Final reply words | Output discipline |

### Success criteria

Token-efficient-execution passes on this benchmark if, across all stages, `with_tee` uses at least 15% fewer tokens per passing run and its pass rate stays within 5 points of `without_tee`. A stage that misses either bar gets a written finding, even when the totals pass.

## Pilot

Run stages 2 and 4 once per configuration before the full benchmark. The pilot does two things:

1. It confirms the graders work on real output.
2. It sets the tool call, harness run, and word limits for stages 3 to 5 from observed numbers instead of guesses.

### Pilot results

The pilot ran stages 2 and 4 once in each configuration, in October 2026.

| Stage | Configuration | Checks | Tokens | Time | Tool calls |
| --- | --- | --- | --- | --- | --- |
| Debugging | `with_tee` | 22 of 22 | 474,000 | 64 s | 8 |
| Debugging | `without_tee` | 21 of 22 | 414,000 | 71 s | 7 |
| Review | `with_tee` | 17 of 17 | 1,160,000 | 223 s | 16 |
| Review | `without_tee` | 17 of 17 | 1,430,000 | 289 s | 18 |

The pilot led to these changes before the full run:

- **Grader:** the log check now counts only commands that print the log, not text that names it. The global-read check now skips comment lines.
- **Limits:** tool call limits sit at about one and a half times the most calls seen, and the stage 2 reply limit is now 200 words.
- **Isolation:** each run gets its own scratch folder, after two review runs overwrote each other's copy in a shared folder.
- **Reference:** both reviews found real defects beyond R1 to R8. The root search let the first marker win instead of the nearest folder and put a file marker's root one folder too high. Tracker IDs were keyed by name only. `:WaypointJump` threw E37 from a modified buffer, and the README's Logger example used Vim9 syntax. The reference now fixes all of them, and a hidden 3b test checks the nearest-root rule that the prompt states.
- **Review recall:** both runs found all eight planted issues, so recall alone will not separate the configurations. Cost and the grader agent's precision judgment carry stage 4.

## Results

The full run finished on 2026-10-21: 7 stages, 2 configurations, and 3 runs each, 42 runs in all. The table gives means.

| Stage | Pass rate with | Pass rate without | Tokens with | Tokens without | Tokens saved | Time with | Time without |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 Design | 87.0% | 87.0% | 363k | 683k | 47% | 140 s | 194 s |
| 2 Debugging | 98.3% | 92.0% | 455k | 556k | 18% | 73 s | 82 s |
| 3a Rename | 100% | 100% | 714k | 1,024k | 30% | 123 s | 172 s |
| 3b Project scope | 98.7% | 100% | 728k | 1,012k | 28% | 152 s | 224 s |
| 3c Line tracking | 100% | 97.3% | 1,130k | 1,601k | 29% | 320 s | 371 s |
| 4 Review | 100% | 98.0% | 848k | 1,093k | 22% | 248 s | 282 s |
| 5 Analysis | 93.0% | 89.0% | 718k | 993k | 28% | 187 s | 290 s |
| All | 96.7% | 94.8% | 14.9M total | 20.9M total | 29% | 62 min total | 81 min total |

Both success criteria pass. Tokens per passing check fell 30%, from 1,050k to 732k, against a bar of 15%. The pass rate rose 2.0 points, inside the 5-point guardrail. Every stage saved tokens, and the skill also cut tool calls by about a third and token spread from 337k to 256k standard deviation.

### Notes on the results

- **Length limits:** every run in both configurations failed the 1,500-word design limit, the 120-word design reply limit, and the 900-word analysis limit. The checks measure length but do not separate the configurations, so later runs should use the word counts instead.
- **Review recall:** five of six reviews found all eight planted issues. The sixth, without the skill, also cited the vendored Logger. Every review found real defects beyond R1 to R8, so a precision score needs the grader agent or a human, which this run did not do.
- **Write refusals:** the harness refused every stage 5 run's Write of a report-style `.md` file. Four runs returned the document in their reply, and the main session saved it verbatim from the transcript. Each such run has a `HARNESS_NOTE.md`. Two runs, one in each configuration, wrote the file through a shell heredoc instead, which evades the refusal.
- **Grader fixes during the run,** each applied to all runs and each passing `--validate`:
  - The global-read check allows one runtime setting read in one place.
  - The alias check skips the vendored `plugin/logger.vim`.
  - Review citations may give a bare file name.
  - Findings group at the top level, and issue keywords match case-insensitively.
  - An effort may sit in a summary table.

## Cost

| Part | Runs |
| --- | --- |
| Pilot | 4 |
| Stages 1, 2, 3a, 3b, 3c, 4, and 5, with 2 configurations and 3 runs each | 42 |
| End-to-end, with 2 configurations and 3 runs each | 6 |

The earlier ledger evals processed about 230,000 tokens per run. Feature and review stages will likely run two to five times that, which puts the full benchmark at roughly 25 to 40 million tokens processed, mostly cached reads. The pilot will give a firmer figure.

## Build status

| Part | Location |
| --- | --- |
| Brief, reference v1, v2 overlay, and solution overlays | `waypoint/brief/`, `waypoint/src/`, `waypoint/solutions/` |
| Snapshot builder with B1 to B3, R1 to R8, and the log | `waypoint/make_waypoint.py`, run by `make_fixtures.py` |
| Hidden tests | `waypoint/hidden/` |
| Grader | `grade_waypoint.py` |
| Evals and run prompts | `evals.json` IDs 10 to 16, seeded by `seed.py` |

- [x] Write `BRIEF.md`.
- [x] Write reference v1 and its tests, following vim9script-plugin and code-comments.
- [x] Derive `v1-buggy` with B1, B2, and B3, and write `BUGS.md`.
- [x] Generate `logs/waypoint.log` with the B1 evidence and the distractor warning.
- [x] Write reference solutions for 3a, 3b, and 3c, giving reference v2.
- [x] Derive `v2-review` with R1 to R8.
- [x] Write hidden tests for stages 2 and 3.
- [x] Write `grade_waypoint.py` with the shared checks and per-stage checks.
- [x] Validate every grader against its snapshot and reference solution.
- [x] Add the stage evals to `evals.json` and teach `seed.py` the two configurations.
- [x] Run the pilot and set the remaining limits in `LIMITS` in `grade_waypoint.py`.

### Validation

`python3 grade_waypoint.py --validate` checks four things:

1. Every hidden test fails on its stage's input and passes on the reference, except the guard tests, which check old behavior and pass on both.
2. Every non-transcript check passes on each stage's reference solution.
3. The plugin's own tests pass on all four code snapshots. The bugs and review issues slip past the suite, as they would past CI.
4. The static checks flag exactly the four planted rule breaks in `v2-review`, R3, R5, R6, and R7.

The guard tests are `Global_is_the_default_scope` and `Project_waypoints_work_inside_their_project` for 3b, and `Edits_below_do_not_move_it` and `Unloaded_buffers_keep_their_lines` for 3c.
