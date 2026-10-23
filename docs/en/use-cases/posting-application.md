# Apply to a posting

**Goal:** from a concrete Stellenanzeige to a checked application you can send, with the
application recorded in its own folder.

**Example:** Musterfirma GmbH advertises a *Senior Backend Developer* (reference 2026-114). You
apply by e-mail.

## Before you start

- Plugin installed and `job-application/konfiguration.md` in place
  ([Getting started](../getting-started.md)).
- A Datengrundlage and `profil.md`. If they are missing, the front door runs
  `job-application-profile-capture` first.

## Steps

### 1. Start with the posting

```text
/claude-job-search:job-application-solution
```

Paste the posting text (or the link) when asked. The skill checks that the profile is current,
then hands the posting to the analysis.

### 2. Read the analysis

The analysis creates the folder `musterfirma-senior-backend/` and records each requirement with
evidence from your Datengrundlage:

| Requirement | Status | Evidence |
|---|---|---|
| 5+ years Java | erfüllt | Station "Beispiel AG, 2019–2025", bullet 2 |
| Kubernetes in production | teilweise | One project, no operating role |
| Team lead experience | nicht belegt | no entry in the Datengrundlage |

It also notes the tone of the posting (Sie or du), the requested documents and the counterpart
(here: employer directly, department). Gaps are not papered over: *nicht belegt* stays a gap,
and the plan shows how the letter handles it honestly.

### 3. Approve the plan

The plan lists the documents and their format, the stations and bullets that will be used, the
open gaps, and the e-mail as the channel. Answer in plain words:

```text
Ja, aber bitte ohne die Station von 2014 im Lebenslauf. Und mit Kurzprofil.
```

The skill shows the changed plan and waits for your yes. Only then it writes the documents.
The status becomes `geplant`.

### 4. Documents are created in order

Lebenslauf, then Anschreiben (the letter reuses the same stations, dates and numbers), then the
e-mail with subject line, short body, attachment list and ASCII file names. The status becomes
`erstellt`.

### 5. Quality gate

The gate reports blockers, warnings and notes: identical role and reference number in every
document, every claim traceable to the Datengrundlage, spelling, page limits, attachment size,
leftover `[ERGÄNZEN]`. With no blockers the status is `geprüft`. With blockers the owning skill
fixes the document and the gate runs again.

For a second opinion, ask the agent `job-application-reviewer`. It reads the whole set like a
recruiter in the first minute and returns READY or NEEDS-WORK; it changes nothing.

### 6. Export and send

```text
/claude-job-search:job-application-export
```

Pick PDF (the default, also for portals). Then send the mail yourself and record date, channel
and attachments in `vorgang.md`; set the status `versendet` and a `wiedervorlage` date.

### 7. Follow up

After the follow-up date, ask for the mail on request:

```text
Schreib die Nachfass-Mail für Musterfirma.
```

The e-mail skill writes `email-nachfassen.md` from the dates in `vorgang.md`.

## What remains in your data root

```text
musterfirma-senior-backend/
├── vorgang.md          status, plan, history
├── stellenanzeige.md   the posting, verbatim
├── analyse.md          requirement match, counterpart
├── lebenslauf.md
├── anschreiben.md
├── email.md
├── email-nachfassen.md only if you asked for it
├── pruefbericht.md     selection and gate result
├── notizen.md          yours alone
└── export/             PDF, only on request
```

## Variations

- **Portal instead of e-mail:** say so in the plan. No `email.md` is written; the letter gets a
  plain-text copy for the free-text field.
- **The posting asks for a Motivationsschreiben:** the plan adds it, see
  [Initiative application and Motivationsschreiben](initiative-and-motivation.md).
- **ATS portal:** choose the CV format `ats`.
