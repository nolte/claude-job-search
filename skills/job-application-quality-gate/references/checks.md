# Checks of the quality gate

Loaded by `job-application-quality-gate` in step 2 of its workflow. Every rule names its severity; the verdict words are
`Blocker`, `Warnung`, `Hinweis` (CG-13.1). Severities of `cv_checks.py` are printed by the script; the table repeats them so
the gate can read a run without the script (a sandbox may refuse it).

## Contents

- [Rules of `cv_checks.py` for the Lebenslauf](#rules-of-cv_checkspy-for-the-lebenslauf)
- [Rules of `cv_checks.py` for the letters and the e-mail](#rules-of-cv_checkspy-for-the-letters-and-the-e-mail)
- [Checks of the gate](#checks-of-the-gate)

## Rules of `cv_checks.py` for the Lebenslauf

| Rule | Check | Severity |
|---|---|---|
| CV-01 | Placeholder `[ERGÄNZEN` or `[KLÄREN` left | Blocker |
| CV-02 | Station header not in form `MM/JJJJ – MM/JJJJ \| Position \| Arbeitgeber, Ort`, or a month missing (years only) | Warnung |
| CV-03 | More than 5 bullets, or a station without bullets | Warnung, Hinweis |
| CV-04 | Stations not reverse chronological; end before start; stations at the same employer that overlap by more than a month (F-05) | Warnung, Blocker; Hinweis for the overlap |
| CV-05 | Number or number word in a bullet not in the station record (notation is not compared: `1,5` = `1.5`, `5` = `fünf`; a unit conversion is no match): Hinweis when it is elsewhere in the Grundlage, Blocker when nowhere | Hinweis, Blocker; Warnung when the station holds the number with another unit or noun |
| CV-06 | Station period differs from the Grundlage | Blocker |
| CV-07 | *Muss* row marked *erfüllt* without evidence; *Muss* gap as report | Blocker, Warnung |
| CV-24 | `analyse.md`: *erfüllt* while `Offen` names an aspect the Nachweis does not show (Blocker for *Muss*, Warnung for *Wunsch*); *teilweise* or *unklar* without an entry in `Offen`; a table without the column `Offen` (CG-4.7, CG-4.8) | Blocker, Warnung |
| CV-08 | Table in the Lebenslauf | Warnung (Blocker with `--ats`) |
| CV-09 | Duplicate bullet | Hinweis |
| CV-10 | Heading outside the standard headings (CG-11.2a), qualifier in parentheses allowed | Warnung |
| CV-11 | Generic or evaluative phrase (CG-8.2.3) | Warnung |
| CV-12 | Bullet longer than two lines | Hinweis |
| — | Bullet form not as CG-8.1 (subject, finite verb, final period, list longer than two items) (judged in review) | Warnung |
| CV-13 | Employment gap over two months (time that no station covers) without a neutral entry between the two stations | Blocker |
| CV-14 | Invalid status or strength in the analysis (e.g. `fehlt`) | Warnung |
| CV-15 | Station title or employer not in the Grundlage (note `titel` and `arbeitgeber`, or an R-2.1 header); only the spelling differs: Hinweis | Blocker (Warnung if the Grundlage has no station records), Hinweis for a spelling variant |
| CV-16 | Personnel-leadership wording (`Teamleitung`, `Abteilungsleiter`, `Personalverantwortung`, `disziplinarisch`, `Leitung eines Teams`, `geleitet` with a led Team (also `Entwicklungsteam`), Mitarbeiter or Abteilung, not `mit dem Team geführt`; `gemanagt` or `angeleitet` directly after Team or Mitarbeiter) without `fuehrung: ja` (`nein`, `ungeklärt` or missing; the Grundlage records it as the station note key or the line `Führung: ja`) | Blocker (CG-13.4.3) |
| CV-17 | Sub-bullets below a bullet (R-2.1) | Hinweis |
| CV-18 | Birthdate of a person (`Geburtsdatum`, `geb.`, `geboren` or `*` with a date) in `analyse.md` or a firm file passed with `--firma` (RC-5.3 rule 5, RC-11 rule 4) | Warnung |
| CV-19 | Entry of a list section (skills, languages, certificates, education) that stands nowhere in the Grundlage (spelling variants such as `K8s`/`Kubernetes` are equated, similar names are not), or a number in its parenthesis that stands nowhere; a certificate with a year or status the Grundlage does not give, or shown as current while expired (CG-13.4.6) | Blocker; Warnung for an unrecorded year or status; Hinweis for an expired certificate without status |
| CV-20 | Station used in the Lebenslauf that the Grundlage records with `Bestätigt: nein` (R-9.5 point 5, CG-13.4.8) | Blocker |
| CV-21 | Lebenslauf with nothing but frontmatter and headings | Blocker |
| CV-22 | Wording of ownership, scope or expertise (`eigenverantwortlich`, `gesamte`, `Experte`, …) or a project role (`Projektleitung`) that the station record does not use (CG-7.4, CG-13.4.10) | Warnung |
| CV-23 | Number that the record gives as a team result, in a bullet without a team reference (CG-13.4.11) | Warnung |

## Rules of `cv_checks.py` for the letters and the e-mail

The letters run the same script with `--doc-type`, once per document that exists (`anschreiben.md` and
`anschreiben-portal.txt` as `letter`, `motivationsschreiben.md` and its portal copy as `motivation`, `email.md` and
`email-nachfassen.md` as `email`; CG-13.6):

| Rule | Check | Severity |
|---|---|---|
| BR-01 | Placeholder `[ERGÄNZEN` or `[KLÄREN` left in a letter or the e-mail | Blocker |
| BR-02 | Number in the text (Anrede to Grußformel) that stands nowhere in the Grundlage, the analysis or the posting; Warnung when only the analysis or the posting holds it; Hinweis for an amount with a currency | Blocker, Warnung, Hinweis |
| BR-03 | Experience span (`N Jahre Erfahrung`) that the Grundlage does not state and the station periods do not reach | Blocker |
| BR-04 | Personnel-leadership wording while no station of the Grundlage records `fuehrung: ja` (Hinweis when one does) | Blocker, Hinweis |
| BR-05 | Anschreiben, Motivationsschreiben or E-Mail with nothing but frontmatter and headings | Blocker |

CV-22 and CV-23 ask for the evidence and are a Warnung; a confirmed contradiction (personnel management without
`fuehrung: ja`) is the Blocker CV-16. Whether a statement is stronger than its record in a way the markers do not see stays
in the review. A semantic finding names the statement, quotes the record line that supports the weaker reading, says which
dimension (CG-7.4) is expanded and offers a factual wording; the gate never rewrites the Lebenslauf or the Grundlage. A
Warnung of this kind needs the user's decision before the set is sent, and a Blocker keeps the verdict `BLOCKIERT`.

Checks that need judgement stay in the review: ownership, leadership, expertise and proficiency wording beyond the
markers (CG-7.2, CG-7.4), relevance of selection (CG-5), seniority and role positioning, language and country
conventions, employer instructions, and the requested format.

## Checks of the gate

| Check | Severity when it fails |
|---|---|
| `[ERGÄNZEN` or `[KLÄREN` placeholder left in any document: `lebenslauf.md`, `anschreiben.md`, `anschreiben-portal.txt`, `motivationsschreiben.md`, `email.md` | Blocker |
| Required document missing (Lebenslauf, Anschreiben, Motivationsschreiben if asked for, E-Mail if `email`, `anschreiben-portal.txt` if `portal`, Zeugnisse if requested) | Blocker |
| Motivationsschreiben: a statement of motivation without a source in `## Auswahl Motivationsschreiben` (user statement or confirmed Wunschprofil entry), or `[ERGÄNZEN: Beweggrund]` left (MS-3) | Blocker |
| Motivationsschreiben: a competence without a proof, or text that retells the Lebenslauf (MS-6.1, MS-5.3) | Warnung |
| Company, role, reference number, or contact name differ between documents, or between the documents and `vorgang.md` | Blocker |
| Claim in a document not traceable to the Grundlage entry (R-1, CG-2) | Blocker |
| Muss requirement presented as *erfüllt* without evidence (CV-07) | Blocker |
| Employer instruction that is mandatory and not met (CG-11.6) | Blocker; a recommendation that is not met is a Warnung |
| Requested document format not produced (R-8.4, CG-11.5) | Blocker |
| Export content differs from the approved Markdown (CG-12.2) | Blocker |
| Anstellungsgeber `unbekannt` where a document needs it (UA-6.1) | Blocker |
| Letter addressed to a Vermittler, or naming an Auftraggeber or Anstellungsgeber that the counterpart has not disclosed (KK-4.1, UA-6.2) | Blocker |
| Application to the same Anstellungsgeber or Auftraggeber through two channels without the user's decision (KK-4.2) | Blocker |
| Documents sent to a counterpart the candidate has not approved for it (KK-7.1) | Blocker |
| Company fact in a document that has no source in `analyse.md`, or comes from a rating portal (UA-2.1, UA-4.5) | Blocker |
| `analyse.md` without the classification keys of KK-6, or without the section `## Unternehmen` (UA-5.1) | Warnung |
| Counterpart is a Vermittler with confidence `unklar`, and the Auftraggeber question has not been asked (KK-3.3) | Warnung |
| E-Mail attachment list, or the Anlagen line of the Anschreiben, names a file that is not in the folder (AS-10.4, KK-7.1) | Blocker |
| Anschreiben longer than one page (AS-7.1, AS-12). Page count from `export/…manifest.json` (`ausgabe.seiten`) or `pdfinfo`; the export also exits with code 4 | Blocker; the Anschreiben has no exception |
| Anschreiben outside 250 to 400 words (AS-7.2). Without a PDF this is the only length signal | Hinweis only, never a Blocker |
| Lebenslauf longer than its page limit: two pages, one page for `format: einseitig` (LB-2.3, LB-13). Page count as above | Blocker; with the user's exception recorded under `### Entscheidungen des Nutzers` it stays a Warnung, for every later run |
| Motivationsschreiben longer than the limit of its variant: one page for `stelle`, `quereinstieg` and `berufseinstieg`, two pages for `studium` and `stipendium` (MS-7, MS-12), checked against `ausgabe.seiten`, `ausgabe.seitenlimit` and `ausgabe.seitenlimit_ueberschritten` in the manifest (an export that also differs in content exits with code 2 and still reports the breach there). Exit code 4 of the export for `motivation` means more than two pages | Warnung; no exception rule |
| Attachments in `export/` larger than 5 MB in total (R-4) | Warnung from 5 MB, Blocker from 10 MB |
| Attachment file name not ASCII (`ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`, no spaces) or not `Vorname_Nachname_<Dokument>.pdf` (R-4) | Warnung |
| Betreff of Anschreiben or E-Mail carries a gender suffix such as `(m/w/d)` (AS-4) | Warnung |
| `vorgang.md` missing in a Vorgang folder, or its `status` not one of the LS-6 values | Warnung |
| `status` inconsistent with the documents: `erstellt` or later without `lebenslauf.md`, `geprüft` with open Blocker, `erfasst` or `analysiert` with documents present (LS-6) | Warnung |
| `grundlage_hash` in `vorgang.md`, in a document or in an export differs from the current hash (LS-5.4, R-9.5; the hash comes from `scripts/grundlage_hash.py`), or a document's hash differs from `vorgang.md` | Warnung: stale, re-derive |
| Mixed date formats or inconsistent Zeiträume | Warnung |
| Spelling or grammar errors in German text | Warnung |
| Anrede not matching the Ansprechperson, generic (`Sehr geehrte Damen und Herren`) when a name is known, or not following AS-5.6 to AS-5.8 (Sie default, du form only when the posting uses du, `Guten Tag <Vorname Nachname>` when the gender is not clear, academic title taken over) | Warnung |
| Requirement marked *Muss* in the analysis not addressed in the Anschreiben | Warnung |
| Stock phrase ("hiermit bewerbe ich mich") | Warnung |
| Kurzprofil longer than three sentences, or missing in `kombiniert`; a Kurzprofil outside `kombiniert` without the user's opt-in (LB-4.2) | Warnung |
| Optional personal data present without the user's request | Hinweis |
| `scripts/grundlage_hash.py` stops with a `Blocker:` line (missing `grundlage_index`, missing or invalid `stand`, Grundlage inside the plugin repository) (R-9.5, R-9.9, R-9.10) | Blocker |
| Eintragsblock not in header-line form, or bullets outside 1–5 per station (R-2.1) | Warnung |
| Table or multi-column layout in a CV (R-8.3) | Warnung; Blocker if the posting requires ATS |
| Photo present in an ATS or portal application (R-8.2) | Warnung |
| Europass or academic CV required by the posting but not produced (R-8.4) | Blocker |
| Lebenslauf not matching the format chosen for the situation (R-8.1) | Warnung |
| Missing Ort, Datum, or Unterschrift line where R-2 expects them | Hinweis |
| Date in the closing line of the Lebenslauf more than 30 days before the check date (LB-9.4) | Warnung |
| Motivationsschreiben: a leadership claim without `fuehrung: ja` (MS-6.2, MS-12; the script finds the wording as BR-04, the mapping to the station is review) | Blocker |
| Motivationsschreiben: a wish from the Wunschprofil without the user's confirmation, or a `hypothese: ja` wish (MS-3.3) | Blocker |
| Motivationsschreiben: counterpart fact without source in `analyse.md`, or from a rating portal (MS-3.5) | Blocker |
| Motivationsschreiben or Anschreiben: mandatory counterpart instruction not met (MS-11, CG-11.6) | Blocker |
| Anschreiben or Motivationsschreiben: a wish from the Wunschprofil written into the Anschreiben (AS-6.8, WJ-7.2) | Blocker |
| Salary question to a Vermittler or before the employer is known (KK-4.4); exclusivity question not asked before documents go to a Vermittler (KK-4.6) | Warnung |
| `anschreiben-portal.txt` or `motivationsschreiben-portal.txt` carries letter head, Betreff, Anlagen or Markdown (AS-8.1) | Warnung |
| Invented reference number in the Betreff (AS-4.1) | Warnung |
| Gehaltsvorstellung outside the Schluss (AS-10.1) | Hinweis |
| Skill rating as bars, stars or percentages (LB-7.4) | Warnung |
| List entry not in the form of LB-6.1 | Hinweis |
| Keyword stuffing: a posting term in the Lebenslauf without a proof in the Grundlage; padding with posting terms (R-1.4, CG-4.6) | Blocker without proof; Warnung for padding |
| Export manifest missing for a file in `export/` (LV-3) | Warnung |
| Export file changed after its manifest, or `quelle.sha256` of the manifest differs from the current Markdown (CG-12.2, R-10.3, LV-3.4) | Blocker for the differing source; Warnung for a changed export file |
| Manifest `frontmatter.grundlage_hash` differs from the current hash, or a frozen version in `versionen/` does not match its manifest (LV-3.4, LV-6.4) | Warnung; optionally confirm with `export_document.py --reproduce` |
| PDF without selectable text (CG-11.5, CG-12.4); where LuaLaTeX is not installed this check is *not run* and the report says so | Blocker |
| `## Auswahl …` section missing in `pruefbericht.md` for a generated document (R-9.11.5, CG-2.3) | Warnung |
| Vorgang with a Vermittler and no `## Recherche` in `analyse.md` (RC-11) | Warnung |
| A document names a firm, `## Recherche` exists, and the identity line E-1 is not `ermittelt` (RC-11, RC-6.4) | Blocker. Level 0 alone (no `## Recherche` beyond `Stufe: 0`) never blocks. Warnung instead, when E-1 is open only because the web route was unavailable and the user declined to paste the imprint and register pages, with the decision in `## Verlauf` of `vorgang.md` (RC-11 rule 1) |
| A query in the block `### Suchen` of `## Recherche` keeps a token outside the list of RC-5.5, or contains a token of the contact person's name recorded in `analyse.md`, in what is left after removing the whole phrases of the firm name and of the Sitz as recorded in `## Unternehmen` or the firm file (match on whole words, ignoring case, hyphens, spaces and the legal form GmbH, gGmbH, mbH, AG, SE, KG, UG, e.V., Co.; a firm name that contains a person's name is removed as a phrase, that name alone is left over, so `Beispiel Logistik Impressum` is clean and `Beispiel Impressum` is a Warnung for the firm `Beispiel Logistik GmbH` and the contact `Erika Beispiel`; tokens are split at spaces and slashes, quotation marks are dropped; a list term of several words such as `Engineering Blog` matches as a whole phrase; a search operator such as `site:` is a token outside the list). A leftover token is a Warnung even if it might be an unrecorded Sitz; a firm name that is not recorded makes the query unverifiable and is a Warnung (review of the record, no script) (RC-5.5 rule 3, UA-3.2, RC-9, UA-5) | Warnung |
| A search in `### Suchen` uses an engine outside the allowlist `duckduckgo`, `startpage`, `brave` without the user's wish for `bing` (RC-5.5 rule 5) | Warnung |
| The counts in `Kanäle` (summed over all web entries) exceed the budget of the level (10 searches and 15 page fetches at level 1, 20 and 30 in total at level 2, shared by both levels; the numbers of RC-5.5 rule 6), or `Kanäle` names a web route while `### Suchen` is missing or its rows differ from the count (RC-5.5 rule 6, RC-9 rule 7) | Warnung |
| `analyse.md` or a firm file in `<wurzel>/firmen/` contains a birthdate of a managing director or another person taken from the register: `Geburtsdatum`, `geb.`, or a `*` date next to a name (RC-5.3 rule 5). Personal data of a third party that E-1 does not need; it stays local and is not sent, so it is a Warnung (as a contact person's name in a query, RC-11 rule 3), removed with the user's agreement through the owning skill. Deterministic: `scripts/cv_checks.py` rule CV-18, with `--analyse` and `--firma` (RC-11 rule 4) | Warnung |
| The count in `Kanäle` of `Handelsregister über handelsregister-mcp (1 Abruf)` or `(n Abrufe)` exceeds the budget of the level (4 at level 1, 8 at level 2, shared by both levels; RC-5.3 rule 4), falls below the count of an earlier record of the same Vorgang (`## Verlauf` or an earlier `Kanäle`), or the register entry of `Kanäle` is none of the four forms of RC-9 rule 8 (review of the record, no script) (RC-11 rule 5) | Warnung |
| A document names a firm with `Warnzeichen` (RC-7, RC-8) | Blocker; a Warnung when the user decided against the assessment and the decision stands in `## Verlauf` of `vorgang.md` (RC-8.4) |
