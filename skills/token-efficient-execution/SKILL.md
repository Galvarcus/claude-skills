---
name: token-efficient-execution
# prettier-ignore
description: Minimize token use without losing correctness, completeness, or requested detail. Use for any non-trivial task, especially code changes, repository work, research, multi-step reasoning, and tool-assisted workflows, or when the user asks for concise, low-cost, or token-efficient work.
---

# Token-Efficient Execution

Use the least information, reasoning, tool calls, and output that give a correct, complete, maintainable result. Efficiency limits effort. It never replaces needed reasoning, verification, or requested detail.

## Priority Order

When goals conflict: 1. Correctness. 2. User requirements. 3. Safety. 4. Maintainability. 5. Risk-appropriate verification. 6. Token efficiency. 7. Extra explanation.

## 1. Scope the Work

Classify the task first. Do only that level of work.

- **Trivial**: answer directly, no tools.
- **Localized**: inspect only the relevant file, function, or section.
- **Multi-file**: map dependencies before reading.
- **Repository-wide**: search first, read only the hits.
- **Research**: use the fewest authoritative sources.
- **High-risk**: spend extra on verification.

Ask: "What is the minimum information needed for a correct result?" Get it, then stop. Never explore or call tools only because they are available.

## 2. Retrieve Context

Use the first sufficient source: conversation, earlier tool results, relevant local files, targeted repository search, targeted external docs, broad research.

- Search before reading. Location unknown: search the symbol, phrase, error, or API; read only the hits; widen only if needed. Location known: read only that range or section.
- Never read a whole file for one function, a whole repository for one behavior, or generated files when their source exists.
- Prefer the narrowest operation: exact search over directory listing, line range over whole file, one test over the full suite, official docs for the exact API over broad web search.
- Limit tool output: `head`/`tail`, line ranges, match limits, quiet flags, `--stat` or name-only diffs, filters. Never dump large logs. Extract the failing lines.

## 3. Tool Calls

- Each call needs a purpose: what does it give that I lack? If unclear, skip it.
- Treat results as cached. Never repeat a search or re-read a file to confirm unchanged information. Trust a successful edit; do not re-read to check it.
- Batch independent calls in parallel. Combine related queries. Make one edit, not several incremental ones. No speculative calls.
- Escalate only when needed: known information, targeted search, targeted read, broader read, external research, deep analysis. Stop when the evidence suffices.
- Delegate bulk exploration to a subagent when available. Use only its summary.

## 4. Reasoning

Use the simplest valid path: direct deduction, known APIs, project conventions, deterministic transformations. Match depth to difficulty.

- No alternatives unless they help the user's decision.
- No edge cases that cannot affect the result.
- No solving a more general problem than asked.
- Do not output chain-of-thought. Give conclusions, evidence, and decisions. Summarize important reasoning at a high level.

## 5. Code Changes

- Search for an existing implementation. Follow project conventions. Reuse helpers and abstractions. Modify the smallest surface.
- Make the minimal diff: change only required lines, keep formatting, no unrelated cleanup, refactoring, reformatting, renaming, or API changes. One requested change gives one focused change.
- Use targeted edit operations, not full-file rewrites.
- Add no abstraction when one exists. Do not rewrite working code for style.
- If a broader refactor is required, explain it only when it affects the user.

## 6. Verification

Match verification to risk.

| Risk | Examples | Verification |
|---|---|---|
| Low | formatting, docs, obvious text edits | none or minimal |
| Medium | localized code, config, API usage | smallest relevant test or check |
| High | security, migrations, build system, public API, complex behavior | targeted checks; widen only when justified |

- Prefer a focused test over the full suite when confidence is equal.
- Do not verify one fact by several means unless the task is high-risk, sources disagree, the first check is inconclusive, or confirmation materially raises confidence. One authoritative source usually suffices.

## 7. Failures and Uncertainty

- Name the specific uncertainty. Use the smallest action that resolves it: API behavior, read docs; implementation location, search; expected behavior, read tests; user requirement, ask. Ignore uncertainty that cannot affect the result.
- After a failure, find the cause before retrying. Never repeat an unchanged failing action. Change approach after two failed attempts.

## 8. Questions to the User

Infer from the request, context, conventions, standard behavior, and docs. Ask only when the ambiguity materially changes the result. Ask the smallest single question that resolves it.

## 9. Output

- Default: what was done, key result or caveat, verification (when relevant). Simple task: a few sentences. Complex task: enough to use the result, no more.
- Answer first. Add detail only when required.
- Omit: restating the request, narrating steps or tool calls (also between calls), summaries of unchanged code, unrequested background, repeated conclusions, needless headings and examples.
- Do not paste file contents or diffs the user already has. Cite `path:line`.
- Be dense: "Changed X because Y. Fixes Z. Verified with A." Use tables or bullets only when they reduce ambiguity or repetition.
- An explicit user request for more detail overrides these limits.

## 10. Token Budget and Stop

Spend tokens by value. Highest: understand the request, get relevant context, implement. High: targeted verification. Medium: explain key decisions. Low: alternatives, background. None: unrelated cleanup.

Stop when the requested outcome is achieved, needed information is obtained, the result is consistent, verification passed, and more work would not materially improve it. Do not keep searching, refactoring, testing, or explaining because more is possible.

## Checklist

- **Before**: Smallest sufficient context? Answer without tools? Most targeted operation? Operations combinable? Already have it?
- **During**: Unnecessary context? Repeating? Can I stop? Unrelated changes?
- **Before replying**: Request satisfied? Verified what needs it? Anything removable? Results, not process narration?

**Default behavior: do less, but do exactly enough.**
