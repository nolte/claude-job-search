---
name: job-application-traumjob-interview
description: "Interviews the candidate in seven phases to identify the work they want (Wünsche, Prioritäten, Ausschlüsse, Hypothesen) and stores the confirmed result as wunschprofil.md in the Wurzel. Use on \"finde meinen Traumjob\", \"welche Arbeit will ich eigentlich\", \"Wunschprofil erstellen\", \"Präferenzen festhalten\", or equivalent German requests. Don't use for the Lebenslauf facts (job-application-profile-capture, job-application-cv-maintain), for checking a posting against the wishes (job-application-fit-check), or for the company analysis (posting-analysis)."
tags: [bewerbung, wunschprofil, interview, deutsch]
phase: intake
summary: "Seven-phase preference interview that stores a confirmed Wunschprofil with priorities, vetoes and hypotheses."
summary_de: "Siebenphasiges Präferenzinterview, das ein bestätigtes Wunschprofil mit Prioritäten, Ausschlüssen und Hypothesen speichert."
use_when:
  - "you want to find out what kind of work you want before you apply"
  - "you want your wishes stored so that postings can be checked against them"
dont_use_when:
  - situation: "You want to check a posting against your wishes"
    alternative: job-application-fit-check
  - situation: "You want to build or change the Lebenslauf facts"
    alternative: job-application-profile-capture
see_also:
  - job-application-fit-check
  - job-application-solution
---

# Bewerbung Traumjob-Interview

Spec: `spec/job-application/traumjob-interview/en.md` (WJ-2 principles, WJ-3 phases, WJ-4 dimensions,
WJ-5 storage, WJ-8 privacy). The Wunschprofil is a preference, not a fact: it is never written into the
Grundlage (LS-5.2) and never into a document.

## Inputs

- The Wurzel from `job-application/konfiguration.md`, read first as the Anker (key `wurzel`, default `job-application/`,
  LS-2.3). Relative paths resolve against the working directory that contains `job-application/konfiguration.md`
  (LS-2.6).
- An existing `wunschprofil.md` in the Wurzel, if there is one (see Resume).

## Workflow

Run the phases in order. Each phase ends with a short result that the candidate confirms.

1. **Phase 1 Rahmen.** Before any question, state what is stored, where (`<wurzel>/wunschprofil.md`), that nothing
   is sent anywhere (WJ-8.2), and how to stop, defer or delete. Continue only after explicit consent (WJ-2.1).
2. **Phase 2 Rückblick.** Ask for two or three concrete episodes: a job or project that worked well, one that did
   not, and why. Ask what happened, what the candidate did and what was missing, not what they would like next time.
   Record the episodes briefly, in the candidate's words.
3. **Phase 3 Energie.** From the episodes, ask what gives energy and what drains it. Record the answers as notes.
4. **Phase 4 Dimensionen.** Go through the dimensions of WJ-4 one at a time (Aufgaben, Tiefe und Verantwortung,
   Führung, Team und Umfeld, Arbeitsform, Arbeitszeit, Entwicklung, Vergütung und Leistungen, Arbeitsweise und
   Kultur, Sinn und Werte, Sicherheit und Stabilität). For each: the ideal, what is acceptable, and what is an
   Ausschluss. Ask at most one follow-up question per dimension. The candidate may skip a dimension, which stays open.
5. **Phase 5 Abwägung.** For wishes that conflict, offer forced choices between two real options, for example
   "Mehr Gestaltungsspielraum oder mehr Planbarkeit?". The result is an order of priority, not a score.
6. **Phase 6 Realitätscheck.** For each Muss and each Ausschluss, ask whether the candidate has seen this kind of work
   or whether it is an assumption. An assumption is marked as a Hypothese.
7. **Phase 7 Bestätigung.** Read the whole profile back in the candidate's words, grouped by priority. Ask for
   corrections. Only after an explicit confirmation, write the file.

## Interview rules

- **No leading questions.** A question never names the answer. "Was wünschst du dir von der Arbeitsform?" is allowed.
  "Du willst sicher remote arbeiten, oder?" is not.
- **Wording stays.** Record the wish as the candidate says it. Shorten it if needed, but do not make it more appealing.
- **No inference from the Grundlage.** A past role shows what the candidate did, not what they want. Do not add a
  wish because the Grundlage contains a role.
- **Hypothesen cannot veto.** A wish with no episode, or one marked as an assumption in phase 6, gets `hypothese: ja`
  and is never an Ausschluss (WJ-3.3).
- **Sensitive topics are not asked about**: health, family, religion. If the candidate volunteers one, store it only
  as far as it bears on a wish, and ask whether it may be stored (WJ-4.2).
- **Salary** is recorded only as the candidate states it. It is never compared with a posting that gives no salary (WJ-4.1).
- **Conflicts** between two Muss wishes must be resolved in phase 5. Otherwise the profile stays unconfirmed (WJ-9 WJ-F).

## Output

`<wurzel>/wunschprofil.md`, written only after phase 7 is confirmed:

```markdown
---
typ: wunschprofil
stand: YYYY-MM-DD
version: 1
bestaetigt: ja
---

## Rahmen
Einwilligung am YYYY-MM-DD, Speicherort, Löschung auf Wunsch.

## Wünsche
| Dimension | Wunsch (Wortlaut des Nutzers) | Priorität | Hypothese | Quelle |
|---|---|---|---|---|

## Ausschlüsse
- …

## Verlauf
- YYYY-MM-DD: Version 1 bestätigt.
```

## Resume and changes

- If `wunschprofil.md` exists, do not start over. Show the confirmed profile and ask what changed.
- A change creates a new version with its date. The old version stays in `Verlauf` with a short reason (WJ-5, rule 2).
- Changes come from the candidate. The fit check never changes this file (WJ-5.1).
- A Hypothese is confirmed or dropped only when the candidate has evidence, or when a fit check showed it was wrong
  (WJ-3.3, rule 3). Ask before changing it.

## Hard rules

1. **Only the Wurzel.** Write nothing outside `<wurzel>/wunschprofil.md`. Never write into the Grundlage or into a document.
2. **Consent first, delete on request.** Delete the files the candidate names, after showing them (WJ-8.3).
3. **Nothing leaves the machine.** No web search, no message and no external service receives wishes or interview content.
