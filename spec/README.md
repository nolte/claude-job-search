# Specifications

Normative specifications for the skills and agents in this plugin. The canonical
language is English; German translations live beside them (`de.md`) once the
translation is produced via `/nolte-shared:spec`.

| Path | Governs |
|------|---------|
| `spec/job-application/konventionen/en.md` | DACH conventions for Lebenslauf, Anschreiben, E-Mail, Zeugnisse, data protection and the quality gate (rules R-1 … R-10) |
| `spec/job-application/cv-generierung/en.md` | CV content: source-of-truth model, target-specific selection, evidence mapping, controlled rewriting, length defaults, ATS and output consistency, quality-gate severities and acceptance scenarios (rules CG-1 … CG-14) |
| `spec/job-application/kontaktklassifikation/en.md` | Classification of the counterpart (recruiter, employer directly, referral, platform), each one's motivation, disclosure rules, and communication by counterpart (rules KK-1 … KK-9) |
| `spec/job-application/unternehmensanalyse/en.md` | Analysis of the companies behind an application (Anstellungsgeber, Bedarfsträger, Vermittler, Kontaktgeber), source ranking, conflicts, storage in `analyse.md` and `firmen/`, and consequences for the documents (rules UA-1 … UA-9) |
| `spec/job-application/traumjob-interview/en.md` | Preference interview in seven phases, the stored Wunschprofil with priorities and Ausschlüsse, and the fit check of a posting or company against it, with vetoes and sourced results (rules WJ-1 … WJ-10) |
| `spec/job-application/lokale-struktur/en.md` | Local structure of the Wurzel, where Stammdaten, Metadaten and Notizen are persisted, the Vorgang lifecycle S0–S9, Markdown conventions and Obsidian (rules LS-1 … LS-10) |

Every skill under `skills/` names the spec section it obeys in its `SKILL.md`.
