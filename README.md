# claude-job-search

[![ci](https://github.com/nolte/claude-job-search/actions/workflows/ci.yml/badge.svg)](https://github.com/nolte/claude-job-search/actions/workflows/ci.yml)

Claude Code plugin with skills and an agent for German-speaking job applications
(*Bewerbungsunterlagen*) — single-column Lebenslauf, DIN-5008-style Anschreiben, Bewerbungs-E-Mail,
requirement match against the Stellenanzeige, and a quality gate before you send.

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
| `job-application-posting-analysis` | analyse | Extracts requirements, tone, and requested documents from a Stellenanzeige and matches each requirement against the Grundlage with priority, evidence, strength, and status (erfüllt, teilweise, nicht belegt, unklar). |
| `job-application-cv-create` | create | Creates the Lebenslauf in the format for the situation (chronological, one page, combined, ATS). Selects stations and bullets by relevance and evidence. Bullet limits are defaults with a maximum of 5 per station, see `spec/job-application/cv-generierung/en.md`. |
| `job-application-cover-letter-create` | create | Writes a one-page Anschreiben in DIN 5008 layout. Variants: job posting, unsolicited application, career change, entry-level. |
| `job-application-email-create` | deliver | Writes the Bewerbungs-E-Mail: subject, short body, attachment list, and file names. |
| `job-application-export` | deliver | Exports a finished document to PDF (LaTeX), DOCX, HTML, or Markdown via `task export`. Carries the hash and checks that the content is unchanged. |
| `job-application-quality-gate` | review | Checks a folder before sending: blockers, warnings, and notes. Automated rules CV-01 to CV-15 come from `scripts/cv_checks.py`; the rest is judged in review. |

### Agent

| Agent | What it does |
|---|---|
| `job-application-reviewer` | Read-only review of the whole set from a recruiter's view: traceability, consistency, requirement coverage, and language. Writes nothing. |

All skills read and write only in the git-ignored `job-application/` folder of your working copy.
The rules they follow are in `spec/job-application/konventionen/en.md`.

## Use cases

- **Complete application for one posting** — `job-application-solution`.
- **Check whether your profile fits a posting** — `job-application-posting-analysis`.
- **Cover letter for a posting, an unsolicited application, or a career change** — `job-application-cover-letter-create`.
- **Review before sending** — `job-application-quality-gate`, plus the `job-application-reviewer` agent for a second read.
- **Export for sending or viewing** — `job-application-export`, e.g. `task export -- <datei.md> --format pdf --doc-type cv`.

## Usage

Install the plugin via its marketplace, then invoke a skill with
`/claude-job-search:<skill>`, for example `/claude-job-search:job-application-solution`.

Application data lives in the git-ignored `job-application/` folder of the working copy.

### Work on the plugin itself (dogfooding)

```bash
claude --plugin-dir .
```

Use `/reload-plugins` inside the session to pick up changes. Local automation runs through
`Taskfile.yml`:

```bash
task lint     # pre-commit checks
task test     # unit and structure tests: CV checks, export (md, html, docx), skill structure
task docs     # build the MkDocs site
task export -- <datei.md> --format pdf --doc-type cv   # export a document (pdf, docx, html, md)
```

## Documentation

Published at <https://nolte.github.io/claude-job-search>, English and German.

## Structure

```text
.claude-plugin/       # plugin.json + marketplace.json manifests
skills/<name>/        # one skill per folder (SKILL.md)
agents/<name>.md      # reusable sub-agents
spec/                 # specifications (English canonical, German translation pending)
scripts/              # deterministic checks: grundlage_hash.py, cv_checks.py
tests/                # stdlib unittest suite, run by task test
docs/                 # MkDocs source (en/, de/)
project/              # mission and roadmap
Taskfile.yml          # lint / test / docs automation
```

## Status

Early release `0.1.0`. The MVP skill set is in place; German translations of the specs,
Zeugnisanalyse, and interview preparation are on the roadmap (`project/roadmap.md`).

Verified by `task test`: the CV rules CV-01 to CV-15, DOCX and HTML export with content check,
and the skill structure. PDF export needs pandoc and LuaLaTeX. Without LuaLaTeX its test is
skipped, and the PDF page check is unverified. The plugin does not guarantee that any specific
ATS parser reads a document correctly.

## License

[MIT](LICENSE) — Copyright © 2026 nolte
