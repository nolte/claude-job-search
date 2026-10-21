---
name: job-application-profile-capture
description: "Builds the user's own Datengrundlage (chronological Markdown, spec R-9) from existing CVs, certificates, and notes, then derives job-application/profil.md from it with source references. Asks only for gaps and contradictions. Never invents facts; unknown items become [ERGÄNZEN] or [KLÄREN]. Use on \"lege meine Datengrundlage an\", \"arbeite meinen alten Lebenslauf auf\", \"erfasse mein Profil\", \"aktualisiere meine Daten\", or equivalent German requests. Don't use to write an application for a posting (job-application-solution), to analyse a posting (job-application-posting-analysis), or to produce the Lebenslauf itself (job-application-cv-create)."
tags: [bewerbung, datengrundlage, profil, intake, deutsch]
phase: intake
summary: "Builds the user's chronological Datengrundlage from raw documents and derives the profile with source references."
summary_de: "Erstellt die chronologische Datengrundlage des Nutzers aus Rohdaten und leitet daraus das Profil mit Quellenverweisen ab."
use_when:
  - "you are starting job applications and need your facts in one place"
  - "you have an old CV or certificates that must be turned into a usable basis"
  - "your career changed and the basis must be updated"
dont_use_when:
  - situation: "You already have a current basis and want a document from it"
    alternative: job-application-cv-create
  - situation: "You want the whole application for a posting"
    alternative: job-application-solution
see_also:
  - job-application-solution
  - job-application-cv-create
---

# Bewerbung Datengrundlage und Profil

Spec: `spec/job-application/konventionen/en.md` R-1 (facts) and R-9 (Datengrundlage).
Requirement: `project/requirements/eigene-datengrundlage.md`.

Two artefacts, in this order:

1. **Datengrundlage** `job-application/grundlage/lebenslauf-chronologisch.md` (default, spec R-9.1). The full,
   chronological record. It is the source of truth. If the user keeps one note per Station in a directory, `grundlage` names the directory and `grundlage_index` names the index note (R-9.1, R-9.10).
2. **Profil** `job-application/profil.md`. Derived from the Grundlage, condensed, with a
   source reference per entry. The other `job-application-*` skills read only the profile.

## Stage A: Datengrundlage

**If the Datengrundlage exists:** do not create a new one. Hand over to `job-application-cv-maintain`, which runs the Pflegelauf (spec R-9.8).

**If it does not exist:**

1. Ask whether the user has existing documents (CV as PDF/DOCX/Markdown, certificates,
   notes). Process them first (R-9.4).
2. Without documents, interview station by station in batches of at most three questions.

**Entry template** (one per Station, reverse chronological):

```markdown
---
stand: YYYY-MM-DD
---

# Chronologischer Lebenslauf — Datengrundlage

## Berufliche Stationen

### MM/JJJJ – MM/JJJJ | Position | Arbeitgeber (Rechtsform), Ort
- Quelle: `rohdaten/<datei>`, S. <n>
- Bestätigt: ja | nein
- Aufgaben: …
- Ergebnisse (mit Zahl nur, wenn belegt): …
- Werkzeuge: …
- Zeugnis: `<datei>`, <Datum>, <Aussteller>
  > Wortlaut der Schlussbeurteilung
- [KLÄREN: …] / [ERGÄNZEN: …]

## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse (Niveau nach GER)
## IT- und Fachkenntnisse
## Weiterbildung und Zertifikate
## Ehrenamt und Interessen (optional)
```

**Rules for Stage A:**

- German. Original wording in another language is marked, e.g. `(EN-Original)`.
- Each adopted station is confirmed by the user (`Bestätigt: ja`) before it counts.
- Contradictions (two different periods for one station) are marked `[KLÄREN]`, not smoothed over.
- Certificates: full wording of the closing assessment. The scan stays outside the file and outside git.

## Stage B: Profil

Derive `job-application/profil.md` from the confirmed entries only:

```markdown
---
stand: YYYY-MM-DD
grundlage_stand: YYYY-MM-DD
grundlage_hash: <hash from grundlage_hash.py>
---

## Kontakt
## Berufserfahrung
### MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort
- Quelle: Grundlage, Station „<Position> — <Arbeitgeber>“
- Aufgaben: …
- Ergebnisse: …
## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse
## IT- und Fachkenntnisse
## Weiterbildung und Zertifikate
## Zielrichtung
## Offene Punkte
- [ERGÄNZEN: …]
```

Compute the hash with `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md`
(`<plugin-root>` is the plugin directory, two levels above this skill's base directory; spec R-9.5).
Store its `hash` value in `grundlage_hash` and its `stand` value in `grundlage_stand`. For a
Grundlage that is a directory, the script hashes all notes and the index note together. A
`Blocker:` line stops the derivation.

## Hard rules

1. **Never invent.** A missing date, grade, or skill becomes `[ERGÄNZEN: …]`.
2. **No polishing into claims.** A title stays as in the source. No extra seniority, no results the source does not state.
3. **Gaps are data.** Ask about unexplained gaps and record the neutral reason the user gives (e.g. „Elternzeit“).
4. **Sensitive fields stay optional.** Foto, Geburtsdatum, Familienstand and Konfession are recorded only if the user wants them (R-2, R-8.2).
5. **Local only.** Grundlage and profile live in `job-application/`, which is git-ignored. Nothing is committed.
6. **Derived, not separate.** Do not write a profile entry that has no station in the Grundlage.
