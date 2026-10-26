# Follow-up and learning

After you send an application, `job-application-follow-up` keeps the course of it: replies enter the Vorgang as proposals that
you approve, Wiedervorlagen remind you, and the confirmed results of many applications become figures and a retrospective. Two small
scripts do the work, `scripts/kommunikation.py` and `scripts/lernen.py`; both read and write files in your Wurzel only. The rules are in
`spec/job-application/mail-verwaltung/en.md` (MV-18 to MV-27) and `spec/job-application/ergebnisauswertung/en.md` (EA-1 to EA-16).

## What it does and what it does not

| Part | Who | Status |
|---|---|---|
| Read a reply you hand over (a JSON list, or text you paste), assign it to a Vorgang, name the mail type | the script, by fixed rules | works; **no mailbox is read**, you hand the mail over |
| Propose the `## Verlauf` line, the status change, the result and a Wiedervorlage | the script | works; nothing is written yet |
| Write them | you approve the exact proposal (`bestaetigen --hash … --ja`) | by design never automatic |
| An unclear or unassigned mail, an unknown mail type | you decide (`zuweisen`) | never guessed |
| Wiedervorlage and the basis of a follow-up | the script; the date is yours | works; a Wiedervorlage never sends |
| The follow-up mail itself | `job-application-email-create`, then your approval in the workflow | works as a checked draft |
| Sending, reading Gmail, calendar | nobody | **not integrated**: no connector, no send adapter ships |
| Statistics, retrospective, proposals | the script, from confirmed results | works; derived, never the source |

The status stays `status` in `vorgang.md`; the dispatch (S7) stays your statement. Nothing is sent, and no mail is stored as full text.

## Processing replies

```bash
python3 <plugin>/scripts/kommunikation.py verarbeiten --nachrichten eingang.json   # or: task communication -- verarbeiten …
python3 <plugin>/scripts/kommunikation.py liste --status vorgeschlagen
python3 <plugin>/scripts/kommunikation.py zeige <id>                                # the proposal as it is now, with its hash
python3 <plugin>/scripts/kommunikation.py bestaetigen <id> --hash <hash> --ja       # writes exactly what zeige showed
```

A message has `id`, `thread_id`, `von`, `betreff`, `datum`, `text` and `anhaenge`. Each is assigned by reference number, sender domain, thread,
firm name and job title. With two possible Vorgänge nothing is assigned: you see both with their reasons and choose
(`zuweisen <id> --vorgang … --typ …`), and then you confirm the new proposal. A proposal carries a certainty: `eindeutig`, `wahrscheinlich`,
`unklar` or `nicht_zuordenbar`. A hash binds your approval to the exact lines; if the status of the Vorgang moves in between, the hash changes and
you look again. The result is a line in `## Verlauf`, optionally a status change (only forward, only after `versendet`), an event in
`<vorgang>/nachverfolgung.json` and, if you give a date, a Wiedervorlage.

What is stored: references (message id, thread), the sender domain, a short literal quote (at most 240 characters, amounts removed) and the
attachment names. No full mail text, no address, no salary figure.

## Wiedervorlage and follow-up

```bash
python3 <plugin>/scripts/kommunikation.py wiedervorlage anlegen <vorgang> --anlass nachfassen --faellig 2026-11-10
python3 <plugin>/scripts/kommunikation.py nachfass <vorgang> --nach-tage 14
```

A due Wiedervorlage becomes a task for you (`workflow.py laufen`). `nachfass` says whether a follow-up makes sense: sent, no substantive reply,
nothing waiting for the check, and **a deadline you set** (`--nach-tage`, `nachfass_tage` in `konfiguration.md`, or `wiedervorlage` in
`vorgang.md`). Without a deadline it asks you; there is no default. The draft is written by `job-application-email-create`; before anything is
sent you see message, recipient and Vorgang and approve the exact file in the workflow.

## Results and evaluation

```bash
python3 <plugin>/scripts/lernen.py statistik --von 2026-10-01 --nach zeitraum      # or: task learn -- statistik …
python3 <plugin>/scripts/lernen.py retrospektive
python3 <plugin>/scripts/lernen.py vorschlaege erzeugen
```

| Figure | How it is counted |
|---|---|
| Response rate | applications with a confirmed, substantive reply / all dispatched applications in the period. **Open applications stay in the denominator** and are shown apart; `ruecklaufquote_ohne_offene` leaves them out |
| Transitions | application to reply, to invitation; invitation to further phase and to offer; application to hire |
| Response times | days from `versendet_am` to a dated event; an event without a date is counted, never estimated |
| Segments | by employer, month, channel, source, direction, profile, document version, fit verdict; a group below 5 is marked not comparable |

Only confirmed results count: a proposal is no result, and a message not yet checked is listed under `datenqualitaet`. A figure that rests on
the status alone is shown as such. A denominator below 5 is a snapshot. The retrospective states its basis (period, evaluated and open Vorgänge,
exclusions) and is stale as soon as a source changes (`aktualitaet`). A Vorgang whose `loeschen_ab` has passed leaves the figures.

**What the evaluation does not say.** It does not say why an application failed. A refusal without a stated reason is "reason unknown" and gives
no weakness of you or of the documents. A stated reason is a hint with low certainty until you confirm it. A theme named in two refusals is
"named in two Vorgänge", not a cause. A passed quality check is no proof of success, and a refusal no proof of a faulty document; the quality
status is not part of any rate.

**Proposals.** Rules make proposals (a stated reason named in two Vorgänge, Vorgänge without a provable document version, messages not yet
checked, applications without a reply after your `nachfass_tage`). Each has sources, a reason, an effect, a risk and an uncertainty. You show it
(`vorlegen`), then decide with `--ja`. Accepting a proposal changes **no file**: your Datengrundlage and `profil.md` change only through you, in
`job-application-cv-maintain`, with evidence.

## Limits

- No Gmail connector and no send adapter ship; the interface is the JSON list and the approval task `nachricht_senden`.
- Mail types and reasons are found by fixed German patterns; unusual wording is `unbekannt` and needs your decision.
- The document version of a Vorgang is unambiguous only with a current `qualitaet.json` and named attachments in `vorgang.md`.
- Runs start when you ask; the plugin sets no timer.
