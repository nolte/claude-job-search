---
name: bewerbung-profil-erfassen
description: "Captures the candidate's career facts into one local source of truth, bewerbung/profil.md, that every other bewerbung-* skill reads. Asks only for missing fields, never invents facts, and marks unknown items as [ERGÄNZEN]. Use on \"lege mein Bewerbungsprofil an\", \"erfasse meinen Lebenslauf als Basis\", \"aktualisiere mein Profil\", or equivalent German requests. Don't use to write an application for a posting (bewerbung-solution), to analyse a posting (bewerbung-stellenanzeige-analysieren), or to produce the Lebenslauf itself (bewerbung-lebenslauf-erstellen)."
tags: [bewerbung, profil, intake, deutsch]
phase: intake
summary: "Builds bewerbung/profil.md, the single local source of truth for all application documents."
summary_de: "Erfasst das Kandidatenprofil in bewerbung/profil.md als einzige Faktenquelle für alle Bewerbungsdokumente."
use_when:
  - "you are starting job applications and need your facts in one place"
  - "your career changed and the profile must be updated"
dont_use_when:
  - situation: "You already have a current profile and want a document from it"
    alternative: bewerbung-lebenslauf-erstellen
  - situation: "You want the whole application for a posting"
    alternative: bewerbung-solution
see_also:
  - bewerbung-solution
  - bewerbung-lebenslauf-erstellen
---

# Bewerbung Profil erfassen

Spec: `spec/bewerbung/konventionen/en.md` R-1 (Faktentreue). The profile is the only
place facts live. Every document is derived from it.

## Output

`bewerbung/profil.md`, git-ignored, with this structure:

```markdown
---
stand: YYYY-MM-DD
---

## Kontakt
- Name:
- Anschrift:
- Telefon:
- E-Mail:
- LinkedIn (optional):

## Berufserfahrung
### <Rolle> — <Arbeitgeber>, <Ort>
- Zeitraum: MM/JJJJ – MM/JJJJ | seit MM/JJJJ
- Aufgaben:
- Ergebnisse (mit Zahlen, wenn vorhanden):
- Eingesetzte Technologien / Methoden:

## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse (Niveau nach GER, z. B. B2)
## IT- und Fachkenntnisse (mit Niveau oder Erfahrungsdauer)
## Weiterbildung und Zertifikate
## Ehrenamt und Interessen (optional)
## Zielrichtung
- Gesuchte Rollen:
- Standort / Remote:
- Frühester Eintrittstermin:
- Gehaltsvorstellung (privat, nur wenn der User sie angibt):

## Offene Punkte
- [ERGÄNZEN: …]
```

## Workflow

1. If `bewerbung/profil.md` exists, read it and ask only what is outdated or missing.
2. Otherwise ask for the sections in batches of at most three questions, in German.
3. Record answers verbatim where precision matters (dates, titles, numbers).
4. Write the file and set `stand` to today's date.

## Hard rules

1. **Never invent.** A missing date, grade, or skill becomes `[ERGÄNZEN: …]`.
2. **Do not polish facts into claims.** "Projektleitung" stays "Projektleitung" unless
   the user describes what was done; no extra seniority or results.
3. **Gaps are data.** Ask about unexplained gaps in the CV and record the neutral
   reason the user gives (for example "Elternzeit"). Never hide them.
4. **Sensitive fields stay optional.** Foto, Geburtsdatum, Familienstand and
   Konfession are only recorded if the user wants them (spec R-2).
5. **Local only.** Do not write the profile anywhere but `bewerbung/`, and do not
   commit it.
