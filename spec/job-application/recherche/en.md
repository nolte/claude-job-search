# Research on employer and recruiter (EN canonical)

Normative rules for the research that precedes and accompanies an application: which information
about a possible employer or recruiter is needed, why, from which source and by which channel it is
obtained, how reliable it is, how it is assessed, and where the result is recorded. The goal is a
sourced, proportionate picture that lets the candidate decide whether to apply, address the right
counterpart safely, and avoid being misled.

This specification is the procedure. It does not repeat the rules it builds on:
`spec/job-application/unternehmensanalyse/en.md` (UA) defines the firm roles, the source ranking, the
dimensions and the record of company facts; `spec/job-application/kontaktklassifikation/en.md` (KK)
defines the counterpart classes, the disclosure rules and the questions to the counterpart. Further
related rules: `spec/job-application/konventionen/en.md` R-1 (facts), R-6 (data protection),
`spec/job-application/traumjob-interview/en.md` WJ-6 (fit check), `spec/job-application/lokale-struktur/en.md`
LS-4 (firm files), LS-6 (lifecycle).

## RC-1 Principles

1. **Proportionate.** The depth of the research follows the stage of the application (RC-2). A
   first look does not need a deep investigation.
2. **Sourced.** Every finding records its source, the channel and the date it was read (UA-3). A
   finding without a source is not a finding.
3. **Reading only.** Research reads. It never sends a message, a connection request or an
   application, and it never logs in on the candidate's behalf anywhere but where the candidate
   has already done so.
4. **The candidate's data stays home.** A query, a search term or a page request carries no
   candidate data, no Grundlage text, no application text and no Wunschprofil content (UA-3.2,
   WJ-8.2, R-6).
5. **Minimal data about people.** Research on a person is limited to the person who contacts the
   candidate or is named in the posting, and to what that person's role in the application needs
   (RC-4 rule 1, UA-2.2). Other employees are not researched.
6. **Signals, not verdicts.** The assessment lists signals and what they might mean (RC-7, RC-8). It
   does not produce a score and does not judge a person. The candidate decides.
7. **Unknown stays unknown.** A fact that no source gives is `nicht ermittelt`. It is not filled
   from memory or by guessing (UA-4.3).
8. **On request.** Network use starts when the user asks for it, or when the plan the user approved
   says so (UA-3.3). A skill does not start a network search on its own.

## RC-2 Research levels

| Level | Name | When | Network | Covers |
|---|---|---|---|---|
| **0** | `Anzeige` | always, first | no | What the posting, the messages and the user's own documents give: signals of KK-3.1, the roles of UA-1, the questions that are open |
| **1** | `Basis` | before the first document goes to a counterpart | yes | Identity, plausibility and current state of the employer (E-1, E-3 to E-5), identity and legitimacy of a recruiter (V-1 to V-3, V-5) |
| **2** | `Vertieft` | on request, or when the status reaches `gespräch` or `angebot` | yes | Everything of level 1, refreshed, plus E-2, E-6 to E-9 and V-4 |

1. Level 0 is part of every posting analysis. Levels 1 and 2 are chosen by the user. The plan of
   `job-application-solution` names the level and what it will read.
2. A research run ends when the items of its level are covered or marked `nicht ermittelt`. It
   does not continue until something is found.
3. **Refresh.** A finding older than 30 days is read again when the status reaches `gespräch` or
   `angebot`. The insolvency check (E-3) is repeated before the candidate signs (`zusage`).

## RC-3 Information about a possible employer

The employer in these rules is the firm in the role Anstellungsgeber, and where it differs the
Bedarfsträger (UA-1). `Level` is the first level that covers the item. `Rank` is the source rank of
UA-3.

| ID | Information | Why it is needed | Where it comes from | Rank | Level |
|---|---|---|---|---|---|
| **E-1** | Legal identity: name, Rechtsform, Sitz, register number, managing directors | Addressee of the Anschreiben; protection against look-alike names and fake firms | Imprint of the website; register extract (RC-5.3) | 3 | 1 |
| **E-2** | Group and ownership: Muttergesellschaft, subsidiaries | Context for size, stability and who the contract partner is | Imprint, register, annual accounts (RC-5.3), own statements | 3, 4 | 2 |
| **E-3** | Stability: size class, annual accounts if published, insolvency notices, reports of closures or mass layoffs | Risk of the position; question for the interview | Unternehmensregister, Bundesanzeiger, official insolvency notices (RC-5.3); press | 3, 4 | 1 |
| **E-4** | Business: what the firm does, for whom, with which products | Fit and motivation (R-3); ability to talk about the firm | Own website, press releases | 3 | 1 |
| **E-5** | State of the position: posting date, repostings, the same posting on the firm's own career page, Ref.-Nr., Bewerbungsweg, deadline, contact | A stale or duplicated posting wastes the application; the career page confirms that the firm itself seeks this person | Posting, career page, `get_job_details`, `get_job_apply_url` (RC-5.4) | 2, 3 | 1 |
| **E-6** | Technology and working method: stack, practices, open-source activity, talks | Fit with the requirements (CG-4); questions for the interview | Posting, engineering blog, public repositories, talks | 2, 3 | 2 |
| **E-7** | Conditions: location and remote rule, salary range if stated, Tarifbindung, Betriebsrat, probation, contract form | Comparison with the Wunschprofil (WJ-6) | Posting, career page, the counterpart on request (RC-5.7) | 2, 3 | 2 |
| **E-8** | Perception: employer ratings, press tone | Questions for the interview, the candidate's own decision. **Opinion only** (UA-2.1) | Rating portals, press | 5 | 2 |
| **E-9** | Contact person's role: name, function, channel as given by the posting | Anrede and channel (KK-5); never a private profile (UA-2.2) | Posting, signature | 2 | 1 |

1. **Identity first.** No other item is researched for a firm until E-1 is established with two
   matching attributes, for example name and Sitz, or name and website domain (RC-6.4).
2. E-8 is read for questions, not for facts. It is not stored in a firm file (UA-2.1). A recurring
   complaint may be kept as a Hinweis in `notizen.md` by the user.

## RC-4 Information about a recruiter

A recruiter is a Vermittler in the sense of UA-1 and KK-1: an agency, a headhunter or a platform
recruiter. The research serves three questions: who is this, does the firm exist and act lawfully,
and for whom does it act.

| ID | Information | Why it is needed | Where it comes from | Level |
|---|---|---|---|---|
| **V-1** | Identity of the sender and of the firm: name, function, firm name, address, e-mail domain, phone | Is the message from whom it claims to be? | Message, signature, the firm's imprint; domain of the e-mail address against the domain of the website | 1 |
| **V-2** | Existence and form of the firm: register entry, Rechtsform, Sitz, age | A firm without a verifiable identity is not a counterpart (UA-4.2) | Imprint, register (RC-5.3) | 1 |
| **V-3** | Mandate and Auftraggeber: for which employer does the firm act, exclusively or not | Disclosure (KK-4.1), exclusivity (KK-4.6), double submission (KK-4.2) | **Ask** (KK-3.3). Cross-check: the same position on the named employer's career page | 1 |
| **V-4** | Standing: since when active, specialisation, size, references, the sender's tenure and role | Whether the recruiter can place the candidate with the named employer | Website, press, the firm's page, and the sender's profile for position, firm and tenure only (RC-5.4) | 2 |
| **V-5** | Warning signs of fraud or unlawful terms | Protection of identity data and money | RC-7.2 | 1 |
| **V-6** | Employment form if the firm lends people: Festanstellung at the client, Arbeitnehmerüberlassung, freelance | The Anstellungsgeber differs from the Bedarfsträger (UA-C) | The counterpart, in writing (KK-5); permit under the Arbeitnehmerüberlassungsgesetz where applicable (RC-5.3, open point) | 1 |

1. **The sender is researched, not the sender's network.** For a person the research reads the
   sender's role, firm and tenure, nothing else: no connections, no private posts, no history
   beyond what the role needs (UA-2.2, RC-1.5).
2. **A recruiter's reputation does not transfer to the employer, nor the other way round**
   (UA-1.3).
3. **What only the counterpart can say** (V-3, V-6, the conditions of E-7) is asked, not guessed
   (RC-5.7).

## RC-5 Channels and how to use them

### RC-5.1 Local material

The posting (`stellenanzeige.md`), the messages and signatures the user provides, contracts and
letters. No network. These are source ranks 1 and 2 and are read first (level 0).

