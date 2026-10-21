---
name: job-application-email-create
description: "Writes the German Bewerbungs-E-Mail that sends an application by e-mail: subject line with role and reference number, short body, attachment list with DIN-style file names, and a size check. Writes plain text to job-application/<slug>/email.md. Use on \"schreib die Bewerbungsmail\", \"E-Mail-Text für meine Bewerbung\", \"Anhänge für die Bewerbung benennen\", or equivalent German requests. Don't use when the posting asks for a portal application (only the documents are then needed), for the cover letter itself (job-application-cover-letter-create), or for the review (job-application-quality-gate)."
tags: [bewerbung, email, anhang, deutsch]
phase: deliver
summary: "Writes the German cover e-mail, subject, attachment list and file names for an e-mail application."
summary_de: "Schreibt die deutsche Begleit-E-Mail mit Betreff, Anhangsliste und Dateinamen für eine Bewerbung per E-Mail."
use_when:
  - "the posting asks for an application by e-mail"
  - "you need the sending e-mail text and attachment names"
dont_use_when:
  - situation: "The application goes through a portal or by post"
    alternative: job-application-solution
  - situation: "You need the cover letter itself"
    alternative: job-application-cover-letter-create
see_also:
  - job-application-cover-letter-create
  - job-application-cv-create
  - job-application-quality-gate
---

# Bewerbung E-Mail erstellen

Spec: `spec/job-application/konventionen/en.md` R-4 (e-mail form), R-5 (Zeugnisse),
R-1 (facts). Channel, tone and content per counterpart: `spec/job-application/kontaktklassifikation/en.md`
KK-4 (disclosure and confidentiality), KK-5 (communication by counterpart), KK-7 (data protection).

## Inputs

- `job-application/<slug>/analyse.md` (Stammdaten, Betreff details, verlangte Unterlagen).
- `job-application/profil.md` (Name, phone, e-mail).
- The documents that will be attached. Their file names are the basis for the list.

## Output

`job-application/<slug>/email.md`, plain text:

```text
An: <Ansprechpartner-E-Mail or the posting's address>
Betreff: Bewerbung als <Stelle> (Ref.-Nr. <nr>) – Vorname Nachname

Sehr geehrte Frau <Nachname>,

anbei sende ich Ihnen meine Bewerbung für die Stelle <Stelle>, die ich auf <Quelle> gefunden habe.
<Ein bis zwei Sätze: wichtigster Grund, warum das Profil passt, belegt durch das Profil.>

Im Anhang finden Sie:
- Anschreiben (Vorname_Nachname_Anschreiben.pdf)
- Lebenslauf (Vorname_Nachname_Lebenslauf.pdf)
- Zeugnisse (Vorname_Nachname_Zeugnisse.pdf), nur wenn verlangt

Für ein persönliches Gespräch stehe ich Ihnen gerne zur Verfügung.

Mit freundlichen Grüßen

Vorname Nachname
Telefon · E-Mail
```

## Workflow

0. **Counterpart first.** Read `kontaktart`, `auftraggeber`, `exklusiv` and the section `## Unternehmen` of `analyse.md`.
   Apply the KK-5 row for this counterpart to the Anrede, the opening, and the content. For a Vermittler, the mail
   names no Auftraggeber before disclosure (KK-4.1), and it asks the exclusivity question before the documents are
   sent (KK-4.6). If the counterpart is `Unklar`, the mail asks the question of KK-3.3 instead of sending documents.
   Check the double submission list of the analysis (KK-4.2) before the mail is written; report any match first.
1. Build the subject from the posting's exact role title and reference number.
2. Write the body in three to five sentences. Do not repeat the cover letter.
3. List only the attachments that exist and that the posting asks for (R-5).
4. Derive file names as `Vorname_Nachname_<Dokument>.pdf`. These are the names the user
   should use when exporting, and the skill does not export files itself.
5. Estimate the total size from the files present, if they exist. Warn when it is
   large, and suggest a combined PDF or compression (R-4).

## Hard rules

1. **Plain text, no HTML, no tracking.** The e-mail text must read correctly in any client.
   `email.md` starts with a frontmatter block carrying `grundlage_hash` (the `hash` value of `scripts/grundlage_hash.py`, R-9.5); only the text
   below it is the mail itself.
2. **No new facts** in the body beyond what the profile and analysis already contain.
3. **Attachments named in the list must exist** in the folder. Report missing ones as blockers.
4. **Recipient address** is never guessed. Use `[ERGÄNZEN: Bewerbungs-E-Mail]` if the posting does not give one.
5. **Attachments only for this counterpart.** The attached documents are those the candidate has approved for this
   counterpart (KK-7.1). A Vermittler does not receive the documents for an employer that has not been disclosed.
6. **No company fact from rating portals** and no Auftraggeber name before disclosure (UA-2.1, KK-4.1).
