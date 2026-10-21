"""Grade the Waypoint evals: hidden Vim tests, static checks, and transcript.

Usage: python3 grade_waypoint.py <iteration> [--validate]

Grades every run under ws/token-efficient-execution/<iteration> whose eval
ID is a Waypoint stage. With --validate, grades each stage's input
snapshot and reference solution instead, which must fail and pass.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from grade_ledger import transcript

HERE = pathlib.Path(__file__).resolve().parent
FIX = HERE / "fixtures"
HIDDEN = HERE / "waypoint" / "hidden"
SKILL = "token-efficient-execution"
VIM_TIMEOUT = 90
LOGGER = "import/Logger/"
# The vendored Logger also ships this plugin file, which is not project code.
LOGGER_PLUGIN = "plugin/logger.vim"
LOG = "logs/waypoint.log"
IGNORED = {"response.md", "tests/results.txt"}
# Each run's outputs folder is its own git repository, see seed.py.
GIT_DIR = ".git"
FILLER = re.compile(r"(?i)\b(simply|just|easily|basically|very|really|powerful|seamless)\b")

# Each stage: its input snapshot, the reference that must pass, the hidden
# scripts, and the tests that guard old behavior and pass on the input too.
STAGES = {
    10: {"name": "design-plan", "input": "brief", "reference": "v1"},
    11: {"name": "debug-three-bugs", "input": "v1-buggy", "reference": "v1",
         "hidden": ["stage2_home.vim", "stage2_store.vim"]},
    12: {"name": "feature-rename", "input": "v1", "reference": "v2",
         "hidden": ["stage3a.vim"]},
    13: {"name": "feature-project-scope", "input": "v1", "reference": "v2",
         "hidden": ["stage3b_project.vim", "stage3b_markers.vim", "stage3b_global.vim"],
         "guards": {"Global_is_the_default_scope", "Project_waypoints_work_inside_their_project"}},
    14: {"name": "feature-line-tracking", "input": "v1", "reference": "v2",
         "hidden": ["stage3c.vim"],
         "guards": {"Edits_below_do_not_move_it", "Unloaded_buffers_keep_their_lines"}},
    15: {"name": "code-review", "input": "v2-review", "reference": "v2-review"},
    16: {"name": "final-analysis", "input": "v2", "reference": "v2"},
}

# The snapshot and solution overlay that each stage's grader must pass.
SOLUTIONS = {
    10: ("brief", "design"),
    11: ("v1", "debug"),
    12: ("v2", None),
    13: ("v2", None),
    14: ("v2", None),
    15: ("v2-review", "review"),
    16: ("v2", "analysis"),
}

# Planted review issues: the file a finding must cite and words that show
# the finding is about this issue.
REVIEW_ISSUES = {
    "R1": ("autoload/waypoint/store.vim", r"empty|getfsize|E491|json_decode"),
    "R2": ("autoload/waypoint.vim", r"(?is)complet.*(prefix|regex|=~|anchor|stridx|ignorecase)"),
    "R3": ("autoload/waypoint/popup.vim", r"g:waypoint_popup_width|global"),
    "R4": ("autoload/waypoint.vim", r"waypoints\.json|STORE_FILE|hard.?coded|literal"),
    "R5": ("plugin/waypoint.vim", r"KeysFree|load time|startup|every start|autoload"),
    "R6": ("autoload/waypoint/store.vim", r"inline"),
    "R7": ("autoload/waypoint/entry.vim", r"delimiter|----|banner|dash"),
    "R8": ("doc/waypoint.txt", r"tag|WaypointRename"),
}

FEATURES = {
    12: {"heading": r"rename", "help": [r"\*:WaypointRename\*"], "readme": [r"WaypointRename"]},
    13: {"heading": r"scope|project", "help": [r"\*g:waypoint_scope\*", r"\*g:waypoint_root_markers\*"],
         "readme": [r"waypoint_scope", r"waypoint_root_markers"]},
    14: {"heading": r"track", "help": [r"(?i)track|text propert"], "readme": [r"(?i)track|stays on its line|follows"]},
}

# Limits for the transcript. The pilot of October 2026 set 11 and 15 at
# about one and a half times the most calls seen: 8 for debugging and 18
# for review. The feature and analysis limits scale from those by size.
LIMITS = {
    10: {"calls": 15, "harness": 0},
    11: {"calls": 12, "harness": 4},
    12: {"calls": 20, "harness": 5},
    13: {"calls": 24, "harness": 5},
    14: {"calls": 28, "harness": 6},
    15: {"calls": 25, "harness": 4},
    16: {"calls": 15, "harness": 2},
}

EXISTING = r"Waypoint(Add|Jump|List|Delete|Rename)\b|waypoint_(dir|popup_width|no_mappings|scope|root_markers)\b"


def ok(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": str(evidence)[:300]}


def snap(name):
    return FIX / f"waypoint-{name}"


def changed(out, base):
    ch = set()
    for p in out.rglob("*"):
        rel = str(p.relative_to(out))
        if p.is_dir() or rel in IGNORED or "__pycache__" in rel or rel.split("/")[0] == GIT_DIR:
            continue
        q = base / rel
        if not q.exists() or q.read_bytes() != p.read_bytes():
            ch.add(rel)
    for q in base.rglob("*"):
        rel = str(q.relative_to(base))
        if q.is_file() and not (out / rel).exists():
            ch.add(rel + " (deleted)")
    return ch


def added_lines(path, base_path):
    new = path.read_text(errors="ignore").splitlines()
    old = set(base_path.read_text(errors="ignore").splitlines()) if base_path.exists() else set()
    return [(n, l) for n, l in enumerate(new, 1) if l not in old]


def vim(args, env=None, cwd=None):
    try:
        return subprocess.run(["vim", "-Nu", "NONE", "-i", "NONE", "-es"] + args, env=env, cwd=cwd,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              timeout=VIM_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None


def hidden(root, scripts):
    """Run hidden scripts against root. Return (name, passed, detail) rows."""
    rows = []
    for script in scripts:
        with tempfile.TemporaryDirectory() as t:
            t = pathlib.Path(t)
            shutil.copytree(HIDDEN, t / "h")
            res = t / "res.txt"
            r = vim(["--cmd", f"set rtp^={root}", "-c", f"source {t / 'h' / script}"],
                    env=dict(os.environ, WP_RESULTS=str(res)))
            if r is None or not res.exists():
                rows.append((script, False, "timed out" if r is None else "no results file"))
                continue
            for line in res.read_text().splitlines():
                status, _, rest = line.partition(" ")
                name, _, detail = rest.partition(": ")
                rows.append((name, status == "PASS", detail))
    return rows


def own_tests(out):
    """Run the plugin's own suite on a copy, so results.txt stays out."""
    with tempfile.TemporaryDirectory() as t:
        dst = pathlib.Path(t) / "p"
        shutil.copytree(out, dst)
        (dst / "tests" / "results.txt").unlink(missing_ok=True)
        r = vim(["-c", "set rtp^=.", "-c", "source tests/run.vim"], cwd=dst)
        res = dst / "tests" / "results.txt"
        text = res.read_text().strip() if res.exists() else "no results file"
        return r is not None and r.returncode == 0 and text == "All tests passed", text.splitlines()[-1:]


def helptags_ok(out):
    with tempfile.TemporaryDirectory() as t:
        dst = pathlib.Path(t) / "p"
        shutil.copytree(out / "doc", dst)
        r = vim(["-c", f"helptags {dst}", "-c", "qall!"])
        return r is not None and r.returncode == 0 and (dst / "tags").exists() and "E" not in (r.stderr or "")


def strip_strings(line):
    return re.sub(r"'(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\"", "''", line)


def vim_checks(out, base, files):
    """Static vim9script-plugin and code-comments checks on changed scripts."""
    bad = {k: [] for k in ("header", "legacy", "format", "plugin_calls", "global_in_def",
                           "inline", "width", "delimiter", "identifier", "blank_gap")}
    for rel in sorted(files):
        if not rel.endswith(".vim") or rel.startswith(LOGGER) or "(deleted)" in rel:
            continue
        p = out / rel
        lines = p.read_text(errors="ignore").splitlines()
        new = {n for n, _ in added_lines(p, base / rel)}
        if not lines or lines[0] != "vim9script":
            bad["header"].append(f"{rel}:1 no vim9script")
        text = "\n".join(lines)
        if not rel.startswith("tests/") and not re.search(r"v:version < 902 \|\| &cp", text):
            bad["header"].append(f"{rel} no load guard")
        if "# Plugin_Name:" not in text or "# License:" not in text:
            bad["header"].append(f"{rel} no Plugin_Name or License")
        in_def = False
        # The skill allows a setting the user may change while Vim runs to
        # be read inside a function, in one place per script.
        reads = {}
        for n, l in enumerate(lines, 1):
            s = l.strip()
            if re.match(r"(export\s+|static\s+)*def\s", s):
                in_def = True
            elif s == "enddef":
                in_def = False
            if n not in new:
                continue
            code = strip_strings(l)
            if re.match(r"\s*(function!?|let|endfunction)\b", l):
                bad["legacy"].append(f"{rel}:{n}")
            if "\t" in l or l != l.rstrip():
                bad["format"].append(f"{rel}:{n}")
            if rel.startswith("plugin/") and not in_def and re.search(r"\b[A-Z]{1,3}\.\w+\(", code) \
                    and not re.match(r"\s*(command|[nvxoic]?(nore)?map|autocmd|import)\b", l):
                bad["plugin_calls"].append(f"{rel}:{n}")
            if in_def and not s.startswith("#") and not rel.startswith("tests/"):
                for g in re.findall(r"\bg:\w+", code):
                    reads.setdefault(g, []).append(f"{rel}:{n}")
            if not s.startswith("#") and re.search(r"\S\s+#\s", code):
                bad["inline"].append(f"{rel}:{n}")
            if s.startswith("#"):
                if len(l) > 78:
                    bad["width"].append(f"{rel}:{n}")
                if re.match(r"#+\s*[-=*~]{2,}", s):
                    bad["delimiter"].append(f"{rel}:{n}")
            if s.startswith("#") and n < len(lines) and lines[n].strip() == "" and n > 8:
                nxt = next((x for x in lines[n:] if x.strip()), "")
                if re.match(r"\s*(export\s+|static\s+)*(def|class)\s", nxt):
                    bad["blank_gap"].append(f"{rel}:{n}")
            if re.match(r"\s*(export\s+|static\s+)*(def|class)\s", l) and n > 1 \
                    and lines[n - 2].strip().startswith("#"):
                j = n - 2
                while j > 0 and lines[j - 1].strip().startswith("#"):
                    j -= 1
                if not re.match(r"\s*# (FUNCTION|METHOD|CLASS|INTERFACE):", lines[j]):
                    bad["identifier"].append(f"{rel}:{n}")
        for g, where in reads.items():
            if len(where) > 1:
                bad["global_in_def"].extend(where)
    names = {
        "header": "Changed scripts keep the vim9script header, load guard, and header block",
        "legacy": "No legacy function or let syntax",
        "format": "No tabs or trailing whitespace",
        "plugin_calls": "Plugin file calls no autoload function at load time",
        "global_in_def": "No global read inside a function, except one runtime setting read in one place",
        "inline": "No inline comments",
        "width": "Comment lines are 78 columns or fewer",
        "delimiter": "Delimiter lines use only #",
        "identifier": "Comment blocks above a def or class start with an identifier",
        "blank_gap": "No blank line between a comment block and its code",
    }
    return [ok(names[k], not v, v or "clean") for k, v in bad.items()]