### RC-5.2 The firm's own website

Read the imprint, the career page, the press and blog pages and the privacy notice for
applications, in that order. The imprint is the first source for E-1. The page is fetched by URL;
the URL comes from the posting or from the sender's domain, never from a search ranking alone
(RC-7.2).

### RC-5.3 Official registers and portals

| Portal | Use | Note |
|---|---|---|
| Handelsregister (`handelsregister.de`) | E-1, V-2: register number, Rechtsform, Sitz, managing directors | The user decides whether a lookup is made and whether fees are accepted (UA-9) |
| Unternehmensregister (`unternehmensregister.de`) and Bundesanzeiger (`bundesanzeiger.de`) | E-2, E-3: published annual accounts, notices | Small firms often publish little; `nicht ermittelt` is a legitimate result |
| Official insolvency notices (`insolvenzbekanntmachungen.de`) | E-3: current and recent proceedings | Search by the exact legal name and Sitz, to avoid look-alikes |
| Federal Employment Agency | V-6: permit for Arbeitnehmerüberlassung of an agency that lends people | Whether and how a public lookup is possible is to be verified (RC-13) |

### RC-5.4 LinkedIn through the MCP server

The open-source LinkedIn MCP server (<https://github.com/stickerdaniel/linkedin-mcp-server>) gives
direct, read access to LinkedIn pages through the user's own browser session. **It is the preferred
channel for all LinkedIn content the research needs** (postings, company pages, the contact
person's role). When the server is connected, LinkedIn content is read through it and through no
other route. When it is not connected, the research says so, points to the setup in the docs page
*LinkedIn access*, and the user may paste the text instead; the research then continues with the
other channels. The server stays optional for the plugin as a whole: no skill depends on it.

| Need | Tool | Item |
|---|---|---|
| Posting text, requirements, company details | `get_job_details`, `search_jobs` | E-5 |
| Easy Apply or employer's application page | `get_job_apply_url` | E-5 |
| Company page, size, sector, open jobs | `get_company_profile`, `search_companies` | E-1, E-4, E-5 |
| Company's own posts | `get_company_posts` | E-4 |
| The contact person's role, firm and tenure | `get_person_profile` with the sections needed for this | E-9, V-4 |

1. **Reading tools only.** `send_message`, `connect_with_person` and any other tool that acts in
   the user's name are not part of research (RC-1.3). `get_company_employees`, `search_people`,
   `get_feed` and `search_posts` are not used, because they serve profiling and not one of the
   items above.
2. **Consent.** LinkedIn's User Agreement prohibits automated access, and accounts can be
   restricted. Before the first LinkedIn read of a Vorgang, the skill names this risk and waits for
   the user's yes. A no leaves the other channels.
3. **Budget.** At most 6 page reads per Vorgang at level 1 and at most 15 at level 2. Calls run one
   after the other, never in bulk. The user may lower the numbers.
4. **Visibility.** Reading a profile can be visible to its owner, depending on the settings of
   both accounts. The user is told before a person's profile is read.
5. **Not an authority.** A LinkedIn page is a statement of the firm or of the person. It ranks 4,
   like other social media, and does not replace the imprint or the register (UA-3).
6. **One route.** Web search and direct page fetches are not used to read `linkedin.com` pages: they
   are unreliable there, and they bypass the consent of rule 2, the budget of rule 3 and the
   visibility notice of rule 4. A link to LinkedIn that a search returns is opened through the server
   or not at all.
7. **Availability check.** At the start of a run (RC-6 step 1) the research checks whether the
   server's tools are connected. The result is stated in the record (RC-9, line `Kanäle`).

### RC-5.5 Web search

A search query contains the exact company name, optionally the Sitz, and one generic term from
the following list. It contains nothing else (UA-3.2).

| Purpose | Allowed generic terms |
|---|---|
| Identity | `Impressum`, `Handelsregister`, `Sitz` |
| Stability | `Geschäftsbericht`, `Insolvenz`, `Stellenabbau`, `Pressemitteilung` |
| Business and technology | `Produkte`, `Karriere`, `Engineering Blog`, `GitHub` |
| Perception | `Bewertungen`, `Erfahrungen` |

1. A search finds leads. A lead becomes a finding only when a page of the right rank states it
   and the page is read, not the snippet.
2. **Name collisions.** Several firms can share a name. The result is attached to the firm only
   after RC-6.4.
3. The sender of a message is searched by name and firm only, to find their firm page or profile
   (V-4). Nothing the sender wrote is placed into the query.

### RC-5.6 Press and public statements

Press releases, trade press and public talks give context and technology (E-4, E-6). Each claim
is marked with its source and date (UA-3 rank 4).

### RC-5.7 Questions to the counterpart

Some information can only come from the counterpart. Asking is a normal step (KK-3.3). The research
prepares one short question list instead of several messages:

| Question | Item | When |
|---|---|---|
| For which employer do you act, and exclusively or not? | V-3 | always for a Vermittler |
| Who will be my contract partner, and in which form (Festanstellung or Überlassung)? | V-6 | for Zeitarbeit and Vermittlung |
| What is the salary range and the contract form? | E-7 | when the posting is silent and the Wunschprofil needs it |
| Where does the work happen, and what is the remote rule? | E-7 | when the posting is silent |
| How is the process organised, and by when is a decision expected? | E-5 | after the first contact |

The candidate shares nothing with a Vermittler that the employer would not also receive (KK-4.4).

## RC-6 Procedure

1. **Level and consent.** Fix the level (RC-2). For levels 1 and 2 confirm with the user that the
   network is used and which channels, and check whether the LinkedIn MCP server is connected
   (RC-5.4 rules 2 and 7).
2. **Local first.** Read the posting and the messages. Record the signals of KK-3.1 and the
   open questions.
3. **Roles.** Determine the roles of UA-1 and the Kontaktart (KK-3).
4. **Identity gate.** For each firm, establish E-1 or V-1 and V-2 with two matching attributes from
   different sources. A firm that fails the gate gets the signal `Identität nicht bestätigt`
   (RC-7) and no further research until the candidate decides.
5. **Items of the level.** Work through the items of RC-3 and RC-4 for the level, in the order of
   the tables. Stop at the cap of the level (RC-2.2) and mark the rest `nicht ermittelt`.
6. **Conflicts.** Two sources that disagree are recorded with both values (UA-3.1). They are not
   resolved silently.
7. **Signals.** Compare the findings with RC-7 and record each signal that applies, with its source.
8. **Questions.** Collect what only the counterpart can answer (RC-5.7).
9. **Assessment and record.** Write the assessment (RC-8) and the result (RC-9).

## RC-7 Signals

A signal is an observation, not a verdict. It points at a question to ask or a step to take.

### RC-7.1 Employer

| Signal | Reading | Reaction |
|---|---|---|
| `Identität nicht bestätigt`: no imprint, no register entry, name or Sitz differ between sources | A look-alike or a fake firm is possible | No documents with personal data. Ask for the legal name. Record the conflict (UA-3.1) |
| An insolvency notice for the firm in the last two years | Risk to the position | Mark in the assessment. Ask in the interview. Check again before signing (RC-2.3) |
| Same position reposted for months, or open on a platform but absent from the career page | Stale posting, a search that never ends, or a hidden recruiter | Ask whether the position is open. Check against V-3 |
| Remote or location differs between the posting and the career page | Inaccurate posting | Ask (E-7). Record both values |
| Posting names no employer and no contact | Possibly a Vermittler | Classify the counterpart (KK-3) |
| Application portal asks for far more personal data than the stage needs (for example ID copy) | Early over-collection | Provide only what the process needs (KK-4.3) |
| Consistent complaints on rating portals | Opinion, not fact | A Hinweis for the interview questions; never used in documents (UA-2.1) |

### RC-7.2 Recruiter

| Signal | Reading | Reaction |
|---|---|---|
| Free-mail address, or an e-mail domain that is not the domain of the firm named in the signature | Identity unverified, possible phishing | `Identität nicht bestätigt`. Contact the firm only via the number in its imprint |
| Message arrives in a chat app only, and the firm has no imprint | Possible fraud | Do not reply with documents. Record the signal |
| Request for ID copy, bank details, tax number or social insurance number before an interview | Fraud or over-collection | Do not give them. Real contracts and onboarding come after an offer (KK-4.3) |
| The candidate is to pay a fee or buy something | Contradicts KK-4.5 | Stop. Check the arrangement before any step |
| The Auftraggeber stays hidden after the question (KK-3.3) | Lower confidence (KK-3.3 rule 2); possibly a collection of profiles | No Lebenslauf before the name is known (KK-5) |
| The named employer has no matching position on its career page | The Mandat is unconfirmed | Ask for the Ref.-Nr. or a contact at the employer. Do not contact the employer without the candidate's consent |
| Pressure to answer or to decide on the same day | Pressure on the candidate | Take the time. Record the signal |
| A generic text addressed to many, wrong role or wrong skills | Mass mailing | Treat as a platform contact (KK-2) |
| Zeitarbeit presented as Festanstellung at the client | The Anstellungsgeber differs (UA-C) | Ask for the contract partner in writing (V-6) |

### RC-7.3 Rules for signals

1. A signal needs a source: the message, the page, the notice. A feeling is not a signal.
2. One signal is a question. Two independent signals are a warning (KK-3.2 rule 1 applies by
   analogy).
3. The absence of a signal is not proof that all is well. The assessment says which items were
   covered and which were not.

## RC-8 Assessment

The result per firm (employer and, separately, recruiter, UA-1.3) is one value and its reasons:

| Einschätzung | Meaning | Consequence |
|---|---|---|
| **unauffällig** | The items of the level are covered, no signal of RC-7 applies | Proceed as planned |
| **Rückfragen offen** | At least one signal or one `nicht ermittelt` item that matters for the decision | Ask (RC-5.7); documents with personal data wait for the answer where KK-4 requires it |
| **Warnzeichen** | Two independent signals, or `Identität nicht bestätigt` | No document and no personal data to this counterpart until the candidate decides, with the reasons in front of them |

1. The assessment lists the signals with their sources and the items that were not covered. It
   gives no number and no ranking (WJ-6.3 rule 4).
2. The assessment is about firms and facts. It does not contain opinions about named persons
   (UA-2.2).
3. A Veto of the fit check (WJ-6.3) is independent of the assessment. A firm can be
   `unauffällig` and still violate an Ausschluss.
4. The candidate may decide against the assessment. The decision is recorded in *Verlauf* of
   `vorgang.md` (LS-6).

## RC-9 Recording

The result is part of the analysis of the Vorgang (UA-5). Stable facts go to the firm file, facts of
one application to `analyse.md`.

```markdown
## Recherche

Stufe: 1 (Basis) · Stand: 2026-10-23 · Kanäle: Anzeige, Impressum, Unternehmensregister, LinkedIn (4 Seiten)

| ID | Befund | Quelle | Stand | Status |
|---|---|---|---|---|
| E-1 | Musterfirma GmbH, Berlin, HRB 000000 B | Impressum; Handelsregister | 2026-10-23 | ermittelt |
| E-3 | Kein Insolvenzeintrag, Jahresabschluss 2024 hinterlegt | insolvenzbekanntmachungen.de; Unternehmensregister | 2026-10-23 | ermittelt |
| E-5 | Stelle auch auf der Karriereseite, Ref.-Nr. gleich | Karriereseite | 2026-10-23 | ermittelt |
| V-3 | Auftraggeber nicht genannt | Nachricht vom 2026-10-22 | 2026-10-23 | offen |

Einschätzung (Vermittler): Rückfragen offen. Signal: Auftraggeber nicht genannt (RC-7.2).

### Rückfragen
- Für welchen Arbeitgeber handeln Sie, und exklusiv? (V-3)
```

1. The section `## Recherche` is written by the skill that runs the research (RC-11) into
   `analyse.md`. A re-run replaces the section and adds one line with the old `Stand` to *Verlauf* of
   `vorgang.md` (UA-5.1 rule 3).
2. `Status` is one of `ermittelt`, `nicht ermittelt`, `Konflikt`, `offen`. A conflict lists both
   values.
3. The details of E-1 to E-4 that are stable across postings go to the firm file as in UA-5.2. The
   key `recherche_stand` (date of the last research, `JJJJ-MM-TT`) is added to its frontmatter.
4. The classification keys of KK-6 stay as they are. `kontakt_signale` may reference signal texts
   of RC-7.
5. Pages read are not copied into the Vorgang. The record holds the finding, the source and the
   date, not the page text. A quote is allowed where a document later needs it (UA-4.5).

## RC-10 Data protection

1. **What leaves the machine:** search terms (RC-5.5), URLs requested, and the pages that the
   user's own LinkedIn session reads. Nothing from the Grundlage, the Wunschprofil or the documents.
2. **What is read from the network ends up in the session** and is processed by the model
   provider like any other text of the session. The user is told this once per research run.
3. **Third-party personal data** is limited to the contact person: name, function, firm, tenure
   (RC-1.5). It is stored only in `analyse.md` of the Vorgang and follows its retention (S10).
4. **No covert contact.** Research does not message, follow, connect or visit more than the items
   require (RC-5.4).
5. **Private repository.** If the Wurzel is tracked in a private repository, `## Recherche` is
   tracked with it. A public repository never holds it (R-6, LV-4).

## RC-11 Responsibility in the plugin

| Part | Role |
|---|---|
| `job-application-posting-analysis` | Runs level 0 on every posting. Runs levels 1 and 2 when the user asks. Writes `## Recherche` and the firm file |
| `job-application-solution` | Asks for the level in the plan. Passes the result to the documents |
| `job-application-fit-check` | Uses the findings of E-5 and E-7 against the Wunschprofil. Does not run its own research |
| `job-application-quality-gate` | Reports a missing `## Recherche` for a Vorgang with a Vermittler as a Warnung, and a document that names a firm with `Warnzeichen` or without E-1 as a Blocker |
| `job-application-reviewer` | Reviews whether disclosure, sources and signals were handled (KK-4, UA-6, RC-7) |

This table states the target. The skills do not implement it yet (RC-13).

## RC-12 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| RS-A | Direct posting, employer named, level 1 | E-1 from the imprint, E-3 checked at the official notices, E-5 against the career page. Assessment `unauffällig` if nothing applies |
| RS-B | Headhunter, "für unseren Mandanten" | V-1 to V-3: identity of the firm checked, Auftraggeber asked, no Lebenslauf before the answer. Assessment `Rückfragen offen` |
| RS-C | Zeitarbeit, client named | Anstellungsgeber is the agency, Bedarfsträger the client. V-6 asked in writing. The CV does not show the client as an employer |
| RS-D | Message with free-mail address and a request for an ID copy | Two independent signals. Assessment `Warnzeichen`. No data given |
| RS-E | LinkedIn MCP server not installed, or the user declines | The other channels run. The record states that LinkedIn was not read. Missing items are `nicht ermittelt`. The user may paste the text. No error, and no attempt to read LinkedIn by web search or page fetch |
| RS-J | LinkedIn MCP server connected, posting found on LinkedIn | The posting is read with `get_job_details` after the consent of RC-5.4 rule 2. It is not fetched as a web page |
| RS-F | Two firms with the same name | The identity gate separates them by Sitz or domain. Without two matching attributes, `Identität nicht bestätigt` |
| RS-G | Offer received, research from 40 days ago | Findings older than 30 days are read again. The insolvency check is repeated before signing |
| RS-H | Rating portal shows poor reviews | Recorded only as a Hinweis for interview questions. Not used in any document |
| RS-I | Recruiter's LinkedIn profile is requested | The user is told about the risk and the visibility. Only role, firm and tenure are read |

The scenarios are verified by reviewing a generated research record, not by a script.

## RC-13 Open points

| Area | Point | Status |
|---|---|---|
| Skill integration | The skills of RC-11 do not yet run levels 1 and 2 or write `## Recherche`; today they apply UA and KK only | open (skill) |
| Quality gate | The checks of RC-11 for `## Recherche` are not in `job-application-quality-gate` | open (skill) |
| Script check | Validate the table and the `Status` values of RC-9 deterministically | open |
| Register access | Whether a register lookup is made, by which provider and under which fees | open, decision for the user (UA-9) |
| Permit lookup | How an agency's permit for Arbeitnehmerüberlassung can be checked publicly | open, to be verified |
| Legal references | Rules on fees for candidates, lending of employees and the handling of applicant data are not stated as settled law here | open, to be verified (KK-9) |
| Budgets and periods | The page limits (RC-5.4), the 30 days (RC-2.3) and the two years (RC-7.1) are defaults | open, to be tuned by practice |
| LinkedIn terms | The server's use is the user's risk; the terms can change | open, deliberate |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |
