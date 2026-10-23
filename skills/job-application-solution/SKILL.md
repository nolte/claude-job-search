---
name: job-application-solution
description: "Front door for a complete German-language job application (Bewerbung) for one concrete Stellenanzeige: checks the candidate profile, analyses the posting, then routes to the lebenslauf, anschreiben, and email skills in dependency order and finishes with the quality gate. Presents the plan and waits for approval before generating any document. Use on \"schreib mir eine Bewerbung für X\", \"erstelle meine Bewerbungsunterlagen\", \"Bewerbung für diese Stelle\", or equivalent German requests. Don't use for a single document (use the owning job-application-* skill), for a pure review of existing documents (job-application-quality-gate or the job-application-reviewer agent), or for interview preparation (no skill yet, see roadmap). Supports resume on re-invocation."
tags: [bewerbung, job-application, deutsch, dach, router]
phase: plan
summary: "Front-door router that turns one Stellenanzeige plus the candidate profile into a checked set of Bewerbungsunterlagen."
summary_de: "Oberster Einstieg, der aus einer Stellenanzeige und dem Kandidatenprofil einen geprüften Satz Bewerbungsunterlagen erstellt."
use_when:
  - "you want a complete application for one specific job posting"
  - "you have a posting and want Lebenslauf, Anschreiben and E-Mail produced consistently"
dont_use_when:
  - situation: "You only need one document, such as a cover letter"
    alternative: job-application-cover-letter-create
  - situation: "You want to review documents you already have"
    alternative: job-application-quality-gate
  - situation: "You want the profile captured first, without a posting"
    alternative: job-application-profile-capture
see_also:
  - job-application-profile-capture
  - job-application-posting-analysis
  - job-application-cv-create
  - job-application-cover-letter-create
  - job-application-email-create
  - job-application-quality-gate
---

# Bewerbung Solution

Spec: `spec/job-application/konventionen/en.md` (rules R-1 … R-7). Paths, Vorgang and status:
`spec/job-application/lokale-struktur/en.md` LS-2.6, LS-5.4, LS-6. This skill owns no document itself. It sequences
the focused skills, threads the shared facts between them, and enforces the quality gate.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`),
`grundlage` and `grundlage_index` from its frontmatter. Relative paths resolve against the working directory that
contains `job-application/konfiguration.md` (LS-2.6). The Datengrundlage (Grundlage) is the file or directory named by
`grundlage`; `<wurzel>/profil.md` is its derivation; `<wurzel>/<slug>/` is the Vorgang folder of this application.

## Inputs

| Field | Required | Default | Notes |
|---|---|---|---|
| `stellenanzeige` | yes | — | Posting text pasted by the user, or a file path. A URL is fetched only if the user asks; postings often block automated fetches. |
| `bewerbungsweg` | no | asked | `email`, `portal`, or `post`. Decides whether the E-Mail skill runs and whether the Anschreiben gets a portal copy (AS-8.1). |
| `ausrichtung` | no | `ausschreibung` | `ausschreibung`, `initiativ`, `quereinstieg`, `berufseinstieg`, or `vermittler`. |
| `ziel_ordner` | no | `<wurzel>/<firma-slug>-<stelle-slug>/` | The Vorgang folder (LS-3). A second Vorgang for the same company and role gets a numeric suffix (LS-6 rule 6). |

## Workflow

1. **Grundlage gate.** If the Grundlage (key `grundlage`; default `<wurzel>/grundlage/lebenslauf-chronologisch.md`) is
   missing, run `job-application-profile-capture` first (it builds the Grundlage, then the profile, spec R-9). If the
   Grundlage exists but `<wurzel>/profil.md` is missing or its `grundlage_hash` differs from the current hash (`hash` of
   `python3 <plugin-root>/scripts/grundlage_hash.py job-application/konfiguration.md`, spec R-9.5), re-derive the profile
   with `job-application-profile-capture` before continuing. `<plugin-root>` is the plugin directory, two levels above
   this skill's base directory.
2. **Analysis.** Run `job-application-posting-analysis`. It creates the Vorgang folder with `stellenanzeige.md`,
   `vorgang.md` (status `erfasst`, then `analysiert`), `notizen.md` and `analyse.md` (LS-6, S1 and S2), and produces the
   requirement-match table against the profile, the counterpart classification (KK-6 keys), the section `## Unternehmen`
   with the firm roles (UA-5.1), and the double-submission check (KK-4.2). If a confirmed `wunschprofil.md` exists in
   the Wurzel, also run `job-application-fit-check`. A veto in its result stops the plan gate in step 3 until the
   candidate decides (WJ-7.1). Without a Wunschprofil, skip the check and say so in the plan.
3. **Plan gate.** Present the plan: which documents, the format per document from the situation (spec R-8.1:
   chronologisch, einseitig, kombiniert, ats), the page limits (Lebenslauf two pages, LB-2.3; Anschreiben one page,
   AS-7.1; both are Blocker for the quality gate, an exception only with the user's decision recorded in
   `pruefbericht.md`), the question whether a Kurzprofil is wanted (optional in every format, required in `kombiniert`,
   at most three sentences), a Foto question for Österreich only (R-8.2), which open `[ERGÄNZEN]` gaps, which
   requirements are *teilweise*, *nicht belegt* or *unklar* (CG-4), and the chosen tone (Sie / du) with the Anrede
   (AS-5.6 to AS-5.8). A posting that requires Europass or an academic CV is shown as a blocker here (R-8.4). The plan
   also shows the counterpart (`kontaktart`, `auftraggeber`, confidence), the Anstellungsgeber and its source (UA-6.1),
   any disclosure still missing (KK-4.1), and any double submission found (KK-4.2). Wait for explicit approval. Do not
   generate anything before it. **After approval**, write the plan as the section `## Plan` of `vorgang.md`, set
   `status: geplant`, and append `- JJJJ-MM-TT: analysiert → geplant, job-application-solution` to `## Verlauf`
   (LS-6, S3).
4. **Lebenslauf**, then **Anschreiben**, then **Motivationsschreiben** only when the posting or the programme asks for
   it (MS-2, `job-application-motivation-letter-create`). The Lebenslauf goes first, so the letters reference the same
   entries and dates. The plan in step 3 states which letters are written. Each skill sets `status: erstellt` and its
   `## Verlauf` line (LS-6, S4).
5. **E-Mail**, only when `bewerbungsweg` is `email`.
6. **Quality gate.** Run `job-application-quality-gate` on the folder. It sets `status: geprüft` (zero Blocker) or
   `in Arbeit`. Fix blockers with the owning skill and re-run. Stop with the open blockers listed if the user does not
   resolve them.
7. **Hand-off.** Report the folder path, the verdict, and the remaining warnings. Do not export PDF or DOCX unless the
   user asks.

## Hard rules

1. **Plan before generate.** Step 3 is a hard gate, and `## Plan` in `vorgang.md` is written before S4 starts (LS-6 rule 3).
2. **One posting, one run.** Never batch several applications into one run.
3. **Facts only from the Grundlage**, through the profile (spec R-1). Gaps become `[ERGÄNZEN: …]`.
4. **Consistency across documents.** Company, role, reference number and contact name are taken from the analysis and
   reused unchanged.
5. **Stop on blockers.** Do not declare the set ready while `job-application-quality-gate` reports blockers.
6. **Disclosure before documents.** No document goes to a counterpart whose Auftraggeber or Anstellungsgeber is not
   disclosed, and no unresolved double submission is passed on (KK-4, UA-6). The plan states this as an open point
   until the user decides.
7. **Only the Wurzel is written** (LS-5.7).

## Resume

If `ziel_ordner` already exists, read `vorgang.md` first: its `status` names the last completed stage (LS-6), and
`## Verlauf` names the skills that ran. Continue at the first stage after that status. Then compare the `grundlage_hash`
of every derivation that exists (`profil.md`, `lebenslauf.md`, `anschreiben.md`, `motivationsschreiben.md`,
`email.md`, `vorgang.md`) with the current hash (LS-5.4); a stale derivation is re-derived by its owning skill, never
patched by hand. Without `vorgang.md` (a folder created before S1 existed), derive the stage from the documents present
and say so. Never overwrite a document the user has edited without showing the diff first.
