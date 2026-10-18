---
name: "code-comments"
description: Write, edit, or review comments in any file that can hold them, using this project's comment standards. Covers source code in any language, shell and Vim scripts, Python, Lua, YAML and CI workflows, TOML, LaTeX, CSS, HTML, and Markdown. The rules state why, not what; forbid inline comments; keep blocks to 78 columns; mark blocks with identifiers such as FUNCTION: and TODO:; and link GitHub issues on REFERENCE: lines. Use whenever writing or changing code, configuration, or templates, even when the task is not about comments, and when reviewing a diff that adds or changes comments. A language skill, such as vim9script-plugin, adds its comment marker and header fields on top of these rules.
---

# Code Comments

## Scope

These rules apply to every comment in every file that can hold one: source code, scripts, configuration, CI workflows, templates, style sheets, and markup.

* A language or project skill may add specifics, such as the fields of a file header. Follow both. On a conflict, the more specific skill wins.
* A doc comment that a tool reads, such as a Python docstring, a Go doc comment, or JSDoc, keeps the form that the tool expects. The writing rules still apply to its text. The identifiers do not.
* Generated files and vendored code keep their comments as they are.

## Principles

Good code should explain itself. Before adding a comment, ask whether the code can be changed so the comment is unnecessary. When a comment is necessary, state **why**, not merely **what** the code does.

* Omit needless comments. Prefer clear code over comments that explain unclear code.
* Explain **rationale, intent, constraints, or non-obvious consequences**, not mechanics that the code already makes clear.
* Keep comments **brief, specific, and concrete**. Omit vague or unnecessary words.
* Use direct, declarative language. Prefer strong verbs and specific nouns.
* Avoid promotional, conversational, or rhetorical language.
* Do not repeat what the code, a name, or nearby documentation already says.
* Do not use comments to compensate for poor code. Refactor the code when that produces a clearer explanation than a comment.
* Keep comments current. A comment that no longer describes the code is worse than no comment.

## Placement

* No inline comments. Put a comment on the line directly above the code it explains, with no blank line between the comment and the code.
* A comment inside a function or block explains the next line or lines of code and takes no identifier.
* Use one space after the comment marker.
* A file header block gets one blank line before and after it. It follows any line that must come first, such as a shebang or an encoding line.

| Marker | Used in |
| --- | --- |
| `#` | Vim9 script, Python, shell, YAML, TOML, Ruby, Makefile |
| `//` | C, C++, Java, JavaScript, TypeScript, Go, Rust, Swift |
| `--` | Lua, SQL, Haskell |
| `%` | LaTeX, TeX |
| `;` | Lisp, INI |
| `"` | Legacy Vim script |
| `/* */` | CSS, and C-family block comments |
| `<!-- -->` | HTML, XML, Markdown |

## Punctuation

Avoid quotation marks, brackets, parentheses, dashes, em dash, and en dash unless they are part of a code example. Name options, variables, settings, and files without quotes: guioptions, g:plugin_width, ci.yml.

## Comment Blocks

Comment blocks should be concise, orderly, and easy to scan.

* A delimiter line contains only the comment marker, repeated: `#####`, `/////`, `-----` for the `--` marker, `%%%%%`. Never follow a marker with a different character, such as `# ----` or `// ====`.
* Keep comment lines to **78 columns or fewer**, counted from column 1. An indented comment has 78 minus its indent for text. A delimiter line ends at column 78.
* A block that documents a class, method, function, or section begins with an identifier followed by `:`, for example `# CLASS:` or `// TODO:`.
* Use specific, concrete language. Avoid vague phrases such as handles things, does some processing, or for convenience.
* Omit needless introductory phrases such as This function is used to or This code will.
* Prefer imperative or direct descriptions where appropriate:
  * `# METHOD: Parse the configuration file.`
  * `// CLASS: Represents a plugin configuration.`
* Keep related information together, and use parallel construction when listing multiple items.
* Do not add a comment block merely to provide structure that the code already makes obvious.

In a format with only block comments, such as CSS or HTML, the opening and closing markers stand on their own lines, or enclose a one-line comment: `/* text */`. The width, writing, and identifier rules still apply.

### Identifiers

`CLASS:` (a class, struct, or other type with methods), `INTERFACE:` (an interface, trait, or protocol), `METHOD:` (a function defined in a class or type), `FUNCTION:` (a function outside one), `SECTION:` (the header of a delimited section), `FIXME:` (should never be needed), `TODO:`, `OPTIMIZE:` (should never be needed), `HACK:` (should never be needed), `REVIEW:`, `REFERENCE:` (a link to a GitHub issue, see Issue References). The user's syntax highlighting matches these. Add a new identifier only for a distinct, recurring purpose.

## Issue References

Link a GitHub issue from a comment only when the issue is needed to understand why the code is as it is: the change is obscure, breaks normal coding practice, or is a workaround. Do not link an issue for every change it caused.

* Put the link on its own line, directly below the comment it supports, after `REFERENCE:`.
* One link per line, the full address of the issue.

```yaml
# Pandoc 3.8.2.1 and later write a table without a caption that the
# templates must support, and the distro pandoc is older.
# REFERENCE: https://github.com/jgm/pandoc/issues/11201
pandoc: [distro, '3.10']
```

## File Header Blocks

Where a project uses a file header block, it states what the file does, tersely and concretely, without praise or unnecessary adjectives. The fields come from the language or project skill.

Prefer:

```python
# Plugin_Name: example
# Provides commands for managing plugin configuration.
# License: GNU GPL 3.0
```

over:

```python
# Plugin_Name: example
# This is a powerful and easy-to-use plugin that provides
# useful functionality for managing plugin configuration.
# License: GNU GPL 3.0
```

## Examples

A function block, and a comment that explains the next line, in Lua:

```lua
-- FUNCTION: Return the columns of a longtable spec, or nil for a spec of
-- another form, which is left alone.
local function split_columns(spec)
  -- Pandoc wraps the spec in @{}, which removes the outer padding.
  local s = spec:gsub('^%s*@{}', '')
```

A block comment in CSS:

```css
/* Normal weight, so that the header style setting decides. */
th {
  font-weight: normal;
}
```

## Response Style

Apply these rules directly when writing or editing comments rather than describing them. When reviewing comments, name the violated rule and give the concrete fix.
