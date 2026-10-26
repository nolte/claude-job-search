# Workflow orchestration (EN canonical)

Normative rules for the central control of the application process: which task is due, what it needs, what is done, what
waits for the user, what failed, and what comes next. The orchestration keeps the order, the dependencies, the attempts
and the approvals; the facts stay where they live. It is implemented by `scripts/workflow.py`; the skills do the work.

Related rules: `spec/job-application/lokale-struktur/en.md` (LS-3 layout, LS-4 persistence, LS-5 invariants, LS-6 lifecycle
S0 to S10), `spec/job-application/stellensuche/en.md` (ST-13 to ST-20 Suchauftrag, run and Warteschlange),
`spec/job-application/konventionen/en.md` (R-1 facts, R-6 data protection), `spec/job-application/mail-verwaltung/en.md`
(MV, the communication functions of A-02; specification only), `spec/job-application/kontaktklassifikation/en.md` (KK-5
follow-up) and `spec/job-application/recherche/en.md` (RC-5.0 rules for optional network channels).

**Status:** implemented by `scripts/workflow.py` for the tasks of WF-3. It plans and reconciles; it runs no skill and sends
nothing (WF-12). A scheduler is the user's (WF-9 rule 4).

**Provenance.** The behaviour of Claude Code permission rules named here (WF-12) was checked with `claude -p` on 2026-10-25
and is the behaviour of that version, not a promise.

## WF-1 Terms

| Term | Meaning |
|---|---|
| **Aufgabe** | One piece of work with a status, dependencies and attempts. Stored in `workflow/aufgaben.json` (WF-6). |
| **Aufgabentyp** | A kind of task from the fixed catalog of WF-3. A type fixes who does it, what it needs and when it is done. |
| **Bezug** | The Vorgang (folder slug) or the Suchauftrag (id) a task belongs to. |
| **Nachbedingung** | The condition in the files that makes a task done (WF-3). It is read, never declared. |
| **Voraussetzung** | The condition in the files or a dependency that must hold before a task may run. |
| **Versuch** | One attempt of an agent to do a task, with its result and error class. |
| **Lease** | The time until which a running task belongs to the agent that took it. |
| **Freigabe** | The user's explicit decision on one exact content (WF-7). |
| **Adapter** | The only code that may carry out an external action, and only for an approved task (WF-7). |

Vorgang, Wurzel and the status values of a Vorgang are used as defined in `lokale-struktur/en.md` LS-1 and LS-6.

## WF-2 Principles and the decision

1. **One master per fact (LS-5.1).** The status of an application is `status` in `vorgang.md`; the state of a search is the
   Suchauftrag. The workflow stores neither. A task stores only what the orchestration needs: dependencies, attempts,
   leases, retry times, approvals and a reference to its result with a hash.
2. **Reality wins.** The reconciliation (WF-6) reads the files. A step done outside the workflow, by the user or by a skill
   that ran on its own, is recognised and the task is closed; the workflow does not redo it and does not argue with it.
3. **Planning and doing are separate.** A task is created (planned), becomes ready when its conditions hold, is taken by an
   agent, and is done only when its postcondition holds. Starting a task never counts as finishing it.
4. **The decision.** The store is one JSON file with atomic writes and one file lock, like the Suchaufträge
   (`stellensuche` ST-13). The need is small: a few hundred tasks, one writer at a time, restart safety and readable diffs in
   a private repository. A database, a server or a queue would add an installation and a failure mode without a requirement
   that asks for it. If the store ever has to serve several machines at once, that is a new decision.
5. **No second approval mechanism.** The plan is approved in the plan gate of `job-application-solution` (it writes
   `geplant`), a Suchauftrag in `stellensuche` (ST-14). The workflow observes these. It adds one approval of its own, for what
   no existing mechanism covers: the exact documents to be sent, and an external message by an adapter (WF-7).

## WF-3 Task types

