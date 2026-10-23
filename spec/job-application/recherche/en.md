# Research on employer and recruiter (EN canonical)

Normative rules for the research that precedes and accompanies an application: which information
about a possible employer or recruiter is needed, why, from which source and by which channel it is
obtained, how reliable it is, how it is assessed, and where the result is recorded. The goal is a
sourced, proportionate picture that lets the candidate decide whether to apply, address the right
counterpart safely, and avoid being misled.

**Status:** the skills implement levels 0 to 2, the `## Recherche` record and the quality-gate checks
(RC-11, RC-13). The LinkedIn, register, web-search and job-board channels depend on optional MCP
servers (docs page *LinkedIn access*; the other servers are tracked as feature requests).

**Citation form.** A numbered rule of a section is cited as `RC-n rule m` or `RC-n.m`; a step of the
procedure in RC-6 is cited as `RC-6.n` or `RC-6 step n`. Both forms point to the same item.

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
   application. It has no login of its own and uses no paid access. The only authenticated access
   is the user's own LinkedIn session that the LinkedIn server uses (RC-5.4); a register lookup that
   incurs a fee needs the user's decision first (RC-5.3).
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
| **1** | `Basis` | before the first document goes to a counterpart | yes | Identity, plausibility and current state of the employer (E-1, E-3 to E-5, E-9), identity, legitimacy and employment form of a recruiter (V-1 to V-3, V-5, V-6) |
| **2** | `Vertieft` | on request; offered when the status reaches `gespräch` or `angebot` | yes | Everything of level 1, refreshed, plus E-2, E-6 to E-8 and V-4 |

1. Level 0 is part of every posting analysis. Levels 1 and 2 are chosen by the user. The plan of
   `job-application-solution` names the level and what it will read. The status change only makes
   the skill offer level 2; the run starts after the user's yes (RC-1.8).
2. A research run ends when the items of its level are covered or marked `nicht ermittelt`. It
   does not continue until something is found.
3. **Refresh.** A finding older than 30 days is offered for a new reading when the status reaches
   `gespräch` or `angebot`, and read again after the user's yes. The insolvency check (E-3) is
   offered again before the candidate signs (`zusage`).

## RC-3 Information about a possible employer

The employer in these rules is the firm in the role Anstellungsgeber, and where it differs the
Bedarfsträger (UA-1). `Level` is the first level that covers the item. `Rank` is the source rank of
UA-3.

| ID | Information | Why it is needed | Where it comes from | Rank | Level |
|---|---|---|---|---|---|
| **E-1** | Legal identity: name, Rechtsform, Sitz, register number, managing directors | Addressee of the Anschreiben; protection against look-alike names and fake firms | Imprint of the website (RC-5.2); register extract (RC-5.3) | 3 | 1 |
| **E-2** | Group and ownership: Muttergesellschaft, subsidiaries | Context for size, stability and who the contract partner is | Imprint, register, annual accounts (RC-5.3), own statements | 3, 4 | 2 |
| **E-3** | Stability: size class, annual accounts if published, insolvency notices, reports of closures or mass layoffs | Risk of the position; question for the interview | Unternehmensregister, Bundesanzeiger, official insolvency notices (RC-5.3); press | 3, 4 | 1 |
| **E-4** | Business: what the firm does, for whom, with which products | Fit and motivation (R-3); ability to talk about the firm | Own website, press releases | 3 | 1 |
| **E-5** | State of the position: posting date, repostings, the same posting on the firm's own career page, Ref.-Nr., Bewerbungsweg, deadline, contact | A stale or duplicated posting wastes the application; the career page confirms that the firm itself seeks this person | Posting, career page, `get_job_details`, `get_job_apply_url` (RC-5.4) | 2, 3 | 1 |
| **E-6** | Technology and working method: stack, practices, open-source activity, talks | Fit with the requirements (CG-4); questions for the interview | Posting, engineering blog, public repositories, talks | 2, 3 | 2 |
| **E-7** | Conditions: location and remote rule, salary range if stated, Tarifbindung, Betriebsrat, probation, contract form | Comparison with the Wunschprofil (WJ-6) | Posting, career page, the counterpart on request (RC-5.7) | 2, 3 | 2 |
| **E-8** | Perception: employer ratings, press tone | Questions for the interview, the candidate's own decision. **Opinion only** (UA-2.1) | Rating portals, press | 5 | 2 |
| **E-9** | Contact person's role: name, function, channel as given by the posting | Anrede and channel (KK-5); never a private profile (UA-2.2) | Posting, signature | 2 | 1 |

