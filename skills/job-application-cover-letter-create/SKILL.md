---
name: job-application-cover-letter-create
description: "Writes a German Anschreiben (cover letter) for one Stellenanzeige in DIN-5008-style layout, maximum one page, with requirement-to-proof paragraphs taken from job-application/profil.md and the posting analysis. Supports ausschreibung, initiativ, quereinstieg and berufseinstieg variants. Writes Markdown to job-application/<slug>/anschreiben.md. Use on \"schreib ein Anschreiben\", \"Initiativbewerbung schreiben\", or equivalent German requests. Don't use for a Motivationsschreiben (job-application-motivation-letter-create), for the CV (job-application-cv-create), the E-Mail (job-application-email-create), or the review of finished documents (job-application-quality-gate)."
tags: [bewerbung, anschreiben, motivationsschreiben, deutsch, din-5008]
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

## Inputs

- `job-application/profil.md` (required).
- `job-application/<slug>/analyse.md` (required for `ausschreibung`; optional otherwise).
- `ausrichtung` (`ausschreibung` default, `initiativ`, `quereinstieg`, `berufseinstieg`).

## Output

`job-application/<slug>/anschreiben.md`:

```markdown
**Vorname Nachname**
Straße Hausnummer, PLZ Ort
Telefon · E-Mail

Firma GmbH
Ansprechpartner/in (if known)
Straße Hausnummer, PLZ Ort

Ort, TT.MM.JJJJ

**Bewerbung als <Stelle> (Ref.-Nr. <nr>)**

Sehr geehrte Frau <Nachname>,

<Einstieg: concrete reference to the company or role>

<Absatz 1: requirement → proof from the profile>

<Absatz 2: requirement → proof from the profile>

<Absatz 3: motivation specific to this employer, only with facts from the analysis>

<Schluss: wish for a conversation, optional earliest start date>

Mit freundlichen Grüßen

Vorname Nachname
```

## Workflow

1. Take the Betreff, Anrede, and reference number from the analysis. Use only a name
   the posting or profile gives.
   - **Addressee** is the Anstellungsgeber from the section `## Unternehmen` of `analyse.md` (UA-6.1). If it is
     `unbekannt`, stop: do not write a firm name, and report that the letter needs it.
   - **Recruiter.** If `kontaktart` is a Vermittler class and `auftraggeber` is unknown or not disclosed, the letter is
     not addressed to the Vermittler, and it does not name the Auftraggeber. Stop and ask the user for the disclosure
     (KK-4.1, UA-6.2). The letter may name the employer only after it has been disclosed.
2. Choose the two or three *Muss* requirements with the strongest *erfüllt* evidence.
   Each paragraph pairs one requirement with one concrete, profile-backed example.
3. Write the opening and the motivation paragraph from the posting's own facts. If the
   posting gives none, leave `[ERGÄNZEN: konkreter Bezug zum Unternehmen]`.
4. Match the tone of the posting (Sie unless the posting uses du).
5. Count words and keep the letter under one page (R-3, about 250–400 words).
6. Put a frontmatter block with `grundlage_hash: <current hash>` at the top of the file. The hash is the `hash` value of `<plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md` (R-9.5).
   Sending the letter with a stale hash is a blocker for `job-application-quality-gate`.

## Variants

- **initiativ:** no posting. Name the target area and two or three proven strengths.
  Say what the company gets, not only what the candidate wants.
- **quereinstieg:** lead with transferable experience that maps to the requirements,
  and state the motivation for the change in one sentence without apology.
- **berufseinstieg:** lead with the degree or training, relevant projects, and
  internships, all from the profile.

## Hard rules

1. **Never use the phrase "hiermit bewerbe ich mich"** or other stock openings.
2. **Every claim maps to the profile.** Anything not in the profile is not in the letter.
3. **One page maximum.** Trim the weakest paragraph first.
4. **Gehaltsvorstellung only if requested** by the posting (R-3).
5. **Motivation sources only.** A company fact in the letter comes from the posting or from a public company statement,
   and `analyse.md` names its source (UA-4.5). A rating-portal statement is never used (UA-2.1).
6. **Disclosure first.** The letter names an employer the candidate has not agreed to disclose to the counterpart
   only if the candidate has decided to (KK-4.1).
