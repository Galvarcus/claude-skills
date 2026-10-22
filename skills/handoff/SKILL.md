---
name: handoff
description: Write or update a handoff file that lets a fresh agent pick up the current work and continue it, and resume work from one. Use when the user asks for a handoff, a session summary to continue later, or to save progress before clearing or ending a session; when a hook reports that context or usage limits have reached the threshold; and when the user asks to resume or continue from a handoff. Not for commit messages, pull request descriptions, changelogs, or status reports meant for people.
---

# Handoff

## Purpose

Record the state of the current work in one file so that an agent with no memory of this session can continue it without asking the user to repeat anything. The file holds what exists only in this conversation and points to everything else.

## When to Use

Use this skill when:
- The user asks for a handoff, or to save progress before clearing, compacting, or ending a session.
- A hook message reports context or usage at or above the threshold. Write the handoff first, then continue the task.
- The user asks to resume, continue, or pick up from a handoff.

Do not use this skill for commit messages, pull request descriptions, changelogs, or status reports for people.

## Location

Write the file to `.claude/handoff.md` at the root of the git repository, or in the current directory outside a repository. Overwrite it each time; the newest handoff replaces the old one, and git history and the linked records carry the past.

Before writing, make sure git ignores the file:

1. Run `git check-ignore -q .claude/handoff.md` from the repository root.
2. If the file is not ignored, append `.claude/handoff.md` to `.git/info/exclude`. This file is local, so the rule never reaches the shared `.gitignore`.
3. If the file is already tracked, stop and tell the user rather than overwrite a committed file.

## Writing a Handoff

1. Gather state with cheap commands: `git status --short`, `git branch --show-current`, `git log --oneline -10`, and `git stash list`. Note any open pull request with `gh pr view --json url,title` when `gh` is available.
2. Write the file using the structure under Output. Leave out a section that has nothing to say.
3. Reference, never copy. When content lives somewhere durable, give its path, URL, commit hash, or issue number with a one-line note on why it matters:
   - Code and documents: a path with a line number, such as `src/parse.py:142`.
   - Committed work: a commit hash or branch name, not a list of the changes.
   - Plans, specs, and reports: their path or artifact URL.
   - Long-lived project facts: `CLAUDE.md` or memory files, by path.
   - Uncommitted changes: the file list from `git status`, not the diff.
4. Record what only this conversation knows: the goal in the user's terms, decisions and their reasons, approaches that failed and why, the user's stated preferences for this task, and anything half done.
5. Redact before saving. Follow the rules under Redaction.
6. Read the file once, as a fresh agent would. Fix anything that depends on this conversation to make sense, such as "the bug we found" or "as discussed".
7. Tell the user the path in one line.

## Resuming from a Handoff

1. Read `.claude/handoff.md`.
2. Check it against the repository: compare the branch, recent commits, and `git status` with what the file records. Say so when they differ, and trust the repository over the file.
3. Read only the references that the next step needs.
4. Continue from Next Steps. Ask the user only about the items under Open Questions that block the work.

## Redaction

The file must never hold a secret or private data. Replace each with `[REDACTED: kind]` and say where the real value lives, such as "in `.env`" or "in the team password manager".

Redact:
- API keys, tokens, passwords, private keys, session cookies, and signed URLs.
- Connection strings and URLs that carry credentials or tokens.
- Internal hostnames, IP addresses, and account or customer identifiers that the work does not need.
- Personal data about anyone other than the user, such as names, emails, and phone numbers from logs or tickets.

Name an environment variable or config key instead of its value, such as `DATABASE_URL` in `.env`.

## Output

Use this structure. Keep each section short and concrete.

```markdown
# Handoff: <task in a few words>

Updated: <YYYY-MM-DD HH:MM> · Branch: <branch> · Head: <short hash>

## Goal
What the user wants done and how they will judge it done.

## State
Done, in progress, and not started. Uncommitted files by path.

## Decisions
Each decision with its reason, so the next agent does not reopen it.

## Tried and Failed
Each approach that did not work and why.

## Next Steps
1. The next concrete action, with paths.

## Open Questions
Questions only the user can answer.

## References
- `path/or/URL`: why it matters.
```

## Examples

- **Use this skill:** "Write a handoff so I can pick this up in a new session tomorrow."
- **Use this skill:** "Resume from the handoff."
- **Do not use this skill:** "Write a pull request description for this branch."