The catalog is fixed in the code. A task of another type is not created, and a stored task of another type makes the store
invalid. Text from a posting, a mail or a page never creates a type, a dependency or a limit (WF-13).

| Type | Who | Skill or role | Needs (Voraussetzung) | Done when (Nachbedingung) |
|---|---|---|---|---|
| `analyse` | agent | `job-application-posting-analysis` | `stellenanzeige.md` and `vorgang.md` exist | `status` is at least `analysiert` and `analyse.md` exists |
| `passung` | agent | `job-application-fit-check` | (only created with a confirmed Wunschprofil) `analyse` | `passung.md` exists |
| `plan` | user | plan gate of `job-application-solution` | `analyse` (and `passung`) | `status` is at least `geplant` and `vorgang.md` has a heading `## Plan` |
| `unterlagen` | agent | `job-application-solution` steps 4 and 5 | `plan` | `status` is at least `erstellt`; `lebenslauf.md` and `anschreiben.md` exist |
| `pruefung` | agent | `job-application-quality-gate` | `unterlagen` | `status` is `geprüft` |
| `versand_freigabe` | user | the user's decision | `pruefung` | an approval covers the hash of the documents (WF-7) |
| `versand` | user | the user sends; no adapter ships | `versand_freigabe` | `status` is at least `versendet` and `versendet_am` is set (S7, written by the user) |
| `nachfassen` | agent | `job-application-email-create`, variant `nachfassen` | `status` is `versendet`; the date `wiedervorlage` has come | `email-nachfassen.md` was written after the task was created |
| `suche` | agent | `job-application-job-search`, Suchauftrag | the Suchauftrag is approved and active (`stellensuche` ST-14) | a run of the Suchauftrag ended `ok`, `ok_ohne_treffer` or `teilweise` after the task was created |
| `nachricht_senden` | adapter | an adapter of A-02; none ships | an approval for the exact message file | the adapter reports sent, or the user confirms the outcome (WF-7) |

1. **The chain of an application** is `analyse`, `passung` (optional), `plan`, `unterlagen`, `pruefung`, `versand_freigabe`,
   `versand`. A step may be skipped by the user doing it in the files; the reconciliation recognises it (WF-2 rule 2).
2. **Task ids are stable.** `<type>:<slug>` for a Vorgang, `<type>:<id>:<n>` for a recurring task of a Suchauftrag,
   `<type>:<slug>:<date>` for a follow-up, `nachricht_senden:<slug>:<file>` for a message (one task per file). The same id is
   the same task; creating it again gives back the first (WF-6). The same id with another `bezug` is refused
   (`aufgabe_existiert`), never silently reused.
3. **`passung` is advice, not a gate.** If the user cancels it, what follows is not blocked. If a confirmed Wunschprofil appears
   after the chain was made, `starten` adds `passung` and puts it before `plan` as long as `plan` has not started.
4. **Not every application needs every step.** A step whose type is not in the chain is not created. Optional and
   alternative paths are the user's decision in the files; the catalog is not a flow diagram for every variant.

## WF-4 Statuses and transitions

| Status | Meaning |
|---|---|
| `wartend` | created, a dependency or a date is not met |
| `bereit` | all conditions hold; it may be taken (agent), done (user) or carried out (adapter) |
| `laeuft` | taken by an agent, within its lease |
| `wartet_auf_freigabe` | the user's decision on an exact content is missing (the approval of WF-7, or the approval of a Suchauftrag that `stellensuche` owns) |
| `wartet_auf_eingabe` | information is missing, or the outcome of an external action is unclear (WF-7 rule 5) |
| `wiederholung_geplant` | an attempt failed; the next one is not before `naechster_versuch` |
| `erledigt` | the postcondition holds; the result is referenced with a hash |
| `fehlgeschlagen` | the attempts are over or the error is permanent; only the user repeats it |
| `blockiert` | a prerequisite failed, was cancelled or is missing; nothing runs until it is met |
| `abgebrochen` | ended on purpose, by the user or because the Vorgang reached a final status |

