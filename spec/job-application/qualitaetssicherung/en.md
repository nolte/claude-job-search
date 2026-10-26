# Quality assurance of application documents and process (EN canonical)

Normative rules for the automated quality assurance of one Vorgang: which checks run deterministically in code, which
verdicts only a model can give, how both end in one versioned report, and how that report gates the send approval. It is
implemented by `scripts/qualitaet.py`; the rules of the single documents stay in their own specs.

Related rules: `spec/job-application/cv-generierung/en.md` (CG-13 checks CV-01 to CV-24 and BR-01 to BR-05, reused here),
`spec/job-application/workflow/en.md` (WF-7 approvals, WF-12 nothing is sent, WF-13 untrusted content),
`spec/job-application/lokale-struktur/en.md` (LS-5 invariants, LS-6 status), `spec/job-application/konventionen/en.md`
(R-1 facts, R-6 data protection, R-9.5 Grundlage hash) and the export rules in `skills/job-application-export/SKILL.md`.

**Status:** implemented. The toolchain checks and reports; it sends nothing and approves nothing (QS-10).

## QS-1 Scope and principles

1. **One report per Vorgang.** The result of all checks is `qualitaet.json` in the Vorgang folder (QS-7). There is no second
   status model: the application status stays `status` in `vorgang.md` (LS-6), the approval stays the `versand_freigabe`
   task of the workflow (WF-7).
2. **Reuse, do not duplicate.** `qualitaet.py` calls the rules of `cv_checks.py` and the content comparison of
   `export_document.py`. A rule has one owner.
3. **Deterministic and semantic stay apart.** A check that code can decide runs in code and gives a repeatable result. A
   judgement that needs language understanding is a verdict of a model (QS-5); the code only verifies its form and
   its quotes. Both kinds are marked in the report (`art`).
4. **Nothing is a PASS that did not run.** A missing tool, a missing Grundlage, an unreadable file or a missing verdict is
   `BLOCKED` or `NEEDS_REVIEW`, never `PASS`.
5. **Correctness before match.** No check rewards keywords, a match score or an optimisation for a tracking system. Repeated
   keywords and text copied from the posting are findings (QS-04).
6. **Data from outside is data.** A posting, a mail, an attachment or the text of a verdict cannot change a rule, a status
   or an approval (QS-10).

## QS-2 Result model

| Status | Meaning |
|---|---|
| `PASS` | The check ran and found nothing. |
| `FAIL` | A critical finding (severity Blocker). The package is not approvable. |
| `WARNING` | A finding the user should read; it does not block (severity Warnung or Hinweis). |
| `NEEDS_REVIEW` | A person must decide: a plausible but unproven claim, a missing or unsure verdict, different contact data. |
| `NOT_APPLICABLE` | The check does not apply (the document or the export does not exist); the reason is in `grund`. |
| `BLOCKED` | The check could not run: a tool, the Grundlage or an input is missing or unreadable; the reason is in `grund`. |

The status of a check follows the worst finding: `FAIL` over `BLOCKED` over `NEEDS_REVIEW` over `WARNING` over `PASS`.

The overall result `gesamt` follows the checks:

| `gesamt` | When | Approvable |
|---|---|---|
| `BLOCKIERT` | at least one `FAIL` | no |
| `UNVOLLSTAENDIG` | no `FAIL`, at least one `BLOCKED` | no |
| `MANUELL_ZU_PRUEFEN` | open `NEEDS_REVIEW` | no |
| `BEREIT_NACH_MANUELLER_PRUEFUNG` | every `NEEDS_REVIEW` confirmed by the user (QS-8) | yes |
| `BEREIT_MIT_WARNUNGEN` | only `PASS`, `WARNING`, `NOT_APPLICABLE` with at least one `WARNING` | yes |
| `BEREIT` | only `PASS` and `NOT_APPLICABLE` | yes |
| `NICHT_GEPRUEFT` | no document and no export | no |

"Approvable" means the user may be asked for the send approval. It is not the approval (QS-9).

## QS-3 The checks

