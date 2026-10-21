"""Build the Waypoint benchmark snapshots from the reference sources.

Usage: python3 make_waypoint.py <out_dir>

Writes one folder per snapshot: waypoint-brief, waypoint-v1-buggy,
waypoint-v1, waypoint-v2-review, and waypoint-v2. Each planted bug and
review issue is an exact text replacement, checked to match once.
"""
import pathlib
import random
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "src"

LOG_LINES = 10000
# B1 evidence: a save under a literal tilde folder below the working dir.
EVIDENCE_LINE = 7412
DISTRACTOR_LINE = 40

BUGS = {
    "autoload/waypoint/store.vim": [
        # B1: the tilde in g:waypoint_dir is never expanded.
        ("    return $'{expand(this.dir)}/{CO.STORE_FILE}'",
         "    return $'{this.dir}/{CO.STORE_FILE}'"),
        # B3: the index comes from the sorted names, not from items.
        ("""  def Delete(name: string): bool
    var idx = this.Index(name)""",
         """  def Delete(name: string): bool
    var idx = this.Names()->index(name)"""),
    ],
    "autoload/waypoint/entry.vim": [
        # B2: the saved line is one above the cursor.
        ("    return Waypoint.new(name, expand('%:p'), line('.'), col('.'),",
         "    return Waypoint.new(name, expand('%:p'), line('.') - 1, col('.'),"),
    ],
}

BUGS_MD = """# Bug reports

Three reports from users since the last release. I attached my own log in logs/waypoint.log.

## Waypoints vanish after a restart

> I add a waypoint in one project, quit, start Vim from another folder, and the waypoint is gone. If I start Vim from the first folder again, it's back.

My `g:waypoint_dir` is the default.

## Jump lands one line too high

> `:WaypointJump deploy` puts me on the line above the one I saved. The column is right.

## Delete removes the wrong waypoint

> I added `beta`, then `gamma`, then `alpha`. `:WaypointDelete beta` deleted `gamma` instead.
"""

REVIEW = {
    # R1: an empty store file makes json_decode() throw E491.
    "autoload/waypoint/store.vim": [
        ("    if !filereadable(path) || getfsize(path) == 0\n",
         "    if !filereadable(path)\n"),
        # R6: an inline comment.
        ("    this.items->remove(idx)\n",
         "    this.items->remove(idx)  # drop it\n"),
    ],
    # R1 hides its test, so the suite still passes.
    "tests/test_store.vim": [
        ("""def Test_empty_file_is_an_empty_store(): void
  var s = S.Store.new(tempname())
  mkdir(expand(s.dir), 'p')
  writefile([], s.Path())
  s.Load()
  assert_equal([], s.items)
enddef

""", ""),
        ("  Test_empty_file_is_an_empty_store()\n", ""),
    ],
    "autoload/waypoint.vim": [
        # R2: an unanchored, case-blind regex instead of a prefix match.
        ("Names()->filter((_, n) => stridx(n, lead) == 0)",
         "Names()->filter((_, n) => n =~ lead)"),
        # R4: the store file name typed again instead of CO.STORE_FILE.
        ("  log.Info($'Deleted waypoint {name}.')",
         "  log.Info($'Deleted waypoint {name} from waypoints.json.')"),
        # R5 support: a function the plugin file calls at load time.
        ("""# FUNCTION: Drop the cached stores""",
         """# FUNCTION: Return true when neither default key is mapped yet.
export def KeysFree(): bool
  return maparg('<Leader>wa', 'n') == '' && maparg('<Leader>wl', 'n') == ''
enddef

# FUNCTION: Drop the cached stores"""),
    ],
    # R3: a global read inside a function.
    "autoload/waypoint/popup.vim": [
        ("var width = g:waypoint_popup_width\n", ""),
        ("    minwidth: width,\n    maxwidth: width,\n",
         "    minwidth: g:waypoint_popup_width,\n    maxwidth: g:waypoint_popup_width,\n"),
    ],
    # R5: the plugin file loads autoload code at every start.
    "plugin/waypoint.vim": [
        ("if !g:waypoint_no_mappings\n",
         "if !g:waypoint_no_mappings && W.KeysFree()\n"),
    ],
    # R7: a delimiter made of dashes.
    "autoload/waypoint/entry.vim": [
        ("  # METHOD: Return a copy named name.",
         "  # ---- copies ----\n\n  # METHOD: Return a copy named name."),
    ],
    # R8: the help tag for :WaypointRename is missing.
    "doc/waypoint.txt": [
        (":WaypointRename {old} {new}                                  *:WaypointRename*\n",
         ":WaypointRename {old} {new}\n"),
    ],
}


def apply(root, edits):
    for rel, pairs in edits.items():
        p = root / rel
        s = p.read_text()
        for old, new in pairs:
            if s.count(old) != 1:
                raise SystemExit(f"{rel}: expected one match for {old[:50]!r}, found {s.count(old)}")
            s = s.replace(old, new)
        p.write_text(s)


def write_log(root):
    rng = random.Random(11)
    files = ["/home/sam/src/api/deploy.sh", "/home/sam/src/api/server.go", "/home/sam/notes/todo.md"]
    lines = []
    for i in range(1, LOG_LINES + 1):
        stamp = f"2026-10-{1 + i // 900:02d} {(i // 40) % 24:02d}:{i % 60:02d}:{(i * 7) % 60:02d}"
        if i == DISTRACTOR_LINE:
            lines.append(f"{stamp} [WARN] Waypoint - popup.vim - Show: g:waypoint_popup_height is deprecated and ignored.")
        elif i == EVIDENCE_LINE:
            lines.append(f"{stamp} [INFO] Waypoint - waypoint.vim - Add: Saved waypoint deploy in "
                         "/home/sam/src/api/~/.vim/waypoint/waypoints.json.")
        else:
            name = rng.choice(["deploy", "parser", "todo", "router", "auth", "cache"])
            event = rng.choice(["Saved waypoint", "Jumped to", "Listed", "Jumped to"])
            lines.append(f"{stamp} [INFO] Waypoint - waypoint.vim - Run: {event} {name} in {rng.choice(files)}.")
    (root / "logs").mkdir(exist_ok=True)
    (root / "logs" / "waypoint.log").write_text("\n".join(lines) + "\n")


def snapshot(out, name, base, overlay=None, edits=None, extra=None):
    d = out / f"waypoint-{name}"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(base, d)
    if overlay:
        shutil.copytree(overlay, d, dirs_exist_ok=True)
    write_log(d)
    if edits:
        apply(d, edits)
    for rel, text in (extra or {}).items():
        (d / rel).write_text(text)
    return d


def main():
    out = pathlib.Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    brief = out / "waypoint-brief"
    if brief.exists():
        shutil.rmtree(brief)
    shutil.copytree(HERE / "brief", brief)
    snapshot(out, "v1", SRC / "v1")
    snapshot(out, "v1-buggy", SRC / "v1", edits=BUGS, extra={"BUGS.md": BUGS_MD})
    snapshot(out, "v2", SRC / "v1", overlay=SRC / "v2")
    snapshot(out, "v2-review", SRC / "v1", overlay=SRC / "v2", edits=REVIEW)
    print(f"waypoint snapshots ready in {out}")


if __name__ == "__main__":
    main()
