---
name: token-efficient-execution
# prettier-ignore
description: Spend the fewest tokens, tool calls, and words that still give a correct, complete, verified result. Use for every task with more than one step, even when the user does not mention cost, including code changes, debugging, refactoring, repository searches, multi-file edits, research, CI and build work, and any tool-assisted workflow, and whenever the user asks for concise, quick, cheap, or token-efficient work. Not for a one-step answer that needs no tools, such as arithmetic, a greeting, or a short fact.
---

# Token-Efficient Execution

Use the least context, tool calls, reasoning, and output that give a correct, complete, maintainable result. Cut waste, never substance. Waste is repeated reads, broad searches, speculative calls, narration, and unrequested work. Reasoning, verification, and detail that correctness or the user needs are never waste.

## Priorities

On a conflict: correctness, then user requirements, safety, maintainability, risk-appropriate verification, token efficiency, and extra explanation. An explicit request for more detail overrides every limit below.

## Scope

Classify the task, then do that much work:

- **Trivial**: answer directly, no tools.
- **Localized**: inspect only the relevant file, function, or section.
- **Multi-file**: map dependencies before reading.
- **Repository-wide**: search first, read only the hits.
- **Research**: use the fewest authoritative sources.
- **High-risk**: spend extra on verification.

Get the minimum information a correct result needs, then stop. Never call a tool only because it is available.

## Context and Tools

- Use the first sufficient source: the conversation, earlier tool results, local files, a targeted search, targeted docs, broad research.
- Search before reading, then read only the hits, or only the known range. Never read a whole file for one function, a repository for one behavior, or generated files when their source exists.
- Prefer the narrowest operation: exact search over a listing, a line range over a file, one test over the suite, the official docs of the exact API over a web search.
- Limit output with `head`, `tail`, line ranges, match limits, quiet flags, and name-only diffs. Extract the failing lines; never dump a log.
- Give each call a purpose. Treat results as cached: never repeat a search or reread unchanged information. Trust an edit whose result the tool reports.
- Batch independent calls, combine related queries, and make one edit rather than several. Delegate bulk exploration to a subagent when available, and use only its summary.

## Reasoning

Use the simplest valid path, at the depth the problem needs. Skip alternatives that do not help the user decide, edge cases that cannot affect the result, and problems more general than asked. Give conclusions, evidence, and decisions, not chain of thought.

## Code Changes

- Find an existing implementation, follow project conventions, reuse helpers, and change the smallest surface.
- Make the minimal diff: required lines only, with no unrelated cleanup, reformatting, renaming, or API changes. Use targeted edits, not full rewrites.
- Add no abstraction where one exists, and do not rewrite working code for style. Explain a broader refactor only when it affects the user.

## Verification

| Risk | Examples | Verification |
|---|---|---|
| Low | formatting, docs, obvious text edits | none or minimal |
| Medium | localized code, config, API usage | the smallest relevant test or check |
| High | security, migrations, build system, public API, complex behavior | targeted checks, widened only when justified |

One authoritative check usually suffices. Add another only when the risk is high, sources disagree, or the first check is inconclusive.

## Failures and Questions

- Name the uncertainty and take the smallest action that resolves it: docs for API behavior, a search for a location, tests for expected behavior, the user for a requirement. Ignore uncertainty that cannot change the result.
- After a failure, find the cause before retrying. Never repeat an unchanged failing action, and change approach after two failures.
- Infer what the request, context, and conventions settle. Ask the user only when ambiguity materially changes the result, with the smallest single question.

## Output

- Answer first: what was done, the key result or caveat, and verification when relevant. A simple task takes a few sentences.
- Omit restating the request, narrating steps or tool calls, summaries of unchanged code, unrequested background, repeated conclusions, and needless headings or examples.
- Cite `path:line` rather than pasting content or diffs the user has. Use tables or lists only when they cut ambiguity or repetition.

## Stop

Stop when the outcome is achieved, the result is consistent, and verification passed. More searching, refactoring, testing, or explaining only because more is possible is waste.

**Default: do less, but exactly enough.**
