# Roadmap

## MVP (this release, 0.1.0)

- [x] Plugin scaffold in the claude-home-assistant repository structure
- [x] DACH conventions spec (`spec/bewerbung/konventionen/en.md`)
- [x] Front-door router `bewerbung-solution`
- [x] Profile intake `bewerbung-profil-erfassen`
- [x] Stellenanzeige analysis with requirement match `bewerbung-stellenanzeige-analysieren`
- [x] Lebenslauf `bewerbung-lebenslauf-erstellen`
- [x] Anschreiben `bewerbung-anschreiben-erstellen`
- [x] Bewerbungs-E-Mail `bewerbung-email-erstellen`
- [x] Quality gate `bewerbung-pruefen` and read-only agent `bewerbungs-reviewer`

## Next

- German translations of the specs (`de.md`) via `/nolte-shared:spec`
- Zeugnis-Analyse (Arbeitszeugnis-Codes in German, read-only interpretation)
- Initiativbewerbung and Quereinstieg variants as dedicated skills
- Export to PDF / DOCX with a documented pandoc recipe
- Interview preparation skill (Vorstellungsgespräch)
- Automated tests for the Markdown templates (`task test`, currently a placeholder)