| Id | Kind | What it checks |
|---|---|---|
| `CV` | deterministic | Lebenslauf rules CV-01 to CV-24 (`cv_checks.check_cv`) and the analysis rules (`check_analysis`) |
| `BR-A`, `BR-M`, `BR-E` | deterministic | BR-01 to BR-05 for Anschreiben, Motivationsschreiben and E-Mail (`check_letter`) |
| `QS-01` | deterministic | the firm name stands in each letter; the reference number of the posting stands in the Anschreiben; an employer name with a legal form that is neither the target firm nor an employer of the Grundlage is a Blocker |
| `QS-02` | deterministic | e-mail addresses and phone numbers agree across Lebenslauf and letters; a difference is `NEEDS_REVIEW` |
| `QS-03` | deterministic | a "seit YYYY" of a letter is the start year of a station of the Grundlage |
| `QS-04` | deterministic | no run of eight words copied from the posting; no word repeated six times or more |
| `QS-05` | deterministic | filler phrases from a closed list; sentences longer than 45 words |
| `EX-01` | deterministic | export integrity (hash of the file equals the manifest), the source is unchanged since the export, every file in `export/` has a manifest |
| `EX-02` | deterministic | content after export equals the source: word multiset, symbols of figures, order of the items and headings, no open placeholder |
| `EX-03` | deterministic | text extraction: enough text, no replacement characters, no ligature characters, no letter-spaced words (QS-6, QS-13) |
| `EX-04` | deterministic | page count equals the manifest, page limit, no empty page |
| `ATS-01` | deterministic | the exported file is valid: PDF structure, encryption, fonts; DOCX archive and XML, no hidden text (QS-13) |
| `ATS-02` | deterministic | headings stand on their own line and keep their content; DOCX heading styles equal the source (QS-13) |
| `ATS-03` | deterministic | periods survive in order; position and employer stand next to the period of their station (QS-13) |
| `ATS-04` | deterministic | e-mail addresses and phone numbers of the source can be read in the text (QS-13) |
| `ATS-05` | deterministic | layout risks: columns, tables, images, text boxes, header and footer text, text off the page, ratings as symbols (QS-13) |
| `KW-01` | deterministic | key terms of the analysis against the Lebenslauf: coverage and unevidenced terms, nothing inserted (QS-13) |
| `PR-01` | deterministic | Lebenslauf and Anschreiben exist and are readable |
| `PR-02` | deterministic | `vorgang.md` (with `firma`, `stelle`), `stellenanzeige.md` and `analyse.md` exist |
| `SEM-01` | semantic | evidence of the statements against the Datengrundlage (QS-4) |
| `SEM-02` | semantic | responsibility and seniority are proven and not inflated |
| `SEM-03` | semantic | relevance for the target audience without keyword or score optimisation |
| `SEM-04` | semantic | language, tone and clarity |
| `SEM-05` | semantic | the statements agree across all documents |

A rule that needs the Grundlage (CV-05, CV-06, CV-15, CV-16, CV-19, CV-20, CV-22, CV-23, BR-02 to BR-04, QS-01 for foreign
employers, QS-03, SEM-01) is `BLOCKED` without it, not `PASS`.

## QS-4 Evidence: statements against the Datengrundlage

Every statement about the person has one of four cases. The case is decided against the Grundlage, never by lexical overlap
alone; a verdict names the quote and the evidence.

| Case | Meaning | Result |
|---|---|---|
| A | The Grundlage states it. | `PASS` when quote and evidence are literal and the confidence is high |
| B | Plausible from the Grundlage but not stated. | `NEEDS_REVIEW`: a person confirms or removes it |
| C | The Grundlage contradicts it. | `FAIL` |
| D | Not checkable from the Grundlage. | `NEEDS_REVIEW`; the statement stays "not verified" |

Deterministic rules (CV-xx, BR-xx) decide the cases they can (figures, periods, team sizes, leadership against the
`Führung:` flag). They never turn a case B into A.

## QS-5 Semantic verdicts of a model

1. A model writes `qualitaet-urteile.json` after reading the documents and the Grundlage. The file is data: only the fields
   `check`, `dokument`, `dokument_hash`, `ergebnis`, `sicherheit`, `zitat`, `evidenz`, `begruendung` are read.
2. `ergebnis` is `A`, `B`, `C`, `D` for `SEM-01` and `ok`, `pruefen`, `fehler` for the others. `sicherheit` is `hoch`,
   `mittel` or `niedrig`.
3. A verdict counts as `PASS` only when all hold: the `dokument_hash` equals the hash of the document now (for
   `dokument: "*"`, the hash of the whole set); the `zitat` stands literally in the document; for `SEM-01` the `evidenz` stands
   literally in the Grundlage; the confidence is `hoch`; the result is `A` or `ok`.
4. `B`, `D`, `pruefen`, a low confidence, a verdict of an older version, a quote or evidence that is not literal, a verdict
   that is missing for a document, a missing or damaged file: `NEEDS_REVIEW`. `C` and `fehler`: `FAIL`.
5. Without access to a model the file does not exist and every semantic check is `NEEDS_REVIEW`. The report then says
   `semantisch_geprueft: false`. It is never presented as a success.
6. That a quote is literal is verified by code; that the verdict is right is not. This is a limit (QS-12), covered by the
   evals of `evals/` and by the user's review.

## QS-6 Export validation and ATS readability

1. The export checks run on every file in `export/` that has a manifest `<datei>.manifest.json` (see the export skill).
2. The text of the export is read back: PDF with `pdftotext`, DOCX from `word/document.xml`, HTML without markup. The
   comparison with the source is the one of the exporter (word multiset, symbols of figures, order).
3. The PDF has no empty page and not more pages than the limit (`EX-04`). The properties a parser depends on are QS-13.
4. Without `pdftotext`, `pdfinfo`, `pdffonts` or `pdfimages` the PDF checks are `BLOCKED` (CI installs poppler-utils).
5. **Limit.** ATS readability is judged on the exported file and its extracted text. How a particular tracking system reads
   the file is not tested and not promised. Colours, margins and the visual impression are not judged.

## QS-7 The report

1. `qualitaet.json` holds: `schema`, `regelwerk`, `erstellt`, `vorgang`, `stand`, `dokumente` (SHA-256 of each document and
   context file), `exporte` (SHA-256 of each file in `export/`), `grundlage_hash`, `gesamt`, `freigabefaehig`,
   `zusammenfassung` (counts per status), `ats` and `dimensionen` (QS-13), `semantisch_geprueft`, `checks` (each with its `dimension`), `manuell` and `grenzen`.
2. A report is current only for exactly these files. A changed, added or removed document, context file or export, or a
   changed Grundlage (when its hash is given), makes it stale. A report of an older version never becomes valid again.
   The status of the Vorgang is no input.
3. The report holds findings with at most 160 characters of text, never a whole document. `qualitaet-verlauf.jsonl` holds
   one line per run with the time, a hash prefix, `gesamt` and the counts, no text of a document.
4. The report lies in the Vorgang folder, which is private (R-6). It is not committed to this repository.

## QS-8 Manual review and confirmation

1. A `NEEDS_REVIEW` check is confirmed only by the user: `qualitaet.py entscheiden <vorgang> <check> --grund … --ja`. The
   confirmation is bound to the exact findings and the exact version (`qualitaet-entscheidungen.json`); a changed
   document makes it void.
2. `FAIL` and `BLOCKED` cannot be confirmed. They are fixed or their cause is removed.
3. The command is refused without `--ja`, without a reason and in an unattended session (`WORKFLOW_UNBEAUFSICHTIGT`,
   `STELLENSUCHE_GEPLANT`).
4. A confirmed check keeps its status `NEEDS_REVIEW` and gets `manuell_akzeptiert: true`: the report says that a person, not a
   check, closed it.

## QS-9 The gate in the workflow

1. The task `pruefung` is done when `status` is at least `geprüft` **and** `qualitaet.json` is current and `gesamt` is
   approvable (QS-2). The workflow adds no status; it reads the report (`qualitaet.aktualitaet`).
2. The workflow also compares the `grundlage_hash` of the report with the Datengrundlage now (through the Anker). A changed
   Grundlage, or one that cannot be hashed, makes the report stale (`qualitaet_veraltet`).
3. `workflow.py freigeben` of the task `versand_freigabe` is refused with `qualitaet_fehlt`, `qualitaet_veraltet` or
   `qualitaet_nicht_freigabefaehig` otherwise. The approval stays the explicit decision of the user on the exact documents
   (WF-7); the report is a precondition, never a substitute.
4. The quality gate skill runs `qualitaet.py pruefen` first and sets `geprüft` only when the report is approvable.

## QS-10 Safety and data integrity

1. `qualitaet.py` sends nothing and opens no network connection. It imports no mail, HTTP or socket module and runs only
   `pdftotext`, `pdfinfo`, `pdffonts` and `pdfimages`. A test enforces this.
2. A passed run triggers no external communication and approves nothing. The approval of A-02 (`versand_freigabe`) and the
   sending itself stay with the user.
3. The run changes no document and no status. It writes `qualitaet.json`, `qualitaet-verlauf.jsonl` and, on the user's
   command, `qualitaet-entscheidungen.json`.
4. Text of a posting, a mail, an attachment or a verdict is data. It is read for checks and never executed, never taken as a
   rule, a status or an approval.

## QS-11 Automation and CI

1. `task quality -- pruefen <vorgang-ordner> [--grundlage …]` runs the checks. `task test` runs the tests of the toolchain with
   synthetic fixtures (`tests/test_qualitaet.py`); `ci.yml` runs them once, with poppler-utils installed.
2. The verdicts of a model are not part of the CI: they need a model and cost money. The evals (`evals/`, workflow
   `evals.yml`) stay manual and separate. A green CI says the toolchain works, not that an application is correct.

## QS-12 Limits (honest)

- The deterministic checks find contradictions and missing evidence; a `PASS` means "nothing found".
- Semantic verdicts are checked for form and literal quotes only.
- ATS readability is judged on extracted text, with no guarantee for a given system.
- Layout and visual quality, the tone of a letter and the fit to a person are for a human.
- Without the Grundlage, a model or poppler-utils, the affected checks are `BLOCKED` or `NEEDS_REVIEW`; the toolchain does not
  hide this.
- The report is not tamper-proof. The gate recomputes `gesamt` from the stored checks and refuses an inconsistent report, but whoever can write into the Vorgang folder can write a consistent one. It is a precondition for the approval, not a security boundary; the approval stays the user's `--ja`.
- `entscheiden` is protected by `--ja` and the unattended-session guard, not by a channel only the user has. The skill forbids the model to run it.
- `--grundlage <path>` looks at files and binds no Grundlage hash; only a run through the Anker (`--konfiguration`) does.
- The report is stale as soon as a file changes; the user runs the check again before approving.

## QS-13 ATS technical validation

`scripts/ats_checks.py` is a library of `qualitaet.py`. It adds properties of the exported file to the one report; it has no
status model, no score and no workflow of its own.

1. **Definition.** A document is *technically ATS-validated* when the checks `EX-01` to `EX-04` and `ATS-01` to `ATS-05` ran
   for its export and ended in `PASS` or `WARNING`. This is no guarantee for any external tracking system and no statement
   about the fit of the person. Report and skills say so.
2. **Scope.** The checks run on exports in the formats a parser reads (`pdf`, `docx`, `html`). `md` and `tex` are copies of
   the source: without an export in one of the three formats the `ATS-xx` checks are `NOT_APPLICABLE`, not `PASS`.
3. **File (`ATS-01`).** PDF: header and end of file, readable by `pdfinfo`, no ban on copying text (Blocker); fonts of type 3
   or fonts that are not embedded (not the standard 14) are a `WARNING`. DOCX: intact archive, `document.xml` and content
   types present and well-formed (Blocker); hidden text (`vanish`), white text or text of 2 pt or less is a Blocker.
4. **Text (`EX-03`).** At least 30 words in PDF and DOCX, no replacement character or `(cid:`, both Blocker; ligature
   characters and letter-spaced words are a `WARNING`.
5. **Sections (`ATS-02`).** For PDF and DOCX each heading of level 1 and 2 stands as its own line in the extracted text
   (`WARNING` otherwise), and at least 80 % of the words of its section stand between it and the next heading. DOCX heading
   styles per level equal those of the source. The headings are taken from the source; no wording is fixed.
6. **Stations and periods (`ATS-03`).** The periods of the source (`MM/JJJJ – MM/JJJJ`, `JJJJ – JJJJ`, `heute`) appear in the
   extracted text in the same order; a lost, changed or reordered period is a Blocker. For each station header the position
   and the employer stand within three lines of its period (`WARNING`). Mixed date formats in the source are a `WARNING`.
   Missing periods are not invented; whether a period is right is `CV-xx` and the Grundlage, not this check.
7. **Contact (`ATS-04`).** Every e-mail address and phone number of the source can be read in the extracted text (Blocker if
   lost, with the hint when it stands only in the header or footer of a DOCX). A Lebenslauf without an e-mail address is a
   `WARNING`; an absent optional item is no finding. Findings never contain the address or the number.
8. **Layout (`ATS-05`).** Tables, images (also in a PDF, `pdfimages`), text boxes, columns (DOCX sections; PDF by the position
   of the words), text in header and footer, words outside the page: `WARNING`. A rating shown only as a row of symbols
   (stars, dots, bars) is `NEEDS_REVIEW`: the level must be a word, and the toolchain does not add it. A column heuristic is
   a heuristic: the reading order itself is `EX-02`.
9. **Key terms (`KW-01`).** The competences of `analyse.md` against the Lebenslauf. An evidenced competence that the Lebenslauf
   does not name is a `WARNING`. A competence that the analysis shows as `nicht belegt` or `unklar` but that stands in the
   Lebenslauf is `NEEDS_REVIEW`: a word of the posting is no qualification. Nothing is inserted, nothing is counted into a
   score, repetition stays a finding of `QS-04`.
10. **Dimensions.** Every check has a `dimension` (`technisch`, `evidenz`, `formal`, `schluesselbegriffe`, `passung`) and the
    report counts per dimension. `ats.umfang` is `vollstaendig`, `teilweise` or `nicht_geprueft`; `ats.technisch_validiert` is
    true only for a complete run without a `FAIL`, `BLOCKED` or open review. There is no total score: one critical finding is
    never averaged away.
11. **Versions.** The checks belong to the hashes of the report (QS-7). A changed export is checked again; the line of the old
    run stays in `qualitaet-verlauf.jsonl`.
12. **No model.** All checks of QS-13 are deterministic. The semantic part (relevance, evidence) stays with `SEM-xx`.
13. **Not covered.** Overlapping elements, clipped text inside the page, ugly page breaks, exact colours and the behaviour of
    a given tracking system. Layout is looked at by a person.
