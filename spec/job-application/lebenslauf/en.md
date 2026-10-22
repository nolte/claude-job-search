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
5. **One document per application.** The Lebenslauf is generated for one Stellenanzeige from the Grundlage
   (CG-5). The Grundlage is complete; the document is a selection.

## LB-2 Formats

The format follows the situation (R-8.1). This document adds what each format contains.

| Format | Situation | Sections | Length |
|---|---|---|---|
| `chronologisch` | Standard, experience in Germany | LB-3 in full order | 2 pages at most |
| `einseitig` | Entry level, student, internship | Education and internships first, then skills | 1 page |
| `kombiniert` | Career change, many stations | Kurzprofil, then LB-3; stations may be grouped | 2 pages at most |
| `ats` | ATS hint or online portal | Same as `chronologisch`, with the rules of R-8.3 | as the posting asks |

1. **Length.** Sources give about one page for students and graduates, and two pages for working people
   ([Uni Münster](https://www.wiwi.uni-muenster.de/fakultaet/sites/fakultaet/files/broschuere_lebenslauf_final_neu.pdf),
   [fintiba](https://www.fintiba.com/de/germany/working/german-cv)). One source states 1 to 2 pages
   depending on experience. The plugin sets 1 page and 2 pages as above (CG-6.1).
2. **Not produced.** Europass, the academic CV, and the functional CV are not produced (R-8.4, R-8.1).

## LB-3 Sections and their order

The order is fixed. A section that has no content is omitted, except those marked as required.

| # | Section (heading) | Required | Content | Entry shape |
|---|---|---|---|---|
| 1 | `Persönliche Daten` | yes | Name, address, phone, e-mail; LinkedIn optional | one line (LB-4.1) |
| 2 | `Kurzprofil` | only in `kombiniert` | 2 to 4 sentences of facts | prose (LB-4.2) |
| 3 | `Berufserfahrung` | yes, unless entry level | Stations in reverse order | station block (LB-5) |
| 4 | `Praktika` | entry level | Internships | station block (LB-5) |
| 5 | `Relevante Projekte` | optional | Projects that carry a *Muss* requirement (CG-5.2) | list (LB-6) |
| 6 | `Ausbildung und Studium` | yes | Vocational training, degrees | list (LB-6) |
| 7 | `Schulbildung` | yes | School degrees | list (LB-6) |
| 8 | `Sprachkenntnisse (GER-Niveau)` | yes | Languages with a CEFR level | list (LB-7) |
| 9 | `IT- und Fachkenntnisse` | recommended | Skills with level or duration | list (LB-7) |
| 10 | `Weiterbildung und Zertifikate` | optional | Courses and certificates with issuer and year | list (LB-6) |
| 11 | `Ehrenamt` | optional | Voluntary work | list (LB-6) |
| 12 | `Interessen` | optional | Only if relevant (LB-8) | one line |
| 13 | Ort, Datum, Unterschrift | yes | LB-9 | one line |

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
   photo default is none.
3. **Form.** One line: `Name · Anschrift · Telefon · E-Mail`. The separator is the middle dot with spaces.
4. **Placeholders.** An unknown item is `[ERGÄNZEN: <Item>]`. A document with a placeholder is not ready
   (CV-01).
5. **No headings for labels.** Labels such as "Name:" are not used.

### LB-4.2 Kurzprofil

1. **Only in `kombiniert`.** The Kurzprofil is part of the combined format (R-8.1). No source found for this
   document confirms it as usual in Germany. The plugin therefore uses it only for career changes and many
   stations (open point LB-14).
2. **Content.** Two to four sentences. They state facts that are in the Grundlage: field, years of
   experience, the two or three most relevant competences, and for a career change the transferable
   evidence. They contain no evaluation and no personality words (LB-1.4, CG-8.2).
3. **Sourcing.** Every statement has a Grundlage entry (CG-2.3). A year count is computed from the Grundlage
   periods, not estimated.
4. **Wording.** Nominal phrases or participle phrases, no "Ich". Example form: `Softwareentwickler mit
   13 Jahren Erfahrung in Backend und Plattformbetrieb; Schwerpunkt Kubernetes`.

## LB-5 Station block

The station block follows R-2.1 and `cv-generierung/en.md`. This section adds the field rules.

1. **Header line.** `MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort` as a heading of level three. The period
   uses an en dash with spaces. The current station ends with `heute`.
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

1. **Form.** `<Zeitraum>: <Abschluss oder Inhalt>, <Institution>, <Ort>`. Example: `2007 – 2010: Fachinformatiker
   Anwendungsentwicklung, Hermes Logistik Gruppe Deutschland GmbH, Hamburg`.
2. **Period.** `MM/JJJJ – MM/JJJJ` when the Grundlage has months. A year-only entry is written as `JJJJ – JJJJ`
   and reported (CV-02, CG-9). A school degree may carry only the year of the degree.
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
6. **Brevity.** At most six entries per group. The full list stays in the Grundlage.

## LB-8 Optional sections

1. **Ehrenamt.** Only if it supports the application or fills a period. The same entry form as LB-6.
2. **Interessen.** Only if the user asks and the interests are neutral and relevant. Health, family, religion,
   politics, and similar topics are not written without the user's explicit request (CG-9.2, E-5).
3. **Not written.** References ("Referenzen auf Anfrage") are not written. Sources name references only for
   special cases such as freelancers ([Lingoda](https://www.lingoda.com/blog/de/lebenslauf-auf-deutsch/)).

## LB-9 Closing

1. **Ort, Datum, Unterschrift.** The document ends with the place, the current date, and the signature line
   (sources: [Uni Münster](https://www.wiwi.uni-muenster.de/fakultaet/sites/fakultaet/files/broschuere_lebenslauf_final_neu.pdf),
   [Uni Gießen](https://www.uni-giessen.de/de/fbz/zentren/zfbk/career/international/bewerbung/lebenslauf)).
2. **Form.** `Ort, TT.MM.JJJJ`, same as in the Anschreiben.
3. **Signature.** A handwritten signature for paper. For digital applications the line is optional; a scanned
   signature is common in practice, and the plugin does not require it (R-2).
4. **Date.** The date of generation, in the same format as the Anschreiben. An old date is a Warnung.

## LB-10 Dates and periods

1. **Format.** `MM/JJJJ – MM/JJJJ`, `MM/JJJJ – heute`, with an en dash and no day (R-2).
2. **Consistency.** One format in the whole document. A mixed format is a Warnung (CV-02).
3. **Order and plausibility.** The end is not before the start (CV-04). Stations are in reverse order
   (CV-04).
4. **Gaps.** A gap over two months is a neutral entry or an explicit marker; the reason is not invented
   (CG-9, CV-13).
5. **Source.** Periods equal the Grundlage (CV-06). A year-only period in the Grundlage stays year-only
   in the document and is reported.

## LB-11 Layout and file

1. **Layout.** One column, one accent colour, thin rules under the section headings, coloured bullets, no
   tables, no icons, no photos by default, no text in header or footer except a quiet page number. The design is
   in `skills/job-application-export/templates/document.tex` and `templates/cv.lua`.
2. **Same look as the Anschreiben.** Both use one template (`anschreiben/en.md` AS-3.7). The letter page has its
   own margins (AS-3.3) and does not use the Lebenslauf macros.
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

13. **File name.** `Vorname_Nachname_Lebenslauf.<ext>` (R-4, R-10.4).
14. **Plain text.** The text extracted from the PDF equals the Markdown text apart from the page number
   (R-10.8, CG-12).

## LB-12 Overrides by the posting

An explicit instruction of the posting overrides the defaults of this document: a format, a length, a file
type, a language, a section, a form field (CG-11.6). The analysis records it and the quality gate checks it. A
mandatory instruction that is not met is a Blocker.

## LB-13 Quality checks

The automated rules of `scripts/cv_checks.py` (CV-01 to CV-16) apply to this document. This table adds the
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
| A leadership word without `fuehrung: ja` | CG-8.2 | automated (CV-16) | Blocker |
| A table in the document | LB-11.1 | automated (CV-08) | Warnung, Blocker with ATS |
| More than five bullets, or a bullet longer than two lines | CG-6 | automated (CV-03, CV-12) | Warnung, Hinweis |
| A generic or evaluative phrase | CG-8.2 | automated (CV-11) | Hinweis |
| The Kurzprofil in a format other than `kombiniert`, or with unsourced content | LB-4.2 | review | Warnung |
| A skill with a graphic rating | LB-7.4 | review | Warnung |
| A list entry not in the form of LB-6.1 | LB-6.1 | review | Hinweis |
| Optional personal data without the user's request | LB-4.1.2 | review | Hinweis |
| More than two pages (`cv`) | LB-2 | export page check | Warnung |
| The date of the closing line is old | LB-9.4 | review | Warnung |

## LB-14 Open points

| Area | Point | Status |
|---|---|---|
| Kurzprofil | No source found for a Kurzprofil as usual in Germany. A primary source or an employer statement is needed to keep or drop it | open |
| Photo | Sources call the photo still common in practice. The default of R-8.2 is none. The user's choice decides; no change proposed | open |
| Automation | Checks for list-entry form (LB-6), skill group size (LB-7.6), and the closing date (LB-9.4) are not in `cv_checks.py` | open |
| Document ID | A unique `dokument_id` in the frontmatter, carried into the export metadata, is proposed and not decided | open |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |

## LB-15 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| LB-A | Experienced candidate, standard posting | `chronologisch`, two pages at most, sections in LB-3 order, stations with bullets within CG-6 |
| LB-B | Entry-level candidate | `einseitig`, education and internships first, one page |
| LB-C | Career change | `kombiniert`, a Kurzprofil of facts, the history unchanged |
| LB-D | Postings with an ATS hint | Same sections, plain headings, no table (CV-08 as Blocker), DOCX or text PDF |
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
