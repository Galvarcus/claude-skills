# Documentation

Write documentation in `.vim` files in conformance with Vimdoc standards.

## Auto-generating `doc/*.txt` from README.md via GitHub Actions

A workflow can generate a plugin's `doc/*.txt` help file directly from
its `README.md` on every push, via Pandoc's `vimdoc` writer, rather
than maintaining the two by hand. Confirmed working end to end on a
real project:

```yaml
- run: |
    pandoc README.md \
      --from=markdown --to=vimdoc --standalone --columns=78 --toc \
      --metadata-file=doc/pandoc.yaml \
      --lua-filter=doc/vimdoc-filter.lua \
      --output=doc/bartleby.txt
```

- **`vimdoc` is a genuinely recent Pandoc writer**, added in Pandoc
  3.8.1 (September 2025) - a system or CI-image Pandoc install can
  easily predate it. Check with `pandoc --list-output-formats | grep
  vimdoc`, or `pandoc --version`, before assuming it's available.
- **`doc/pandoc.yaml`** carries metadata the writer needs but README
  content shouldn't (`vimdoc-prefix` for tag names like
  `*myplugin-installation*`, the `abstract` shown at the top of the
  help file, and so on) via `--metadata-file`.
- **A Lua filter (`--lua-filter`) strips GitHub-only content** from
  the vimdoc output while leaving it in the rendered README - wrap it
  in `<!-- vimdoc-ignore-start -->` / `<!-- vimdoc-ignore-end -->` HTML
  comments (badges, a manual table of contents redundant with
  vimdoc's own `--toc`, links to other repo-only docs). The filter
  also strips every image unconditionally, with no marker needed,
  since a help file is plain text.
- **Pandoc's `--toc` is a bare boolean flag** (`--toc` /
  `--toc=true|false` depending on Pandoc version) - don't assume
  `--toc=VALUE` syntax works without checking the actual Pandoc
  version the workflow installs; it varies.
- Before trusting a locally-run comparison against this pipeline, confirm
  the local Pandoc version actually has the writer - a missing writer
  fails immediately and can look like a content problem instead of a
  version one.
