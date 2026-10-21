# CV generation: target fit, evidence and validation (EN canonical)

Normative rules for generating the German Lebenslauf for one Stellenanzeige. This document
defines the *content* decisions. The form rules of `spec/job-application/konventionen/en.md`
(R-2 layout, R-2.1 entry block, R-8 format by situation) stay in force; where this document
sets a default for bullet counts or length, it replaces the fixed numbers in R-2.1 (see CG-6).
The data locations are defined in `spec/job-application/lokale-struktur/en.md`.

Rule IDs `CV-xx` are the IDs reported by `scripts/cv_checks.py`. A rule marked *automated* is
decided by that script; a rule marked *review* needs the generating skill or a reader.

## CG-1 Scope

1. The rules apply to every Lebenslauf the plugin generates: `job-application-cv-create`
   produces it, `job-application-quality-gate` checks it, `job-application-posting-analysis`
   prepares the input.
2. The rules do not decide whether to apply. The user decides, and the posting's explicit
   instructions take precedence over every default here (CG-11.6).

## CG-2 Source of truth

Authority runs from the top down. A level may only use facts from the levels above it.

| Level | Artefact | Role |
|---|---|---|
| 1 | Grundlage (`grundlage` in `konfiguration.md`, file or directory) and `rohdaten/` | Authoritative factual basis, with source references. |
| 2 | `profil.md` | Derived from level 1. Condensed, with a source reference per entry. Carries `grundlage_hash`. |
| 3 | `analyse.md` | Job-specific analysis. Contains no new candidate facts. |
| 4 | `lebenslauf.md` | Generated content. Only facts from levels 1 and 2. |
| 5 | `pruefbericht.md` | Report. Quotes sources, never changes them. |

1. **Profile never overrides the Grundlage.** The profile is re-derived when it is stale
   (hash mismatch, R-9.5). It is never edited to match a document.
2. **Conflict procedure.** A conflict exists when a profile entry and its Grundlage entry differ in
   employer, position, period, or a number, or when two Grundlage entries describe the same
   station with different data. A conflict is never resolved silently by picking one value:
   - a conflict that reaches a generated document is a Blocker (CV-06) until the user decides
     which value is correct, and the user's decision is written into the Grundlage through
     `job-application-cv-maintain`;
   - a title the sources do not agree on is written as `[KLÄREN: Titel laut Zeugnis]` (R-2.1).
3. **Traceability.** Every entry in `lebenslauf.md` must name its Grundlage entry in
   `pruefbericht.md` section `## Auswahl Lebenslauf`. The reference never appears in the CV text.
4. **Station notes (CG-2.4).** The Grundlage holds the career detail as one note per station. The
   note is the record from which the CV selects. Its form:
   - frontmatter `typ: station`, `titel` (position exactly as in the Zeugnis), `arbeitgeber`
     (legal name), `ort`, `zeitraum_von` and `zeitraum_bis` (`JJJJ`, `JJJJ-MM` or `MM/JJJJ`;
     `zeitraum_bis` may be `heute`), `fuehrung` (`ja`, `nein` or `ungeklärt`; `ungeklärt` when
     unknown), and optionally `team_groesse` (a number taken from the source);
   - body sections `## Stichpunkte` (tasks with their scope; the name used in the vault), `## Erfolge` (results, each with its
     source or the user's confirmation) and `## Team` (team structure: size, roles around the
     candidate, reporting line, and whether the candidate led people).
   - Rules: a number in a CV bullet must appear in the note (CV-05). Leadership wording needs
     `fuehrung: ja` in the note (CV-16). A year-only period is accepted in the note, but the CV
     needs `MM/JJJJ`, so the note is completed (CV-02). Title and employer in the CV equal the
     note's `titel` and `arbeitgeber` (CV-15).

## CG-3 Target-specific presentation

Three dimensions are kept separate. They are combined at selection time instead of selecting a
fixed template for each combination.

