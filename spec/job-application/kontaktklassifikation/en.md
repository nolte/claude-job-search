# Contact classification and communication (EN canonical)

Normative rules for identifying who the candidate is talking to in an application, and for
adapting the communication to that counterpart. The counterpart is either a **recruiter**
acting for a client, or the **employer** itself. The two differ in what they want, what they
are paid for, and what they may disclose. A message that ignores this difference wastes the
counterpart's time or exposes the candidate.

Related rules: `spec/job-application/konventionen/en.md` R-1 (facts), R-3 (Anschreiben
and Anrede), R-4 (E-Mail), R-6 (data protection). The record of a classification is written to
`analyse.md` (`Kontakt` in Stammdaten, see KK-6). Facts about the posting are in
`spec/job-application/cv-generierung/en.md` CG-4.

## KK-1 Scope and terms

| Term | Meaning |
|---|---|
| **Kontaktart** | The class of the counterpart (KK-2). |
| **Auftraggeber** | The employer on whose behalf a recruiter acts. Unknown until named. |
| **Vermittler** | Any third party that places or advertises a position for an employer. |
| **Mandat** | A recruiting assignment from an employer to a recruiter. |
| **Signal** | An observable fact about a message or posting that supports a classification (KK-3). |

1. The classification is a working hypothesis. It is recorded with its signals and with a
   confidence (KK-3.4), and it is revised when new signals appear.
2. The rules do not decide whether the candidate applies. They decide how to communicate once
   the candidate has decided.

## KK-2 Counterpart types

| Kontaktart | Typical sender | What the counterpart wants | What it is paid for | Main risk for the candidate |
|---|---|---|---|---|
| **Direkt: Personalabteilung** | HR, Recruiting, Personalreferent | Complete documents, a fit with the posting, a clean process | Its own salary; it is not paid per hire | Slow process, generic replies |
| **Direkt: Fachbereich** | Hiring manager, team lead, department | Technical depth, evidence of the problems solved, speed to the core facts | Its own productivity; it needs the hire | Over-claiming technical depth |
| **Direkt: Geschäftsführung** | Managing director, owner (often in small firms) | Strategic and cultural fit, scope, reliability | Its own business success | Unclear role boundaries, informal tone |
| **Personalberatung / Headhunter** | Recruiter with an exclusive or non-exclusive Mandat | A complete, quickly presentable profile; availability; flexibility on terms; a result for the client | A fee from the employer, usually on success | Presented to several clients at once; undisclosed employer; pressure on salary expectations |
| **Personalvermittlung / Zeitarbeit** | Agency that places people as employees of the agency or places them with a client | Availability, a standard profile, fast placement | Margin on placement or on hours worked | Terms of employment differ from the posting (agency vs. client) |
| **Empfehlung (intern)** | An employee who refers the candidate | A positive referral without damage to the referrer | Often a referral bonus | Referrer's reputation at stake; obligations to the referrer |
| **Job-Portal / Plattform** | Automated message or a platform recruiter | A quick match, a click, a profile in the platform | Subscription or fee from the employer | The posting may be stale or duplicated |
| **Unklar** | Anyone who does not fit the rows above | To be found out | — | Acting on the wrong assumption |

1. **Motivation first.** The table states what each counterpart is motivated by. The
   communication answers that motivation (KK-5). It does not invent a motivation for the
   counterpart.
2. **Fee does not change the facts.** A recruiter's fee does not change the candidate's facts
   (R-1). It changes what the recruiter needs to present them.

## KK-3 Classification procedure

### KK-3.1 Signals

| Signal | Points to |
|---|---|
| The posting names the employer, the department, and a contact | Direkt |
| The posting uses "unser Kunde", "für unseren Mandanten", "vertraulich", "diskret", or hides the employer | Personalberatung or Vermittler |
| The sender's domain differs from the employer's domain and the signature names an agency | Vermittler |
| The message mentions a Festanstellung at a client, Arbeitnehmerüberlassung, Einsatz, Stundensatz, or Zeitarbeit | Personalvermittlung / Zeitarbeit |
| The message mentions a Provision, Erfolgshonorar, or a placement fee | Vermittler (the fee must be paid by the employer; see KK-4.5) |
| The message is addressed to the candidate by name and mentions a referral by an employee | Empfehlung (intern) |
| The message is automated and links to a platform | Job-Portal / Plattform |
| The sender signs with the employer's name and role (e.g. "Teamleitung Plattform") | Direkt: Fachbereich or Geschäftsführung |
| The sender signs in HR language ("Bewerbungsprozess", "Personalabteilung") | Direkt: Personalabteilung |

### KK-3.2 Decision rules

1. **Two independent signals** agree before a class is recorded as *wahrscheinlich*.
2. **A fee signal** or an agency signature always puts the counterpart in a Vermittler class,
   even if the posting names the employer.
3. **No signal** records *unklar*. The candidate then asks, and the answer is recorded.

### KK-3.3 Verification

1. The candidate may ask the counterpart directly for the Auftraggeber (the employer name) and
   the Mandat status (exklusiv or nicht). Asking is a normal step, not an accusation.
2. An answer that names the employer is recorded in `analyse.md` with the date. A refusal is
   recorded too, and it lowers the confidence.

### KK-3.4 Record and confidence

Each classification records:
- Kontaktart (one value from KK-2),
- Auftraggeber (name, or `unbekannt`),
- the signals that were found, each with its source (posting, message, signature),
- confidence: `gesichert` (verified by the counterpart), `wahrscheinlich` (two independent
  signals), or `unklar`.

## KK-4 Disclosure and confidentiality

1. **Never send the application to an unknown employer.** A recruiter may send the candidate's
   profile to a client. The candidate must know which employer each profile goes to.
2. **One Vorgang per employer.** If the same candidate is presented to the same employer through
   a recruiter and directly, the candidate is told before any document goes out. The Vorgang
   records both channels (`analyse.md`, Stammdaten `Kontaktart`). This prevents a double
   submission.
3. **Consent before disclosure.** The candidate decides which profile details a recruiter may
   share. Contact data (phone, address) is shared only with the candidate's consent for that
   employer (R-6).
4. **Salary and notice period.** These are shared only when the posting asks for them or the
   candidate has decided to. The recruiter receives the same facts as the employer, no more.
5. **Fee rule.** A candidate does not pay a placement fee to a recruiter for an employer's
   position. Whether any party may charge a fee depends on the arrangement and must be checked
   before the candidate accepts terms (to be verified against current German rules, not stated
   here as settled law).
6. **Recruiter's exclusivity.** Before a document goes to a recruiter, the candidate asks whether
   the recruiter has an exclusive Mandat for that employer. An exclusive Mandat blocks direct
   applications to the same employer through other channels. The answer is recorded.

## KK-5 Communication by counterpart

| Kontaktart | Channel | Opening | Content first | Content to avoid | Follow-up |
|---|---|---|---|---|---|
| Direkt: Personalabteilung | E-Mail, Portal | Sie, formal, Anrede from the posting (R-3) | Documents per posting, Ref.-Nr., availability | Long narrative, claims without proof | After the stated deadline, once |
| Direkt: Fachbereich | E-Mail, direct phone if offered | Sie, factual | Concrete problems solved, technical scope with numbers from the Grundlage | Generic soft skills | Within one week, with a specific question |
| Direkt: Geschäftsführung | E-Mail | Sie, concise | Fit with the company's direction, scope, reliability | Detail on tools | As agreed |
| Personalberatung / Headhunter | E-Mail or phone | Sie unless the recruiter uses du | A short profile, availability, Auftraggeber question (KK-3.3), exclusivity question (KK-4.6) | Full Lebenslauf before the Auftraggeber is known | Ask for feedback after each step |
| Personalvermittlung / Zeitarbeit | E-Mail or phone | Sie | Availability, scope of work, the employment form (Festanstellung or Überlassung) | Agreeing to terms without the written conditions | Confirm terms in writing |
| Empfehlung (intern) | E-Mail, with the referrer informed | Sie, mention of the referral | Facts relevant to the referrer's team | Pressure on the referrer | Thank the referrer after the outcome |
| Job-Portal / Plattform | Platform message | Short | The matching requirements, the Ref.-Nr. | Long text, uncertain match | Only when the posting is current |
| Unklar | As the posting says | Sie | A question to the counterpart (KK-3.3) | Documents before the counterpart is known | After the answer |

