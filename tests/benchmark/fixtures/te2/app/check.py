import pathlib
import sys
import tomllib

REQUIRED = ["name", "retries", "timeout"]
path = pathlib.Path(__file__).resolve().parents[1] / "config" / "settings.toml"
data = tomllib.loads(path.read_text())
missing = [k for k in REQUIRED if k not in data]
if missing:
    sys.exit(f"ERROR: config/settings.toml: missing required key {missing[0]!r}")
if not isinstance(data["timeout"], int):
    sys.exit("ERROR: config/settings.toml: timeout must be an integer")
print("config ok")
