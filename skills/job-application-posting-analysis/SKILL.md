---
name: job-application-posting-analysis
description: "Analyses one German-language Stellenanzeige: creates the Vorgang folder (stellenanzeige.md, vorgang.md, notizen.md), extracts role, company, reference number, contact person, must-have versus nice-to-have requirements, tone (Sie or du), and requested documents, then matches each requirement against <wurzel>/profil.md with evidence and a status (erfüllt, teilweise, nicht belegt, unklar). Writes <wurzel>/<slug>/analyse.md. Use on \"analysiere diese Stellenanzeige\", \"passt mein Profil zu dieser Stelle\", \"welche Anforderungen fehlen mir\", or equivalent German requests. Don't use for writing documents (job-application-cv-create, job-application-cover-letter-create), for the profile intake (job-application-profile-capture), or for a full application (job-application-solution)."
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
(UA-4, UA-5). The Vorgang folder, its files and its status come from `spec/job-application/lokale-struktur/en.md`
(LS-2.6 paths, LS-3 layout, LS-6 lifecycle S1 and S2, LS-6.1 to LS-6.3).

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`),
`grundlage` and `grundlage_index` from its frontmatter. Relative paths resolve against the working directory that
contains `job-application/konfiguration.md` (LS-2.6). The Vorgang folder is `<wurzel>/<firma-slug>-<stelle-slug>/`; a
second Vorgang for the same company and role gets a numeric suffix (LS-6 rule 6). Folders are never moved after S1.

## Inputs

- The posting text, pasted or read from a file. Use a URL only when the user asks and
  when fetching works. If the fetch fails, ask the user to paste the text.
- `<wurzel>/profil.md`. If it is missing, stop and point to `job-application-profile-capture`.
- The Datengrundlage (Grundlage, key `grundlage`, CG-2). Every `Nachweis` cites a Grundlage entry, so the
  Grundlage is read for the evidence and the profile for the overview.
- The message or signature the posting came with, if any, and what the user knows about the sender. This is the
  basis of the counterpart classification (KK-3.1). The user can answer the classification questions instead.

## Output: the Vorgang folder (S1, S2)

Before the analysis, create the Vorgang folder with these files (LS-6, S1). Existing files are never overwritten.

1. `stellenanzeige.md`: the posting text verbatim, including the gender suffix of the role title and every reference
   number. Frontmatter: `quelle: <URL, or: Text, eingefügt>` and `erfasst: JJJJ-MM-TT`.
2. `vorgang.md` (LS-6.1): the Metadaten of the application. Created with `status: erfasst`; after the analysis set to
   `analysiert` with one `## Verlauf` line.

   ```yaml
   ---
   firma: <Anstellungsgeber, or unbekannt>
   stelle: <role title without gender suffix>
   ref_nr: <reference number, empty when the posting has none>
   bewerbungsweg: email | portal | post
   ausrichtung: ausschreibung | initiativ | quereinstieg | berufseinstieg | vermittler
   stellenquelle: <URL, or: Text, eingefügt>
   kontaktart: "<KK-6 value, or Unklar>"
   status: erfasst
   erfasst: JJJJ-MM-TT
   grundlage_hash:                     # set in S4 by the writing skills (LS-5.4)
   versendet_am:                       # S7, user statement
   weg:                                # S7
   anhaenge: []                        # S7
   wiedervorlage:                      # empty until sent; then versendet_am plus the follow-up period of KK-5.4
   loeschen_ab:                        # S10: deletion date set by the user, or empty (LS-6 rule 8)
   tags: []
   ---

   ## Plan

   ## Verlauf
   - JJJJ-MM-TT: Vorgang angelegt (erfasst), job-application-posting-analysis
   - JJJJ-MM-TT: erfasst → analysiert, job-application-posting-analysis
   ```

   Allowed `status` values (LS-6): `erfasst, analysiert, geplant, erstellt, geprüft, in Arbeit, versendet, rückmeldung,
   gespräch, angebot, verhandlung, zusage, absage, abgelehnt, zurückgezogen, ohne Antwort`. Every change of status adds
   one line `- JJJJ-MM-TT: <alter> → <neuer Status>, <Skill>` to `## Verlauf`; old lines are never removed.
3. `notizen.md`: created empty, no frontmatter (LS-6.3). Never overwritten and never read for a document.
4. `firmen/<firma-slug>.md` in the Wurzel on first occurrence of the firm (LS-6.2, UA-5.2), see item 9 below.

## Output: `analyse.md`

`<wurzel>/<slug>/analyse.md`, with these sections:

1. **Stammdaten:** Stelle (the posting's exact title; the gender suffix such as `(m/w/d)` is noted here and in
   `stellenanzeige.md`, and the Betreff of the documents uses the title without it, AS-4), Unternehmen, Standort / Remote,
   Referenznummer, Ansprechperson (only if named in the posting, with academic title as written), Eintrittstermin,
   Gehalt (only if stated). The frontmatter of `analyse.md` carries the classification keys of item 8 and the company
   roles of item 9.
2. **Bewerbungsweg und verlangte Unterlagen:** E-Mail, Portal, or Post; ATS-Hinweis,
   Europass-Forderung, Formatangabe, and the posting's country (for R-8.2 and R-8.5) as
   separate lines so the format choice can follow; required
   attachments such as Gehaltsvorstellung or Zeugnisse; a portal's character limit for the letter field (AS-8.1).
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
   posting worth reusing where the profile supports them (ATS keywords, rule R-1.4). The Anrede that follows from it
   (AS-5.6 to AS-5.8) is noted here.
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

   - Copy `kontaktart` into `vorgang.md` as a quoted string (LS-6.1).
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
   - Firm files: on first use create `<wurzel>/firmen/<firma-slug>.md` with the keys of LS-6.2 (`firma`, `rechtsform`,
     `sitz`, `website`, `aktualisiert`, `tags`) and `rollen`, `identitaet_quelle`, `identitaet_stand` (UA-5.2), body
     `## Notizen` empty. An existing file is updated in its identity fields only after the user confirms. Its
     `## Notizen` body is never touched (LS-5.6).
   - A re-run replaces the section and records the old `Stand` as one line in `## Verlauf` of `vorgang.md` (UA-5.1).

## Hard rules

1. **No *erfüllt* without evidence** from the profile.
2. **Quote the posting exactly** for requirements and reference numbers. Do not paraphrase them. The verbatim text lives
   in `stellenanzeige.md`.
3. **Name the gaps.** Every *nicht belegt* or *teilweise* *Muss* row is reported to the user, with its
   `Verwendung` (`Anschreiben` or `Rückfrage`), so it can be addressed honestly. It is never claimed.
4. **Not evidenced is not lacking.** *nicht belegt* means no evidence was found in the Grundlage. The row must
   never say the candidate lacks the competency, and the word *fehlt* is not used (CG-4.3).
5. **Muss without evidence is never *erfüllt*.** A *Muss* row needs *mittel* or *stark* evidence for *erfüllt* (CG-4.1, CG-4.5).
6. **Do not write application text.** Hand over to the writing skills.
7. **Disclosure.** When the counterpart is a Vermittler and the Auftraggeber is not disclosed, the analysis says so, and
   the Anstellungsgeber is not presented as the addressee (KK-4.1, UA-6.2).
8. **Double submission.** Look for other Vorgänge in `<wurzel>/` with the same Anstellungsgeber or Auftraggeber (their
   `vorgang.md`). Any match is reported to the user before the plan is approved, with the channel of each application
   (KK-4.2).
9. **Reputation is opinion.** Rating-portal statements are never written into a Stammdatum or a document (UA-2.1).
10. **Never overwrite `notizen.md`, `## Notizen` of a firm file, or an existing `stellenanzeige.md`** (LS-5.6). A re-run
    replaces `analyse.md` and its sections, updates `vorgang.md`, and adds `## Verlauf` lines.
11. **Only the Wurzel is written** (LS-5.7).
