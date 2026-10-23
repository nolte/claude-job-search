# Mail management for applications (EN canonical)

Normative rules for how a skill manages the user's Google Mail account for applications: it sorts
incoming mail with labels, assigns relevant mail to a Vorgang, proposes calendar entries, records
the course of a Vorgang in the Wurzel, and on request proposes a reply. The user owns the rules; the
skill proposes a starting structure and never acts beyond the approvals in MV-8.

Requirement basis: `project/requirements/mail-verwaltung.md`. Related rules:
`spec/job-application/lokale-struktur/en.md` (LS-4 persistence, LS-5 invariants, LS-6 lifecycle, LS-9
privacy), `spec/job-application/kontaktklassifikation/en.md` (KK-3 signals, KK-4 disclosure, KK-5
communication), `spec/job-application/recherche/en.md` (RC-2 level 0), and
`spec/job-application/konventionen/en.md` (R-1 facts, R-4 E-Mail, R-6 data protection).

**Status:** specification only. No skill implements it yet (MV-14).

## MV-1 Terms

| Term | Meaning |
|---|---|
| **Eingang** | The Gmail label `unsort`. Every mail the skill has not yet decided about carries it. |
| **Lauf** | One run of the skill over the Eingang, started by the user (MV-2.1). |
| **Relevanzprüfung** | The coarse decision whether a mail belongs to an application (MV-5). |
| **Zuordnung** | The assignment of a relevant mail to a Vorgang (MV-6). |
| **Sammel-Label** | The label `Bewerbung/_ohne Vorgang` for relevant mail without a safe Zuordnung. |
| **Mailtyp** | The kind of a mail inside a Vorgang: Eingangsbestätigung, Einladung, Angebot, Absage, Zusage or Rückfrage (MV-3.2). |
| **Regelwerk** | The user's rules for Relevanz, Zuordnung, labels and Mailtypen (MV-4). |
| **Freigabe** | The user's explicit approval of one proposed change before it is made (MV-8). |

Vorgang, Wurzel, Anker and Verlauf are used as defined in `lokale-struktur/en.md` LS-1 and LS-6.

## MV-2 Access, trigger and scope

1. **On request only.** A Lauf starts when the user asks for it. There is no schedule and no start at the
   beginning of a session.
2. **Connector.** The skill reaches Gmail and Google Calendar through the Google connector (MCP) of the
   client. It manages no OAuth tokens or credentials of its own.
3. **Allowed operations.** Read mail and threads, read and create labels, add and remove labels on
   messages, read the calendar list, create events in the calendar `Bewerbungen`.
4. **Forbidden operations, whatever the user's Regelwerk says.** Delete, trash, archive, report as spam,
   send, create a Gmail draft, change or delete an existing calendar event, create a calendar. Mail is
   never removed from the account. The skill adds and removes only user labels. It never adds or removes
   a Gmail system label (`INBOX`, `SPAM`, `TRASH`, `SENT`, `DRAFT`, `STARRED`, `UNREAD`), because removing
   `INBOX` is archiving. "Move" means: add the target label and remove `unsort`, nothing else.
5. **One account.** The skill serves the one account the connector is connected to. Other or several
   accounts are not supported.
6. **No research.** A Lauf does no web or register research and uses no search tool. Research stays a
   separate step on the user's request (`recherche/en.md` RC-1 rule 8).

## MV-3 Label structure

### MV-3.1 Proposal

```text
unsort                                      Eingang
Bewerbung/
├── _ohne Vorgang                           Sammel-Label (MV-6.3)
└── <vorgang>/                              folder name of the Vorgang (LS-7.7)
    ├── Eingangsbestätigung
    ├── Einladung
    ├── Angebot
    ├── Absage
    ├── Zusage
    └── Rückfrage
```

1. **Outer level is the Vorgang, inner level the Mailtyp.** `<vorgang>` is the folder name of the
   Vorgang, for example `musterfirma-senior-backend`. It is stable after S1 (LS-6 rule 5), so a label never
   has to be renamed.
2. The structure is a proposal. The user may rename labels, add or drop Mailtypen and change the nesting
   in the Regelwerk (MV-4). Without a Regelwerk, the proposal applies.
