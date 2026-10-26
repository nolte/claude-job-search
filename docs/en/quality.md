# Quality assurance

`scripts/qualitaet.py` checks one Vorgang and writes one report, `qualitaet.json`, into its folder. The rules are in
`spec/job-application/qualitaetssicherung/en.md` (QS-1 to QS-12). This page says what you can rely on and what you must do
yourself.

```bash
task quality -- pruefen <wurzel>/<slug> --konfiguration job-application/konfiguration.md
```

## What it does and what it does not

| Part | Who | Status |
|---|---|---|
| Rules of the Lebenslauf and the letters (figures, periods, leadership, placeholders), contact data, firm name, copied posting text, filler phrases | the script, repeatable | works |
| Export read-back: hash, source unchanged, wording, order, text extractable, page limit, empty pages | the script (PDF needs `pdftotext` and `pdfinfo` from poppler-utils) | works; without the tools the check is `BLOCKED` |
| Evidence of each statement against the Datengrundlage, responsibility and seniority, relevance, language, consistency | a model writes verdicts (`qualitaet-urteile.json`); the script checks that quote and evidence are literal | **needs a model**; without it the checks are `NEEDS_REVIEW` |
| Confirming an open review | you (`entscheiden … --ja`) | by design not automatic |
| Approving the package and sending it | you | **never done by the toolchain**: no check sends anything or approves anything |

A `PASS` means "nothing found", not "correct". ATS readability is judged on the extracted text; how a given tracking system
reads your file is not tested and not promised.

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
