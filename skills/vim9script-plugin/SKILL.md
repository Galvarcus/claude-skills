---
name: "vim9script-plugin"
description: Create, edit, review, or maintain Vim plugins and Vim scripts using Vim9script per this project's standards. Use whenever writing or modifying a .vim file, a Vim plugin, Vim9 classes, autoload/import scripts, Vim commands, or Vim plugin documentation — even for small edits or single functions. Covers naming, formatting, comments, imports, logging, script section ordering, and directory structure.
---

# Vim9script Plugin Development

## Scope

- Use the latest, or highest available stable, version of Vim.
- Use Vim9script.
- Target Vim and gvim only. Other Vim clones and UIs are out of scope.
- Never rely on compatibility mode (vi), except to ensure the plugin does not load under it.

## Vim9script Design

- Use classes and other Vim9 performance features.
- Prefer classes over bare methods/functions. Use bare methods/functions only when necessary.
- Put any method used more than once into its own exportable, reusable method or class.
- Each Vim script should focus on a singular task.

## Script Structure

Order each script's sections as follows, when applicable:

1. Vim9script header (if vim9script)
2. Main script comment block
3. Imports
4. Script-level variables
5. Script-level constants
6. Global variables
7. Bare methods/functions — exported ones first
8. Classes — exported ones first

Deviate from this order only when functionality depends on a different order.

## Required Script Header

Every Vim9script begins with:

```vim
vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true
```

The version check enforces Vim 9.2+ and blocks loading under compatibility mode.

Syntax, ftdetect, ftplugin, and indent files are also Vim9 script, but they run once per buffer, so they never use the `s:is_loaded` guard. A syntax file starts with `vim9script`, guards with `if exists('b:current_syntax') | finish | endif` on separate lines, and ends with `b:current_syntax = 'name'`. After converting one, compare `synID()` names for every character of a sample against the old file. A syntax file can import shared constants and build a rule with `:execute`. A rule's `\` continuation line then joins the string expression, not the command, so put the whole rule in the executed string.

## Plugin Directory Structure

```text
Project/
  autoload/
  plugin/
  import/
  doc/
  README.md
```

- `autoload/`: always autoload imports from here.
- `import/`: scripts meant to be imported by other plugins, scripts that cannot be autoloaded, or scripts explicitly meant to be imported rather than autoloaded.

### Shared constants

Never hard-code a value in more than one script. Put every constant that more than one script uses in `import/<plugin>/variables/constants.vim`, each exported, and import it with a plain import, which Vim finds in the `import/` folder of `runtimepath`. The file imports nothing, so it can never be part of an import cycle. A constant that only one script uses stays in that script and moves when it becomes shared. Derive display names from one `PLUGIN_NAME`. Give values stored on disk, such as a file extension or a data folder name, their own literal, so that renaming the plugin never breaks existing user data.

## Naming

Use English for identifiers. Never use kebab-case.

| Case | Use for |
|---|---|
| PascalCase | Class names, function/method names, function-reference variables, user commands |
| camelCase | Class-local variables, function/method-local variables, class/method parameters |
| snake_case | Global, script-local, buffer-local, window-local, tab-local variables |
| ALLCAPS | Import aliases, constants |

Ephemeral variables (loop vars, etc.): single lowercase letter, preferring the first letter of what it references (`for f in foo`); default to `i` when no letter fits.

Never separate numbers from letters: `special_var1`, not `special_var_1`.

## Imports and Aliases

Default alias is the first letter of the imported script:

```vim
import autoload 'project/foo.vim' as F
```

When taken, use a two-letter alias: first letter + first letter of the next word, or first letter + next available letter.

```vim
import autoload 'project/foobar.vim' as FB
import autoload 'project/food.vim' as FO
import autoload 'project/foody.vim' as FD
```

When two letters are also taken, add a letter in the same way: the first letter of the next word, else the next available letter. Test modules, which all start with `test_`, use `T` plus the first letter of each following word: `test_binder.vim` as `TB`, `test_binder_directory.vim` as `TBD`.

Keep an alias consistent for the same script across all imports, and never use one alias for two scripts, even in different files. Before adding an import, check the aliases already in the project.

## Global Variables

- Use a one-line `get()` method for global variables.
- Define global variables in the `plugin/` script. If unavailable to edit, define at the top of the current script for later relocation.
- Assign any global variable used in a script to a terse script-local variable near the top, after imports: `var foo = g:some_option`.
- Prefer short names when reducing globals: `var foo = g:my_foo`.

## Formatting

- Two-space indentation. Never hard tabs.
- No trailing whitespace. Unix line endings.
- Break line continuations at semantic boundaries; never use backslash for continuation.
- Use long names of built-ins (`tabstop`, not `ts`).

## Comments

Good code should explain itself. Before adding a comment, ask whether the code can be changed so the comment is unnecessary. When a comment is necessary, state **why**, not merely **what** the code does.

* Omit needless comments. Prefer clear code over comments that explain unclear code.
* Use comments to explain **rationale, intent, constraints, or non-obvious consequences**—not mechanics that the code already makes clear.
* Keep comments **brief, specific, and concrete**. Omit vague or unnecessary words.
* Use direct, declarative language. Prefer strong verbs and specific nouns.
* Avoid promotional, conversational, or rhetorical language.
* Do not repeat information already expressed by the code, function name, variable name, or surrounding documentation.
* No inline comments: place explanatory comments on the line directly above the code, with no blank line between the comment and the code.
* Use one space after the leading `#`.
* Do not use comments to compensate for poor code. Refactor the code when that produces a clearer explanation than a comment.
* Keep comments current. A comment that no longer describes the code is worse than no comment.
* Exception: the top-of-script comment block gets one blank line before and after it.
* Avoid the use of quotation marks, brackets, parentheses, dashes, em dash, and en dash unless required as part of a code example. Name options and variables without quotes: guioptions, g:plugin_width.

### Comment Blocks

Comment blocks should be concise, orderly, and easy to scan.

* A block's opening and closing delimiter lines contain only `#`, never `-` or `=`.
* Keep comment lines to **78 columns or fewer**, counted from column 1. An indented comment has 78 minus its indent for text. A delimiter line ends at column 78.
* A block that documents a class, method, function, or section begins with an identifier followed by `:` (for example, `# CLASS:` or `# TODO:`). A comment inside a function body explains the next line of code and takes no identifier.
* Use specific, concrete language. Avoid vague phrases such as "handles things," "does some processing," or "for convenience."
* Omit needless introductory phrases such as "This function is used to" or "This code will."
* Prefer imperative or direct descriptions where appropriate:

  * `# METHOD: Parse the configuration file.`
  * `# CLASS: Represents a Vim plugin configuration.`
* Keep related information together and use parallel construction when listing multiple items.
* Do not add a comment block merely to provide structure that the code already makes obvious.

Identifiers:

`CLASS:`, `INTERFACE:`, `METHOD:` (a def inside a class), `FUNCTION:` (a def outside a class), `SECTION:` (the header of a delimited section), `FIXME:` (should never be needed), `TODO:`, `OPTIMIZE:` (should never be needed), `HACK:` (should never be needed), `REVIEW:`, `REFERENCE:` (a link to a GitHub issue, see Issue References). The user's syntax highlighting matches these. Add a new identifier only for a distinct, recurring purpose.

### Issue References

Link a GitHub issue from a comment only when the issue is needed to understand why the code is as it is: the change is obscure, breaks normal coding practice, or is a workaround. Do not link an issue for every change it caused.

* Put the link on its own line, directly below the comment it supports, after `REFERENCE:`.
* One link per line, the full address of the issue.

```vim
# The cursor is a highlighted character, so at the end of its line it
# needs a space to show on, as text fields have their padding.
# REFERENCE: https://github.com/Galvarcus/bartleby/issues/3
```

### Top-of-Script Comment Block

The top-of-script block contains:

* `# Plugin_Name:` followed by the plugin name.
* A terse, concrete description of the plugin's purpose.
* License information; default: GNU GPL 3.0.

The description should state what the plugin does, not praise it or describe it with unnecessary adjectives.

Prefer:

```vim
# Plugin_Name: example
# Provides commands for managing plugin configuration.
# License: GNU GPL 3.0
```

over:

```vim
# Plugin_Name: example
# This is a powerful and easy-to-use plugin that provides
# useful functionality for managing plugin configuration.
# License: GNU GPL 3.0
```



## Strings

Precedence order:
1. Regexes: always single-quoted (`'\s*'` — escaping differs from `"\s*"`). Double a single quote to embed one: `'example('')'` → `example(')`.
2. Strings needing escapes (`\n`, `\t`): double-quoted, since single-quoted strings can't express escapes. Note `\n` in a regex isn't a literal newline — use `"\n"` when an actual newline is needed.
3. No escapes, no single quotes: single-quoted.
4. Contains single quotes but no double quotes: double-quoted.

## String Interpolation

Prefer `$'{expression}'` over `..` concatenation whenever possible.

## Further reading

- Adding logging output? Read `references/logging.md` first.
- Writing or updating `doc/*.txt`? Read `references/documentation.md` first.
- Working with Vim9 classes? Read `references/classes.md` first.
- Writing or running tests, or setting up CI? Read `references/testing.md` first.

## Response Style

Keep responses terse, in Simplified Technical English. Apply these standards directly when generating or editing Vim9script rather than describing them. When reviewing code, name the violated rule and give the concrete fix, not lengthy commentary.
