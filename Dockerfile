# LaTeX PDF export for the Bewerbung skills (job-application-export, --format pdf and tex).
# Build-time hardening per spec/project/dockerfile-best-practices/: base pinned by tag and digest,
# numeric non-root USER, no secrets, OCI core labels on the final stage.
FROM debian:bookworm-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8

ARG VERSION=0.1.0
ARG REVISION=unknown
ARG CREATED=unknown

LABEL org.opencontainers.image.title="claude-job-search LaTeX export" \
      org.opencontainers.image.description="Exports Bewerbungsunterlagen from Markdown to LaTeX, PDF, DOCX, HTML and Markdown" \
      org.opencontainers.image.source="https://github.com/nolte/claude-job-search" \
      org.opencontainers.image.version="$VERSION" \
      org.opencontainers.image.revision="$REVISION" \
      org.opencontainers.image.created="$CREATED" \
      org.opencontainers.image.base.name="docker.io/library/debian:bookworm-slim" \
      org.opencontainers.image.base.digest="sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8

# pandoc and LuaLaTeX for PDF and tex; poppler-utils for the page and text checks; python-docx for DOCX.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      pandoc \
      texlive-latex-base \
      texlive-latex-recommended \
      texlive-luatex \
      texlive-lang-german \
      texlive-fonts-recommended \
      poppler-utils \
      python3 \
      python3-docx \
 && rm -rf /var/lib/apt/lists/*

# Dedicated non-root user with a fixed numeric UID, so runAsNonRoot admission checks pass.
RUN groupadd --gid 10001 export \
 && useradd --uid 10001 --gid 10001 --home-dir /home/export --create-home --shell /usr/sbin/nologin export

# The skill is read-only code; the working files live in /work, mounted by the caller.
COPY skills/job-application-export /app/skills/job-application-export

# The caller may run the image with any UID (for example the host user, so that the exports belong to
# them). HOME and the TeX cache therefore point to /tmp, which every UID can write. A cache under a
# fixed user's home makes LuaLaTeX produce an empty PDF for a foreign UID.
ENV HOME=/tmp \
    TEXMFVAR=/tmp/texmf-var \
    TEXMFCACHE=/tmp/texmf-var
WORKDIR /work

USER 10001:10001

ENTRYPOINT ["python3", "/app/skills/job-application-export/scripts/export_document.py"]
