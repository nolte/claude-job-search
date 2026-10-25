#!/usr/bin/env bash
# Run evals/run.sh inside a container in which the Bash tool of `claude plugin eval` can create its sandbox.
# For the cases that need Bash (behavior-gate-runs-script) on a machine where the sandbox fails (docs/en/evals.md).
#
#   evals/docker/run.sh behavior-gate-runs-script        the same arguments and variables as evals/run.sh
#   RUNS=3 MAX_COST_USD=3 TRUST=1 evals/docker/run.sh behavior-bash-works
#
# Credentials come from your environment (ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL,
# CLAUDE_CODE_OAUTH_TOKEN) and are passed by name only; none is written into the image. The repository is mounted read-only;
# only evals/results/ is writable. TRUST defaults to 1 here because the container has no terminal for the trust question;
# running this script is the decision to trust this plugin. CLAUDE_CODE_VERSION overrides the pinned version at build time.
# The container drops all capabilities and runs as your user. It does need three security options to be relaxed, because
# the default profile of Docker blocks the user namespaces that bubblewrap creates: seccomp, apparmor and the masked
# paths of /proc. That lowers the isolation of the container from the host; run it only for plugins you trust and
# only on a machine where that is acceptable (see the docs).
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."

command -v docker >/dev/null || { echo "docker is not installed" >&2; exit 1; }
image="${EVAL_IMAGE:-claude-job-search-eval}"
build=(--tag "$image" --file evals/docker/Dockerfile)
[ -n "${CLAUDE_CODE_VERSION:-}" ] && build+=(--build-arg "CLAUDE_CODE_VERSION=$CLAUDE_CODE_VERSION")
if ! log=$(docker build "${build[@]}" evals/docker 2>&1); then echo "$log" >&2; echo "docker build failed" >&2; exit 1; fi
mkdir -p evals/results
export TRUST="${TRUST:-1}"

pass=()
for name in ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL CLAUDE_CODE_OAUTH_TOKEN MODEL JUDGE MAX_COST_USD THRESHOLD RUNS ABLATION TRUST SKIP_PRECHECK; do
  [ -n "${!name:-}" ] && pass+=(--env "$name")
done

exec docker run --rm --interactive --user "$(id -u):$(id -g)" \
  --cap-drop ALL --security-opt no-new-privileges \
  --security-opt seccomp=unconfined --security-opt apparmor=unconfined --security-opt systempaths=unconfined \
  --env HOME=/tmp/eval-home --tmpfs /tmp:exec --tmpfs /tmp/eval-home:exec,mode=1777 \
  ${pass[@]+"${pass[@]}"} \
  --volume "$PWD:/work:ro" --volume "$PWD/evals/results:/work/evals/results" \
  "$image" "$@"
