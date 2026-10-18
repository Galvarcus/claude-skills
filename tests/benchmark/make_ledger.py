"""Generate the ledger fixture repo for the token-efficient-execution evals."""
import pathlib
import random
import shutil
import sys

root = pathlib.Path(sys.argv[1])
if root.exists():
    shutil.rmtree(root)
random.seed(42)

F = {}

F["README.md"] = """# ledger

Import bank exports, categorize transactions, and export reports as CSV or JSON.

```sh
python3 -m ledger.cli import statements/2026-09.csv
python3 -m ledger.cli export --format csv -o out.csv
```

Run the tests with `python3 -m unittest discover -s tests -t .`.
The integration suite in `tests/test_integration_slow.py` takes about 20 seconds.
"""

F["CHANGELOG.md"] = """# Changelog

## 1.4.0

- Drop rows with unprintable payees from exports, so control characters from
  some bank exports no longer corrupt the CSV.

## 1.3.0

- Add JSON export.
"""

F["ISSUE-214.md"] = """# CSV export drops rows with accented payees (#214)

Since 1.4.0, `ledger export --format csv` silently leaves out any transaction
whose payee has a non-ASCII character. For example `Café Rio` and `Zürich
Versicherung` are missing from the export, while `Cafe Rio` is fine.

Expected: every transaction is exported. Rows with real control characters,
like the BEL character some bank exports contain, should still be dropped,
as 1.4.0 intended.
"""

F["config/ledger.toml"] = """# Sample configuration.
currency = "USD"
date_fmt = "%Y-%m-%d"
categories_file = "config/categories.toml"
"""

F["config/categories.toml"] = "\n".join(
    f'"{k}" = "{v}"' for k, v in [("Café Rio", "dining"), ("Shell", "fuel"), ("Rent Co", "housing"),
                                 ("Zürich Versicherung", "insurance"), ("Grocer", "groceries")]) + "\n"

F["docs/configuration.md"] = """# Configuration

ledger reads `config/ledger.toml`.

| Key | Meaning | Default |
| --- | --- | --- |
| `currency` | ISO currency code for amounts | `USD` |
| `date_fmt` | strftime format for dates in exports | `%Y-%m-%d` |
| `categories_file` | path of the payee to category map | none |

Example:

```toml
date_fmt = "%d.%m.%Y"
```
"""

F["docs/exports.md"] = """# Exports

`ledger export --format csv` writes one row per transaction with the columns
date, payee, amount, and category. Dates use the `date_fmt` setting.

`ledger export --format json` writes a list of objects with the same fields.
"""

F["src/ledger/__init__.py"] = '__version__ = "1.4.0"\n'

F["src/ledger/models.py"] = '''from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Transaction:
    day: date
    payee: str
    amount_cents: int
    category: str = "uncategorized"

    @property
    def amount(self):
        return self.amount_cents / 100
'''

F["src/ledger/config.py"] = '''import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATE_FMT = "%Y-%m-%d"


@dataclass
class Config:
    currency: str = "USD"
    date_fmt: str = DEFAULT_DATE_FMT
    categories_file: str | None = None


def load(path):
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return from_dict(data)


def from_dict(data):
    return Config(
        currency=data.get("currency", "USD"),
        date_fmt=data.get("date_fmt", DEFAULT_DATE_FMT),
        categories_file=data.get("categories_file"),
    )
'''

F["src/ledger/util/__init__.py"] = ""

F["src/ledger/util/strings.py"] = '''import string

_PRINTABLE = set(string.printable)


def clean_payee(text):
    return " ".join(text.split())


def is_printable(text):
    return all(c in _PRINTABLE for c in text)
'''

F["src/ledger/util/dates.py"] = '''from datetime import datetime


def parse_day(text, fmt):
    return datetime.strptime(text.strip(), fmt).date()


def format_day(day, fmt):
    return day.strftime(fmt)
'''

F["src/ledger/util/money.py"] = '''def to_cents(text):
    text = text.strip().replace(",", "")
    negative = text.startswith("-")
    whole, _, frac = text.lstrip("-").partition(".")
    cents = int(whole or 0) * 100 + int((frac + "00")[:2])
    return -cents if negative else cents
'''

F["src/ledger/parse.py"] = '''import csv
import io

from .models import Transaction
from .util.dates import parse_day
from .util.money import to_cents
from .util.strings import clean_payee


def parse_statement(text, date_fmt):
    rows = csv.DictReader(io.StringIO(text))
    return [Transaction(parse_day(r["Date"], date_fmt), clean_payee(r["Payee"]), to_cents(r["Amount"]))
            for r in rows]
'''

F["src/ledger/categorize.py"] = '''from dataclasses import replace


def categorize(transactions, mapping):
    return [replace(t, category=mapping.get(t.payee, t.category)) for t in transactions]
'''

F["src/ledger/report.py"] = '''from collections import defaultdict


def totals_by_category(transactions):
    totals = defaultdict(int)
    for t in transactions:
        totals[t.category] += t.amount_cents
    return dict(sorted(totals.items()))
'''

F["src/ledger/export/__init__.py"] = '''from .csv_export import to_csv
from .json_export import to_json

FORMATS = {"csv": to_csv, "json": to_json}
'''

F["src/ledger/export/csv_export.py"] = '''import csv
import io

from ..util.dates import format_day
from ..util.strings import is_printable

COLUMNS = ["date", "payee", "amount", "category"]


def to_csv(transactions, config):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\\n")
    w.writerow(COLUMNS)
    for t in transactions:
        if not is_printable(t.payee):
            continue
        w.writerow([format_day(t.day, config.date_fmt), t.payee, f"{t.amount:.2f}", t.category])
    return buf.getvalue()
'''

