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
profile evidence) and R-3 (tone and Anrede). The matrix format, status values and evidence
strength are defined in `spec/job-application/cv-generierung/en.md` CG-4. The counterpart is
classified by `spec/job-application/kontaktklassifikation/en.md` (KK-3, KK-6). The companies
behind the application are analysed and recorded by `spec/job-application/unternehmensanalyse/en.md`
(UA-4, UA-5).

## Inputs

- The posting text, pasted or read from a file. Use a URL only when the user asks and
  when fetching works. If the fetch fails, ask the user to paste the text.
- `job-application/profil.md`. If it is missing, stop and point to `job-application-profile-capture`.
- The Grundlage (path from `job-application/konfiguration.md`, CG-2). Every `Nachweis` cites a Grundlage entry, so the
  Grundlage is read for the evidence and the profile for the overview.
- The message or signature the posting came with, if any, and what the user knows about the sender. This is the
  basis of the counterpart classification (KK-3.1). The user can answer the classification questions instead.

## Output

`job-application/<firma-slug>-<stelle-slug>/analyse.md`, with these sections:

1. **Stammdaten:** Stelle, Unternehmen, Standort / Remote, Referenznummer,
   Ansprechpartner (only if named in the posting), Eintrittstermin, Gehalt (only if stated).
   The frontmatter of `analyse.md` carries the classification keys of item 8 and the
   company roles of item 9.
2. **Bewerbungsweg und verlangte Unterlagen:** E-Mail, Portal, or Post; ATS-Hinweis,
   Europass-Forderung, Formatangabe, and the posting's country (for R-8.2 and R-8.5) as
   separate lines so the format choice can follow; required
   attachments such as Gehaltsvorstellung or Zeugnisse.
3. **Aufgaben** in the posting's own words, shortened.
4. **Anforderungen** split into *Muss* and *Wunsch*, as the posting states them.
5. **Abgleich** as a table with exactly these columns (CG-4):

   | Anforderung | Priorität | Kompetenz | Nachweis | Stärke | Status | Verwendung |
   |---|---|---|---|---|---|---|
   | „Python, mehrjährige Erfahrung“ | Muss | Python | Grundlage „<Stationsüberschrift>“ (`<Datei>.md#<Station>`): „<Zitat>“ | stark | erfüllt | Lebenslauf |
   | „Kubernetes“ | Wunsch | Kubernetes-Betrieb | — | — | nicht belegt | Rückfrage |

   - `Priorität`: `Muss`, `Wunsch`, or `Kontext`.
   - `Nachweis`: the Grundlage entry (file and heading) and the quoted phrase; `—` when none.
   - `Stärke`: `stark` (task with scope and result), `mittel` (task, no result), `schwach` (mention only), `—` (none).
   - `Status`: `erfüllt` needs `mittel` or `stark`; `teilweise` for related or partial evidence;
     `nicht belegt` when no evidence was found; `unklar` when posting or evidence is ambiguous.
   - `Verwendung`: `Lebenslauf`, `Anschreiben`, `Vorbereitung`, or `Rückfrage`.
6. **Tonalität:** Sie or du, formal or informal, plus two or three phrases from the
   posting worth reusing where the profile supports them (ATS keywords, rule R-1.4).
7. **Unternehmensbezug:** facts the posting itself gives about the company (mission,
   product, values). Anything not in the posting is marked as to be researched.
8. **Kontakt (KK-3, KK-6).** Classify the counterpart as one value of KK-2 (Direkt: Personalabteilung,
   Direkt: Fachbereich, Direkt: Geschäftsführung, Personalberatung / Headhunter, Personalvermittlung / Zeitarbeit,
   Empfehlung (intern), Job-Portal / Plattform, Unklar). Name the signals with their source (KK-3.1).
   - Two independent signals agree before a class is *wahrscheinlich*. A fee signal (Provision, Erfolgshonorar) or an
     agency signature puts the counterpart in a Vermittler class. No signal means *unklar*; then ask the user, and do
     not guess.
   - Write the frontmatter block at the top of `analyse.md`:

     ```yaml
     kontaktart: <KK-2 value or Unklar>
     auftraggeber: <name, or unbekannt>
     kontakt_konfidenz: gesichert | wahrscheinlich | unklar
     kontakt_signale:
       - "<signal>: <source>"
     exklusiv: ja | nein | unbekannt
     ```

   - Ask the user to confirm the Auftraggeber and the exclusivity status when the counterpart is a Vermittler (KK-3.3).
     A reply that names the employer is recorded with its date; a refusal lowers the confidence.
9. **Unternehmen (UA-4, UA-5).** Identify the firm roles from the posting and the classification (UA-1): Anstellungsgeber,
   Bedarfsträger, Vermittler, Kontaktgeber, Muttergesellschaft. Then write the section `## Unternehmen`:
   - a table with the columns `Firma | Rolle | Identität | Quelle | Konfidenz | Stand`, one row per firm and role;
   - under each firm, short lines for the dimensions of UA-2, each with its source and date. Mark a dimension
     `nicht ermittelt` when no source gives it. Never fill it from memory.
   - Identity comes from rank 1 to 3 sources of UA-3, or stays `unbekannt`. Two conflicting values are both recorded with
     their sources, and the conflict is flagged. It is not resolved silently.
   - Web research only when the user asks, with the company name and a generic term in the query. Never candidate
     data or text of the application (UA-3.3).
   - Firm files: on first use create `<wurzel>/firmen/<firma-slug>.md` with the keys of LS-6.2 and `rollen`,
     `identitaet_quelle`, `identitaet_stand` (UA-5.2). An existing file is updated in its identity fields only after the
     user confirms. Its `## Notizen` body is never touched (LS-5.6).
   - A re-run replaces the section and records the old `Stand` in `Verlauf` of `vorgang.md` (UA-5.1).

## Hard rules

1. **No *erfüllt* without evidence** from the profile.
2. **Quote the posting exactly** for requirements and reference numbers. Do not paraphrase them.
3. **Name the gaps.** Every *nicht belegt* or *teilweise* *Muss* row is reported to the user, with its
   `Verwendung` (`Anschreiben` or `Rückfrage`), so it can be addressed honestly. It is never claimed.
4. **Not evidenced is not lacking.** *nicht belegt* means no evidence was found in the Grundlage. The row must
   never say the candidate lacks the competency, and the word *fehlt* is not used (CG-4.3).
5. **Muss without evidence is never *erfüllt*.** A *Muss* row needs *mittel* or *stark* evidence for *erfüllt* (CG-4.1, CG-4.5).
6. **Do not write application text.** Hand over to the writing skills.
7. **Disclosure.** When the counterpart is a Vermittler and the Auftraggeber is not disclosed, the analysis says so, and
   the Anstellungsgeber is not presented as the addressee (KK-4.1, UA-6.2).
8. **Double submission.** Look for other Vorgänge in `<wurzel>/` with the same Anstellungsgeber or Auftraggeber. Any match
   is reported to the user before the plan is approved, with the channel of each application (KK-4.2).
9. **Reputation is opinion.** Rating-portal statements are never written into a Stammdatum or a document (UA-2.1).
