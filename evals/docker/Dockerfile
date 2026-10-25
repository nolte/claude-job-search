# Runs `claude plugin eval` in a container whose user namespaces work, for the cases that need a working Bash tool
# (behavior-gate-runs-script) on a machine where the sandbox of the eval fails (docs/en/evals.md, "Running in a container").
# The image holds only tools; the repository is mounted at run time and no credential is baked in.
FROM debian:bookworm-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8

ARG CLAUDE_CODE_VERSION=2.1.310

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    HOME=/home/eval \
    DISABLE_AUTOUPDATER=1

# bubblewrap and socat: the OS sandbox of the Bash tool; git and python3: the scaffolds and the fixtures
RUN apt-get update \
 && apt-get install -y --no-install-recommends bubblewrap socat nodejs npm git python3 ca-certificates coreutils \
 && rm -rf /var/lib/apt/lists/* \
 && npm install --global "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
 && npm cache clean --force \
 && useradd --uid 10001 --create-home --home-dir /home/eval --shell /bin/bash eval

WORKDIR /work
USER 10001:10001
ENTRYPOINT ["/work/evals/run.sh"]
