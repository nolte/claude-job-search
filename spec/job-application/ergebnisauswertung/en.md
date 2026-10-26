# Evaluation of application results (EN canonical)

Normative rules for how the confirmed results of many applications are counted, summarised and turned into proposals that the user
may take up. It is implemented by `scripts/lernen.py`; the results themselves come from `scripts/kommunikation.py` (the
communication after the dispatch, `spec/job-application/mail-verwaltung/en.md` MV-18 to MV-27) or from the user's own statement.

Related rules: `spec/job-application/lokale-struktur/en.md` (LS-5 invariants, LS-6 lifecycle and status values, LS-6 rule 8 retention,
LS-9 privacy), `spec/job-application/qualitaetssicherung/en.md` (QS-7 report, QS-13 ATS validation: quality is not a result),
`spec/job-application/workflow/en.md` (WF-3 task catalog, WF-7 approvals) and `spec/job-application/konventionen/en.md` (R-1 facts,
R-6 data protection).

**Status:** implemented. The evaluation counts and proposes; it changes no status, no document and no personal data (EA-10).

## EA-1 Terms and principles

| Term | Meaning |
|---|---|
| **Ereignis** | One confirmed fact about the course of an application: a reply, an invitation, a refusal, an offer. Stored in `<vorgang>/nachverfolgung.json` (EA-3). |
| **Ergebnis** | The kind (`art`) of an Ereignis, or a state derived from the status the user keeps in `vorgang.md` (EA-4). |
| **Auswertung** | A derivation over many Vorgänge: statistics, retrospective, proposals. It is never the source of a result. |
| **Vorschlag** | A proposal for an improvement that rests on confirmed results (EA-10). |

1. **The Vorgang is the source.** `status` and `## Verlauf` of `vorgang.md` (LS-6) stay the one history of an application. An Ereignis is
   the structured counterpart of a Verlauf line, not a second status.
2. **Only confirmed results count.** A proposal for a message, an Ereignis in the state `erkannt` or `zur_pruefung`, and a discarded
   Ereignis are not results.
3. **No cause.** The evaluation counts what happened. It does not say why an application succeeded or failed (EA-9 rule 4).
4. **Quality is not a result.** A passed quality check (QS) is no proof of a successful application, a refusal no proof of a faulty
   document. The two are shown apart and never merged into one figure (EA-8).
5. **Derivations are marked and go stale.** Every output says that it is derived and carries a hash of its sources (EA-9).

## EA-2 Result kinds

| Group | Kinds (`art`) |
|---|---|
| positive | `eingangsbestaetigung`, `kontaktaufnahme`, `gespraechseinladung`, `gespraech`, `technisches_gespraech`, `assessment`, `weitere_phase`, `angebot`, `einstellung` |
| negative | `absage`, `absage_nach_unterlagen`, `absage_nach_gespraech`, `absage_nach_assessment`, `zurueckgezogen` |
| further | `rueckfrage`, `gespraechsfeedback` |
| open | not stored: derived from the state (EA-4): no reply yet, reply expected, process open, assignment unclear |

The kinds are the closed list `kommunikation.ARTEN`. `absage` without a stated phase stays `absage`; the phase is set by the user
(`absage_nach_gespraech`), never inferred.

## EA-3 The Ereignis

Fields: `id` (`e-001`…), `art`, `datum` (ISO date, may be empty and is then never estimated), `quelle` (`nachricht` with the message
reference, or `nutzer`), `original` (a literal part of the message, at most 240 characters, amounts removed), `interpretation` (separate from
the original, EA-6), `status`, `erfasst`, `bestaetigt_am`, and for a correction `korrekturen` with the old values.

| Status of an Ereignis | Meaning |
|---|---|
| `erkannt` | found by a rule, nobody looked at it; not counted |
| `zur_pruefung` | waits for the user; not counted |
| `bestaetigt` | the user confirmed it as it is |
| `korrigiert` | the user changed it or assigned it by hand |
| `verworfen` | the user threw it away; stays in the file for the trace, not counted |

The status of an Ereignis, of a message (`vorgeschlagen`, `bestaetigt`, `korrigiert`, `verworfen`), of a workflow task and of a proposal
(EA-11) are four different things and are never mixed. The status of the Vorgang stays `status` in `vorgang.md`.

## EA-4 Population and flags

1. **Population.** The dispatched applications: `versendet_am` is a real date. A Vorgang before the dispatch, without `versendet_am`,
   outside the period or whose `loeschen_ab` has been reached is out and is counted under `ausgeschlossen` with its reason (retention,
   LS-6 rule 8: derived figures do not live on data that is due for deletion).
2. **Flags** of a Vorgang come from its confirmed Ereignisse and from the status the user keeps: `rueckmeldung` (any reply except a bare
   confirmation of receipt), `einladung`, `gespraech`, `weitere_phase`, `angebot`, `einstellung`, `absage`, `ohne_antwort`. A status
   implies flags (`zusage` implies invitation, interview, offer and hire; `gespräch` implies an invitation, not a held interview).
