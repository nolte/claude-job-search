#!/usr/bin/env python3
"""Markdown summary of the JSON results of `claude plugin eval` (evals/results/last-run*.json) for the job summary of
.github/workflows/evals.yml. Names every case, its score and every failed grader with the explanation of the tool.
Usage: summarize.py <result.json>...   Standard library only; reads files, calls no model."""

import json
import sys


def summarize(path):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    total = data["aggregates"]
    lines = [f"### {path}", "",
             f"{total['casesPassed']} of {total['casesTotal']} cases passed, score {total['overallScore']:.2f}, "
             f"cost {data['costUsd']:.2f} US dollars" + (", **partial: the cost ceiling or an abort ended the run**" if data.get("partial") else ""),
             "", "| Case | Score | Runs passed | Failed graders |", "|---|---|---|---|"]
    for case in data["cases"]:
        runs = case["arms"]["with"]
        failed = sorted({g["name"] + (": " + g["explanation"] if g.get("explanation") else "")
                         for run in runs for g in run["graders"] if g.get("scored", True) and not g["passed"]}
                        | {"run error: " + run["error"] for run in runs if run.get("error")})
        lines.append(f"| `{case['name']}` | {case['aggregates']['score']:.2f} | {sum(1 for r in runs if r['passed'])}/{len(runs)} | "
                     + ("<br>".join(f.replace("|", "\\|").replace("\n", " ") for f in failed) or "-") + " |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: summarize.py <result.json>...")
    for result in sys.argv[1:]:
        print(summarize(result))
