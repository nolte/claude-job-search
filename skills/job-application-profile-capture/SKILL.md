---
name: job-application-profile-capture
description: "Builds the user's own Datengrundlage (chronological Markdown, spec R-9) from existing CVs, certificates, and notes, then derives <wurzel>/profil.md from it with source references. Asks only for gaps and contradictions. Never invents facts; unknown items become [ERGÄNZEN] or [KLÄREN]. Use on \"lege meine Datengrundlage an\", \"arbeite meinen alten Lebenslauf auf\", \"erfasse mein Profil\", \"aktualisiere meine Daten\", or equivalent German requests. Don't use to write an application for a posting (job-application-solution), to analyse a posting (job-application-posting-analysis), or to produce the Lebenslauf itself (job-application-cv-create)."
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

Spec: `spec/job-application/konventionen/en.md` R-1 (facts) and R-9 (Datengrundlage). Paths:
`spec/job-application/lokale-struktur/en.md` LS-2.6, LS-4. Requirement: `project/requirements/eigene-datengrundlage.md`.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`),
`grundlage` and `grundlage_index` from its frontmatter. Relative paths resolve against the working directory that
contains `job-application/konfiguration.md` (LS-2.6). Without an Anker, ask for the path once and write it there.

Two artefacts, in this order:

1. **Datengrundlage (Grundlage)** `<wurzel>/grundlage/lebenslauf-chronologisch.md` (default, spec R-9.1). The full,
   chronological record. It is the source of truth. If the user keeps one note per Station in a directory, `grundlage` names the directory and `grundlage_index` names the index note (R-9.1, R-9.10).
2. **Profil** `<wurzel>/profil.md`. Derived from the Grundlage, condensed, with a
   source reference per entry. The other `job-application-*` skills read the profile and follow its references into
   the Grundlage.

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

## Kontakt
Name · Anschrift · Telefon · E-Mail · LinkedIn: optional · GitHub/Portfolio: optional

## Berufliche Stationen

### MM/JJJJ – MM/JJJJ | Position | Arbeitgeber (Rechtsform), Ort
- Quelle: `rohdaten/<datei>`, S. <n>
- Bestätigt: ja | nein
- Aufgaben: …
- Ergebnisse (mit Zahl nur, wenn belegt): …
- Team: Größe, Rollen, Berichtslinie; Führung: ja | nein | ungeklärt
- Werkzeuge: …
- Zeugnis: `<datei>`, <Datum>, <Aussteller>
  > Wortlaut der Schlussbeurteilung
- [KLÄREN: …] / [ERGÄNZEN: …]

## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse (Niveau nach GER)
## IT- und Fachkenntnisse
## Weiterbildung und Zertifikate
## Zielrichtung
- Gesuchte Rollen, Standort, Eintrittstermin (optional)

## Referenzen (optional)
- Name: … · Funktion: … · Firma: … · Einwilligung: ja | nein, <Datum>

## Ehrenamt und Interessen (optional)

## Pflegeverlauf
- JJJJ-MM-TT: angelegt aus <Quelle>
```

In directory mode (one note per Station) the station note carries `typ: station`, `titel`, `arbeitgeber`, `ort`,
`zeitraum_von`, `zeitraum_bis`, `fuehrung` (`ja`, `nein`, `ungeklärt`) in its frontmatter and the sections
`## Stichpunkte`, `## Erfolge`, `## Team` (CG-2.4). A reference is recorded only with the person's consent and its date;
it is never written into a document without the user's request.

**Rules for Stage A:**

- German. Original wording in another language is marked, e.g. `(EN-Original)`.
- Each adopted station is confirmed by the user (`Bestätigt: ja`) before it counts.
- Contradictions (two different periods for one station) are marked `[KLÄREN]`, not smoothed over.
- Certificates: full wording of the closing assessment. The scan stays outside the file and outside git.
- Gaps over two months: ask for the reason once. The user chooses one of `Elternzeit`, `Pflege eines Angehörigen`,
  `Weiterbildung`, `Berufliche Neuorientierung`, `Bewerbungsphase`, or declines; then the gap stays
  `[ERGÄNZEN: Grund der Lücke]`. Never write `Auszeit` as a default and never infer a reason (CG-9, D19).

## Stage B: Profil

Derive `<wurzel>/profil.md` from the confirmed entries only:

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
3. **Gaps are data.** Ask about unexplained gaps and record the neutral wording the user chooses (Stage A rules). No
   default, no inferred reason.
4. **Sensitive fields stay optional.** Foto, Geburtsdatum, Familienstand and Konfession are recorded only if the user wants them (R-2, R-8.2).
5. **Local only.** Grundlage and profile live in the Wurzel (LS-5.7), git-ignored by default; tracking it in a private
   repository is the user's decision (R-6). Nothing is committed by a skill.
6. **Derived, not separate.** Do not write a profile entry that has no station in the Grundlage.
