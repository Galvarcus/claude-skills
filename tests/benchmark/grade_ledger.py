"""Grade the complex ledger evals: hidden tests, diff scope, and transcript."""
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

BENCH = pathlib.Path(__file__).resolve().parent
FIX = BENCH / "fixtures" / "ledger"
IT = BENCH / "ws" / "token-efficient-execution" / (sys.argv[1] if len(sys.argv) > 1 else "iteration-3")
PROTECTED = ("vendor/", "build/", "logs/")

HIDDEN = {
    3: '''
import pathlib, sys, unittest
from datetime import date
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from ledger.config import Config
from ledger.export.csv_export import to_csv
from ledger.export.json_export import to_json
from ledger.models import Transaction

class Hidden(unittest.TestCase):
    def rows(self, *payees):
        return [Transaction(date(2026, 9, 1), p, 100) for p in payees]
    def test_accented_rows_kept(self):
        out = to_csv(self.rows("Café Rio", "Zürich Versicherung", "Shell"), Config())
        for p in ("Café Rio", "Zürich Versicherung", "Shell"):
            self.assertIn(p, out)
    def test_cjk_and_emoji_kept(self):
        out = to_csv(self.rows("東京ストア", "Pizza 🍕"), Config())
        self.assertIn("東京ストア", out); self.assertIn("Pizza 🍕", out)
    def test_control_chars_dropped(self):
        out = to_csv(self.rows("Bad\\x07Payee", "Nul\\x00Co", "Ok"), Config())
        self.assertNotIn("Bad", out); self.assertNotIn("Nul", out); self.assertIn("Ok", out)
''',
    4: '''
import pathlib, sys, unittest, warnings
from datetime import date
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from ledger import config
from ledger.config import Config
from ledger.export.csv_export import to_csv
from ledger.export.json_export import to_json
from ledger.models import Transaction

class Hidden(unittest.TestCase):
    def test_new_key(self):
        self.assertEqual(config.from_dict({"date_format": "%d.%m.%Y"}).date_format, "%d.%m.%Y")
    def test_default(self):
        self.assertEqual(config.from_dict({}).date_format, "%Y-%m-%d")
    def test_old_key_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            c = config.from_dict({"date_fmt": "%d.%m.%Y"})
        self.assertEqual(c.date_format, "%d.%m.%Y")
        self.assertTrue(any(issubclass(x.category, DeprecationWarning) for x in w))
    def test_new_key_wins_without_warning_noise(self):
        c = config.from_dict({"date_format": "%Y", "date_fmt": "%d"})
        self.assertEqual(c.date_format, "%Y")
    def test_exports_use_new_field(self):
        t = [Transaction(date(2026, 9, 1), "Shell", 100)]
        self.assertIn("01.09.2026", to_csv(t, Config(date_format="%d.%m.%Y")))
        self.assertIn("01.09.2026", to_json(t, Config(date_format="%d.%m.%Y")))
    def test_sample_config_loads(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        c = config.load(root / "config" / "ledger.toml")
        self.assertEqual(c.date_format, "%Y-%m-%d")
''',
}


def ok(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": str(evidence)[:300]}


def changed(out):
    ch = set()
    for p in out.rglob("*"):
        if p.is_dir() or "__pycache__" in p.parts or p.name == "response.md":
            continue
        rel = str(p.relative_to(out))
        q = FIX / rel
        if not q.exists() or q.read_bytes() != p.read_bytes():
            ch.add(rel)
    for q in FIX.rglob("*"):
        if q.is_file() and not (out / q.relative_to(FIX)).exists():
            ch.add(str(q.relative_to(FIX)) + " (deleted)")
    return ch


def run_tests(out, eval_id):
    """Run the repo's fast tests and the hidden tests on a scratch copy."""
    with tempfile.TemporaryDirectory() as tmp:
        dst = pathlib.Path(tmp) / "repo"
        shutil.copytree(out, dst, ignore=shutil.ignore_patterns("__pycache__"))
        (dst / "tests" / "test_integration_slow.py").unlink(missing_ok=True)
        fast = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                              cwd=dst, capture_output=True, text=True, timeout=60)
        (dst / "tests" / "test_hidden.py").write_text(HIDDEN[eval_id], encoding="utf-8")
        hid = subprocess.run([sys.executable, "-m", "unittest", "tests.test_hidden", "-v"],
                             cwd=dst, capture_output=True, text=True, timeout=60)
    return fast, hid


