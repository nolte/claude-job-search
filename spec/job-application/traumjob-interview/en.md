# Preference interview and fit check (EN canonical)

Normative rules for a structured interview that identifies what the candidate wants from work,
the stored result (the **Wunschprofil**), and a check that compares a real posting or company
against it (the **Passungsprüfung**). The interview records preferences. It does not record
facts about the candidate, and it does not test or diagnose personality.

Related rules: `spec/job-application/konventionen/en.md` R-1 (facts), R-6 (data protection),
`spec/job-application/lokale-struktur/en.md` LS-4 (storage) and LS-5 (invariants),
`spec/job-application/unternehmensanalyse/en.md` (company facts and sources),
`spec/job-application/kontaktklassifikation/en.md` (counterpart), and
`spec/job-application/cv-generierung/en.md` CG-4 (evidence for requirements).

## WJ-1 Terms

| Term | Meaning |
|---|---|
| **Wunsch** | A stated preference about work, with a priority (WJ-3.2). |
| **Ausschluss** | A preference the candidate will not accept. It works as a veto in the fit check. |
| **Wunschprofil** | The stored set of Wünsche and Ausschlüsse of one candidate, in `wunschprofil.md` (WJ-5). |
| **Passung** | How a real posting or company matches one Wunsch (WJ-6.2). |
| **Hypothese** | A preference the candidate is not yet sure of. It is marked as such and is never used as a veto. |

1. A Wunsch is the candidate's statement. The interview never replaces it with a conclusion of
   the skill.
2. The Wunschprofil is a preference, not a fact. It is not stored in the Grundlage, because the
   Grundlage carries no application state (LS-5.2) and no preference.

## WJ-2 Interview: principles

1. **Consent and purpose first.** Before the first question, the interview states what is stored,
   where (`wunschprofil.md` in the Wurzel, LS-2), that nothing is sent anywhere (WJ-8), and how to
   stop or delete. The candidate agrees before the interview starts.
2. **The candidate's words.** Wishes are recorded in the words the candidate uses. The skill may
   shorten them. It does not improve them into more appealing wording.
3. **No leading questions.** A question does not name the answer. "Was wünschst du dir von der
   Arbeitsform?" is allowed. "Du willst sicher remote arbeiten, oder?" is not.
4. **Episodes before opinions.** Concrete past experiences are asked for before abstract wishes.
   A wish that matches no episode is recorded as a Hypothese (WJ-3.3).
5. **No inference from the Grundlage.** A skill does not add a wish because the Grundlage shows a
   past role. Past roles show what the candidate did, not what they want.
6. **Stop anytime.** The candidate can skip a dimension, end the interview, or defer it. A skipped
   dimension stays open and is not filled in.

## WJ-3 Interview: structure

The interview runs in seven phases. Each phase has a short result that the candidate confirms.

| Phase | Purpose | Result |
|---|---|---|
| **1 Rahmen** | Consent, purpose, storage, deletion (WJ-2.1) | Confirmed consent |
| **2 Rückblick** | Two or three concrete episodes: a job or project that worked well, one that did not, and why | Episode notes, in the candidate's words |
| **3 Energie** | What gives energy in work, and what drains it, drawn from the episodes | Energy notes |
| **4 Dimensionen** | For each dimension of WJ-4: the ideal, what is acceptable, and what is an Ausschluss | Wünsche and Ausschlüsse per dimension |
| **5 Abwägung** | Forced choices between two wishes that conflict, to set the order of priority | Priorities |
| **6 Realitätscheck** | For each Muss or Ausschluss: has the candidate seen this work, or is it an assumption? | Hypothesis marks |
| **7 Bestätigung** | A summary of the whole profile, read back to the candidate, with corrections | Confirmed profile, version 1 |

### WJ-3.1 Phase details

- **Phase 2** asks what happened, what the candidate did, and what was missing, not what they would
  like next time. Episodes are recorded briefly; the wording stays with the candidate.
- **Phase 4** covers the dimensions one at a time. The candidate may answer briefly. The skill asks
  at most one follow-up question per dimension.
- **Phase 5** uses pairs such as "Mehr Gestaltungsspielraum oder mehr Planbarkeit?". Both sides are
  real options. The result is an order, not a score.
- **Phase 6** names an assumption as an assumption. A Muss that rests only on an assumption is a
  Hypothese until the candidate has evidence.

### WJ-3.2 Priorities

Each Wunsch carries one priority:

| Priorität | Meaning | Use in the fit check |
|---|---|---|
| **Muss** | The job does not work without it. | A posting that contradicts it lowers the fit strongly. |
| **Soll** | Clearly wanted, but a trade-off is possible. | A contradiction lowers the fit. |
| **Kann** | A plus that does not decide. | Only a note. |
| **Ausschluss** | Not acceptable. | A contradiction is a veto (WJ-6.3). |

### WJ-3.3 Hypothesen

1. A Wunsch is a Hypothese when the candidate has no episode for it, or marks it as an assumption
   in phase 6.
2. A Hypothese carries the flag `hypothese: ja` in the profile. It can be a Soll or a Kann, but never
   an Ausschluss, because a veto needs a confirmed reason.
