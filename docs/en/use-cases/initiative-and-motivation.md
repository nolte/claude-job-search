# Initiative application and Motivationsschreiben

**Goal:** apply without a posting, or write the text a programme asks for: your reasons and
goals.

## Initiative application

**Example:** You would like to work at Beispiel AG, which has no open role that fits.

```text
/job-application:job-application-cover-letter-create
```

Choose the variant `initiativ`. Without a posting there is no requirement list and no reference
number. The subject reads "Initiativbewerbung als <role>" or "Initiativbewerbung im Bereich
<area>", the opening names
the area and your reason for choosing it, and the proof paragraphs name two or three proven
strengths. The letter also says what the company gets, not only what you want. Facts about the
company need a source. The Lebenslauf is created as usual with `job-application-cv-create`, and the
quality gate checks the set.

Called directly, the skill writes `anschreiben.md` into the folder `<wurzel>/<slug>/`. The
posting analysis (`analyse.md`) is optional for this variant. The status and history in
`vorgang.md` are updated only if that folder already holds a `vorgang.md`; otherwise create the
Vorgang first, so that the application is tracked like any other.

## Motivationsschreiben for a role, a degree or a scholarship

**Example:** A Stipendium of the fictional Beispiel-Stiftung asks for a Motivationsschreiben.

```text
/job-application:job-application-motivation-letter-create
```

The variants are `stelle` (default), `studium`, `stipendium`, `quereinstieg` and
`berufseinstieg`. The text consists of **your** reasons and goals in your own words plus two or
three proofs from the Datengrundlage. The skill asks you for the reasons and never invents them:

```text
Warum dieses Stipendium? Was wollen Sie in drei Jahren erreicht haben?
```

Answer in rough sentences; the skill shapes them and marks the provenance of each part in a note.
The result is `motivationsschreiben.md`. When a portal has a free-text field, a plain-text copy
`motivationsschreiben-portal.txt` is possible.

## Cover letter or Motivationsschreiben?

| Text | Focus | Use when |
|---|---|---|
| Anschreiben | requirements of the posting and proofs from your career | the usual application |
| Motivationsschreiben | why you want this and where you are heading | the posting or programme asks for it; scholarship; degree |

Both can be part of one application if the posting asks for them.

## What remains

`anschreiben.md` or `motivationsschreiben.md`, the quality gate result in `pruefbericht.md` and
the entries in `vorgang.md`.