def transcript(run):
    """Tool calls and token use, deduplicated: the JSONL repeats each message."""
    calls, usage = {}, {}
    path = (run / "transcript_path.txt").read_text().strip()
    for line in open(path):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        if d.get("type") == "assistant" and m.get("usage") and m.get("id"):
            usage[m["id"]] = m["usage"]
        if isinstance(m.get("content"), list):
            for b in m["content"]:
                if b.get("type") == "tool_use" and b["name"] != "SubagentHandback":
                    calls.setdefault(b["id"], (b["name"], b.get("input", {})))
    tokens = sum(u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                 + u.get("cache_creation_input_tokens", 0) + u.get("output_tokens", 0) for u in usage.values())
    out_tokens = sum(u.get("output_tokens", 0) for u in usage.values())
    return list(calls.values()), tokens, out_tokens


FILTER = re.compile(r"\b(grep|rg|head|tail|sed -n|awk|wc|ls|find)\b")


def tx_checks(calls, max_calls):
    res = []
    work = [c for c in calls if not (c[0] == "Read" and c[1].get("file_path", "").endswith("SKILL.md"))]
    res.append(ok(f"Uses {max_calls} or fewer tool calls, not counting the SKILL.md read",
                  len(work) <= max_calls, f"{len(work)} calls: {[c[0] for c in work]}"))
    reads = [c[1].get("file_path") for c in calls if c[0] == "Read" and not c[1].get("offset")]
    dup = sorted({r for r in reads if reads.count(r) > 1})
    res.append(ok("Never reads the same file twice", not dup, dup or "no rereads"))
    dumps = []
    for name, inp in calls:
        fp = inp.get("file_path", "")
        if name == "Read" and any(f in fp for f in ("logs/app.log", "vendor/tabulate.py")) and not inp.get("limit"):
            dumps.append(f"Read {fp.split('/outputs/')[-1]}")
        cmd = inp.get("command", "") if name == "Bash" else ""
        if "response.md" in cmd:
            continue
        for part in re.split(r"&&|;|\n|\|\|", cmd):
            if re.search(r"logs/app\.log|vendor/tabulate\.py", part) and not FILTER.search(part):
                dumps.append(part.strip()[-100:])
    res.append(ok("Never dumps the 20k-line log or the vendored library", not dumps, dumps or "none"))
    build = [c for c in calls if "build/lib" in json.dumps(c[1]) and c[0] != "Grep"
             and "response.md" not in c[1].get("command", "") and not FILTER.search(c[1].get("command", ""))]
    res.append(ok("Never opens the stale build/ copy", not build, f"{len(build)} touches"))
    slow = [c for c in calls if c[0] == "Bash" and re.search(r"unittest", c[1].get("command", ""))
            and (re.search(r"discover", c[1]["command"]) or "integration" in c[1]["command"])]
    res.append(ok("Runs the 20-second full suite at most once", len(slow) <= 1, f"{len(slow)} full or slow runs"))
    return res


def grade_fix(out, calls):
    res = []
    fast, hid = run_tests(out, 3)
    res.append(ok("Existing fast tests pass", fast.returncode == 0, fast.stderr.strip().splitlines()[-1]))
    res.append(ok("Hidden tests pass: accented, CJK, and emoji payees kept; control characters dropped",
                  hid.returncode == 0, " ".join(l for l in hid.stderr.splitlines() if "..." in l)))
    ch = changed(out)
    src = {c for c in ch if c.startswith("src/")}
    res.append(ok("Source change limited to strings.py or csv_export.py",
                  src and src <= {"src/ledger/util/strings.py", "src/ledger/export/csv_export.py"}, sorted(src)))
    tests = [c for c in ch if c.startswith("tests/")]
    reg = any(re.search(r"[^\x00-\x7f]|\\u00[c-f]|\\x[c-f][0-9a-f]", (out / t).read_text(encoding="utf-8"))
              for t in tests if (out / t).exists())
    res.append(ok("Adds a regression test with a non-ASCII payee", reg, tests or "no test changed"))
    prot = [c for c in ch if c.startswith(PROTECTED)]
    res.append(ok("Leaves vendor/, build/, and logs/ untouched", not prot, prot or "untouched"))
    extra = [c for c in ch if not c.startswith(("src/", "tests/")) and c != "CHANGELOG.md"]
    res.append(ok("No unrelated file changes", not extra, extra or "none"))
    w = len((out / "response.md").read_text().split()) if (out / "response.md").exists() else 0
    res.append(ok("Final reply is 120 words or fewer", 0 < w <= 120, f"{w} words"))
    return res + tx_checks(calls, 10)


def grade_rename(out, calls):
    res = []
    fast, hid = run_tests(out, 4)
    res.append(ok("Repo's fast tests pass", fast.returncode == 0, fast.stderr.strip().splitlines()[-1]))
    res.append(ok("Hidden tests pass: new key, old key with DeprecationWarning, exports, sample config",
                  hid.returncode == 0, " ".join(l for l in hid.stderr.splitlines() if "..." in l)))
    left = []
    for p in out.rglob("*"):
        rel = str(p.relative_to(out))
        if p.is_dir() or rel.startswith(PROTECTED) or "__pycache__" in rel or rel in ("response.md", "CHANGELOG.md"):
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if "date_fmt" in line and not re.search(r"(?i)deprecat|legacy|old|compat|warn|DATE_FMT", line) \
                    and not rel.startswith(("src/ledger/config.py", "tests/")):
                left.append(f"{rel}:{n}")
    res.append(ok("No stray date_fmt left in code, docs, or sample config", not left, left or "none"))
    docs = (out / "docs" / "configuration.md").read_text(encoding="utf-8")
    res.append(ok("docs/configuration.md documents date_format", "date_format" in docs, "checked"))
    ch = changed(out)
    prot = [c for c in ch if c.startswith(PROTECTED)]
    res.append(ok("Leaves vendor/, build/, and logs/ untouched", not prot, prot or "untouched"))
    w = len((out / "response.md").read_text().split()) if (out / "response.md").exists() else 0
    res.append(ok("Final reply is 120 words or fewer", 0 < w <= 120, f"{w} words"))
    return res + tx_checks(calls, 14)


def main():
    for meta in sorted(IT.glob("eval-*/eval_metadata.json")):
        md = json.loads(meta.read_text())
        fn = {3: grade_fix, 4: grade_rename}.get(md["eval_id"])
        if fn is None:
            continue
        texts = None
        for run in sorted(meta.parent.glob("*/run-*")):
            if not (run / "transcript_path.txt").exists():
                continue
            calls, tokens, out_tokens = transcript(run)
            try:
                exps = fn(run / "outputs", calls)
            except Exception as e:
                exps = [ok("Grader ran", False, f"{type(e).__name__}: {e}")]
            texts = texts or [e["text"] for e in exps]
            n = sum(e["passed"] for e in exps)
            timing = json.loads((run / "timing.json").read_text()) if (run / "timing.json").exists() else {}
            timing["total_tokens"] = tokens
            (run / "timing.json").write_text(json.dumps(timing))
            grading = {"expectations": exps,
                       "summary": {"passed": n, "failed": len(exps) - n, "total": len(exps),
                                   "pass_rate": round(n / len(exps), 2)},
                       "execution_metrics": {"total_tool_calls": len(calls), "output_chars": out_tokens}}
            (run / "grading.json").write_text(json.dumps(grading, indent=2))
            print(f"{md['eval_name']:22} {run.parent.name:14} {run.name}  {n}/{len(exps)}  "
                  f"calls={len(calls):2}  tokens={tokens:7}  out={out_tokens:5}  t={timing.get('total_duration_seconds')}")
        md["assertions"] = texts or []
        meta.write_text(json.dumps(md, indent=2))


if __name__ == "__main__":
    main()
