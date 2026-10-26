# Workflow

The workflow keeps the order of the steps of an application, what each step needs, what is done, what waits for you and what
failed, across sessions and restarts. It is a small helper script, `scripts/workflow.py`, with a file in your Wurzel. It is
**not** a server and not a background process, and it does not run the skills for you.

The rules are in `spec/job-application/workflow/en.md` (WF-1 to WF-14). This page is how to use it.

## What it does and what it does not

| Step | Who does it | Status of the feature |
|---|---|---|
| Plan the steps, check what is ready, order them by deadline and priority | the script | works; runs when **you** call it or schedule it |
| Analysis, fit check, documents, quality gate, follow-up draft, search | an agent with the skill, prepared by the workflow | works as a hand-over: the agent takes the task and reports; the script checks the result in your files |
| Plan approval (S3), sending (S7), entries about replies (S8) | you | the workflow only watches your files and holds what follows |
| Approval of the exact documents to send | you | works (`freigeben --ja`), bound to the content |
| Sending by the program, mail, calendar | nobody yet | **not integrated**: no sending adapter ships (the mail functions of A-02 are only specified) |
| Running by itself on a timer | your cron or timer | **not set up by the plugin** (see below) |

The application status stays in `vorgang.md`. The workflow never writes into a Vorgang and keeps no second status.

## How it works in short

- A Vorgang gets a chain of tasks: `analyse`, `passung` (only with a confirmed Wunschprofil), `plan`, `unterlagen`, `pruefung`,
  `versand_freigabe`, `versand`. Each task has a status (`wartend`, `bereit`, `laeuft`, `wartet_auf_freigabe`,
  `wartet_auf_eingabe`, `wiederholung_geplant`, `erledigt`, `fehlgeschlagen`, `blockiert`, `abgebrochen`).
- A task is **done only when its result is in your files** (for example `analyse.md` exists and `status` is at least
  `analysiert`). If you or a skill did the step outside the workflow, the next check notices and closes the task.
- A failed step never releases the next one: the dependents are `blockiert` and say why.
- A search task is created for each approved, active Suchauftrag that is due, and a follow-up task when `wiedervorlage` of a sent
  application has come. Tasks are never created from posting text.

## Setup

Nothing to install. The folder `workflow/` is created in your Wurzel on first use. Like `suche/`, it holds personal data and
belongs in a private repository only.

```bash
# in your working folder (the one with job-application/konfiguration.md)
python3 <plugin>/scripts/workflow.py laufen          # or: task workflow -- laufen
```

## Examples

1. **Start the workflow for a Vorgang:** `workflow.py starten musterfirma-backend`. It creates the chain; only the first step is
   ready.
2. **See what is next:** `workflow.py naechste`, or open `workflow/uebersicht.md` in your vault. It lists what is ready for an
   agent, what is ready for you, what waits for your approval or for information, what failed and what is overdue.
3. **An agent does a step:** Claude runs `uebernehmen analyse:musterfirma-backend` (it answers with an attempt number), does the
   work with the named skill, then `fertig analyse:musterfirma-backend --versuch 1` (the attempt number is required, so that a stale session cannot end the attempt of its successor). If the result is not in the files, that counts
   as a failed attempt and is retried after 5, 30 and 180 minutes, three attempts at most. If the agent needs something from you
   (information, an approval, a permission), it reports `fehler ... --klasse eingabe` (or `freigabe`, `berechtigung`, `qualitaet`):
   the task then waits until you run `workflow.py weiter <aufgabe>`.
4. **Approve the documents to send:** after the quality gate, `workflow.py freigeben versand_freigabe:musterfirma-backend --ja`.
   If a document was edited after `pruefbericht.md`, it is refused (`pruefung_veraltet`): run the quality gate again first.
   An exit code of 2 means the command ran but reports `ok: false` (for example `fertig` without its result); 3 is a refusal.
   The approval covers exactly the documents as they are now. If you change one, it expires and the send step is held again.
   Sending is yours: you send, then enter `versendet` and `versendet_am` in `vorgang.md`; the next check closes `versand`.
5. **Look into a failure:** `workflow.py zeige <aufgabe>` shows the attempts, the error class, the reason and the history.
   `workflow.py wiederholen <aufgabe>` lets a failed task try again.
6. **Cancel:** `workflow.py abbrechen musterfirma-backend` ends all open and failed tasks of that Vorgang. A cancelled or failed
   search task is not replaced by itself; `laufen` lists it under `nicht_ersetzt` (retry with `wiederholen`, or pause the Suchauftrag). A task whose send has an unclear outcome is not cancelled; decide with `ausgang`
   first. `laufen` removes finished search tasks after 30 days and the tasks of an ended Vorgang after 90 days (`aufgeraeumt`).
   `wiederholen` on a rejected approval asks for it again.
7. **Limits:** `workflow.py grenzen` shows them, `workflow.py grenzen laufende_max=1 neu_max_je_lauf=5` changes them within
   fixed bounds. Defaults: 2 tasks running at once, 10 new tasks per run, 200 tasks in total, a lease of 60 minutes, 3 attempts.

## Running it on a schedule

The plugin installs no timer. `workflow.py laufen` is the call for one: it checks the files, plans what is due and lists what is
ready. It **executes nothing and sends nothing**; the work is done by an agent session you start, or by you. An example line for
cron, once an hour (change the paths):

```text
7 * * * * cd /path/to/working-folder && python3 /path/to/plugin/scripts/workflow.py laufen >> ~/workflow.log 2>&1
```

Until you set something like this up, nothing runs by itself. Calling `laufen` twice never creates a task twice.

## Approvals and safety

- Approvals are bound to the exact content and to your explicit `--ja`. The flag is your word, not proof of it: an agent could type it. Do not
  put `freigeben`, `weiter`, `ausgang` or `ausfuehren` into the allowed Bash rules of Claude Code, so that each of them asks you first. A restart, a retry, a schedule or a passed date never
  creates one. If the workflow cannot tell whether an approval holds, the task stays blocked.
- If a send step is ever done by an adapter and its outcome is unclear (an error, a crash), the task asks you instead of
  trying again. You answer with `workflow.py ausgang <aufgabe> --gesendet` or `--nicht-gesendet`. No adapter ships today.
- An unattended session (a scheduled run) may plan and look, and may take, finish or fail agent tasks. It may not approve, cancel,
  create or change anything else, and may not lift a hold (`weiter`); those commands answer `nur_interaktiv`. Set `WORKFLOW_UNBEAUFSICHTIGT=1` for such sessions.
- A posting is data. Its text never becomes a task, a type, a limit or an approval.
- Error reasons are shortened and credentials are replaced by `[entfernt]`.

## Known limits

- The skills are instructions for an agent, not functions the script can call. The workflow decides and checks; it does not
  execute them.
- No sending adapter, no mail or calendar integration (A-02 is only a specification).
- Replies and interviews (S8) are not observed; you enter them.
- One store on one disk; no synchronisation between machines.
- A result whose input changed is marked `veraltet` and not redone by itself.
- The behaviour of Claude Code permission rules mentioned in the spec was checked with `claude -p` on 2026-10-25 and may change.

## Verification

`python3 -m unittest tests.test_workflow` (97 tests, no network, no model): statuses and transitions, dependencies and cycles,
restart and damaged stores, idempotence and racing sessions, approvals and the adapter gate, errors and retries, the schedule
and the limits, the chain from a posting to a sent application, and the security cases. Not verified: a real adapter (none
exists) and a long-running schedule on a real machine.