3. A Hypothese is confirmed or dropped when the candidate has evidence, or when a fit check shows it
   was wrong (WJ-6.5).

## WJ-4 Dimensions

The interview covers these dimensions. A dimension can be skipped (WJ-2.6).

| Dimension | Asks about | Typical contradictions in postings |
|---|---|---|
| **Aufgaben** | The kind of work: building, operating, deciding, coordinating, teaching, analysing | A posting that is mostly a different kind of work |
| **Tiefe und Verantwortung** | Hands-on depth, ownership of results, decision rights | Ownership without decision rights, or the reverse |
| **Führung** | Leading people, mentoring, no people responsibility, or only technical lead | A leadership role for someone who wants none (CV-16 applies to the CV) |
| **Team und Umfeld** | Team size, team mix, closeness to customers, independence | Team size and structure, or the lack of one |
| **Arbeitsform** | Remote, hybrid, on site; location; travel | A location the candidate cannot reach, or unclear remote rules |
| **Arbeitszeit** | Hours, flexibility, on-call duties | Core hours or on-call that does not fit |
| **Entwicklung** | Learning, certification, career paths, specialisation vs. breadth | No development path, or one that is not what the candidate wants |
| **Vergütung und Leistungen** | Salary range, benefits that matter | Only if the posting states them (KK-4.4) |
| **Arbeitsweise und Kultur** | Methods (agile, planning), feedback style, pace | Methods or pace that conflict with a stated preference |
| **Sinn und Werte** | Which work the candidate can stand behind, and which they cannot | Business or sector the candidate rules out |
| **Sicherheit und Stabilität** | Contract form, employment stability, risk the candidate accepts | Fixed-term or agency contracts (KK-2) |

1. **Gehalt is never inferred.** A salary wish is recorded as the candidate states it. It is not
   compared with a posting that gives no salary.
2. **Sensitive topics** such as health, family or religion are not asked about. If the candidate
   volunteers one, it is recorded only as far as it bears on a Wunsch (for example a reachable
   location), and the candidate is asked whether it may be stored (R-8.2 and E-5 analogy).

## WJ-5 Storage: `wunschprofil.md`

The Wunschprofil is a Stammdatum class of its own. It is written to the Wurzel, next to the Grundlage
(LS-3). The skill writes it only after phase 7 is confirmed.

```yaml
---
typ: wunschprofil
stand: 2026-10-21                 # date of the last confirmed version (WJ-5.1)
version: 1
bestaetigt: ja                    # set only after phase 7
---
```

Body:

```markdown
## Rahmen
Einwilligung am 2026-10-21, Speicherort, Löschung auf Wunsch.

## Wünsche
| Dimension | Wunsch (Wortlaut des Nutzers) | Priorität | Hypothese | Quelle |
|---|---|---|---|---|
| Arbeitsform | „Hauptsächlich remote, gelegentlich vor Ort“ | Soll | nein | Interview 2026-10-21, Phase 4 |
| Führung | „Keine Personalverantwortung“ | Ausschluss | nein | Interview 2026-10-21, Phase 4 |

## Ausschlüsse
- …

## Verlauf
- 2026-10-21: Version 1 bestätigt.
```

1. **Wording stays.** The Wunsch column keeps the candidate's words (WJ-2.2).
2. **Versions.** A change creates a new version with its date. The old version remains in `Verlauf`
   with a short reason. Nothing is deleted without the candidate's request.
3. **Only the Wurzel.** The file is written in the Wurzel and nowhere else (LS-5.7). It is never
   copied into a document or into a Grundlage.

### WJ-5.1 Changes after the interview

1. A candidate can change a Wunsch at any time. The skill asks only the question needed for the change
   and writes the change as a new version.
2. The fit check (WJ-6) never changes the Wunschprofil. It only reports which wishes conflict with a
   posting. A change of wish comes from the candidate.

## WJ-6 Fit check (Passungsprüfung)

The fit check compares one real posting or one company with the confirmed Wunschprofil. It runs
after `job-application-posting-analysis` and the company analysis (UA-4), so that the facts are
already sourced.

### WJ-6.1 Inputs

- The confirmed `wunschprofil.md` with `bestaetigt: ja`. Without it, the check is not run.
- The posting analysis `analyse.md`, including the requirements (CG-4) and the section
  `## Unternehmen` (UA-5.1).
- Facts about the working conditions from the posting: location, form of work, hours, contract form,
  salary if stated, team and leadership if stated.

### WJ-6.2 Passung per dimension

For each Wunsch, the check gives one value:

| Passung | Meaning |
|---|---|
| **passt** | The posting states something that matches the Wunsch, with a source. |
| **teilweise** | Partly matches, or the posting is silent on a part of it. |
| **passt nicht** | The posting states something that contradicts the Wunsch, with a source. |
| **unklar** | The posting is ambiguous on the point. |
| **nicht ermittelt** | The posting does not say anything about it. |

1. Every value names its source: the posting quote or the source of the company fact.
2. **nicht ermittelt is not passt nicht.** Silence in the posting is not a contradiction. It is a
   question to ask the counterpart (KK-5).
3. A value is never inferred from the company's reputation (UA-2.1).

### WJ-6.3 Vetos and weights

1. An Ausschluss with *passt nicht* is a **Veto**. The check reports the veto first, with the source.
   The result is not *passt*, whatever else matches.
2. A Muss with *passt nicht* is a strong negative. A Soll with *passt nicht* is a negative. A Kann is
   only a note.
3. A Hypothese (WJ-3.3) never triggers a veto. Its value is shown as Hypothese.
4. The check counts the matches and the contradictions, but it does not turn them into a score. A
   total number would hide which wish is in conflict.

### WJ-6.4 Result

The result is written to `<slug>/passung.md` in the Vorgang folder:

```markdown
---
stand: 2026-10-21
wunschprofil_version: 1
gesamturteil: Veto | Klärungsbedarf | Passt überwiegend
---

## Vetos
- Ausschluss „Keine Personalverantwortung“: Stellenanzeige „Teamleitung für fünf Entwickler“ (Zeile 4). Quelle: Stellenanzeige.

## Abweichungen
| Wunsch | Priorität | Passung | Quelle |
|---|---|---|---|
| Arbeitsform: hauptsächlich remote | Soll | teilweise | Stellenanzeige: „hybrid, zwei Tage vor Ort“ |

## Nicht ermittelt
- Arbeitszeit (Wunsch: flexibel). Frage an den Kontakt, siehe KK-5.

## Hinweise
- Hypothese „Sinn und Werte“: Passung nicht beurteilbar, bis Nachweis vorliegt.
```

1. **Gesamturteil** has three values only. `Veto` when any veto exists. `Klärungsbedarf` when a Muss or
   Soll is *unklar*, *nicht ermittelt* or *teilweise*. `Passt überwiegend` otherwise. A "passt" overall
   value is never given while a Muss is *nicht ermittelt*.
2. The file is for the candidate. It is never sent to a counterpart and never copied into a document
   (WJ-8.2).

## WJ-7 Use in the application process

1. **Before the plan gate.** A veto stops the plan gate (`job-application-solution`, step 3) until the
   candidate decides: continue despite the veto, or stop this application. The decision is recorded in
   `vorgang.md`.
2. **Documents are not changed by the Wunschprofil.** The CV and the letter contain facts from the
   Grundlage and evidence from the posting analysis (CG-4). They do not state the candidate's wishes.
   A wish is never a claim about the candidate's experience. The one exception is the
   Motivationsschreiben: it may state a wish that the user has confirmed for that letter, and never a
   wish marked `hypothese: ja` (`motivationsschreiben/en.md` MS-3.3).
3. **Questions to the counterpart.** *nicht ermittelt* values become questions for the counterpart,
   written with `job-application-email-create` only after the counterpart and the disclosure are known
   (KK-4, KK-5).

## WJ-8 Privacy

1. **Local only.** The Wunschprofil and the fit check stay in the git-ignored working folder (R-6, LS-2).
2. **Never sent.** No skill sends the Wunschprofil, a fit check or a wish to any service or counterpart.
   A web search does not include any wish or interview content (UA-3.3).
3. **Deletion.** The candidate can delete the Wunschprofil and the fit checks at any time. The skill
   deletes only the files the candidate names, after showing them.
4. **Sensitive content** volunteered in the interview is stored only as far as WJ-4.2 allows, with the
   candidate's consent.

## WJ-9 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| WJ-A | Interview completed, all phases confirmed | `wunschprofil.md` version 1 with `bestaetigt: ja`, Wünsche in the candidate's words |
| WJ-B | Candidate answers "egal" to a dimension | Dimension recorded as skipped, not filled in |
| WJ-C | Wish with no episode | Hypothese flag set, cannot trigger a veto |
| WJ-D | Posting requires people leadership, Ausschluss says no | Veto reported first, with the posting quote; plan gate stops |
| WJ-E | Posting silent on work location | `nicht ermittelt`, question for the counterpart, not a contradiction |
| WJ-F | Two Muss wishes conflict with each other | Phase 5 must resolve it before phase 7; otherwise the profile stays unconfirmed |
| WJ-G | Candidate changes a Soll after applications | New version, old version kept in Verlauf, no change to fit checks already made |
| WJ-H | Company reputation is negative only on a rating portal | Not used as a value (UA-2.1), no veto |
| WJ-I | Candidate asks to delete the profile | Files named by the candidate are deleted after confirmation |

The scenarios are checked by reviewing an interview transcript and the resulting profile. A script
check for the profile format and the veto rule is an open point.

## WJ-10 Open points

| Area | Point | Status |
|---|---|---|
| Skill | An interview skill runs the phases and writes `wunschprofil.md` | open |
| Skill | The fit check runs after posting analysis and writes `passung.md` | open |
| LS-4 | Add the Wunschprofil to the table of Stammdaten in `lokale-struktur/en.md` | open |
| Script | Validate the profile format (WJ-5) and the veto rule (WJ-6.3) deterministically | open |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |
