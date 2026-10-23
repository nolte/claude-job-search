# Counterparts: who you are dealing with

Not every posting comes from the employer. The plugin classifies the counterpart of each
application when it analyses the posting, records the result in `analyse.md`, and adapts what
it writes and what it asks you first. This page explains the types, the questions, and why
the plugin holds back full documents in some cases.

## The types

| Counterpart | Who that is | What they want from you | What to watch |
|---|---|---|---|
| **Employer directly: HR** | Personalabteilung, Recruiting | Complete documents that match the posting, a clean process | Slow process, generic replies |
| **Employer directly: department** | Hiring manager, team lead | Technical depth and evidence of the problems you solved, quickly | Overstating depth |
| **Employer directly: management** | Managing director, owner, often in small firms | Fit with the company's direction, scope, reliability | Unclear role boundaries |
| **Personalberatung / Headhunter** | A recruiter with a mandate from an employer | A profile they can present quickly, your availability, flexibility on terms | Your profile may be presented to several clients; the employer may stay hidden; pressure on salary |
| **Personalvermittlung / Zeitarbeit** | An agency that employs you or places you with a client | Availability, a standard profile, fast placement | The terms (agency or client) differ from what the posting suggests |
| **Referral** | An employee who recommends you | A referral that does not embarrass them | You owe the referrer a clean process |
| **Job platform** | An automated message or a platform recruiter | A quick match, a click | The posting may be stale or duplicated |
| **Unclear** | Anyone who does not fit the rows above | To be found out | Acting on the wrong assumption |

The plugin reads signals in the posting and the message: a hidden employer ("unser Kunde",
"vertraulich"), a sender domain that differs from the employer's, mentions of a fee or of
Arbeitnehmerüberlassung, an automated platform message, a referral by name. Two independent
signals are needed before a type is recorded as likely; with none it records *unklar* and asks
you.

## The questions the plugin asks you

When the counterpart is a recruiter or an agency, the plan step asks you to clarify a few things
before any document is written, and records the answers with the date:

- **Is the employer known?** A recruiter may present your profile to a client. You must know
  which employer each profile goes to. Asking for the Auftraggeber is a normal step, not an
  accusation; a refusal is recorded too and lowers the confidence.
- **Does the recruiter hold an exclusive mandate?** An exclusive mandate blocks a direct
  application to the same employer through another channel.
- **Double submission?** The plugin looks for other applications in your data root to the same
  employer. If you would reach the same employer twice, through a recruiter and directly, it
  tells you before anything goes out.
- **What may be shared?** Contact data (phone, address), salary and notice period go to a
  recruiter only with your consent for that employer, and the recruiter gets the same facts as
  the employer, no more.
- **Who pays whom?** You do not pay a placement fee for an employer's position. If a message
  mentions a fee, the plugin flags it and no document is produced before you have checked the
  terms.

## Why no full documents before disclosure

A complete Lebenslauf and Anschreiben are written for one employer: the stations are selected
for that posting, the letter names the company, and the quality gate checks the set against the
posting. While the employer is unknown, none of this can be done truthfully, and a full CV in a
recruiter's hands may be sent on without your knowledge.

So for a Headhunter or an agency whose client is not yet named, the plugin produces a **short
profile** (Kurzprofil) and your availability, and the e-mail asks the two questions above. The
full set follows once the employer is known and recorded. For an employer who writes to you
directly, nothing is held back.

## What this means for you

- Expect the plan to name the counterpart and, for recruiters, to pause for your answers.
- Keep the recruiter's answers in the application folder (`analyse.md` records them, your own
  notes go to `notizen.md`), so a later direct contact with the same employer does not become a
  double submission.
- The tone and the opening of the letter follow the counterpart: formal with HR and
  management, factual with a department, short on a platform.
- The plugin decides how to communicate once you have decided to apply. It does not decide
  whether you apply.

!!! info "For developers"
    The rules behind this page: `spec/job-application/kontaktklassifikation/en.md` (types and
    motivations, signals and classification, disclosure and confidentiality, communication by
    counterpart) and `spec/job-application/unternehmensanalyse/en.md` (the companies behind an
    application and how they are recorded).
