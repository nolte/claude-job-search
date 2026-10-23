# CV generation: target fit, evidence and validation (EN canonical)

Normative rules for generating the German Lebenslauf for one Stellenanzeige. This document
defines the *content* decisions. The form rules of `spec/job-application/konventionen/en.md`
(R-2 layout, R-2.1 entry block, R-8 format by situation) stay in force; R-2.1 refers to this
document for the bullet counts and the length (CG-6).
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
| 1 | Datengrundlage (Grundlage; `grundlage` in `konfiguration.md`, file or directory) and `rohdaten/` | Authoritative factual basis, with source references. |
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
     `fuehrung: ja` in the note (CV-16; Warnung while `fuehrung` is `ungeklärt` or missing, Blocker
     with `fuehrung: nein`). A year-only period is accepted in the note; the CV then shows the
     year-only header line unchanged and CV-02 reports a Warnung. No `[ERGÄNZEN: Monat]` placeholder
     is written, and the note does not have to be completed (CG-9). Title and employer in the CV
     equal the note's `titel` and `arbeitgeber` (CV-15).
   - Zeugnisse are not part of a station note. The Grundlage holds each Zeugnis as one entry in its
     section *Zeugnisse* (R-9.3); the station note refers to that entry and does not copy the wording.

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

The selection also follows these rules:

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

This section sets the defaults and hard limits for bullet counts and length. R-2.1 refers here for the
counts; it holds no numbers of its own.

1. **Default length.** Two pages for experienced candidates (*chronologisch*, *kombiniert*),
   one page for entry level, students and interns (*einseitig*). Austria: two pages (R-8.1).
2. **Bullets per station, default.**
   - stations with at least one Muss or Wunsch entry of status `erfüllt` or `teilweise`: up to 5;
   - other stations: up to 2;
   - a station that does not support the application: header line only (no bullets).
3. **Hard limit.** No station exceeds 5 bullets (CV-03). A bullet has at most two lines and at most
   180 characters (CG-8.1.5; CV-12 reports a longer bullet as Hinweis).
4. **Exception.** More than 5 bullets for one station are allowed only when the user asks for it
   in the session; the pruefbericht then records the exception.
5. **Empty stations.** A station with no bullets and no explicit *nur Kopfzeile* decision is a
   Hinweis (CV-03), because the entry may be an accidental gap in the selection.
6. **Length check.** The page count is checked on the exported PDF (`export_document.py`, FA-O13); a
   breach is exit code 4 (R-10.10, CG-12.4). The limit is two pages, and one page for the format
   `einseitig`. Markdown word counts are not a page measure.

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
- *automated* (CV-11): the generic and evaluative phrases of CG-8.2.3 (`verantwortlich für`,
  `zuständig für`, `involved in`, `worked on`, `erfolgreich`, `innovativ`, `dynamisch`, `diverse`,
  `vielfältig`, `Expertise in`, `sicher in`) are flagged as Warnung, because they hide the actual
  task or claim a quality without proof;
- *automated* (CV-16): leadership wording (`geleitet`, `Teamleitung`, `führte`, `Personalverantwortung`
  and similar) is a Warnung while the station note has `fuehrung: ungeklärt` or no `fuehrung`, and a
  Blocker when the note records `fuehrung: nein`. With `fuehrung: ja` there is no finding (CG-7.2,
  leadership);
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

## CG-8.1 Form of a bullet

1. **Structure.** A bullet has this form: `<Objekt mit Umfang> <Tätigkeitsverb im Partizip II>`,
   optionally followed by `; <Ergebnis>`. The object and its scope come first. The past participle
   of the activity verb closes the first clause. A result, if any, follows after a semicolon.
2. **One fact per bullet.** A bullet names one activity and at most one result. Two activities are
   two bullets.
3. **No subject and no finite verb.** A bullet never starts with a subject ("Ich", "Wir", "Er") and
   never uses a conjugated verb ("betreue", "habe betreut").
4. **One form per station.** All bullets of one station use the form of item 1. A station never mixes
   the form with another opening pattern.
