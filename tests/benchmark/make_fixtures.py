"""Generate the large or empty fixture files that are not committed."""
import pathlib
import random
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FIX = HERE / "fixtures"

# The 6,000-line build log hides the one real error near line 5,120, with an
# unrelated warning near the top as a distraction.
LOG_LINES = 6000
ERROR_LINE = 5120
WARNING_LINE = 40


def bundle():
    lines = ["# generated bundle, do not edit"]
    lines += [f"var_{i} = {i}" for i in range(4000)]
    path = FIX / "te0" / "build" / "bundle.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def build_log():
    rng = random.Random(7)
    lines = []
    for i in range(LOG_LINES):
        if i == WARNING_LINE:
            lines.append("WARNING: deprecated option 'color' in ~/.nightlyrc, ignoring")
        elif i == ERROR_LINE:
            lines.append("ERROR: config/settings.toml: missing required key 'timeout'")
        elif i == ERROR_LINE + 1:
            lines.append("FAILED: step 'check-config' exited with status 1 (run: python3 app/check.py)")
        else:
            lines.append(f"[{i:05d}] step compile-assets: wrote dist/asset_{rng.randint(0, 99999):05d}.bin "
                         f"({rng.randint(1, 999)} KB)")
    (FIX / "te2" / "build.log").write_text("\n".join(lines) + "\n")


def main():
    bundle()
    build_log()
    (FIX / "vm0").mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(HERE / "make_ledger.py"), str(FIX / "ledger")], check=True)
    subprocess.run([sys.executable, str(HERE / "waypoint" / "make_waypoint.py"), str(FIX)], check=True)
    print(f"fixtures ready in {FIX}")


if __name__ == "__main__":
    main()
