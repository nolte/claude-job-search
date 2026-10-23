---
name: job-application-cv-maintain
description: "Maintains an existing Datengrundlage (chronological Lebenslauf in Markdown) in a guided interview: checks the required core points and inconsistencies, asks only about the findings, writes each confirmed answer into the file, logs every change in the Pflegeverlauf, and at the close computes and reports the Grundlage hash (the Pflegeverlauf is part of it). Works on the file referenced in job-application/konfiguration.md, typically the user's own notes. Use on \"vervollständige meinen Lebenslauf\", \"pflege meine Datengrundlage\", \"prüfe meine Stationen auf Lücken\", or equivalent German requests. Don't use for the first build from raw documents (job-application-profile-capture), for the derived profile (job-application-profile-capture), or for the tailored CV (job-application-cv-create)."
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

Spec: `spec/job-application/konventionen/en.md` R-1, R-2/R-2.1, R-9 (Datengrundlage, path in R-9.1, hash R-9.5,
boundary R-9.9, config R-9.10), R-9.8 (Pflegelauf), R-9.11; `spec/job-application/lokale-struktur/en.md` LS-2
(Anker, boundary, keys), LS-4, LS-5, LS-7, LS-9; `cv-generierung` CG-2.4, CG-9; `lebenslauf` LB-6.2, LB-8.3.
Requirement: `project/requirements/datengrundlage-pflege-interview.md`.

## Inputs

- **Pfad.** Read `job-application/konfiguration.md` first (the Anker, LS-2.3): frontmatter keys `wurzel` (default
  `job-application/`), `grundlage` (a file, or a directory of notes) and `grundlage_index` (required for a directory,
  not allowed for a file; R-9.1, R-9.10). Relative paths resolve against the working directory that contains
  `job-application/konfiguration.md` (LS-2.6). If `grundlage` is missing, the Grundlage is
  `<wurzel>/grundlage/lebenslauf-chronologisch.md`. **No Anker:** ask once for the path of the Wurzel and write it
  there; the only keys written are `wurzel`, `grundlage`, `grundlage_index` (LS-2.5). A path given in the session is
  stored only in one of these keys, and only after asking. In directory mode the interview reads all notes; a change
  goes into the note of the addressed Station, the Pflegeverlauf and `stand` into the index note (R-9.1, R-9.8).
- **Schwerpunkt** (optional): `alle` (default) or `persönlich`. R-9.8 knows only `persönlich`: it adds the optional
  fields Geburtsdatum, Familienstand, Staatsangehörigkeit, Foto (Konfession only if the user states it, R-2), asked
  only for this scope or when the user asks (FA-P9). Partial scopes such as "nur Stationen" do not exist: the
  checklist always applies to the whole set (R-9.8).
- **Rohdaten** (optional): new CVs or certificates to process first (R-9.4). Read only, never written (LS-5.5), and
  only when the user names them (LS-9.2).

## Step 0: Repository boundary (decision E-P3)

Before reading anything, resolve the absolute path of the **Wurzel**, the **Grundlage** and, in directory mode, the
index note. Walk up from each, including the directory itself. If any directory contains
`.claude-plugin/plugin.json` with `"name": "claude-job-search"`, **refuse** (LS-2.4, R-9.9) and report:

> Der Pfad liegt im Plugin-Repository. Lege die Wurzel und die Datengrundlage außerhalb ab und trage die Pfade
> in `job-application/konfiguration.md` unter `wurzel` und `grundlage` ein.

Write nothing in that case.

## Step 1: Bestandsaufnahme

1. Read the file (all notes in directory mode). Keep its frontmatter, `tags`, and structure unchanged; only `stand`
   changes (step 5).
2. Check the core points of the checklist (below) and the rules of the findings table. Points the user marked
   „zurückgestellt“ in an earlier run are not reported.
3. Show the finding report: counts per level (Blocker, Warnung, Hinweis) and the section of each
   finding. Do not show full values of sensitive fields in the report.

If there are no findings, go to step 5. A second run without changes reports only the still-open points and writes
nothing (no `stand`, no Pflegeverlauf line; R-9.8, FA-P7).

## Step 2: Fragen in Runden

- Blocker first, then Warnungen, then Hinweise.
- At most three questions per round. Each question names the section and states the finding in one
  sentence, then asks for the missing value or the clarification.
- Ask nothing about sections without a finding (FA-P2).

## Step 3: Antwort verarbeiten

| Antwort des Nutzers | Wirkung |
|---|---|
| Wert genannt | Change is shown as a diff of the passage. Written after confirmation. |
| „weiß ich nicht“ / übersprungen | Open marker stays: `[ERGÄNZEN: …]` or `[KLÄREN: …]`. No invented value (FA-P4). Exception: a year-only period stays as it is, without a marker (CG-2.4, CG-9, LB-6.2). |
| „nicht relevant“ | Recorded in the Pflegeverlauf as „zurückgestellt“. Not asked again in later runs unless the user wants it. |

After each answer, save the file at once (NFA-P1). Each change is recorded in the Pflegeverlauf
(FA-P6).

## Step 4: Bestätigung je Station

Each new or changed station is shown in full and confirmed by the user. Only then is
`Bestätigt: ja` set. Unconfirmed stations stay open.

## Step 5: Abschluss

1. If at least one change was written: set `stand: <heutiges Datum>` in the frontmatter (file mode) or in the index
   note (directory mode; R-9.5).
2. Compute the hash with `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md`
   (`<plugin-root>` is the plugin directory, two levels above this skill's base directory; spec R-9.5), after the
   last write. Report `hash` and `stand`; the hash is not written into the Grundlage. If the script stops with a
   `Blocker:` line, report it and do not close.
   Derived artefacts with an older `grundlage_hash` are stale and are flagged by `job-application-quality-gate`.
3. Write the closing report: completed points, open points by level, remaining blockers.
4. If a change was written, or `<wurzel>/profil.md` is missing or its `grundlage_hash` differs from the new hash,
   offer to re-derive the profile and hand over to `job-application-profile-capture`, which runs only Stage B
   (LS-4). Run it only after the user agrees.

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
| Station | Ergebnis, belegt durch Zahl oder qualitativ (`## Erfolge` in der Stationsnotiz, CG-2.4) | empfohlen für relevante Stationen |
| Station | `## Team`: Teamgröße, Rollen um die Person, Berichtslinie (CG-2.4) | empfohlen |
| Station | `fuehrung`: `ja`, `nein` oder `ungeklärt` (Personalführung, CG-2.4, CV-16) | empfohlen; fehlend oder `ungeklärt` ist ein Hinweis (R-9.8) |
| Zeugnis | ein Eintrag je Zeugnis in der Sektion *Zeugnisse*: Datei, Datum, Aussteller, Wortlaut der Schlussbeurteilung (R-9.3, LS-4); die Station verweist nur darauf | Pflicht, wenn ein Zeugnis existiert |
| Lücke | Zeitraum über zwei Monate ohne Station: Eintrag mit neutralem Grund (`Elternzeit`, `Pflege eines Angehörigen`, `Weiterbildung`, `Berufliche Neuorientierung`, `Bewerbungsphase`) | Pflicht, sonst `[ERGÄNZEN: Grund der Lücke]` |
| Ausbildung | Abschluss, Ort, Zeitraum | Pflicht |
| Schule | Abschluss, Schule, Jahr | Pflicht |
| Weiterbildung | Titel, Anbieter, Jahr | empfohlen |
| Sprachen | Sprache mit GER-Niveau | Pflicht |
| IT-Kenntnisse | Werkzeug mit Niveau oder Nutzungsdauer | empfohlen |
| Zielrichtung | gesuchte Rollen, Standort, Eintrittstermin | optional |
| Referenzen | Name, Funktion, Firma, Einwilligung mit Datum (LS-4) | optional; nur auf Angabe des Nutzers, nie als Befund abgefragt |

## Prüfregeln

| Stufe | Befund | Beispiel |
|---|---|---|
| Blocker | Pflichtpunkt fehlt oder widerspricht sich | Kontakt leer; zwei Zeiträume für dieselbe Station |
| Warnung | Format oder Plausibilität weicht von R-2/R-2.1 ab | Jahresangabe statt `MM/JJJJ`; Lücke über zwei Monate ohne Eintrag; Ende vor Beginn |
| Hinweis | Inhalt verbesserbar | Station ohne Ergebnis; `fuehrung` fehlt oder `ungeklärt`; Zahl ohne Beleg; sich überschneidende Vollzeitstationen; mögliche Überschneidung von Ausbildung und Schule; mehr Stichpunkte, als eine Ausgabe erlaubt (R-9.11) |

Additional rules:

- Overlapping full-time stations are a Hinweis; they are reported, not corrected.
- Year-only period: ask once whether the month is known. If not, the year stays without a marker and without
  completion (CG-9, LB-6.2).
- Gaps over two months need a neutral entry (R-2, CG-9). The question offers the wording list of the checklist; the
  user picks one or declines. Never write `Auszeit` as a default and never infer a reason (R-2, CG-9). The chosen
  wording is written as an own entry in the stations section of the Grundlage; declining or skipping leaves
  `[ERGÄNZEN: Grund der Lücke]`. When `job-application-cv-create` stops at a gap, the answer is written here, into
  the Grundlage, not into the Lebenslauf.
- `fuehrung` is asked per station when it is missing or `ungeklärt`: did the candidate lead people (disziplinarisch or
  as Teamleitung)? Technical leadership of a topic is `nein`.
- Bullets: the Grundlage has no bullet limit. The output limits of R-2.1 are applied per application when the Lebenslauf is selected (R-9.11). Too many bullets in a station is a Hinweis, never a Warnung.
- Every number in a bullet should be backed by the file or a certificate. An unbacked number is a Hinweis here (R-9.8);
  the Blocker applies when the number reaches a Lebenslauf (`job-application-cv-create`, CV-05, R-1).
- Sprachniveaus are checked against GER levels (A1–C2).

## Hard rules

1. **Nur Befunde fragen.** No questions about sections without a finding.
2. **Keine Fakten ohne Bestätigung.** Unknown answers stay open markers.
3. **Nur angefragte Stellen ändern.** The rest of the file stays byte-identical. Frontmatter and structure are kept;
   the only frontmatter change is `stand` (R-9.5), plus the Pflegeverlauf lines.
4. **Pflegeverlauf führen.** Every applied change gets a dated line in `## Pflegeverlauf` (index note in directory mode).
5. **Abbruch ohne Verlust.** Save after each confirmed answer.
6. **Lokal bleiben.** No network access. The report in chat shows section names and findings, not full
   values of sensitive fields.
7. **Repository-Grenze.** Step 0 applies before anything else, to the whole Wurzel.
8. **Nur Vollständigkeit.** The skill checks whether the Grundlage is complete (R-9.8). It selects nothing for a Stellenanzeige (R-9.11, point 7).
