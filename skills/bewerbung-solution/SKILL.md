---
name: bewerbung-solution
description: "Front door for a complete German-language job application (Bewerbung) for one concrete Stellenanzeige: checks the candidate profile, analyses the posting, then routes to the lebenslauf, anschreiben, and email skills in dependency order and finishes with the quality gate. Presents the plan and waits for approval before generating any document. Use on \"schreib mir eine Bewerbung für X\", \"erstelle meine Bewerbungsunterlagen\", \"Bewerbung für diese Stelle\", or equivalent German requests. Don't use for a single document (use the owning bewerbung-* skill), for a pure review of existing documents (bewerbung-pruefen or the bewerbungs-reviewer agent), or for interview preparation. Supports resume on re-invocation."
tags: [bewerbung, job-application, deutsch, dach, router]
phase: plan
summary: "Front-door router that turns one Stellenanzeige plus the candidate profile into a checked set of Bewerbungsunterlagen."
summary_de: "Oberster Einstieg, der aus einer Stellenanzeige und dem Kandidatenprofil ein geprüftes Set an Bewerbungsunterlagen erstellt."
use_when:
  - "you want a complete application for one specific job posting"
  - "you have a posting and want Lebenslauf, Anschreiben and E-Mail produced consistently"
dont_use_when:
  - situation: "You only need one document, such as a cover letter"
    alternative: bewerbung-anschreiben-erstellen
  - situation: "You want to review documents you already have"
    alternative: bewerbung-pruefen
  - situation: "You want the profile captured first, without a posting"
    alternative: bewerbung-profil-erfassen
see_also:
  - bewerbung-profil-erfassen
  - bewerbung-stellenanzeige-analysieren
  - bewerbung-lebenslauf-erstellen
  - bewerbung-anschreiben-erstellen
  - bewerbung-email-erstellen
  - bewerbung-pruefen
---

# Bewerbung Solution

Spec: `spec/bewerbung/konventionen/en.md` (rules R-1 … R-7). This skill owns no
document itself. It sequences the focused skills, threads the shared facts between
them, and enforces the quality gate.

## Inputs

| Field | Required | Default | Notes |
|---|---|---|---|
| `stellenanzeige` | yes | — | Posting text pasted by the user, or a file path. A URL is fetched only if the user asks; postings often block automated fetches. |
| `bewerbungsweg` | no | asked | `email`, `portal`, or `post`. Decides whether the E-Mail skill runs. |
| `ausrichtung` | no | `ausschreibung` | `ausschreibung`, `initiativ`, `quereinstieg`, or `berufseinstieg`. |
| `ziel_ordner` | no | `bewerbung/<firma-slug>-<stelle-slug>/` | Working folder, git-ignored. |

## Workflow

1. **Profile gate.** If `bewerbung/profil.md` is missing or older than the last
   career change the user mentions, run `bewerbung-profil-erfassen` first.
2. **Analysis.** Run `bewerbung-stellenanzeige-analysieren`. It produces the
   requirement-match table against the profile.
3. **Plan gate.** Present the plan: which documents, which open `[ERGÄNZEN]` gaps,
   which requirements are *teilweise* or *fehlt*, and the chosen tone (Sie / du).
   Wait for explicit approval. Do not generate anything before it.
4. **Lebenslauf**, then **Anschreiben**. The Lebenslauf goes first, so the cover
   letter references the same entries and dates.
5. **E-Mail**, only when `bewerbungsweg` is `email`.
6. **Quality gate.** Run `bewerbung-pruefen` on the folder. Fix blockers with the
   owning skill and re-run. Stop with the open blockers listed if the user does not
   resolve them.
7. **Hand-off.** Report the folder path, the verdict, and the remaining warnings. Do
   not export PDF or DOCX unless the user asks.

## Hard rules

1. **Plan before generate.** Step 3 is a hard gate.
2. **One posting, one run.** Never batch several applications into one run.
3. **Facts only from the profile** (spec R-1). Gaps become `[ERGÄNZEN: …]`.
4. **Consistency across documents.** Company, role, reference number and contact
   name are taken from the analysis and reused unchanged.
5. **Stop on blockers.** Do not declare the set ready while `bewerbung-pruefen`
   reports blockers.

## Resume

If `ziel_ordner` already holds documents, read them and continue at the first step
whose output is missing or outdated. Never overwrite a document the user has edited
without showing the diff first.
