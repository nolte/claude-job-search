#!/usr/bin/env bash
# Run the model-in-the-loop evals of this plugin with your own credentials. Costs money: see docs/en/evals.md.
#
#   evals/run.sh trigger            one natural request per skill and the reviewer (14 runs)
#   evals/run.sh behavior           the behavioural cases (scaffolds a fictional Wurzel, grants Bash, Write, Edit)
#   evals/run.sh all                both
#   evals/run.sh <case-glob>        one case or a glob, for example behavior-plan-gate
#
# Environment (all optional):
#   MODEL=claude-sonnet-5-5         model of the agent under test (haiku does not trigger the skills, see the docs)
#   JUDGE=claude-opus-5-5           model of the llm graders (the suite uses regex graders only)
#   MAX_COST_USD=10                 hard ceiling for the whole run (exit 2 with partial results)
#   THRESHOLD=0.8                   a case below this score fails the run (exit 1)
#   RUNS=                           override the runs per case (default: the value in each case)
#   ABLATION=none                   none | with-without (with-without also runs every case without the plugin: double cost)
#   TRUST=1                         pass --trust-plugin (otherwise Claude Code asks once whether you trust this plugin)
#   SKIP_PRECHECK=1                 do not run behavior-bash-works first
#   ANTHROPIC_API_KEY               your key; without it the login of `claude` is used
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

MODEL="${MODEL:-claude-sonnet-5-5}"
JUDGE="${JUDGE:-claude-opus-5-5}"
MAX_COST_USD="${MAX_COST_USD:-10}"
THRESHOLD="${THRESHOLD:-0.8}"
ABLATION="${ABLATION:-none}"
TARGET="${1:-}"
shift || true

if [ -z "$TARGET" ]; then
  sed -n '2,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 64
fi
command -v claude >/dev/null || { echo "claude is not on the PATH" >&2; exit 127; }
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "Note: ANTHROPIC_API_KEY is not set; the login of claude is used (and billed)." >&2
fi
mkdir -p evals/results

# Cases that build a workspace need --scaffold and the tool grants; the trigger cases need neither.
needs_scaffold=1
case "$TARGET" in trigger|trigger-*) needs_scaffold=0 ;; esac

common=(plugin eval . --model "$MODEL" --judge-model "$JUDGE" --max-cost-usd "$MAX_COST_USD" --threshold "$THRESHOLD"
        --ablation "$ABLATION" --no-publish)
[ "${TRUST:-0}" = "1" ] && common+=(--trust-plugin)
grants=()
if [ "$needs_scaffold" = "1" ]; then
  grants=(--scaffold --allow-tools "Bash(python3 *)" --allow-tools Write --allow-tools Edit)
  echo "Note: --scaffold runs the fixture.sh of each case as you. They are in this repository (evals/*/fixture.sh)." >&2
fi

# Precondition: if Bash does not work inside the eval sandbox, the cases that run scripts measure the machine.
case "$TARGET" in
  behavior|all|behavior-*)
    if [ "${SKIP_PRECHECK:-0}" != "1" ] && [ "$TARGET" != "behavior-bash-works" ]; then
      echo "Precondition: behavior-bash-works" >&2
      if ! claude "${common[@]}" "${grants[@]}" --runs 1 --case behavior-bash-works --json evals/results/precheck.json; then
        echo "Bash does not work inside the eval sandbox (see docs/en/evals.md). Fix that or set SKIP_PRECHECK=1." >&2
        exit 3
      fi
    fi ;;
esac

args=("${common[@]}" "${grants[@]}" --json "evals/results/last-run.json")
[ -n "${RUNS:-}" ] && args+=(--runs "$RUNS")
case "$TARGET" in
  trigger)  args+=(--tag trigger) ;;
  behavior) args+=(--tag behavior) ;;
  all)      ;;
  *)        args+=(--case "$TARGET") ;;
esac
exec claude "${args[@]}" "$@"
