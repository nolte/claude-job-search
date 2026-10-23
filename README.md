# claude-job-search

[![CI](https://github.com/nolte/claude-job-search/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/nolte/claude-job-search/actions/workflows/ci.yml)

The `ci` workflow runs three required status checks on `develop`: `lint`, `test`, and `docs`. A green `CI` badge means all three passed on the latest `develop` commit.

Claude Code plugin with skills and an agent for German-speaking job applications
(*Bewerbungsunterlagen*) — Wunschprofil and fit check, single-column Lebenslauf, DIN-5008-style
Anschreiben, Motivationsschreiben, Bewerbungs-E-Mail, requirement match against the Stellenanzeige,
a quality gate before you send, and export to PDF, DOCX, HTML or Markdown. "Single-column" is the
term used throughout for the CV layout: one column, no tables, so a parser reads it in order.

## Purpose

Application documents for the DACH region follow specific conventions (reverse-chronological
single-column CV, one-page letter with a concrete subject line, attachment naming), and every
application repeats the same facts. This plugin keeps the facts in one local profile and
derives every document from it, so the output is consistent, tailored to the posting and
never invents experience.

- You describe a **job posting**; `job-application-solution` checks your profile, analyses the
  posting, and asks for approval of the plan before any document is written.
- Every fact comes from your Datengrundlage. `job-application/profil.md` is derived from it and keeps
  a source reference per entry. Gaps are marked `[ERGÄNZEN: …]` and block the quality gate until resolved.
  A requirement is marked as met only with evidence; missing evidence is reported, never claimed.
- The rules are codified in `spec/job-application/konventionen/en.md`.

## What you get

### Skills

| Skill | Phase | What it does |
|---|---|---|
| `job-application-solution` | plan | Front door. Checks the Datengrundlage and profile, analyses the posting, shows a plan, creates the documents in order, and ends with the quality gate. |
| `job-application-profile-capture` | intake | Builds the Datengrundlage (chronological Markdown) from existing CVs, certificates, and notes, and derives `profil.md` from it. |
| `job-application-cv-maintain` | intake | Maintains an existing Datengrundlage in a guided interview. Checks core points and inconsistencies, asks only about findings, and records changes in a Pflegeverlauf. |
| `job-application-traumjob-interview` | intake | Seven-phase preference interview. Stores the confirmed Wunschprofil (wishes, priorities, vetoes, hypotheses) in the Wurzel. See `spec/job-application/traumjob-interview/en.md`. |
| `job-application-fit-check` | analyse | Compares a posting or company with the confirmed Wunschprofil and writes `passung.md`: vetoes first, every value sourced, no score. |
| `job-application-posting-analysis` | analyse | Extracts requirements, tone, and requested documents from a Stellenanzeige and matches each requirement against the Grundlage with priority, evidence, strength, and status (erfüllt, teilweise, nicht belegt, unklar). Creates the Vorgang folder: `stellenanzeige.md`, `vorgang.md`, `notizen.md`, and the company file in `firmen/`. |
| `job-application-cv-create` | create | Creates the Lebenslauf in the format for the situation (chronological, one page, combined, ATS). Selects stations and bullets by relevance and evidence. Bullet limits are defaults with a maximum of 5 per station, see `spec/job-application/cv-generierung/en.md`. |
| `job-application-cover-letter-create` | create | Writes a one-page Anschreiben in DIN 5008 layout. Variants: job posting, unsolicited application, career change, entry-level. |
| `job-application-motivation-letter-create` | create | Writes a Motivationsschreiben when the posting, a university, or a funder asks for one. Reasons and goals come from the user's own words, never invented; every statement gets a provenance note. See `spec/job-application/motivationsschreiben/en.md`. |
| `job-application-email-create` | deliver | Writes the Bewerbungs-E-Mail: subject, short body, attachment list, and file names. |
| `job-application-export` | deliver | Exports a finished document to PDF (LaTeX), DOCX, HTML, or Markdown via `task export`. Carries the hash and checks that the content is unchanged. |
| `job-application-quality-gate` | review | Checks a folder before sending: blockers, warnings, and notes. Automated rules CV-01 to CV-18 come from `scripts/cv_checks.py`; the rest is judged in review. Sets the Vorgang status to `geprüft` or `in Arbeit`. |

### Agent

| Agent | What it does |
|---|---|
| `job-application-reviewer` | Read-only review of the whole set from a recruiter's view: traceability, consistency, requirement coverage, and language. Writes nothing. |

All skills read and write only inside the Wurzel, by default the `job-application/` folder of your
working copy. The folder is local and git-ignored by default; tracking it in a private, unpublished
repository is allowed (R-6, LV-4). The rules the skills follow are in
`spec/job-application/konventionen/en.md`.

## Use cases

- **Complete application for one posting** — `job-application-solution`.
- **Wunschprofil and fit** — `job-application-traumjob-interview` records what you want; `job-application-fit-check` compares a posting or company with it before you invest in documents.
- **Check whether your profile fits a posting** — `job-application-posting-analysis`.
- **Cover letter for a posting, an unsolicited application, or a career change** — `job-application-cover-letter-create`.
- **Review before sending** — `job-application-quality-gate`, plus the `job-application-reviewer` agent for a second read.
- **Export for sending or viewing** — `job-application-export`, e.g. `task export -- <datei.md> --format pdf --doc-type cv`.
- **Tracking after sending** — each application has a `vorgang.md` with status and history; you maintain sending, replies and interviews there (or in Obsidian), no skill does it for you yet.

## Getting started

1. Install the plugin from its marketplace, or run `claude --plugin-dir <path-to-this-repo>` for a local checkout.
2. Create `job-application/konfiguration.md` and point `grundlage` at your Datengrundlage (one Markdown file or a directory of notes).
3. Put your old CVs and certificates into `rohdaten/`, then run `/claude-job-search:job-application-profile-capture`.
4. Run `/claude-job-search:job-application-solution` with the text of a posting.

The step-by-step guide with examples is the docs page *Getting started*:
<https://nolte.github.io/claude-job-search/getting-started/> (German: *Erste Schritte*,
<https://nolte.github.io/claude-job-search/de/getting-started/>).

Optional network channels (LinkedIn, Handelsregister, web search) use third-party MCP servers. None is
required, the plugin registers none, and the same rules hold for all of them. Overview and rules are on the
docs page *Optional MCP servers*: <https://nolte.github.io/claude-job-search/mcp-servers/>.

Optional, for direct access to LinkedIn postings, company pages and your own profile: the
third-party [LinkedIn MCP server](https://github.com/stickerdaniel/linkedin-mcp-server). No skill
needs it. Setup and the risks (LinkedIn's terms prohibit automated access) are on the docs page
*LinkedIn access*: <https://nolte.github.io/claude-job-search/linkedin/>.

Optional, for checking a firm's identity against the Handelsregister: the third-party
[handelsregister-mcp server](https://github.com/lexdoudkin/handelsregister-mcp). No skill needs it.
Setup, the pinned commit and the risks are on the docs page *Handelsregister*:
<https://nolte.github.io/claude-job-search/handelsregister/>.

## Usage

Install the plugin via its marketplace, then invoke a skill with
`/claude-job-search:<skill>`, for example `/claude-job-search:job-application-solution`.

Application data lives in the Wurzel, by default the `job-application/` folder of the working copy:
local, git-ignored by default, tracking in a private, unpublished repository allowed. The anchor
`job-application/konfiguration.md` names the Wurzel and the Datengrundlage; every skill resolves its
paths through it.

### Work on the plugin itself (dogfooding)

```bash
claude --plugin-dir .
```

Use `/reload-plugins` inside the session to pick up changes. Local automation runs through
`Taskfile.yml`:

```bash
task install  # once: create .venv and install the docs dependencies
task lint     # pre-commit checks
task test     # unit and structure tests: CV checks, export (md, html, docx), skill structure
task docs     # build the MkDocs site, strict (shared module from nolte/taskfiles)
task export -- <datei.md> --format pdf --doc-type cv   # export a document (pdf, docx, html, md)
```

## Documentation

Published at <https://nolte.github.io/claude-job-search>, English and German.

## Structure

```text
.claude-plugin/       # plugin.json + marketplace.json manifests
skills/<name>/        # one skill per folder (SKILL.md); job-application-export also holds
                      #   templates/ (document.tex, cv.lua) and scripts/export_document.py
agents/<name>.md      # reusable sub-agents
spec/                 # specifications (English canonical, German translation pending), index in spec/README.md
scripts/              # deterministic checks: grundlage_hash.py, cv_checks.py
tests/                # stdlib unittest suite, run by task test (CV checks, export, skill structure, spec index)
docs/                 # MkDocs source (en/, de/), requirements.txt for the docs build
project/              # mission, roadmap, requirements
Dockerfile            # export image: pandoc, LuaLaTeX, German language support, poppler-utils
Taskfile.yml          # lint / test / docs / export automation
```

## Status

Release `0.2.0`. Implemented: the twelve skills and the agent listed above; Vorgang persistence
for the stages intake to review (`stellenanzeige.md`, `vorgang.md` with status and history,
`notizen.md`, `firmen/`); Wurzel resolution through `konfiguration.md`; export with manifest and
reproducible PDFs for frozen versions; text PDF as the default for ATS portals, DOCX only when a
portal demands it.

Open, on the roadmap (`project/roadmap.md`): a tracking skill for sending and follow-up (you
maintain `vorgang.md` by hand or in Obsidian for now), interview preparation, Zeugnisanalyse, and
the German translations of the specs.

Verified by `task test`: the CV rules CV-01 to CV-18, DOCX and HTML export with content check,
the skill structure, and the spec index. PDF export needs pandoc and LuaLaTeX. Without LuaLaTeX
its test is skipped, and the PDF page check is unverified. The plugin does not guarantee that any
specific ATS parser reads a document correctly.

## License

[MIT](LICENSE) — Copyright © 2026 nolte
