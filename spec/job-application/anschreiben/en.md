# Document type: Anschreiben (EN canonical)

Normative rules for the Anschreiben (cover letter) of one application for one Stellenanzeige. This
document is canonical for the document type: what it is for, what it contains, how it is built, how it
sounds, and how it is checked. It does not repeat rules that other specs own; it refers to them.

Related specs:
- `spec/job-application/konventionen/en.md`: R-1 (facts), R-3 (short form of the letter rules, now
  governed by this document), R-4 (E-Mail), R-6 (data protection), R-9.5 (hash).
- `spec/job-application/cv-generierung/en.md`: CG-4 (requirement-to-evidence rows), CG-7 (controlled
  rewriting), CG-9 (gaps).
- `spec/job-application/kontaktklassifikation/en.md`: KK-4 (disclosure), KK-5 (communication by counterpart).
- `spec/job-application/unternehmensanalyse/en.md`: UA-4.5, UA-6 (company facts and addressee).
- `spec/job-application/motivationsschreiben/en.md`: the separate document type for personal motivation.
- `spec/job-application/lebenslauf/en.md`: the document the Anschreiben accompanies.

Rule IDs `AS-n` name the rules of this document. Each rule states whether it comes from a cited source or is
a decision of this plugin. A decision of this plugin is a default that a posting's instruction overrides
(AS-11).

## AS-1 Purpose and reader

1. **Purpose.** The Anschreiben ties one Stellenanzeige to the candidate's evidence. It answers three
   questions of the reader: why this candidate fits the job, why this employer, and how to continue.
2. **Reader.** The reader is the person who decides on the first selection (HR, a hiring manager, or a
   recruiter, see KK-2). The reader has the Stellenanzeige and the Lebenslauf next to the letter.
3. **Boundary to the Lebenslauf.** The Lebenslauf lists the facts in full. The Anschreiben selects two or
   three of them and states why they matter for this job. It does not list stations one after another.