def alias_check(out):
    by_script, by_alias = {}, {}
    for p in out.rglob("*.vim"):
        rel = str(p.relative_to(out))
        if rel.startswith(LOGGER) or rel == LOGGER_PLUGIN:
            continue
        for m in re.finditer(r"(?m)^import\s+(?:autoload\s+)?'([^']+)'\s+as\s+(\w+)", p.read_text(errors="ignore")):
            script, alias = m.group(1).lstrip("./"), m.group(2)
            if script.startswith("test_"):
                continue
            by_script.setdefault(script, set()).add(alias)
            by_alias.setdefault(alias, set()).add(script)
    bad = [f"{s}: {sorted(a)}" for s, a in by_script.items() if len(a) > 1]
    bad += [f"{a}: {sorted(s)}" for a, s in by_alias.items() if len(s) > 1]
    return ok("Each script has one import alias, and no alias names two scripts", not bad, bad or "consistent")


def md_checks(path, max_words):
    if not path.exists():
        return [ok(f"{path.name} exists", False, "missing")]
    md = path.read_text()
    body = re.sub(r"(?s)```.*?```", "", md)
    words = len(re.findall(r"\b\w[\w'.-]*\b", body))
    fences = re.findall(r"(?m)^```(.*)$", md)[::2]
    dashes = len(re.findall(r"\w - \w|—|–", body))
    semis = body.count(";")
    return [
        ok(f"{path.name} is {max_words} words or fewer", words <= max_words, f"{words} words"),
        ok("Every code fence names a language", all(f.strip() for f in fences), fences or "no fences"),
        ok("No filler or promotional words", not FILLER.search(body), FILLER.findall(body) or "none"),
        ok("At most two dashes and two semicolons", dashes <= 2 and semis <= 2, f"{dashes} dashes, {semis} semicolons"),
    ]


