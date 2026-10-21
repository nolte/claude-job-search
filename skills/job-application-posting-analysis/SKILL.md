---
name: job-application-posting-analysis
description: "Analyses one German-language Stellenanzeige: extracts role, company, reference number, contact person, must-have versus nice-to-have requirements, tone (Sie or du), and requested documents, then matches each requirement against job-application/profil.md with evidence and a status (erfüllt, teilweise, fehlt). Writes job-application/<slug>/analyse.md. Use on \"analysiere diese Stellenanzeige\", \"passt mein Profil zu dieser Stelle\", \"welche Anforderungen fehlen mir\", or equivalent German requests. Don't use for writing documents (job-application-cv-create, job-application-cover-letter-create), for the profile intake (job-application-profile-capture), or for a full application (job-application-solution)."
tags: [bewerbung, stellenanzeige, analyse, ats, deutsch]
phase: analyse
summary: "Extracts the requirements of a posting and matches them to the candidate profile with evidence."
summary_de: "Analysiert eine Stellenanzeige und gleicht die Anforderungen mit dem Profil ab, belegt durch Nachweise."
use_when:
  - "you have a posting and want to know how well your profile fits"
  - "you need the posting's wording and requirements before writing documents"
dont_use_when:
  - situation: "You want the whole application"
    alternative: job-application-solution
  - situation: "You have no profile yet"
    alternative: job-application-profile-capture
see_also:
  - job-application-solution
  - job-application-profile-capture
  - job-application-cover-letter-create
---

# Bewerbung Stellenanzeige analysieren

Spec: `spec/job-application/konventionen/en.md` R-1 (requirements may be *erfüllt* only with
profile evidence) and R-3 (tone and Anrede).

## Inputs

- The posting text, pasted or read from a file. Use a URL only when the user asks and
  when fetching works. If the fetch fails, ask the user to paste the text.
- `job-application/profil.md`. If it is missing, stop and point to `job-application-profile-capture`.

## Output

`job-application/<firma-slug>-<stelle-slug>/analyse.md`, with these sections:

1. **Stammdaten:** Stelle, Unternehmen, Standort / Remote, Referenznummer,
   Ansprechpartner (only if named in the posting), Eintrittstermin, Gehalt (only if stated).
2. **Bewerbungsweg und verlangte Unterlagen:** E-Mail, Portal, or Post; ATS-Hinweis,
   Europass-Forderung, Formatangabe, and the posting's country (for R-8.2 and R-8.5) as
   separate lines so the format choice can follow; required
   attachments such as Gehaltsvorstellung or Zeugnisse.
3. **Aufgaben** in the posting's own words, shortened.
4. **Anforderungen** split into *Muss* and *Wunsch*, as the posting states them.
5. **Abgleich** as a table:

   | Anforderung | Art | Nachweis im Profil | Status |
   |---|---|---|---|
   | Python, mehrjährig | Muss | Berufserfahrung: Backend-Entwickler, 2019–2023 | erfüllt |
   | Kubernetes | Wunsch | — | fehlt |

   Status values: `erfüllt` (evidence exists), `teilweise` (related evidence only),
   `fehlt` (no evidence). Evidence always names the profile section.
6. **Tonalität:** Sie or du, formal or informal, plus two or three phrases from the
   posting worth reusing where the profile supports them (ATS keywords, rule R-1.4).
7. **Unternehmensbezug:** facts the posting itself gives about the company (mission,
   product, values). Anything not in the posting is marked as to be researched.

## Hard rules

1. **No *erfüllt* without evidence** from the profile.
2. **Quote the posting exactly** for requirements and reference numbers. Do not paraphrase them.
3. **Name the gaps.** Every *fehlt* row is reported to the user with the option to
   address it honestly in the cover letter, not to claim it.
4. **Do not write application text.** Hand over to the writing skills.
