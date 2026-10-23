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

Spec: `spec/job-application/konventionen/en.md` R-1 (facts), R-2, R-9 (Datengrundlage: R-9.1 location, R-9.3
Zeugnisse, R-9.4 intake, R-9.5 hash, R-9.6 sources, R-9.8 Pflegelauf, R-9.9 boundary, R-9.10 Konfiguration);
`spec/job-application/lokale-struktur/en.md` LS-2 (Anker, boundary, keys), LS-4, LS-5, LS-7, LS-8.1, LS-9;
`cv-generierung` CG-2.4, CG-9; `lebenslauf` LB-8.3; `recherche` RC-5.4. Requirement:
`project/requirements/eigene-datengrundlage.md`.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`),
`grundlage` and `grundlage_index` from its frontmatter. Relative paths resolve against the working directory that
contains `job-application/konfiguration.md` (LS-2.6). **No Anker:** ask once for the path of the Wurzel and write it
there. The only keys ever written are `wurzel`, `grundlage`, `grundlage_index` (LS-2.5); `grundlage_index` only in
directory mode (R-9.10).

**Repository boundary (LS-2.4, R-9.9).** Before reading or writing, resolve the absolute path of the Wurzel and of
the Grundlage (and the index note). Walk up from each, including the directory itself. If any directory contains
`.claude-plugin/plugin.json` with `"name": "claude-job-search"`, **refuse**, report that the Wurzel and the
Grundlage must lie outside the plugin repository and that the paths go into `job-application/konfiguration.md`
(`wurzel`, `grundlage`), and write nothing.

Two artefacts, in this order:

1. **Datengrundlage (Grundlage)** `<wurzel>/grundlage/lebenslauf-chronologisch.md` (default, spec R-9.1). The full,
   chronological record. It is the source of truth. If the user keeps one note per Station in a directory, `grundlage`
   names the directory and `grundlage_index` names the index note (R-9.1, R-9.10). The Grundlage lives where
   `grundlage` points; that can be outside the Wurzel (R-9.1).
2. **Profil** `<wurzel>/profil.md`. Derived from the Grundlage, condensed, with a
   source reference per entry. The other `job-application-*` skills read the profile and follow its references into
   the Grundlage.

## Stage A: Datengrundlage

**If the Datengrundlage exists:** do not create a new one and skip Stage A (R-9.8). Run Stage B when the user wants
the profile (re-)derived. If the user also wants the Grundlage checked or completed, `job-application-cv-maintain`
runs the Pflegelauf first and hands back to Stage B when it is done. When this skill is invoked from
`job-application-cv-maintain`, run Stage B directly and do not hand back.

**If it does not exist:**

1. Ask whether the user has existing documents (CV as PDF/DOCX/Markdown, certificates,
   notes). Process them first (R-9.4). Read only the documents the user names (LS-9.2); never write into `rohdaten/`
   (LS-5.5). Ask whether the Grundlage is one file or a directory of notes (file mode is the default).
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
- Quelle: [<datei>](../rohdaten/<datei>), S. <n>
- Bestätigt: ja | nein
- Aufgaben: …
- Ergebnisse (mit Zahl nur, wenn belegt): …
- Team: Größe, Rollen, Berichtslinie; Führung: ja | nein | ungeklärt
- Werkzeuge: …
- Zeugnis: siehe Eintrag in „Zeugnisse“
- [KLÄREN: …] / [ERGÄNZEN: …]

### MM/JJJJ – MM/JJJJ | <vom Nutzer gewählte neutrale Formulierung>
- Lücke über zwei Monate; Bestätigt: ja | nein

## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse (Niveau nach GER)
## IT- und Fachkenntnisse
## Weiterbildung und Zertifikate
## Zeugnisse
### <Position> — <Arbeitgeber>
- Datei: [<datei>](../rohdaten/<datei>) · Datum · Aussteller
  > Wortlaut der Schlussbeurteilung
## Zielrichtung
- Gesuchte Rollen, Standort, Eintrittstermin (optional)

## Ehrenamt und Interessen (optional)

## Pflegeverlauf
- JJJJ-MM-TT: angelegt aus <Quelle>
```

