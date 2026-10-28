---
name: job-application-traumjob-interview
description: "Interviews the candidate in seven phases to identify the work they want (Wünsche, Prioritäten, Ausschlüsse, Hypothesen) and stores the confirmed result as wunschprofil.md in the Wurzel. Use on \"finde meinen Traumjob\", \"welche Arbeit will ich eigentlich\", \"Wunschprofil erstellen\", \"Präferenzen festhalten\", or equivalent German requests. Don't use for the Lebenslauf facts (job-application-profile-capture, job-application-cv-maintain), for checking a posting against the wishes (job-application-fit-check), or for the company analysis (job-application-posting-analysis)."
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

Spec: `spec/job-application/traumjob-interview/en.md` (WJ-1 terms, WJ-2 principles, WJ-3 phases, priorities and
Hypothesen, WJ-4 dimensions, WJ-5 storage, WJ-7 use in the process, WJ-8 privacy, WJ-9 scenarios). Storage and privacy:
`spec/job-application/lokale-struktur/en.md` LS-2, LS-4, LS-5 and `spec/job-application/konventionen/en.md` R-6. The
rule IDs cite the spec files under `${CLAUDE_PLUGIN_ROOT}/spec/job-application/`; read a spec file only when a cited rule
is unclear. The Wunschprofil is a preference, not a fact: it is never written into the Grundlage (LS-5.2) and never into a
document. The one exception is the Motivationsschreiben, which may state a wish the user confirmed for that letter, and
never a wish marked `hypothese: ja` (WJ-7.2, `spec/job-application/motivationsschreiben/en.md` MS-3.3). That letter is
written by `job-application-motivation-letter-create`, not by this skill.

## Hard rules

1. **Only the Wurzel.** Write nothing outside `<wurzel>/wunschprofil.md`. Never write into the Grundlage or into a
   document, and never inside the plugin repository (Paths and boundary).
2. **Consent first, delete on request.** Delete the files the candidate names, after showing them (WJ-8.3).
3. **Nothing leaves the machine.** The interview sends nothing: no web search, no message and no external service
   receives wishes or interview content. The only exception is a job search run by `job-application-job-search`, which
   sends just the terms of the Suchbrief the user approved (WJ-8.2, ST-2); Ausschluss reasons, salary expectations,
   personal circumstances and Datengrundlage text never leave.
4. **Nothing is written before phase 7 is confirmed** (WJ-5).

## Paths and boundary

Read `job-application/konfiguration.md` first (the Anker, LS-2.3): key `wurzel` (default `job-application/`); relative
paths resolve against the working directory that contains the Anker (LS-2.6). Without an Anker, ask once for the path of
the Wurzel and write it there; only the keys `wurzel`, `grundlage` and `grundlage_index` are ever written (LS-2.5).

**Repository boundary (LS-2.4, R-9.9).** The Wurzel must lie outside the plugin repository (a directory tree holding
`.claude-plugin/plugin.json` with `"name": "job-application"`). Resolve it before any read or write; if it lies inside,
refuse, write nothing and tell the user to point `wurzel` in `job-application/konfiguration.md` outside. The plugin hook
and the scripts refuse such a path too.

## Inputs

- The Wurzel as resolved above.
- An existing `wunschprofil.md` in the Wurzel, if there is one (see Resume and changes).

## Workflow

Run the phases in order. Each phase ends with a short result that the candidate confirms.

1. **Phase 1 Rahmen.** Before any question, state what is stored, where (`<wurzel>/wunschprofil.md`), that nothing
   is sent anywhere (WJ-8.2), and how to stop, defer or delete. Add the privacy note (WJ-8.1, R-6, LS-2.1): the Wurzel
   is local and git-ignored by default; tracking it in a private, unpublished repository is the candidate's decision; a
   public repository never holds it. Continue only after explicit consent (WJ-2.1).
2. **Phase 2 Rückblick.** Ask for two or three concrete episodes: a job or project that worked well, one that did
   not, and why. Ask what happened, what the candidate did and what was missing, not what they would like next time.
   Keep the episodes briefly, in the candidate's words (see Episodes).
3. **Phase 3 Energie.** From the episodes, ask what gives energy and what drains it. Keep the answers as notes.
4. **Phase 4 Dimensionen.** Go through the dimensions of WJ-4 one at a time (Aufgaben, Tiefe und Verantwortung,
   Führung, Team und Umfeld, Arbeitsform, Arbeitszeit, Entwicklung, Vergütung und Leistungen, Arbeitsweise und
   Kultur, Sinn und Werte, Sicherheit und Stabilität). For each: the ideal, what is acceptable, and what is an
   Ausschluss. Ask at most one follow-up question per dimension. The candidate may skip a dimension or answer "egal"
   (WJ-2.6, WJ-B): it is recorded as skipped and not filled in (see Skipped dimensions).
5. **Phase 5 Abwägung.** For wishes that conflict, offer forced choices between two real options, for example
   "Mehr Gestaltungsspielraum oder mehr Planbarkeit?". The result is an order of priority, not a score. Then show
   every wish with exactly one priority of WJ-3.2 and let the candidate correct it:

   | Priorität | Meaning | Use in the fit check |
   |---|---|---|
   | **Muss** | The job does not work without it. | A contradiction lowers the fit strongly. |
   | **Soll** | Clearly wanted, but a trade-off is possible. | A contradiction lowers the fit. |
   | **Kann** | A plus that does not decide. | Only a note. |
   | **Ausschluss** | Not acceptable. | A contradiction is a veto (WJ-6.3). |

   Two Muss wishes that conflict with each other are resolved here (WJ-F).
6. **Phase 6 Realitätscheck.** For each Muss and each Ausschluss, ask whether the candidate has seen this kind of work
   or whether it is an assumption. An assumption is marked as a Hypothese. **An Ausschluss without an episode or other
   reason is asked about once more; if it stays an assumption, it is lowered to Soll or Kann** (the candidate chooses
   which) **with `hypothese: ja`**, because a veto needs a confirmed reason (WJ-3.3 rule 2). Say this to the candidate.
7. **Phase 7 Bestätigung.** Read the whole profile back in the candidate's words, grouped by priority, with skipped
   dimensions named. Ask for corrections. Ask whether the episodes may be stored (see Episodes). Only after an explicit
   confirmation, write the file.

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
- **Conflicts** between two Muss wishes must be resolved in phase 5. Otherwise the profile stays unconfirmed and
  `wunschprofil.md` is not written (WJ-F).

## Episodes and energy notes

The episodes of phase 2 and the energy notes of phase 3 are the evidence for phases 4 to 6 (WJ-2.4). The storage format
of WJ-5 has no place for them, so by default they stay in the session and only the phase is named in the `Quelle`
column. They are written only with the candidate's explicit yes at phase 7, as the optional section `## Episoden` after
`## Ausschlüsse`: a few lines in the candidate's words, no names of third parties, never copied into a document. A
candidate who says no gets a profile without that section.

## Skipped dimensions, interruption and deferral

- A skipped dimension (or "egal") gets one row in `## Wünsche`: dimension, `— (übersprungen)` in the Wunsch column, `—`
  in `Priorität` and `Hypothese`, `Interview YYYY-MM-DD, Phase 4: übersprungen` as `Quelle`. It is not a wish and not
  an Ausschluss, so the profile shows what is open (WJ-B, WJ-2.6).
- **Nothing is written before phase 7 is confirmed** (WJ-5). If the candidate stops or defers earlier, say so, show
  the interim result in the chat (answers so far, open dimensions) and state that nothing is stored and no fit check can
  run until a profile is confirmed. A later run starts again at phase 1; the candidate may paste the interim result to
  save answers. An existing confirmed profile stays untouched by an interrupted change.

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

`Priorität` is one of `Muss`, `Soll`, `Kann`, `Ausschluss`; `Hypothese` is `ja` or `nein`; an Ausschluss row never has
`ja`. `## Ausschlüsse` lists the Ausschluss rows again. `## Episoden` follows only on consent (above).

## Resume and changes

- If `wunschprofil.md` exists, do not start over. Show the confirmed profile and ask what changed.
- A change creates a new version with its date. The old version stays in `Verlauf` with a short reason (WJ-5, rule 2).
- Changes come from the candidate. The fit check never changes this file (WJ-5.1).
- A Hypothese is confirmed or dropped only when the candidate has evidence, or when a fit check showed it was wrong
  (WJ-3.3, rule 3). Ask before changing it.

## Gotchas

- An interrupted interview stores nothing; the interim result exists only in the chat. Say so before the candidate
  leaves, and offer the paste for the next run.
- An Ausschluss without an episode becomes Soll or Kann with `hypothese: ja`; do not keep it as an Ausschluss because the
  candidate insists, the veto needs a confirmed reason (WJ-3.3).
- The skill never reads the Grundlage for wishes; a role there is not a preference.

## Why this is a skill, not an agent

- The interview is a seven-phase conversation with confirmation after every phase; it cannot run fire-and-forget.
- It writes one file in the Wurzel that the fit check and the job search read in later sessions; there is no report to
  return.
- Counter-dimension: none that is load-bearing; the choice was uncontested.
