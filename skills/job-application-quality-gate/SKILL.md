---
name: job-application-quality-gate
description: "Quality gate for a Vorgang folder: checks completeness, identical role, company and reference data across documents, traceability of every claim to the Datengrundlage via <wurzel>/profil.md, German spelling and grammar, page limits, attachment size, leftover [ERGÄNZEN] placeholders, status consistency in vorgang.md, and attachment names. Writes the section `## Prüfung` of <wurzel>/<slug>/pruefbericht.md with Blocker, Warnungen and Hinweise. Use on \"prüfe meine Bewerbung\", \"ist die Bewerbung versandfertig\", \"check die Unterlagen\", or equivalent German requests. Don't use to write or rewrite documents (use the owning skill), or for an independent whole-set review (use the job-application-reviewer agent)."
tags: [bewerbung, pruefung, qualitaet, deutsch]
phase: review
summary: "Quality gate that reports blockers, warnings and notes for one application folder before it is sent."
summary_de: "Qualitätsprüfung eines Bewerbungsordners mit Blockern, Warnungen und Hinweisen, bevor er versendet wird."
use_when:
  - "you have a set of application documents and want to know whether they are ready to send"
  - "you changed one document and need to confirm consistency"
dont_use_when:
  - situation: "You want the documents written or rewritten"
    alternative: job-application-solution
  - situation: "You want an independent, read-only review of the full set"
    alternative: job-application-reviewer
see_also:
  - job-application-reviewer
  - job-application-solution
---

# Bewerbung prüfen

Spec: `spec/job-application/konventionen/en.md` R-1 … R-7. R-7 defines what "ready to send" means.
Content checks and severities: `spec/job-application/cv-generierung/en.md` CG-12 (export consistency),
CG-13 (severities, criteria, reproducibility) and CG-13.4 (scope of the automated checks). Letter checks:
`spec/job-application/anschreiben/en.md` AS-12. Paths, Vorgang and status: `spec/job-application/lokale-struktur/en.md`
LS-2.6, LS-5.4, LS-6. Page limits: `spec/job-application/lebenslauf/en.md` LB-2.3, AS-7.1.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`),
`grundlage` and `grundlage_index` from its frontmatter. Relative paths resolve against the working directory that
contains `job-application/konfiguration.md` (LS-2.6).

## Inputs

- The Vorgang folder `<wurzel>/<slug>/` with `analyse.md`, `vorgang.md`, `stellenanzeige.md` and the documents
  (`lebenslauf.md`, `anschreiben.md`, `anschreiben-portal.txt`, `motivationsschreiben.md`, `email.md`), plus `export/`
  if it exists.
- `<wurzel>/profil.md` in the Wurzel.
- The Datengrundlage (Grundlage, key `grundlage`), the source of every claim (CG-2).
- An Ausprägungsordner `<wurzel>/<ausprägung>/` (for example `lebenslauf-basis`) holds a Lebenslauf without a posting and
  has no `vorgang.md`, `analyse.md` or letter. The gate then runs the Lebenslauf checks only and skips the status checks.

## Language of the report

One language per artefact (D14): this instruction is English; the report `pruefbericht.md` is German. Severities in the
report are `Blocker`, `Warnung`, `Hinweis`; the verdict is `Ergebnis: BLOCKIERT | BEREIT MIT WARNUNGEN | BEREIT`.

| Report (quality gate) | Reviewer agent (`job-application-reviewer`) | Effect |
|---|---|---|
| Blocker | critical | `BLOCKIERT` |
| Warnung | major | `BEREIT MIT WARNUNGEN` |
| Hinweis | minor | none |

## Automated checks

Run the deterministic checks first. They produce the same output for the same input:

```bash
python3 <plugin-root>/scripts/cv_checks.py <wurzel>/<slug>/lebenslauf.md \
  --grundlage <Grundlage> --analyse <wurzel>/<slug>/analyse.md [--ats]
```

In directory mode pass `--grundlage <Verzeichnis> --grundlage <grundlage_index>` (the option is repeatable).
`<plugin-root>` is the plugin directory, two levels above this skill's base directory. The
script prints JSON with rule IDs, severities, file, line and quoted passage, and exits 1 when
a Blocker exists. Its rule IDs:

| Rule | Check | Severity |
|---|---|---|
| CV-01 | Placeholder `[ERGÄNZEN` or `[KLÄREN` left | Blocker |
| CV-02 | Station header not in form `MM/JJJJ – MM/JJJJ \| Position \| Arbeitgeber, Ort`, or a month missing (years only) | Warnung |
| CV-03 | More than 5 bullets, or a station without bullets | Warnung, Hinweis |
| CV-04 | Stations not reverse chronological; end before start | Warnung, Blocker |
| CV-05 | Number in a bullet not in the station record: Hinweis when it is elsewhere in the Grundlage, Blocker when nowhere | Hinweis, Blocker |
| CV-06 | Station period differs from the Grundlage | Blocker |
| CV-07 | *Muss* row marked *erfüllt* without evidence; *Muss* gap as report | Blocker, Warnung |
| CV-08 | Table in the Lebenslauf | Warnung (Blocker with `--ats`) |
| CV-09 | Duplicate bullet | Hinweis |
| CV-10 | Heading outside the standard headings (CG-11.2a), qualifier in parentheses allowed | Warnung |
| CV-11 | Generic or evaluative phrase (CG-8.2.3) | Warnung |
| CV-12 | Bullet longer than two lines | Hinweis |
| — | Bullet form not as CG-8.1 (subject, finite verb, final period, list longer than two items) (judged in review) | Warnung |
| CV-13 | Employment gap over two months without a neutral entry between the two stations | Blocker |
| CV-14 | Invalid status or strength in the analysis (e.g. `fehlt`) | Warnung |
| CV-15 | Station title or employer not in the Grundlage (note `titel` and `arbeitgeber`, or an R-2.1 header) | Blocker (Warnung if the Grundlage has no station records) |
| CV-16 | Personnel-leadership wording (`Teamleitung`, `Personalverantwortung`, `disziplinarisch`, `geleitet` with Team, Mitarbeiter or Abteilung) without `fuehrung: ja` | Blocker with `fuehrung: nein`; Warnung when `ungeklärt` or missing (CG-13.4) |
| CV-17 | Sub-bullets below a bullet (R-2.1) | Hinweis |

Checks that need judgement stay in the review: ownership, leadership, expertise and proficiency
wording (CG-7.2), relevance of selection (CG-5), seniority and role positioning, language and
country conventions, employer instructions, and the requested format.

## Checks

| Check | Severity when it fails |
|---|---|
| `[ERGÄNZEN` or `[KLÄREN` placeholder left in any document: `lebenslauf.md`, `anschreiben.md`, `anschreiben-portal.txt`, `motivationsschreiben.md`, `email.md` | Blocker |
| Required document missing (Lebenslauf, Anschreiben, Motivationsschreiben if asked for, E-Mail if `email`, `anschreiben-portal.txt` if `portal`, Zeugnisse if requested) | Blocker |
| Motivationsschreiben: a statement of motivation without a source in `## Auswahl Motivationsschreiben` (user statement or confirmed Wunschprofil entry), or `[ERGÄNZEN: Beweggrund]` left (MS-3) | Blocker |
| Motivationsschreiben: a competence without a proof, or text that retells the Lebenslauf (MS-6.1, MS-5.3) | Warnung |
| Company, role, reference number, or contact name differ between documents, or between the documents and `vorgang.md` | Blocker |
| Claim in a document not traceable to the Grundlage entry (R-1, CG-2) | Blocker |
| Muss requirement presented as *erfüllt* without evidence (CV-07) | Blocker |
| Employer instruction that is mandatory and not met (CG-11.6) | Blocker; a recommendation that is not met is a Warnung |
| Requested document format not produced (R-8.4, CG-11.5) | Blocker |
| Export content differs from the approved Markdown (CG-12.2) | Blocker |
| Anstellungsgeber `unbekannt` where a document needs it (UA-6.1) | Blocker |
| Letter addressed to a Vermittler, or naming an Auftraggeber or Anstellungsgeber that the counterpart has not disclosed (KK-4.1, UA-6.2) | Blocker |
| Application to the same Anstellungsgeber or Auftraggeber through two channels without the user's decision (KK-4.2) | Blocker |
| Documents sent to a counterpart the candidate has not approved for it (KK-7.1) | Blocker |
| Company fact in a document that has no source in `analyse.md`, or comes from a rating portal (UA-2.1, UA-4.5) | Blocker |
| `analyse.md` without the classification keys of KK-6, or without the section `## Unternehmen` (UA-5.1) | Warnung |
| Counterpart is a Vermittler with confidence `unklar`, and the Auftraggeber question has not been asked (KK-3.3) | Warnung |
| E-Mail attachment list names a file that is not in the folder | Blocker |
| Anschreiben longer than one page (AS-7.1; page count from the PDF in `export/` when present, otherwise about 400+ words) | Blocker; an exception needs the user's decision recorded in `## Prüfung` |
| Lebenslauf longer than two pages (LB-2.3; page count from the PDF in `export/` when present) | Blocker; an exception needs the user's decision recorded in `## Prüfung` |
| Attachments in `export/` larger than 5 MB in total (R-4, D3) | Warnung from 5 MB, Blocker from 10 MB |
| Attachment file name not ASCII (`ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`, no spaces) or not `Vorname_Nachname_<Dokument>.pdf` (R-4) | Warnung |
| Betreff of Anschreiben or E-Mail carries a gender suffix such as `(m/w/d)` (AS-4) | Warnung |
| `vorgang.md` missing in a Vorgang folder, or its `status` not one of the LS-6 values | Warnung |
| `status` inconsistent with the documents: `erstellt` or later without `lebenslauf.md`, `geprüft` with open Blocker, `erfasst` or `analysiert` with documents present (LS-6) | Warnung |
| `grundlage_hash` in `vorgang.md` differs from the current hash, or a document's `grundlage_hash` differs from `vorgang.md` (LS-5.4) | Warnung: stale, re-derive |
| Mixed date formats or inconsistent Zeiträume | Warnung |
| Spelling or grammar errors in German text | Warnung |
| Anrede not matching the Ansprechperson, generic (`Sehr geehrte Damen und Herren`) when a name is known, or not following AS-5.6 to AS-5.8 (Sie default, du form only when the posting uses du, `Guten Tag <Vorname Nachname>` when the gender is not clear, academic title taken over) | Warnung |
| Requirement marked *Muss* in the analysis not addressed in the Anschreiben | Warnung |
| Stock phrase ("hiermit bewerbe ich mich") | Warnung |
| Kurzprofil longer than three sentences, or missing in `kombiniert` (D8) | Warnung |
| Optional personal data present without the user's request | Hinweis |
| Number in a bullet not in the Grundlage or a certificate (R-1, R-2.1, CV-05) | Blocker |
| Output `grundlage_hash` differs from the current Grundlage hash (R-9.5; the hash comes from `scripts/grundlage_hash.py`) | Warnung: stale, re-derive |
| `scripts/grundlage_hash.py` stops with a `Blocker:` line (missing `grundlage_index`, missing or invalid `stand`, Grundlage inside the plugin repository) (R-9.5, R-9.9, R-9.10) | Blocker |
| Eintragsblock not in header-line form, or bullets outside 1–5 per station (R-2.1) | Warnung |
| Table or multi-column layout in a CV (R-8.3) | Warnung; Blocker if the posting requires ATS |
| Photo present in an ATS or portal application (R-8.2) | Warnung |
| Europass or academic CV required by the posting but not produced (R-8.4) | Blocker |
| Lebenslauf not matching the format chosen for the situation (R-8.1) | Warnung |
| Missing Ort, Datum, or Unterschrift line where R-2 expects them | Hinweis |

## Output

The section `## Prüfung` of `<wurzel>/<slug>/pruefbericht.md` (D9). Create the file if it is missing. A run replaces
only this section and leaves `## Auswahl Lebenslauf`, `## Auswahl Anschreiben` and `## Auswahl Motivationsschreiben`
unchanged.

```markdown
## Prüfung

Stand: JJJJ-MM-TT · Ergebnis: BLOCKIERT | BEREIT MIT WARNUNGEN | BEREIT

### Blocker
- [ ] <Dokument>: <Befund> — <Vorschlag>

### Warnungen
- [ ] …

### Hinweise
- …

### Entscheidungen des Nutzers
- JJJJ-MM-TT: <Ausnahme, zum Beispiel Lebenslauf drei Seiten, Grund>
```

`BEREIT` requires zero Blocker and zero Warnungen. `BEREIT MIT WARNUNGEN` requires zero Blocker. Any Blocker means
`BLOCKIERT`. A user's exception (page limit) is recorded under `### Entscheidungen des Nutzers` and removes the Blocker
for that run only.

## Workflow

1. Read `vorgang.md`, the analysis and the profile first, then each document.
2. Run the automated checks, then the checks of the table above. Quote the exact passage for every finding.
3. Write `## Prüfung`. Show the user the Ergebnis and the Blocker in chat as well.
4. **Status** (LS-6, S5). In a Vorgang folder set `status: geprüft` when zero Blocker remain, otherwise `in Arbeit`, and
   append `- JJJJ-MM-TT: <alter Status> → <neuer Status>, job-application-quality-gate` to `## Verlauf`. Skip this in an
   Ausprägungsordner.
5. Fix blockers only with the user's agreement, through the owning skill.

## Hard rules

1. **Report, do not silently fix.** Edits to the documents happen only through the owning skill.
2. **Every finding quotes its source** with the file name and the passage.
3. **Traceability is strict.** A claim the report cannot find in the Grundlage, through `profil.md`, is a Blocker,
   even if it sounds plausible.
4. **German report, German severities.** No English severity words or verdicts in `pruefbericht.md`.
5. **Only the Wurzel is written** (LS-5.7): `pruefbericht.md` and `vorgang.md` of this Vorgang.
