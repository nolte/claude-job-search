#!/usr/bin/env bash
# Run the model-in-the-loop evals of this plugin with your own credentials. Costs money: see docs/en/evals.md.
#
#   evals/run.sh trigger            one natural request per skill and the reviewer (14 runs)
#   evals/run.sh behavior           the behavioural cases (scaffolds a fictional Wurzel, grants Bash, Write, Edit)
#   evals/run.sh all                both
#   evals/run.sh <case-glob>        one case or a glob, for example behavior-plan-gate
#                                   (a case tagged bash-denied runs in its own invocation without Bash)
#
# Environment (all optional):
#   MODEL=claude-sonnet-5-5         model of the agent under test (haiku does not trigger the skills, see the docs)
#   JUDGE=claude-opus-5-5           model of the llm graders (the suite uses regex graders only)
#   MAX_COST_USD=10                 hard ceiling for the whole run (exit 2 with partial results)
#   THRESHOLD=0.8                   a case below this score fails the run (exit 1)
#   RUNS=                           override the runs per case (default: the value in each case)
#   ABLATION=none                   none | with-without (with-without also runs every case without the plugin: double cost)
#   TRUST=1                         pass --trust-plugin (otherwise Claude Code asks once whether you trust this plugin)
#   SKIP_PRECHECK=1                 do not run the preconditions behavior-bash-works and behavior-python-works first
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

# Cases that build a workspace need --scaffold and the tool grants; the trigger cases need neither.
needs_scaffold=1
case "$TARGET" in trigger|trigger-*) needs_scaffold=0 ;; esac

common=(plugin eval . --model "$MODEL" --judge-model "$JUDGE" --max-cost-usd "$MAX_COST_USD" --threshold "$THRESHOLD"
        --ablation "$ABLATION" --no-publish)
[ "${TRUST:-0}" = "1" ] && common+=(--trust-plugin)
grants=()
if [ "$needs_scaffold" = "1" ]; then
  grants=(--scaffold --allow-tools "Bash(python3 *)" --allow-tools "Bash(uname *)" --allow-tools Write --allow-tools Edit)
  echo "Note: --scaffold runs the fixture.sh of each case as you. They are in this repository (evals/*/fixture.sh)." >&2
fi

# True if the target names a case tagged bash-denied: it runs without Bash and needs no precondition.
is_denied_case() { local d; for d in evals/$1; do [ -f "$d/prompt.md" ] && grep -q '^tags: .*bash-denied' "$d/prompt.md" && return 0; done; return 1; }

# Preconditions: if Bash or python3 does not work inside the eval sandbox, the cases that run commands measure the machine.
# A red precondition no longer stops the run: the cases tagged needs-bash are left out and the rest runs.
bash_ok=1
case "$TARGET" in
  trigger|trigger-*|behavior-bash-works|behavior-python-works) ;;
  *)
    if [ "${SKIP_PRECHECK:-0}" != "1" ] && ! is_denied_case "$TARGET"; then
      for pre in behavior-bash-works behavior-python-works; do
        echo "Precondition: $pre" >&2
        rc=0
        claude "${common[@]}" ${grants[@]+"${grants[@]}"} --runs 1 --case "$pre" --json "evals/results/$pre.json" || rc=$?
        case "$rc" in
          0) ;;
          1) echo "$pre is red: Bash or python3 does not work inside the eval sandbox (see docs/en/evals.md, 'What the spike found')." >&2; bash_ok=0 ;;
          *) echo "The precondition run ended with exit code $rc (2: cost ceiling, 130 or 143: aborted); that is no verdict on the sandbox." >&2; exit "$rc" ;;
        esac
      done
    fi ;;
esac

# Cases that need Bash (tag needs-bash). Left out of the suite targets when a precondition is red.
if [ "$bash_ok" = "0" ] && [ "$TARGET" = "behavior" -o "$TARGET" = "all" ]; then
  skipped=$(grep -l '^tags: .*needs-bash' evals/*/prompt.md 2>/dev/null | xargs -n1 dirname 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')
  echo "Left out because Bash does not work here: ${skipped:-none}. Run them on a machine where the preconditions are green." >&2
fi

main_args=("${common[@]}" ${grants[@]+"${grants[@]}"} --json "evals/results/last-run.json")
# Cases tagged bash-denied need a run in which Bash is removed for every case (--disallow-tools); the grant of Bash
# cannot be taken back for one case. They get their own invocation and do not run in the main one.
denied_args=("${common[@]}" --scaffold --allow-tools Write --allow-tools Edit --disallow-tools Bash --json "evals/results/last-run-bash-denied.json")
if [ -n "${RUNS:-}" ]; then main_args+=(--runs "$RUNS"); denied_args+=(--runs "$RUNS"); fi


run_main=0; run_denied=0
case "$TARGET" in
  trigger)  main_args+=(--tag trigger); run_main=1 ;;
  behavior) if [ "$bash_ok" = "1" ]; then main_args+=(--tag behavior); else main_args+=(--tag no-bash); fi
            run_main=1; run_denied=1; denied_args+=(--tag bash-denied) ;;
  all)      if [ "$bash_ok" = "1" ]; then main_args+=(--tag trigger --tag behavior); else main_args+=(--tag trigger --tag no-bash); fi
            run_main=1; run_denied=1; denied_args+=(--tag bash-denied) ;;
  *)        if is_denied_case "$TARGET"; then run_denied=1; denied_args+=(--case "$TARGET")
            else run_main=1; main_args+=(--case "$TARGET")
                 [ "$bash_ok" = "0" ] && echo "Note: a case tagged needs-bash that you selected by name will fail here." >&2
            fi ;;
esac

main_rc=0; denied_rc=0
[ "$run_main" = "1" ] && { claude "${main_args[@]}" "$@" || main_rc=$?; }
[ "$run_denied" = "1" ] && { echo "Run without Bash: bash-denied cases (results in evals/results/last-run-bash-denied.json)" >&2; claude "${denied_args[@]}" "$@" || denied_rc=$?; }
exit $(( main_rc > denied_rc ? main_rc : denied_rc ))
