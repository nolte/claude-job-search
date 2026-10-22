---
name: job-application-email-create
description: "Writes the German Bewerbungs-E-Mail that sends an application by e-mail: subject line with role and reference number, short body, attachment list with ASCII file names, and a size check. Writes plain text with a frontmatter block to <wurzel>/<slug>/email.md; on request also the follow-up mail email-nachfassen.md. Use on \"schreib die Bewerbungsmail\", \"E-Mail-Text für meine Bewerbung\", \"Anhänge für die Bewerbung benennen\", \"Nachfass-Mail schreiben\", or equivalent German requests. Don't use when the posting asks for a portal application (only the documents are then needed), for the cover letter itself (job-application-cover-letter-create), or for the review (job-application-quality-gate)."
tags: [bewerbung, email, anhang, deutsch]
phase: deliver
summary: "Writes the German cover e-mail, subject, attachment list and file names for an e-mail application."
summary_de: "Schreibt die deutsche Begleit-E-Mail mit Betreff, Anhangsliste und Dateinamen für eine Bewerbung per E-Mail."
use_when:
  - "the posting asks for an application by e-mail"
  - "you need the sending e-mail text and attachment names"
  - "you want to follow up on an application after the reply period"
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
KK-4 (disclosure and confidentiality), KK-5 (communication by counterpart, KK-5.4 and KK-5.5 follow-up), KK-7 (data
protection). Anrede: `spec/job-application/anschreiben/en.md` AS-5.6 to AS-5.8. Paths and status:
`spec/job-application/lokale-struktur/en.md` LS-2.6, LS-6.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`) from its
frontmatter. Relative paths resolve against the working directory that contains `job-application/konfiguration.md`
(LS-2.6). `<wurzel>/<slug>/` is the Vorgang folder.

## Inputs

- `<wurzel>/<slug>/analyse.md` (Stammdaten, Betreff details, tone Sie or du, Ansprechperson, verlangte Unterlagen,
  `kontaktart`, `auftraggeber`, `exklusiv`, section `## Unternehmen`).
- `<wurzel>/profil.md` (Name, phone, e-mail), derived from the Datengrundlage (Grundlage).
- `<wurzel>/<slug>/anschreiben.md` and `lebenslauf.md`: the mail repeats their Stammdaten and nothing else.
- The documents that will be attached, in `<wurzel>/<slug>/export/` if they exist. Their file names are the basis for
  the list.
- For `nachfassen`: `vorgang.md` with `versendet_am` and `wiedervorlage` (LS-6.1).

## Output

`<wurzel>/<slug>/email.md`:

```text
---
grundlage_hash: <current hash of the Grundlage>
format: email
---
An: <address of the Ansprechperson or the posting's address>
Betreff: Bewerbung als <Stelle> (Ref.-Nr. <nr>) – Vorname Nachname

Sehr geehrte Frau <Nachname>,

Ich bewerbe mich auf die Stelle als <Stelle>, die Sie auf <Quelle> ausgeschrieben haben.
<Ein bis zwei Sätze: wichtigster Grund, warum das Profil passt, belegt durch die Grundlage.>

Im Anhang finden Sie:
- Anschreiben (Vorname_Nachname_Anschreiben.pdf)
- Lebenslauf (Vorname_Nachname_Lebenslauf.pdf)
- Zeugnisse (Vorname_Nachname_Zeugnisse.pdf) <only when the posting asks for them>

Über ein Gespräch freue ich mich.

Mit freundlichen Grüßen

Vorname Nachname
Telefon · E-Mail
```

Only the text below the frontmatter is the mail. Everything in `<…>` is an instruction for the writer and never
appears in the mail.

## Workflow

0. **Counterpart first.** Read `kontaktart`, `auftraggeber`, `exklusiv` and the section `## Unternehmen` of `analyse.md`.
   Apply the KK-5 row for this counterpart to the Anrede, the opening, and the content. For a Vermittler, the mail
   names no Auftraggeber before disclosure (KK-4.1), and it asks the exclusivity question before the documents are
   sent (KK-4.6). If the counterpart is `Unklar`, the mail asks the question of KK-3.3 instead of sending documents.
   Check the double submission list of the analysis (KK-4.2) before the mail is written; report any match first.
1. **Betreff** (R-4, D7): `Bewerbung als <Stelle> (Ref.-Nr. <nr>) – Vorname Nachname`. The role title without a gender
   suffix such as `(m/w/d)`, `(w/m/d)`, `(all genders)`; `(Ref.-Nr. <nr>)` only when the posting gives one. The Betreff
   equals the Betreff of the Anschreiben without the name part (AS-4.4).
2. **Anrede** (AS-5.6 to AS-5.8, D6). Sie or du as recorded in `analyse.md`. With a known person:
   `Sehr geehrte Frau <Nachname>,` or `Sehr geehrter Herr <Nachname>,`, academic titles taken over. With du:
   `Hallo <Vorname>,` or `Guten Tag <Vorname Nachname>,`. Gender not clear: `Guten Tag <Vorname Nachname>,`.
   `Sehr geehrte Damen und Herren,` only when no person is known (ask the user once; the quality gate reports it as a
   Warnung). Never guess a name.
3. **Body** in three to five sentences: the opening sentence of the template, one or two sentences with the key reason
   from the Grundlage, the attachment list, the closing sentence. Do not repeat the cover letter.
4. **Attachments** (R-5, D16). List only the attachments that exist and that the posting asks for. The Zeugnisse are one
   combined PDF `Vorname_Nachname_Zeugnisse.pdf`: the last two or three Arbeitszeugnisse, the highest degree, and the
   certificates relevant to the posting, most recent first. The Anlagen line of the Anschreiben lists the same set.
5. **File names** (R-4, D17): `Vorname_Nachname_<Dokument>.pdf` in ASCII: `ä→ae, ö→oe, ü→ue, ß→ss`, a hyphen in the
   name stays, a space in the name part becomes `-` (`Anna-Lena_Mueller_Lebenslauf.pdf`). These are the names the
   user uses when exporting (`job-application-export` applies the same rule); this skill does not export files.
6. **Size** (R-4, D3). Add up the size of the files in `export/`, if they exist. Guideline at most 5 MB in total. From
   5 MB report a Warnung and propose a smaller combined PDF or compression; from 10 MB report a Blocker: the mail is
   not ready until the attachments are smaller.
7. **Frontmatter.** `grundlage_hash` is the `hash` value of
   `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md` (R-9.5); `<plugin-root>` is the
   plugin directory, two levels above this skill's base directory.
8. **Status.** If the folder holds `vorgang.md` (LS-6.1), set `status: erstellt` and append
   `- JJJJ-MM-TT: <alter Status> → erstellt, job-application-email-create` to `## Verlauf`.

## Variant `nachfassen` (only on request)

A follow-up mail after the period of KK-5.4 (the follow-up column of the KK-5 row, counted from `versendet_am`; the
user sets `wiedervorlage`). Written only when the user asks for it.

- Output `<wurzel>/<slug>/email-nachfassen.md`, same frontmatter and Betreff as `email.md` with the prefix
  `Rückfrage zu meiner Bewerbung:`.
- Three to five sentences: the date of the sending (`versendet_am`) and the role, one question about the state of the
  process, the continued interest in one sentence, the closing sentence. No pressure, no deadline for the counterpart,
  no new facts, no repeated attachments (KK-5.5).
- Not before the follow-up period has passed; if `versendet_am` is empty, stop and ask the user for the date.
- Writes no status. Appends `- JJJJ-MM-TT: Nachfass-E-Mail geschrieben, job-application-email-create` to `## Verlauf`.

## Hard rules

1. **Plain text, no HTML, no tracking.** The e-mail text must read correctly in any client. `email.md` starts with the
   frontmatter block carrying `grundlage_hash` and `format: email`; only the text below it is the mail itself.
2. **No new facts** in the body beyond what the Grundlage, the profile and the analysis already contain.
3. **Attachments named in the list must exist** in the folder. Report missing ones as Blocker.
4. **Recipient address** is never guessed. Use `[ERGÄNZEN: Bewerbungs-E-Mail]` if the posting does not give one.
5. **Attachments only for this counterpart.** The attached documents are those the candidate has approved for this
   counterpart (KK-7.1). A Vermittler does not receive the documents for an employer that has not been disclosed.
6. **No company fact from rating portals** and no Auftraggeber name before disclosure (UA-2.1, KK-4.1).
7. **Betreff without gender suffix**, identical to the Anschreiben (AS-4.4).
8. **Only the Wurzel is written** (LS-5.7): the Vorgang folder and `vorgang.md` of this Vorgang.
