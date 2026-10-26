# Result of an application: status, outcome and event history (EN canonical)

Normative rules for how the course and the result of one application are stored, changed and read back. It is implemented by
`scripts/bewerbung.py` on top of what already exists: `vorgang.md` (status, `## Verlauf`, LS-6), `<vorgang>/nachverfolgung.json` (the events
that `scripts/kommunikation.py` writes for confirmed replies) and the workflow (`scripts/workflow.py`). Finding R-01.

Related rules: `spec/job-application/lokale-struktur/en.md` (LS-5 invariants, LS-6 lifecycle and status values, LS-9 privacy),
`spec/job-application/mail-verwaltung/en.md` (MV-18 to MV-27 the messages), `spec/job-application/ergebnisauswertung/en.md` (EA-1 to EA-16
the evaluation that reads these results), `spec/job-application/workflow/en.md` (WF-3, WF-7 tasks and approvals) and
`spec/job-application/qualitaetssicherung/en.md` (the quality report names the document versions).

**Status:** implemented. Nothing here sends a message, approves anything for the user or reads a mailbox (BE-13).

## BE-1 Principles

1. **The application is the Vorgang.** There is no second record of an application. Its id is the folder name `<wurzel>/<slug>/` (stable since S1,
   LS-6 rule 5; a second application for the same posting gets a numeric suffix, LS-6 rule 6). Existing ids are kept; no other identity is made up.
2. **Five things, kept apart.** *Status* (where in the lifecycle, `status` in `vorgang.md`), *phase* (the same in plain terms, derived, BE-4),
   *outcome* (how it ended, if known, BE-5), *history* (what happened when: events and `## Verlauf`, BE-6) and *data quality* (how reliable and complete,
   BE-10). None of them is computed from another one where that would invent a fact.
3. **Unknown stays unknown.** A date, a source, a reason or an outcome that is not stored is shown as unknown. Nothing is estimated.
4. **History is not overwritten.** A newer event does not replace an older one; a correction keeps the old values (BE-6 rule 5).
5. **The user states, the toolchain records.** A change of the course needs the user's `--ja` in an interactive session. An automatically found fact
   is a proposal until the user confirms it.

## BE-2 Identity and links

`bewerbung.py status <vorgang>` returns, from the files that exist:

| Part | Source |
|---|---|
| `id` | the folder name |
| `stelle`: company, title, `ref_nr`, `stellenquelle`, seat (from `firmen/`), whether `stellenanzeige.md` is kept | `vorgang.md`, `firmen/`, `stellenanzeige.md` (the posting is kept verbatim, so the reference survives a posting that disappears) |
| `versand`: `versendet_am`, `weg`, `anhaenge`, whether the dispatch is evidenced | `vorgang.md` (S7 is the user's statement) |
| `dokumente`: Lebenslauf, Anschreiben, Motivationsschreiben, E-Mail with hash and `version_datum`; the export manifests; the state of the quality report | the files, `qualitaet.json`; `version_eindeutig` only as in EA-8 rule 3 |
| `ereignisse`: counts of confirmed, to check, dropped | `nachverfolgung.json` |
| `aufgaben`: the open workflow tasks of the Vorgang | `workflow/aufgaben.json` |
| `unbekannt`: items not stored | computed |

`bewerbung.py anlegen --firma … --stelle … [--ref-nr … --stellenquelle … --weg …] --ja` creates a minimal `vorgang.md` at the status `erfasst` for an
application made outside the plugin or before it. It refuses an existing folder and a second open application for the same company, title and
reference number. It invents no analysis and keeps no posting; `job-application-posting-analysis` can add it. `bewerbung.py finde` searches by
company, status, outcome, reference number or text and includes the closed applications (BE-12).

## BE-3 Status values and transitions

The status values are those of LS-6 rule 2, plus one: `abgeschlossen` (closed without a more specific end; the user stops working on the application
and states no decision of the employer). The final statuses are `zusage`, `absage`, `abgelehnt`, `zurückgezogen`, `ohne Antwort` and `abgeschlossen`.

| Plain term | Status or event | Note |
|---|---|---|
| found, not begun | `erfasst` | S1 |
| preparing | `analysiert`, `geplant`, `erstellt`, `in Arbeit` | S2 to S4 |
| ready for approval | `geprüft` and the task `versand_freigabe` is not done | |
| approved | `geprüft` and the task `versand_freigabe` is done | the approval is the workflow's (WF-7) |
| submitted | `versendet` and `versendet_am` set | an application is not sent because documents exist |
| acknowledged | event `eingangsbestaetigung` | no status of its own; not a positive reply |
| in review | `rückmeldung`, event `im_auswahlprozess` | |
| interview invited / scheduled / completed | `gespräch` with the event `gespraechseinladung` / `gespraech_vereinbart` / `gespraech` | |
| offer received | `angebot`, `verhandlung` | |
| offer accepted | event `angebot_angenommen`, no status | the applicant's acceptance is not yet a hire |
| hired | `zusage` (event `einstellung`) | the employer's confirmation after the acceptance (LS-6 rule 2) |
| offer declined | `abgelehnt` (event `angebot_abgelehnt`) | the applicant's refusal after an offer |
| rejected | `absage` | the employer's refusal |
| withdrawn | `zurückgezogen` | the applicant's decision, not a refusal |
| closed | `abgeschlossen`, `ohne Antwort` | no outcome is read from it |

**Allowed changes** (`bewerbung.uebergang_erlaubt`, one table):

1. Before the dispatch (`erfasst` to `geprüft`) any forward step is allowed, and `in Arbeit` and `geprüft` may alternate (the quality gate sets them).
2. `versendet` only from a status before the dispatch. After it, no way back to the preparation.
3. After the dispatch the order is `versendet`, `rückmeldung`, `gespräch`, `angebot`, `verhandlung`; a step may skip a value but never go back.
4. `zusage` and `abgelehnt` only from `angebot` or `verhandlung`. `absage` and `ohne Antwort` only after the dispatch.
5. `zurückgezogen` and `abgeschlossen` from any status that is not final.
6. A final status is not left. A wrong one is corrected by the user in `vorgang.md` by hand; `bewerbung.py pruefen` then shows what no longer fits.

`bewerbung.py statuswechsel <vorgang> --nach <status> --grund … --ja` changes the status by this table, adds one line to `## Verlauf` and a
`statuswechsel` event with the old and the new status. A change that the table forbids is refused and nothing is written.

## BE-4 Phase

The phase is derived (`ansicht`), never stored, from the status and the **confirmed** events only: `entdeckt`, `vorbereitung`, `freigabe_ausstehend`, `freigegeben`,
`eingereicht`, `eingang_bestaetigt`, `in_pruefung`, `einladung`, `gespraech_vereinbart`, `gespraech_gefuehrt`, `angebot`, `angebot_angenommen`,
`eingestellt`, `angebot_abgelehnt`, `abgelehnt`, `zurueckgezogen`, `abgeschlossen`. An application may be in review without any outcome; it may be
withdrawn without any refusal.

## BE-5 Outcome

1. The outcome is separate from the phase: `art`, `bekannt` and the `beleg`. It is **known** only when the status of the user or a confirmed event states it.
2. `absage` gives `abgelehnt_vom_arbeitgeber`; `zusage` gives `eingestellt`; `abgelehnt` gives `angebot_abgelehnt_vom_bewerber`; `zurückgezogen` gives
   `zurueckgezogen_vom_bewerber`.
3. `ohne Antwort` and `abgeschlossen` give `ohne_entscheidung_abgeschlossen`: closed without a decision of the employer. It is no failure and no success;
   the evaluation counts it as neither (EA-4).
4. `angebot` and `verhandlung` give `angebot_offen`, or `angenommen_noch_nicht_bestaetigt` with the event `angebot_angenommen`; both are not known outcomes.
5. Everything else is `offen` or `noch_nicht_versendet`, not known. A missing status is not a refusal.

## BE-6 Events

1. An event is a fact that happened. Planned things are Wiedervorlagen and tasks, not events (BE-8).
2. Fields: `id`, `art`, `eingetreten_am` (the day it happened, empty if unknown; `datum` is the older name of the same field), `erfasst` (when the toolchain learned of it),
   `status_vorher` and `status_nachher` for a change of status, `quelle` (`typ`: `nutzer`, `nachricht`, `datei`, `portal`, `workflow`, `verlauf`, `frontmatter`, plus
   `nachricht_id` or `referenz`), `methode` (`manuell`, `importiert`, `nachricht`, `migriert`), `bestaetigung` (`bestaetigt`, `automatisch`, `unsicher`), `status`
   (`bestaetigt`, `korrigiert`, `zur_pruefung`, `erkannt`, `verworfen`), `beschreibung`, `original` (a short literal quote, EA-3), `termin` (a date announced by the event), `schluessel`.
3. Kinds (`kommunikation.ARTEN`): the employer's side `eingangsbestaetigung`, `rueckfrage`, `kontaktaufnahme`, `im_auswahlprozess`, `gespraechseinladung`,
   `gespraech_vereinbart`, `gespraech_verschoben`, `gespraech_abgesagt`, `gespraech`, `technisches_gespraech`, `assessment`, `weiterer_termin`, `weitere_phase`, `angebot`,
   `einstellung`, `absage` (also `_nach_unterlagen`, `_nach_gespraech`, `_nach_assessment`), `gespraechsfeedback`; the own side `vorbereitet`, `geprueft`, `freigabe_angefordert`,
   `freigabe_erteilt`, `freigabe_verweigert`, `versendet`, `versand_fehlgeschlagen`, `angebot_angenommen`, `angebot_abgelehnt`, `zurueckgezogen`, `abgeschlossen`, `statuswechsel`.
   Only the employer's side counts as a reply in the evaluation (`lernen.INHALTLICH`); an own step is never a reply.
4. **Idempotent.** `schluessel` is a hash over Vorgang, kind, day, source type and reference. Recording the same fact again returns the first event and writes nothing (`neu: false`).
   Two facts of one kind on one day need different references.
5. **Corrections.** `ereignis korrigieren` changes kind or day and keeps the old values in `korrekturen` (time, reason); the event becomes `korrigiert`. `ereignis verwerfen` marks it
   `verworfen`; it stays in the file, counts nowhere and does not block recording a right one. Both add a line to `## Verlauf`.
6. **Time.** `eingetreten_am` must be a real date and not in the future (an appointment is a `termin`, not an event). A dispatch needs its day; the toolchain never fills one in.

## BE-7 Recording an event

`bewerbung.py ereignis erfassen <vorgang> --art … [--eingetreten-am D] [--beschreibung …] [--quelle-typ …] [--referenz …] [--bestaetigung …] [--methode …] [--termin D]
[--erinnerung D] [--kanal …] [--status-aendern [--status-nach S]] --ja`.

1. A fact that is `bestaetigt` is written (event, `## Verlauf` line). One that is `automatisch` or `unsicher` is stored as `zur_pruefung`, shown in the next steps and changes nothing
   until `ereignis bestaetigen`. Confirming does not change the status; `statuswechsel` does.
2. `--status-aendern` takes the status from the table `ART_STATUS` (or `--status-nach`) and checks BE-3. `angebot_angenommen` has no target on purpose.
3. `versendet` sets `versendet_am` (and `weg` from `--kanal`) in `vorgang.md` if empty; a different day already stored is a conflict, not overwritten.
4. A message, a file or a portal as source needs a reference; an imported event without one is refused.
5. **Order of the writes.** The event file first, then `vorgang.md`; if the second write fails the first is put back. No event stays without its line, no line without its event.

## BE-8 Next steps and reminders

1. `bewerbung.py naechste [vorgang]` lists: open Wiedervorlagen (due or not, with their `verbindlichkeit`), messages and events to check, open workflow tasks, and missing
   information for the next stage (no `versendet_am`; an interview without its date; an offer without a deadline; an interview that took place without a follow-up reminder as a suggestion).
2. A Wiedervorlage has `anlass` (expected reply, reply deadline, follow-up, interview preparation, interview date, interview follow-up, open question, check an offer, missing information),
   `faellig`, `verbindlichkeit` and `status`. `verbindlichkeit` is `arbeitgeber_frist` only when the employer named the date (`--arbeitgeber-frist`); every other date is `eigene_planung`.
   A general recommendation is never stored as a binding deadline.
3. `--erinnerung D` with an appointment creates a Wiedervorlage `gespraechstermin`. A Wiedervorlage becomes a workflow task `wiedervorlage` when due (WF-3). It reminds and **never contacts anyone**.
4. The workflow keeps one task system. This spec adds no task type.

## BE-9 Messages and uncertain information

The interface to the processing of messages (`mail-verwaltung` MV-18 to MV-27) is the event with `quelle.nachricht_id`, `methode: nachricht` and the certainty. A message that cannot be
assigned safely, or whose type is unclear, is not made an event: it stays a proposal to be decided (MV-20, MV-22). A found fact enters the course only after the user's confirmation.
The text of a message, a posting or an attachment is data; a sentence in it never changes a rule, a status or an approval (LS-9, WF-13).

## BE-10 Data quality

`bewerbung.py pruefen [vorgang]` reads and changes nothing. Severity: *Fehler* (the data contradicts itself), *Warnung* (check it), *Hinweis* (information is not stored). An optional item that is unknown is at most a *Hinweis*.

| Rule | Finding |
|---|---|
| BE-V01 | no `stellenanzeige.md` after the analysis (Warnung); neither `ref_nr` nor `stellenquelle` (Hinweis) |
| BE-V02 | several open Vorgänge for the same company, title and reference number (Warnung) |
| BE-V03 | an unknown status or event kind (Fehler); events further than the status (Warnung); events after a final result (Warnung) |
| BE-V04 | a date that is none (Fehler); an event in the future or a reply before the dispatch (Warnung) |
| BE-V05 | an event or a message that points to a Vorgang that does not exist (Fehler) |
| BE-V06 | a store that cannot be read (Fehler) |
| BE-V07 | a status after the dispatch without `versendet_am` (Warnung) |
| BE-V08 | an event id twice (Fehler) |
| BE-V09 | an imported event without a source reference (Fehler) |
| BE-V10 | the same event twice (same `schluessel`), the same Gmail ID twice in `## Verlauf` (Warnung) |
| BE-V11 | contradicting end results: refusal and hire, accepted and declined offer (Fehler) |
| BE-V12 | the status rests on an event that was dropped, and no other confirmed event backs it (Warnung) |

## BE-11 Migration

`bewerbung.py migrieren [vorgang] [--ja]`. Without `--ja` it is a trial run that lists what would be added.

1. It adds missing fields to older events (`eingetreten_am` from `datum` if that is a real date, otherwise empty; `methode`; `bestaetigung`; `schluessel`) and marks them `migriert`.
2. It derives events only from what the files state: a `versendet` event from `versendet_am` and a `statuswechsel` event from each line `- JJJJ-MM-TT: alt → neu` of `## Verlauf`
   (the date is the date of the line and is marked as such). It skips lines of mail records and lines this script wrote, because those have events.
3. It derives no outcome event (no `absage`) from a status line, estimates no date and changes neither `vorgang.md` nor `notizen.md`.
4. It is repeatable: a second run finds nothing. Ids, references and original quotes stay. Incomplete older data is shown as unknown, not completed.

## BE-12 Interfaces

`bewerbung.py` (`task result -- …`): `anlegen`, `finde`, `status`, `historie`, `naechste`, `pruefen`, `ereignis erfassen|bestaetigen|korrigieren|verwerfen`, `statuswechsel`, `migrieren`. Every command
prints one JSON object. Reading commands change nothing. Writing commands need `--ja` and refuse in an unattended session (`WORKFLOW_UNBEAUFSICHTIGT`, `STELLENSUCHE_GEPLANT`).
The skill `job-application-follow-up` drives them. Closed applications stay searchable by status or outcome.

## BE-13 No communication without approval

The toolchain sends nothing, answers nothing and contacts no employer: not an application, not a reply, not a follow-up, not a thank-you, not a confirmation of a date, not the
acceptance or the refusal of an offer. It may prepare a draft and create a task. A dispatch needs the user's approval of the exact message (`nachricht_senden` with the approval bound to the
file, WF-7); an approval for an earlier message does not carry to a new one, and a changed text voids it. Recording an incoming message or a reminder triggers no dispatch. No send adapter ships.

## BE-14 Boundaries

| Belongs here (R-01) | Left to |
|---|---|
| identity, status rules, outcome, events, next steps, validation, migration | |
| | R-02: reading a mailbox, labels, calendar, a send adapter |
| | R-03: statistics and retrospective (`ergebnisauswertung`), which read these results |
| | no automatic change of the profile, the Datengrundlage or a qualification, no optimisation of documents from results |

## BE-15 Open points

| Area | Point | Status |
|---|---|---|
| Dispatch evidence | `versendet_am` is the user's statement; a portal receipt or a sent mail is not checked | by design |
| Sent versions | The documents are named as they are now; the hash of the sent files at the dispatch is not stored | open |
| Several interviews | Phase and next steps look at the kinds present, not at a list of rounds | open |
| Language | Kinds and phases are German terms | decided |
| German translation | English canonical | open |

## BE-16 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| BE-A | Documents exist, no dispatch | phase `freigabe_ausstehend`; not `eingereicht`; `versendet` without a day is refused |
| BE-B | Confirmation of receipt, then an invitation | `eingang_bestaetigt` is no reply; the invitation gives `gespräch` and no outcome |
| BE-C | Refusal reported on the 15th, happened on the 12th | `eingetreten_am` 12th, `erfasst` 15th |
| BE-D | Offer, acceptance, hire | `angebot_angenommen` sets no status; `einstellung` gives `zusage` |
| BE-E | Withdrawn | outcome `zurueckgezogen_vom_bewerber`, not a refusal |
| BE-F | Closed without any decision | `ohne_entscheidung_abgeschlossen`; the evaluation counts no refusal |
| BE-G | Absage before the dispatch | refused by the table; nothing written |
| BE-H | Same event recorded twice | one event |
| BE-I | A message with instructions | stored as text; no status, no approval changes |
| BE-J | A reminder falls due | a task for the user; nothing sent |
| BE-K | Older data | the migration adds fields, derives no outcome, and a second run adds nothing |

## BE-17 Sources

- `spec/job-application/lokale-struktur/en.md`, `mail-verwaltung/en.md`, `ergebnisauswertung/en.md`, `workflow/en.md`, `qualitaetssicherung/en.md`