3. The skill creates a missing label only after the user has approved the structure once per Lauf.
   Creating a label is not a destructive action, and it needs no approval per mail.

### MV-3.2 Mailtypen

| Mailtyp | Meaning | Proposed status in `vorgang.md` (MV-7.4) |
|---|---|---|
| Eingangsbestätigung | The employer confirms receipt | none |
| Einladung | Invitation to an interview or call | `gespräch` |
| Angebot | The employer offers the position or sends terms | `angebot` |
| Absage | The employer declines | `absage` |
| Zusage | The employer confirms the hire after the candidate accepted (final status) | `zusage` |
| Rückfrage | A question or request for documents | `rückmeldung` |

## MV-4 Regelwerk

1. **The user owns the rules.** Rules for Relevanz, Zuordnung, label names and Mailtypen belong to the user.
   The skill never invents a rule and applies none that the user has not approved.
2. **Proposals.** Without rules, the skill works with the proposal of MV-3 and the matching order of MV-6.
   On request it proposes a rule derived from a user correction (MV-9) or from the mail it sees.
3. **A rule takes effect after Freigabe.** An approved rule stays in force for later Läufe.
4. Where and in which form the Regelwerk is stored is open (MV-14).

## MV-5 Relevanzprüfung

1. **Coarse analysis only.** The skill decides from sender, subject and the start of the text. It does
   this at research level 0 (`recherche/en.md` RC-2): no network, no lookup.
2. **Relevant** means: the mail plausibly belongs to an application of the user, or to the contact with
   a recruiter or an employer.
3. **Not relevant.** A mail that is not relevant is left in the Eingang unchanged. The skill does not
   analyse its content further, does not record it and does not quote it in the chat beyond a count.
4. **Analysis only for relevant mail.** The further analysis of MV-6 and MV-7 starts only after a mail
   is classed as relevant.
5. **Doubt is not relevance.** A mail the skill cannot classify stays in the Eingang and is listed for
   the user.

## MV-6 Zuordnung to a Vorgang

1. **Matching order.** The skill compares, in this order:
   1. the reference number (`ref_nr`) of the Stellenanzeige,
   2. the company name or the title of the posting (`firma`, `stelle`),
   3. the sender (address or domain of the company in `firmen/` or of a known contact).

   The **Gmail thread** is an additional signal. It strengthens a Zuordnung that the three features give,
   and it can carry a mail without a company name when another mail of the thread is already assigned.
   It never replaces the three features.
2. **A Zuordnung needs a clear result.** If the features point to exactly one Vorgang, the mail is
   assigned to it, labelled with `Bewerbung/<vorgang>/<Mailtyp>` and no longer carries `unsort`.
3. **No Vorgang, or a conflict.** If no Vorgang matches, or two features point to different Vorgänge,
   the mail moves to `Bewerbung/_ohne Vorgang` and loses `unsort`. A conflict is reported to the user
   with the features that disagree.
4. **The skill never creates a Vorgang.** A new Vorgang comes from the user's posting
   (LS-6 S1). A mail in the Sammel-Label waits for the user to assign it.
5. **No Vault entry without a Vorgang.** Mail in `Bewerbung/_ohne Vorgang` is not recorded in the
   Wurzel (MV-7).
6. **Contact class.** Signals in a relevant mail may be used as in `kontaktklassifikation/en.md` KK-3.1.
   Recording a classification in `analyse.md` is a change of the Wurzel and needs Freigabe (MV-8).

## MV-7 Record in the Wurzel

1. **Target.** The record of a mail is one line in `## Verlauf` of `vorgang.md` (LS-6 rule 1): date,
   Mailtyp, a short summary in the skill's own words, the Gmail message ID and the thread ID. The Wurzel is the vault
   (LS-8.2).
2. **Metadata plus summary.** The line carries no full text of the mail.
3. **What stays out of the summary.** Salary and contract terms, private contact data of a person
   (private phone number, private address), and the content of attachments. An attachment is noted as
   `Anhang vorhanden: <Dateiname>` only. Business contact data stays in `analyse.md` as
   `lokale-struktur/en.md` LS-4 and LS-6 rule 8 describe.
4. **Status proposal.** The skill may propose a change of `status` from the Mailtyp (MV-3.2). The values
   are the fixed values of LS-6 rule 2. A mail never sets S7 (`versendet`, `versendet_am`, `weg`,
   `anhaenge`); that stays a statement of the user (LS-6 rule 4). A proposal is made only when:
   - the current `status` is `versendet` or a later value, so the user has already stated S7;
   - the proposed value comes later in the order `versendet`, `rückmeldung`, `gespräch`, `angebot`,
     `verhandlung`, then a final status, than the current value (no step back);
   - the current `status` is not a final status (`zusage`, `absage`, `abgelehnt`, `zurückgezogen`,
     `ohne Antwort`).

   Otherwise the skill records the line without a status proposal and tells the user why. A Vorgang
   that is not yet `versendet` gets the line only, and the skill points out that S7 is missing.
5. **Freigabe.** Every write to the Wurzel needs the user's approval of the exact line (MV-8). A rejected
   proposal is not written and not repeated for the same mail.
6. **Protected files.** The skill never writes `notizen.md` or the body of `firmen/<firma-slug>.md`
   (LS-5.6). It does not store impressions of third parties (LS-9.3).
7. **No double entry.** A mail whose Gmail message ID already appears in `## Verlauf` is not recorded
   again. Two mails of one thread, even on the same day, are two entries.

## MV-8 Approvals

| Action | Approval |
|---|---|
| Create a missing label | Once per Lauf, for the structure (MV-3.1 rule 3) |
| Add or remove a label on a mail, move a mail to the Sammel-Label | None |
| Create a calendar event | Freigabe per event (MV-9) |
| Write a line to `## Verlauf`, change `status`, record a classification | Freigabe per line (MV-7) |
| Take over a proposed rule (MV-4, MV-10) | Freigabe per rule |
| Create a reply proposal | The user asks for it (MV-11) |

Adding and removing labels is reversible. It runs without a question, but the report of the Lauf
(MV-12) lists each change.

## MV-9 Calendar

1. **Calendar.** Events go to the calendar `Bewerbungen`. If it does not exist, the skill reports that
   and creates no event. It does not create the calendar.
2. **When.** The skill proposes an event for an appointment (for example an interview or a call) and for a
   deadline (for example a date for documents or a reply). Follow-up dates derived from the Vorgang
   are not events of this rule.
3. **Complete data only.** If date, time or time zone of an appointment are unclear, the skill does not
   guess. It asks the user or creates no event.
4. **Freigabe.** The user approves each event after seeing title, date, time and the mail it comes from.

## MV-10 Manual changes

1. **Never overwritten.** A mail the user has labelled by hand is not changed by the skill in any later
   Lauf. The user's label wins.
2. **Learning by proposal.** The skill may propose a rule from the correction (MV-4.2). The rule applies
   only after Freigabe (MV-8).

## MV-11 Reply proposals

1. **On request.** The skill writes a reply proposal for a mail only when the user asks for it.
2. **Text in the session.** The proposal is shown as text. The skill creates no Gmail draft and sends
   nothing.
3. **Facts only.** The proposal follows R-1 and R-4 and the communication of `kontaktklassifikation/en.md`
   KK-5. Unknown facts become `[ERGÄNZEN: …]`.
4. **Disclosure.** The proposal respects KK-4, for example no salary before the Auftraggeber is known.

## MV-12 Report and failure

1. **Report.** At the end of a Lauf the skill reports: mails labelled per target label, mails left in the
   Eingang, conflicts, proposed and approved entries, proposed events.
2. **Abort on failure.** If the connector fails or a permission is missing, the skill stops the Lauf and
   reports the error. It starts no workaround and does not continue partly.
3. **Changes stay.** Label changes already made are reversible and stay. The report lists them. Proposals
   not yet approved are dropped.

## MV-13 Data protection

1. **No mail data in the repository.** Examples, tests and fixtures use fictional senders and text
   (Musterfirma GmbH, Beispiel AG). Real mails or people never enter this repository (R-6).
2. **Local only.** The skill sends mail content nowhere except to the connector it reads from. The chat
   shows labels, counts and findings, not the values of sensitive fields (LS-9.4).
3. **Not-relevant mail.** Private mail, bank mail and newsletters are neither analysed nor recorded
   (MV-5.3).
4. **Wurzel.** What is written lies inside the Wurzel only (LS-5.7).

## MV-14 Open points

| Area | Point | Status |
|---|---|---|
| Connector functions | Which Gmail and Calendar functions the available connector offers (in particular changing labels) is not established; the session that wrote this spec lists only a Google Drive connector | open, to be checked before a skill is written |
| Regelwerk storage | File in the Wurzel, interview, or both; a new key in the Anker would change LS-2.5 | open |
| Mailtyp unknown | A relevant mail with a clear Vorgang but no fitting Mailtyp: label at `Bewerbung/<vorgang>` without a Mailtyp is proposed, not confirmed | open |
| Status mapping | The proposed status per Mailtyp (MV-3.2) is a proposal, not confirmed by the user | open |
| Not relevant mail | Staying in the Eingang unchanged (MV-5.3) was assumed, not asked | open |
| Double entry | MV-7.7 (key: Gmail message ID) is an assumed rule | open |
| Quantities | Mails per Lauf and runtime goals were not collected | open |
| Skill | No skill implements this spec; German translation follows via the `spec` skill | open |

## MV-15 Changes in other specs

This spec requires these changes in `lokale-struktur/en.md`, which are made together with it:

- LS-6 rule 4: the skill of `mail-verwaltung` may propose entries for S8 and a change of `status` after the
  user's Freigabe. S7 stays a statement of the user.
- LS-6 rule 1: a *Verlauf* line without a change of status is also allowed for a mail record (MV-7).
- LS-6 rule 7 and the row *Nachverfolgung (S7, S8)* of LS-10: the proposal path of MV-7 is the first
  tracking function; the user's own maintenance remains possible.

## MV-16 Acceptance scenarios

The check is a probe with invented mails. Each mail is fictional and carries no real person.

| ID | Scenario | Expected behaviour |
|---|---|---|
| MV-A | Confirmation of receipt with the reference number of a known Vorgang | Label `Bewerbung/<vorgang>/Eingangsbestätigung`, `unsort` removed, no status change proposed |
| MV-B | Invitation from the company named in a Vorgang, no reference number | Zuordnung by company name, label `Einladung`, proposal of `gespräch`, event proposal with Freigabe |
| MV-C | Newsletter or private mail | Stays in `unsort`, no analysis, not recorded |
| MV-D | Unsolicited recruiter mail without any Vorgang | `Bewerbung/_ohne Vorgang`, no Vault entry, no Vorgang created |
| MV-E | Sender domain of Vorgang A, subject of Vorgang B | `Bewerbung/_ohne Vorgang`, conflict reported |
| MV-F | Reply in a thread whose first mail is assigned, without company name | Zuordnung supported by the thread |
| MV-G | Invitation with a date but without time zone | No event; the skill asks |
| MV-H | Mail the user labelled by hand earlier | Unchanged; a rule proposal on request |
| MV-I | Mail with salary figures and an attachment | Verlauf line without the figures; attachment named only |
| MV-J | Connector refuses a call mid-Lauf | Lauf stops, error reported, no workaround |
| MV-K | Any Lauf | No mail is deleted, archived, sent or drafted, and the system labels (`INBOX` and others) stay as they were |
| MV-L | Offer mail ("we would like to offer you the position") | Label `Angebot`, proposal of `angebot`, not `zusage` |
| MV-M | Rückfrage on a Vorgang that is already at `gespräch` | Verlauf line without a status proposal |
| MV-N | Invitation on a Vorgang at `erfasst` | Verlauf line without a status proposal, note that S7 is missing |
| MV-O | Two mails of one thread on the same day (receipt, invitation) | Two separate Verlauf entries |

The scenarios are verified by reviewing a Lauf on invented mails, not by a script.

## MV-17 Sources

- `project/requirements/mail-verwaltung.md` (requirements R1 to R16 and their open risks)
- `spec/job-application/lokale-struktur/en.md`, `kontaktklassifikation/en.md`, `recherche/en.md`,
  `konventionen/en.md`