4. **Boundary to the Motivationsschreiben.** The Anschreiben refers to a concrete job and connects posting
   and Lebenslauf. A text that mainly explains personal reasons and long-term goals is a Motivationsschreiben
   (see `motivationsschreiben/en.md`). Source: [business-on.de](https://www.business-on.de/unterschied-anschreiben-und-motivationsschreiben.html),
   [karriere.at](https://www.karriere.at/c/a/anschreiben).
5. **One posting per letter.** A letter is written for exactly one Stellenanzeige or one deliberate
   unsolicited application (one Vorgang per Stellenanzeige, `lokale-struktur/en.md` LS-1; consistency
   across the set, R-7).

## AS-2 Components and order

The letter has these components in this order. The order follows the DIN 5008 sequence named by the
sources below.

| # | Component | Required | Content |
|---|---|---|---|
| 1 | Absender | yes | Name, address, phone, e-mail of the candidate |
| 2 | Empfängeranschrift | yes | Company, contact person if known, address |
| 3 | Ort und Datum | yes | `Ort, TT.MM.JJJJ` |
| 4 | Betreff | yes | Role and reference number (AS-4) |
| 5 | Anrede | yes | Personal salutation (AS-5) |
| 6 | Text | yes | Opening, proof paragraphs, motivation, closing (AS-6) |
| 7 | Grußformel | yes | `Mit freundlichen Grüßen`, no comma after it |
| 8 | Unterschrift | yes | Full first and last name; a handwritten signature only for paper |
| 9 | Anlagen | when attachments exist | One line naming the attached documents |

Sources: [Karrierebibel, DIN 5008 Bewerbung](https://karrierebibel.de/bewerbung-din-5008/),
[Randstad, Das Anschreiben](https://www.randstad.de/karriere/bewerbungsratgeber/anschreiben-bewerbung/),
[Stellenmarkt, DIN 5008 Bewerbung](https://www.stellenmarkt.de/karrieremagazin/bewerbung-nach-din-5008).
Retrieved 2026-10-22.

## AS-3 Layout

1. **DIN 5008 is a guide, not a legal duty.** DIN 5008 regulates the look and structure, not the content, and
   its use is voluntary (sources of AS-2). The plugin follows it as a convention for German applications.
2. **Page.** A4, one column, no tables, no images, no coloured background.
3. **Margins.** The sources recommend about 25 mm left, 20 mm right, 20 mm top and bottom. They differ on the
   minimum of the right margin (10 mm and 15 mm are named). The template uses 25 mm left, 20 mm right, and
   20 mm top and bottom for the letter (document type `letter`); the Lebenslauf has its own margins.
4. **Typeface.** DIN 5008 does not prescribe one (sources of AS-2). The template font applies (Lato with a
   fallback, body 10.5 pt on 14.3 pt leading as `\normalsize` of
   `skills/job-application-export/templates/document.tex`, the same as LB-11.7).
5. **Form A and Form B.** DIN 5008 defines forms that differ in the position of the address field and the
   fold marks. The sources retrieved for this document do not state them. The plugin therefore does not
   claim to implement a specific form. Open point AS-13.
6. **Betreff.** Written without the word "Betreff", starting two lines below the date; the salutation follows
   two blank lines below it (sources of AS-2). The plugin sets the Betreff in bold (decision of this plugin).
7. **Consistency with the Lebenslauf.** Name, address, phone, e-mail, and the typeface and accent colour of the
   template are the same as in the Lebenslauf, so the documents read as one set (R-1, R-7).

## AS-4 Betreff

1. **Form.** `Bewerbung als <Stelle> (Ref.-Nr. <nr>)`, with the posting's role title and, only when the
   posting gives one, the reference number (decision of this plugin, equal to R-3). A gender suffix of the
   posting (`(m/w/d)`, `(w/m/x)`, `(m/w/x)` and similar) is dropped from the Betreff:
   `Senior Backend-Entwickler (m/w/d)` becomes `Bewerbung als Senior Backend-Entwickler`. Without a reference
   number the parentheses are omitted.
2. **Unsolicited application.** `Initiativbewerbung als <Rolle>` or `Initiativbewerbung im Bereich <Bereich>`.
3. **No extra claims.** The Betreff contains no adjective about the candidate.
4. **Same wording everywhere.** The Betreff matches the subject of the e-mail (R-4) and the role in the
   analysis (R-7).

## AS-5 Anrede and closing

1. **Named contact.** The sources recommend a named contact person. The Sie-Form is the default. The
   salutation is `Sehr geehrte Frau <Nachname>,` or `Sehr geehrter Herr <Nachname>,` when the posting or the
   user's profile gives the name. A name is never guessed (R-1, KK-5.1).
2. **No name known.** The skill asks the user once whether a contact is known. If there is none,
   `Sehr geehrte Damen und Herren,` is allowed. The quality gate reports it as a Warnung, not as a Blocker
   (the same severity as MS-4.3).
3. **Comma rules.** A comma follows the salutation. No comma follows the Grußformel (sources of AS-2).
4. **Grußformel.** `Mit freundlichen Grüßen`. The signature line below carries the full first and last name,
   without abbreviations.
5. **Recruiter or undisclosed employer.** The addressee follows KK-4.1 and UA-6.2: a letter to a Vermittler
   does not name an Auftraggeber the counterpart has not disclosed.
6. **Posting in the du-Form.** When the posting clearly uses du (AS-9.1), the salutation is
   `Hallo <Vorname>,` or `Guten Tag <Vorname Nachname>,`. The user chooses; the default is `Guten Tag`.
7. **Gender not derivable.** When the gender cannot be derived from the name and the posting gives no
   pronoun or title, the salutation is `Guten Tag <Vorname Nachname>,`. The gender is never guessed.
8. **Academic titles.** A title (Dr., Prof.) that the posting or the profile states is kept in the
   salutation: `Sehr geehrte Frau Dr. <Nachname>,`, `Sehr geehrter Herr Prof. <Nachname>,`. A title is never
   added from another source (AS-9.7).

## AS-6 Text: structure and content

The text has four parts. The proportions are a default of this plugin.

| Part | Purpose | Default share |
|---|---|---|
| Einstieg | A concrete reference to the company or the role, and the reason for the application in one or two sentences | about 15 % |
| Nachweisabsätze | Two or three paragraphs, each pairing one requirement with one proof | about 55 % |
| Motivation | Why this employer, from facts of the posting or of public company statements | about 15 % |
| Schluss | A wish for a conversation, optionally the earliest start date | about 15 % |

1. **Einstieg.** It starts with a concrete reference. The phrase "hiermit bewerbe ich mich" and other stock
   openings are not used (AS-9).
2. **Nachweisabsatz.** Each paragraph names one requirement of the posting and one proof from the
   Grundlage, with the scope and, when the Grundlage states it, the result. The paragraph is built from
   an analysis row (CG-4) with status `erfüllt` and strength `mittel` or `stark`.
3. **Selection.** The two or three *Muss* requirements with the strongest evidence are chosen. A requirement
   with weak or no evidence is not turned into a paragraph.
4. **No repetition.** A proof paragraph adds the reason why the fact matters for the job. It does not repeat
   a Lebenslauf bullet in the same words.
5. **Consistency.** Every date, number, employer, title, and technology in the letter appears unchanged in the
   Lebenslauf and in the Grundlage (R-1, CV-05, CV-06).
6. **Motivation.** A company fact in the motivation part comes from the posting or a public company statement,
   and the analysis names its source (UA-4.5). A rating-portal statement is not used (UA-2.1). If the posting
   gives no usable fact, the marker `[ERGÄNZEN: konkreter Bezug zum Unternehmen]` stays (R-1).
7. **Gaps.** A *Muss* requirement with status `nicht belegt` or `teilweise` can be addressed in one sentence
   that states the related evidence and the willingness to learn, without claiming the competence (CG-4.5).
   The sentence is optional and the user decides.
8. **No wishes.** The letter states facts and evidence. It does not state the candidate's wishes from the
   Wunschprofil (WJ-7.2).
9. **Schluss.** The wish for a conversation is concrete and short. An earliest start date or a notice period
   appears only when the user states it.

## AS-7 Length and form

1. **One page.** The letter fits on one A4 page (decision of this plugin). A comparison source gives one
   page as the usual length of an Anschreiben, and one to two pages for a Motivationsschreiben
   ([Kickresume](https://www.kickresume.com/de/blog/motivation-letter-vs-cover-letter/)). Other sources allow
   up to two pages; this plugin sets one page.
2. **Word count.** About 250 to 400 words for the text part (decision of this plugin). The count is an aid. The
   page limit decides.
3. **Paragraphs.** Two to five short paragraphs. A paragraph has at most six lines.
4. **Cut order.** When the letter is too long, cut in this order: the optional gap sentence, the weakest proof
   paragraph, then sentences of the Einstieg. The Betreff, the salutation, and the Grußformel are never cut.

## AS-8 Variants

The variant is the `ausrichtung` input of `job-application-cover-letter-create`.

| Variant | When | Difference |
|---|---|---|
| `ausschreibung` | A Stellenanzeige exists | Full structure of AS-6 |
| `initiativ` | No posting | The Betreff names the area. The Einstieg names the target area and the reason for the choice. The proof paragraphs name two or three proven strengths. The letter says what the company gets, not only what the candidate wants |
| `quereinstieg` | Change of field | The first proof paragraph leads with transferable evidence mapped to the requirements. One sentence states the motivation for the change, without apology and without disguising the employment history (CG-3.2) |
| `berufseinstieg` | Entry level | The proof paragraphs lead with education, training, projects, and internships from the Grundlage |
| `vermittler` | A recruiter forwards the letter | The addressee and the content follow KK-4 and UA-6.2. The employer is named only after disclosure |

A letter that mainly explains personal reasons and goals is written as a Motivationsschreiben, not as a
variant of this document.

### AS-8.1 Portal free-text fields

1. **Trigger.** `bewerbungsweg: portal` in `vorgang.md` (LS-6.1) and a portal that offers a free-text field
   for the cover letter instead of an upload.
2. **Content.** The letter is written as in AS-6 and then reduced to plain text for the field: no
   Absender, no Empfängeranschrift, no Ort und Datum, no Betreff, no Anlagen line. The text runs from the
   Anrede (AS-5) to the Grußformel and the name (AS-5.4). Paragraphs are separated by one empty line; no
   Markdown, no bold, no list markers.
3. **Length.** The field limit of the portal, when known, replaces the page limit of AS-7.1. The analysis
   records the limit; the cut order of AS-7.4 applies. Without a known limit the text of a one-page letter
   is used.
4. **File.** The plain text is written to `anschreiben-portal.txt` next to `anschreiben.md` whenever the
   portal route has a free-text field (item 1). Otherwise it is written only on the user's request.
   `anschreiben.md` stays the source (R-10.1); both carry the same facts (AS-6.5).
5. **Motivation fields.** A portal field that asks for motivation follows the same reduction with the
   content rules of `motivationsschreiben/en.md` (MS-2.3).

## AS-9 Wording and tone

1. **Address.** Sie, unless the posting clearly uses du (R-3). The tone follows the posting's tone recorded in
   the analysis.
2. **Voice.** First person, active, plain verbs. The letter does not start every sentence with "Ich".
3. **Stock phrases.** These are not used: "hiermit bewerbe ich mich", "mit großem Interesse habe ich", "ich bin
   teamfähig und belastbar", "ich freue mich über eine Einladung" as the only closing. The quality gate
   reports a stock phrase as a Warnung (existing check).
4. **Evaluations.** No unsourced evaluation of the candidate ("erfolgreich", "innovativ", "motiviert"). A
   quality is shown by a proof (CG-8.2).
5. **Keywords.** A term of the posting is used only where the Grundlage supports it (R-1.4, CG-4.6).
6. **Language.** German. Original wording in another language stays unchanged and is marked (R-9, rule 2).
7. **Gender-neutral wording** of the addressee follows the posting. The letter does not invent a title.

## AS-10 Salary, start date, and further statements

1. **Gehaltsvorstellung.** Only if the posting asks for it, and only with a value the user states (R-3).
   Form: `<Betrag> € brutto pro Jahr` (`65.000 € brutto pro Jahr`) or a range (`60.000 bis 65.000 € brutto
   pro Jahr`). It stands in the Schluss (AS-6, Schluss), in one sentence. Without a value from the user the
   marker `[ERGÄNZEN: Gehaltsvorstellung]` stays (Blocker, R-1.2). A recruiter who asks before the employer
   is known gets no salary yet (KK-4.4).
2. **Eintrittstermin and Kündigungsfrist.** Only if the posting asks for it or the user wants it. The value
   comes from the user.
3. **Personal data.** No birth date, marital status, or photo reference in the letter (R-2, R-8.2).
4. **Anlagen line.** It names only documents that exist in the folder and that the counterpart may receive
   (KK-7.1). Example: `Anlagen: Lebenslauf, Zeugnisse`. The Zeugnisse are one combined PDF selected and
   ordered as R-5 states (the last two or three Arbeitszeugnisse, the highest Abschluss, relevant
   Zertifikate; Arbeitszeugnisse, then Abschlusszeugnisse, then Zertifikate, newest first within a group).
   The line lists the attached documents, not the single certificates.

## AS-11 Overrides by the posting

An explicit instruction of the Stellenanzeige overrides the defaults of this document where it asks for a
format, a length, a file type, a language, or a content item. The analysis records the instruction, and the
quality gate checks it (CG-11.6). A mandatory instruction that is not met is a Blocker; a recommendation that is
not met is a Warnung.

## AS-12 Quality checks

| Check | Source rule | Kind | Severity |
|---|---|---|---|
| Placeholder `[ERGÄNZEN` or `[KLÄREN` left | R-1, AS-6.6 | automated (BR-01, CG-13.6) | Blocker |
| Addressee, Betreff, reference number and contact name equal across the documents | AS-4.4 | review | Blocker |
| A claim not traceable to the Grundlage | R-1, AS-6.5 | numbers, experience spans and leadership wording automated (BR-02 to BR-04, CG-13.6); the rest review | Blocker |
| Number, date, or employer differs from the Lebenslauf | AS-6.5 | review | Blocker |
| Letter longer than one page | AS-7.1 | export page check (`doc-type letter`, exit code 4); no exception | Blocker |
| Letter outside 250 to 400 words (also when no PDF exists) | AS-7.2 | review | Hinweis, never a Blocker |
| A *Muss* requirement of the analysis is not addressed | AS-6.3 | review | Warnung |
| A *Muss* gap is presented as fulfilled | CG-4.5 | review | Blocker |
| Stock phrase | AS-9.3 | review | Warnung |
| Generic salutation `Sehr geehrte Damen und Herren,` | AS-5.2 | review | Warnung |
| Salutation form does not match the case of AS-5 (du-Form, gender not derivable, title) | AS-5.6 to AS-5.8 | review | Warnung |
| Gender suffix or an invented reference number in the Betreff | AS-4.1 | review | Warnung |
| Gehaltsvorstellung without a user value, or outside the Schluss | AS-10.1 | review | Blocker (placeholder), Hinweis (placement) |
| Employer or Auftraggeber named without disclosure | AS-5.5 | review | Blocker |
| Portal text carries letter head, Betreff or Markdown | AS-8.1 | review | Warnung |
| `grundlage_hash` stale (R-9.5) | R-9.5 | automated | Warnung |
| Anlagen line names a file that does not exist in the folder | AS-10.4 | review | Blocker |
| Export manifest missing for an exported file | R-10.3 | review | Warnung |
| Export file changed after its manifest was written | CG-12.5 | review | Warnung |
| Manifest source hash differs from the current `anschreiben.md` (stale export) | CG-12.2 | review | Blocker |
| PDF without extractable text | CG-12.4 | export check | Blocker |
| `## Auswahl Anschreiben` missing in `pruefbericht.md` | CG-2.3, R-9.11.5 | review | Warnung |
| Keyword stuffing: a posting term without evidence, or padding with supported terms | R-1.4, CG-4.6 | review | Blocker (without evidence), Warnung (padding) |

The page limit of one page is the only automated length check today (`export_document.py`, `PAGE_LIMITS`;
the export reports exit code 4, R-10.10, and the quality gate sets the Blocker). The page-limit exception of
the Lebenslauf (LB-2.3) does not apply to the Anschreiben.
Word count, stock phrases, and consistency between the documents are judged in review (AS-13).

## AS-13 Open points

| Area | Point | Status |
|---|---|---|
| DIN 5008 | Form A or Form B, the exact position of the address field, and fold marks are not verified. A primary source (the standard text or DIN Media) is needed before the template claims a form | open |
| Margins | The letter has its own geometry (25 mm left, 20 mm right). It follows the recommendation of the sources, which differ on the minimum of the right margin | done |
| Automation | Deterministic checks for word count, stock phrases, and salutation, in `scripts/` | open |
| Skill | `job-application-cover-letter-create` implements AS-6 to AS-9 only as far as its `SKILL.md` states them; the skill must be aligned with this document | done (skill) |
| Page limit | The export reports a second page with exit code 4 (R-10.10); the quality gate sets the severity Blocker (AS-12) | done (Exit 4) |
| Portal fields | AS-8.1 defines the plain-text reduction; `job-application-cover-letter-create` writes `anschreiben-portal.txt` for `bewerbungsweg: portal` | done (skill, 0.2.0) |
| Versioning | Anschreiben and Motivationsschreiben are not versioned like the Lebenslauf (`lebenslauf-versionen` LV-9) | open |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |

## AS-14 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| AS-A | Posting with a named contact | Personal salutation, Betreff with reference number, one page |
| AS-B | Posting without a contact | The skill asks once; generic salutation only if none is known, reported as Warnung |
| AS-I | Posting in the du-Form with a named contact | `Hallo <Vorname>,` or `Guten Tag <Vorname Nachname>,` (AS-5.6) |
| AS-J | Contact name without a derivable gender | `Guten Tag <Vorname Nachname>,` (AS-5.7) |
| AS-K | Contact with the title Dr. in the posting | `Sehr geehrte Frau Dr. <Nachname>,` (AS-5.8) |
| AS-L | Role title `… (m/w/d)` and no reference number | `Bewerbung als <Stelle>` without suffix and without parentheses (AS-4.1) |
| AS-M | `bewerbungsweg: portal` with a free-text field | Plain text from Anrede to name, within the field limit (AS-8.1) |
| AS-C | Posting with five *Muss* requirements, three well evidenced | Three proof paragraphs for the three, the others in the gap sentence or not at all |
| AS-D | A *Muss* requirement is `nicht belegt` | Never stated as fulfilled; optional gap sentence; reported in the analysis |
| AS-E | Posting asks for the Gehaltsvorstellung | The user's value is stated; without a value the marker `[ERGÄNZEN: Gehaltsvorstellung]` stays |
| AS-F | Recruiter forwards, employer undisclosed | No employer name, addressee per KK-4.1 |
| AS-G | The letter exceeds one page | Blocker (AS-12); the cut order of AS-7.4 applies before the set is ready |
| AS-H | Unsolicited application | Variant `initiativ`; no reference number |

## AS-15 Sources

All retrieved 2026-10-22. They are ratgeber and portal pages (secondary sources). Where they disagree, this
document says so and records a decision of this plugin.

- [Karrierebibel, DIN 5008 Bewerbung: Die wichtigsten Regeln](https://karrierebibel.de/bewerbung-din-5008/)
- [Randstad, Das Anschreiben](https://www.randstad.de/karriere/bewerbungsratgeber/anschreiben-bewerbung/)
- [Stellenmarkt, DIN 5008 Bewerbung: Richtlinien und Formatierungstipps](https://www.stellenmarkt.de/karrieremagazin/bewerbung-nach-din-5008)
- [aubi-plus, DIN-Norm 5008](https://www.aubi-plus.de/bewerbung/din-norm/)
- [Kickresume, Motivation letter vs cover letter](https://www.kickresume.com/de/blog/motivation-letter-vs-cover-letter/)
- [business-on.de, Unterschied Anschreiben und Motivationsschreiben](https://www.business-on.de/unterschied-anschreiben-und-motivationsschreiben.html)
- [karriere.at, Anschreiben](https://www.karriere.at/c/a/anschreiben)