3. A flag that rests on the status alone is counted and shown in `datenqualitaet.ergebnis_nur_durch_status`.

## EA-5 Statistics

`lernen.py statistik [--von --bis --status --arbeitgeber --stellenprofil --ausrichtung] [--nach SEGMENT]` returns one JSON object with:

1. **Counts:** applications, closed, open, replies, refusals, invitations, interviews, offers, hires, closed without reply, open without
   reply.
2. **Response rate** `ruecklaufquote`: numerator = applications with at least one confirmed, substantive reply; denominator = all dispatched
   applications in the period. **Open applications stay in the denominator**; they are reported as `offen_ohne_rueckmeldung`, never as
   failures. `ruecklaufquote_ohne_offene` = replies / (replies + applications the user closed as `ohne Antwort`). Both carry their
   definition in the output.
3. **Transitions:** application to reply, to invitation, invitation to a further phase, invitation to offer, application to hire. Each is
   `zaehler`, `nenner`, `quote`.
4. **Limited data:** a denominator below 5 sets `eingeschraenkt: true` with a note; the quote is shown, as a snapshot and not as a trend.
5. The output is reproducible: the same sources give the same figures (the time of the run is the only input that moves).

## EA-6 Feedback: original and interpretation

1. The original is stored apart from the interpretation (`original`, `interpretation`).
2. The interpretation has `kategorie`, `bezeichnung`, `thema`, `aussage`, `sicherheit`, `grund_genannt` and a `hinweis`. Categories: professional
   qualification, work experience, project experience, technical knowledge, certifications, leadership, communication, languages,
   availability, salary expectation, organisational reasons, other applicant preferred, general refusal, unknown reason. The list is the
   constant `kommunikation.KATEGORIEN`; the user may set any other key (`a-z0-9_`).
3. A category found by a pattern has `sicherheit: niedrig` and the note that it is no confirmed gap. Only the user raises it (`korrigiert`,
   `mittel`).
4. **A refusal without a stated reason** is stored as `absage` with `kategorie: unbekannt`, `grund_genannt: false`. No professional weakness
   and no quality of the documents is derived.
5. A feedback never changes the Datengrundlage (EA-10 rule 3).

## EA-7 Response times

A response time is the number of days from `versendet_am` to the date of the first confirmed Ereignis of its kind: first reply, receipt
confirmation, invitation, refusal (kept apart). It is computed only when both dates exist and the Ereignis is assigned. An Ereignis without
a date is counted in `ohne_datum`, one dated before the dispatch in `datum_vor_versand`; neither is estimated or replaced. Median, minimum
and maximum are shown with `n`; below 5 values the result is `eingeschraenkt`.

## EA-8 Segments, versions and quality

1. `--nach` groups by `arbeitgeber`, `zeitraum` (month of the dispatch), `kanal`, `quelle`, `ausrichtung`, `stellenprofil`,
   `dokumentversion` or `bewertung` (the verdict word of `passung.md`). Only data that exists is used; a missing value is `unbekannt`.
2. A group below 5 applications is `vergleichbar: false`. Groups with different postings, seniority, employers or periods are not
   comparable without the user's check; the output says so.
3. **Document version.** It is unambiguous only if `qualitaet.json` exists, is current for all documents and exports, and `anhaenge` names what
   was sent. Otherwise the Vorgang is `nicht_eindeutig` and is listed in `datenqualitaet`. The last quality check is not proof of what was sent.
4. The quality status (`gesamt`, ATS scope) is never an input of a rate and never a segment. It may be shown beside a result, not tied to it.

## EA-9 Retrospective

`lernen.py retrospektive [filters]` writes `lernen/retrospektive-<datum>.md`; with a period or a filter the name carries a short hash of the criteria, so
other criteria on the same day do not replace the file (the same criteria do).

1. It states the **Datenbasis**: period, number of evaluated and open Vorgänge, those without a confirmed Ereignis, Ereignisse and messages
   still to check, exclusions with reasons, the criteria used.
2. It lists what happened (dispatched, replies, invitations, interviews, offers, hires, refusals, open), the refusals with the **stated** reasons
   (the original in quotes and whether the category is confirmed), themes named in at least two Vorgänge, the groups by direction and profile
   with the warning about comparability, and the limits.
3. It is a derivation: the front matter holds `abgeleitet: ja` and `quellen_hash`. `lernen.py aktualitaet <datei>` says whether a source changed.
4. **No causal statement.** A theme named in two refusals is "named in two Vorgänge", never "the reason for". The text avoids "led to" and
   "because of".

## EA-10 Proposals

