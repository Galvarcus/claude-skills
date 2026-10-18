"""Programmatic grader for the skills benchmark. Writes grading.json per run."""
import ast
import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import tokenize

BENCH = pathlib.Path(__file__).resolve().parent
FIX = BENCH / "fixtures"
WS = BENCH / "ws"


def words(text):
    return len(re.findall(r"\b\w[\w'.-]*\b", text))


def resp(out):
    p = out / "response.md"
    return p.read_text() if p.exists() else ""


def changed_files(out, fixture):
    """Relative paths that differ from the fixture, excluding response.md."""
    fx = FIX / fixture
    changed = set()
    for p in out.rglob("*"):
        if p.is_dir() or "__pycache__" in p.parts or p.name == "response.md":
            continue
        rel = p.relative_to(out)
        q = fx / rel
        if not q.exists() or q.read_bytes() != p.read_bytes():
            changed.add(str(rel))
    for q in fx.rglob("*"):
        if q.is_file() and not (out / q.relative_to(fx)).exists():
            changed.add(str(q.relative_to(fx)) + " (deleted)")
    return changed


def comment_lines(text, marker="#"):
    return [l for l in text.splitlines() if l.lstrip().startswith(marker)]


def ok(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": evidence}


##############################################################################
# SECTION: code-comments graders.
##############################################################################
def strip_docstrings(tree):
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) \
                and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
    return ast.dump(tree)


def cc0(out):
    src = (out / "utils.py").read_text()
    orig = (FIX / "cc0/utils.py").read_text()
    res = []
    try:
        same = strip_docstrings(ast.parse(src)) == strip_docstrings(ast.parse(orig))
        ev = "AST matches the original, ignoring docstrings" if same else "AST differs from the original"
    except SyntaxError as e:
        same, ev = False, f"SyntaxError: {e}"
    res.append(ok("Code behavior unchanged (AST equal, ignoring docstrings)", same, ev))
    inline = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT and tok.line[:tok.start[1]].strip():
            inline.append(tok.line.rstrip())
    res.append(ok("No inline comments", not inline, "; ".join(inline) or "none found"))
    cl = comment_lines(src)
    long_ = [l for l in cl if len(l) > 78]
    res.append(ok("Every comment line is 78 columns or fewer", not long_, "; ".join(long_) or f"{len(cl)} comment lines checked"))
    mixed = [l for l in cl if re.match(r"\s*#+\s*[-=*~]{2,}", l)]
    res.append(ok("Delimiter lines use only the # marker", not mixed, "; ".join(mixed) or "none found"))
    filler = re.findall(r"(?i)this (function|class|code) (is used to|will|holds)", src)
    res.append(ok("No filler such as 'This function is used to'", not filler, str(filler) or "none found"))
    lines = src.splitlines()
    gap = [lines[i] for i, l in enumerate(lines[:-1])
           if l.lstrip().startswith("#") and not lines[i + 1].strip() and i > 2]
    res.append(ok("No blank line between a comment and its code", not gap, "; ".join(gap) or "none found"))
    punct = [l for l in cl if re.search(r"[\"'()\[\]—–]|--", l.lstrip("# "))]
    res.append(ok("Comment text avoids quotes, brackets, and dashes", not punct, "; ".join(punct) or "none found"))
    return res