F["src/ledger/export/json_export.py"] = '''import json

from ..util.dates import format_day


def to_json(transactions, config):
    return json.dumps([
        {"date": format_day(t.day, config.date_fmt), "payee": t.payee,
         "amount": round(t.amount, 2), "category": t.category}
        for t in transactions
    ], ensure_ascii=False, indent=2)
'''

F["src/ledger/cli.py"] = '''import argparse
import sys
from pathlib import Path

from . import config as cfg
from .categorize import categorize
from .export import FORMATS
from .parse import parse_statement


def main(argv=None):
    p = argparse.ArgumentParser(prog="ledger")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("statement")
    e.add_argument("--format", choices=sorted(FORMATS), default="csv")
    e.add_argument("--config", default="config/ledger.toml")
    e.add_argument("-o", "--output")
    args = p.parse_args(argv)
    conf = cfg.load(args.config)
    txs = parse_statement(Path(args.statement).read_text(encoding="utf-8"), conf.date_fmt)
    out = FORMATS[args.format](txs, conf)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
'''

HDR = '''import pathlib
import sys
import unittest
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
'''

F["tests/__init__.py"] = ""

F["tests/test_parse.py"] = HDR + '''from ledger.parse import parse_statement


class ParseTest(unittest.TestCase):
    def test_parse(self):
        txs = parse_statement("Date,Payee,Amount\\n2026-09-01,  Shell  ,-45.10\\n", "%Y-%m-%d")
        self.assertEqual(txs[0].payee, "Shell")
        self.assertEqual(txs[0].amount_cents, -4510)
'''

F["tests/test_config.py"] = HDR + '''from ledger import config


class ConfigTest(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(config.from_dict({}).date_fmt, "%Y-%m-%d")

    def test_date_fmt(self):
        self.assertEqual(config.from_dict({"date_fmt": "%d.%m.%Y"}).date_fmt, "%d.%m.%Y")
'''

F["tests/test_csv_export.py"] = HDR + '''from ledger.config import Config
from ledger.export.csv_export import to_csv
from ledger.models import Transaction


class CsvExportTest(unittest.TestCase):
    def test_rows(self):
        out = to_csv([Transaction(date(2026, 9, 1), "Shell", -4510, "fuel")], Config())
        self.assertEqual(out, "date,payee,amount,category\\n2026-09-01,Shell,-45.10,fuel\\n")

    def test_drops_control_characters(self):
        out = to_csv([Transaction(date(2026, 9, 1), "Bad\\x07Payee", 100)], Config())
        self.assertNotIn("Bad", out)

    def test_date_fmt(self):
        out = to_csv([Transaction(date(2026, 9, 1), "Shell", 100)], Config(date_fmt="%d.%m.%Y"))
        self.assertIn("01.09.2026", out)
'''

F["tests/test_json_export.py"] = HDR + '''import json

from ledger.config import Config
from ledger.export.json_export import to_json
from ledger.models import Transaction


class JsonExportTest(unittest.TestCase):
    def test_rows(self):
        out = json.loads(to_json([Transaction(date(2026, 9, 1), "Café Rio", -1250, "dining")], Config()))
        self.assertEqual(out[0]["payee"], "Café Rio")
'''

F["tests/test_report.py"] = HDR + '''from ledger.models import Transaction
from ledger.report import totals_by_category


class ReportTest(unittest.TestCase):
    def test_totals(self):
        txs = [Transaction(date(2026, 9, 1), "a", 100, "x"), Transaction(date(2026, 9, 2), "b", 50, "x")]
        self.assertEqual(totals_by_category(txs), {"x": 150})
'''

F["tests/test_integration_slow.py"] = HDR + '''import time

from ledger import cli


class IntegrationTest(unittest.TestCase):
    def test_end_to_end(self):
        # Simulates the bank sandbox round trip that the real suite performs.
        time.sleep(20)
        root = pathlib.Path(__file__).resolve().parents[1]
        stmt = root / "tests" / "data" / "statement.csv"
        out = root / "tests" / "data" / "out.json"
        cli.main(["export", str(stmt), "--format", "json", "--config", str(root / "config" / "ledger.toml"),
                  "-o", str(out)])
        self.assertIn("Shell", out.read_text(encoding="utf-8"))
        out.unlink()
'''

F["tests/data/statement.csv"] = "Date,Payee,Amount\n2026-09-01,Shell,-45.10\n2026-09-02,Café Rio,-12.50\n"

# A vendored table formatter: large, unrelated, and it mentions date_fmt.
vend = ['"""Vendored copy of a small table formatter. Do not edit; update from upstream."""', ""]
for i in range(900):
    vend += [f"def _fmt_{i}(value, date_fmt=None, width={i % 40 + 4}):",
             f"    return str(value).ljust(width) if date_fmt is None else value.strftime(date_fmt)", ""]
F["vendor/tabulate.py"] = "\n".join(vend) + "\n"

# A noisy application log with the export runs in it.
log = []
for i in range(20000):
    lvl = random.choice(["INFO"] * 30 + ["DEBUG"] * 10 + ["WARNING"])
    log.append(f"2026-10-{1 + i // 1200:02d}T{(i // 50) % 24:02d}:{i % 60:02d}:00 {lvl} ledger.import "
               f"imported row {i} payee_hash={random.getrandbits(40):010x}")
    if i == 15333:
        log.append("2026-10-13T10:33:00 INFO ledger.export wrote 41 of 44 rows to out.csv")
F["logs/app.log"] = "\n".join(log) + "\n"

for rel, text in F.items():
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

# A stale build copy of the package, as left behind by setup.py build.
shutil.copytree(root / "src" / "ledger", root / "build" / "lib" / "ledger")