| Dimension | Values | Effect |
|---|---|---|
| A. Target position | role, seniority, Muss and Wunsch requirements, leadership expectation, domain | Which evidence is relevant (CG-4, CG-5). |
| B. Candidate situation | experienced specialist, leadership candidate, entry level, student or intern, career change, long or varied career, employment gap, project-based experience | Format and emphasis (R-8.1, CG-5.4). |
| C. Application context | country (R-8.2, R-8.5), language, portal or ATS, requested documents and formats, employer instructions | Format, length, and what the document must contain (CG-11). |

1. **Same person, different role.** An experienced specialist applying for a leadership role
   emphasises supported leadership evidence (team scope, decisions, stakeholders) when the
   Grundlage has it. Without such evidence the CV does not claim it; the gap goes to the
   analysis and the cover letter (CG-4.5).
2. **Career change.** Transferable competencies are shown in the Kurzprofil or in a
   project block, with their real source. The employment history is not rearranged to
   disguise the change.
3. **Entry level.** Education, projects, internships and verified skills come first; the
   format is *einseitig* (R-8.1).
4. **Long career.** Older entries shrink to header lines or one bullet unless they carry
   the strongest evidence for a Muss requirement (CG-5).

## CG-4 Requirement-to-evidence mapping

`job-application-posting-analysis` writes one row per significant requirement. The columns are
fixed:

| Column | Content |
|---|---|
| Anforderung | Posting wording, quoted exactly (R-1, posting-analysis rule 2). |
| Priorität | `Muss`, `Wunsch`, or `Kontext` (business context, tone, working model). |
| Kompetenz | Normalised competency, for example `Kubernetes-Betrieb`. Used for matching only. |
| Nachweis | Grundlage entry reference (file and heading) and a quoted phrase. `—` when none. |
| Stärke | `stark`: a described task with its scope in the Grundlage, and a result. `mittel`: a described task without result. `schwach`: mention only (skill list, one project line). `—`: none. |
| Status | `erfüllt`, `teilweise`, `nicht belegt`, or `unklar` (CG-4.3). |
| Verwendung | `Lebenslauf`, `Anschreiben`, `Vorbereitung`, or `Rückfrage`. |

1. **`erfüllt`** requires evidence of strength `mittel` or `stark`.
2. **`teilweise`** means related evidence only, or evidence that covers part of the requirement.
3. **`nicht belegt`** means no evidence was found in the Grundlage. It is not a statement that
   the candidate lacks the competency. It is never written as `fehlt`.
4. **`unklar`** means the posting or the evidence is ambiguous. The row goes to `Rückfrage`.
5. **Muss without evidence.** A `Muss` row with status `nicht belegt` or `teilweise` is reported
   as a gap and assigned `Verwendung` `Anschreiben` or `Rückfrage`. It is never marked `erfüllt`
   (CV-07).
6. **Keywords.** A posting term is used in the CV only where the requirement has status
   `erfüllt` or `teilweise` with matching evidence (R-1.4). Terms are not added to improve ATS
   matching.

## CG-5 Relevance-based selection

Selection decides which stations, bullets and projects appear, and in which order inside a
station. It applies these criteria in this order:

1. coverage of Muss requirements by the entry;
2. coverage of Wunsch requirements;
3. evidence strength (CG-4);
4. scope and seniority of the responsibility described;
5. demonstrable results;
6. redundancy: an entry already covered by a stronger entry is dropped or shortened;
7. recency, as a tie-breaker only.

1. **Recency is not the primary criterion.** The most recent role is not automatically the most
   relevant one.
2. **Stations keep reverse chronological order** (R-2). Relevance decides what is shown in full,
   and older strong evidence is surfaced in one of two ways: in the Kurzprofil, or in a
   *Relevante Projekte* block in the *kombiniert* format (R-8.1). Both point to the Grundlage
   entry they come from. Reordering stations by relevance is not allowed.
3. **Page space.** When space is short, cut in this order: redundant bullets, bullets without
   evidence for a requirement, then whole stations with no Muss coverage. A Muss-covering
   station is never removed.
4. **Format choice** follows the situation (R-8.1), not the selection. The selection then fills
   the chosen format.

## CG-6 Length and bullets: defaults, limits, exceptions

This section replaces the fixed bullet counts in R-2.1 with defaults and hard limits.

1. **Default length.** Two pages for experienced candidates (*chronologisch*, *kombiniert*),
   one page for entry level, students and interns (*einseitig*). Austria: two pages (R-8.1).
2. **Bullets per station, default.**
   - stations with at least one Muss or Wunsch entry of status `erfüllt` or `teilweise`: up to 5;
   - other stations: up to 2;
   - a station that does not support the application: header line only (no bullets).
3. **Hard limit.** No station exceeds 5 bullets (CV-03). A bullet fits in two lines (CV-12 as
   Hinweis).
4. **Exception.** More than 5 bullets for one station are allowed only when the user asks for it
   in the session; the pruefbericht then records the exception.
5. **Empty stations.** A station with no bullets and no explicit *nur Kopfzeile* decision is a
   Hinweis (CV-03), because the entry may be an accidental gap in the selection.
6. **Length check.** The page count is checked on the exported PDF (`export_document.py`, FA-O13).
   Markdown word counts are not a page measure.

## CG-7 Controlled rewriting

The skill may reformulate verified content. It may not add facts.

### CG-7.1 Allowed transformations

- shortening and removing filler words;
- reordering bullets and stations, within CG-5;
- merging two bullets that state the same facts;
- grammatical rewording that keeps every number, name, technology, role and period;
- replacing a generic phrase with the more specific phrase from the same Grundlage entry;
- moving a verified detail from a bullet into a header line, or the reverse, if nothing is lost.

### CG-7.2 Forbidden transformations

- any new number, team size, budget, percentage, duration or count (CV-05);
- any new technology, tool, certificate, language level or qualification;
- any title, employer or period change (CV-06);
- *participation to ownership*: "mitgearbeitet" must not become "verantwortlich";
- *assistance to leadership*: "unterstützt" must not become "geleitet" or "Teamleitung";
- *exposure to expertise*: "Einblick in X" must not become "Expertise in X";
- *familiarity to proficiency*: "Grundkenntnisse" must not become "sicher in X" or a level;
- adding a posting term the Grundlage does not support (CG-4.6).

### CG-7.3 Validation

- *automated* (CV-05): every number in a bullet appears in the Grundlage text;
- *automated* (CV-11): generic phrases (`verantwortlich für`, `zuständig für`, `involved in`,
  `worked on`) are flagged as Hinweis, because they hide the actual task;
- *automated* (CV-16): leadership wording (`geleitet`, `Teamleitung`, `führte`, `Personalverantwortung`
  and similar) is a Blocker unless the station note records `fuehrung: ja` (CG-7.2, leadership);
- *review*: the remaining semantic checks of CG-7.2 (ownership, expertise, proficiency) are made by
  the generating skill and the reviewer agent. They are not decided by the script.

## CG-8 Achievements and results

1. **Results only from the Grundlage.** A result (time, cost, quantity, quality, scope) appears
   only when the Grundlage states it or the user confirms it.
2. **No result, still a bullet.** A bullet without a result describes the scope and the
   technical work: Verb + Objekt + Umfang or Kontext. It is not dropped only because it has no
   metric.
3. **No routine duties** without a described scope or result, unless they are the only evidence
   for a Muss requirement.
4. **Achievement wording.** Use the verb the source supports. When the source says the candidate
   took part, the CV says so.

## CG-9 Missing facts, gaps, conflicts

| Case | Handling | Severity |
|---|---|---|
| Unknown fact needed for a statement | `[ERGÄNZEN: …]` in the document | Blocker until resolved |
| Uncertain job title | `[KLÄREN: …]` | Blocker until resolved |
| Conflicting dates for one station (profile vs. Grundlage) | Do not generate; ask the user | Blocker (CV-06) |
| Employment gap over two months, with a user-stated reason | Neutral entry with the stated reason | — |
| Employment gap over two months, no reason known | `[ERGÄNZEN: Grund der Lücke]` | Blocker until resolved |
| Gap over two months, reason not needed in the document | Neutral entry *Auszeit* or the period without text | Hinweis |
| Unsupported achievement or metric in a draft | Remove from the draft | Blocker if it reaches the document (CV-05) |
| Period end before start | Fix in the Grundlage through `cv-maintain` | Blocker |
| Period given as year only (R-2.1 format `MM/JJJJ`) | Keep the year and mark `[ERGÄNZEN: Monat]` | Warnung |

1. **Gap reasons are never invented.** The reason comes from the user or from a source passage.
2. **Privacy in gaps.** A gap reason is written only at the level the user chose. Health, family
   and similar reasons are not written into the Lebenslauf unless the user asks for it (E-5).
3. **Placeholders are final-blockers.** Any `[ERGÄNZEN` or `[KLÄREN` in a document marked ready
   is a Blocker (CV-01).

## CG-10 Personal details

1. Name and contact are required. Birth date, marital status, nationality and photo are optional
   and included only when the user asks for them or the country requires it (R-2, R-8.2).
2. Optional personal data is a Hinweis when present without a request (quality-gate).

## CG-11 Structure, ATS and output formats

1. **Claim scope.** The plugin follows ATS-friendly practices. It does not guarantee that any
   specific parser reads the document correctly.
2. **Structure.** Single column, standard headings, reverse chronological order (R-2, R-8.3).
   Standard headings are the ones listed in CG-11.2a.
   - CG-11.2a Standard headings: `Persönliche Daten`, `Kurzprofil`, `Berufserfahrung`,
     `Relevante Projekte`, `Praktika`, `Ausbildung und Studium`, `Schulbildung`,
     `Sprachkenntnisse`, `IT- und Fachkenntnisse`, `Weiterbildung und Zertifikate`,
     `Ehrenamt`, `Interessen`. A heading may add a qualifier in parentheses, for example
     `Sprachkenntnisse (GER-Niveau)`.
3. **Forbidden elements** in the Markdown source: tables, text boxes, columns, images other than
   the optional photo, graphical skill ratings, icons that replace text, critical content in
   headers or footers (CV-08, CV-10).
4. **Plain-text readability.** The document remains understandable when converted to plain
   text. The export check (CG-12) tests this.
5. **File format.** DOCX is preferred for ATS-marked postings; a PDF made from text is the second
   choice; a scanned PDF is not acceptable (R-8.3.4, FA-O16). A format stated in the posting
   overrides this. No format is assumed to be universally better.
6. **Employer instructions.** A format, length, file type or content requirement in the posting
   overrides the defaults of this document. The posting-analysis records the instruction; the
   quality gate checks it.

## CG-12 Output consistency

1. **Canonical content.** `lebenslauf.md` is the single source. DOCX, PDF, HTML and Markdown exports
   are generated from it by `skills/job-application-export/scripts/export_document.py`. Outputs
   are never edited by hand (R-10.1).
2. **Content check.** The word multiset of the source equals the word multiset of the export
   (FA-O6). A difference blocks the export. The check is run by the export and by the tests.
3. **Structure check.** Export tests verify that all section headings appear in the DOCX text in
   the source order.
4. **PDF check.** The PDF must contain extractable text and stay within the page limit of the
   document type (FA-O11, FA-O13). Where LuaLaTeX is not installed, this check is *not run* and
   the report says so.

## CG-13 Quality gate: severities and criteria

### CG-13.1 Severities

| Severity | Criterion | Effect on verdict |
|---|---|---|
| Blocker | The document would be materially wrong, misleading, incomplete, or breaks a mandatory requirement: a fact not in the source, a placeholder, a Muss requirement presented as met, a conflicting date, a missing required document or format. | `BLOCKED` |
| Warnung | A meaningful improvement is recommended, and the document is still usable: format deviation from a default, weak evidence for a Wunsch requirement, long bullet, generic phrase in an allowed case. | `READY-WITH-WARNINGS` |
| Hinweis | A non-critical observation: possible redundancy, optional personal data, a note the user may ignore. | No effect |

A missing Wunsch qualification is never a Blocker (CG-4.2). The gate reports it in the analysis
and lets the user decide.

### CG-13.2 Criteria

| # | Dimension | Check | Kind | Rule |
|---|---|---|---|---|
| 1 | Factual integrity | Numbers traceable to the Grundlage | automated | CV-05 |
| 2 | Source traceability | Entry references in `pruefbericht.md` | review | CG-2.3 |
| 3 | Target-role relevance | Selection follows CG-5 | review | CG-5 |
| 4 | Muss coverage | Muss rows not marked `erfüllt` without evidence | automated | CV-07 |
| 5 | Wunsch coverage | Wunsch gaps reported | automated | CV-07 (analysis), report |
| 6 | Evidence strength | Stärke of rows used in the CV | automated | CG-4 |
| 7 | Seniority and role positioning | Titles as in the Grundlage; leadership only with `fuehrung: ja` | automated and review | CV-15, CV-16; CG-7.2 |
| 8 | Relevance of entries | Stations and projects per CG-5 | review | CG-5 |
| 9 | Skills ordering | Skills appear with posting relevance and evidence | review | CG-5 |
| 10 | Conciseness and redundancy | Duplicate bullets | automated | CV-09 |
| 11 | Chronology and dates | Order, format, conflicts | automated | CV-04, CV-06 |
| 12 | Placeholders | Open markers | automated | CV-01 |
| 13 | Unsupported achievements | Numbers, forbidden transformations | automated and review | CV-05, CG-7.2 |
| 14 | ATS and layout | Tables, headings, forbidden elements | automated | CV-08, CV-10 |
| 15 | Export consistency | Word multiset, headings order | automated | CG-12 |
| 16 | Requested formats | Requested format present | review | CG-11.5 |
| 17 | Language and country | German spelling, country conventions | review | R-8, R-3 |
| 18 | Employer instructions | Recorded instruction met | review | CG-11.6 |

### CG-13.3 Reproducibility

1. Every automated finding has a rule ID, the file, the line, and the quoted passage.
2. `scripts/cv_checks.py` produces the same output for the same input. It reads only the files it
   is given and writes JSON to stdout.
3. A review finding names the rule and the passage. Two reviewers should reach the same verdict
   from the same passage.

## CG-14 Acceptance scenarios

Each scenario states the expected behaviour. The column *Verification* tells how it is checked.

| ID | Scenario | Expected behaviour | Verification |
|---|---|---|---|
| A | Experienced specialist | Relevant technical evidence first; unsupported technology absent | review; CV-05 keeps technology claims tied to the Grundlage |
| B | Leadership role without evidence | No team size, direct reports or management title | CV-05 for numbers; CV-16 for leadership wording; CV-15 for titles; `tests/test_cv_checks.py` |
| C | Career change | Transferable evidence highlighted; history not altered | review; CG-2 and CV-06 |
| D | Entry-level | *einseitig*, education and projects first | review; CG-6.1 default length |
| E | Older strong evidence | Older stations' bullets selected by relevance; order stays reverse chronological | `tests/test_cv_checks.py` (order check); selection review |
| F | Missing metrics | Bullets without numbers kept; no numbers added | `tests/test_cv_checks.py` (CV-05) |
| G | Conflicting dates | Blocker on each conflict | `tests/test_cv_checks.py` (CV-06) |
| H | Unsupported Muss requirement | Not `erfüllt` | `tests/test_cv_checks.py` (CV-07) |
| I | ATS-specific posting | Standard headings, no tables, DOCX or text PDF | `tests/test_cv_checks.py` (CV-08, CV-10); `tests/test_export.py` |
| J | Output consistency | Same content in every format | `tests/test_export.py` (DOCX, HTML, Markdown) |
| K | Unresolved placeholders | Blocker | `tests/test_cv_checks.py` (CV-01) |
| L | Employment gap | Dates accurate; no invented reason | `tests/test_cv_checks.py` (gap placeholder rule, no invented text) |

Scenarios A, C, D and E depend on the selection step and are verified by review of a generated
example, not by a script.