1. `lernen.py vorschlaege erzeugen` creates proposals by fixed rules over confirmed results: a stated reason named in at least two Vorgänge
   (check that requirement before the next application); Vorgänge without an unambiguous document version (make the version provable);
   messages not yet checked (check them, otherwise they stay out); applications without a reply for longer than `nachfass_tage` of the Anker
   (consider a follow-up). A rule that needs a deadline does not run without the user's `nachfass_tage`.
2. A proposal has `id` (stable from rule and sources), `titel`, `beschreibung`, `bereich`, `beobachtung`, `quellen` (Vorgang and Ereignis),
   `begruendung`, `erwarteter_nutzen`, `unsicherheit`, `risiken`, `prioritaet`, `status`, `entscheidungen`, `quellen_hash`, and
   `aendert_stammdaten: false` always.
3. **No change of personal data.** Accepting or carrying out a proposal changes no file. No qualification, experience or personal item from a
   posting, a refusal or an interpretation enters the Datengrundlage or `profil.md` by the toolchain; the user does that in the owning skill
   (`job-application-profile-capture`, `job-application-cv-maintain`) with the usual evidence.
4. A proposal rests on real information: its sources are listed and re-checked; a changed or removed source, or a source Vorgang whose
   `loeschen_ab` has been reached, makes it `veraltet`.

## EA-11 Proposal status and approval

| Status | Meaning | Next |
|---|---|---|
| `erstellt` | made by a rule | `zur_pruefung` (`vorlegen`) |
| `zur_pruefung` | shown to the user: observation, sources, reasons, effect, uncertainty | `angenommen`, `abgelehnt`, `zurueckgestellt` |
| `zurueckgestellt` | later | `zur_pruefung` |
| `angenommen` | the user wants to carry it out | `umgesetzt`, `abgelehnt` |
| `umgesetzt` | the user says it is done (nothing happens by this status) | – |
| `abgelehnt` | the user declined | – (a rule does not make it again) |
| `veraltet` | a source changed | the rule may make a new one |

A decision is `lernen.py vorschlag entscheiden <id> --entscheidung … --grund … --ja`. It is refused without `--ja`, without a reason, from a
status not in the table, and in an unattended session (`WORKFLOW_UNBEAUFSICHTIGT`, `STELLENSUCHE_GEPLANT`).

## EA-12 Results by the user's statement

`lernen.py ergebnis erfassen <vorgang> --art … --datum … [--original … --kategorie … --thema …] --ja` records a result the user states (for
example an interview that took place). It adds an Ereignis with the status `bestaetigt` and one line to `## Verlauf` without a change of
status. `korrigieren` and `verwerfen` keep the old value in `korrekturen`. A missing date is refused, not estimated. All three need `--ja`
and an interactive session.

## EA-13 Workflow

The workflow (WF-3) holds three task types for the user: `rueckmeldung_pruefen` (messages of a Vorgang wait for the check), `wiedervorlage`
(a Wiedervorlage is due) and `lernvorschlag_pruefen` (a proposal waits). They are created by `workflow.py laufen`, one open task per kind and
scope, and are done when the files show it. They execute nothing and send nothing; a follow-up message stays a `nachricht_senden` task with
the approval bound to the exact file (WF-7).

## EA-14 Limits and open points

| Area | Point | Status |
|---|---|---|
| Causes | The evaluation says nothing about why an application failed | by design |
| Small data | Few applications: figures are snapshots | stated in every output |
| Document versions | The last quality check is not proof of what was sent; a stored hash of the sent files at the dispatch would close this | open |
| Free-text feedback | The category is found by fixed patterns; understanding the sentence is for the user | by design |
| Connector | No mailbox connector ships; the messages arrive as a JSON list (MV-19) | open, see MV-27 |
| Scheduler | No schedule: runs start when the user asks | by design |
| Language | German wording only for the mail types and categories | open |

## EA-15 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| EA-A | Six dispatched applications, three open | open ones stay in the denominator and are shown separately; `ruecklaufquote_ohne_offene` leaves them out |
| EA-B | A refusal without a reason | `kategorie: unbekannt`; the retrospective says "Grund unbekannt"; no proposal |
| EA-C | The same stated reason in two Vorgänge | one proposal with both sources; `unsicherheit` says that no cause is shown; no change of the Datengrundlage |
| EA-D | An Ereignis without a date | counted under `ohne_datum`; no response time |
| EA-E | A source changes after the retrospective | `aktualitaet` reports it as stale |
| EA-F | A Vorgang reaches `loeschen_ab` | it leaves the figures and the proposals that cite it become `veraltet` |
| EA-G | A refused proposal | stays refused; the rule makes no second one |
| EA-H | A message proposal not yet confirmed | not in any figure |
| EA-I | Quality report `BLOCKIERT` vs `BEREIT` on the same Vorgang | the same result figures |

## EA-16 Sources

- `spec/job-application/mail-verwaltung/en.md`, `lokale-struktur/en.md`, `workflow/en.md`, `qualitaetssicherung/en.md`
- `project/roadmap.md` (statistics and retrospective across Vorgänge)
