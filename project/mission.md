# Mission

`claude-job-search` gives job seekers in the German-speaking region a Claude Code
skill set that produces complete, consistent and fact-true application documents
(Lebenslauf, Anschreiben, Motivationsschreiben, Bewerbungs-E-Mail) from a single
Datengrundlage, tailored to a concrete Stellenanzeige, matched against the candidate's
own Wunschprofil, and checked against DACH conventions. Beyond the documents, it keeps
the process: one Vorgang per application with status and history, from intake to closure.

## Principles

- **Facts from the candidate only.** No invented experience; gaps are marked, not hidden (spec R-1).
- **One Datengrundlage, many documents.** The Datengrundlage is the single source of truth; `profil.md` is derived from it and carries a source reference per entry.
- **Plan before generate.** The front door shows the plan and waits for approval.
- **Local and private.** Application data never leaves the working copy by default.
- **The process is visible.** Every application has a `vorgang.md` with a fixed set of status values and a history; nothing happens to an application that is not recorded there.

## Audience

- The plugin author (dogfooding, own applications).
- Later public users: job seekers, career changers and first-time applicants who write in German.
