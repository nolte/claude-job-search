# Bewerbungsunterlagen — DACH conventions (EN canonical)

Normative rules every `bewerbung-*` skill and the `bewerbungs-reviewer` agent obey.
German output is the default target language; the rules describe German-speaking
(DE / AT / CH) practice. Where practice varies, the rule says so — the job posting
(Stellenanzeige) always has priority over this default.

## R-1 Faktentreue (fact integrity) — hard rule

1. Every factual claim in a generated document (employer, role, period, task,
   result, degree, grade, certificate, language level, skill) must trace to
   `bewerbung/profil.md` or to the user's explicit statement in the session.
2. Unknown facts are never invented or "smoothed over". They are written as
   `[ERGÄNZEN: <what is missing>]` and reported as a blocker by `bewerbung-pruefen`.
3. A requirement from the Stellenanzeige may be marked as *erfüllt* only with
   evidence from the profile. Otherwise it is *teilweise* or *fehlt*.
4. Keywords from the posting are reused verbatim only where the candidate has the
   skill or experience. Keyword stuffing is not allowed.

## R-2 Lebenslauf

- **Form:** tabellarisch (tabular), **rückwärts chronologisch** — the most recent
  entry comes first.
- **Umfang:** typically 1–2 pages; longer only with substantial, relevant experience.
- **Sections, in this order:** persönliche Daten → beruflicher Werdegang →
  Ausbildung / Studium → Schulbildung → Sprachkenntnisse (with CEFR level, e.g. B2) →
  IT- und Fachkenntnisse → Weiterbildung → optional: ehrenamtliches Engagement,
  Interessen.
- **Zeiträume:** `MM/JJJJ – MM/JJJJ` (or `seit MM/JJJJ`), consistent across entries.
- **Lücken:** shown as a gap or as a short neutral entry (e.g. "Elternzeit"); never
  hidden or disguised.
- **Personal data:** Name and contact are mandatory. Foto, Geburtsdatum/-ort,
  Familienstand and Konfession are **optional**; none is required by law or the
  AGG-compliant standard. Do not add them unless the user wants them.
- **Abschluss:** Ort, Datum, and — for paper applications — a handwritten
  Unterschrift. For digital applications the signature line is optional.

## R-3 Anschreiben (cover letter)

- **Layout:** DIN-5008-style letter: Absender block, Empfängeranschrift,
  Ort und Datum, **Betreff** in bold, Anrede, body, Schlussformel, Unterschrift.
- **Betreff:** concrete — role plus reference number if given, e.g.
  `Bewerbung als Backend-Entwickler (Ref.-Nr. 12345)`.
- **Anrede:** `Sehr geehrte Frau <Nachname>` / `Sehr geehrter Herr <Nachname>`
  when the contact person is known; otherwise `Sehr geehrte Damen und Herren`.
  Only use a name that is in the posting or the user's profile.
- **Umfang:** maximum one page; in practice roughly 250–400 words.
- **Structure:** opening with a concrete reference to the company or role (no
  "hiermit bewerbe ich mich") → two to three paragraphs with *requirement → proof*
  pairs from the profile → motivation that is specific to this employer (only with
  facts from the analysis) → closing with a wish for a conversation and optionally
  the earliest start date → Schlussformel `Mit freundlichen Grüßen`.
- **Tone:** match the posting. Use Sie unless the posting clearly uses du.
- **Gehaltsvorstellung:** only if the posting asks for it.

## R-4 Bewerbungs-E-Mail

- **Betreff:** `Bewerbung als <Stelle> (Ref.-Nr. <nr>) – <Vorname Nachname>`.
- **Body:** three to five sentences: what you apply for, where you saw the posting,
  the key reason you fit, what is attached, a greeting.
- **Anhänge:** one PDF per document, named `Vorname_Nachname_Lebenslauf.pdf`,
  `Vorname_Nachname_Anschreiben.pdf`. Optionally one combined PDF.
- **Größe:** check total attachment size before sending. Many mail providers and
  recipients limit attachments (often around 10–25 MB); when in doubt, compress or
  send a combined PDF link.
- **Signatur:** full name, phone, address optional.

## R-5 Zeugnisse (Anlagen)

- Attach certificates only if the posting asks for them or the user's sector
  expects them. Otherwise "Zeugnisse auf Anfrage" is common and acceptable.
- Order: most recent first.

## R-6 Datenschutz and handling

- Application documents contain personal data. They stay local, are never published
  and are not committed to git. The `bewerbung/` working folder is git-ignored.
- Documents are generated as Markdown sources; PDF or DOCX export is a separate step
  and is never done automatically without the user's request.

## R-7 Quality gates before "bereit zum Versand"

A set is ready to send only when `bewerbung-pruefen` reports **zero blockers**:

- no `[ERGÄNZEN: …]` placeholder left,
- company name, role, reference number and contact name identical across all documents,
- every claim traceable to the profile (R-1),
- Anschreiben within one page and Lebenslauf within the length budget (R-2, R-3),
- German spelling and grammar free of obvious errors.
