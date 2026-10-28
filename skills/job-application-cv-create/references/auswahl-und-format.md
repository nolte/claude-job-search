# Selection per application, format by situation, photo

Loaded by `job-application-cv-create` in steps 2 and 4 of its workflow. Spec: `spec/job-application/konventionen/en.md`
R-8.1 (format by situation), R-8.2 (photo), R-9.11 (selection); `spec/job-application/cv-generierung/en.md` CG-5, CG-6,
CG-7, CG-11.3; `spec/job-application/lebenslauf/en.md` LB-4.2, LB-6, LB-7, LB-8.

## Auswahl pro Bewerbung (R-9.11)

The Grundlage is complete and may hold more than one application needs. This step selects what the Lebenslauf for this
posting uses.

1. **Choose** stations, bullets, and certificates by the criteria of CG-5, in this order: coverage of *Muss*
   requirements, coverage of *Wunsch* requirements, evidence strength, scope and seniority, demonstrable results,
   redundancy, recency as tie-breaker only. Stations stay in reverse chronological order; relevance decides what is
   shown in full. Older strong evidence goes into the Kurzprofil or, only in the format `kombiniert`, a *Relevante
   Projekte* block (CG-5.2).
2. **Only existing entries.** Use only entries that exist in the Grundlage. Do not add facts. Reword only as the
   controlled rewriting of CG-7.1 allows, in the bullet form of CG-8.1; no new claims (CG-7.2).
3. **Output limits.** Bullet counts come from CG-6 (R-2.1), applied to this output. They do not come from the
   Grundlage.
4. **List sections.** One bullet per entry in the form of LB-6.1 (`<Zeitraum>: <Abschluss oder Inhalt>, <Institution>,
   <Ort>`; certificates `<Jahr>: <Zertifikat>, <Aussteller>, <Ort>`). Dated lists are in reverse chronological order
   (LB-6.3). Use the official name of the degree; state a grade only if the Grundlage states it (LB-6.4); a
   certificate the Grundlage does not hold is not written (LB-6.5). A year-only period is written `JJJJ – JJJJ` (a
   Warnung, CV-02; no placeholder, LB-6.2).
   - *Sprachkenntnisse:* `<Sprache>: <GER-Niveau>` or `Muttersprache`; no level without a source (LB-7.1, R-9.8).
   - *IT- und Fachkenntnisse:* one bullet per group, `<Gruppe>: <Eintrag>, <Eintrag>`; a level or duration only if the
     Grundlage has it; entries that the *Muss* requirements name come first, and the most relevant group first
     (LB-7.2, LB-7.3); at most ten entries per group (LB-7.6).
   - No bars, dots, stars or percentages for skills (LB-7.4). No Zeugnis wording (LB-6.6).
   - *Ehrenamt* only if it supports the application or fills a period; *Interessen* only if the user asks and the
     interests are neutral and relevant (LB-8.1, LB-8.2).
   - No Referenzen and no reference persons in the Lebenslauf (LB-8.3).
5. **Kurzprofil** (when written, LB-4.2): at most three sentences of facts from the Grundlage (field, years of
   experience, the two or three most relevant competences, for a career change the transferable evidence). Years are
   computed from the Grundlage periods, not estimated. Every statement has a Grundlage entry, listed in the
   `## Auswahl Lebenslauf` section. Nominal or participle phrases, no „Ich“, no evaluation, no personality words.
6. **Omissions and sources are visible.** Write the section `## Auswahl Lebenslauf` in `pruefbericht.md` of the
   folder: for every entry used, its Grundlage entry (file and heading, CG-2.3); for every omitted entry, a short
   reason; the Kurzprofil decision; stations with the header line only (CG-6.5); an allowed exception of more than 5
   bullets (CG-6.4); a photo decision. Create the file if it is missing. A re-run replaces only this section and leaves
   `## Auswahl Anschreiben`, `## Auswahl Motivationsschreiben` and `## Prüfung` unchanged (LS-7.4). A left-out station
   must not leave an unexplained gap. A gap over two months stays as a neutral entry (R-2). A page-limit exception does
   not belong here (step 7 of the workflow).
7. **Never store the selection** in the Grundlage or in the profile. The Grundlage carries no application-specific
   marks.

## Format rules by situation (R-8.1)

- **chronologisch:** default. Full station list, two pages at most.
- **einseitig:** one page. Education and internships first, then skills. Praktika with month, company, and two bullets
  (school internships are not listed).
- **kombiniert:** a Kurzprofil of at most three sentences, then the chronological station list. Used for Quereinstieg
  and many stations. Stations may be grouped in blocks such as „Praktika“, „Relevante Projekte“.
- **ats:** single column, standard headings, no photo, keywords only with evidence (R-8.3). The final file is
  Markdown; the export is a separate step (R-8.3.4): a text PDF by default, DOCX only when the portal asks for it.

## Photo

A photo is included only when R-8.2 allows it and the user wants it: on the user's request in Germany, recommended in
Austria, never for an ATS or portal application. The file is `rohdaten/foto.jpg`, linked from the Grundlage (LS-4);
the skill only reads it. Insert it as a Markdown image with the relative path to the file at the top of
`## Persönliche Daten` (CG-11.3 allows this one image). Without a request there is no photo.
