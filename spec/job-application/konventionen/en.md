# Bewerbungsunterlagen — DACH conventions (EN canonical)

Normative rules every `job-application-*` skill and the `job-application-reviewer` agent obey.
German output is the default target language; the rules describe German-speaking
(DE / AT / CH) practice. Where practice varies, the rule says so — the job posting
(Stellenanzeige) always has priority over this default.

## R-1 Faktentreue (fact integrity) — hard rule

1. Every factual claim in a generated document (employer, role, period, task,
   result, degree, grade, certificate, language level, skill) must trace to
   `job-application/profil.md` or to the user's explicit statement in the session.
2. Unknown facts are never invented or "smoothed over". They are written as
   `[ERGÄNZEN: <what is missing>]` and reported as a blocker by `job-application-quality-gate`.
3. A requirement from the Stellenanzeige may be marked as *erfüllt* only with
   evidence from the profile. Otherwise it is *teilweise*, *nicht belegt* or *unklar*
   (CG-4 of `spec/job-application/cv-generierung/en.md`). *nicht belegt* is not a statement that the candidate lacks the competency.
4. Keywords from the posting are reused verbatim only where the candidate has the
   skill or experience. Keyword stuffing is not allowed.

## R-2 Lebenslauf

The document type is described in full in `spec/job-application/lebenslauf/en.md` (sections, entry shapes,
layout, checks). The rules below stay in force and are the short form.

- **Form:** einspaltig (single column, no layout tables), **rückwärts chronologisch** — the most recent
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

### R-2.1 Eintragsblock (one entry per position)

Each position (Station) of the Berufserfahrung is one block with a fixed shape.
Sources: [lebenslauf.de – Berufserfahrung](https://www.lebenslauf.de/ratgeber/lebenslauf/berufserfahrung/),
[Karrierebibel – Berufserfahrung](https://karrierebibel.de/berufserfahrung-im-lebenslauf/),
[cv-folio – Berufserfahrung 2026](https://www.cv-folio.io/artikel/berufserfahrung-lebenslauf),
[Emory – Resume bullets](https://cpd.emory.edu/resources/creating-impressive-resume-bullets/),
[Jobscan – STAR method](https://www.jobscan.co/blog/star-method-resume/).

**Block shape (header line plus bullets):**

```markdown
### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin
- Betreuung der Event-Pipeline in Python und Kafka; Latenz von 800 ms auf 120 ms gesenkt.
- Einführung von Code-Reviews als Pflichtschritt im Team mit fünf Entwicklern.
```

1. **Header line** in this order: `Zeitraum | Position | Arbeitgeber, Ort`.
   - Zeitraum: `MM/JJJJ – MM/JJJJ` with an en dash (–), or `MM/JJJJ – heute`. No day.
   - Position: exactly the title from the Arbeitszeugnis or Arbeitsvertrag. If none exists, the title in the profile, marked `[KLÄREN: Titel laut Zeugnis]`.
   - Arbeitgeber: legal name (with Rechtsform) and city, as in the profile.
2. **Bullets** below the header, not a table.
   - **Count:** defaults and the hard maximum of 5 bullets per station are set in CG-6 of `spec/job-application/cv-generierung/en.md`. Bullet counts are not fixed by this rule; they follow relevance and evidence (CG-5). A station that does not support the application may carry the header line only.
   - **Length:** each bullet fits on one line, two lines at most.
   - **Form and wording:** canonical in CG-8.1 to CG-8.3 of `spec/job-application/cv-generierung/en.md`: object first, past participle last, optional result after a semicolon, digits for measured values, no subject, no final period. Avoid „verantwortlich für“ and „zuständig für“ (CG-8.2).
   - **Results:** prefer a number (Prozent, Zeit, Kosten, Teamgröße, Volumen), supported by the profile or the Zeugnis. If no number is known, a qualitative result from the profile is enough. Never invent a number. Where confidentiality applies, a size band replaces the exact figure (cv-folio).
   - **No routine duties:** daily tasks without a result are left out (Emory, Jobscan).
   - **Relevance:** bullets follow the requirements of the Stellenanzeige where the profile supports them (R-1.4). The STAR order (Situation, Aufgabe, Handlung, Ergebnis) is used to think through a bullet, not to write it out in full.
3. **Gaps:** a period without employment longer than two months needs a neutral entry or an explanation (lebenslaufdesigns.de).
4. **Ordering inside the CV:** stations are reverse chronological. The bullets within a station are ordered by relevance to the posting, not by date.
5. **Traceability:** every bullet links to a Grundlage entry (FA-5, FA-7 of the Datengrundlage requirement). The link is kept in the Grundlage or in `pruefbericht.md`, never in the CV text itself.

## R-3 Anschreiben (cover letter)

The document type is described in full in `spec/job-application/anschreiben/en.md`. A personal motivation
letter is a separate document type (`spec/job-application/motivationsschreiben/en.md`). The rules below stay
in force and are the short form.

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
  and are not committed to git. The `job-application/` working folder is git-ignored.
- Documents are generated as Markdown sources; PDF or DOCX export is a separate step
  and is never done automatically without the user's request.

## R-7 Quality gates before "bereit zum Versand"

A set is ready to send only when `job-application-quality-gate` reports **zero blockers**:

- no `[ERGÄNZEN: …]` placeholder left,
- company name, role, reference number and contact name identical across all documents,
- every claim traceable to the profile (R-1),
- Anschreiben within one page and Lebenslauf within the length budget (R-2, R-3),
- German spelling and grammar free of obvious errors,
- the Datengrundlage hash in every output matches the current Grundlage (R-9.4),
- every Eintragsblock follows R-2.1 (header order, bullet limits of CG-6, no invented numbers),
- every automated rule of CG-13 (CV-01 to CV-15, as reported by `scripts/cv_checks.py`) has no Blocker,
- for ATS or portal applications, the ATS rules of R-8.3 hold.

## R-8 Formatauswahl nach Situation

### R-8.1 Vorschlag je Situation

The skill proposes a format from the situation, and the user may deviate (recorded in the result). Sources: [Profiling-Institut – ATS-Generator](https://www.profiling-institut.de/job-application/ats-lebenslauf-generator/), [Karrierebibel – Quereinsteiger](https://karrierebibel.de/lebenslauf-quereinsteiger/), [Kickresume – Praktikum](https://www.kickresume.com/de/blog/internship-resume-examples/), [Karrierebibel – Europass](https://karrierebibel.de/europass/).

| Situation | Format | Note |
|---|---|---|
| Standard, Berufserfahrung in DE | chronologisch | default, two pages at most |
| Berufseinstieg, Ausbildung oder Studium | einseitig | Ausbildung and Praktika first |
| Schüler, Studierende, Praktikum | einseitig | Praktika with month, company, two bullets |
| Quereinstieg, Branchenwechsel | kombiniert | Kurzprofil of 2–4 sentences, then chronological |
| Lücke (Elternzeit, Pflege, Auszeit) | chronologisch | gap as its own line, neutral wording |
| Viele Stationen oder Projektarbeit | kombiniert | Berufserfahrung grouped in blocks |
| Akademische Stelle, Promotion, Habilitation | akademischer CV | Phase 2; in Phase 1 a blocker, see R-8.4 |
| EU-Stelle, öffentlicher Dienst, Stipendium | Europass | see R-8.4 |
| ATS-Hinweis oder Online-Portal | ATS-optimiert | see R-8.3 |
| Bewerbung in Österreich | chronologisch, Foto | Foto ca. 4 × 5 cm, see R-8.2 |
| Bewerbung in der Schweiz | chronologisch | German default, see R-8.5 |

Funktional (skill-based without timeline) is not produced. It is recommended only in extreme cases, and then never without the user's explicit request ([airesume.guru](https://airesume.guru/de/blog/funktionaler-lebenslauf-beispiele)).

### R-8.2 Foto

- Default: no photo. The profile has an optional photo field.
- Germany: photo only on the user's request. It is common, not mandatory (AGG; [Euroakademie](https://www.euroakademie.de/magazin/?p=4599)).
- Austria: recommended, about 4 × 5 cm, at the top ([workinaustria](https://www.workinaustria.com/your-personal-guide/arbeiten-in-oesterreich/bewerbungsunterlagen)).
- ATS application or online portal: no photo, because a parser cannot read it.
- Internship: photo may be omitted.

### R-8.3 ATS-Regeln

For ATS or portal applications, the CV follows these rules ([Profiling-Institut](https://www.profiling-institut.de/5-haeufigste-fehler-im-ats-lebenslauf/), [Remotely](https://www.remotely.de/ats-lebenslauf), [pdf2go](https://pdf2go.com/blog/the-best-resume-formats-for-ats)):

1. Single-column layout, no layout tables, text boxes, graphics, or header/footer content.
2. Standard headings: „Berufserfahrung“, „Ausbildung“, „Kenntnisse“, „Sprachkenntnisse“.
3. Keywords from the posting only where the profile shows evidence (R-1.4).
4. File format: DOCX preferred; a text-PDF exported from Word is second. A scanned PDF is not acceptable.
5. A format stated in the posting overrides this rule.

A violation of an ATS rule is a warning. It becomes a blocker when the posting requires an ATS-compatible format and the output does not meet it.

### R-8.4 Europass und akademischer CV (Phase 1)

- **Europass** is not generated. A posting that explicitly requires it yields a blocker with the hint to the EU portal ([Karrierebibel – Europass](https://karrierebibel.de/europass/)). The Europass is voluntary and usual only for EU bodies, public sector, and scholarships.
- **Akademischer CV** is Phase 2. In Phase 1 the skill reports the need for a dedicated structure (publications, teaching, third-party funding are separate sections).

### R-8.5 Schweiz

No separate Swiss variant in Phase 1. The German default applies, with a hint that language and photo expectations are regional. The Swiss rules (photo, signature) are only added after a second source confirms them ([Karrierebibel – Schweiz](https://karrierebibel.de/bewerbung-schweiz/), single source).

## R-9 Datengrundlage (Quelle der Wahrheit)

The user's own, complete, chronological basis in Markdown. Requirement document: `project/requirements/eigene-datengrundlage.md`.

1. **Location:** referenced, not copied (decision E-P2). The path is set in `job-application/konfiguration.md` under the frontmatter key `grundlage` (R-9.10). Default: `job-application/grundlage/lebenslauf-chronologisch.md`. The path names either one Markdown file (file mode) or a directory of Markdown notes (directory mode), for example one note per Station, Ausbildung and Weiterbildung. Directory mode requires the key `grundlage_index`, which names the index note with `stand` and the Pflegeverlauf. Every skill that reads the Grundlage reads all notes of the set in directory mode. The Grundlage may live anywhere on the local disk, for example in an existing notes folder. A path inside the plugin repository is refused (R-9.9).
2. **Language:** German. Original wording in another language (Zeugnis, Zertifikat, English project names) stays unchanged and is marked, e.g. `(EN-Original)`.
3. **Certificates (Zeugnisse):** one entry per certificate with file, date, issuer, and the full wording of the closing assessment. The scan stays outside the Grundlage and outside git.
4. **Intake:** existing CVs and certificates are processed first (raw material to entries with source reference). The interview asks only for gaps, contradictions, and `[KLÄREN]` markers. Every adopted entry is confirmed by the user before it counts as established.
5. **Hash and date:** the Grundlage carries `stand: JJJJ-MM-DD` in its frontmatter. In file mode this is the file itself, in directory mode the index note. A missing or invalid `stand` is a Blocker. Each output carries `grundlage_hash` (the hash below, at creation time). The quality gate compares the stored with the current hash. A mismatch makes the output stale. The hash is computed by `scripts/grundlage_hash.py` of this plugin, so every skill obtains the same value:
   - **File mode:** SHA-256 of the file's bytes.
   - **Directory mode:** the set consists of every `*.md` file below the directory, recursively, plus the index note if it lies outside the directory. Entries whose name starts with `.` (files and folders) are skipped. Symbolic links are followed; a file reached twice counts once. Each file has a label: `file:<relative path>` for files below the directory, where the relative path uses forward slashes, and `index:<file name>` for an index outside it. The set is sorted by label in byte order. The hash is SHA-256 over the UTF-8 text in which each file contributes two lines, `<label>` and the SHA-256 hex of the file's bytes, in that order.
   - File contents are hashed as bytes. Line endings and whitespace are not normalised.
   - The Pflegeverlauf in the index note is part of the set. Every maintenance change therefore makes the Grundlage hash change.
6. **Source references:** each station in the Grundlage names its raw source (file and page). The profile (`job-application/profil.md`) is derived from the Grundlage and keeps the reference per entry (FA-5).
7. **Maintenance:** a change adds or corrects the affected entries only. A complete rewrite of an existing Grundlage is not done.
8. **Pflegelauf:** an existing Grundlage is maintained with the interview of R-9.8, carried out by `job-application-cv-maintain`. `job-application-profile-capture` creates a Grundlage only when none exists.
9. **Repository boundary:** the skill refuses any Grundlage path inside a directory tree that contains the plugin manifest `.claude-plugin/plugin.json` with `"name": "claude-job-search"`. The message names the `konfiguration.md` setting, so the user can point to a path outside the repository.
10. **Konfiguration:** `job-application/konfiguration.md` contains the frontmatter keys `wurzel`, `grundlage` and `grundlage_index` (LS-2.5, spec `lokale-struktur/en.md`). `grundlage_index` is required in directory mode and not allowed in file mode. Relative paths resolve against the working directory of the user; absolute paths are recommended. Every skill that reads or hashes the Grundlage resolves the paths from this file first and falls back to the defaults.

### R-9.8 Pflegelauf (maintenance interview)

**Checklist.** Required items for a complete Grundlage:

- Contact: name, address, phone, e-mail (required). LinkedIn: optional.
- Persönlich: Geburtsdatum, Familienstand, Staatsangehörigkeit, Foto are optional and asked only when the session scope includes them (scope `persönlich`).
- Each Station: Zeitraum in `MM/JJJJ – MM/JJJJ` or `MM/JJJJ – heute`, Position exactly as in the Zeugnis, Arbeitgeber with Rechtsform and Ort, at least one Aufgabe. Results are recommended for relevant stations. A Zeugnis entry is required when a Zeugnis exists.
- Station notes (CG-2.4 of `spec/job-application/cv-generierung/en.md`): sections `## Erfolge` and `## Team` are recommended for every station, and `fuehrung` records whether the candidate led people (`ungeklärt` until known). A missing `fuehrung` is a Hinweis.
- Ausbildung: Abschluss, Ort, Zeitraum. Schule: Abschluss, Schule, Jahr.
- Sprachen with GER level (required). IT-Kenntnisse with level or duration (recommended). Weiterbildung (recommended). Zielrichtung (optional).

**Prüfstufen.** Each finding has one of three levels:

| Stufe | Meaning | Example |
|---|---|---|
| Blocker | required item missing or contradictory | contact empty; two periods for one station |
| Warnung | format or plausibility deviates from R-2 and R-2.1 | year only instead of `MM/JJJJ`; gap over two months without a note; end before start |
| Hinweis | content can be improved | station without result; number without proof; possible but unclear overlap of education and school; more bullets than R-2.1 allows for an output (selection per application, R-9.11) |

**Flow.**

1. Bestandsaufnahme: the complete check runs before any question and produces a finding report by level and section.
2. Questions: blockers first, then warnings, then notes. At most three questions per round. Each question names the section and states the finding in one sentence.
3. Answer: the user answers, skips, or marks a finding as not relevant. Skipping keeps the open marker (`[ERGÄNZEN: …]` or `[KLÄREN: …]`). A finding marked not relevant is recorded in the Pflegeverlauf and not asked again unless the user wants it.
4. Apply: each answer is written to the file after the user has seen the changed passage. Every answer is saved immediately, so an abort loses at most the open question.
5. Confirmation: each new or changed Station is confirmed by the user (`Bestätigt: ja`).
6. Close: `stand` is set to today's date, the hash is computed and reported, and a closing report lists completed points, open points, and remaining blockers.

**Rules.**

- Only values the user states or confirmed source passages support are written (R-1). An unknown answer becomes an open marker, never an invented value.
- Only the addressed passages change. Frontmatter and structure are kept. Changes are recorded in a section `## Pflegeverlauf` with the date and a short description per change.
- A second run without changes reports only the still-open points.
- The run uses only the file and the user's answers. No network access.
- German, with original quotations unchanged.
- In directory mode the addressed Station is changed in its own note. The Pflegeverlauf goes into the index note. The checklist applies to the whole set.

Hash command: `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md`. It prints `hash`, `stand` and the mode as JSON, or a `Blocker:` line with exit code 1 (R-9.5).

### R-9.11 Umfang der Datengrundlage und Auswahl pro Bewerbung

1. **Complete, not lean.** The Grundlage holds all of the user's facts. It may contain more stations, bullets, and certificates than one application needs. Its size is not a finding by itself.
2. **Limits apply to outputs.** The bullet counts and page limits of R-2 and R-2.1 govern the generated Lebenslauf, not the Grundlage. In the Pflegelauf, too many bullets in a station is a Hinweis, not a Warnung.
3. **Selection per application.** `job-application-cv-create` selects from the Grundlage for each Stellenanzeige: which stations, which bullets, which certificates, and in which order. The selection follows the posting and the evidence rules of R-1.3 and R-2.1.
4. **Selection never adds facts.** Only entries that exist in the Grundlage can be selected. Wording is not rewritten to fit the posting beyond the reordering and shortening that R-2.1 allows.
5. **Omissions are visible.** The output records which Grundlage entries were used and which were left out, with a short reason, in `pruefbericht.md`. A station left out must not produce an unexplained gap; a gap over two months is still shown as a neutral entry (R-2, Lücken).
6. **Nothing is marked in the Grundlage.** A selection is never stored in the Grundlage. The Grundlage carries no application-specific marks.
7. **Pflegelauf does not select.** `job-application-cv-maintain` checks the completeness of the Grundlage (R-9.8), not its fit to a posting.
8. **Directory mode.** In directory mode the selection reads all notes of the set (R-9.1), not only the index note. Entries are referenced by note and heading (LS-7.5), so that the source of each claim stays traceable.

## R-10 Ausgabeformate

Requirement: `project/requirements/ausgabeformate.md` (FA-O1 … FA-O23). Decisions O-1 … O-5 are recorded there.

1. **One source.** Every output is generated from the Markdown document. Outputs are never edited by hand (FA-O1).
2. **Formats per document.** Lebenslauf and Anschreiben: PDF (LaTeX), DOCX, Markdown, HTML, and the LaTeX source as `tex` (same template, pandoc only, no LuaLaTeX needed). E-Mail: Markdown only. Review report: Markdown only.
3. **Hash.** Each output carries the `grundlage_hash` of its source (FA-O2). Stale outputs are reported by `job-application-quality-gate`.
4. **File names** follow R-4: `Vorname_Nachname_<Dokument>.<ext>`, in `job-application/<slug>/export/` by default (FA-O3, FA-O4).
5. **PDF.** LuaLaTeX, embedded fonts, selectable text. Lebenslauf at most two pages, Anschreiben exactly one (FA-O11 to FA-O13).
6. **DOCX.** Single column, Word heading styles, no tables, editable paragraphs (FA-O16, FA-O17). Recommended for ATS portals (R-8.3).
7. **HTML.** Self-contained, `lang="de"`, responsive, printable, semantic structure, no external resources (FA-O21 to FA-O23).
8. **Content.** Every export must contain the same words as the source (FA-O6).
9. **Export on request only** (R-6). The export command is `task export`.