5. **Length.** At most two lines and at most 180 characters (CV-12). The object part before the participle is at
   most about 100 characters long, so that the reader reaches the verb within the first line; a longer
   object part is split into two bullets.
6. **No final period.** A bullet is a phrase, not a sentence.
7. **At most two items in a list.** "und" joins at most two items. A longer list is shortened to the
   two most relevant items. An enumeration of technologies may name three (`Python, Kafka und
   PostgreSQL`). The full list stays in the Grundlage (CG-5).

## CG-8.2 Wording

1. **Verbs.** Use the past participle of a concrete activity verb: `aufgebaut`, `betrieben`,
   `eingeführt`, `entwickelt`, `automatisiert`, `migriert`, `integriert`, `konzipiert`, `gesenkt`,
   `gesteigert`, `betreut`, `begleitet`, `umgesetzt`. The verb says what the candidate did (CG-8.4).
2. **Leadership verbs** (`geleitet`, `verantwortet`, `Teamleitung`) need `fuehrung: ja` in the station
   note (CV-16).
3. **Forbidden phrases.** `verantwortlich für`, `zuständig für`, `involved in`, `worked on`,
   `erfolgreich`, `innovativ`, `dynamisch`, `diverse`, `vielfältig`, `Expertise in`, `sicher in` are not
   used. CV-11 enforces the whole set and reports a Warnung (CG-7.3). `Expertise in` and `sicher in`
   require a source that states proficiency (CG-7.2); with such a source the finding is dismissed in
   review and recorded in `pruefbericht.md`.
4. **Names.** Tool and product names are written as in the Grundlage ("Kubernetes", "Argo CD",
   "GitLab CI"). Abbreviations the Grundlage does not use are not introduced.
5. **Participation.** When the source says the candidate took part, the bullet uses a participation
   form such as `mitgearbeitet an` or `beteiligt an`, never a lead verb (CG-7.2).

## CG-8.3 Numbers and typography

1. **Digits for measured values.** Values are written as digits with their unit: "800 ms", "5
   Entwickler", "3 Partnersysteme". This makes them checkable against the Grundlage (CV-05).
2. **No number words in bullets.** "fünf Entwickler" is not used. The value is written as "5 Entwickler".
3. **German typography.** A space before the percent sign ("40 %") and in large numbers ("120 000 €").
   A range uses an en dash ("3–5 Tage").

## CG-8.4 Examples

| | Bullet | Reason |
|---|---|---|
| Good | Event-Pipeline auf Basis von Python und Kafka betreut; Latenz von 800 ms auf 120 ms gesenkt | Object first, participle closes the first clause, result after the semicolon with digits (CG-8.1.1) |
| Good | Latenz der Event-Pipeline in Python und Kafka von 800 ms auf 120 ms gesenkt | Object first, participle last, measured values as digits |
| Good | Code-Reviews als Pflichtschritt für ein Team von 5 Entwicklern eingeführt | Form and digits; the result is qualitative and sourced |
| Bad | Event-Pipeline für die Verarbeitung von Bestell-, Zahlungs- und Versandereignissen aus 12 Partnersystemen in drei Regionen auf Basis von Python und Kafka betreut | Object part longer than about 100 characters; the reader reaches the verb late. Split into two bullets (CG-8.1.5) |
| Good | Schnittstellen für 3 Partnersysteme umgesetzt | Scope as digits; no result claimed |
| Bad | Ich habe die Event-Pipeline optimiert | Subject, finite verb, unspecific claim (CG-8.1.3, CG-8.2.1) |
| Bad | Verantwortlich für die Plattform | Forbidden phrase, no activity, no scope (CG-8.2.3) |
| Bad | Erfolgreich fünf Teams unterstützt | Unsourced adjective, number as a word (CG-8.2.3, CG-8.3.2) |

## CG-9 Missing facts, gaps, conflicts

| Case | Handling | Severity |
|---|---|---|
| Unknown fact needed for a statement | `[ERGÄNZEN: …]` in the document | Blocker until resolved |
| Uncertain job title | `[KLÄREN: …]` | Blocker until resolved |
| Conflicting dates for one station (profile vs. Grundlage) | Do not generate; ask the user | Blocker (CV-06) |
| Employment gap over two months, with a user-stated reason | Neutral entry with the stated reason | — |
| Employment gap over two months, no reason known | `[ERGÄNZEN: Grund der Lücke]` | Blocker until resolved |
| Gap over two months, reason not needed in the document | Neutral entry whose wording the user chooses from `Elternzeit`, `Pflege eines Angehörigen`, `Weiterbildung`, `Berufliche Neuorientierung`, `Bewerbungsphase` (R-2); `Auszeit` is not a default | Hinweis |
| Unsupported achievement or metric in a draft | Remove from the draft | Blocker if it reaches the document (CV-05) |
| Period end before start | Fix in the Grundlage through `cv-maintain` | Blocker |
| Period given as year only (R-2.1 format `MM/JJJJ`) | Keep the year-only header line unchanged; no placeholder, no completion required | Warnung (CV-02) |

1. **Gap reasons are never invented.** The reason comes from the user or from a source passage.
2. **Privacy in gaps.** A gap reason is written only at the level the user chose. Health, family
   and similar reasons are not written into the Lebenslauf unless the user asks for it (E-5).
3. **Placeholders are final-blockers.** Any `[ERGÄNZEN` or `[KLÄREN` in a document marked ready
   is a Blocker (CV-01).

## CG-10 Personal details

1. Name and contact are required. Birth date, marital status, nationality and photo are optional
   and included only when the user asks for them or the country requires it (R-2, R-8.2).
2. Optional personal data is a Hinweis when present without a request (quality-gate).
3. Schwerbehinderung or a GdB, Arbeitserlaubnis and Führerschein are written only on the user's explicit
   request in the session (R-2, LB-4.1.6). A link to LinkedIn, GitHub or a portfolio is optional in the
   contact line and taken from the profile only (LB-4.1.3).

## CG-11 Structure, ATS and output formats

1. **Claim scope.** The plugin follows ATS-friendly practices. It does not guarantee that any
   specific parser reads the document correctly.
2. **Structure.** Single column, standard headings, reverse chronological order (R-2, R-8.3).
   Standard headings are the ones listed in CG-11.2a.
   - CG-11.2a Standard headings: `Persönliche Daten`, `Kurzprofil`, `Berufserfahrung`,
     `Relevante Projekte`, `Praktika`, `Ausbildung und Studium`, `Schulbildung`,
     `Sprachkenntnisse`, `IT- und Fachkenntnisse`, `Weiterbildung und Zertifikate`,
     `Ehrenamt`, `Interessen`. A heading may add a qualifier in parentheses, for example
     `Sprachkenntnisse (GER-Niveau)`. For the `ats` format the short forms `Ausbildung` (for
     `Ausbildung und Studium`) and `Kenntnisse` (for `IT- und Fachkenntnisse`) are allowed as well
     (R-8.3.2 refers here).
3. **Forbidden elements** in the Markdown source: tables, text boxes, columns, images other than
   the optional photo (`rohdaten/foto.jpg`, LB-4.1.2), graphical skill ratings, icons that replace text, critical content in
   headers or footers (CV-08, CV-10).
4. **Plain-text readability.** The document remains understandable when converted to plain
   text. The export check (CG-12) tests this.
5. **File format.** A PDF made from text is the default, also for ATS-marked postings. DOCX is used
   only when the portal requires it; the DOCX export then strips the document metadata (author,
   revisions, comments). A scanned PDF is not acceptable (R-8.3.4, FA-O16). A format stated in the
   posting overrides this. No format is assumed to be universally better.
6. **Employer instructions.** A format, length, file type or content requirement in the posting
   overrides the defaults of this document. The posting-analysis records the instruction; the
   quality gate checks it.

## CG-12 Output consistency

1. **Canonical content.** `lebenslauf.md` is the single source. DOCX, PDF, HTML and Markdown exports
   are generated from it by `skills/job-application-export/scripts/export_document.py`. Outputs
   are never edited by hand (R-10.1).
2. **Content check.** The word multiset of the source equals the word multiset of the export
   (FA-O6). A difference does not delete the output: file and manifest stay, the export exits with
   code 2 (R-10.10) and the set is not ready to send. The quality gate reports the difference as a
   Blocker. Equally a Blocker: an export whose manifest source hash (`quelle.sha256`) no longer matches
   the current Markdown (stale export, LV-6.4). The check is run by the export and by the tests.
3. **Structure check.** Export tests verify that all section headings appear in the DOCX text in
   the source order.
4. **PDF check.** The PDF must contain extractable text and stay within the page limit of the
   document type (FA-O11, FA-O13). A breach of the page limit is exit code 4; file and manifest stay.
   The export only reports. The quality gate sets the severity: Blocker for `cv` and `letter`,
   Warnung for `motivation`. The limit for `cv` with the format `einseitig` is one page. A PDF without
   extractable text is a Blocker. Where LuaLaTeX is not installed, this check is *not run* and the
   report says so.
5. **Further export findings.** A missing manifest for a file in `export/` is a Warnung. An export
   file changed after its manifest was written is a Warnung (LV-6.4).

## CG-13 Quality gate: severities and criteria

### CG-13.1 Severities

| Severity | Criterion | Effect on verdict |
|---|---|---|
| Blocker | The document would be materially wrong, misleading, incomplete, or breaks a mandatory requirement: a fact not in the source, a placeholder, a Muss requirement presented as met, a conflicting date, a missing required document or format. | `BLOCKED` |
| Warnung | A meaningful improvement is recommended, and the document is still usable: format deviation from a default, weak evidence for a Wunsch requirement, long bullet, generic phrase in an allowed case. | `READY-WITH-WARNINGS` |
| Hinweis | A non-critical observation: possible redundancy, optional personal data, a note the user may ignore. | No effect |

The verdict labels are `BLOCKED`, `READY-WITH-WARNINGS` and `READY`. A skill may write the German
equivalents `BLOCKIERT`, `BEREIT MIT WARNUNGEN` and `BEREIT` in its German report; they mean the same.
The reviewer agent (`job-application-reviewer`) uses the same severities and the same verdict labels.
`READY` requires zero Blocker and zero Warnungen.

A missing Wunsch qualification is never a Blocker (CG-4.2). The gate reports it in the analysis
and lets the user decide.

### CG-13.2 Criteria

| # | Dimension | Check | Kind | Rule |
|---|---|---|---|---|
| 1 | Factual integrity | Numbers traceable to the Grundlage | automated | CV-05 |
| 2 | Source traceability | Entry references in `pruefbericht.md` | review | CG-2.3 |
| 3 | Target-role relevance | Selection follows CG-5 | review | CG-5 |
| 4 | Muss coverage | Muss rows not marked `erfüllt` without evidence | automated | CV-07 |
| 5 | Wunsch coverage | Wunsch gaps reported | review | CG-4.2, report |
| 6 | Evidence strength | Stärke of rows used in the CV | review | CG-4 |
| 7 | Seniority and role positioning | Titles as in the Grundlage; leadership only with `fuehrung: ja` (Warnung with `ungeklärt` or missing, Blocker with `nein`) | automated and review | CV-15, CV-16; CG-7.2 |
| 8 | Relevance of entries | Stations and projects per CG-5 | review | CG-5 |
| 9 | Skills ordering | Skills appear with posting relevance and evidence | review | CG-5 |
| 10 | Conciseness and redundancy | Duplicate bullets; sub-bullets below a bullet (Hinweis) | automated | CV-09, CV-17 |
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

### CG-13.4 Scope of single rules

1. **CV-02 does not stop the other checks.** A station whose header line does not match LB-5.1 (for
   example a year-only period) is still checked for CV-05, CV-09, CV-11, CV-12 and CV-16. CV-02
   reports the header; the bullets are checked as in any other station.
2. **CV-13 is position-based.** A gap entry counts only when it stands between the two stations whose
   periods leave the gap. A neutral entry elsewhere in the document does not close the gap.
3. **CV-16 severity** follows the station note: Warnung while `fuehrung` is `ungeklärt` or missing,
   Blocker with `fuehrung: nein`, no finding with `fuehrung: ja` (CG-7.3).
4. **CV-11 severity** is Warnung for every phrase of CG-8.2.3 (CG-7.3).
5. **CV-17** reports sub-bullets as Hinweis (R-2.1: a station block has bullets, no sub-bullets).

### CG-13.5 Severities of the further gate checks

These checks are made by the quality gate, not by `cv_checks.py`. The severities are fixed here so that
the gate and the reviewer report the same level.

| Check | Severity |
|---|---|
| Keyword stuffing: a posting term in a document without evidence in the Grundlage (R-1.4, CG-4.6) | Blocker |
| Keyword stuffing: padding with posting terms that the Grundlage does support | Warnung |
| A Lebenslauf above its page limit (LB-2.3) | Blocker; Warnung with the user's recorded decision, for every later run |
| An Anschreiben above one page (AS-7.1) | Blocker; no exception |
| A Motivationsschreiben above the limit of its variant (MS-7) | Warnung; no exception rule |
| Word count outside the aid range (AS-7.2, MS-7.2) | Hinweis only, never a Blocker; also when no PDF exists |
| An Anlagen line or an attachment list names a file that does not exist (AS-10.4) | Blocker |
| Export findings of CG-12 | as listed in CG-12.2, CG-12.4 and CG-12.5 |
| A `## Auswahl …` section missing in `pruefbericht.md` for a generated document (CG-2.3, R-9.11.5) | Warnung |
| `grundlage_hash` of a document or an export stale (R-9.5) | Warnung |

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
| I | ATS-specific posting | Standard headings, no tables, text PDF (DOCX only when the portal requires it) | `tests/test_cv_checks.py` (CV-08, CV-10); `tests/test_export.py` |
| J | Output consistency | Same content in every format | `tests/test_export.py` (DOCX, HTML, Markdown) |
| K | Unresolved placeholders | Blocker | `tests/test_cv_checks.py` (CV-01) |
| L | Employment gap | Dates accurate; no invented reason | `tests/test_cv_checks.py` (gap placeholder rule, no invented text) |
| M | Year-only period in a station note | Year-only header line unchanged, CV-02 Warnung, no placeholder; the bullets are still checked | `tests/test_cv_checks.py` (CV-02, CG-13.4.1) |

Scenarios A, C, D and E depend on the selection step and are verified by review of a generated
example, not by a script.

## CG-15 Open points

| Area | Point | Status |
|---|---|---|
| CV-11 severity | `cv_checks.py` reports Warnung for the whole phrase set (CG-7.3) | done (script, 0.2.0) |
| CV-16 severity | `cv_checks.py` distinguishes Warnung (`ungeklärt`, missing) and Blocker (`nein`) (CG-13.4.3); lead verbs count only with a people object | done (script, 0.2.0) |
| CV-13 position | The gap entry must stand between the two affected stations (CG-13.4.2); the script checks the position | done (script, 0.2.0) |
| CV-02 scope | Stations with a non-conformant header line are still checked for CV-05, CV-09, CV-11, CV-12, CV-15, CV-16 (CG-13.4.1) | done (script, 0.2.0) |
| Year-only periods | No `[ERGÄNZEN: Monat]` placeholder, no completion of the station note required (CG-2.4, CG-9) | done (decision) |
| Gap wording | Neutral wording chosen by the user from the list in CG-9; `Auszeit` is not a default | done (decision) |
| DOCX metadata | The DOCX export clears the author fields (`dc:creator`, `cp:lastModifiedBy`) in `export_document.py` (CG-11.5); a fresh pandoc DOCX carries no revisions or comments | done (export, 0.2.0) |
| CV-17 | `cv_checks.py` reports sub-bullets as Hinweis; CV-01 to CV-18 are the whole automated set (R-7, CG-13.4.5) | done (script) |
| Page limit | Exit code 4 of `export_document.py` (R-10.10); the gate sets the severity (CG-12.4, CG-13.5) | done (export) |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |
