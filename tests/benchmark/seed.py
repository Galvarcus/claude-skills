"""Seed run workspaces for one iteration from evals.json.

Usage: python3 seed.py <iteration> [--skill NAME] [--ids 11,15] [--runs N] [--all]

Each run gets a fresh copy of its fixture in
ws/<skill>/<iteration>/eval-<id>-<name>/<config>/run-<n>/outputs, which is
the layout that the skill-creator aggregate and viewer scripts expect, and
a prompt.txt with the exact subagent prompt for that run.
"""
import argparse
import json
import pathlib
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
SKILLS = HERE.parents[1] / "skills"

TEMPLATE = """You are running one benchmark task. Treat this directory as the project root and change no files outside it:
{out}

{skills}

Put any scratch copies or probe files under {scratch}, never in a shared temporary folder, because other runs work at the same time.

Task from the user: "{prompt}"

When you finish, write your final reply to the user to response.md in that directory (exactly what you would tell the user), then return the same reply."""


def skill_text(skill, config, names):
    """Return the prompt paragraph that says which skills a run may read."""
    if names is None:
        names = [skill] if config == "with_skill" else []
    off = "" if skill in names else f" Never load or read {skill}."
    if not names:
        return ("This is the baseline run with no skill. Do not use the Skill tool, and do not read "
                "any SKILL.md file or anything under ~/.claude/skills or the skills folder.")
    paths = ", ".join(str(SKILLS / n / "SKILL.md") for n in names)
    return (f"Before you start, read these skills, plus any reference files they tell you to read, "
            f"and follow them: {paths}. Do not use the Skill tool, and read no other SKILL.md file.{off}")


def snapshot(out):
    """Make out its own git repository with the fixture as the first commit.
    Git commands that a run makes then stay inside the run, instead of
    reaching the benchmark repository that holds ws/."""
    git = ["git", "-C", str(out), "-c", "user.name=benchmark", "-c", "user.email=benchmark@example.com"]
    subprocess.run(git + ["init", "-q"], check=True)
    subprocess.run(git + ["add", "-A"], check=True)
    subprocess.run(git + ["commit", "-qm", "Initial snapshot"], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iteration")
    ap.add_argument("--skill")
    ap.add_argument("--ids", help="comma-separated eval IDs to seed")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--all", action="store_true", help="include retired evals")
    args = ap.parse_args()
    evals = json.loads((HERE / "evals.json").read_text())["evals"]
    for e in evals:
        if args.skill and e["skill"] != args.skill:
            continue
        if args.ids and str(e["id"]) not in args.ids.split(","):
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
        configs = e.get("configs", {"with_skill": None, "without_skill": None})
        for cfg, names in configs.items():
            for n in range(1, args.runs + 1):
                run = d / cfg / f"run-{n}"
                out = run / "outputs"
                if out.exists():
                    shutil.rmtree(out)
                shutil.copytree(fixture, out)
                if e.get("git"):
                    snapshot(out)
                text = skill_text(e["skill"], cfg, names)
                (run / "prompt.txt").write_text(TEMPLATE.format(out=out, skills=text, prompt=e["prompt"],
                                                                scratch=run / "scratch"))
        print(d.relative_to(HERE))


if __name__ == "__main__":
    main()