1. **Identity first.** No other item is researched for a firm until E-1 has passed the identity
   gate (RC-6.4).
2. E-8 is read for questions, not for facts. It is not stored in a firm file (UA-2.1). A recurring
   complaint may be kept as a Hinweis in `notizen.md` by the user.

## RC-4 Information about a recruiter

A recruiter is a Vermittler in the sense of UA-1 and KK-1: an agency, a headhunter or a platform
recruiter. The research serves three questions: who is this, does the firm exist and act lawfully,
and for whom does it act.

| ID | Information | Why it is needed | Where it comes from | Level |
|---|---|---|---|---|
| **V-1** | Identity of the sender and of the firm: name, function, firm name, address, e-mail domain, phone | Is the message from whom it claims to be? | Message, signature, the firm's website and imprint (RC-5.2); domain of the e-mail address against the domain of the website | 1 |
| **V-2** | Existence and form of the firm: register entry, Rechtsform, Sitz, age | A firm without a verifiable identity is not a counterpart (UA-4.2) | Imprint (RC-5.2), register (RC-5.3) | 1 |
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

### RC-5.2 Public sources: web presence and imprint

The public web presence of a firm is the first network source and the cheapest one. It applies to
the employer and the Bedarfsträger, and equally to the website of a recruiter's firm (V-1, V-2, V-4).
The pages are read in the following order, because each one confirms or questions the one before.

| Page | What it gives | Items | What to check |
|---|---|---|---|
| **Imprint** (Impressum) | Legal name, Rechtsform, address, register court and number, authorised representatives, contact, VAT ID if given | E-1, V-1, V-2 | Name and Sitz against the posting, the signature and the register (RC-5.3); a missing or incomplete imprint is a signal (RC-7) |
| **Start page, Über uns** | Business, self-description, group affiliation, size statements | E-2, E-4 | Statements about size and age are the firm's own claims (rank 3), not proof |
| **Career page** | The position with date and Ref.-Nr., process, conditions, benefits | E-5, E-7 | The same position as in the posting; differences in place, form of work or wording are recorded (RC-7.1) |
| **Press, news, blog** | Announcements, projects, technology, changes | E-3, E-4, E-6 | Dates; a page without a date has no value as a current fact |
| **Privacy notice for applicants** | Who is the responsible body, how application data is stored and for how long | E-1, KK-4.3 | The responsible body matches the imprint; no notice at all for a portal that asks for personal data is a signal |
| **Contact, locations** | Addresses, a switchboard number | E-1, E-7 | The number is the one to use for a verification call (RC-7.2) |
| **Recruiter's references and team pages** | Clients, sectors, people, specialisation | V-2, V-4 | Named clients are the firm's own claim; they do not confirm the named employer (V-3) |

1. **The URL comes from a trusted place:** the posting, the domain of the sender's e-mail, the
   register entry, or the user. It never comes from a search ranking alone (RC-7.2).
2. **The page itself is read**, not the search snippet. A fetched page is recorded with its URL and
   the date it was read (RC-9).
3. **Domain consistency.** The domain of the website, of the e-mail address in the signature and
   of the career page named in the posting should match. A mismatch is not a verdict. It is a
   signal that triggers the identity gate (RC-6.4).
4. **The imprint is a statement of the firm** (rank 3, UA-3). It establishes E-1 together with a
   second attribute from another source, for example the register (RC-6.4).
5. **Pages change.** A finding from a public page is dated. It is read again at the stages of
   RC-2.3.
6. **Other public pages** such as an encyclopedia entry or a business directory give context
   only (rank 4) and never replace the imprint or the register. Private social-media pages of
   employees are not read (RC-1.5).
7. **Fetch for known URLs, search for leads.** A page with a known URL is fetched. Web search
   (RC-5.5) only finds the URL when none is known. LinkedIn pages are never fetched this way
   (RC-5.4 rule 6).

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
| Easy Apply or employer's application page (`portal` or `email` for `bewerbungsweg`) | `get_job_apply_url` | E-5 |
| Company page, size, sector, open jobs | `get_company_profile`, `search_companies` | E-4, E-5 (not E-1, see rule 5) |
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
5. **Not an authority.** The text of a posting, as posted, is the posting (rank 2). Any other
   LinkedIn content, such as a company page or a person's profile, is social media and ranks 5 in
   UA-3: a lead and an opinion, never a Stammdatum, never a motivation (UA-4.5), and never the
   source of E-1. Identity comes from the imprint and the register (RC-5.2, RC-5.3).
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
3. **No person search.** A person is not searched for on the web. The sender's role is read from the
   signature, from a team page of the firm that is reached by a known URL (RC-5.2), or through the
   LinkedIn server (RC-5.4). A search query contains no personal name.

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
4. **Identity gate.** For each firm, E-1 (or V-1 and V-2 for a recruiter's firm) must be
   established by two attributes, each confirmed by at least two independent sources. The
   attributes are the legal name plus the Sitz, the register number or the website domain. The
   sources are the imprint, the register, the posting and the signature; one imprint alone is one
   source. The steps that decide the gate (reading the imprint, the register lookup, comparing the
   domains) are part of the gate and always run. A firm that fails the gate gets the result
   `Identität nicht bestätigt` (RC-7, RC-8). No other item of that firm is researched until the
   candidate decides.
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
| Free-mail address, or an e-mail domain that is not the domain of the firm named in the signature | Identity unverified, possible phishing | One signal. Run the identity gate (RC-6.4); only a failed gate gives `Identität nicht bestätigt`. Contact the firm only via the number in its imprint |
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
| **Warnzeichen** | Two independent signals, or a failed identity gate (`Identität nicht bestätigt`, RC-6.4) | No document and no personal data to this counterpart until the candidate decides, with the reasons in front of them |

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
| E-1 | siehe `## Unternehmen` (Identität bestätigt: Name und Sitz in Impressum und Handelsregister) | Impressum; Handelsregister | 2026-10-23 | ermittelt |
| E-3 | Kein Insolvenzeintrag, Jahresabschluss 2024 hinterlegt | insolvenzbekanntmachungen.de; Unternehmensregister | 2026-10-23 | ermittelt |
| E-5 | Stelle auch auf der Karriereseite, Ref.-Nr. gleich | Karriereseite | 2026-10-23 | ermittelt |
| V-3 | Auftraggeber nicht genannt | Nachricht vom 2026-10-22 | 2026-10-23 | offen |

Einschätzung (Vermittler): Rückfragen offen. Signal: Auftraggeber nicht genannt (RC-7.2).

### Rückfragen
- Für welchen Arbeitgeber handeln Sie, und exklusiv? (V-3)
```

1. The section `## Recherche` is written by the skill that runs the research (RC-11) into
   `analyse.md`, next to `## Unternehmen`. A re-run replaces the section; the old `Stand` goes into
   *Verlauf* of `vorgang.md` once per run, together with the re-run of `## Unternehmen`
   (UA-5.1 rule 3), not once per section.
2. **One master for identity.** The values of E-1 (legal name, Rechtsform, Sitz, register number)
   and of the recruiter firm's identity (V-1, V-2) are written only to `## Unternehmen`, the master
   of UA-5.1. `## Recherche` records for these items the status, the sources checked and the date,
   and refers to `## Unternehmen` for the values. A conflict of identity values is recorded in
   `## Unternehmen` with both values (UA-3.1); `## Recherche` shows the status `Konflikt`.
3. `Status` is one of `ermittelt`, `nicht ermittelt`, `Konflikt`, `offen`.
4. The details of E-1 to E-4 that are stable across postings go to the firm file as in UA-5.2. The
   key `recherche_stand` (date of the last research, `JJJJ-MM-TT`) is added to its frontmatter. The
   skill sets it after a run of level 1 or 2, without asking the user; level 0 never sets it.
   `unternehmensanalyse` UA-5 lists the section `## Recherche` and the key in its ownership table.
5. The classification keys of KK-6 stay as they are. `kontakt_signale` may reference signal texts
   of RC-7.
6. Pages read are not copied into the Vorgang. The record holds the finding, the source and the
   date, not the page text. A quote is allowed where a document later needs it (UA-4.5).

## RC-10 Data protection

1. **What leaves the machine:** search terms (RC-5.5), URLs requested, and the pages that the
   user's own LinkedIn session reads. Nothing from the Grundlage, the Wunschprofil or the documents.
2. **What is read from the network ends up in the session** and is processed by the model
   provider like any other text of the session. The user is told this once per research run.
3. **Third-party personal data** is limited to the contact person: name, function, firm, tenure
   (RC-1.5). It is stored only in `analyse.md` of the Vorgang. At any final status, including `zusage`, the
   person data is removed (`lokale-struktur` LS-6 rule 8, LS-9 rule 6).
   `get_person_profile` is called with the narrowest section selection that yields the current
   position. The record keeps only function, firm and tenure; the rest of the returned text is not
   copied to any file. It does enter the session (rule 2), which is why the user is told before the
   call (RC-5.4 rule 4).
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
| `job-application-quality-gate` | Checks `## Recherche` as stated in the rules below |
| `job-application-reviewer` | Reviews whether disclosure, sources and signals were handled (KK-4, UA-6, RC-7) |

Rules for the quality-gate checks:

1. **Missing E-1.** A document that names a firm is a Blocker only if `## Recherche` exists (level 1
   or 2) and E-1 of that firm is not `ermittelt`. Level 0 alone never blocks: the identity gate needs
   sources outside the posting (RC-6.4). For a Vorgang with a Vermittler and no `## Recherche`, the gate
   reports a Warnung.
2. **Warnzeichen.** A document that names a firm with the assessment `Warnzeichen` is a Blocker. It
   becomes a Warnung if the user has decided against the assessment (RC-8 rule 4) and the decision
   stands in `## Verlauf` of `vorgang.md`.
3. The gate reads the record. It runs no research of its own.

## RC-12 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| RS-A | Direct posting, employer named, level 1 | E-1 from the imprint, E-3 checked at the official notices, E-5 against the career page. Assessment `unauffällig` if nothing applies |
| RS-B | Headhunter, "für unseren Mandanten" | V-1 to V-3: identity of the firm checked, Auftraggeber asked, no Lebenslauf before the answer. Assessment `Rückfragen offen` |
| RS-C | Zeitarbeit, client named | Anstellungsgeber is the agency, Bedarfsträger the client. V-6 asked in writing. The CV does not show the client as an employer |
| RS-D | Message with free-mail address and a request for an ID copy | Two independent signals. Assessment `Warnzeichen`. No data given |
| RS-E | LinkedIn MCP server not installed, or the user declines | The other channels run. The record states that LinkedIn was not read. Missing items are `nicht ermittelt`. The user may paste the text. No error, and no attempt to read LinkedIn by web search or page fetch |
| RS-F | Two firms with the same name | The identity gate separates them by Sitz or domain. Without two attributes, each confirmed by two sources, `Identität nicht bestätigt` |
| RS-G | Offer received, research from 40 days ago | The skill offers a new reading of findings older than 30 days and of the insolvency check; the run starts after the user's yes |
| RS-H | Rating portal shows poor reviews | Recorded only as a Hinweis for interview questions. Not used in any document |
| RS-I | Recruiter's LinkedIn profile is requested | The user is told about the risk and the visibility. The tool is called with the narrowest section selection; only function, firm and tenure are recorded, the rest is not copied to any file (RC-10 rule 3) |
| RS-J | LinkedIn MCP server connected, posting found on LinkedIn | The posting is read with `get_job_details` after the consent of RC-5.4 rule 2. It is not fetched as a web page |
| RS-K | Recruiter writes from an e-mail domain that differs from the website named in the signature | One signal. The gate steps run: the imprint of the website is read and compared with the register. If the gate passes, the assessment is `Rückfragen offen`; if it fails, `Warnzeichen`. The candidate does not reply with documents meanwhile (RC-7.2) |
| RS-L | Employer's imprint and the register disagree on the Sitz | Both values are recorded in `## Unternehmen` with their sources and dates (UA-3.1), status `Konflikt`. The gate is not passed until the user decides |

The scenarios are verified by reviewing a generated research record, not by a script.

## RC-13 Open points

| Area | Point | Status |
|---|---|---|
| Skill integration | `job-application-posting-analysis` runs levels 0 to 2 (RC-1 to RC-10) and writes `## Recherche`; `job-application-fit-check` uses E-5 and E-7 (RC-11); `job-application-solution` chooses the level in the plan (RC-2.1) | done |
| Quality gate | The checks of RC-11 for `## Recherche` are in `job-application-quality-gate` | done |
| Script check | Validate the table and the `Status` values of RC-9 deterministically | open |
| Register access | Whether a register lookup is made, by which provider and under which fees | open, decision for the user (UA-9) |
| Permit lookup | How an agency's permit for Arbeitnehmerüberlassung can be checked publicly | open, to be verified |
| Legal references | Rules on fees for candidates, lending of employees and the handling of applicant data are not stated as settled law here | open, to be verified (KK-9) |
| Budgets and periods | The page limits (RC-5.4), the 30 days (RC-2.3) and the two years (RC-7.1) are defaults | open, to be tuned by practice |
| LinkedIn terms | The server's use is the user's risk; the terms can change | open, deliberate |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |
