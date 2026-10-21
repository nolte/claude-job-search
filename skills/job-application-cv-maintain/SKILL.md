---
name: job-application-cv-maintain
description: "Maintains an existing Datengrundlage (chronological Lebenslauf in Markdown) in a guided interview: checks the required core points and inconsistencies, asks only about the findings, writes each confirmed answer into the file, and records a Pflegeverlauf with a fresh hash. Works on the file referenced in job-application/konfiguration.md, typically the user's own notes. Use on \"vervollständige meinen Lebenslauf\", \"pflege meine Datengrundlage\", \"prüfe meine Stationen auf Lücken\", or equivalent German requests. Don't use for the first build from raw documents (job-application-profile-capture), for the derived profile (job-application-profile-capture), or for the tailored CV (job-application-cv-create)."
tags: [bewerbung, datengrundlage, pflege, interview, deutsch]
phase: intake
summary: "Guided maintenance interview for an existing Datengrundlage: checks core points and inconsistencies, asks only about the findings, writes confirmed answers."
summary_de: "Geführtes Pflegeinterview für eine bestehende Datengrundlage: prüft Kernpunkte und Unstimmigkeiten und schreibt bestätigte Antworten in die Datei."
use_when:
  - "you already have a notes file or Datengrundlage and want it complete and consistent"
  - "you added a station, a certificate, or a training and need it recorded"
  - "you want a check of your Lebenslauf for gaps and contradictions"
dont_use_when:
  - situation: "There is no Datengrundlage yet and you have raw documents to process"
    alternative: job-application-profile-capture
  - situation: "You want the tailored CV for a posting"
    alternative: job-application-cv-create
  - situation: "You want the whole application for a posting"
    alternative: job-application-solution
see_also:
  - job-application-profile-capture
  - job-application-cv-create
  - job-application-quality-gate
---

# Bewerbung Lebenslauf vervollständigen

Spec: `spec/job-application/konventionen/en.md` R-9 (Datengrundlage, path in R-9.1, config in R-9.10)
and R-9.8 (Pflegelauf). Requirement: `project/requirements/datengrundlage-pflege-interview.md`.

## Inputs

- **Pfad.** Read `job-application/konfiguration.md`, frontmatter keys `grundlage` (a file, or a directory of notes) and `grundlage_index` (required for a directory, spec R-9.1, R-9.10). If the file or key is
  missing, use `job-application/grundlage/lebenslauf-chronologisch.md`. An argument given in the session
  overrides both, and the user is asked whether to store it in the configuration. In directory mode the interview reads all notes; a change goes into the note of the addressed Station, the Pflegeverlauf into the index note.
- **Schwerpunkt** (optional): `alle` (default), `nur stationen`, `nur zertifikate`, `persönlich`.
  Optional personal fields (Geburtsdatum, Familienstand, Staatsangehörigkeit, Foto) are asked only
  for `persönlich` or when the user asks for them (FA-P9).
- **Rohdaten** (optional): new CVs or certificates to process first (R-9.4).

## Step 0: Repository boundary (decision E-P3)

Before reading anything, resolve the absolute path of the Grundlage. Walk up from its directory,
including the directory itself. If any directory contains `.claude-plugin/plugin.json` with
`"name": "claude-job-search"`, **refuse** and report:

> Der Pfad liegt im Plugin-Repository. Lege die Datengrundlage außerhalb ab und trage den Pfad
> in `job-application/konfiguration.md` unter `grundlage` ein.

Do not write to the file in that case.

## Step 1: Bestandsaufnahme

1. Read the file. Keep its frontmatter, `tags`, and structure unchanged.
2. Check the core points of the checklist (below) and the rules of the findings table.
3. Show the finding report: counts per level (Blocker, Warnung, Hinweis) and the section of each
   finding. Do not show full values of sensitive fields in the report.

If there are no findings, go to step 5.

## Step 2: Fragen in Runden

- Blocker first, then Warnungen, then Hinweise.
- At most three questions per round. Each question names the section and states the finding in one
  sentence, then asks for the missing value or the clarification.
- Ask nothing about sections without a finding (FA-P2).

## Step 3: Antwort verarbeiten

| Antwort des Nutzers | Wirkung |
|---|---|
| Wert genannt | Change is shown as a diff of the passage. Written after confirmation. |
| „weiß ich nicht“ / übersprungen | Open marker stays: `[ERGÄNZEN: …]` or `[KLÄREN: …]`. No invented value (FA-P4). |
| „nicht relevant“ | Recorded in the Pflegeverlauf as „zurückgestellt“. Not asked again in later runs unless the user wants it. |

After each answer, save the file at once (NFA-P1). Each change is recorded in the Pflegeverlauf
(FA-P6).

## Step 4: Bestätigung je Station

Each new or changed station is shown in full and confirmed by the user. Only then is
`Bestätigt: ja` set. Unconfirmed stations stay open.

## Step 5: Abschluss

1. Set `stand: <heutiges Datum>` in the frontmatter.
2. Compute the hash with `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md`
   (`<plugin-root>` is the plugin directory, two levels above this skill's base directory; spec R-9.5).
   Report `hash` and `stand`. If the script stops with a `Blocker:` line, report it and do not close.
   Derived artefacts with an older `grundlage_hash` are stale and are flagged by `job-application-quality-gate`.
3. Write the closing report: completed points, open points by level, remaining blockers.
4. If the profile `job-application/profil.md` exists and its `grundlage_hash` differs from the new hash,
   say that it needs re-deriving with `job-application-profile-capture`.

## Checklist (Kernpunkte)

| Bereich | Kernpunkt | Status |
|---|---|---|
| Kontakt | Name, Anschrift, Telefon, E-Mail | Pflicht |
| Kontakt | LinkedIn | optional |
| Persönlich | Geburtsdatum, Familienstand, Staatsangehörigkeit, Foto | optional, nur Schwerpunkt `persönlich` |
| Station | Zeitraum `MM/JJJJ – MM/JJJJ` oder `MM/JJJJ – heute` | Pflicht |
| Station | Position exakt wie im Zeugnis | Pflicht |
| Station | Arbeitgeber mit Rechtsform und Ort | Pflicht |
| Station | mindestens eine Aufgabe | Pflicht |
| Station | Ergebnis, belegt durch Zahl oder qualitativ | empfohlen für relevante Stationen |
| Station | Zeugnis: Datei, Datum, Aussteller, Wortlaut der Schlussbeurteilung | Pflicht, wenn ein Zeugnis existiert |
| Ausbildung | Abschluss, Ort, Zeitraum | Pflicht |
| Schule | Abschluss, Schule, Jahr | Pflicht |
| Weiterbildung | Titel, Anbieter, Jahr | empfohlen |
| Sprachen | Sprache mit GER-Niveau | Pflicht |
| IT-Kenntnisse | Werkzeug mit Niveau oder Nutzungsdauer | empfohlen |
| Zielrichtung | gesuchte Rollen, Standort, Eintrittstermin | optional |

## Prüfregeln

| Stufe | Befund | Beispiel |
|---|---|---|
| Blocker | Pflichtpunkt fehlt oder widerspricht sich | Kontakt leer; zwei Zeiträume für dieselbe Station |
| Warnung | Format oder Plausibilität weicht von R-2/R-2.1 ab | Jahresangabe statt `MM/JJJJ`; Lücke über zwei Monate ohne Erklärung; Ende vor Beginn |
| Hinweis | Inhalt verbesserbar | Station ohne Ergebnis; Zahl ohne Beleg; mögliche Überschneidung von Ausbildung und Schule; mehr Stichpunkte, als eine Ausgabe erlaubt (R-9.11) |

Additional rules:

- Overlapping full-time stations are reported, not corrected.
- Gaps over two months need a neutral entry (R-2.1).
- Bullets: the Grundlage has no bullet limit. The output limits of R-2.1 are applied per application when the Lebenslauf is selected (R-9.11). Too many bullets in a station is a Hinweis, never a Warnung.
- Every number in a bullet must be backed by the file or a certificate. An unbacked number is a blocker (R-1).
- Sprachniveaus are checked against GER levels (A1–C2).

## Hard rules

1. **Nur Befunde fragen.** No questions about sections without a finding.
2. **Keine Fakten ohne Bestätigung.** Unknown answers stay open markers.
3. **Nur angefragte Stellen ändern.** The rest of the file, including frontmatter and structure, stays
   byte-identical.
4. **Pflegeverlauf führen.** Every applied change gets a dated line in `## Pflegeverlauf`.
5. **Abbruch ohne Verlust.** Save after each confirmed answer.
6. **Lokal bleiben.** No network access. The report in chat shows section names and findings, not full
   values of sensitive fields.
7. **Repository-Grenze.** Step 0 applies before anything else.
8. **Nur Vollständigkeit.** The skill checks whether the Grundlage is complete (R-9.8). It selects nothing for a Stellenanzeige (R-9.11, point 7).
