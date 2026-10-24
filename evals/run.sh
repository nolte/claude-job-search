#!/usr/bin/env bash
# Run the model-in-the-loop evals of this plugin with your own credentials. Costs money: read evals/README.md first.
#
#   evals/run.sh trigger            one natural request per skill and the reviewer (about 14 runs)
#   evals/run.sh behavior           the behavioural cases (3 runs each, scaffolds a fictional Wurzel, grants Bash)
#   evals/run.sh all                both
#   evals/run.sh <case-glob>        one case or a glob, for example behavior-plan-gate
#
# Environment (all optional):
#   MODEL=claude-sonnet-5-5         model of the agent under test (haiku does not trigger the skills, see README)
#   JUDGE=claude-opus-5-5           model of the llm graders (the suite uses mostly regex graders)
#   MAX_COST_USD=10                 hard ceiling for the whole run (exit 2 with partial results)
#   THRESHOLD=0.8                   a case below this score fails the run (exit 1)
#   RUNS=                           override the runs per case (default: the value in each case)
#   ABLATION=none                   none | with-without (with-without also runs every case without the plugin: double cost)
#   TRUST=1                         pass --trust-plugin (otherwise Claude Code asks once whether you trust this plugin)
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
  sed -n '2,19p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 64
fi
command -v claude >/dev/null || { echo "claude is not on the PATH" >&2; exit 127; }
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "Note: ANTHROPIC_API_KEY is not set; the login of claude is used (and billed)." >&2
fi
mkdir -p evals/results

args=(plugin eval . --model "$MODEL" --judge-model "$JUDGE" --max-cost-usd "$MAX_COST_USD" --threshold "$THRESHOLD"
      --ablation "$ABLATION" --no-publish --json "evals/results/last-run.json")
[ "${TRUST:-0}" = "1" ] && args+=(--trust-plugin)
[ -n "${RUNS:-}" ] && args+=(--runs "$RUNS")

case "$TARGET" in
  trigger)  args+=(--tag trigger) ;;
  behavior) args+=(--tag behavior --scaffold --allow-tools "Bash(python3 *)" --allow-tools Write --allow-tools Edit) ;;
  all)      args+=(--scaffold --allow-tools "Bash(python3 *)" --allow-tools Write --allow-tools Edit) ;;
  *)        args+=(--case "$TARGET")
            case "$TARGET" in behavior-*|all) args+=(--scaffold --allow-tools "Bash(python3 *)" --allow-tools Write --allow-tools Edit) ;; esac ;;
esac

if [[ " ${args[*]} " == *" --scaffold "* ]]; then
  echo "Note: --scaffold runs the fixture.sh of each case as you. They are in this repository (evals/*/fixture.sh)." >&2
fi
exec claude "${args[@]}" "$@"