The link path in `Quelle` and `Datei` is the relative path from the Grundlage file to the scan (LS-8.1). Optional
*Persönlich* and *Referenzen* sections are not created here: LS-4 assigns them to `job-application-cv-maintain`
(scope `persönlich`, resp. on the user's statement with consent and date). A reference is never written into a
document without the user's request (R-5, LB-8.3).

**Directory mode.** Create the directory and the index note. The index note carries `stand: YYYY-MM-DD` in its
frontmatter and the section `## Pflegeverlauf` with the first line (R-9.1, R-9.5). Then write `grundlage` (the
directory) and `grundlage_index` (the index note) into `job-application/konfiguration.md`, keeping free notes below the
frontmatter (LS-2.5); without `grundlage_index` the hash script stops. Each station note carries `typ: station`,
`titel`, `arbeitgeber`, `ort`, `zeitraum_von`, `zeitraum_bis`, `fuehrung` (`ja`, `nein`, `ungeklärt`) in its
frontmatter and the sections `## Stichpunkte`, `## Erfolge`, `## Team` (CG-2.4). The Zeugnisse go into notes of
their own (R-9.3).

**Rules for Stage A:**

- German. Original wording in another language is marked, e.g. `(EN-Original)`.
- With documents, the interview asks only for gaps, contradictions and `[KLÄREN]` markers (R-9.4).
- Each adopted station is confirmed by the user (`Bestätigt: ja`) before it counts.
- Contradictions (two different periods for one station) are marked `[KLÄREN]`, not smoothed over.
- Certificates: one entry per Zeugnis with the full wording of the closing assessment (R-9.3). The scan stays outside
  the file and outside git.
- Gaps over two months: ask for the reason once. The user chooses one of `Elternzeit`, `Pflege eines Angehörigen`,
  `Weiterbildung`, `Berufliche Neuorientierung`, `Bewerbungsphase`; the chosen wording is written as an own entry
  in the stations section (template above). Only if the user declines or does not know, the gap carries
  `[ERGÄNZEN: Grund der Lücke]`. Never write `Auszeit` as a default and never infer a reason (R-2, CG-9).

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
- Quelle: [Grundlage, <Position> — <Arbeitgeber>](../grundlage/lebenslauf-chronologisch.md#<Überschrift der Station>)
- Aufgaben: …
- Ergebnisse: …
## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse
## IT- und Fachkenntnisse
## Weiterbildung und Zertifikate
## Zeugnisse
## Zielrichtung
## Offene Punkte
- [ERGÄNZEN: …]
```

Source references are Markdown links with a relative path from `profil.md` to the Grundlage and the anchor of the
`###` heading of the Station (R-9.6, LS-7.5, LS-7.6, LS-8.1); in directory mode the path names the station note, with
its heading. Adjust the example path to the configured `grundlage`.

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
4. **Sensitive fields stay optional.** Foto, Geburtsdatum, Familienstand, Staatsangehörigkeit and Konfession are
   recorded only if the user wants them (R-2, R-8.2, R-9.8); the Persönlich section is written by
   `job-application-cv-maintain` (LS-4).
5. **Local only.** The profile lives in the Wurzel (LS-5.7); the Grundlage lives where `grundlage` points (R-9.1).
   Both are git-ignored by default; tracking them in a private repository is the user's decision (R-6). Nothing is
   committed by a skill. No network access; LinkedIn pages are never fetched, only pasted content or an export the
   user names (RC-5.4).
6. **Derived, not separate.** Do not write a profile entry that has no station in the Grundlage.
7. **Raw material is read-only** and read only when the user names it (LS-5.5, LS-9.2).
