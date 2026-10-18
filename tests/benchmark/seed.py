"""Seed run workspaces for one iteration from evals.json.

Usage: python3 seed.py <iteration> [--skill NAME] [--runs N] [--all]

Each run gets a fresh copy of its fixture in
ws/<skill>/<iteration>/eval-<id>-<name>/<config>/run-<n>/outputs, which is
the layout that the skill-creator aggregate and viewer scripts expect.
"""
import argparse
import json
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
CONFIGS = ("with_skill", "without_skill")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iteration")
    ap.add_argument("--skill")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--all", action="store_true", help="include retired evals")
    args = ap.parse_args()
    evals = json.loads((HERE / "evals.json").read_text())["evals"]
    for e in evals:
        if args.skill and e["skill"] != args.skill:
            continue
        if e["status"] != "active" and not args.all:
            continue
        fixture = HERE / "fixtures" / e["fixture"]
        if not fixture.exists():
            raise SystemExit(f"missing {fixture}; run make_fixtures.py first")
        d = HERE / "ws" / e["skill"] / args.iteration / f"eval-{e['id']}-{e['name']}"
        d.mkdir(parents=True, exist_ok=True)
        meta = {"eval_id": e["id"], "eval_name": e["name"], "prompt": e["prompt"], "assertions": []}
        (d / "eval_metadata.json").write_text(json.dumps(meta, indent=2))
        for cfg in CONFIGS:
            for n in range(1, args.runs + 1):
                out = d / cfg / f"run-{n}" / "outputs"
                if out.exists():
                    shutil.rmtree(out)
                shutil.copytree(fixture, out)
        print(d.relative_to(HERE))


if __name__ == "__main__":
    main()
