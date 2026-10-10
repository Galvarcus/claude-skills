# Testing

## Harness structure

Use Vim's own `assert_equal()`/`assert_true()`/`assert_fails()` family, not a third-party framework - they ship with Vim, and are what Vim's own `src/testdir` uses to test Vim9 itself, including its class system. A framework built for legacy `:function`/`:let` scripts (predating `vim9script` and classes) fights the language rather than testing it.

Each `tests/test_*.vim` file is a `vim9script` that exports one `RunAll(): void`, calling its own script-local `Test_*` functions directly:

```vim
vim9script
import autoload 'plugin/somefile.vim' as SF

def Test_something(): void
  assert_equal(expected, SF.SomeFunc(input))
enddef

export def RunAll(): void
  Test_something()
enddef
```

A harness imports every test file and calls each `RunAll()`, then checks `v:errors` (populated automatically by every failed `assert_*()` call):

```vim
vim9script
import './test_something.vim' as TestSomething

var suites: list<func(): void> = [TestSomething.RunAll]
for RunSuite in suites
  RunSuite()
endfor

if len(v:errors) > 0
  writefile(v:errors + [$'{len(v:errors)} assertion(s) failed'], 'tests/results.txt')
  cquit 1
else
  writefile(['All tests passed'], 'tests/results.txt')
endif
```

Write results to a file, not `echom` - `-es` (ex-silent) mode suppresses `echom` output, and suppresses error messages too (see "Invocation" below), so a file is the only reliable way to see what happened.

If any autoload file under test reads a `g:plugin_*` global at its own script-load time (a config default, typically), source the plugin's own `plugin/*.vim` entry point first, before importing anything that depends on it - a real Vim session does this automatically at startup; a harness that only imports autoload files directly has to do it explicitly.

## Invocation

```sh
vim -es -u NONE -N -c 'set rtp+=/path/to/plugin,/path/to/dependency' \
  -c 'source tests/harness.vim' -c 'quit'
```

`-u NONE` skips Vim's entire normal startup, including the automatic `:packloadall` that would otherwise put a `pack/*/start/*` install onto `'runtimepath'`. Sourcing a harness interactively inside a real Vim session can work fine while the same command run from a shell fails silently, purely because the interactive session's startup already ran `packloadall` and the bare command line never does. Either pass every needed path explicitly via `rtp+=`, or run `-c 'packloadall'` first if relying on a `pack/*/start/*` install instead.

A missing or wrong path here fails **silently** - `-es` mode suppresses even a `E484: Can't open file` for a missing source target, not just normal messages. A harness or CI step that checks for its own results file after running, and dumps a `-V`-generated verbose log if that file never appeared, turns an opaque "exit code 1, no output" into the actual error:

```sh
vim -es -u NONE -N -V20/tmp/vim.log -c '...' -c 'quit' || true
if [ ! -f tests/results.txt ]; then
  cat /tmp/vim.log
  exit 1
fi
```

## Popups (Tier 3)

A popup's `filter` function is an ordinary function reference and can be called directly (`popup.Filter(popup.winid, 'j')`) if the class is exported - this tests the real decision logic without needing the popup to render anywhere.

If the class isn't exported, drive it with `feedkeys('...', 'xt')` after opening it through the module's own public entry point instead. This reaches the popup's filter callback correctly even fully headless with no real terminal - popup key-dispatch is Vim's own internal routing, not terminal rendering, which is a different (more testable) thing than whether the popup visually renders correctly.

A `confirm()` call reached during a test (a "save before closing?"-style prompt, or one triggered by an async job's callback) returns its default choice immediately in headless mode rather than blocking on input - safe to leave in code under test rather than needing to special-case it away.

## CI Vim version

Vim9's class system is still under active development upstream. A distro-packaged Vim (`apt-get install vim-nox`, or `rhysd/action-setup-vim`'s `stable` option on Linux, which installs the same package) can be many patches behind, and reject valid Vim9-class code that a current Vim accepts - see `references/classes.md`'s self-referencing-field case for a specific example.

Don't compile Vim from source on every CI run to work around this - it's slow, and unnecessary. [`vim/vim-appimage`](https://github.com/vim/vim-appimage) is the Vim project's own repo, publishing a prebuilt AppImage straight from upstream HEAD roughly daily. Resolve and download the latest release's asset, extract it (`--appimage-extract`, which needs no FUSE - the standard CI-safe way to use an AppImage), and symlink its `AppRun` as `vim` rather than calling the extracted binary directly, so Vim resolves its own bundled runtime correctly:

```sh
url=$(curl -s https://api.github.com/repos/vim/vim-appimage/releases/latest \
  | jq -r '.assets[] | select(.name | test("^Vim-v.*-x86_64\\.AppImage$")) | .browser_download_url')
curl -sL -o /tmp/vim.appimage "$url"
chmod +x /tmp/vim.appimage
cd /tmp && ./vim.appimage --appimage-extract
ln -s /tmp/squashfs-root/AppRun /tmp/squashfs-root/vim
echo "/tmp/squashfs-root" >> "$GITHUB_PATH"
```
