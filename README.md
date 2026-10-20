# claude-job-search

[![ci](https://github.com/nolte/claude-job-search/actions/workflows/ci.yml/badge.svg)](https://github.com/nolte/claude-job-search/actions/workflows/ci.yml)

Claude Code plugin with skills and an agent for German-speaking job applications
(*Bewerbungsunterlagen*) — tabular Lebenslauf, DIN-5008-style Anschreiben, Bewerbungs-E-Mail,
requirement match against the Stellenanzeige, and a quality gate before you send.

## Purpose

Application documents for the DACH region follow specific conventions (reverse-chronological
tabular CV, one-page letter with a concrete subject line, attachment naming), and every
application repeats the same facts. This plugin keeps the facts in one local profile and
derives every document from it, so the output is consistent, tailored to the posting and
never invents experience.

- You describe a **job posting**; `bewerbung-solution` checks your profile, analyses the
  posting, and asks for approval of the plan before any document is written.
- Every fact comes from `bewerbung/profil.md`. Gaps are marked `[ERGÄNZEN: …]` and block
  the quality gate until resolved.
- The rules are codified in `spec/bewerbung/konventionen/en.md`.

## What you get

- **Skills** — `bewerbung-solution` (front door), `bewerbung-profil-erfassen`,
  `bewerbung-stellenanzeige-analysieren`, `bewerbung-lebenslauf-erstellen`,
  `bewerbung-anschreiben-erstellen`, `bewerbung-email-erstellen`, `bewerbung-pruefen`.
- **Agent** — `bewerbungs-reviewer`: read-only, whole-set review from a recruiter's perspective.

## Use cases

- **Complete application for one posting** — `bewerbung-solution`.
- **Check whether your profile fits a posting** — `bewerbung-stellenanzeige-analysieren`.
- **Cover letter for a posting, an unsolicited application, or a career change** — `bewerbung-anschreiben-erstellen`.
- **Review before sending** — `bewerbung-pruefen`, plus the `bewerbungs-reviewer` agent for a second read.

## Usage

Install the plugin via its marketplace, then invoke a skill with
`/claude-job-search:<skill>`, for example `/claude-job-search:bewerbung-solution`.

Application data lives in the git-ignored `bewerbung/` folder of the working copy.

### Work on the plugin itself (dogfooding)

```bash
claude --plugin-dir .
```

Use `/reload-plugins` inside the session to pick up changes. Local automation runs through
`Taskfile.yml`:

```bash
task lint     # pre-commit checks
task test     # placeholder until runtime tests exist
task docs     # build the MkDocs site
```

## Documentation

Published at <https://nolte.github.io/claude-job-search>, English and German.

## Structure

```text
.claude-plugin/       # plugin.json + marketplace.json manifests
skills/<name>/        # one skill per folder (SKILL.md)
agents/<name>.md      # reusable sub-agents
spec/                 # specifications (English canonical, German translation pending)
docs/                 # MkDocs source (en/, de/)
project/              # mission and roadmap
Taskfile.yml          # lint / test / docs automation
```

## Status

Early release `0.1.0`. The MVP skill set is in place; German translations of the specs,
Zeugnisanalyse, interview preparation, and PDF / DOCX export are on the roadmap
(`project/roadmap.md`).

## License

[MIT](LICENSE) — Copyright © 2026 nolte