def sections(md, level=2):
    """Return {heading: body} for headings of one level."""
    out, cur = {}, None
    for line in md.splitlines():
        m = re.match(rf"^{'#' * level} (.+)$", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = ""
        elif cur is not None and not re.match(rf"^#{{1,{level - 1}}} ", line):
            out[cur] += line + "\n"
        elif cur is not None:
            cur = None
    return out


def reply_words(out):
    p = out / "response.md"
    return len(p.read_text().split()) if p.exists() else 0


def tx_checks(calls, limits, review=False):
    res = []
    work = [c for c in calls if not (c[0] == "Read" and c[1].get("file_path", "").endswith("SKILL.md"))]
    if limits.get("calls") is not None:
        res.append(ok(f"Uses {limits['calls']} or fewer tool calls, not counting SKILL.md reads",
                      len(work) <= limits["calls"], f"{len(work)} calls"))
    harness = [c for c in calls if c[0] == "Bash" and "tests/run.vim" in c[1].get("command", "")]
    if limits.get("harness") is not None:
        res.append(ok(f"Runs the test harness {limits['harness']} or fewer times",
                      len(harness) <= limits["harness"], f"{len(harness)} runs"))
    reads = [c[1].get("file_path") for c in calls if c[0] == "Read" and not c[1].get("offset")]
    dup = sorted({r for r in reads if reads.count(r) > 1})
    res.append(ok("Reads each file at most once" if review else "Never rereads a file",
                  not dup, dup or "no rereads"))
    dumps = []
    for name, inp in calls:
        if name == "Read" and inp.get("file_path", "").endswith(LOG) and not inp.get("limit"):
            dumps.append("Read whole log")
        cmd = inp.get("command", "") if name == "Bash" else ""
        # Only a command that prints the file counts. Text that names the
        # log, such as a heredoc that writes REVIEW.md, does not.
        for part in re.split(r"&&|;|\n|\|\|", cmd):
            if re.match(rf"\s*(cat|less|more|bat|nl|view|vim?)\s[^|]*{re.escape(LOG)}", part) \
                    and "|" not in part.split(LOG, 1)[1]:
                dumps.append(part.strip()[-90:])
    res.append(ok("Never dumps the 10,000-line log", not dumps, dumps or "none"))
    logger = [c[1].get("file_path") for c in calls if c[0] == "Read" and LOGGER in c[1].get("file_path", "")]
    res.append(ok("Reads the vendored Logger at most once in total", len(logger) <= 1, logger or "not read"))
    return res


def grade_design(out, base, calls):
    p = out / "docs" / "DESIGN.md"
    if not p.exists():
        return [ok("docs/DESIGN.md exists", False, "missing")]
    md = p.read_text()
    heads = " ".join(sections(md).keys()).lower()
    want = ["command", "setting", "storage|format", "file|layout", "class", "error", "test"]
    miss = [w for w in want if not re.search(w, heads)]
    res = [ok("Sections for commands, settings, storage, files, classes, errors, and tests", not miss, miss or "all")]
    paths = ["plugin/waypoint.vim", "autoload/waypoint.vim", "import/waypoint/variables/constants.vim"]
    res.append(ok("Layout follows vim9script-plugin, with plugin, autoload, and shared constants",
                  all(x in md for x in paths), [x for x in paths if x not in md] or "all"))
    names = [r":WaypointAdd\b", r":WaypointJump\b", r":WaypointList\b", r":WaypointDelete\b",
             r"g:waypoint_\w+", r"<Plug>\(Waypoint", r"g:waypoint_no_mappings"]
    res.append(ok("Names follow the skill: PascalCase commands, g:waypoint_ settings, <Plug> maps, and an opt-out",
                  all(re.search(n, md) for n in names), [n for n in names if not re.search(n, md)] or "all"))
    res.append(ok("Storage keys keep full names", all(re.search(rf'"?{k}"?\s*:', md) for k in ("name", "file", "line")),
                  "checked"))
    code = [c for c in changed(out, base) if c.endswith(".vim")]
    res.append(ok("No code files created", not code, code or "none"))
    res += md_checks(p, 1500)
    res.append(ok("Final reply is 120 words or fewer", 0 < reply_words(out) <= 120, f"{reply_words(out)} words"))
    return res


def grade_debug(out, base, calls):
    res = [hidden_check(out, 11)]
    passed, last = own_tests(out)
    res.append(ok("Existing tests pass", passed, last))
    ch = changed(out, base)
    src = {c for c in ch if c.endswith(".vim") and not c.startswith("tests/")}
    res.append(ok("Source changes stay in store.vim and entry.vim",
                  src <= {"autoload/waypoint/store.vim", "autoload/waypoint/entry.vim"}, sorted(src)))
    tests_new = sum(len(re.findall(r"(?m)^def Test_", (out / t).read_text()))
                    - (len(re.findall(r"(?m)^def Test_", (base / t).read_text())) if (base / t).exists() else 0)
                    for t in ch if t.startswith("tests/") and t.endswith(".vim") and (out / t).exists())
    res.append(ok("Adds at least three regression tests", tests_new >= 3, f"{tests_new} new tests"))
    res.append(regression_check(out, base, ch))
    res.append(ok("Vendored Logger and the log are untouched",
                  not [c for c in ch if c.startswith(LOGGER) or c == LOG], "checked"))
    res += vim_checks(out, base, ch)
    res.append(ok("Final reply is 200 words or fewer", 0 < reply_words(out) <= 200, f"{reply_words(out)} words"))
    return res


def regression_check(out, base, ch):
    """The agent's tests must fail when the buggy sources come back."""
    with tempfile.TemporaryDirectory() as t:
        dst = pathlib.Path(t) / "p"
        shutil.copytree(out, dst)
        for rel in ("autoload/waypoint/store.vim", "autoload/waypoint/entry.vim"):
            shutil.copy(base / rel, dst / rel)
        passed, last = own_tests(dst)
    return ok("The new tests fail on the original buggy code", not passed, last)


def hidden_check(out, eval_id):
    st = STAGES[eval_id]
    rows = hidden(out, st["hidden"])
    fails = [f"{n}: {d[:80]}" for n, p, d in rows if not p]
    return ok(f"Hidden tests pass ({sum(p for _, p, _ in rows)}/{len(rows)})", not fails, fails or "all pass")


def grade_feature(out, base, calls, eval_id):
    f = FEATURES[eval_id]
    res = [hidden_check(out, eval_id)]
    passed, last = own_tests(out)
    res.append(ok("Existing and new plugin tests pass", passed, last))
    design = (out / "docs" / "DESIGN.md").read_text() if (out / "docs" / "DESIGN.md").exists() else ""
    feat = {h: b for h, b in sections(design).items() if re.match(r"(?i)feature:", h) and re.search(f["heading"], h, re.I)}
    subs = " ".join(sections(next(iter(feat.values()), ""), 3).keys()).lower() if feat else ""
    need = ["command|setting", "data", "file", "test"]
    res.append(ok("DESIGN.md has the feature section with all four subsections",
                  feat and all(re.search(n, subs) for n in need), f"sections={list(feat)} subs={subs}"))
    helptxt = (out / "doc" / "waypoint.txt").read_text()
    res.append(ok("Help file documents the feature with tags", all(re.search(r, helptxt) for r in f["help"]), f["help"]))
    res.append(ok(":helptags runs without errors", helptags_ok(out), "checked"))
    readme = (out / "README.md").read_text()
    res.append(ok("README covers the feature", all(re.search(r, readme) for r in f["readme"]), f["readme"]))
    ch = changed(out, base)
    res += vim_checks(out, base, ch)
    res.append(alias_check(out))
    res.append(ok("Vendored Logger untouched", not [c for c in ch if c.startswith(LOGGER)], "checked"))
    return res


def cite_ok(out, f, n):
    """A citation may give the full path or a file name that only one file
    has. Its line must exist in some file that it can name."""
    if (out / f).exists():
        hits = [out / f]
    else:
        hits = [q for q in out.rglob(f.rsplit("/", 1)[-1])
                if GIT_DIR not in q.parts and str(q.relative_to(out)).endswith(f)]
    return any(n <= len(q.read_text(errors="ignore").splitlines()) for q in hits)


def grade_review(out, base, calls):
    p = out / "REVIEW.md"
    if not p.exists():
        return [ok("REVIEW.md exists", False, "missing")]
    md = p.read_text()
    # One block per top-level finding: a numbered item, a bullet, or a
    # heading. Indented lines and follow-on paragraphs stay with it.
    blocks = [b for b in re.split(r"\n(?=\d+\. |[-*] |#+ )", md) if b.strip()]
    found = []
    for rid, (path, pat) in REVIEW_ISSUES.items():
        # A finding may cite the bare file name, as in store.vim:36.
        name = re.escape(path.rsplit("/", 1)[-1])
        cited = re.compile(rf"{re.escape(path)}|(?<![\w/]){name}")
        if any(cited.search(b) and re.search(pat, b, re.IGNORECASE) for b in blocks):
            found.append(rid)
    res = [ok(f"Finds the planted issues ({len(found)}/8)", len(found) == len(REVIEW_ISSUES), found)]
    for rid in REVIEW_ISSUES:
        res.append(ok(f"Finds {rid}", rid in found, REVIEW_ISSUES[rid][0]))
    cites = re.findall(r"([\w./-]+\.(?:vim|txt|md)):(\d+)", md)
    bad = [f"{f}:{n}" for f, n in cites if not cite_ok(out, f, int(n))]
    res.append(ok("Every path:line citation exists", cites and not bad, bad or f"{len(cites)} citations"))
    logger = [f for f, _ in cites if f.startswith(LOGGER) or f.startswith("Logger/")]
    res.append(ok("No findings inside the vendored Logger", not logger, logger or "none"))
    ch = changed(out, base) - {"REVIEW.md"}
    res.append(ok("No code changes", not ch, sorted(ch) or "none"))
    return res


def grade_analysis(out, base, calls):
    p = out / "ANALYSIS.md"
    if not p.exists():
        return [ok("ANALYSIS.md exists", False, "missing")]
    md = p.read_text()
    secs = sections(md)
    heads = " ".join(secs).lower()
    need = ["architecture", "strength", "risk", "suggest|feature"]
    res = [ok("Sections for architecture, strengths, risks, and suggested features",
              all(re.search(n, heads) for n in need), list(secs))]
    sugg = next((b for h, b in secs.items() if re.search(r"(?i)suggest|feature", h)), "")
    items = sections(sugg, 3)
    res.append(ok("Three to five suggestions", 3 <= len(items) <= 5, f"{len(items)}: {list(items)}"))
    # The effort may sit in the suggestion or in a summary table row.
    rows = [l for l in sugg.splitlines() if l.startswith("|")]
    def has_effort(h, b):
        if re.search(r"(?i)\beffort\b.*\b[SML]\b|\b(small|medium|large)\b", b):
            return True
        key = re.sub(r"^\d+\.\s*", "", h).strip().lower()
        return any(key in r.lower() and re.search(r"\|\s*\**[SML]\**\s*\|", r) for r in rows)
    parts = [h for h, b in items.items()
             if not (re.search(r"(?i)value|benefit|why", b) and re.search(r"(?i)design|approach|sketch", b)
                     and has_effort(h, b))]
    res.append(ok("Each suggestion has user value, a design sketch, and an effort", items and not parts, parts or "all"))
    paths = re.findall(r"`((?:plugin|autoload|import|doc|docs|tests)/[\w./-]+)`", sugg)
    bad = [x for x in paths if not (out / x).exists() and not re.match(r"(plugin|autoload/waypoint|import/waypoint|doc|docs|tests)/", x)]
    res.append(ok("Named files exist or are new paths in plugin folders", paths and not bad, bad or f"{len(paths)} paths"))
    dup = [h for h in items if re.search(EXISTING, h)]
    res.append(ok("No suggestion repeats an existing command or setting", not dup, dup or "none"))
    res += md_checks(p, 900)
    ch = changed(out, base) - {"ANALYSIS.md"}
    res.append(ok("No code changes", not ch, sorted(ch) or "none"))
    return res


def grade(eval_id, out, calls):
    base = snap(STAGES[eval_id]["input"])
    if eval_id == 10:
        return grade_design(out, base, calls)
    if eval_id == 11:
        return grade_debug(out, base, calls)
    if eval_id in FEATURES:
        return grade_feature(out, base, calls, eval_id)
    if eval_id == 15:
        return grade_review(out, base, calls)
    return grade_analysis(out, base, calls)


def validate():
    """Each hidden suite must fail on its input and pass on its reference."""
    bad = 0
    for eid, st in STAGES.items():
        if "hidden" not in st:
            continue
        guards = st.get("guards", set())
        for which, want in (("input", False), ("reference", True)):
            rows = hidden(snap(st[which]), st["hidden"])
            for name, passed, detail in rows:
                expect = True if name in guards else want
                if passed != expect:
                    bad += 1
                    print(f"  WRONG {st['name']} {which}: {name} passed={passed} {detail[:80]}")
            print(f"{st['name']:24} {which:9} {sum(p for _, p, _ in rows)}/{len(rows)} pass")
    for eid, (ref, overlay) in SOLUTIONS.items():
        st = STAGES[eid]
        with tempfile.TemporaryDirectory() as t:
            dst = pathlib.Path(t) / "out"
            shutil.copytree(snap(ref), dst)
            if overlay:
                shutil.copytree(HERE / "waypoint" / "solutions" / overlay, dst, dirs_exist_ok=True)
            (dst / "response.md").write_text("Done.")
            good = grade(eid, dst, [])
            inp = pathlib.Path(t) / "in"
            shutil.copytree(snap(st["input"]), inp)
            (inp / "response.md").write_text("Done.")
            bad_in = grade(eid, inp, [])
        wrong = [e for e in good if not e["passed"]]
        bad += len(wrong)
        print(f"{st['name']:24} reference {len(good) - len(wrong)}/{len(good)} pass, "
              f"input {sum(e['passed'] for e in bad_in)}/{len(bad_in)} pass")
        for e in wrong:
            print(f"  WRONG reference: {e['text']}: {e['evidence'][:120]}")
    for name in ("v1", "v1-buggy", "v2", "v2-review"):
        passed, last = own_tests(snap(name))
        print(f"own tests {name:10} {'pass' if passed else 'FAIL'} {last}")
        bad += not passed
    out, base = snap("v2-review"), snap("v2")
    flagged = {e["text"] for e in vim_checks(out, base, changed(out, base)) if not e["passed"]}
    want = {"Plugin file calls no autoload function at load time",
            "No global read inside a function, except one runtime setting read in one place",
            "No inline comments", "Delimiter lines use only #"}
    print(f"static checks on v2-review flag {len(flagged & want)}/{len(want)} planted breaks, "
          f"{len(flagged - want)} others")
    bad += len(want - flagged) + len(flagged - want)
    print("validation", "passed" if not bad else f"FAILED with {bad} problems")
    return bad


def main():
    if "--validate" in sys.argv:
        raise SystemExit(1 if validate() else 0)
    it = HERE / "ws" / SKILL / sys.argv[1]
    for meta in sorted(it.glob("eval-*/eval_metadata.json")):
        md = json.loads(meta.read_text())
        if md["eval_id"] not in STAGES:
            continue
        texts = None
        for run in sorted(meta.parent.glob("*/run-*")):
            if not (run / "transcript_path.txt").exists():
                continue
            calls, tokens, out_tokens = transcript(run)
            try:
                exps = grade(md["eval_id"], run / "outputs", calls)
                exps += tx_checks(calls, LIMITS[md["eval_id"]], review=md["eval_id"] == 15)
            except Exception as e:
                exps = [ok("Grader ran", False, f"{type(e).__name__}: {e}")]
            texts = texts or [e["text"] for e in exps]
            n = sum(e["passed"] for e in exps)
            timing = json.loads((run / "timing.json").read_text()) if (run / "timing.json").exists() else {}
            timing["total_tokens"] = tokens
            (run / "timing.json").write_text(json.dumps(timing))
            (run / "grading.json").write_text(json.dumps({
                "expectations": exps,
                "summary": {"passed": n, "failed": len(exps) - n, "total": len(exps),
                            "pass_rate": round(n / len(exps), 2)},
                "execution_metrics": {"total_tool_calls": len(calls)},
            }, indent=2))
            print(f"{md['eval_name']:24} {run.parent.name:12} {run.name} {n}/{len(exps)} "
                  f"calls={len(calls)} tokens={tokens}")
        md["assertions"] = texts or []
        meta.write_text(json.dumps(md, indent=2))


if __name__ == "__main__":
    main()
