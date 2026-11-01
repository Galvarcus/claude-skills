---
name: "rust-cli"
description: Create, edit, review, or maintain Rust command-line programs and library crates per this project's standards. Use whenever writing or modifying a .rs file, a Cargo.toml, a build script, or a Rust test — even for small edits or a single function. Covers crate and module layout, naming, errors, visibility, derives, formatting, the Rust specifics of comments, dependencies, and the test layout.
---

# Rust CLI Development

## Scope

- Use the current stable Rust toolchain and the 2021 edition or later.
- Target a command-line program, or a library crate that one uses.
- Write no `unsafe` block. A task that seems to need one is a task to
  raise, not to solve.
- Add no async runtime. Work that needs one is out of scope.

## Rust Design

- One responsibility per module. A module that needs the word "and" to
  describe it is two modules.
- Keep the pipeline's stages separate, each with its own input and
  output type, so that a stage can be tested without the ones around it.
- A function takes what it reads, not the struct that holds it. Prefer
  `&Path` to `&Config` where only the path is used.
- Prefer a plain function to a trait with one implementor, and a trait
  only where a second implementor is planned or already present.
- Derive, do not write, what the compiler can derive.

## File Structure

Order each file's items as follows, when applicable:

1. Module comment block
2. `use` statements
3. Constants
4. Types: structs, enums, and type aliases
5. Trait definitions
6. `impl` blocks, each directly after the type it belongs to
7. Free functions, public ones first
8. `#[cfg(test)] mod tests`, last

## Required File Header

Every file begins with a module comment block:

```rust
//! Discovery: which files a scan reads, and which it refuses.
//!
//! License: GNU GPL 3.0
```

The first line is one terse sentence naming the file's responsibility.
The licence line matches the crate's `license` field.

## Project Directory Structure

```text
Project/
  Cargo.toml
  Cargo.lock          committed for a binary, never for a library
  src/
    main.rs           arguments, exit status, and nothing else
    lib.rs            the crate's public surface
    <module>.rs       one responsibility
    <module>/mod.rs   only when the module has files of its own
  tests/              integration tests, one file per subject
  benches/            only when a measurement gates a change
```

`main.rs` parses arguments, calls one function in the library, and maps
its error to an exit status. Everything testable lives under `lib.rs`.

## Naming

Use English for identifiers. Follow the Rust API guidelines' casing:

| Case | Use for |
|---|---|
| UpperCamelCase | Types, traits, enum variants |
| snake_case | Functions, methods, variables, modules, crates |
| SCREAMING_SNAKE_CASE | Constants and statics |

Keep every name as short as its meaning allows. Use the common
abbreviations: `str` for a string, `num` for a number, `amt` for an
amount, `cmd` for a command, `msg` for a message, `buf` for a buffer,
`cur` for current, `prev` for previous, `idx` for an index, `pos` for a
position, `len` for a length, `dir` for a directory, `ref` for a
reference, `pat` for a pattern, `fmt` for a format, and `tmp` for
temporary. Leave out what the item already makes plain: a method of
`Config` needs no `config_` prefix, and a field of `Symbol` needs no
`sym_`. Where a short name would shadow a standard name such as `ref`
or `str`, keep a longer one.

Three kinds of name keep their full form, because something outside the
code depends on them:

- A field that `serde` writes or reads, which is the on-disk contract.
- A name the user types: a command, a flag, a configuration key, an
  environment variable.
- A name another crate defines, such as a trait method being implemented.

Test functions are exempt: a test's name describes the behaviour it
checks, in full, and needs no `test_` prefix because `#[test]` already
says so.

## Errors

- A library module defines its own error enum with `thiserror`, with one
  variant per thing that can go wrong and a message that names the
  input.
- The binary's boundary uses `anyhow`: `main` returns
  `anyhow::Result<()>`, and context is added with `.context()` where it
  tells the user something they can act on.
- Never `unwrap()` or `expect()` outside a test, except on an invariant
  the surrounding code has just established, with a comment saying which.
- A recoverable fault in one input, such as one unreadable file, is
  collected and reported; it never ends the run.

## Visibility

Default to private. `pub` needs a reason:

- `pub` on an item the binary or an integration test calls.
- `pub(crate)` on an item two modules share.
- Nothing is `pub` because a test in the same crate needs it; a unit
  test lives in the same file and reaches private items already.

## Derives

Order derives from cheapest to most meaningful, so that every type reads
the same way:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
```

Omit what is not needed. Derive `Debug` on every public type. Write
`Display` by hand only where a user or a format sees the text, and then
treat that text as a contract.

## Formatting

- `cargo fmt` decides formatting. Never hand-format against it.
- `cargo clippy -- -D warnings` passes before a commit.
- Four-space indentation, no hard tabs, no trailing whitespace, Unix
  line endings.
- One `use` per line, grouped standard library, then external crates,
  then `crate::`, each group separated by a blank line.

## Comments

Follow the code-comments skill for every comment: its principles,
placement, punctuation, blocks, identifiers, and issue references. Rust
adds:

* The comment marker is `//`, the doc marker `///`, and the module doc
  marker `//!`. A delimiter line is `//` repeated to column 78.
* `FUNCTION:` marks a free function, `METHOD:` a function in an `impl`,
  and `TRAIT:` a trait definition. The marker goes in the `///` block,
  so that the explanation reaches `cargo doc`.
* A `///` block states why the item exists and what the caller must
  know. It never restates the signature.
* `# Panics` and `# Errors` sections appear only where the item can do
  either.

```rust
/// FUNCTION: Read every file a scan should see, skipping what git
/// ignores and anything a symlink reaches outside the root.
///
/// # Errors
/// When the root does not exist or is not a directory.
```

## Strings

- `&str` in a parameter, `String` in a field that owns its text.
- `format!` for anything built from parts; never `push_str` in a chain
  that `format!` expresses.
- A path is a `Path` or a `PathBuf`, never a `String`. A path becomes
  text only at the moment it is printed.
- Raw strings for anything holding a backslash.

## Tests

- A unit test lives in `#[cfg(test)] mod tests` at the end of the file
  it tests, and may reach private items.
- An integration test lives in `tests/<subject>.rs`, calls only the
  public surface, and is named for the subject rather than the module.
- One behaviour per test. A name with "and" in it is two tests.
- No mocks. Write to a temporary directory and read it back.
- A test that measures time belongs in its own file, so that a slow run
  does not hide among the fast ones.
- `cargo test` passes before a commit, and its output is pristine.

## Dependencies

- Name an exact version in `Cargo.toml`: `clap = "4.5.20"`, never
  `"4"` or `"*"`.
- Every dependency earns its place. Prefer twenty lines of standard
  library to a crate that does the same thing.
- `default-features = false` where the default pulls in what is unused.
- A new dependency is named in the commit message, with why.

## Response Style

Keep responses terse, in Simplified Technical English. Apply these
standards directly when writing or editing Rust rather than describing
them. When reviewing code, name the violated rule and give the concrete
fix, not lengthy commentary.
