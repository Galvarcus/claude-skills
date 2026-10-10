#!/usr/bin/env python3
"""Run repository validation and unit tests."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [sys.executable, str(ROOT / "tools" / "validate.py")],
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
