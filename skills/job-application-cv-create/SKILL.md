---
name: job-application-cv-create
description: "Writes the German Lebenslauf for one Vorgang from the Datengrundlage via <wurzel>/profil.md in the format of the situation (chronologisch, einseitig, kombiniert, ats): header line plus bullets per station, selection by evidence, gaps marked. Use on \"erstelle meinen Lebenslauf\", \"Lebenslauf für diese Stelle anpassen\", \"Lebenslauf im ATS-Format\". Don't use for the Anschreiben (job-application-cover-letter-create), the Grundlage (job-application-profile-capture), or Europass (R-8.4)."
tags: [bewerbung, lebenslauf, cv, deutsch, dach, ats]
phase: create
summary: "Builds a German CV from the profile in the format chosen for the situation, one header line plus bullets per station."
summary_de: "Erstellt einen deutschen Lebenslauf aus dem Profil im Format der Situation, je Station eine Kopfzeile mit Stichpunkten."
use_when:
  - "you need a German CV from your profile"
  - "you want the CV ordered and emphasised for a specific posting"
  - "the posting is an ATS or portal application"
dont_use_when:
  - situation: "You need the cover letter"
    alternative: job-application-cover-letter-create
  - situation: "The profile or Datengrundlage does not exist yet"
    alternative: job-application-profile-capture
  - situation: "You need Europass or an academic CV"
    alternative: "not supported (R-8.4); tell the user and point to the EU portal or to a dedicated academic structure"
see_also:
  - job-application-profile-capture
  - job-application-posting-analysis
  - job-application-cover-letter-create
  - job-application-quality-gate
---

# Bewerbung Lebenslauf erstellen

Spec: `spec/job-application/konventionen/en.md` R-1 (facts), R-2 (form), R-2.1 (entry block),
R-8 (format by situation, photo, ATS), R-9.5 (hash). Content decisions: `spec/job-application/cv-generierung/en.md`
CG-2 (source of truth), CG-3 (target fit), CG-4 (evidence), CG-5 (selection), CG-6 (length and bullets),
CG-7 (controlled rewriting), CG-8 (bullets and results), CG-9 (gaps and conflicts), CG-11 (ATS), CG-13.4 (scope of
the checks). Paths and status: `spec/job-application/lokale-struktur/en.md` LS-2.6, LS-6. Page limit: `spec/job-application/lebenslauf/en.md`
LB-2.3. This skill only reshapes facts that already exist in the Datengrundlage (Grundlage), through the profile.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`),
`grundlage` and `grundlage_index` from its frontmatter. Relative paths resolve against the working directory that
contains `job-application/konfiguration.md` (LS-2.6). `<wurzel>/<slug>/` is the Vorgang folder of this application;
`<wurzel>/<ausprägung>/` (for example `lebenslauf-basis`) is a folder for a Lebenslauf without a posting; it has no
`vorgang.md`.

## Inputs

- `<wurzel>/profil.md` (required). Its `grundlage_hash` is checked (step 1).
- The Grundlage (key `grundlage`, a file or a directory with `grundlage_index`), default
  `<wurzel>/grundlage/lebenslauf-chronologisch.md` (R-9.1, R-9.10). Required for the hash check and as the only source
  of the selection (R-9.11). In directory mode the selection reads all notes of the set.
- `<wurzel>/<slug>/analyse.md` (optional). Its rows (CG-4) decide which requirements the CV addresses and which entries
  get more room. A *Muss* row that is not *erfüllt* is never claimed in the CV.
- `situation` (asked if not given): Standard, Berufseinstieg, Schüler/Studierende/Praktikum, Quereinstieg, Lücke, Viele
  Stationen, ATS/Portal, Österreich, Schweiz. Europass and academic CV are not produced here (R-8.4).
- `kurzprofil` (asked at the plan gate, default no): a Kurzprofil of at most three sentences. Optional in every format,
  required in `kombiniert`.
- `foto` (optional): `ja` only if the user requests it or the situation is Österreich (R-8.2).

## Output

`<wurzel>/<slug>/lebenslauf.md` (or `<wurzel>/<ausprägung>/lebenslauf.md`):

```markdown
---
grundlage_hash: <current hash of the Grundlage>
format: chronologisch | einseitig | kombiniert | ats
auspraegung: <folder name of the variant>
version: <integer, starting at 1>
version_datum: <set only when the Version is frozen, LV-3>
---

# Lebenslauf

## Persönliche Daten
Name · Anschrift · Telefon · E-Mail · LinkedIn (optional) · GitHub/Portfolio (optional)

## Kurzprofil
<optional, at most three sentences; required in kombiniert>

## Berufserfahrung

### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin
- Event-Pipeline auf Basis von Python und Kafka betreut; Latenz von 800 ms auf 120 ms gesenkt
- Code-Reviews als Pflichtschritt für ein Team von 5 Entwicklern eingeführt

### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg
- [ERGÄNZEN: Aufgaben]

## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse (GER-Niveau)
## IT- und Fachkenntnisse
## Weiterbildung und Zertifikate

Ort, Datum
```

Section headings are the standard headings (R-8.3, CG-11.2a). No tables, no columns, no text boxes, no sub-bullets
(CV-17).

## Workflow

1. **Hash check.** Compute the hash with `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md`
   (R-9.5). If it differs from the profile's `grundlage_hash`, stop and report that the profile is stale. Offer to
   re-derive it with `job-application-profile-capture` (R-9.5).
2. **Situation.** If `situation` is missing, ask once. Propose the format from the R-8.1 table and take the user's
   decision. Record the chosen format in the frontmatter. Ask once whether a Kurzprofil is wanted (default no; required
   in `kombiniert`). When `job-application-solution` runs this skill, both answers come from its plan gate.
3. **Order.** Stations reverse chronological (R-2). Within a station, bullets by relevance to the posting when an
   analysis exists (R-2.1).
4. **Auswahl pro Bewerbung.** Select stations, bullets, and certificates from the Grundlage for this Stellenanzeige, as
   described in the section below (R-9.11).
5. **Entries.** Each selected station: header line `MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort` (R-2.1.1), then
   the bullets allowed by CG-6.2: up to 5 for a station with a *Muss* or *Wunsch* entry that is *erfüllt* or
   *teilweise*, up to 2 for other stations, header line only where a station does not support the application. A
   header with years only is a Warnung (CV-02), not a placeholder: keep the year and ask the user for the month through
   `job-application-cv-maintain`.
6. **Bullets.** Write each bullet in the form of CG-8.1 (object and scope first, past participle of the activity verb
   last, optional result after a semicolon, no subject, no final period). Use the verbs and avoid the phrases of CG-8.2,
   and write measured values as digits with their unit (CG-8.3). Use a number only if the Grundlage states it.
   Otherwise write a qualitative result **that the Grundlage states**; if it states none, keep the task without a
   result (CG-8.2). A routine task without a described scope or result is dropped, unless it is the only evidence for
   a *Muss* requirement; then it stays (CG-8.3).
7. **Length.** Standard about two pages (LB-2.3), einseitig for Einsteiger, Praktikum, Schüler. When space is short,
   cut in the order of CG-5.3: redundant bullets, bullets without evidence for a requirement, then whole stations with
   no *Muss* coverage. A *Muss*-covering station is never removed. More than two pages is a Blocker for the quality
   gate; an exception needs the user's decision in the session and is recorded in `pruefbericht.md`.
8. **Gaps.** A period over two months without a station needs a neutral entry (R-2, CG-9). If the Grundlage states the
   reason, write it. If no reason is known, **stop and ask the user once**: they choose one of `Elternzeit`, `Pflege
   eines Angehörigen`, `Weiterbildung`, `Berufliche Neuorientierung`, `Bewerbungsphase`, or decline. The answer is
   written into the Grundlage through `job-application-cv-maintain`, then the draft continues. Never write `Auszeit` as
   a default and never infer a reason. If the user declines, the entry is `[ERGÄNZEN: Grund der Lücke]`.
9. **Write** the file with the frontmatter. `auspraegung` and `version` follow `lebenslauf-versionen` LV-3. Do not set
   `version_datum` here: it is set when the user freezes the Version.
10. **Check.** Run `python3 <plugin-root>/scripts/cv_checks.py <wurzel>/<slug>/lebenslauf.md --grundlage <Grundlage> --analyse <wurzel>/<slug>/analyse.md`
    (add `--ats` for an ATS posting). In directory mode pass `--grundlage <Verzeichnis> --grundlage <grundlage_index>`;
    the option is repeatable. `<plugin-root>` is the plugin directory, two levels above this skill's base directory.
    Fix every Blocker before handing over; report the Warnungen and Hinweise with the file. The output is the
    reproducible basis for `job-application-quality-gate` (CG-13.3).
11. **Status.** If the folder holds `vorgang.md` (a Vorgang, LS-6.1), set `status: erstellt` and `grundlage_hash`, and
    append one line to `## Verlauf`: `- JJJJ-MM-TT: <alter Status> → erstellt, job-application-cv-create`. An
    Ausprägungsordner has no `vorgang.md`; skip this step there.
12. **Freeze on request.** Ask whether this state is the one to send. If the user confirms, copy it to
    `versionen/v<NNN>_<YYYY-MM-DD>.md` with `version_datum` set to today (LV-3). A frozen Version is never edited;
    a correction is a new Version. When the Arbeitsstand was frozen before, raise `version` by one first (LV-3.3), so a
    second freeze never reuses an existing `versionen/` file.

## Auswahl pro Bewerbung (R-9.11)

The Grundlage is complete and may hold more than one application needs. This step selects what the Lebenslauf for this
posting uses.

1. **Choose** stations, bullets, and certificates by the criteria of CG-5, in this order: coverage of *Muss*
   requirements, coverage of *Wunsch* requirements, evidence strength, scope and seniority, demonstrable results,
   redundancy, recency as tie-breaker only. Stations stay in reverse chronological order; relevance decides what is
   shown in full. Older strong evidence goes into the Kurzprofil or a *Relevante Projekte* block (CG-5.2).
2. **Only existing entries.** Use only entries that exist in the Grundlage. Do not add facts. Reword only as far as
   R-2.1 allows: shortening and reordering, no new claims.
3. **Output limits.** Bullet counts and page limits come from R-2 and R-2.1, applied to this output. They do not come
   from the Grundlage.
4. **Omissions and sources are visible.** Write the section `## Auswahl Lebenslauf` in `pruefbericht.md` of the
   folder: for every entry used, its Grundlage entry (file and heading, CG-2.3); for every omitted entry, a short
   reason; the Kurzprofil decision; a page-limit exception, if the user granted one. Create the file if it is missing.
   A re-run replaces only this section and leaves `## Auswahl Anschreiben`, `## Auswahl Motivationsschreiben` and
   `## Prüfung` unchanged. A left-out station must not leave an unexplained gap. A gap over two months stays as a
   neutral entry (R-2).
5. **Never store the selection** in the Grundlage or in the profile. The Grundlage carries no application-specific
   marks.

## Format rules by situation (R-8.1)

- **chronologisch:** default. Full station list, two pages at most.
- **einseitig:** one page. Education and internships first, then skills. Praktika with month, company, and at least
  two bullets (school internships are not listed).
- **kombiniert:** a Kurzprofil of at most three sentences, then the chronological station list. Used for Quereinstieg
  and many stations. Stations may be grouped in blocks such as „Praktika“, „Relevante Projekte“.
- **ats:** single column, standard headings, no photo, keywords only with evidence (R-8.3). The final file is
  Markdown; the export is a separate step (R-8.3.4): a text PDF by default, DOCX only when the portal asks for it.

## Hard rules

1. **Reverse chronological, single column, entry block per R-2.1.** No layout tables, no sub-bullets.
2. **Only Grundlage facts, through the profile.** Tailoring changes emphasis and order, never content.
3. **Gaps stay visible.** Shown with the reason the user chose (step 8), or as `[ERGÄNZEN: Grund der Lücke]`. No
   default wording, no inferred reason.
4. **No invented numbers** in bullets. A number that is not in the Grundlage is not written.
5. **Optional personal data stays out** unless the profile includes it and the situation allows it (R-8.2).
6. **Europass and academic CV are not produced.** The skill reports that they are not supported (R-8.4) and stops.
7. **Signature line:** Ort, Datum. A handwritten signature only for a paper copy (R-2).
8. **Controlled rewriting only** (CG-7). Shorten, reorder and reword verified content. Never add a number, team size,
   title, technology, or level, and never turn participation into ownership, assistance into leadership, exposure into
   expertise, or familiarity into proficiency (CG-7.2).
9. **Conflicts stop the draft.** A date or title that differs between the profile and the Grundlage, or a *Muss*
   requirement without evidence, is reported to the user and not resolved by choosing a value (CG-2.2, CG-4.5).
10. **Only the Wurzel is written** (LS-5.7): the Vorgang folder, `pruefbericht.md` and `vorgang.md` of this Vorgang.
