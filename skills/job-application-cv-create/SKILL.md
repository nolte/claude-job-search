---
name: job-application-cv-create
description: "Produces a German Lebenslauf from job-application/profil.md in the format chosen for the situation (chronologisch, einseitig, kombiniert, ATS-optimiert), with each Station as a single header line plus bullets within the limits of spec CG-6, selects stations and bullets by relevance and evidence (CG-5), and marks gaps as [ERGÄNZEN]. Checks the Datengrundlage hash. Writes Markdown only. Use on \"erstelle meinen Lebenslauf\", \"Lebenslauf für diese Stelle anpassen\", \"Lebenslauf im ATS-Format\", or equivalent German requests. Don't use for the cover letter (job-application-cover-letter-create), for the Datengrundlage or profile (job-application-profile-capture), or for Europass or the academic CV (out of scope in Phase 1, spec R-8.4)."
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
    alternative: job-application-solution
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
CG-7 (controlled rewriting), CG-9 (gaps and conflicts), CG-11 (ATS). This skill only reshapes facts that
already exist in the Grundlage, through the profile.

## Inputs

- `job-application/profil.md` (required). Its `grundlage_hash` is checked (step 1).
- The Datengrundlage path from `job-application/konfiguration.md` (key `grundlage`, file or directory with `grundlage_index`), default `job-application/grundlage/lebenslauf-chronologisch.md` (spec R-9.1, R-9.10). Required for the hash check and as the only source of the selection (R-9.11). In directory mode the selection reads all notes of the set.
- `job-application/<slug>/analyse.md` (optional). Its rows (CG-4) decide which requirements the CV addresses and which entries get more room. A *Muss* row that is not *erfüllt* is never claimed in the CV.
- `situation` (asked if not given): Standard, Berufseinstieg, Schüler/Studierende/Praktikum, Quereinstieg, Lücke, Viele Stationen, ATS/Portal, Österreich, Schweiz. Europass and academic CV are not produced here (R-8.4).
- `foto` (optional): `ja` only if the user requests it or the situation is Österreich (R-8.2).

## Output

`job-application/<slug>/lebenslauf.md`:

```markdown
---
grundlage_hash: <current hash of the Grundlage>
format: chronologisch | einseitig | kombiniert | ats
---

# Lebenslauf

## Persönliche Daten
Name · Anschrift · Telefon · E-Mail · LinkedIn (optional)

## Berufserfahrung

### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin
- Betreuung der Event-Pipeline in Python und Kafka; Latenz von 800 ms auf 120 ms gesenkt.
- Einführung von Code-Reviews als Pflichtschritt im Team mit fünf Entwicklern.

### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg
- [ERGÄNZEN: Aufgaben]

## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse (GER-Niveau)
## IT- und Fachkenntnisse
## Weiterbildung und Zertifikate

Ort, Datum
```

Section headings are the standard headings (R-8.3). No tables, no columns, no text boxes.

## Workflow

1. **Hash check.** Compute the hash with `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md` (spec R-9.5). If it differs from the profile's
   `grundlage_hash`, stop and report that the profile is stale. Offer to re-derive it with
   `job-application-profile-capture` (R-9.5).
2. **Situation.** If `situation` is missing, ask once. Propose the format from the R-8.1 table and
   take the user's decision. Record the chosen format in the frontmatter.
3. **Order.** Stations reverse chronological (R-2). Within a station, bullets by relevance to
   the posting when an analysis exists (R-2.1).
4. **Auswahl pro Bewerbung.** Select stations, bullets, and certificates from the Datengrundlage for this Stellenanzeige, as described in the section below (R-9.11).
5. **Entries.** Each selected station: header line `Zeitraum | Position | Arbeitgeber, Ort` (R-2.1.1),
   then the bullets allowed by CG-6.2: up to 5 for a station with a *Muss* or *Wunsch* entry that is
   *erfüllt* or *teilweise*, up to 2 for other stations, header line only where a station does not support the application.
6. **Bullets.** Write each bullet in the form of CG-8.1 (object and scope first, past participle of the
   activity verb last, optional result after a semicolon, no subject, no final period). Use the verbs and
   avoid the phrases of CG-8.2, and write measured values as digits with their unit (CG-8.3). Use a number
   only if the profile states it. Otherwise use a qualitative result. Routine tasks without result are dropped.
7. **Length.** Standard about two pages. Einseitig for Einsteiger, Praktikum, Schüler. Trim older
   or less relevant entries before recent ones.
8. **Write** the file with the frontmatter.
9. **Check.** Run `python3 <plugin-root>/scripts/cv_checks.py job-application/<slug>/lebenslauf.md --grundlage <Grundlage> --analyse job-application/<slug>/analyse.md`
   (add `--ats` for an ATS posting). `<plugin-root>` is the plugin directory, two levels above this skill's base
   directory. Fix every Blocker before handing over; report the Warnungen and Hinweise with the file. The output is the
   reproducible basis for `job-application-quality-gate` (CG-13.3).

## Auswahl pro Bewerbung (R-9.11)

The Datengrundlage is complete and may hold more than one application needs. This step selects
what the Lebenslauf for this posting uses.

1. **Choose** stations, bullets, and certificates by the criteria of CG-5, in this order: coverage of *Muss*
   requirements, coverage of *Wunsch* requirements, evidence strength, scope and seniority, demonstrable results,
   redundancy, recency as tie-breaker only. Stations stay in reverse chronological order; relevance decides what
   is shown in full. Older strong evidence goes into the Kurzprofil or a *Relevante Projekte* block (CG-5.2).
2. **Only existing entries.** Use only entries that exist in the Datengrundlage. Do not add facts.
   Reword only as far as R-2.1 allows: shortening and reordering, no new claims.
3. **Output limits.** Bullet counts and page limits come from R-2 and R-2.1, applied to this output.
   They do not come from the Datengrundlage.
4. **Omissions and sources are visible.** Write the omitted entries with a short reason to `pruefbericht.md` in the
   application folder, as the section `## Auswahl Lebenslauf`. For every entry used, name its Grundlage entry (file and
   heading, CG-2.3). Create the file if it is missing. A
   left-out station must not leave an unexplained gap. A gap over two months stays as a neutral entry (R-2).
5. **Never store the selection** in the Datengrundlage or in the profile. The Grundlage carries no
   application-specific marks.

## Format rules by situation (R-8.1)

- **chronologisch:** default. Full station list, two pages at most.
- **einseitig:** one page. Education and internships first, then skills. Praktika with month,
  company, and at least two bullets (school internships are not listed).
- **kombiniert:** a Kurzprofil of 2–4 sentences, then the chronological station list. Used for
  Quereinstieg and many stations. Stations may be grouped in blocks such as „Praktika“, „Projekte“.
- **ats:** single column, standard headings, no photo, keywords only with evidence (R-8.3).
  The final file is Markdown; the DOCX export is a separate step (R-8.3.4).

## Hard rules

1. **Reverse chronological, single column, entry block per R-2.1.** No layout tables.
2. **Only profile facts.** Tailoring changes emphasis and order, never content.
3. **Gaps stay visible.** Shown as the user described them, or as `[ERGÄNZEN: Grund der Lücke]`.
4. **No invented numbers** in bullets. A number that is not in the profile is not written.
5. **Optional personal data stays out** unless the profile includes it and the situation allows it (R-8.2).
6. **Europass and academic CV are not produced.** The skill reports that and points to `job-application-solution` (R-8.4).
7. **Signature line:** Ort, Datum. A handwritten signature only for a paper copy (R-2).
8. **Controlled rewriting only** (CG-7). Shorten, reorder and reword verified content. Never add a number, team
   size, title, technology, or level, and never turn participation into ownership, assistance into leadership,
   exposure into expertise, or familiarity into proficiency (CG-7.2).
9. **Conflicts stop the draft.** A date or title that differs between the profile and the Grundlage, or a *Muss*
   requirement without evidence, is reported to the user and not resolved by choosing a value (CG-2.2, CG-4.5).
