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
     `fuehrung: ja` in the note (CV-16; Blocker while `fuehrung` is `nein`, `ungeklärt` or missing). A year-only period is accepted in the note; the CV then shows the
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
| Stärke | How much the entry describes, independent of the requirement: `stark`: a described task with its scope in the Grundlage, and a result. `mittel`: a described task without result. `schwach`: mention only (skill list, one project line). `—`: none. It does not say that the entry shows what *this* requirement demands (CG-4.7). |
| Status | `erfüllt`, `teilweise`, `nicht belegt`, or `unklar` (CG-4.3). |
| Verwendung | `Lebenslauf`, `Anschreiben`, `Vorbereitung`, or `Rückfrage`. |
| Offen | What the requirement demands that the Nachweis does not show, in a few words (CG-4.7), or the missing information for `unklar`. `—` when nothing is open. |

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

7. **Fit of the evidence (audit finding F-03).** A technology or topic that the Nachweis shares with the requirement fixes
   `Kompetenz` only. Before a status is set, the requirement is read for the aspects it demands and each one is compared with
   the quoted phrase of the Grundlage:
   - *Art*: use, development, implementation, architecture, operation and maintenance, coordination, ownership;
   - *Umfang*: single component or application against platform, project against organisation-wide, one-off against continuous;
   - *Verantwortung*: participation, independent execution, technical coordination, responsibility for a topic or operation,
     personnel management (`fuehrung`, CV-16);
   - *Ergebnis*: effect or figure demanded, activity only recorded (CV-05).

   An aspect counts as shown only if the quoted phrase or its station record says it; it is not inferred from the title, the
   employer or what is usual for the technology. Another wording of the same activity shows the aspect (`Laufender
   Clusterbetrieb` for `Betrieb einer Container-Orchestrierung`); a missing keyword is no reason to reject. Every aspect that is
   demanded and not shown goes into `Offen`. `Stärke` and `Offen` are independent: a `mittel` entry can still leave the
   demanded aspect open.
8. **Status follows `Offen`.** `erfüllt` only with `Offen` `—`. If an aspect is open, the status is `teilweise`: related or
   indirect evidence belongs here, and `Offen` says what the requirement still demands. `teilweise` and `unklar` need an entry in
   `Offen` (what is missing or which information would decide). `nicht belegt` has none. A model does not fill `Offen` with
   assumptions about the candidate; it names only what the requirement demands and the phrase lacks. `cv_checks.py` rule CV-24
   checks that status and `Offen` do not contradict each other; it cannot judge whether the aspects were identified correctly
   (review, CG-13).
9. **Use of a `teilweise` row.** The row stays usable: the Lebenslauf states what the Nachweis shows, in its scope and with its
   activity verb (CG-7.4, CG-8.1), and never the word of the requirement for the aspect named in `Offen` (no `Betrieb` for a use,
   no `verantwortet` for a participation, no `Plattform` for a component, no result without one in the Grundlage). A `Muss` row
   that is `teilweise` or `unklar` is a gap for the Anschreiben or a `Rückfrage` (CG-4.5). An old `analyse.md` without the
   column `Offen` is read as unchecked: CV-24 asks to write the analysis again, the status is not changed by the script.

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
  and similar) is a Blocker unless the station note records `fuehrung: ja` (`nein`, `ungeklärt` and a missing entry
  all block, CG-13.4.3). With `fuehrung: ja` there is no finding (CG-7.2, leadership);
- *automated* (CV-22, CV-23): wording of ownership, scope or expertise that the station record does not use, and a team
  result without a team reference (CG-7.4, CG-13.4.10, CG-13.4.11). Both are a Warnung: the script asks for the
  evidence, it does not decide that a claim is false;
- *review*: the remaining semantic checks of CG-7.2 and CG-7.4 are made by the generating skill and the reviewer agent.
  They are not decided by the script.

### CG-7.4 Semantic fidelity

A rewording keeps the factual meaning. Six dimensions describe what a statement claims; a statement may move up in none of
them unless the station record of the Grundlage says so. The levels are ordered, the examples are illustrative.

| Dimension | Levels, weak to strong | Moving up needs |
|---|---|---|
| Activity | took part, implemented, operated, coordinated, designed, reviewed, led | the verb, or a stronger one, in the record |
| Responsibility | contribution, shared responsibility, operational responsibility, technical ownership, project responsibility, organizational responsibility | a record that names the level (`gemeinsam`, `eigenverantwortlich`, `Projektleitung`) |
| Leadership | technical coordination, technical leadership, project leadership, personnel management, organizational leadership | personnel management and above: `fuehrung: ja` (CV-16); the lower levels: the record |
| Expertise | exposure, practical use, repeated use, specialization, documented expert responsibility | a record that states the level; the presence of a technology in a skill list states none |
| Scope | task, component, service, project, platform, organization | the record names the object; `die gesamte …`, `unternehmensweit` need it too |
| Outcome | activity, deliverable, contribution, team outcome, individual outcome, quantified result | a result of the team stays a team result; a number needs its source (CV-05) |

Allowed: shorter, clearer, more professional wording, a better sentence structure, selecting and ordering by the posting
(CG-5), and replacing a vague phrase by the exact one of the same entry (CG-7.1). `Mitarbeit am Betrieb einer
Kubernetes-Plattform` may become `an dem Betrieb von Kubernetes-Plattformen mitgewirkt`; `Koordination technischer
Aufgaben im Team` may become `technische Arbeit im Team koordiniert`.

Not allowed without a record: `die gesamte Plattform eigenverantwortlich betrieben` for the first, `das Engineering-Team
gemanagt` for the second, `Terraform-Experte` for `Terraform in einem Projekt eingesetzt`, `die gesamte Enterprise-Architektur
verantwortet` for a contribution to one service, and a team's `Latenz um 40 % gesenkt` as the candidate's own.

An ambiguous record (it names the activity but not the level) gives a Warnung and a question to the user; the skill does
not choose the stronger reading. A statement that matches the record in meaning is no finding, even when no word is the same.
Only the user changes the Grundlage; the skills, the script and the reviewer never write into it.

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
2. **Leadership verbs** (`geleitet`, `gemanagt`, `angeleitet`, `Teamleitung`) need `fuehrung: ja` in the station
   note (CV-16). `verantwortet` and other wording of ownership are checked against the station record (CV-22, CG-7.4).
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
   With equal multisets the export also compares the order of the headings of level 1 and 2 (EXP-002, row 15 of CG-13.2):
   a heading that the export does not carry after the previous one prints `Reihenfolge: Abweichung bei den Überschriften`
   and a Warnung on stderr, and leaves the exit code unchanged. The words inside a section are not compared, because the
   templates move header fields (the name stands before "Persönliche Daten") and lay out the station lines as a grid.
   The comparison is a heuristic: it looks for the words of each heading after the previous one, so a one-word heading whose
   word also stands in the running text before it can pass although the sections are swapped; only `#` headings are read
   (no underlined headings), and a `#` inside a code block counts as a heading.
3. **Structure check.** Export tests verify that all section headings appear in the DOCX text in
   the source order.
4. **PDF check.** The PDF must contain extractable text and stay within the page limit of the
   document type (FA-O11, FA-O13). A breach of the page limit is exit code 4; file and manifest stay.
   The export only reports. The quality gate sets the severity: Blocker for `cv` and `letter`,
   Warnung for `motivation`. The limit for `cv` with the format `einseitig` is one page. A PDF without
   extractable text is a Blocker. Where LuaLaTeX is not installed, this check is *not run* and the
   report says so.
5. **Open placeholders.** The export does not block on an open `[ERGÄNZEN …]` or `[KLÄREN …]` (R-6: the export is
   made on the user's request, and a preview with the gaps visible is useful; R-7: the quality gate is what blocks).
   The whole file is searched, frontmatter included, with the marker of CV-01. It keeps them visible in the output, reports
   `Platzhalter: n offen` on stdout and a Warnung on stderr, and leaves the exit code unchanged. The set is not ready
   to send; the quality gate reports the placeholder as a Blocker (CV-01, BR-01).
6. **Further export findings.** A missing manifest for a file in `export/` is a Warnung. An export
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
| 1 | Factual integrity | Numbers traceable to the Grundlage, with their unit or noun; entries of the list sections (skills, languages, certificates, education) present in the Grundlage; stations confirmed; wording of ownership, scope and expertise and team results backed by the record (CG-7.4) | automated and review | CV-05, CV-19, CV-20, CV-22, CV-23 |
| 2 | Source traceability | Entry references in `pruefbericht.md` | review | CG-2.3 |
| 3 | Target-role relevance | Selection follows CG-5 | review | CG-5 |
| 4 | Muss coverage | Muss rows not marked `erfüllt` without evidence, and not `erfüllt` while `Offen` names an aspect the Nachweis does not show (CG-4.7, CG-4.8); whether the aspects were identified correctly is review | automated and review | CV-07, CV-24 |
| 5 | Wunsch coverage | Wunsch gaps reported | review | CG-4.2, report |
| 6 | Evidence strength | Stärke of rows used in the CV; fit of the Nachweis to the demanded Art, Umfang, Verantwortung and Ergebnis (CG-4.7) | review | CG-4 |
| 7 | Seniority and role positioning | Titles as in the Grundlage; leadership only with `fuehrung: ja` (Blocker with `nein`, `ungeklärt` or missing) | automated and review | CV-15, CV-16; CG-7.2 |
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
3. **CV-16 severity.** Personnel-leadership wording is a Blocker unless the Grundlage records `fuehrung: ja`
   for the station (CG-7.3). `nein`, `ungeklärt` and a missing entry all block: leadership that is not
   evidenced is not written. The way to unlock a true claim is to record it: the station note key
   `fuehrung: ja`, or the line `Führung: ja` in the block of a header-form station (R-9.3). The key stands at the start of the line or after `;`, `,` or `|`, so `Fachliche Führung: ja` is no answer, and the
   value is read without regard to case. The unfilled template form `Führung: ja | nein | ungeklärt` is no answer.
4. **CV-11 severity** is Warnung for every phrase of CG-8.2.3 (CG-7.3).
5. **CV-17** reports sub-bullets as Hinweis (R-2.1: a station block has bullets, no sub-bullets).
6. **CV-19 scope.** The list sections `IT- und Fachkenntnisse`, `Kenntnisse`, `Sprachkenntnisse`,
   `Weiterbildung und Zertifikate`, `Ausbildung und Studium`, `Ausbildung` and `Schulbildung` are checked entry by
   entry. An entry is `<Label>: <item>, <item>`; each item must stand in the Grundlage as whole words
   (case, punctuation and parentheses ignored). The label is checked only in `Sprachkenntnisse` (the language);
   a period or a skill group label is not. A language and its level must stand together on one line of the Grundlage (`Englisch (C2)` is blocked when
   only `Englisch B2` stands there). A number in a parenthesis must stand in the Grundlage, not as part of a word
   (`B2` does not carry a `2`). A leading period (`2014`, `09/2010 – 06/2014`) is dropped, `|` separates the parts of
   an entry, `und` and `&` join two items, `ä ö ü ß` equal `ae oe ue ss`, Markdown emphasis is ignored. The match
   covers the whole Grundlage: a skill named in a negation (`kein Kubernetes`) or a one-letter name (`R`, `Go`) can be
   backed by an unrelated passage; that stays with the review. An entry with a
   placeholder is left to CV-01. The match is exact and makes no claim about meaning: a paraphrase
   (`Container-Orchestrierung` for `Kubernetes`) is a Blocker here and is cleared by using the Grundlage's word,
   and an entry that the Grundlage states in other words stays a judgement of the review. Free text (Kurzprofil,
   Relevante Projekte, Ehrenamt, Interessen) is not covered and stays with the review.
7. **CV-05 unit.** When a number of a bullet stands in the station record, the word after it (a unit or a noun) must
   stand after the same number there, compared by its first four letters (`Entwickler`, `Entwicklern`). A different
   unit is a Warnung. `%` equals `Prozent`. Not compared: a year, a number with no word after it, a standard number (`ISO 27001`) and a
   number that the record gives with no word after it. A year used as a quantity (`2000 Nutzer`) is not caught.
8. **CV-20.** A station used in the Lebenslauf that the Grundlage records with `Bestätigt: nein` (header-form line
   `- Bestätigt: nein`, or the station note key `bestaetigt: nein`) is a Blocker: a station counts only once the user has confirmed it (R-9.5 point 5). A missing flag is no finding, so
   older Grundlagen keep working.
9. **CV-21.** A Lebenslauf with nothing but frontmatter and headings is a Blocker: every other rule passes on an empty document, so an empty file would read as clean.
10. **CV-22.** Wording of ownership or independence (`eigenverantwortlich`, `Gesamtverantwortung`, `verantwortet`,
    `eigenständig`), of scope (`gesamte`, `komplette`, `unternehmensweit`, `Enterprise-…`) or of expertise (`Experte`,
    `Spezialist`, `Spezialisierung`, `sehr gute Kenntnisse`, `Expertise`) is a Warnung when its first seven letters do not
    stand in the record of the station. The finding names the dimension, quotes the line of the record that is closest to the
    bullet, and asks the user. Not read: the meaning (a paraphrase with other words passes, a claim without a marker also
    passes), a station without a record, and the sentences of a letter.
11. **CV-23.** A number that the record of the station gives only in lines that speak of a team (`Team`, `gemeinsam`, `wir`,
    `Kollegen`) is a Warnung when the bullet has no team reference. A head count (`4 Entwickler`) is a fact about the team,
    not a result, and is left to CV-05. A result without a number (`Umsatz gesteigert`) is not read: it stays with the review.
12. **CV-24.** In `analyse.md` the status must not contradict the column `Offen` (CG-4.7, CG-4.8): `erfüllt` with an entry in
    `Offen` is a Blocker for a `Muss` row and a Warnung for a `Wunsch` row; `teilweise` or `unklar` with an empty `Offen` is a
    Warnung; a table without the column is one Warnung per table. The script reads no meaning: an open aspect that nobody
    recorded is not seen (`tests/test_evidence_fit.py`, known limit), and no keyword list rejects a differently worded Nachweis.

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
| Export findings of CG-12 | as listed in CG-12.2, CG-12.4, CG-12.5 and CG-12.6 |
| A `## Auswahl …` section missing in `pruefbericht.md` for a generated document (CG-2.3, R-9.11.5) | Warnung |
| `grundlage_hash` of a document or an export stale (R-9.5) | Warnung |

### CG-13.6 Automated checks of the letters

`scripts/cv_checks.py --doc-type letter|motivation|email` runs a smaller set on `anschreiben.md`,
`motivationsschreiben.md` (and their `-portal.txt` copies) and `email.md`. It reuses the number and leadership
functions of the Lebenslauf checks. The text checked runs from the Anrede (`Sehr geehrte`, `Guten Tag|Morgen|Abend`, `Hallo`, `Hi`, `Moin`, `Liebe`, …) to the
Grußformel (`Mit freundlichen Grüßen`, `Viele Grüße`, `Hochachtungsvoll`, …) or, failing that, to the `Anlagen:` line.
Absender, Empfängeranschrift, date, Betreff and Anlagen are outside it. A document without an Anrede is checked whole.

| Rule | Check | Severity |
|---|---|---|
| BR-01 | Placeholder `[ERGÄNZEN` or `[KLÄREN` left (all three document types) | Blocker |
| BR-02 | Number in the text. Not in the Grundlage, the analysis or the posting | Blocker |
| BR-02 | Number only in the analysis or the posting: a requirement or a company fact proves nothing about the candidate | Warnung |
| BR-02 | Amount with a currency in a sentence about Gehalt, Vergütung or brutto (Gehaltsvorstellung, a value of the user, AS-10.1). Any other amount is a number like the rest | Hinweis |
| BR-03 | `N Jahre Erfahrung` that no Grundlage entry states (`N Jahre`) and that the union of the station periods does not reach. A running station counts up to the date of the letter (the first date before the Anrede, numeric or with a spelled-out month). Without such a date running stations cannot be counted and the finding is a Warnung, not a Blocker. Gap entries, education, retraining and internships (`Studium`, `Ausbildung`, `Umschulung`, `Praktikum`, …) and stations with `Bestätigt: nein` do not count. Phrasings: `N Jahre Berufserfahrung`, `Erfahrung von N Jahren`, `Erfahrung seit N Jahren`, `seit N Jahren` | Blocker |
| BR-04 | Personnel-leadership wording while no station of the Grundlage records `fuehrung: ja`. With one such station it is a Hinweis: the mapping to the station stays in the review (MS-6.2). A sentence that states a wish (`möchte`, `suche`, `künftig`) or speaks of the employer (`Ihre …`) is a Hinweis: a target role is no claim | Blocker, Hinweis |
| BR-05 | Anschreiben, Motivationsschreiben or E-Mail with nothing but frontmatter and headings (no text to check) | Blocker |

1. **A posting number is never proof.** The numbers of `analyse.md` and `stellenanzeige.md` lower BR-02 from
   Blocker to Warnung, never to nothing, and never cover BR-03: a letter that repeats the `5 Jahre` of the posting
   as the candidate's own experience is blocked when the periods do not reach it (R-1, CG-4.5).
2. **Scope.** The rules read numbers, placeholders and leadership words only. Whether a claim is true of the right
   station, a technology, a certificate, and company facts stay in the review (AS-6.5, MS-6.1). With no
   Grundlage given, only BR-01 runs and the report says so.
3. **What is not a number for BR-02:** dates (`24.10.2026`, `1. März`), ordinals (`7. Platz`, `3. Quartal`), `24/7`, and digits inside a name (`S3`, `OAuth2`, `3D`). `10x`, `70k` and `5 Mio` are figures. A number is not proved by the start of another one (`70` against `70.000`); `70.000`, `70000` and `70 000` equal each other. A year is a number like any other: found only in the posting it is a Warnung.
   An unreadable input file ends with exit code 2, never 1: 1 means that a Blocker exists.
4. **Known limit.** BR-02 grounds a number against the whole Grundlage, not against one station (that is CV-05 in the Lebenslauf). A number that stands anywhere in the Grundlage passes; whether it belongs to the right employer stays in the review.

### CG-13.7 Currency of the report

`## Prüfung` in `pruefbericht.md` is a record of one run. The documents can change afterwards, and a report that no
longer matches them must not be read as their state (audit finding REV-001).

1. **The gate settles it.** `job-application-quality-gate` compares the `grundlage_hash` and the export manifests with
   the current files (R-9.5, CG-12.2). A report is current only after a run of the gate on the present documents.
2. **The gate leaves the data.** The head of `## Prüfung` has a second line, `Grundlage: <grundlage_hash des Laufs> ·
   Geprüft: <documents>`. A report without it is of an older format and gives no sign.
3. **The reviewer looks for signs.** The reviewer agent has no shell and cannot prove currency. It reports one of `fehlt`,
   `veraltet`, `möglicherweise veraltet` and `ohne Anzeichen für Veraltung` in its section *Prüfbericht*.
   `veraltet`: a document or `vorgang.md` with a `grundlage_hash` other than the recorded one; quoted Blocker passages that
   are all gone while the result is `BLOCKIERT`; an open placeholder read by the reviewer under a `BEREIT` result.
   `möglicherweise veraltet`: a document dated strictly after `Stand` (a planned sending date looks the same).
4. **No inheritance.** The verdict of the reviewer comes from its own reading. A gate result does not lift a Blocker
   that the reviewer finds, and does not replace a check the reviewer cannot make (it goes under *Nicht beurteilbar*).
   The deterministic results of an outdated or missing report are quoted as "Stand des Gates, nicht bestätigt".
5. **Severity.** `fehlt` and `veraltet` are a Warnung with the advice to run the gate again, and a Warnung acts on the
   verdict like any other. `möglicherweise veraltet` is a Hinweis.

## CG-14 Acceptance scenarios

Each scenario states the expected behaviour. The column *Verification* tells how it is checked.

| ID | Scenario | Expected behaviour | Verification |
|---|---|---|---|
| A | Experienced specialist | Relevant technical evidence first; unsupported technology absent | review; CV-19 blocks a skill or certificate that the Grundlage does not hold; CV-05 keeps numbers tied to it |
| B | Leadership role without evidence | No team size, direct reports or management title | CV-05 for numbers; CV-16 for leadership wording (Blocker without `fuehrung: ja`); CV-15 for titles; `tests/test_cv_checks.py` |
| C | Career change | Transferable evidence highlighted; history not altered | review; CG-2 and CV-06 |
| D | Entry-level | *einseitig*, education and projects first | review; CG-6.1 default length |
| E | Older strong evidence | Older stations' bullets selected by relevance; order stays reverse chronological | `tests/test_cv_checks.py` (order check); selection review |
| F | Missing metrics | Bullets without numbers kept; no numbers added | `tests/test_cv_checks.py` (CV-05) |
| G | Conflicting dates | Blocker on each conflict | `tests/test_cv_checks.py` (CV-06) |
| H | Unsupported Muss requirement | Not `erfüllt` | `tests/test_cv_checks.py` (CV-07) |
| N | Evidence that names the technology but not the demanded Art, Umfang, Verantwortung or Ergebnis | `teilweise` with `Offen`; usable in the Lebenslauf in its real scope | `tests/test_evidence_fit.py` (CV-24; groups A to J); the model's assessment: reviewer and eval case `behavior-evidence-fit` |
| I | ATS-specific posting | Standard headings, no tables, text PDF (DOCX only when the portal requires it) | `tests/test_cv_checks.py` (CV-08, CV-10); `tests/test_export.py` |
| J | Output consistency | Same content in every format | `tests/test_export.py` (DOCX, HTML, Markdown) |
| K | Unresolved placeholders | Blocker | `tests/test_cv_checks.py` (CV-01) |
| L | Employment gap | Dates accurate; no invented reason | `tests/test_cv_checks.py` (gap placeholder rule, no invented text) |
| M | Year-only period in a station note | Year-only header line unchanged, CV-02 Warnung, no placeholder; the bullets are still checked | `tests/test_cv_checks.py` (CV-02, CG-13.4.1) |

Scenarios A, C, D and E depend on the selection step and are verified by review of a generated
example, not by a script. `tests/test_scenarios.py` runs the deterministic part of every scenario on fictional
fixtures (`tests/fixtures/szenarien/README.md`).

## CG-15 Open points

| Area | Point | Status |
|---|---|---|
| CV-11 severity | `cv_checks.py` reports Warnung for the whole phrase set (CG-7.3) | done (script, 0.2.0) |
| CV-16 severity | `cv_checks.py` reports a Blocker for `nein`, `ungeklärt` and missing (CG-13.4.3, audit finding FF-004); lead verbs count only with a people object | done (script) |
| CV-13 position | The gap entry must stand between the two affected stations (CG-13.4.2); the script checks the position | done (script, 0.2.0) |
| CV-02 scope | Stations with a non-conformant header line are still checked for CV-05, CV-09, CV-11, CV-12, CV-15, CV-16 (CG-13.4.1) | done (script, 0.2.0) |
| Year-only periods | No `[ERGÄNZEN: Monat]` placeholder, no completion of the station note required (CG-2.4, CG-9) | done (decision) |
| Gap wording | Neutral wording chosen by the user from the list in CG-9; `Auszeit` is not a default | done (decision) |
| DOCX metadata | The DOCX export clears the author fields (`dc:creator`, `cp:lastModifiedBy`) in `export_document.py` (CG-11.5); a fresh pandoc DOCX carries no revisions or comments | done (export, 0.2.0) |
| CV-17 | `cv_checks.py` reports sub-bullets as Hinweis; CV-01 to CV-24 are the whole automated set (R-7, CG-13.4.5) | done (script) |
| BR-01 to BR-05 | `cv_checks.py --doc-type letter, motivation or email` checks placeholders, numbers, experience spans and leadership wording of the letters (CG-13.6, audit finding FF-002) | done (script) |
| CV-24 | Fit of a Nachweis to its requirement: column `Offen`, status follows it; identification of the open aspects is model judgement and review (audit finding F-03) | done (script for consistency), review for meaning |
| CV-22, CV-23 | Wording of ownership, scope and expertise and team results are checked against the station record; the rest of CG-7.4 is review (audit finding F-01) | done (script) |
| CV-19, CV-20, CV-05 unit | List-entry grounding, unconfirmed stations and unit comparison (CG-13.4.6 to 13.4.8, audit findings FF-001, FF-003) | done (script) |
| Page limit | Exit code 4 of `export_document.py` (R-10.10); the gate sets the severity (CG-12.4, CG-13.5) | done (export) |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |
