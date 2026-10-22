# Specifications

Normative specifications for the skills and agents in this plugin. The canonical
language is English; German translations live beside them (`de.md`) once the
translation is produced via `/nolte-shared:spec`.

| Path | Governs |
|------|---------|
| `spec/job-application/konventionen/en.md` | DACH conventions for Lebenslauf, Anschreiben, E-Mail, Zeugnisse, data protection, the quality gate, the output formats (text PDF as the ATS default) and English documents (rules R-1 … R-11; R-11 is a stub) |
| `spec/job-application/cv-generierung/en.md` | CV content: source-of-truth model, target-specific selection, evidence mapping, controlled rewriting, length defaults, ATS and output consistency, quality-gate severities and acceptance scenarios (rules CG-1 … CG-14) |
| `spec/job-application/kontaktklassifikation/en.md` | Classification of the counterpart (recruiter, employer directly, referral, platform), each one's motivation, disclosure rules, and communication by counterpart (rules KK-1 … KK-9) |
| `spec/job-application/unternehmensanalyse/en.md` | Analysis of the companies behind an application (Anstellungsgeber, Bedarfsträger, Vermittler, Kontaktgeber), source ranking, conflicts, storage in `analyse.md` and `firmen/`, and consequences for the documents (rules UA-1 … UA-9) |
| `spec/job-application/traumjob-interview/en.md` | Preference interview in seven phases, the stored Wunschprofil with priorities and Ausschlüsse, and the fit check of a posting or company against it, with vetoes and sourced results (rules WJ-1 … WJ-10) |
| `spec/job-application/lebenslauf/en.md` | Document type Lebenslauf: purpose, formats, sections and their order, entry shapes, Kurzprofil opt-in, Zeugnis entries, single-column layout, metadata, checks and scenarios (rules LB-1 … LB-16) |
| `spec/job-application/anschreiben/en.md` | Document type Anschreiben: purpose, components and order, DIN 5008 layout, Betreff and Anrede variants, text structure, length, variants, portal free-text fields, tone, checks (rules AS-1 … AS-15) |
| `spec/job-application/motivationsschreiben/en.md` | Document type Motivationsschreiben: difference to the Anschreiben, when to write it, where motivation may come from, structure, evidence for competences, length, variants, checks (rules MS-1 … MS-15) |
| `spec/job-application/lebenslauf-versionen/en.md` | Lebenslauf variants (Ausprägungen) in their own folders next to the Vorgänge, frozen versions in `versionen/`, manifest per export, byte-reproducible PDFs, what may be stored in a private repository (rules LV-1 … LV-11) |
| `spec/job-application/lokale-struktur/en.md` | Local structure of the Wurzel, the Anker `konfiguration.md` with its keys, where Stammdaten, Metadaten and Notizen are persisted, the Vorgang lifecycle S0–S10 with fixed status values and the retention rule, Markdown conventions and Obsidian (rules LS-1 … LS-10) |

Every skill under `skills/` names the spec section it obeys in its `SKILL.md`.
