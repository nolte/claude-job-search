---
name: bewerbung-anschreiben-erstellen
description: "Writes a German Anschreiben (cover letter) for one Stellenanzeige in DIN-5008-style layout, maximum one page, with requirement-to-proof paragraphs taken from bewerbung/profil.md and the posting analysis. Supports ausschreibung, initiativ, quereinstieg and berufseinstieg variants. Writes Markdown to bewerbung/<slug>/anschreiben.md. Use on \"schreib ein Anschreiben\", \"Motivationsschreiben für diese Stelle\", \"Initiativbewerbung schreiben\", or equivalent German requests. Don't use for the CV (bewerbung-lebenslauf-erstellen), the E-Mail (bewerbung-email-erstellen), or the review of finished documents (bewerbung-pruefen)."
tags: [bewerbung, anschreiben, motivationsschreiben, deutsch, din-5008]
phase: create
summary: "Writes a one-page German cover letter that maps the posting's requirements to proven experience from the profile."
summary_de: "Schreibt ein einseitiges deutsches Anschreiben, das die Anforderungen der Stelle mit belegter Erfahrung aus dem Profil verbindet."
use_when:
  - "you need a cover letter for a specific posting"
  - "you want an unsolicited application (Initiativbewerbung) letter"
  - "you are changing careers or starting out and need a tailored letter"
dont_use_when:
  - situation: "You need the CV"
    alternative: bewerbung-lebenslauf-erstellen
  - situation: "You need the text for the sending e-mail"
    alternative: bewerbung-email-erstellen
see_also:
  - bewerbung-stellenanzeige-analysieren
  - bewerbung-lebenslauf-erstellen
  - bewerbung-email-erstellen
  - bewerbung-pruefen
---

# Bewerbung Anschreiben erstellen

Spec: `spec/bewerbung/konventionen/en.md` R-1 (facts), R-3 (letter form, length,
tone), R-7 (quality gate).

## Inputs

- `bewerbung/profil.md` (required).
- `bewerbung/<slug>/analyse.md` (required for `ausschreibung`; optional otherwise).
- `ausrichtung` (`ausschreibung` default, `initiativ`, `quereinstieg`, `berufseinstieg`).

## Output

`bewerbung/<slug>/anschreiben.md`:

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
2. Choose the two or three *Muss* requirements with the strongest *erfüllt* evidence.
   Each paragraph pairs one requirement with one concrete, profile-backed example.
3. Write the opening and the motivation paragraph from the posting's own facts. If the
   posting gives none, leave `[ERGÄNZEN: konkreter Bezug zum Unternehmen]`.
4. Match the tone of the posting (Sie unless the posting uses du).
5. Count words and keep the letter under one page (R-3, about 250–400 words).

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
