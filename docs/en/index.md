# claude-job-search

Claude Code plugin with skills and an agent for German-speaking job applications
(*Bewerbungsunterlagen*): tabular Lebenslauf, DIN-style Anschreiben, Bewerbungs-E-Mail,
a requirement match against the posting, and a quality gate before you send.

## Overview

You describe one **job posting**. The front-door skill `job-application-solution` checks your
profile, analyses the posting, shows you a plan, and only then produces the documents in
dependency order. Every fact comes from your local Datengrundlage. The profile, `job-application/profil.md`, is derived from it with a source reference per entry.
Unknown facts are marked, never invented.

## Start here

- Run `/claude-job-search:job-application-solution` with the posting text for a complete application.
- Run `/claude-job-search:job-application-profile-capture` first if you have no profile yet.
- Run `/claude-job-search:job-application-quality-gate` on any existing folder before sending.

The conventions behind all of it are in the spec `spec/job-application/konventionen/en.md`.

!!! note "Privacy"
    Application data stays in the git-ignored `job-application/` folder and is never committed.

!!! note "Not covered yet"
    Zeugnis analysis and interview preparation are on the roadmap. Export produces DOCX, HTML and Markdown; PDF needs LuaLaTeX.
