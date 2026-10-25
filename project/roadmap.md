# Roadmap

## MVP

- [x] Plugin scaffold in the claude-home-assistant repository structure
- [x] DACH conventions spec (`spec/job-application/konventionen/en.md`)
- [x] Front-door router `job-application-solution`
- [x] Profile intake `job-application-profile-capture`
- [x] Stellenanzeige analysis with requirement match `job-application-posting-analysis`
- [x] Lebenslauf `job-application-cv-create`
- [x] Anschreiben `job-application-cover-letter-create`
- [x] Bewerbungs-E-Mail `job-application-email-create`
- [x] Quality gate `job-application-quality-gate` and read-only agent `job-application-reviewer`
- [x] Datengrundlage maintenance interview `job-application-cv-maintain` (spec R-9.8)
- [x] Preference interview `job-application-traumjob-interview` and fit check `job-application-fit-check` (`spec/job-application/traumjob-interview/en.md`)
- [x] Motivationsschreiben `job-application-motivation-letter-create` (`spec/job-application/motivationsschreiben/en.md`)
- [x] Export `job-application-export` to PDF (LaTeX), DOCX, HTML, Markdown, with manifest and reproducible PDFs for frozen versions (`spec/job-application/lebenslauf-versionen/en.md`)

## After the MVP

- [x] Vorgang persistence for the stages S1 to S5: `stellenanzeige.md`, `vorgang.md`, `notizen.md`, `firmen/<slug>.md` created by `job-application-posting-analysis`; plan written to `vorgang.md` by `job-application-solution`
- [x] Status and Verlauf in `vorgang.md`: fixed status values S0 to S10, each skill sets the status of its stage, `job-application-quality-gate` sets `geprüft` or `in Arbeit`
- [x] Wurzel resolution through `job-application/konfiguration.md` (keys `wurzel`, `grundlage`, `grundlage_index`); no hard-coded paths in the skills
- [x] Ausprägungsordner (for example `lebenslauf-basis/`) with `lebenslauf.md`, `pruefbericht.md`, `versionen/`, `export/` next to the Vorgänge
- [x] Anrede variants in Anschreiben and E-Mail
- [x] ATS rule: text PDF is the default, DOCX only when the portal demands it
- [x] Zeugnis rules (which Zeugnisse are attached, how they are named and referenced)
- [x] Kurzprofil as opt-in in the Lebenslauf
- [x] Retention and deletion (S10): final status other than `zusage` leads to deletion six months after closure, date `loeschen_ab` set by the user in `vorgang.md`, no skill deletes
- [x] Docs pages *Getting started*, *Glossary*, *Counterparts* in English and German
- [x] CV checks hardened (CV-01 to CV-17, including the sub-bullet rule CV-17)
- [x] Recurring job search (finding A-01): persistent Suchauftrag with approval bound to its content, run log with limits, identity and de-duplication across runs, Warteschlange, hand-off to `job-application-solution` (`spec/job-application/stellensuche/en.md` ST-13 to ST-20, `scripts/stellensuche.py`); scheduled runs through `scripts/stellensuche_geplant.sh`, whose scheduler the user sets up and which has not run against a real JobSpy server

## Next

- Tracking skill for S7 and S8: sending (`versendet`, attachments, channel), replies, interviews, follow-up dates (`wiedervorlage`); until then the user maintains `vorgang.md` by hand or in Obsidian
- Follow-up e-mail variant (Nachfass-E-Mail) in `job-application-email-create`
- Interview preparation (Vorstellungsgespräch): question catalogue, rounds, notes per round
- Offer and negotiation: the status values `angebot` and `verhandlung` exist, the skill is open
- Deletion routine for S10 (list Vorgänge whose `loeschen_ab` has passed, delete only after confirmation)
- Statistics and retrospective across Vorgänge (response rate per channel, time to reply, reasons for rejection)
- Network and contacts across Vorgänge (people met in several processes, referrers)
- Versioning of Anschreiben and Motivationsschreiben like the Lebenslauf versions
- English application documents (spec stub R-11 in `konventionen`)
- Portal free-text fields (Anschreiben content split into the fields a portal asks for)
- Signature image in the PDF export
- German translations of the specs (`de.md`) via `/nolte-shared:spec`
- Zeugnis-Analyse (Arbeitszeugnis-Codes in German, read-only interpretation)
- Scenario tests for the CV checks and the exporters beyond the current suite (`task test`, see `tests/README.md`), including LuaLaTeX-based PDF checks