1. **Anrede.** Use the contact person's name only when the posting or the candidate's profile
   contains it (R-3). The forms for du-Form, a gender that cannot be derived, and academic titles
   follow `anschreiben/en.md` AS-5. Otherwise "Sehr geehrte Damen und Herren," (Warnung, AS-5.2).
2. **Tone.** Match the counterpart's wording where it is formal or informal, as R-3 requires.
3. **Motivation statement.** Each message answers the motivation in KK-2. A recruiter gets a
   clear availability and a clear profile. A hiring manager gets the problems solved. HR gets a
   complete and consistent set.
4. **Follow-up date.** The column *Follow-up* gives the default per Kontaktart. `job-application-posting-analysis`
   writes it into `wiedervorlage` of `vorgang.md` (LS-6.1) as `versendet_am` plus the period of
   the row: the deadline stated in the posting for `Direkt: Personalabteilung`, seven days for
   `Direkt: Fachbereich`. Where the row gives no period (`As agreed`, `After the answer`), the
   field stays empty and the user sets it. As long as `versendet_am` is empty, `wiedervorlage`
   stays empty; the user fills both at S7. The user may change the date at any time.
5. **Nachfassen is an event, not a status.** A follow-up message is recorded as one line in
   *Verlauf* of `vorgang.md` (LS-6 rule 1). The status stays `versendet` until the counterpart
   answers. A follow-up is sent once per deadline, as the table says.

## KK-6 Metadaten in `analyse.md`

`analyse.md` carries the classification in its Stammdaten:

```yaml
kontaktart: Personalberatung            # one value of KK-2, or: Unklar
auftraggeber: unbekannt                 # name, or unbekannt
kontakt_konfidenz: wahrscheinlich       # gesichert | wahrscheinlich | unklar
kontakt_signale:
  - "Signatur: Personalberatung; Domain abweichend"
  - "Posting: \"für unseren Mandanten\""
exklusiv: unbekannt                     # ja | nein | unbekannt
```

The keys are written by `job-application-posting-analysis`, once the classification is
recorded. Values that are not known stay `unbekannt`, never a guess.

## KK-7 Data protection

1. A recruiter or employer receives only the documents of the Vorgang that the candidate has
   approved for that counterpart.
2. Contact and personal data are shared only as KK-4.3 allows.
3. Notes about the counterpart (`notizen.md`, LS-6.3) are personal to the candidate. Skills do
   not send them anywhere.

## KK-8 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| CK-A | Posting names the employer and HR contact | Kontaktart Direkt: Personalabteilung, confidence gesichert if the employer's domain matches |
| CK-B | "Für unseren Mandanten", no employer named | Kontaktart Personalberatung, Auftraggeber unbekannt, question before documents go out |
| CK-C | Message mentions a Provision | Vermittler class, KK-4.5 applies, no document before the fee rule is checked |
| CK-D | Recruiter and candidate's own application both target one employer | Double-submission warning (KK-4.2), channel recorded |
| CK-E | Message from an employee referring the candidate | Kontaktart Empfehlung (intern), referrer informed, no pressure |
| CK-F | No signal at all | Unklar, the candidate asks, the answer is recorded |
| CK-G | Recruiter asks for salary before the employer is known | No salary given yet (KK-4.4), the Auftraggeber question comes first |

The scenarios are verified by reviewing a generated classification and the message draft, not by
a script. A script can check that the `analyse.md` keys of KK-6 are present and valid; that check
is deferred (see the open points below).

## KK-9 Open points

| Area | Point | Status |
|---|---|---|
| Fee rules | Current German rules on candidate fees and Arbeitnehmerüberlassung are not verified here | open, to be checked before a candidate relies on it |
| Skill integration | `job-application-posting-analysis` writes the KK-6 keys; `cover-letter-create`, `email-create`, `solution` and `quality-gate` apply KK-4, KK-5 and KK-7 | done in the skills; deterministic check open |
| Script check | Validate the KK-6 keys in `analyse.md` (deterministic) | open |
| Nachfass-E-Mail | A text module for the follow-up message as variant `nachfassen` of `job-application-email-create`: Betreff of R-4 with the prefix `Nachfrage:`, reference to `versendet_am`, one question, no new facts | open (skill) |
| `wiedervorlage` default | posting-analysis pre-fills `wiedervorlage` from KK-5.4 once `versendet_am` is set (LS-6.1) | open (skill) |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |
