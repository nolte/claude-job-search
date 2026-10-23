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
R-8 (format by situation, photo, ATS, Europass, Schweiz), R-9.5 (hash), R-9.9 (repository boundary). Document type:
`spec/job-application/lebenslauf/en.md` LB-1…LB-13 (sections LB-3, personal data and Kurzprofil LB-4, station block
LB-5, list entries LB-6, skills LB-7, optional sections LB-8, closing LB-9, dates LB-10, frontmatter LB-11.12,
posting overrides LB-12). Content decisions: `spec/job-application/cv-generierung/en.md` CG-1…CG-13 (CG-2 source of
truth, CG-4 evidence, CG-5 selection, CG-6 length and bullets, CG-7 controlled rewriting, CG-8 bullets, CG-9 gaps,
CG-10 personal details, CG-11 ATS, CG-13.4 scope of the checks). Variants and Versions:
`spec/job-application/lebenslauf-versionen/en.md` LV-2, LV-3, LV-8. Paths, status, invariants:
`spec/job-application/lokale-struktur/en.md` LS-2…LS-7. This skill only reshapes facts that already exist in the
Datengrundlage (Grundlage), through the profile.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). If it is missing, ask the user once for the path of
the Wurzel and write it there. Only the keys `wurzel` (default `job-application/`), `grundlage` and `grundlage_index`
are written (LS-2.5). Relative paths resolve against the working directory that contains
`job-application/konfiguration.md` (LS-2.6). `<wurzel>/<slug>/` is the Vorgang folder of this application;
`<wurzel>/<ausprägung>/` (for example `lebenslauf-basis`) is a folder for a Lebenslauf without a posting; it has no
`vorgang.md`.

## Step 0: Repository boundary (LS-2.4, R-9.9)

Before reading or writing anything, resolve the absolute path of the Wurzel and of the Grundlage. For each, walk up from
the directory, including the directory itself. If any directory contains `.claude-plugin/plugin.json` with
`"name": "claude-job-search"`, **refuse**, write nothing, and report:

> Der Pfad liegt im Plugin-Repository. Lege die Wurzel und die Datengrundlage außerhalb ab und trage den Pfad in
> `job-application/konfiguration.md` unter `wurzel` bzw. `grundlage` ein.

## Inputs

- `<wurzel>/profil.md` (required). Its `grundlage_hash` is checked (step 1).
- The Grundlage (key `grundlage`, a file or a directory with `grundlage_index`), default
  `<wurzel>/grundlage/lebenslauf-chronologisch.md` (R-9.1, R-9.10). Required for the hash check and as the only source
  of the selection (R-9.11). In directory mode the selection reads all notes of the set.
- `<wurzel>/<slug>/analyse.md` (optional). Its rows (CG-4) decide which requirements the CV addresses and which entries
  get more room; it also records the posting's instructions (LB-12). A *Muss* row that is not *erfüllt* is never
  claimed in the CV.
- `situation` (asked if not given): Standard, Berufseinstieg, Schüler/Studierende/Praktikum, Quereinstieg, Lücke, Viele
  Stationen, ATS/Portal, Österreich, Schweiz. Europass and academic CV are not produced here (R-8.4).
- `kurzprofil` (asked at the plan gate, default no): a Kurzprofil of at most three sentences. Optional in every format,
  required in `kombiniert` (LB-4.2).
- `foto` (optional): `ja` only if the user requests it (Germany) or the situation is Österreich (R-8.2). Never for an
  ATS or portal application, whatever the user answers earlier: tell the user why (R-8.2).
- Optional personal data (Geburtsdatum/-ort, Familienstand, Staatsangehörigkeit): only on the user's request or when
  the country requires it (LB-4.1.2, CG-10.1). Schwerbehinderung/GdB, Arbeitserlaubnis, Führerschein: only on the
  user's explicit request in the session; a posting that mentions them does not make them required, and the skill may
  ask once (LB-4.1.6, CG-10.3).

## Output

`<wurzel>/<slug>/lebenslauf.md` (or `<wurzel>/<ausprägung>/lebenslauf.md`):

```markdown
---
grundlage_hash: <current hash of the Grundlage>
format: chronologisch | einseitig | kombiniert | ats
situation: <situation chosen for the format, LB-11.12>
auspraegung: <folder name of the variant>
version: <integer, starting at 1>
version_datum: <set only when the Version is frozen, LV-3>
---

# Lebenslauf

## Persönliche Daten
Name · Anschrift · Telefon · E-Mail · LinkedIn (optional) · GitHub/Portfolio (optional)

## Kurzprofil
<optional, at most three sentences of facts; required in kombiniert>

## Berufserfahrung

### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin
- Event-Pipeline auf Basis von Python und Kafka betreut; Latenz von 800 ms auf 120 ms gesenkt
- Code-Reviews als Pflichtschritt für ein Team von 5 Entwicklern eingeführt

### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg
- [ERGÄNZEN: Aufgaben]

## Ausbildung und Studium
- 09/2015 – 08/2018: Fachinformatiker Anwendungsentwicklung, Musterfirma GmbH, Berlin

## Schulbildung
- 2015: Abitur, Beispiel-Gymnasium, Hamburg

## Sprachkenntnisse (GER-Niveau)
- Deutsch: Muttersprache
- Englisch: C1

## IT- und Fachkenntnisse
- Programmiersprachen: Python, Go

## Weiterbildung und Zertifikate
- 2022: Zertifikat Beispiel, Beispiel-Akademie, Berlin

Berlin, 23.10.2026
```

Sections follow LB-3 in this order; the optional ones `Praktika`, `Relevante Projekte`, `Ehrenamt` and `Interessen` are
added where they apply. A section without content is omitted (LB-3). The required ones (`Persönliche Daten`,
`Berufserfahrung` unless entry level, `Ausbildung und Studium`, `Schulbildung`, `Sprachkenntnisse`) are required only
where the Grundlage holds content for them; if it holds nothing, the section is omitted without a placeholder and not
reported as a Blocker. Section headings are the standard headings
(R-8.3, CG-11.2a). No tables, no columns, no text boxes, no sub-bullets (CV-17). The closing line is `Ort, TT.MM.JJJJ`
with the city of the address and the date of generation (LB-9.2, LB-9.4); an unknown city is `[ERGÄNZEN: Ort]`.

## Workflow

1. **Hash check.** Compute the hash with `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md`
   (R-9.5). If it differs from the profile's `grundlage_hash`, stop and report that the profile is stale. Offer to
   re-derive it with `job-application-profile-capture` (R-9.5).
2. **Situation.** If `situation` is missing, ask once. Propose the format from the R-8.1 table and take the user's
   decision. Record the format and the situation in the frontmatter. Ask once whether a Kurzprofil is wanted (default
   no; required in `kombiniert`). When `job-application-solution` runs this skill, both answers come from its plan gate.
   - **Europass** required by the posting: Blocker, no CV is produced; point to the EU portal (R-8.4). An academic CV:
     report the need for a dedicated structure (R-8.4).
   - **Schweiz:** the German default applies; tell the user that language and photo expectations are regional and that
     there is no Swiss variant in Phase 1 (R-8.5).
3. **Order.** Stations reverse chronological (R-2). Within a station, bullets by relevance to the posting when an
   analysis exists (R-2.1).
4. **Auswahl pro Bewerbung.** Select stations, bullets, and certificates from the Grundlage for this Stellenanzeige, as
   described in the section below (R-9.11).
5. **Entries.** Each selected station: header line `MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort` (R-2.1.1), then
   the bullets allowed by CG-6.2: up to 5 for a station with a *Muss* or *Wunsch* entry that is *erfüllt* or
   *teilweise*, up to 2 for other stations, header line only where a station does not support the application (a
   *nur Kopfzeile* decision, recorded in `pruefbericht.md`, CG-6.5, LB-5.5). More than 5 bullets only on the user's
   request in the session, recorded there too (CG-6.4). A header with years only is a Warnung (CV-02), not a
   placeholder: keep the year, write no month placeholder, and offer the user once, as an option, to add the month
   through `job-application-cv-maintain`. If the user declines, the header stays as it is (CG-9, LB-10.5).
6. **Bullets.** Write each bullet in the form of CG-8.1:
   - object and scope first, past participle of the activity verb last, optional result after a semicolon, no subject,
     no finite verb, no final period (CG-8.1.1, 8.1.3, 8.1.6);
   - one fact per bullet: one activity, at most one result; two activities are two bullets (CG-8.1.2);
   - one form per station, no mixed opening patterns (CG-8.1.4);
   - at most 180 characters and two lines; the object part before the participle at most about 100 characters, else
     split into two bullets (CG-8.1.5, CV-12);
   - "und" joins at most two items; a technology list may name three (CG-8.1.7).

   Use the verbs and avoid the forbidden phrases of CG-8.2; write measured values as digits with unit (CG-8.3). Leadership
   verbs (`geleitet`, `verantwortet`, `Teamleitung`) only when the station note has `fuehrung: ja` (CG-8.2.2, CV-16);
   when the source says the candidate took part, use a participation form such as `mitgearbeitet an` or `beteiligt an`
   (CG-8.2.5). Use a number only if the Grundlage states it. Otherwise write a qualitative result **that the Grundlage
   states**; if it states none, keep the task without a result (CG-8 Nr. 1 and Nr. 2). A routine task without a
   described scope or result is dropped, unless it is the only evidence for a *Muss* requirement; then it stays
   (CG-8 Nr. 3).
7. **Length and posting overrides.** Standard about two pages (LB-2.3), einseitig for Einsteiger, Praktikum, Schüler.
   First apply the posting's instructions recorded in `analyse.md` or given by the user (format, length, file type,
   language, section, form field): they override the defaults, and a mandatory instruction that cannot be met is
   reported as a Blocker (LB-12, CG-11.6). When space is short, cut in the order of CG-5.3: redundant bullets,
   bullets without evidence for a requirement, then whole stations with no *Muss* coverage. A *Muss*-covering station
   is never removed. The font size is never reduced (LB-11.7). The page count is checked on the exported PDF, not on
   Markdown word counts (CG-6.6); more than two pages is a Blocker. An exception needs the user's decision in the
   session; the quality gate records it in `pruefbericht.md` section `## Prüfung` and reports a Warnung instead
   (LB-2.3, LS-7.4). This skill does not write it.
8. **Gaps.** A period over two months without a station needs a neutral entry (R-2, CG-9). Gap reasons are never
   invented and are written only at the level of detail the user chose (CG-9.1, CG-9.2). Health, family and similar
   reasons are never written on their own initiative, also not when the Grundlage states them. Ask the user once per
   gap: show the stated reason, use a neutral wording chosen from `Elternzeit`, `Pflege eines Angehörigen`,
   `Weiterbildung`, `Berufliche Neuorientierung`, `Bewerbungsphase`, or decline. A reason the user chooses for the
   document is written into the Grundlage through `job-application-cv-maintain`, then the draft continues. Never write
   `Auszeit` as a default. If the user declines, the entry is `[ERGÄNZEN: Grund der Lücke]` (CG-9).
9. **Write** the file with the frontmatter and the closing line. Version handling (LV-3):
   - If `lebenslauf.md` exists, read it first and keep its `auspraegung` and `version`.
   - If a frozen Version of this number exists (`versionen/v<NNN>_*.md`), the Arbeitsstand has been frozen: raise
     `version` by one at the first change and drop `version_datum` (LV-3.3). A frozen Version is never edited
     (LV-8.3).
   - A new file starts with `version: 1`. `auspraegung` is the folder name (LV-2.1).
   - Do not set `version_datum` here: it is set when the user freezes the Version.
   - **Deriving a Lebenslauf for a Vorgang from a Version** (LV-2.2): when the user wants a changed Lebenslauf for a
     Vorgang, take a Version of an Ausprägung as the starting point, read-only. Write the result into the Vorgang
     folder as its own Arbeitsstand with `auspraegung` set to the Vorgang folder name and `version: 1`. The other
     Ausprägung stays unchanged. Check the facts against the current Grundlage (step 10); a Version holds the facts as
     they were (LV-3.5).
10. **Check.** Run `python3 <plugin-root>/scripts/cv_checks.py <wurzel>/<slug>/lebenslauf.md --grundlage <Grundlage> --analyse <wurzel>/<slug>/analyse.md`
    (add `--ats` for an ATS posting). In directory mode pass `--grundlage <Verzeichnis> --grundlage <grundlage_index>`;
    the option is repeatable. `<plugin-root>` is the plugin directory, two levels above this skill's base directory.
    Fix every Blocker that the skill can fix before handing over. A Blocker that needs the user (an open
    `[ERGÄNZEN: …]` or `[KLÄREN: …]`, such as `[ERGÄNZEN: Grund der Lücke]`) stays open: do not fill it with a guess;
    report it with the file, and the file is not ready (CG-9.3). Report the Warnungen and Hinweise too. The output is
    the reproducible basis for `job-application-quality-gate` (CG-13.3).
11. **Status.** If the folder holds `vorgang.md` (a Vorgang, LS-6.1), set `status: erstellt` and `grundlage_hash` only
    when the current status comes before `erstellt` in the LS-6 chain (`erfasst`, `analysiert`, `geplant`). Never set
    it back from `erstellt`, `geprüft`, `in Arbeit`, `versendet` or a later value (LS-6 rules 1, 2, 4, 7); say that the
    quality gate has to run again after a change. Append one line to `## Verlauf` only on an actual change:
    `- JJJJ-MM-TT: <alter Status> → erstellt, job-application-cv-create`. An Ausprägungsordner has no `vorgang.md`;
    skip this step there.
12. **Freeze on request.** Ask whether this state is the one to send. If the user confirms, copy it to
    `versionen/v<NNN>_<YYYY-MM-DD>.md` (NNN = `version`, three digits) with `version_datum` set to today (LV-3.2). A
    frozen Version is never edited; a correction is a new Version, numbered at the next change (step 9).

## Auswahl pro Bewerbung (R-9.11)

The Grundlage is complete and may hold more than one application needs. This step selects what the Lebenslauf for this
posting uses.

1. **Choose** stations, bullets, and certificates by the criteria of CG-5, in this order: coverage of *Muss*
   requirements, coverage of *Wunsch* requirements, evidence strength, scope and seniority, demonstrable results,
   redundancy, recency as tie-breaker only. Stations stay in reverse chronological order; relevance decides what is
   shown in full. Older strong evidence goes into the Kurzprofil or, only in the format `kombiniert`, a *Relevante
   Projekte* block (CG-5.2).
2. **Only existing entries.** Use only entries that exist in the Grundlage. Do not add facts. Reword only as the
   controlled rewriting of CG-7.1 allows, in the bullet form of CG-8.1; no new claims (CG-7.2).
3. **Output limits.** Bullet counts come from CG-6 (R-2.1), applied to this output. They do not come from the
   Grundlage.
4. **List sections.** One bullet per entry in the form of LB-6.1 (`<Zeitraum>: <Abschluss oder Inhalt>, <Institution>,
   <Ort>`; certificates `<Jahr>: <Zertifikat>, <Aussteller>, <Ort>`). Dated lists are in reverse chronological order
   (LB-6.3). Use the official name of the degree; state a grade only if the Grundlage states it (LB-6.4); a
   certificate the Grundlage does not hold is not written (LB-6.5). A year-only period is written `JJJJ – JJJJ` (a
   Warnung, CV-02; no placeholder, LB-6.2).
   - *Sprachkenntnisse:* `<Sprache>: <GER-Niveau>` or `Muttersprache`; no level without a source (LB-7.1, R-9.8).
   - *IT- und Fachkenntnisse:* one bullet per group, `<Gruppe>: <Eintrag>, <Eintrag>`; a level or duration only if the
     Grundlage has it; entries that the *Muss* requirements name come first, and the most relevant group first
     (LB-7.2, LB-7.3); at most ten entries per group (LB-7.6).
   - No bars, dots, stars or percentages for skills (LB-7.4). No Zeugnis wording (LB-6.6).
   - *Ehrenamt* only if it supports the application or fills a period; *Interessen* only if the user asks and the
     interests are neutral and relevant (LB-8.1, LB-8.2).
   - No Referenzen and no reference persons in the Lebenslauf (LB-8.3).
5. **Kurzprofil** (when written, LB-4.2): at most three sentences of facts from the Grundlage (field, years of
   experience, the two or three most relevant competences, for a career change the transferable evidence). Years are
   computed from the Grundlage periods, not estimated. Every statement has a Grundlage entry, listed in the
   `## Auswahl Lebenslauf` section. Nominal or participle phrases, no „Ich“, no evaluation, no personality words.
6. **Omissions and sources are visible.** Write the section `## Auswahl Lebenslauf` in `pruefbericht.md` of the
   folder: for every entry used, its Grundlage entry (file and heading, CG-2.3); for every omitted entry, a short
   reason; the Kurzprofil decision; stations with the header line only (CG-6.5); an allowed exception of more than 5
   bullets (CG-6.4); a photo decision. Create the file if it is missing. A re-run replaces only this section and leaves
   `## Auswahl Anschreiben`, `## Auswahl Motivationsschreiben` and `## Prüfung` unchanged (LS-7.4). A left-out station
   must not leave an unexplained gap. A gap over two months stays as a neutral entry (R-2). A page-limit exception does
   not belong here (step 7).
7. **Never store the selection** in the Grundlage or in the profile. The Grundlage carries no application-specific
   marks.

## Format rules by situation (R-8.1)

- **chronologisch:** default. Full station list, two pages at most.
- **einseitig:** one page. Education and internships first, then skills. Praktika with month, company, and two bullets
  (school internships are not listed).
- **kombiniert:** a Kurzprofil of at most three sentences, then the chronological station list. Used for Quereinstieg
  and many stations. Stations may be grouped in blocks such as „Praktika“, „Relevante Projekte“.
- **ats:** single column, standard headings, no photo, keywords only with evidence (R-8.3). The final file is
  Markdown; the export is a separate step (R-8.3.4): a text PDF by default, DOCX only when the portal asks for it.

## Photo

A photo is included only when R-8.2 allows it and the user wants it: on the user's request in Germany, recommended in
Austria, never for an ATS or portal application. The file is `rohdaten/foto.jpg`, linked from the Grundlage (LS-4);
the skill only reads it. Insert it as a Markdown image with the relative path to the file at the top of
`## Persönliche Daten` (CG-11.3 allows this one image). Without a request there is no photo.

## Hard rules

1. **Reverse chronological, single column, entry block per R-2.1.** No layout tables, no sub-bullets.
2. **Only Grundlage facts, through the profile.** Tailoring changes emphasis and order, never content.
3. **Gaps stay visible.** Shown at the level of detail the user chose (step 8), or as `[ERGÄNZEN: Grund der Lücke]`. No
   default wording, no inferred reason, no health or family reason on its own initiative.
4. **No invented numbers** in bullets. A number that is not in the Grundlage is not written.
5. **Optional personal data stays out** unless the user asks for it or the country requires it (LB-4.1.2, LB-4.1.6,
   CG-10); a photo follows R-8.2.
6. **Europass and academic CV are not produced.** The skill reports that they are not supported (R-8.4) and stops; a
   posting that requires Europass is a Blocker with the hint to the EU portal.
7. **Signature line:** `Ort, TT.MM.JJJJ`. A handwritten signature only for a paper copy (R-2, LB-9).
8. **Controlled rewriting only** (CG-7). Shorten, reorder and reword verified content. Never add a number, team size,
   title, technology, or level, and never turn participation into ownership, assistance into leadership, exposure into
   expertise, or familiarity into proficiency (CG-7.2).
9. **Conflicts stop the draft.** A date or title that differs between the profile and the Grundlage, or a *Muss*
   requirement without evidence, is reported to the user and not resolved by choosing a value (CG-2.2, CG-4.5).
10. **Only the Wurzel is written** (LS-5.7): the Vorgang folder or Ausprägungsordner with `lebenslauf.md` and
    `versionen/`, `pruefbericht.md` and `vorgang.md` of this Vorgang. Nothing outside the Wurzel, never the plugin
    repository, never `rohdaten/`. The one exception of CG-2.2: a conflict is resolved by writing the user's decision
    into the Grundlage, and that is done through `job-application-cv-maintain`, not by this skill.
