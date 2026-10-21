# Roadmap

## MVP (this release, 0.1.0)

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

## Next

- German translations of the specs (`de.md`) via `/nolte-shared:spec`
- Zeugnis-Analyse (Arbeitszeugnis-Codes in German, read-only interpretation)
- Initiativbewerbung and Quereinstieg variants as dedicated skills
- Export to PDF / DOCX with a documented pandoc recipe
- Interview preparation skill (Vorstellungsgespräch)
- Scenario tests for the CV checks and the exporters beyond the current suite (`task test`, see `tests/README.md`), including LuaLaTeX-based PDF checks
