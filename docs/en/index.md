# claude-job-search

Claude Code plugin with skills and an agent for German-speaking job applications
(*Bewerbungsunterlagen*): tabular Lebenslauf, DIN-style Anschreiben, Bewerbungs-E-Mail,
a requirement match against the posting, and a quality gate before you send.

## Overview

You describe one **job posting**. The front-door skill `bewerbung-solution` checks your
profile, analyses the posting, shows you a plan, and only then produces the documents in
dependency order. Every fact comes from one local profile file, `bewerbung/profil.md`.
Unknown facts are marked, never invented.

## Start here

- Run `/claude-job-search:bewerbung-solution` with the posting text for a complete application.
- Run `/claude-job-search:bewerbung-profil-erfassen` first if you have no profile yet.
- Run `/claude-job-search:bewerbung-pruefen` on any existing folder before sending.

The conventions behind all of it are in the spec `spec/bewerbung/konventionen/en.md`.

!!! note "Privacy"
    Application data stays in the git-ignored `bewerbung/` folder and is never committed.

!!! note "Not covered yet"
    Zeugnis analysis, interview preparation, and PDF / DOCX export are on the roadmap.
