# Document type: Lebenslauf (EN canonical)

Normative rules for the Lebenslauf (CV) as a document: its purpose, its sections and their content, its
formats, its entry shapes, its layout, and how it is checked. This document is canonical for the document
type. It does not repeat rules that other specs own. It refers to them and says where they apply.

Where the rules live:

| Topic | Owner |
|---|---|
| What the document is, its sections, entry shapes, layout, metadata | this document |
| Selection by relevance, evidence mapping, bullet limits, bullet form and wording, gaps, severities | `spec/job-application/cv-generierung/en.md` (CG-2 to CG-14) |
| Format by situation, photo, ATS, Europass, Schweiz | `spec/job-application/konventionen/en.md` (R-8) |
| Fact integrity, Grundlage, hash | `spec/job-application/konventionen/en.md` (R-1, R-9) |
| Output formats and export | `spec/job-application/konventionen/en.md` (R-10) |
| Station notes in the Grundlage | `cv-generierung/en.md` CG-2.4 |

Rule IDs `LB-n` name the rules of this document. Each rule says whether it comes from a cited source or is a
decision of this plugin. A posting's instruction overrides a default of this plugin (LB-12).

## LB-1 Purpose and reader

1. **Purpose.** The Lebenslauf lists the facts of the candidate's career and education in a form that the
   reader can scan. It is the fact base that the Anschreiben refers to (`anschreiben/en.md` AS-1.3).
2. **Reader.** A person who scans the document, and often a parser (ATS). Both need a plain structure and
   predictable headings (R-8.3).
3. **Form.** The German Lebenslauf is tabular and in reverse chronological order: the most recent entry
   comes first. Sources: [Randstad](https://www.randstad.de/karriere/bewerbungsratgeber/lebenslauf/),
   [Uni Münster, Broschüre Lebenslauf](https://www.wiwi.uni-muenster.de/fakultaet/sites/fakultaet/files/broschuere_lebenslauf_final_neu.pdf).
4. **Facts only.** The document states facts. It contains no description of the candidate's personality (a
   source on the German form says so: [Lingoda](https://www.lingoda.com/blog/de/lebenslauf-auf-deutsch/)).
   Personal statements belong into the Motivationsschreiben (`motivationsschreiben/en.md`).
5. **One document per application.** The Lebenslauf is generated for one Stellenanzeige from the
   Datengrundlage (Grundlage, R-9; CG-5). The Grundlage is complete; the document is a selection.

## LB-2 Formats

The format follows the situation (R-8.1). This document adds what each format contains.

| Format | Situation | Sections | Length |
|---|---|---|---|
| `chronologisch` | Standard, experience in Germany | LB-3 in full order | 2 pages at most |
| `einseitig` | Entry level, student, internship | Education and internships first, then skills | 1 page (a second page breaches the limit, item 3) |
| `kombiniert` | Career change, many stations | Kurzprofil, then LB-3; stations may be grouped | 2 pages at most |
| `ats` | ATS hint or online portal | Same as `chronologisch`, with the rules of R-8.3 | as the posting asks |

1. **Length.** Sources give about one page for students and graduates, and two pages for working people
   ([Uni Münster](https://www.wiwi.uni-muenster.de/fakultaet/sites/fakultaet/files/broschuere_lebenslauf_final_neu.pdf),
   [fintiba](https://www.fintiba.com/de/germany/working/german-cv)). One source states 1 to 2 pages
   depending on experience. The plugin sets 1 page and 2 pages as above (CG-6.1).
2. **Not produced.** Europass, the academic CV, and the functional CV are not produced (R-8.4, R-8.1). A
   Deckblatt (cover sheet) is not generated either.
3. **Limit.** A Lebenslauf longer than two pages, or longer than one page in the format `einseitig`, is a
   Blocker (R-2, R-7). The export reports the breach with exit code 4 (R-10.10); the file and the manifest
   stay. The only exception is the user's explicit decision in the session; the quality gate records it in
   `pruefbericht.md`, section `## Prüfung` (LS-7.4), and reports a Warnung instead. The decision is not
   limited to one run: it holds in every later run until the user withdraws it. The exception exists only
   for the Lebenslauf; the Anschreiben has none (AS-7.1) and the Motivationsschreiben has no exception rule.
   The font size is never reduced to meet the limit (LB-11.7).

## LB-3 Sections and their order

The order is fixed. A section that has no content is omitted. *Required* means: the section is written when
the Grundlage has content for it, and it is omitted when the Grundlage has none. A missing section never
produces an `[ERGÄNZEN]` placeholder or a Blocker; only the required items inside a written section do
(for example a Sprache without a level, LB-7.1). `Persönliche Daten` and the closing line are required
unconditionally.

| # | Section (heading) | Required | Content | Entry shape |
|---|---|---|---|---|
| 1 | `Persönliche Daten` | yes | Name, address, phone, e-mail; LinkedIn, GitHub or portfolio link optional | one line (LB-4.1) |
| 2 | `Kurzprofil` | in `kombiniert`; otherwise only on the user's opt-in | at most 3 sentences of facts | prose (LB-4.2) |
| 3 | `Berufserfahrung` | yes if the Grundlage has stations, unless entry level | Stations in reverse order | station block (LB-5) |
| 4 | `Praktika` | entry level | Internships | station block (LB-5) |
| 5 | `Relevante Projekte` | optional | Projects that carry a *Muss* requirement (CG-5.2) | list (LB-6) |
| 6 | `Ausbildung und Studium` | yes, if the Grundlage has content | Vocational training, degrees | list (LB-6) |
| 7 | `Schulbildung` | yes, if the Grundlage has content | School degrees | list (LB-6) |
| 8 | `Sprachkenntnisse (GER-Niveau)` | yes, if the Grundlage has content | Languages with a CEFR level | list (LB-7) |
| 9 | `IT- und Fachkenntnisse` | recommended | Skills with level or duration | list (LB-7) |
| 10 | `Weiterbildung und Zertifikate` | optional | Courses and certificates with issuer and year | list (LB-6) |
| 11 | `Ehrenamt` | optional | Voluntary work | list (LB-6) |
| 12 | `Interessen` | optional | Only if relevant (LB-8) | one line |
| 13 | Ort, Datum (Unterschrift optional, digital) | yes | LB-9 | one line |

1. **Headings.** The headings are the standard headings of CG-11.2a, in German. A heading may carry a
   qualifier in parentheses, as in `Sprachkenntnisse (GER-Niveau)`. No other heading is used (CV-10).
2. **Order.** Personal data first, then experience and education, then skills, then the optional parts at
   the end. Sources: [Uni Münster](https://www.wiwi.uni-muenster.de/fakultaet/sites/fakultaet/files/broschuere_lebenslauf_final_neu.pdf),
   [Randstad](https://www.randstad.de/karriere/bewerbungsratgeber/lebenslauf/). R-2 names the same order.
3. **Entry level.** For `einseitig`, `Ausbildung und Studium` and `Praktika` move before `Berufserfahrung`, or
   `Berufserfahrung` is omitted (R-8.1).
4. **One heading, one topic.** A section holds one kind of content. Skills are not mixed into education.

## LB-4 Personal data and Kurzprofil

### LB-4.1 Persönliche Daten

1. **Required.** Name, address, phone, e-mail. A source names the address with phone and e-mail as the
   minimum ([fintiba](https://www.fintiba.com/de/germany/working/german-cv),
   [Uni Köln](https://www.bfit.uni-koeln.de/sites/wiso_career/pdf/Allgemeines_UEbergreifendes/Bewerbungshilfen/Kurzinfo_Lebenslauf.pdf)).
2. **Optional.** Birth date and place, marital status, nationality, and photo are optional. Some sources list
   birth date and place as usual, and a photo as still common in practice
   ([Uni Gießen](https://www.uni-giessen.de/de/fbz/zentren/zfbk/career/international/bewerbung/lebenslauf)).
   The plugin includes them only when the user asks for them or the country requires it (R-2, R-8.2). The
   photo default is none. The photo is the image file `rohdaten/foto.jpg`; it is inserted as a Markdown image
   link with a relative path at the start of `Persönliche Daten`, before the data line of item 3. The skill
   only reads the file. Whether the export places the image is open (LB-14).
3. **Form.** One line: `Name · Anschrift · Telefon · E-Mail`. The separator is the middle dot with spaces.
   A link to LinkedIn, GitHub or a portfolio may follow as a further item. It is optional, recommended for
   IT roles, and written only when the profile holds it (R-2).
4. **Placeholders.** An unknown item is `[ERGÄNZEN: <Item>]`. A document with a placeholder is not ready
   (CV-01).
5. **No headings for labels.** Labels such as "Name:" are not used.
6. **Only on request.** Schwerbehinderung or a GdB, Arbeitserlaubnis and Führerschein are written only on
   the user's explicit request in the session (R-2). A posting that mentions them does not make them
   required; the skill may ask the user once.

### LB-4.2 Kurzprofil

1. **Required in `kombiniert`, optional elsewhere.** The Kurzprofil is part of the combined format (R-8.1).
   In every other format it is written only when the user opts in during the session. No source found for
   this document confirms it as usual in Germany; the opt-in is a decision of this plugin.
2. **Content.** At most three sentences. They state facts that are in the Grundlage: field, years of
   experience, the two or three most relevant competences, and for a career change the transferable
   evidence. They contain no evaluation and no personality words (LB-1.4, CG-8.2).
3. **Sourcing.** Every statement has a Grundlage entry (CG-2.3). A year count is computed from the Grundlage
   periods, not estimated.
4. **Wording.** Nominal phrases or participle phrases, no "Ich". Example form: `Softwareentwickler mit
   13 Jahren Erfahrung in Backend und Plattformbetrieb; Schwerpunkt Kubernetes`.

## LB-5 Station block

The station block follows R-2.1 and `cv-generierung/en.md`. This section adds the field rules.

1. **Header line.** `MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort` as a heading of level three. The period
   uses an en dash with spaces. The current station ends with `heute` (`MM/JJJJ – heute`); `seit MM/JJJJ` is
   not used (R-2).
2. **Position.** Exactly as in the Arbeitszeugnis or the contract. If none exists, the title of the
   Grundlage with `[KLÄREN: Titel laut Zeugnis]` (R-2.1).
3. **Arbeitgeber.** The legal name with Rechtsform and the city, as in the Grundlage. A Zeitarbeit placement
   shows the agency as Arbeitgeber, never the client (`unternehmensanalyse/en.md` UA-8 UA-C).
4. **Bullets.** Selection, limits, form, and wording follow CG-5, CG-6, and CG-8.1 to CG-8.3.
5. **A station without bullets.** A header line alone is allowed for a station that does not support the
   application, and the omission is recorded in `pruefbericht.md` (CG-6.5).
6. **Order inside the section.** Reverse chronological. Overlapping stations are ordered by start date,
   latest first.
7. **Projects.** Project-based experience (freelance, contract work) is shown as one station with the
   projects as bullets, or as a block `Relevante Projekte` that points to the Grundlage entry (CG-5.2).
   The employment history is not rearranged.

## LB-6 List entries (education, school, training, volunteering)

The list sections use one bullet per entry.

1. **Form.** `<Zeitraum>: <Abschluss oder Inhalt>, <Institution>, <Ort>`. Example: `09/2015 – 08/2018: Fachinformatiker
   Anwendungsentwicklung, Musterfirma GmbH, Berlin`.
2. **Period.** `MM/JJJJ – MM/JJJJ` when the Grundlage has months. A year-only entry is written as `JJJJ – JJJJ`
   and reported as a Warnung (CV-02, CG-9). No `[ERGÄNZEN: Monat]` placeholder is written, and the Grundlage
   note does not have to be completed for the document to be ready. A school degree may carry only the year
   of the degree.
3. **Order.** Reverse chronological, most recent first.
4. **Degree.** The official name of the degree, as in the certificate. A grade is stated only if the
   Grundlage states it, and then it is written unchanged.
5. **Certificates.** `<Jahr>: <Zertifikat>, <Aussteller>, <Ort>`. A certificate that the Grundlage does not
   hold is not written (R-1).
6. **Zeugnisse.** Certificates are attached documents, not part of this document. The Lebenslauf does not
   copy their wording. Sources: Arbeitszeugnisse are the usual proof
   ([Uni Gießen](https://www.uni-giessen.de/de/fbz/zentren/zfbk/career/international/bewerbung/lebenslauf)).
7. **No explanation of a gap here.** A gap over two months is handled by CG-9, as its own neutral entry.

## LB-7 Languages and skills

1. **Languages.** `<Sprache>: <GER-Niveau>` (A1 to C2) or `Muttersprache`. A level without a source is not
   written (R-9.8). A self-assessment is marked as such in the Grundlage; the document may state the level but
   not a certificate.
2. **IT- und Fachkenntnisse.** Grouped by topic, one bullet per group: `<Gruppe>: <Eintrag>, <Eintrag>`. A level
   or a duration is stated only when the Grundlage has it.
3. **Order.** Within a group, the entries that the *Muss* requirements name come first (CG-5). Across the
   groups, the most relevant group comes first.
4. **No rating graphics.** No bars, dots, stars, or percentages for skills (R-8.3, CG-11.3).
5. **No invented proficiency.** "Grundkenntnisse" does not become "sicher in" (CG-7.2).
6. **Brevity.** At most ten entries per group. A hiring manager scans a skill group in a few seconds and
   reads only the terms that match the posting; a longer list hides them. The full list stays in the
   Grundlage, and the order of LB-7.3 brings the matching terms to the front.

## LB-8 Optional sections

1. **Ehrenamt.** Only if it supports the application or fills a period. The same entry form as LB-6.
2. **Interessen.** Only if the user asks and the interests are neutral and relevant. Health, family, religion,
   politics, and similar topics are not written without the user's explicit request (CG-9.2, E-5).
3. **Not written.** References ("Referenzen auf Anfrage") and reference persons are not written in the
   Lebenslauf. Sources name references only for special cases such as freelancers
   ([Lingoda](https://www.lingoda.com/blog/de/lebenslauf-auf-deutsch/)). When the posting asks for
   references, the Anschreiben carries `[ERGÄNZEN: Referenzen]` until the user names persons who have
   consented (R-5, Blocker). Names are never invented.

## LB-9 Closing

1. **Ort, Datum, Unterschrift.** The document ends with the place, the current date, and the signature line
   (sources: [Uni Münster](https://www.wiwi.uni-muenster.de/fakultaet/sites/fakultaet/files/broschuere_lebenslauf_final_neu.pdf),
   [Uni Gießen](https://www.uni-giessen.de/de/fbz/zentren/zfbk/career/international/bewerbung/lebenslauf)).
2. **Form.** `Ort, TT.MM.JJJJ`, same as in the Anschreiben. The Ort is the city of the candidate's address
   (the Anschrift in `Persönliche Daten`).
3. **Signature.** A handwritten signature for paper. For digital applications the line is optional; a scanned
   signature is common in practice, and the plugin does not require it (R-2). A signature image in the
   document is not supported in Phase 1: the document allows no images apart from the optional photo
   (CG-11.3), so the user signs the printed page or leaves the line empty.
4. **Date.** The date of generation, in the same format as the Anschreiben. A date more than 30 days before
   the check date of the quality gate is *old* and is a Warnung.

## LB-10 Dates and periods

1. **Format.** `MM/JJJJ – MM/JJJJ`, `MM/JJJJ – heute`, with an en dash and no day (R-2).
2. **Consistency.** One format in the whole document. A mixed format is a Warnung (CV-02).
3. **Order and plausibility.** The end is not before the start (CV-04). Stations are in reverse order
   (CV-04).
4. **Gaps.** A gap over two months is a neutral entry or an explicit marker; the reason is not invented
   (CG-9, CV-13).
5. **Source.** Periods equal the Grundlage (CV-06). A year-only period in the Grundlage stays year-only
   in the document and is reported as a Warnung (CV-02). No month placeholder is written and no completion
   of the Grundlage is required (LB-6.2, CG-9).

## LB-11 Layout and file

1. **Layout.** One column, one accent colour, thin rules under the section headings, coloured bullets, no
   tables, no icons, no photos by default, no text in header or footer except a quiet page number. The page
   number is the one exception that R-8.3.1 allows for ATS documents. The design is
   in `skills/job-application-export/templates/document.tex` and `templates/cv.lua`.
2. **Same look as the Anschreiben in the PDF.** Both use one template (`anschreiben/en.md` AS-3.7). The letter
   page has its own margins (AS-3.3) and does not use the Lebenslauf macros. Only the PDF carries this layout;
   the HTML export has its own reduced layout with the same text (R-10.7), and DOCX uses Word heading styles
   (R-10.6).
3. **Heading placement.** A heading is never the last element of a page (template rule).
4. **Header block.** The name stands first and large, above the personal data. The Markdown form `Name · Anschrift
   · Telefon · E-Mail` (LB-4.1) is rendered as the name, then the label `Persönliche Daten` and the remaining
   items, which wrap only between items. All words of the source stay in the PDF.
5. **Grid.** A left column of 33 mm holds periods and labels; the content stands to its right. It applies to the
   stations (LB-5.1: period, position in bold, employer and place below in the muted colour) and to the list
   sections with a period (LB-6.1). Bullets under a station use the full width. The grid is made with boxes,
   not with a table.
6. **Skill groups.** In `IT- und Fachkenntnisse` and `Sprachkenntnisse` the label before the colon is bold.
7. **Sizes.** Name 25 pt, section heading 13 pt, position 11 pt, body 10.5 pt on 14.3 pt leading, periods,
   employers and labels 9.5 pt, page number 9 pt. The size is not reduced to fit a page limit.
8. **Margins.** 20 mm left, 18 mm right, 17 mm top, 19 mm bottom.
9. **Text flow.** Ragged right with a bounded stretch, no justification. Hyphenation is rare and is switched
   off in station headings. The last two words of a bullet are bound with a no-break space, and the names in
   `KEEP_TOGETHER` of `cv.lua` (for example `VMware Tanzu`, `Argo Workflows`) never break. Widows and orphans
   are suppressed.
10. **Colours.** Ink `#1E2328` (15.8:1 on white), accent `#1F4E79` (8.7:1), muted `#5A6270` (6.1:1). All pass
    WCAG AA for body text (4.5:1), and the hierarchy stays visible in grayscale through weight and position.
11. **Page break.** The export moves a section heading to the next page when fewer than six lines remain, and a
    station when fewer than three and a half lines remain.
12. **Frontmatter of the Markdown source.**

    | Key | Required | Meaning |
    |---|---|---|
    | `grundlage_hash` | yes | Hash of the Grundlage at creation (R-9.5) |
    | `format` | yes | `chronologisch`, `einseitig`, `kombiniert`, or `ats` |
    | `situation` | recommended | The situation chosen for the format (R-8.1) |
    | `auspraegung` | recommended | The variant (folder name), `lebenslauf-versionen` LV-3 |
    | `version` | recommended | Integer of the Version, LV-3 |
    | `version_datum` | for a frozen Version | `YYYY-MM-DD`; fixes the PDF dates so the PDF is reproducible (LV-6) |

13. **File name.** `Vorname_Nachname_Lebenslauf.<ext>` (R-4, R-10.4).
14. **Plain text.** The text extracted from the PDF equals the Markdown text apart from the page number
   (R-10.8, CG-12).

## LB-12 Overrides by the posting

An explicit instruction of the posting overrides the defaults of this document: a format, a length, a file
type, a language, a section, a form field (CG-11.6). The analysis records it and the quality gate checks it. A
mandatory instruction that is not met is a Blocker.

## LB-13 Quality checks

The automated rules of `scripts/cv_checks.py` (CV-01 to CV-17) apply to this document. This table adds the
document-level checks and shows which are automated.

| Check | Rule | Kind | Severity |
|---|---|---|---|
| A placeholder is left | LB-4.1.4 | automated (CV-01) | Blocker |
| A section heading is not in the standard set | LB-3.1 | automated (CV-10) | Warnung |
| A station header is not in the form of LB-5.1 | LB-5.1 | automated (CV-02) | Warnung |
| Stations not in reverse order, or the end is before the start | LB-5.6, LB-10.3 | automated (CV-04) | Warnung, Blocker |
| A period differs from the Grundlage | LB-10.5 | automated (CV-06) | Blocker |
| A station is not in the Grundlage | LB-5 | automated (CV-15) | Blocker |
| A gap over two months has no entry | LB-10.4 | automated (CV-13) | Blocker |
| A number that the Grundlage does not state | CG-8.3 | automated (CV-05) | Blocker |
| A leadership word while `fuehrung` is `ungeklärt` or missing in the station note | CG-8.2 | automated (CV-16) | Warnung |
| A leadership word while the station note says `fuehrung: nein` | CG-8.2 | automated (CV-16) | Blocker |
| A table in the document | LB-11.1 | automated (CV-08) | Warnung, Blocker with ATS |
| More than five bullets, or a bullet longer than two lines | CG-6 | automated (CV-03, CV-12) | Warnung, Hinweis |
| A generic or evaluative phrase | CG-8.2 | automated (CV-11) | Warnung |
| A sub-bullet below a bullet | R-2.1 | automated (CV-17) | Hinweis |
| The Kurzprofil without the user's opt-in outside `kombiniert`, with more than three sentences, or with unsourced content | LB-4.2 | review | Warnung |
| A skill with a graphic rating | LB-7.4 | review | Warnung |
| A list entry not in the form of LB-6.1 | LB-6.1 | review | Hinweis |
| Optional personal data without the user's request | LB-4.1.2, LB-4.1.6 | review | Hinweis |
| More than two pages (`cv`), or more than one page with the format `einseitig` | LB-2.3 | export page check (exit code 4, R-10.10); the gate sets the severity | Blocker; Warnung with the user's recorded decision, in every later run |
| The date of the closing line is more than 30 days before the check date | LB-9.4 | review | Warnung |

## LB-14 Open points

| Area | Point | Status |
|---|---|---|
| Kurzprofil | No source found for a Kurzprofil as usual in Germany. Decision: required in `kombiniert`, opt-in elsewhere, at most three sentences (LB-4.2) | done (decision of this plugin) |
| Photo | Sources call the photo still common in practice. The default of R-8.2 is none. The user's choice decides; no change proposed | open |
| Automation | Checks for list-entry form (LB-6), skill group size (LB-7.6), and the closing date (LB-9.4) are not in `cv_checks.py` | open |
| CV-16 severity | `cv_checks.py` distinguishes Warnung (`ungeklärt`, missing) and Blocker (`nein`) | done (script, 0.2.0) |
| Photo in the export | The Markdown source carries the photo as an image link (LB-4.1.2). The PDF template (`cv.lua`, `document.tex`) has no photo layout, and no test covers an image in any format; the word check (CG-12.2) is not specified for the alternative text | open (export) |
| Signature image | Not supported in Phase 1 (LB-9.3). An image-capable export is a later requirement | open, deliberate |
| Deckblatt | Not generated (LB-2.2). No requirement known | closed |
| English documents | Language override produces the German structure with English text; a dedicated spec is a stub (R-11) | open |
| Document ID | A unique `dokument_id` in the frontmatter, carried into the export metadata, is proposed and not decided | open |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |

## LB-15 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| LB-A | Experienced candidate, standard posting | `chronologisch`, two pages at most, sections in LB-3 order, stations with bullets within CG-6 |
| LB-B | Entry-level candidate | `einseitig`, education and internships first, one page |
| LB-C | Career change | `kombiniert`, a Kurzprofil of facts, the history unchanged |
| LB-D | Postings with an ATS hint | Same sections, plain headings, no table (CV-08 as Blocker), text PDF; DOCX only when the portal requires it (R-8.3.4) |
| LB-E | Education with only years in the Grundlage | Year-only periods in the document, reported (CV-02) |
| LB-F | The user asks for no photo and no birth date | Neither appears |
| LB-G | A skill without a level in the Grundlage | Written without a level |
| LB-H | An interest that touches a sensitive topic | Not written unless the user explicitly asks |

## LB-16 Sources

All retrieved 2026-10-22. They are ratgeber and university pages (secondary sources). They disagree on the
photo and on birth data, and none of them confirms a Kurzprofil.

- [Randstad, Lebenslauf schreiben](https://www.randstad.de/karriere/bewerbungsratgeber/lebenslauf/)
- [Uni Münster, Broschüre Lebenslauf (PDF)](https://www.wiwi.uni-muenster.de/fakultaet/sites/fakultaet/files/broschuere_lebenslauf_final_neu.pdf)
- [Uni Köln, Kurzinfo Lebenslauf (PDF)](https://www.bfit.uni-koeln.de/sites/wiso_career/pdf/Allgemeines_UEbergreifendes/Bewerbungshilfen/Kurzinfo_Lebenslauf.pdf)
- [Uni Gießen, Lebenslauf](https://www.uni-giessen.de/de/fbz/zentren/zfbk/career/international/bewerbung/lebenslauf)
- [fintiba, German CV](https://www.fintiba.com/de/germany/working/german-cv)
- [Lingoda, Lebenslauf auf Deutsch](https://www.lingoda.com/blog/de/lebenslauf-auf-deutsch/)
