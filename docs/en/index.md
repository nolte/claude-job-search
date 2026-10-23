# claude-job-search

Claude Code plugin with skills and an agent for German-speaking job applications
(*Bewerbungsunterlagen*): Wunschprofil and fit check, single-column Lebenslauf, DIN-style
Anschreiben, Motivationsschreiben, Bewerbungs-E-Mail, a requirement match against the posting,
a quality gate before you send, export to PDF, DOCX, HTML or Markdown, and one folder per
application that records its status.

## Overview

You describe one **job posting**. The front-door skill `job-application-solution` checks your
profile, analyses the posting, shows you a plan, and only then produces the documents in
dependency order. Every fact comes from your local Datengrundlage. The profile, `profil.md`, is
derived from it with a source reference per entry. Unknown facts are marked, never invented.

Each application gets its own folder, the Vorgang. It holds the posting, the analysis, the
documents, the check report, and `vorgang.md` with the status and the history of the
application. See [Getting started](getting-started.md) for the walk-through and the
[Glossary](glossary.md) for the terms.

## Start here

- New here? Read [Getting started](getting-started.md): install, configure, capture your data, first application.
- Run `/claude-job-search:job-application-profile-capture` first if you have no Datengrundlage yet.
- Want to know what you are looking for before you apply? Run `/claude-job-search:job-application-traumjob-interview` once, then `/claude-job-search:job-application-fit-check` for each posting or company.
- Run `/claude-job-search:job-application-solution` with the posting text for a complete application.
- Run `/claude-job-search:job-application-quality-gate` on any existing application folder before sending.
- Applying through a recruiter or an agency? Read [Counterparts](counterparts.md) first.
- Want Claude to read LinkedIn postings, company pages and profiles directly? See [LinkedIn access](linkedin.md), an optional MCP server with its own risks.

!!! note "Privacy"
    Application data stays local, in the folder you configure (by default `job-application/`).
    The folder is git-ignored by default; keeping it in a private, unpublished repository is
    allowed and your decision. Nothing is sent anywhere by a skill.

!!! note "Not covered yet"
    Sending, replies and interviews are recorded by you in `vorgang.md` and `notizen.md`
    (or in Obsidian); a tracking skill is on the roadmap, as are interview preparation and
    Zeugnis analysis. Export produces DOCX, HTML and Markdown everywhere; PDF needs LuaLaTeX
    or the export container, see [Export](export.md).

!!! info "For developers"
    The conventions behind all of it are in the specs under `spec/job-application/`, starting
    with `spec/job-application/konventionen/en.md` and `spec/job-application/lokale-struktur/en.md`
    (canonical in English, German translation pending). The index is `spec/README.md`.
