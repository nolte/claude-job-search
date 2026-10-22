---
name: job-application-cover-letter-create
description: "Writes a German Anschreiben (cover letter) for one Stellenanzeige in DIN-5008-style layout, maximum one page, with requirement-to-proof paragraphs taken from the Datengrundlage via <wurzel>/profil.md and the posting analysis. Supports the variants ausschreibung, initiativ, quereinstieg, berufseinstieg and vermittler. Writes Markdown to <wurzel>/<slug>/anschreiben.md and, for a portal application, a plain-text copy. Use on \"schreib ein Anschreiben\", \"Initiativbewerbung schreiben\", or equivalent German requests. Don't use for a Motivationsschreiben (job-application-motivation-letter-create), for the CV (job-application-cv-create), the E-Mail (job-application-email-create), or the review of finished documents (job-application-quality-gate)."
tags: [bewerbung, anschreiben, deutsch, din-5008]
phase: create
summary: "Writes a one-page German cover letter that maps the posting's requirements to proven experience from the profile."
summary_de: "Schreibt ein einseitiges deutsches Anschreiben, das die Anforderungen der Stelle mit belegter Erfahrung aus dem Profil verbindet."
use_when:
  - "you need a cover letter for a specific posting"
  - "you want an unsolicited application (Initiativbewerbung) letter"
  - "you are changing careers or starting out and need a tailored letter"
dont_use_when:
  - situation: "The posting or programme asks for a Motivationsschreiben"
    alternative: job-application-motivation-letter-create
  - situation: "You need the CV"
    alternative: job-application-cv-create
  - situation: "You need the text for the sending e-mail"
    alternative: job-application-email-create
see_also:
  - job-application-motivation-letter-create
  - job-application-posting-analysis
  - job-application-cv-create
  - job-application-email-create
  - job-application-quality-gate
---

# Bewerbung Anschreiben erstellen

Spec: `spec/job-application/anschreiben/en.md` (AS-1 to AS-12) and `spec/job-application/konventionen/en.md` R-1 (facts), R-3
(letter form, length, tone), R-7 (quality gate). A text that mainly explains personal reasons and goals is a
Motivationsschreiben: use `job-application-motivation-letter-create` (AS-1.4). Addressee and disclosure: `spec/job-application/kontaktklassifikation/en.md`
KK-4.1 and KK-5; company facts and their sources: `spec/job-application/unternehmensanalyse/en.md` UA-4.5 and UA-6.
Paths and status: `spec/job-application/lokale-struktur/en.md` LS-2.6, LS-6.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`),
`grundlage` and `grundlage_index` from its frontmatter. Relative paths resolve against the working directory that
contains `job-application/konfiguration.md` (LS-2.6). `<wurzel>/<slug>/` is the Vorgang folder.

## Inputs

- `<wurzel>/profil.md` (required) and the Datengrundlage (Grundlage, key `grundlage`). Every proof in a paragraph is a
  Grundlage entry, reached through the profile; the `Nachweis` cell of the analysis names it (AS-6.2).
- `<wurzel>/<slug>/analyse.md` (required for `ausschreibung` and `vermittler`; optional otherwise): Stammdaten,
  Ansprechperson, tone, `kontaktart`, `auftraggeber`, the section `## Unternehmen`, the requirement rows (CG-4).
- `<wurzel>/<slug>/lebenslauf.md` (required when it exists): the letter names the same stations, dates and numbers.
- `ausrichtung`: `ausschreibung` (default), `initiativ`, `quereinstieg`, `berufseinstieg`, `vermittler` (AS-8).
- `bewerbungsweg` from `analyse.md` or `vorgang.md`: `portal` adds the plain-text copy (AS-8.1).

## Output

`<wurzel>/<slug>/anschreiben.md`:

```markdown
---
grundlage_hash: <current hash of the Grundlage>
format: anschreiben
variante: ausschreibung | initiativ | quereinstieg | berufseinstieg | vermittler
---

**Vorname Nachname**
Straße Hausnummer, PLZ Ort
Telefon · E-Mail

Firma GmbH
<Ansprechperson, if known>
Straße Hausnummer, PLZ Ort

Ort, TT.MM.JJJJ

**Bewerbung als <Stelle> (Ref.-Nr. <nr>)**

Sehr geehrte Frau <Nachname>,

<Einstieg: concrete reference to the company or role>

<Absatz 1: requirement → proof from the Grundlage>

<Absatz 2: requirement → proof from the Grundlage>

<Absatz 3: motivation specific to this employer, only with facts from the analysis>

<Schluss: wish for a conversation; earliest start date and Gehaltsvorstellung only when asked, AS-10>

Mit freundlichen Grüßen

Vorname Nachname

Anlagen: Lebenslauf, Zeugnisse
```

Everything in `<…>` is an instruction for the writer and never appears in the letter. The Anlagen line names only
documents that exist in the folder and that the counterpart may receive (AS-10.4, KK-7.1); the Zeugnisse are one
combined PDF `Vorname_Nachname_Zeugnisse.pdf` (R-5).

For `bewerbungsweg: portal`, write in addition `<wurzel>/<slug>/anschreiben-portal.txt` (AS-8.1): plain text, no
frontmatter, no Absender block, no Empfängeranschrift, no date, starting with the Anrede and ending with the name. Same
wording as the letter. If the portal states a character limit, cut in the order of AS-7.4 and report the count.

## Workflow

1. **Stammdaten from the analysis.** Take Firma, Stelle, reference number, Ansprechperson and tone from `analyse.md`.
   - **Betreff** (AS-4, D7): `Bewerbung als <Stelle> (Ref.-Nr. <nr>)`. Use the posting's role title without a gender
     suffix such as `(m/w/d)`, `(w/m/d)`, `(all genders)`; the suffix stays in `analyse.md` and `stellenanzeige.md`.
     `(Ref.-Nr. <nr>)` only when the posting gives one. `initiativ`: `Initiativbewerbung als <Rolle>` or
     `Initiativbewerbung im Bereich <Bereich>`.
   - **Ansprechperson** (AS-5.2): if the analysis names none, ask the user once whether a contact is known. Never guess a
     name.
   - **Addressee** is the Anstellungsgeber from the section `## Unternehmen` of `analyse.md` (UA-6.1). If it is
     `unbekannt`, stop: do not write a firm name, and report that the letter needs it.
   - **Vermittler.** If `kontaktart` is a Vermittler class and `auftraggeber` is unknown or not disclosed, the letter is
     not addressed to the Vermittler, and it does not name the Auftraggeber. Stop and ask the user for the disclosure
     (KK-4.1, UA-6.2). The letter may name the employer only after it has been disclosed.
2. **Anrede** (AS-5, AS-5.6 to AS-5.8, D6). Sie is the default. With a known person: `Sehr geehrte Frau <Nachname>,` or
   `Sehr geehrter Herr <Nachname>,`; an academic title (`Dr.`, `Prof.`) is taken over as the posting writes it. When
   the posting uses du: `Hallo <Vorname>,` or `Guten Tag <Vorname Nachname>,`. When the gender of the person is not
   clear from the posting: `Guten Tag <Vorname Nachname>,`. `Sehr geehrte Damen und Herren,` only when no person is
   known after the question in step 1; the quality gate reports it as a Warnung.
3. **Proof paragraphs** (AS-6.2, AS-6.3). Take the *Muss* rows with status `erfüllt` and strength `mittel` or `stark`,
   strongest first. Each paragraph pairs one requirement with one proof: the Grundlage entry named in the `Nachweis`
   cell, with its scope and, when the Grundlage states it, its result, and the reason why it matters for this job.
   Two or three paragraphs. If fewer than two rows qualify: one proof paragraph plus the optional gap sentence
   (AS-6.7); never pad with weak evidence or general statements.
4. **Einstieg and motivation** from the posting's own facts and the sourced facts of `## Unternehmen` (UA-4.5). If
   there are none, leave `[ERGÄNZEN: konkreter Bezug zum Unternehmen]`.
5. **Schluss** (AS-6.9, AS-10). A short, concrete wish for a conversation. An earliest start date only when the user
   states it. **Gehaltsvorstellung** (D18) only when the posting asks for it: `<Betrag> € brutto pro Jahr` or a range,
   with the value the user states in the session; if the posting asks and the user gives no value, write
   `[ERGÄNZEN: Gehaltsvorstellung]`. A Vermittler gets no salary before the employer is known (KK-4.4).
6. **Tone.** Sie or du as recorded in the analysis (AS-9.1). First person, active, no stock phrases (AS-9.3), no
   unsourced evaluation (AS-9.4).
7. **Length.** One page (AS-7.1), about 250 to 400 words (AS-7.2). When too long, cut in the order of AS-7.4: the optional
   gap sentence, the weakest proof paragraph, then sentences of the Einstieg. More than one page is a Blocker for the
   quality gate (D4).
8. **Frontmatter.** `grundlage_hash` is the `hash` value of
   `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md` (R-9.5); `<plugin-root>` is the
   plugin directory, two levels above this skill's base directory. A stale hash is a Warnung for the quality gate.
9. **Auswahl Anschreiben.** Write the section `## Auswahl Anschreiben` in `<wurzel>/<slug>/pruefbericht.md`: one line
   per paragraph with the analysis row it answers (requirement, status, strength) and the Grundlage entry (file and
   heading, CG-2.3); for the Einstieg and the motivation the source named in `analyse.md` (UA-4.5); for the Anrede the
   source of the name. Create the file if it is missing. A re-run replaces only this section and leaves the other
   sections (`## Auswahl Lebenslauf`, `## Auswahl Motivationsschreiben`, `## Prüfung`) unchanged (D9).
10. **Status.** If the folder holds `vorgang.md` (LS-6.1), set `status: erstellt` and `grundlage_hash`, and append
    `- JJJJ-MM-TT: <alter Status> → erstellt, job-application-cover-letter-create` to `## Verlauf`.
11. **Hand over.** Show the letter, the open markers and the Auswahl section. Name the next step:
    `job-application-quality-gate`.

## Variants (AS-8)

- **initiativ:** no posting. The Betreff names the area. Name the target area and two or three proven strengths
  from the Grundlage. Say what the company gets, not only what the candidate wants.
- **quereinstieg:** lead with transferable evidence that maps to the requirements. State the motivation for the change
  in one sentence, in the user's words, asked in the session; otherwise `[ERGÄNZEN: Grund des Wechsels]`. No apology,
  no disguised employment history (CG-3.2).
- **berufseinstieg:** lead with the degree or training, relevant projects, and internships, all from the Grundlage.
- **vermittler:** a recruiter forwards the letter. The addressee and the content follow KK-4 and UA-6.2: the employer
  is named only after disclosure, no salary before the employer is known (KK-4.4), the exclusivity question is asked
  before the letter goes out (KK-4.6).

## Hard rules

1. **Never use the phrase "hiermit bewerbe ich mich"** or other stock openings (AS-9.3).
2. **Every claim maps to the Grundlage.** Anything not in the Grundlage, through the profile, is not in the letter.
   Dates, numbers, employers and titles equal the Lebenslauf (AS-6.5).
3. **One page maximum.** Cut in the order of AS-7.4.
4. **Gehaltsvorstellung only if requested** by the posting, with the user's value (AS-10.1).
5. **Motivation sources only.** A company fact in the letter comes from the posting or from a public company statement,
   and `analyse.md` names its source (UA-4.5). A rating-portal statement is never used (UA-2.1).
6. **Disclosure first.** The letter names an employer the candidate has not agreed to disclose to the counterpart
   only if the candidate has decided to (KK-4.1).
7. **Betreff without gender suffix**, identical in the e-mail subject and the analysis (AS-4.4).
8. **Only the Wurzel is written** (LS-5.7): the Vorgang folder, `pruefbericht.md` and `vorgang.md` of this Vorgang.