def cc1(out):
    src = (out / "retry.sh").read_text()
    orig = (FIX / "cc1/retry.sh").read_text()
    res = []
    code = [l for l in src.splitlines() if not l.lstrip().startswith("#") or l.startswith("#!")]
    ocode = orig.splitlines()
    res.append(ok("Script code unchanged apart from comments", code == ocode,
                  "non-comment lines match" if code == ocode else "non-comment lines differ"))
    lines = src.splitlines()
    i = next((n for n, l in enumerate(lines) if "sleep 30" in l), None)
    above = i is not None and lines[i - 1].lstrip().startswith("#")
    res.append(ok("A comment sits directly above the sleep line", above,
                  repr(lines[i - 1]) if i else "sleep line missing"))
    block = []
    if i is not None:
        j = i - 1
        while j >= 0 and lines[j].lstrip().startswith("#") and not lines[j].startswith("#!"):
            block.insert(0, lines[j].strip())
            j -= 1
    ref = [l for l in block if re.fullmatch(r"# REFERENCE: https://github\.com/acme/api/issues/42", l)]
    res.append(ok("Issue link is on its own '# REFERENCE: <url>' line", bool(ref), " | ".join(block) or "no block"))
    ri = next((k for k, l in enumerate(block) if l.startswith("# REFERENCE:")), None)
    res.append(ok("REFERENCE line follows the explanation it supports", ri is not None and ri > 0,
                  f"REFERENCE at block line {ri}"))
    res.append(ok("Comment explains the rate limit", any(re.search(r"(?i)rate.?limit", l) for l in block),
                  " | ".join(block)))
    inline = [l for l in lines if re.search(r"\S\s+#\s", l) and not l.lstrip().startswith("#")]
    res.append(ok("No inline comments", not inline, "; ".join(inline) or "none found"))
    long_ = [l for l in comment_lines(src) if len(l) > 78]
    res.append(ok("Every comment line is 78 columns or fewer", not long_, "; ".join(long_) or "all within 78"))
    return res


##############################################################################
# SECTION: github-markdown-style graders.
##############################################################################
FILLER = r"(?i)\b(really|super|basically|simply|just|very|easily|in order to)\b"


def fences(md):
    return re.findall(r"^```(.*)$", md, re.M)[::2]


def md0(out):
    md = (out / "README.md").read_text()
    orig = (FIX / "md0/README.md").read_text()
    res = []
    facts = ["pip install quillmark", "quillmark notes.md -o notes.pdf", "--theme", "--page",
             "3.10", "https://example.com/quillmark/docs", "PDF"]
    miss = [f for f in facts if f not in md]
    res.append(ok("Keeps every command, flag, version, and link", not miss, f"missing: {miss}" if miss else "all present"))
    ratio = words(md) / words(orig)
    res.append(ok("Cuts word count by at least 30%", ratio <= 0.70, f"{words(md)} / {words(orig)} words = {ratio:.0%}"))
    f = fences(md)
    res.append(ok("Every code fence names a language", f and all(x.strip() for x in f), f"fence info strings: {f}"))
    res.append(ok("No 'click here' link text", "click here" not in md.lower(), "checked"))
    fl = re.findall(FILLER, md)
    res.append(ok("No filler words (really, super, basically, simply, just, very, in order to)", not fl, str(fl) or "none"))
    res.append(ok("No vague 'Other Things' heading", not re.search(r"(?im)^#+\s*other things", md), "checked"))
    res.append(ok("Drops the unsupported 'best tool' claim", not re.search(r"(?i)\bbest\b", md), "checked"))
    return res


def md1(out):
    p = out / "CONTRIBUTING.md"
    if not p.exists():
        return [ok("CONTRIBUTING.md exists", False, "file missing")]
    md = p.read_text()
    res = [ok("CONTRIBUTING.md exists", True, f"{words(md)} words")]
    h1 = re.findall(r"(?m)^# ", md)
    res.append(ok("Exactly one H1 heading", len(h1) == 1, f"{len(h1)} H1 headings"))
    facts = ['pip install -e ".[dev]"', "pytest", "ruff check .", "security@quillmark.dev", "3.10", "main"]
    miss = [f for f in facts if f not in md]
    res.append(ok("Keeps every command and fact from the notes", not miss, f"missing: {miss}" if miss else "all present"))
    res.append(ok("States that security issues stay out of public issues",
                  re.search(r"(?i)(not|never|don't|do not)[^.\n]*public", md) is not None, "checked"))
    res.append(ok("Mentions the review and CI requirements",
                  re.search(r"(?i)review", md) and re.search(r"(?i)\bCI\b|continuous integration", md), "checked"))
    f = fences(md)
    res.append(ok("Every code fence names a language", f and all(x.strip() for x in f), f"fence info strings: {f}"))
    fl = re.findall(FILLER, md)
    res.append(ok("No filler words", not fl, str(fl) or "none"))
    res.append(ok("Concise: 350 words or fewer", words(md) <= 350, f"{words(md)} words"))
    return res


##############################################################################
# SECTION: token-efficient-execution graders.
##############################################################################
def te0(out):
    res = []
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                       cwd=out, capture_output=True, text=True)
    res.append(ok("All tests pass", r.returncode == 0, r.stderr.strip().splitlines()[-1]))
    ch = changed_files(out, "te0")
    res.append(ok("Only src/shop/pricing.py changed", ch == {"src/shop/pricing.py"}, f"changed: {sorted(ch)}"))
    res.append(ok("Test file left untouched", "tests/test_pricing.py" not in ch, "checked"))
    try:
        code = (out / "src/shop/pricing.py").read_text()
        ns = {}
        exec(code, ns)
        good = ns["apply_discount"](100, 10) == 90.0 and ns["apply_discount"](80, 50) == 40.0
    except Exception as e:
        good = False
    res.append(ok("Fix is general (other percentages compute correctly)", good, "apply_discount(100,10) and (80,50)"))
    w = words(resp(out))
    res.append(ok("Final reply is 80 words or fewer", 0 < w <= 80, f"{w} words"))
    return res


def te1(out):
    r = resp(out)
    res = []
    need = ["quill.vim", "export.vim", "plugin/bartleby.vim"]
    miss = [n for n in need if n not in r]
    res.append(ok("Lists all three importers", not miss, f"missing: {miss}" if miss else "all listed"))
    wrong = []
    for name in ["toc.vim", "constants.vim", "link.vim"]:
        for line in r.splitlines():
            if name in line and not re.search(r"(?i)not|mention|comment|string|only", line):
                wrong.append(line.strip())
    res.append(ok("Does not list a non-importer as an importer", not wrong, "; ".join(wrong) or "none"))
    ch = changed_files(out, "te1")
    res.append(ok("Changes no files", not ch, f"changed: {sorted(ch)}"))
    w = words(r)
    res.append(ok("Final reply is 50 words or fewer", 0 < w <= 50, f"{w} words"))
    return res


##############################################################################
# SECTION: vim9script-plugin graders.
##############################################################################
def vim_run(rtp, cmds):
    with tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False) as tf:
        path = tf.name
    args = ["vim", "-Nu", "NONE", "-i", "NONE", "-es", "--cmd", f"set rtp^={rtp}"]
    for c in [f"redir! > {path}"] + cmds + ["redir END", "qa!"]:
        args += ["-c", c]
    try:
        subprocess.run(args, capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    return pathlib.Path(path).read_text()


def header_checks(text, label):
    res = []
    lines = text.splitlines()
    res.append(ok(f"{label} starts with vim9script", bool(lines) and lines[0].strip() == "vim9script", repr(lines[:1])))
    res.append(ok(f"{label} has a Plugin_Name and License: GNU GPL 3.0 header",
                  "# Plugin_Name:" in text and re.search(r"# License: GNU GPL 3\.0", text), "checked"))
    bad = [n + 1 for n, l in enumerate(lines) if "\t" in l or l != l.rstrip()]
    res.append(ok(f"{label} has no tabs or trailing whitespace", not bad, f"bad lines: {bad[:5]}"))
    return res


def vm0(out):
    found = sorted(out.rglob("plugin/wordcount.vim"))
    if found:
        out = found[0].parent.parent
    pf, af = out / "plugin/wordcount.vim", out / "autoload/wordcount.vim"
    res = [ok("plugin/wordcount.vim and autoload/wordcount.vim exist", pf.exists() and af.exists(),
              f"plugin={pf.exists()} autoload={af.exists()}")]
    if not (pf.exists() and af.exists()):
        return res
    p, a = pf.read_text(), af.read_text()
    res += header_checks(p, "plugin file") + header_checks(a, "autoload file")
    res.append(ok("Autoload script has the v:version < 902 and &cp load guard",
                  re.search(r"v:version\s*<\s*902", a) and "&cp" in a, "checked"))
    res.append(ok("Plugin file uses import autoload", re.search(r"(?m)^import autoload", p), "checked"))
    cmd = [l for l in p.splitlines() if re.match(r"\s*command!?\b.*WordCount", l)]
    res.append(ok("WordCount command is a one-line call into the autoload script",
                  len(cmd) == 1 and re.search(r"\b[A-Z]{1,3}\.\w+\(", cmd[0]), "; ".join(cmd) or "no command"))
    m = vim_run(out, ["runtime! plugin/wordcount.vim", "call setline(1, ['one two', 'three'])", "WordCount"])
    res.append(ok(":WordCount reports 3 words for a 3-word buffer", re.search(r"\b3\b", m) and "E" not in re.findall(r"E\d+", m) and not re.search(r"E\d{2,4}:", m),
                  m.strip()[-200:] or "no output"))
    return res


def vm1(out):
    f = out / "autoload/greet.vim"
    t = f.read_text()
    res = header_checks(t, "greet.vim")
    res.append(ok("Has the v:version < 902 and &cp load guard", re.search(r"v:version\s*<\s*902", t) and "&cp" in t, "checked"))
    legacy = re.findall(r"(?m)^\s*(function!?|let |endfunction)|\b[al]:\w", t)
    res.append(ok("No legacy syntax (function, let, a:, l:)", not legacy, str(legacy[:5]) or "none"))
    res.append(ok("Uses export def", re.search(r"(?m)^export def \w+", t), "checked"))
    res.append(ok("Uses $'' interpolation instead of concatenation",
                  "$'" in t and not re.search(r"\s\.\.?\s", t), "checked"))
    res.append(ok("Function block starts with FUNCTION:", re.search(r"(?m)^# FUNCTION:", t), "checked"))
    res.append(ok("Names the length limit 20 as a constant", re.search(r"(?m)^const \w+(: number)? = 20", t), "checked"))
    m = vim_run(out, ["echo greet#Say('Bob')", "echo greet#Say(repeat('x', 25))"])
    good = "Hello, Bob!" in m and "Hello, friend!" in m and not re.search(r"E\d{2,4}:", m)
    res.append(ok("greet#Say still works from legacy callers", good, m.strip()[-200:] or "no output"))
    return res


##############################################################################
# SECTION: Transcript checks for token-efficient-execution.
##############################################################################
def tool_calls(run):
    tp = run / "transcript_path.txt"
    if not tp.exists():
        return None
    calls, seen = [], set()
    for line in open(tp.read_text().strip()):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = d.get("message")
        if isinstance(m, dict) and isinstance(m.get("content"), list):
            for b in m["content"]:
                if b.get("type") == "tool_use" and b["name"] != "SubagentHandback" and b["id"] not in seen:
                    seen.add(b["id"])
                    calls.append((b["name"], b.get("input", {})))
    return calls


def tx_checks(run, max_calls, dump_file=None, avoid_file=None):
    calls = tool_calls(run)
    if calls is None:
        return [ok("Transcript available", False, "no transcript_path.txt")]
    res = []
    work = [c for c in calls if not (c[0] == "Read" and c[1].get("file_path", "").endswith("SKILL.md"))]
    res.append(ok(f"Uses {max_calls} or fewer tool calls, not counting the SKILL.md read",
                  len(work) <= max_calls, f"{len(work)} calls: {[c[0] for c in work]}"))
    reads = [c[1].get("file_path") for c in calls if c[0] == "Read"]
    dup = sorted({r for r in reads if reads.count(r) > 1})
    res.append(ok("Never reads the same file twice", not dup, f"reread: {dup}" if dup else "no rereads"))
    if dump_file:
        dumps = []
        for name, inp in calls:
            if name == "Read" and inp.get("file_path", "").endswith(dump_file) and not inp.get("limit"):
                dumps.append(f"Read {dump_file} in full")
            cmd = inp.get("command", "") if name == "Bash" else ""
            if "response.md" in cmd:
                continue
            for part in re.split(r"&&|;|\n", cmd):
                if dump_file in part and not re.search(r"\b(grep|rg|head|tail|sed -n|awk|wc)\b", part):
                    dumps.append(part.strip()[-120:])
        res.append(ok(f"Never dumps all of {dump_file} into context", not dumps, "; ".join(dumps) or "filtered every time"))
    if avoid_file:
        hit = [c for c in calls if avoid_file in json.dumps(c[1]) and c[0] in ("Read", "Bash")
               and not re.search(r"\b(grep|rg|find|ls)\b", c[1].get("command", ""))]
        res.append(ok(f"Never opens the generated {avoid_file}", not hit, f"{len(hit)} touches"))
    return res


def te0_tx(out):
    return te0(out) + tx_checks(out.parent, 6, avoid_file="build/bundle.py")


def te2(out):
    res = []
    r = subprocess.run([sys.executable, "app/check.py"], cwd=out, capture_output=True, text=True)
    res.append(ok("app/check.py passes", r.returncode == 0, (r.stdout + r.stderr).strip()))
    import tomllib
    try:
        t = tomllib.loads((out / "config/settings.toml").read_text()).get("timeout")
    except Exception as e:
        t = str(e)
    res.append(ok("Sets timeout to the documented default of 30", t == 30, f"timeout = {t!r}"))
    ch = changed_files(out, "te2")
    res.append(ok("Only config/settings.toml changed", ch == {"config/settings.toml"}, f"changed: {sorted(ch)}"))
    w = words(resp(out))
    res.append(ok("Final reply is 80 words or fewer", 0 < w <= 80, f"{w} words"))
    res.append(ok("Reply leaves out the unrelated color warning",
                  "color" not in resp(out).lower(), "checked"))
    return res + tx_checks(out.parent, 5, dump_file="build.log")


##############################################################################
# SECTION: code-comments JavaScript graders.
##############################################################################
def js_code(src):
    lines, in_block = [], False
    for l in src.splitlines():
        st = l.strip()
        if in_block:
            in_block = "*/" not in st
            continue
        if st.startswith("/*"):
            in_block = "*/" not in st
            continue
        if st.startswith("//") or not st:
            continue
        lines.append(re.sub(r"\s+//\s.*$", "", l).rstrip())
    return lines


def cc2(out):
    src = (out / "api.js").read_text()
    orig = (FIX / "cc2/api.js").read_text()
    res = []
    r = subprocess.run(["node", "--check", str(out / "api.js")], capture_output=True, text=True)
    same = js_code(src) == js_code(orig)
    res.append(ok("Code unchanged and still parses", same and r.returncode == 0,
                  f"node --check rc={r.returncode}; code lines equal={same}"))
    lines = src.splitlines()
    cl = [l for l in lines if re.match(r"\s*(//|/\*|\*)", l)]
    inline = [l for l in lines if not re.match(r"\s*(//|/\*|\*)", l) and re.search(r"\S\s+//\s", l)]
    res.append(ok("No inline comments", not inline, "; ".join(inline) or "none"))
    long_ = [l for l in cl if len(l) > 78]
    res.append(ok("Every comment line is 78 columns or fewer", not long_, "; ".join(long_) or "ok"))
    mixed = [l for l in cl if re.search(r"(//|/\*)\s*[-=*~]{2,}", l)]
    res.append(ok("Delimiter lines use only the comment marker", not mixed, "; ".join(mixed) or "none"))
    todo = [l for l in cl if re.search(r"(?i)\btodo\b", l)]
    res.append(ok("TODO is written as TODO: in capitals", todo and all("TODO:" in l for l in todo), "; ".join(todo) or "TODO dropped"))
    res.append(ok("Issue 12 link is on its own REFERENCE: line",
                  any(re.fullmatch(r"\s*// REFERENCE: https://github\.com/acme/web/issues/12", l) for l in lines), "checked"))
    blocks = []
    for i, l in enumerate(lines):
        if re.match(r"\s*(async function|function|class|async \w+\(|constructor\(|\w+\()", l) and i and \
                lines[i - 1].strip().startswith("//"):
            j = i - 1
            while j > 0 and lines[j - 1].strip().startswith("//"):
                j -= 1
            blocks.append(lines[j].strip())
    bad = [b for b in blocks if not re.match(r"// (FUNCTION|CLASS|METHOD|TODO|REVIEW|SECTION):", b)]
    res.append(ok("Blocks above a function, class, or method start with an identifier", not bad,
                  "; ".join(bad) or f"{len(blocks)} blocks ok"))
    punct = [l for l in cl if re.search(r"[\"()\[\]—–]|--", re.sub(r"https?://\S+", "", l.split("//", 1)[-1]))]
    res.append(ok("Comment text avoids quotes, brackets, and dashes", not punct, "; ".join(punct) or "none"))
    return res


##############################################################################
# SECTION: github-markdown-style changelog graders.
##############################################################################
def md2(out):
    md = (out / "CHANGELOG.md").read_text()
    res = []
    i21, i20 = md.find("2.1.0"), md.find("2.0.0")
    res.append(ok("2.1.0 entry sits above 2.0.0", -1 < i21 < i20, f"positions {i21}, {i20}"))
    old = (FIX / "md2/CHANGELOG.md").read_text().split("## [2.0.0]")[1]
    res.append(ok("2.0.0 entry left unchanged", old in md, "checked"))
    entry = md[i21:i20] if -1 < i21 < i20 else ""
    res.append(ok("Heading matches the existing format", re.search(r"(?m)^## \[2\.1\.0\] - 2026-10-20$", md), "checked"))
    facts = ["--toc", "88", "3.10", "3.9", "--legacy-pdf", "3.0", "emoji", "footnote", "page number"]
    miss = [f for f in facts if f.lower() not in entry.lower()]
    res.append(ok("Keeps every change from the notes", not miss, f"missing: {miss}" if miss else "all present"))
    res.append(ok("Uses Keep a Changelog groups: Added, Fixed, Removed, Deprecated",
                  all(f"### {g}" in entry for g in ("Added", "Fixed", "Removed", "Deprecated")), "checked"))
    bullets = re.findall(r"(?m)^- (\S+)", entry)
    imp = [b for b in bullets if not re.match(r"(Add|Fix|Remove|Deprecate|Drop|Make|Speed|Render|Replace|Require|Improve|Change)\b", b)]
    res.append(ok("Bullets start with an imperative verb, like the 2.0.0 entry", bullets and not imp, f"non-imperative: {imp}"))
    p = re.findall(r"[—–;]", entry)
    res.append(ok("No dashes or semicolons in the new entry", not p, f"found {p}" if p else "none"))
    res.append(ok("Drops the unsupported 'blazing fast' wording", "blazing" not in entry.lower(), "checked"))
    one = [b for b in re.findall(r"(?m)^- .*$", entry) if re.search(r"(?i)\balso\b", b)]
    res.append(ok("One change per bullet (page numbers and footnotes split)", not one, "; ".join(one) or "ok"))
    return res


CHECKS = {
    ("code-comments", 0): (cc0, "cc0"), ("code-comments", 1): (cc1, "cc1"),
    ("github-markdown-style", 0): (md0, "md0"), ("github-markdown-style", 1): (md1, "md1"),
    ("token-efficient-execution", 0): (te0_tx, "te0"), ("token-efficient-execution", 2): (te2, "te2"),
    ("code-comments", 2): (cc2, "cc2"), ("github-markdown-style", 2): (md2, "md2"), ("token-efficient-execution", 1): (te1, "te1"),
    ("vim9script-plugin", 0): (vm0, "vm0"), ("vim9script-plugin", 1): (vm1, "vm1"),
}


def main():
    it = sys.argv[1] if len(sys.argv) > 1 else "iteration-1"
    for meta in sorted(WS.glob(f"*/{it}/eval-*/eval_metadata.json")):
        skill = meta.parts[-4]
        md = json.loads(meta.read_text())
        if (skill, md["eval_id"]) not in CHECKS:
            continue
        fn, _ = CHECKS[(skill, md["eval_id"])]
        texts = None
        for run in sorted(meta.parent.glob("*/run-*")):
            out = run / "outputs"
            try:
                exps = fn(out)
            except Exception as e:
                exps = [ok("Grader ran", False, f"{type(e).__name__}: {e}")]
            texts = texts or [e["text"] for e in exps]
            for e in exps:
                e["passed"] = bool(e["passed"])
            n = sum(e["passed"] for e in exps)
            grading = {"expectations": exps,
                       "summary": {"passed": n, "failed": len(exps) - n, "total": len(exps),
                                   "pass_rate": round(n / len(exps), 2)}}
            (run / "grading.json").write_text(json.dumps(grading, indent=2))
            print(f"{skill:27} {md['eval_name']:32} {run.parent.name:14} {n}/{len(exps)}")
        md["assertions"] = texts or []
        meta.write_text(json.dumps(md, indent=2))


if __name__ == "__main__":
    main()
