---
name: job-application-quality-gate
description: "Quality gate for an application folder: checks completeness, identical role, company and reference data across documents, traceability of every claim to job-application/profil.md, German spelling and grammar, length limits, leftover [ERGÄNZEN] placeholders, and attachment names. Writes job-application/<slug>/pruefbericht.md with blockers, warnings, and notes. Use on \"prüfe meine Bewerbung\", \"ist die Bewerbung versandfertig\", \"check die Unterlagen\", or equivalent German requests. Don't use to write or rewrite documents (use the owning skill), or for an independent whole-set review (use the job-application-reviewer agent)."
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
Content checks and severities: `spec/job-application/cv-generierung/en.md` CG-12 (export consistency)
and CG-13 (severities, criteria, reproducibility).

## Inputs

- The folder `job-application/<slug>/`, with `profil.md` and `analyse.md` in `job-application/`
  and the documents in the slug folder.
- The Grundlage (path from `job-application/konfiguration.md`), the source of every claim (CG-2).

## Automated checks

Run the deterministic checks first. They produce the same output for the same input:

```bash
python3 <plugin-root>/scripts/cv_checks.py job-application/<slug>/lebenslauf.md \
  --grundlage <Grundlage> --analyse job-application/<slug>/analyse.md [--ats]
```

`<plugin-root>` is the plugin directory, two levels above this skill's base directory. The
script prints JSON with rule IDs, severities, file, line and quoted passage, and exits 1 when
a Blocker exists. Its rule IDs:

| Rule | Check | Severity |
|---|---|---|
| CV-01 | Placeholder `[ERGÄNZEN` or `[KLÄREN` left | Blocker |
| CV-02 | Station header not in form `MM/JJJJ – MM/JJJJ \| Position \| Arbeitgeber, Ort` | Warnung |
| CV-03 | More than 5 bullets, or a station without bullets | Warnung, Hinweis |
| CV-04 | Stations not reverse chronological; end before start | Warnung, Blocker |
| CV-05 | Number in a bullet not found in the Grundlage | Blocker |
| CV-06 | Station period differs from the Grundlage | Blocker |
| CV-07 | *Muss* row marked *erfüllt* without evidence; *Muss* gap as report | Blocker, Warnung |
| CV-08 | Table in the Lebenslauf | Warnung (Blocker with `--ats`) |
| CV-09 | Duplicate bullet | Hinweis |
| CV-10 | Heading outside the standard headings (CG-11.2a) | Warnung |
| CV-11 | Generic phrase that hides the task | Hinweis |
| CV-12 | Bullet longer than two lines | Hinweis |
| CV-13 | Employment gap over two months without a gap entry | Blocker |
| CV-14 | Invalid status or strength in the analysis (e.g. `fehlt`) | Warnung |
| CV-15 | Station title or employer not in the Grundlage (note `titel` and `arbeitgeber`, or an R-2.1 header) | Blocker (Warnung if the Grundlage has no station records) |
| CV-16 | Leadership wording (`geleitet`, `Teamleitung`, `führte` and similar) without `fuehrung: ja` in the station note | Blocker |

Checks that need judgement stay in the review: ownership, leadership, expertise and proficiency
wording (CG-7.2), relevance of selection (CG-5), seniority and role positioning, language and
country conventions, employer instructions, and the requested format.

## Checks

| Check | Severity when it fails |
|---|---|
| `[ERGÄNZEN` placeholder left in any document | Blocker |
| Required document missing (Lebenslauf, Anschreiben, E-Mail if `email`, Zeugnisse if requested) | Blocker |
| Company, role, reference number, or contact name differ between documents | Blocker |
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
| Anschreiben longer than one page (about 400+ words) | Warning |
| Lebenslauf longer than two pages | Warning |
| Mixed date formats or inconsistent Zeiträume | Warning |
| Spelling or grammar errors in German text | Warning |
| Anrede not matching the Ansprechpartner, or generic when a name is known | Warning |
| Requirement marked *Muss* in the analysis not addressed in the Anschreiben | Warning |
| Stock phrase ("hiermit bewerbe ich mich") | Warning |
| Optional personal data present without the user's request | Note |
| Number in a bullet not in the Grundlage or a certificate (R-1, R-2.1, CV-05) | Blocker |
| Output `grundlage_hash` differs from the current Grundlage hash (R-9.5; the hash comes from `scripts/grundlage_hash.py`) | Warning: stale, re-derive |
| `scripts/grundlage_hash.py` stops with a `Blocker:` line (missing `grundlage_index`, missing or invalid `stand`, Grundlage inside the plugin repository) (R-9.5, R-9.9, R-9.10) | Blocker |
| Eintragsblock not in header-line form, or bullets outside 1–5 per station (R-2.1) | Warning |
| Table or multi-column layout in a CV (R-8.3) | Warning; blocker if the posting requires ATS |
| Photo present in an ATS or portal application (R-8.2) | Warning |
| Europass or academic CV required by the posting but not produced (R-8.4) | Blocker |
| Lebenslauf not matching the format chosen for the situation (R-8.1) | Warning |
| Missing Ort, Datum, or Unterschrift line where R-2 expects them | Note |

## Output

`job-application/<slug>/pruefbericht.md`:

```markdown
# Prüfbericht — <Stelle> (<Firma>)

Stand: YYYY-MM-DD · Verdict: BLOCKED | READY-WITH-WARNINGS | READY

## Blocker
- [ ] <Dokument>: <Befund> — <Vorschlag>

## Warnungen
- [ ] …

## Hinweise
- …
```

`READY` requires zero blockers and zero warnings. `READY-WITH-WARNINGS` requires zero
blockers. Any blocker means `BLOCKED`.

## Workflow

1. Read the analysis and the profile first, then each document.
2. Run the checks above. Quote the exact passage for every finding.
3. Write the report. Show the user the verdict and the blockers in chat as well.
4. Fix blockers only with the user's agreement, through the owning skill.

## Hard rules

1. **Report, do not silently fix.** Edits to the documents happen only through the owning skill.
2. **Every finding quotes its source** with the file name and the passage.
3. **Traceability is strict.** A claim the report cannot find in `profil.md` is a blocker,
   even if it sounds plausible.
