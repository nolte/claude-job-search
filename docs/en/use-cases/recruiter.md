# Via a recruiter or an agency

**Goal:** answer a Headhunter or an agency without handing your data to an unknown employer, and
without applying twice to the same company.

**Example:** A recruiter writes: *"Unser Kunde, ein führender Softwareanbieter, sucht eine
Teamleitung Entwicklung. Bitte senden Sie uns Ihre vollständigen Unterlagen."* No employer is
named.

## Steps

### 1. Hand the message to the front door

```text
/job-application:job-application-solution
```

Paste the message. The posting analysis reads the signals ("unser Kunde", a sender domain that
differs from any employer, a mention of a fee) and records the counterpart in `analyse.md`.
It records a type as *likely* only with two independent signals; with none it records
*unklar* and asks you. Background: [Counterparts](../counterparts.md).

### 2. Answer the plan-step questions

Before any document, the plan asks:

- Is the employer known? You decide whether to continue without that name.
- Does the recruiter hold an exclusive mandate?
- Have you already applied to this employer? The plugin searches the other folders in your
  data root and warns before a double submission.
- Which contact data, salary and notice period may be shared? Only with your consent for this
  employer.
- Is a fee mentioned? Then no document is produced before you have checked the terms.

The plan shows the counterpart, the confidence and any disclosure still missing, and states
the open point until you decide. After your approval the plan is written to the section `## Plan`
of `vorgang.md`.

### 3. No full set before disclosure

While the employer is unknown, no document goes to the recruiter: stations cannot be selected
truthfully for an unnamed posting, and a full CV may be passed on without your knowledge. What
may go out is a short profile and your availability. The e-mail skill words such a reply for a
Vermittler whose Auftraggeber is not disclosed: it names no employer and asks for the
Auftraggeber and the mandate. The short profile is part of that reply; no separate file is
created for it.

### 4. The employer is named

Add the name to the Vorgang (tell the front door: *"Der Kunde ist Beispiel AG."*). The plugin
checks again for earlier applications to Beispiel AG, then continues like a normal application
([Apply to a posting](posting-application.md)). The Anschreiben uses the variant `vermittler`;
the recruiter receives the same facts as the employer, no more.

If a Handelsregister server is connected, the firm's identity can be checked with your consent
([Handelsregister access](../handelsregister.md)). Without it the item stays `nicht ermittelt`.

## What remains

`analyse.md` with the counterpart classification and its confidence, the approved plan and the
history in `vorgang.md`, and the reply mail as `email.md`. Whether you continue without the
employer's name is your decision; the plan keeps the point open until you decide.

## When the employer writes to you directly

Nothing is held back: the plugin classifies the counterpart (HR, department or management) and
produces the full set.