1. **The matrix is in the code** (`UEBERGAENGE`) and tested for every pair. A transition that is not in it is refused with
   `uebergang_unzulaessig`. `abgebrochen` has no exit. `erledigt` has one: back to `wartet_auf_freigabe`, only for an
   approval whose content changed after it was given.
2. **A blocked task is not run.** `blockiert` becomes `wartend` or `bereit` again only when the reconciliation finds its
   prerequisites met. A task waiting for an approval is not released by a general workflow call (WF-7).
3. **A hold reported by an agent stays.** When an agent reports that it needs information, an approval, a permission or a
   quality fix (`fehler` with class `eingabe`, `freigabe`, `berechtigung` or `qualitaet`), the task keeps the matching
   status through every reconciliation and every schedule run, and is not offered to an agent again. Only the user lifts it
   with `weiter`; the files and the clock never do.
4. **The status of a task is not the status of an application.** `erledigt` of `versand` follows `versendet` in the Vorgang,
   never the other way round. The workflow writes nothing into a Vorgang.

## WF-5 Dependencies

1. A dependency is the id of another task. A task is ready only when all its dependencies are `erledigt`.
2. A failed, blocked or cancelled dependency makes its dependents `blockiert`, with the id in the hint. It never releases
   them silently.
3. A missing reference or a cycle is refused (`abhaengigkeit_unbekannt`, `zyklus`), when a task is created and when the store
   is read.
4. A manual decision is a task of type `plan` or `versand_freigabe` and a dependency like any other.
5. **Stale results.** A finished task stores the hash of its input files (for example `stellenanzeige.md`). When an input
   changes, the task stays `erledigt`, is marked `veraltet` and is listed in the overview. It is not reset by itself, and
   the dependents are not reset: re-running is the user's decision, with the owning skill.

## WF-6 Store, reconciliation and idempotence

1. **Place.** `<wurzel>/workflow/aufgaben.json` (`version` 1, `grenzen`, `aufgaben`), written atomically, under one file
   lock `workflow/.workflow.lock` for every command that is not read-only. A second command waits up to 30 seconds and then
   answers `beschaeftigt`. The readable derivation `workflow/uebersicht.md` is rewritten after each command; its failure does
   not hide the command's result (`warnung_uebersicht`).
2. **A damaged store is reported, not repaired.** Unreadable JSON, an unknown version, a task of an unknown type or status,
   a task whose key fields have the wrong type, a reference to a task that does not exist, or a cycle gives
   `speichern_fehlgeschlagen` or `speicher_ungueltig`, before any command changes anything. A task that merely lacks an
   optional field (an older or hand-written file) is loaded with the default of that field; no result is invented.
3. **Reconciliation (`abgleichen`).** In dependency order, for each task: a missing Vorgang folder blocks it; a final status of
   the Vorgang cancels it; a met postcondition closes it (not a running task: its session still reports with `fertig`; also for work done outside, with a hint when its dependencies were
   not done; an approval task that is still open for that step is cancelled as no longer needed, never marked approved); failed dependencies block it, open ones keep it `wartend`; an expired lease is handled (WF-8 rule 4); a due
   retry becomes `bereit`; a date in `ab` holds it; a prerequisite or approval that fails puts it in the matching waiting
   status; otherwise it is `bereit`. A state left by a command is already reconciled.
4. **A running task that reality stops** (its Vorgang folder is gone, or the Vorgang reached a final status) loses its lease, and
   its open attempt ends as an aborted one.
5. **Idempotence.** Starting a workflow, planning and reconciling again create no task and change no finished one. A task
   taken by an agent cannot be taken again (`laeuft_bereits`) and two sessions racing for it end with one winner. A finished
   task is not taken again.
6. **Internal and external.** An internal, repeatable task (an analysis) may be repeated by the rules of WF-8. An external
   action is never repeated to find out whether it worked (WF-7). The workflow does not claim exactly-once; it claims that an
   uncertain external outcome stops and asks.

