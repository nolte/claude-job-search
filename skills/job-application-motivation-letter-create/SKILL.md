---
name: job-application-motivation-letter-create
description: "Writes a German Motivationsschreiben for one posting, programme, or scholarship: the candidate's reasons and goals in their own words, plus two or three proofs from the Datengrundlage. Asks the user for the reasons and never invents them. Writes Markdown to job-application/<slug>/motivationsschreiben.md. Use on \"schreib ein Motivationsschreiben\", \"Motivationsbrief für das Stipendium\", \"Begründung meiner Motivation für diese Stelle\", or equivalent German requests. Don't use for the normal Anschreiben (job-application-cover-letter-create), for the Lebenslauf (job-application-cv-create), or when the posting does not ask for a Motivationsschreiben."
tags: [bewerbung, motivationsschreiben, stipendium, studium, deutsch]
phase: create
summary: "Writes a Motivationsschreiben from the user's own stated reasons and sourced proofs, with a provenance note per statement."
summary_de: "Schreibt ein Motivationsschreiben aus den vom Nutzer genannten Beweggründen und belegten Nachweisen, mit Herkunftsnachweis je Aussage."
use_when:
  - "the posting, the university, or the funder asks for a Motivationsschreiben"
  - "you want to explain personal reasons and goals for an application"
dont_use_when:
  - situation: "You need the normal cover letter for a Stellenanzeige"
    alternative: job-application-cover-letter-create
  - situation: "You need the Lebenslauf"
    alternative: job-application-cv-create
see_also:
  - job-application-cover-letter-create
  - job-application-posting-analysis
  - job-application-traumjob-interview
  - job-application-fit-check
  - job-application-quality-gate
---

# Bewerbung Motivationsschreiben erstellen

Spec: `spec/job-application/motivationsschreiben/en.md` (MS-1 to MS-12). Layout and shared rules:
`spec/job-application/anschreiben/en.md` (AS-2, AS-3, AS-5, AS-9). Facts: `spec/job-application/konventionen/en.md`
R-1. A Motivationsschreiben is a separate document type. It explains the reasons and goals of the
candidate. The normal Anschreiben pairs requirements with proofs.

## Inputs

- `job-application/profil.md` and the Datengrundlage (path from `job-application/konfiguration.md`). Facts come
  from the Grundlage only (MS-3).
- `job-application/<slug>/analyse.md`, including the section `## Unternehmen` and the counterpart keys. If it is
  missing, run `job-application-posting-analysis` first.
- `variante`: `stelle` (default), `studium`, `stipendium`, `quereinstieg`, `berufseinstieg` (MS-8).
- The counterpart's own rules, if any: length, language, structure, questions (MS-11). Ask for them.
- The user's statements of motivation, collected in this session (Step 3).
- `<wurzel>/wunschprofil.md` with `bestaetigt: ja`, optional (MS-3.3).

## Output

`job-application/<slug>/motivationsschreiben.md`:

```markdown
---
dokumenttyp: motivationsschreiben
variante: stelle | studium | stipendium | quereinstieg | berufseinstieg
grundlage_hash: <current hash of the Grundlage>
---

**Vorname Nachname**
Straße Hausnummer, PLZ Ort
Telefon · E-Mail

<Empfänger: Institution, Ansprechperson if known>
<Straße Hausnummer, PLZ Ort>

Ort, TT.MM.JJJJ

**Motivationsschreiben: <Stelle, Programm oder Stipendium> (Ref.-Nr. <nr>)**

Sehr geehrte Frau <Nachname>,

<Einstieg: the target and the central reason>

<Beweggründe: the candidate's reasons, tied to facts of the counterpart>

<Qualifikation: two or three proofs from the Grundlage>

<Persönliche Kompetenzen und Ziele: goals in the user's words, each competence with a proof>

<Schluss: wish for a conversation, optional earliest start date>

Mit freundlichen Grüßen

Vorname Nachname

Anlagen: <existing documents>
```

The provenance note goes into `job-application/<slug>/pruefbericht.md` as the section `## Auswahl Motivationsschreiben`
(Step 6).

## Workflow

1. **Check the document type** (MS-2). Confirm that the posting, the programme, or the user asks for a
   Motivationsschreiben. If only an Anschreiben is asked for, stop and point to
   `job-application-cover-letter-create`. If both are asked for, this skill writes the Motivationsschreiben after
   the Anschreiben exists (MS-9.1). If it is unclear, ask once and record the answer in the analysis.
2. **Collect the counterpart's rules** (MS-11): length, language, structure, and the questions it asks. A
   prescribed rule replaces the default of this skill. Record it in `analyse.md`.
3. **Collect the reasons from the user** (MS-3). Ask, one part at a time and at most three questions per round:
   - Beweggründe: why this organisation, programme, or field, and what made the user choose it;
   - Qualifikation: which two or three experiences the user wants to point to;
   - Ziele: where the user wants to go, and how this step helps.
   Record each answer in the user's words. Do not suggest an answer and do not ask a leading question. A part
   without an answer stays open as `[ERGÄNZEN: Beweggrund]` (MS-3.4).
4. **Use the Wunschprofil only with confirmation** (MS-3.3). If a confirmed Wunschprofil holds a wish that fits a
   part, show the sentence to the user and ask whether it may be used in this letter. Use it only after a clear
   yes. A wish marked `hypothese: ja` is never used. If a fit check exists, apply its result first: a veto stops the
   run until the user decides (MS-9.3, WJ-7.1).
5. **Select the proofs** (MS-5, MS-6). Take two or three proofs from the Grundlage that support the stated
   reasons, from analysis rows with status `erfüllt` and strength `mittel` or `stark` (CG-4). A personal competence
   is written only with one proof (MS-6.1). Do not turn participation into ownership or assistance into leadership.
   A leadership statement needs `fuehrung: ja` in the station note (CV-16).
6. **Write the provenance note.** For every statement of motivation, write one line to
   `## Auswahl Motivationsschreiben` in `pruefbericht.md`: the statement, and its source: `Nutzer, <Datum>` or
   `Wunschprofil, bestätigt <Datum>`. For every proof: the Grundlage entry (file and heading, CG-2.3). For every
   counterpart fact: the source in `analyse.md` (UA-4.5).
7. **Write the letter** in the structure of MS-5. The Betreff, the Anrede, and the Grußformel follow MS-4 and AS-5.
   Use the tone and the forbidden phrases of MS-10 and AS-9. Keep the paragraphs short (one idea, six lines at most).
8. **Check length** (MS-7). One page for `stelle`, `quereinstieg`, `berufseinstieg`; up to two pages for `studium`
   and `stipendium`, unless the counterpart prescribes another limit. About 300 to 600 words is the aid. Trim in this
   order: the weakest proof, then sentences of the Einstieg. Never cut a statement of motivation that the user
   stated for the sake of length without asking.
9. **Write the file** with the frontmatter. The hash is the `hash` value of
   `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md` (R-9.5). `<plugin-root>` is the
   plugin directory, two levels above this skill's base directory.
10. **Hand over.** Show the user the letter, the open markers, and the provenance note. Name the next step:
    `job-application-quality-gate`.

## Hard rules

1. **Never invent a motivation.** No reason, no emotion, no personal story, no admiration, and no goal that the user did
   not state or confirm (MS-3.1, MS-3.2). A missing reason is a marker.
2. **No inference from the Grundlage.** A past role shows what the candidate did, not what the candidate wants (WJ-2.5).
3. **Facts only from the Grundlage.** Every fact in the letter equals the Lebenslauf and the Grundlage (R-1, MS-9.2).
4. **Competences need proofs** (MS-6.1). Goals are written as goals, never as a present ability (MS-6.3).
5. **Counterpart facts need a source** and never come from a rating portal (MS-3.5, UA-2.1). The letter names the
   programme or company as verified.
6. **A Motivationsschreiben is not an Anschreiben.** Do not copy paragraphs from the Anschreiben (MS-9.1).
7. **Disclosure.** A letter to a Vermittler does not name an employer that the counterpart has not disclosed (KK-4.1).
8. **Overrides.** A prescribed format, length, language, or list of questions of the counterpart is followed and
   recorded (MS-11).
9. **One document per run.** Never batch several applications into one run (`CLAUDE.md` rule 3).
