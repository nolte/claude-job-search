# Quality assurance

`scripts/qualitaet.py` checks one Vorgang and writes one report, `qualitaet.json`, into its folder. The rules are in
`spec/job-application/qualitaetssicherung/en.md` (QS-1 to QS-13). This page says what you can rely on and what you must do
yourself.

```bash
task quality -- pruefen <wurzel>/<slug> --konfiguration job-application/konfiguration.md
```

## What it does and what it does not

| Part | Who | Status |
|---|---|---|
| Rules of the Lebenslauf and the letters (figures, periods, leadership, placeholders), contact data, firm name, copied posting text, filler phrases | the script, repeatable | works |
| Export read-back: hash, source unchanged, wording, order, text extractable, page limit, empty pages | the script (PDF needs `pdftotext` and `pdfinfo` from poppler-utils) | works; without the tools the check is `BLOCKED` |
| Technical ATS check of the exported file (`ATS-01` to `ATS-05`): valid file, fonts, hidden text, headings with their content, periods and stations, contact data, columns, tables, images, ratings shown as symbols | the script (`pdffonts` and `pdfimages` as well), for PDF, DOCX and HTML only | works; without the tools `BLOCKED` |
| Key terms of the analysis in the Lebenslauf (`KW-01`) | the script; it never inserts anything | works |
| Evidence of each statement against the Datengrundlage, responsibility and seniority, relevance, language, consistency | a model writes verdicts (`qualitaet-urteile.json`); the script checks that quote and evidence are literal | **needs a model**; without it the checks are `NEEDS_REVIEW` |
| Confirming an open review | you (`entscheiden … --ja`) | by design not automatic |
| Approving the package and sending it | you | **never done by the toolchain**: no check sends anything or approves anything |

A `PASS` means "nothing found", not "correct". ATS readability is judged on the exported file and its extracted text; how a given
tracking system reads your file is not tested and not promised.

## Technical ATS check

The report has an `ats` block: `umfang` is `vollstaendig`, `teilweise` or `nicht_geprueft`, and `technisch_validiert` is true only for
a complete run without a `FAIL`, `BLOCKED` or open review. It means the defined checks passed. It does not mean a given system reads
the file, and it says nothing about your fit. There is no total score; every check has a `dimension` (`technisch`, `evidenz`,
`formal`, `schluesselbegriffe`, `passung`).

| Check | What it finds | Severity |
|---|---|---|
| `EX-03` | hardly any text, replacement characters, ligature characters, letter-spaced words | Blocker or warning |
| `ATS-01` | broken PDF or DOCX structure, a ban on copying text, hidden, white or tiny text; type 3 or not embedded fonts | Blocker or warning |
| `ATS-02` | a heading not on its own line, content not under its heading, DOCX heading styles unlike the source | warning |
| `ATS-03` | a lost or reordered period; position and employer not next to the period; mixed date formats | Blocker or warning |
| `ATS-04` | an e-mail or phone number of the source that cannot be read (also: only in header or footer); a Lebenslauf without an e-mail | Blocker or warning |
| `ATS-05` | columns, tables, images, text boxes, header or footer text, words off the page; a rating shown only as stars or bars | warning or `NEEDS_REVIEW` |
| `KW-01` | an evidenced competence missing as a term; a term in the Lebenslauf that the analysis does not evidence | warning or `NEEDS_REVIEW` |

`md` and `tex` are copies of the source: without a PDF, DOCX or HTML in `export/` the `ATS-xx` checks are `NOT_APPLICABLE`. A
warning about columns or tables is a risk, not an error. Layout, overlapping elements and pleasant page breaks you look at
yourself; the checks do not replace that. No model is needed.

!!! note "Not yet measured on a real LaTeX PDF"
    The station and column checks for PDF are tested with synthetic PDFs. They have not run on a real LuaLaTeX PDF of the template
    in this environment (LuaLaTeX is missing there). Run `task quality` on your next real PDF and report false alarms.

## Results

Each check ends in `PASS`, `FAIL`, `WARNING`, `NEEDS_REVIEW`, `NOT_APPLICABLE` or `BLOCKED`. The overall result decides whether
the package may be offered for your approval: only `BEREIT`, `BEREIT_MIT_WARNUNGEN` and `BEREIT_NACH_MANUELLER_PRUEFUNG`
(every open review confirmed by you).

The report is bound to the hash of every document and export. Change a file and the report is stale: run the check again. The
workflow task `pruefung` is not done, and the send approval is refused, without a current approvable report. The approval itself
stays yours.

## Where it stops

- The deterministic checks do not read meaning. A wrong sentence without a figure, a date or a name can pass.
- A semantic verdict is only checked for form and literal quotes, not for being right.
- Layout, fonts, tone and the fit to you are for a human; the evals (`evals.md`) are separate and manual.