## WF-7 Approvals and external actions

0. **A send approval needs a checked package.** `freigeben` of `versand_freigabe` is refused (`pruefung_veraltet`) when a
   document is newer than `pruefbericht.md`: the quality gate must have seen this content.
1. **Approval is the user's, for one exact content.** `freigeben <aufgabe> --ja` stores the hash of the content as it is now
   (for `versand_freigabe` the hash over the existing documents of the Vorgang, for `nachricht_senden` the hash of the message
   file) with the time. The word `--ja` is the user's explicit yes; a command without it is refused.
2. **The approval expires with the content.** When the content changes, the approval is gone: the task is
   `wartet_auf_freigabe` again, and what follows is held again. A restart, a retry, a scheduler run, a status change, a passed
   check or a passed due date creates or renews no approval. If the workflow cannot tell whether an approval holds, the
   task stays blocked.
3. **A rejection** (`ablehnen`) cancels the task and blocks its dependents. `wiederholen` takes a rejection back (the one way
   out of `abgebrochen`): the approval is asked for again, and the dependents wait instead of being blocked.
4. **Who may approve.** Only an interactive command. In an interactive session the `--ja` is the user's word, not proof of it: an
   agent can type the flag. So do not put `freigeben` (or `weiter`, `ausgang`, `ausfuehren`) into the allowed Bash rules of Claude Code;
   then every one of them asks you first. The skills tell the agent never to run them for you. A session marked unattended (`WORKFLOW_UNBEAUFSICHTIGT`, or
   `STELLENSUCHE_GEPLANT` of the launcher) is refused `anlegen`, `weiter`, `freigeben`, `ablehnen`, `ausfuehren`, `ausgang`,
   `wiederholen`, `abbrechen` and `grenzen` with `nur_interaktiv`. It may plan, reconcile, look and take, finish or fail the
   tasks that are agent tasks.
5. **The adapter gate (`ausfuehren`).** An external action by an adapter runs only when an adapter for the type is registered,
   the task is `bereit`, and the approval covers the current content. The state `laeuft` with the time of the start
   (`extern_begonnen`) is saved **before** the call. A raised exception, an unsure answer, or a lease that runs out after the
   start leaves the task `wartet_auf_eingabe` with the hint that the outcome is unclear. Neither time nor a retry resolves it;
   only `ausgang --gesendet` or `--nicht-gesendet` of the user does. After `--nicht-gesendet` a new approval is needed. If the
   adapter says it is sure that nothing left, the task fails and is not repeated by itself either.
   The adapter receives the approval with the approved hash and has to send exactly the content with that hash; if the file
   changed between the check and the call, it refuses. That check belongs to the adapter, because the workflow cannot see it.
6. **No adapter ships.** `ausfuehren` answers `kein_adapter`. Sending an application and every message stays the user's
   (LS-6 rule 4); the type `versand` is observed, never executed. The adapter interface is the place A-02 plugs in; until
   then the overview lists such tasks under *Noch nicht integriert*.
7. **Nothing else sends.** Creating documents, a passed quality gate, a draft, a due date and a general instruction to
   automate the process are no approval and no authority to send, to answer an employer, to give a salary, to confirm an
   appointment or to pass on personal data.

## WF-8 Errors, retries and resumption

1. **Error classes** an agent reports with `fehler` (and the workflow itself with `ergebnis_fehlt` and `abbruch`):

   | Class | Leads to |
   |---|---|
   | `vorlaeufig`, `dienst`, `zeitlimit`, `abbruch`, `ergebnis_fehlt` | `wiederholung_geplant` with a backoff of 5, 30, 180 minutes; after `versuche_max` attempts `fehlgeschlagen` |
   | `eingabe` | `wartet_auf_eingabe` |
   | `freigabe` | `wartet_auf_freigabe` |
   | `berechtigung`, `qualitaet` | `blockiert` |
   | `daten`, `dauerhaft` | `fehlgeschlagen` |
   | `unklar` | `wartet_auf_eingabe` (outcome unclear) for an external action; for an internal task a retry with backoff |

   A task that is an external action is never retried automatically, whatever the class.
