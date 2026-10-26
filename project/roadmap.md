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
- [x] Workflow orchestration (finding A-03): `scripts/workflow.py` keeps tasks with dependencies, attempts, leases, retries and approvals bound to content in `workflow/aufgaben.json`, reconciles them against `vorgang.md` (no second application status) and plans follow-ups and searches for a scheduler (`spec/job-application/workflow/en.md`). It executes no skill and sends nothing; no sending adapter ships (depends on A-02)
- [x] Recurring job search (finding A-01): persistent Suchauftrag with approval bound to its content, run log with limits, identity and de-duplication across runs, Warteschlange, hand-off to `job-application-solution` (`spec/job-application/stellensuche/en.md` ST-13 to ST-20, `scripts/stellensuche.py`); scheduled runs through `scripts/stellensuche_geplant.sh`, whose scheduler the user sets up and which has not run against a real JobSpy server
- [x] Technical ATS validation (finding A-05): `scripts/ats_checks.py` extends the quality report (`EX-03`, `ATS-01` to `ATS-05`, `KW-01`, spec `qualitaetssicherung` QS-13) with checks of the exported PDF, DOCX or HTML: valid file and fonts, hidden text, headings that keep their content, periods and stations, contact data, columns, tables, images, symbol ratings, key terms against the evidence. No score, no guarantee for any ATS; tested on synthetic exports, not yet on a real LuaLaTeX PDF of the template
- [x] Communication after the dispatch (finding A-02): `scripts/kommunikation.py` and the skill `job-application-follow-up` process messages the user hands over: assignment to a Vorgang (several candidates are never decided), mail type with a stated certainty, proposals for the `## Verlauf` line, status, result and Wiedervorlage, written only after the user approves the exact proposal by hash (`spec/job-application/mail-verwaltung/en.md` MV-18 to MV-27); Wiedervorlagen, follow-up basis with a deadline only the user sets, workflow tasks `rueckmeldung_pruefen` and `wiedervorlage`. Not implemented: reading Gmail, labels and the calendar (no connector) and sending (no adapter)
- [x] Application results (finding R-01): `scripts/bewerbung.py` and the spec `bewerbungsergebnis`: one table of allowed status changes (new final status `abgeschlossen`), phase and outcome kept apart from status and history, events with the day they happened apart from the day they were recorded, source and certainty, idempotent recording, corrections that keep the old value, reminders that contact no one, data-quality checks and a repeatable migration that invents nothing. Open: a stored hash of the sent files at the dispatch; reading a mailbox and sending (R-02); statistics are `lernen.py` (R-03)
- [x] Learning from results (finding A-06): `scripts/lernen.py` counts confirmed results across Vorgänge (response rate with open applications in the denominator, transitions, response times from existing dates, segments), writes a derived retrospective with its basis, and proposes improvements with sources and uncertainty that change no personal data (`spec/job-application/ergebnisauswertung/en.md`); workflow task `lernvorschlag_pruefen`

## Next

- Tracking of S7 (the dispatch itself: `versendet`, attachments, channel) and a Gmail connector with labels and calendar; replies are covered by `job-application-follow-up` for messages the user hands over
- Follow-up e-mail variant (Nachfass-E-Mail) in `job-application-email-create`
- Interview preparation (Vorstellungsgespräch): question catalogue, rounds, notes per round
- Offer and negotiation: the status values `angebot` and `verhandlung` exist, the skill is open
- Deletion routine for S10 (list Vorgänge whose `loeschen_ab` has passed, delete only after confirmation)
- Network and contacts across Vorgänge (people met in several processes, referrers)
- Versioning of Anschreiben and Motivationsschreiben like the Lebenslauf versions
- English application documents (spec stub R-11 in `konventionen`)
- Portal free-text fields (Anschreiben content split into the fields a portal asks for)
- Signature image in the PDF export
- German translations of the specs (`de.md`) via `/nolte-shared:spec`
- Zeugnis-Analyse (Arbeitszeugnis-Codes in German, read-only interpretation)
- Scenario tests for the CV checks and the exporters beyond the current suite (`task test`, see `tests/README.md`), including LuaLaTeX-based PDF checks