2. **Done without the result.** `fertig` checks the postcondition. When it does not hold, the attempt is a failure of class
   `ergebnis_fehlt`, not a success.
3. **A report belongs to an attempt.** `uebernehmen` returns the number of the attempt; `fertig` and `fehler` take it as
   `--versuch`, which the command line requires. A report for an attempt that is no longer the latest (the lease ran out and another session took the task) is
   refused with `veraltete_sitzung` and changes nothing.
4. **Orphans.** A running task whose lease ran out is an aborted attempt (class `abbruch`) and follows rule 1; an external one
   follows WF-7 rule 5. The attempt count includes it.
5. **Repeat by the user.** `weiter` (after a hold) and `wiederholen` (of a failed task) start the count again; the latter releases it for the next reconciliation.
   `abbrechen` ends a failed task for good. It never cancels a task whose external action has an unclear outcome
   (`extern_begonnen`): `abbrechen` is refused as a whole (`ausgang_unklar`), also for a Vorgang slug, so that
   nothing is cancelled half; only `ausgang` resolves it, then it can be cancelled.
6. **What is stored about an error.** Class, a reason of at most 200 characters with credentials replaced by `[entfernt]`, and
   the time. No page content and no personal data beyond what the task already refers to.
7. **After a restart** the store is read, finished results and waiting or blocked tasks stay as they are, due retries become
   ready, orphans are handled, and nothing is approved. A failure never disappears by a new status alone: the attempt and the
   error stay in the task.

## WF-9 Planning and the schedule

1. **`starten <slug>`** creates the chain of WF-3 rule 1 for an existing Vorgang (`passung` only with a confirmed Wunschprofil),
   all of it or nothing: if `aufgaben_max` leaves no room for the whole chain, none of it is created.
2. **`laufen`** is the call for a scheduler. It reconciles, plans what the existing state asks for, reconciles again and lists
   what is ready. It executes nothing and sends nothing. It plans:
   - the chain for each Vorgang without a workflow and without a final status;
   - a `suche` task for each approved, active Suchauftrag that is due (`stellensuche` ST-16) and has no open `suche` task. A
     `suche` task of the same round that was cancelled or has failed is not replaced by itself; `laufen` lists it under
     `nicht_ersetzt`. The user retries it with `wiederholen`, or pauses or ends the Suchauftrag to stop the search;
   - a `nachfassen` task for each Vorgang with `status: versendet` whose `wiedervorlage` date has come.
   One unreadable Suchauftrag file is listed under `defekte_auftraege` and does not stop the rest.
   The overview derives, without tasks: the Stellen of the Warteschlange waiting for a decision, tasks waiting for approval,
   failed and blocked tasks, and overdue ones.
3. **Deduplication** is by the task id (WF-3 rule 2): any number of calls gives one task.
   **Dates** (`ab`, `faellig`, `wiedervorlage`) are local dates of the machine, because the user types them as such.
4. **The plugin starts no process.** The user calls `workflow.py laufen` from cron or a timer. Until the user has done that,
   nothing runs by itself, and the docs say so.
5. **Limits stay in force.** The search keeps its own budget (ST-16); the workflow never lifts it. A task for a search is
   only the reminder and the record; the run is made by the agent under the rules of `stellensuche`.

## WF-10 Limits

`grenzen` in the store, with these defaults and bounds: `laufende_max` 2 (1 to 10) tasks running at once; `neu_max_je_lauf` 10
(1 to 50) tasks created per `laufen`; `aufgaben_max` 200 (10 to 1000) tasks in the store; `lease_minuten` 60 (5 to 1440);
`versuche_max` 3 (1 to 10). A value outside the bounds is refused. When `neu_max_je_lauf` is used up, the rest is reported as
`zurueckgestellt` and follows in the next run; when `aufgaben_max` is reached, creation stops with that note. Only the catalog
creates tasks and a task never creates tasks, so there is no chain of new tasks. A limit never deletes a stored result.

## WF-11 Priority and the next action

Priority is `prioritaet` 1 to 5 per type (decisions of the user 5, follow-up 4, work of the agents 3, search 2). The order of
`naechste` and of the overview is: overdue first, then priority, then due date, then age. Priority does not grant permission:
a task that waits for a prerequisite or an approval is not listed as ready however high it ranks. The overview comes from the
stored state only and invents no result.

## WF-12 Integration with the skills

| Step | Done by | How the workflow takes part |
|---|---|---|
| Reconcile, plan, list, order | the script, automatically (when the user schedules `laufen`) | WF-6, WF-9, WF-11 |
| Analysis, fit check, documents, quality gate, follow-up draft, search | an agent with the named skill, prepared by the workflow | `uebernehmen`, then `fertig` or `fehler`; the postcondition is checked by the script |
| Plan, send approval, sending, the entry of S7 and S8 | the user | the workflow observes and holds what follows |
| Approvals | the user | WF-7 |
| Sending by an adapter, mail and calendar of A-02 | not integrated | the adapter interface of WF-7 rule 5 exists; no adapter ships |

1. The skills keep their rules and their files; none calls the workflow. An agent that works on a task takes it first, so
   that two sessions do not do the same work, and reports when it is done or has failed.
2. **The engine runs no skill.** The skills are instructions for an agent, not callable functions. The workflow decides
   what is next and checks the result; it does not pretend to execute.
3. **An unattended session** (a scheduled `claude -p`) may be given exactly `uebernehmen`, `fertig`, `fehler`, `laufen`,
   `abgleichen`, `naechste` and `uebersicht` as Bash prefixes. A file rule for results is written
   `Edit(//absolute/path/*)` with two slashes; a `Write(...)` rule is not matched (checked with `claude -p`, see Provenance).
   The session inherits the permissions of the user's own settings; the launcher of the search documents the same limit
   (`stellensuche` ST-16 rule 5).
4. **Existing data.** The workflow adds the folder `workflow/` and changes no existing file. Vorgänge that exist are picked up by
   `laufen` and their tasks are closed from their files; nothing is migrated and nothing is deleted.

## WF-13 Security

1. A posting, a mail, a page and an imported document are data. They are stored only as what a task refers to (a path, a hash);
   their text never becomes a task type, a dependency, a permission, a limit or a command (R-6, RC-5.0 rule 5).
2. The permissions of a task come from the catalog and the user's explicit decisions, never from a sentence in external text.
3. A reference in a task (`bezug`) is a slug of `a-z`, `0-9` and `-`, or a plain file name of `.md` or `.txt` in the Vorgang
   folder; anything with a path separator is refused.
4. The workflow writes only below `<wurzel>/workflow/`, after the repository boundary check of `lokale-struktur` LS-2.4. It
   reads Vorgang files and the state of `stellensuche`, and writes into neither.
5. **The limit of a local file.** The store is a file the user owns. The workflow protects against its own commands and
   sessions, not against someone who edits the file by hand or an agent that may write the Wurzel: a forged entry in
   `entscheidung` would be believed. Skills write only their own files (LS-5.7) and no skill writes `workflow/`; the
   unattended sessions of the launchers may write only the folder for search results.
6. Errors are shortened and stripped of credentials (WF-8 rule 6). The folder is personal data and belongs in a private
   repository (R-6, LS-9).

## WF-14 Acceptance scenarios and open points

Automated in `tests/test_workflow.py` with invented data; no model, network or mail is involved.

| ID | Scenario | Expected behaviour |
|---|---|---|
| WA-A | A chain is started for a Vorgang | only `analyse` is ready; the rest waits with the id it waits for; `passung` only with a confirmed Wunschprofil |
| WA-B | Every pair of statuses | allowed pairs pass, all others are refused; `abgebrochen` has no exit |
| WA-C | A cycle, a missing reference, an unknown type, a path in `bezug` | refused; the store is not changed |
| WA-D | `analyse` fails permanently | its dependents are `blockiert` with the id; a repeat releases the chain, it does not run it |
| WA-E | The store is read after a restart, much later | finished results, waiting and blocked tasks are unchanged |
| WA-F | A running task misses its lease | an aborted attempt, a retry after the backoff; an external one is unclear |
| WA-G | A damaged or foreign store | reported with a code; nothing is changed |
| WA-H | `starten` and `laufen` many times | no new task; one winner when sessions race for a task |
| WA-I | Errors of each class; attempts over the limit | the status of WF-8 rule 1; after `versuche_max` the task fails; no retry beyond a lowered limit |
| WA-J | `fertig` without the result | a failed attempt of class `ergebnis_fehlt`, never a success |
| WA-K | The send approval | waits for the user; time, restart and repeated runs grant nothing; `--ja` is required |
| WA-L | A document changes after the approval | the approval is gone and `versand` is held again |
| WA-M | A rejection | the task is cancelled, what follows is blocked |
| WA-N | An unattended session | refused every changing command with `nur_interaktiv`; may plan, look and report |
| WA-O | `ausfuehren` without adapter, without approval, after a change | refused; nothing is sent |
| WA-P | An adapter raises, or a crash happens during the call | `wartet_auf_eingabe`, the hint says unclear; time and a repeat do not resolve it; `ausgang` does |
| WA-Q | A sure failure of the adapter | `fehlgeschlagen`; no automatic retry |
| WA-R | A due Suchauftrag; an unapproved, paused or ended one | one `suche` task; none for the others; the approval stays with `stellensuche` |
| WA-S | A follow-up is due | one `nachfassen` task; an old draft does not count as done |
| WA-T | More Vorgänge than the budget allows; the cap of tasks | the rest is `zurueckgestellt` and follows; creation stops at `aufgaben_max` |
| WA-U | More tasks to take than `laufende_max` | the extra one stays ready, nothing is lost |
| WA-V | The chain from a posting to a sent application | each step closes from its files; the approval is the user's; the entry of S7 closes `versand` |
| WA-W | Work done outside the workflow | recognised, tasks closed, a hint where dependencies were open |
| WA-X | An input changes after a result | `veraltet`, still `erledigt`, not reset |
| WA-Y | A posting with instructions; a tampered store; credentials in an error | no task, no limit, no type; refused; stripped |
| WA-Z | The overview file cannot be written | the command keeps its result with `warnung_uebersicht` |
| WA-AA | An agent reports a hold (information, approval, permission, quality) | it survives every reconciliation and schedule run; an unattended session cannot lift it; `weiter` of the user does |
| WA-AB | A session whose lease ran out reports | `veraltete_sitzung`; the successor's attempt is untouched |
| WA-AC | A cancelled or failed search task of this round | not replaced by itself and listed under `nicht_ersetzt`; a failed task can be cancelled |
| WA-AD | A store with missing optional fields; one with a dangling reference or a wrong type | defaults are filled; the other is refused before any change |
| WA-AE | An adapter answer that is no object; a heading `## Planungsnotizen`; a limit `laufende_max=²`; a date around midnight in another time zone | unclear outcome; no plan; refused; the local date counts |
| WA-AG | The cap leaves room for half a chain; a fit check appears later; it is cancelled | the whole chain waits; `passung` joins `plan`; cancelling it does not block `plan` |
| WA-AH | A running task's Vorgang vanishes or ends; a hold is overtaken by work done by hand | lease and attempt end; the hold is cleared |
| WA-AI | A report without `--versuch`; a loaded store with a path in `bezug`, a half attempt or a bad limit | refused by the command line; `speicher_ungueltig` before any change |
| WA-AJ | `ausfuehren` after the Vorgang was rejected; an unreadable Suchauftrag | refused after reconciling, nothing sent; planning goes on and lists the file |
| WA-AL | `freigeben` after a document was edited since the quality report; a refused command after a lease ran out; a damaged store; a result with ok=false; a reported-running task whose files look finished | refused with `pruefung_veraltet`; the expiry is still saved; `speicher_ungueltig` and `wurzel` still works; exit code 2; the task stays `laeuft` until `fertig` |
| WA-AM | `weiter` after several holds; `abbrechen` by a name that is both a Vorgang and a Suchauftrag; `ausgang` confirms a send; the content changes right before the adapter call; `fehler` class `unklar` on an internal task | attempts start again after `weiter`; only the exact id, else the Vorgang, else the Suchauftrag; the unclear marker goes; a new approval is asked for, not a failure; a retry with backoff |
| WA-AN | A chain longer than `neu_max_je_lauf`; a repair that would close a cycle; the same task id with another `ab`; a reference that is no string | the chain comes whole, first in its run; nothing is changed; refused with `aufgabe_existiert`; `speicher_ungueltig` |
| WA-AO | An ended Vorgang older than 90 days with every task over; a rejected approval and `wiederholen` | its tasks are removed by `laufen`; a running Vorgang keeps its tasks; the approval is asked for again and the dependents wait |
| WA-AF | The final reconciliation of a command fails | the command keeps its result and its saved state, with `warnung_abgleich` |
| WA-AK | `wurzel`; a second message for one Vorgang; `abbrechen` of an unclear send; the content changes after the lease is saved; a step done by hand; a search finished 30 days ago | `wurzel` prints the Wurzel; each message is its own task; the unclear task stays; nothing is sent and the attempt ends as plain failure; the open approval is cancelled, none invented; `laufen` removes the old search task and lists it under `aufgeraeumt` |

| Area | Point | Status |
|---|---|---|
| Execution of skills | The skills are not callable; an agent runs them. A headless session per ready task (like the search launcher) is not built | open, deliberate |
| Scheduler | `workflow.py laufen` is the call; the user sets cron or a timer. A headless worker for ready agent tasks is not provided | open, deliberate |
| Sending | No adapter ships; sending stays the user's (S7). A-02 (`mail-verwaltung`) is specified, not implemented | open, depends on A-02 |
| Stale results | Marked, not re-run; the user decides | decided |
| Several machines | One store, one lock on one disk; no sync | decided |
| Replies and appointments | Not observed: S8 stays the user's (LS-6 rule 4) | open, depends on A-02 |
| Cost of a command | A state-changing command reconciles up to three times and re-reads files each time under the lock; fine for the budgeted store size (`aufgaben_max`), not optimised | open, deliberate |
| Code duplication | The start of an attempt and its lease is written in `uebernehmen` and `ausfuehren` (the adapter path saves between the two steps) | open, deliberate |
| Quality report age | The check that the report is newer than the documents compares file times; a copy that resets times, or a missing report, is not caught | open, deliberate |
| Follow-up draft time | `nachfassen` compares the draft's file time with the task's creation second; under `--jetzt` in the future it does not match | open, deliberate |
| What the approval covers | The hash covers the Markdown and text sources of the package (`DOKUMENTE`), not exported PDF or DOCX files or other attachments; the user checks those before sending | open, deliberate |
| Trust in `vorgang.md` | A step the Vorgang file shows as done counts as done (also ahead of its predecessors, with a hint); a wrong `status` there is not caught | decided (LS-6) |
| Re-run of a finished check | A task that is `erledigt` cannot be taken again; after a document changed, the user runs the quality gate outside the workflow (its newer report lifts `pruefung_veraltet`), and the task keeps showing `veraltet` | open, deliberate |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |
