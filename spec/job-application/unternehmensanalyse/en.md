# Company analysis for an application (EN canonical)

Normative rules for analysing the company or companies behind one application, and for
recording the result. An application may involve several companies at once: the company that
will employ the candidate, the company where the work happens, a recruiter's firm, and a
group or parent company. Each has a different relation to the application and a different
reliability of information. This specification keeps them apart.

Related rules: `spec/job-application/lokale-struktur/en.md` LS-4 (storage of `firmen/` and
`analyse.md`), LS-6 (Vorgang lifecycle), `spec/job-application/kontaktklassifikation/en.md`
(who the counterpart is), `spec/job-application/konventionen/en.md` R-1 (facts), R-6 (data
protection), `spec/job-application/cv-generierung/en.md` CG-4 (evidence for requirements).

## UA-1 Terms and firm roles

A firm is analysed in one or more **roles**. The role states its relation to the application,
not its legal form. One company may hold several roles, and several companies may hold one role
each.

| Rolle | Meaning | Example |
|---|---|---|
| **Anstellungsgeber** | The legal employer if the candidate is hired. Named in the employment contract. | Arbeitgeber laut Vertrag |
| **Bedarfsträger** | The company where the work is done and whose needs define the job. | Kunde einer Zeitarbeitsfirma, Konzerngesellschaft |
| **Vermittler** | A firm that acts for another firm in this application: recruiter, agency. | Personalberatung |
| **Kontaktgeber** | The company where the contact person works, if different from the roles above. | Headhunter-Firma bei Zielfirma-Ausschreibung |
| **Muttergesellschaft** | A group parent that owns the employer or the Bedarfsträger. Only for context. | Holding |

1. **Zieljob** is the job the candidate applies for. Its employer is the Anstellungsgeber if it
   is named. If it is not named, the Anstellungsgeber is `unbekannt` (UA-4.4).
2. **A firm in more than one role** is analysed once, with each role listed (UA-5).
3. **The Vermittler's own facts** are analysed separately from the Zieljob. A recruiter's
   reputation does not transfer to the Zieljob, and the other way round.

## UA-2 Scope of the analysis

The analysis covers only facts that bear on the application. It does not profile the company.

| Dimension | Question it answers | Typical sources |
|---|---|---|
| **Identität** | Who legally exists, under which name and form, where? | Imprint (Impressum), commercial register extract, the posting |
| **Größe und Lage** | How large is it, and how stable? | Own statements, annual report if published, the posting |
| **Geschäft** | What does it sell or do, for whom? | Own website, press releases, the posting |
| **Standort und Arbeitsform** | Where would the candidate work, remotely or on site? | The posting, own statements |
| **Technik und Arbeitsweise** | Which tools and methods does it use? | Posting, engineering blog, public talks, job description |
| **Bezug zur Bewerbung** | Which role the company plays here (UA-1), and what that means for communication | Posting, contact information, KK-3 classification |
| **Reputation** | How is the company perceived? | Bewertungsportale, press |

1. **Reputation is opinion.** Reviews on rating portals are not facts. They may inform the
   candidate's own decision, but they are never written into a document and never stored as a
   Stammdatum.
2. **No personal profiling.** The analysis uses the contact person named in the posting, and
   only for the role of that person in the application (KK-5). It does not research employees,
   their private profiles or their history.

## UA-3 Sources and their reliability

Every fact records its source and the date it was read. Sources rank in this order:

| Rang | Source | Use |
|---|---|---|
| 1 | Document the user provided (Vertrag, Zeugnis, Schreiben des Unternehmens) | Authoritative for this application |
| 2 | Posting, text as posted | Authoritative for the job's requirements and Bewerbungsweg |
| 3 | Imprint, commercial register extract, company's own statements | Authoritative for identity and public positioning |
| 4 | Press, reports, third-party databases | Context; each claim is marked with its source and date |
| 5 | Rating portals, forums, social media | Opinion only (UA-2.1), never a Stammdatum |

1. **Conflicts.** If two sources disagree on a fact (for example Rechtsform or Sitz), the
   conflict is recorded with both values and their sources. It is not resolved silently. A
   conflict on identity that reaches a generated document is a Blocker in the quality gate,
   following the conflict procedure of `cv-generierung/en.md` CG-2.2.
2. **Search queries.** A web search for a company uses only the company name and a generic term
   such as "Impressum" or "Geschäftsbericht". No candidate data, no Grundlage text and no
   application text is sent in a query (R-6).
3. **Network use** happens only when the user asks for it, as for postings (posting-analysis
   rule on URLs).

## UA-4 Analysis procedure

1. **Roles first.** Identify the roles of UA-1 from the posting and the classification of the
   counterpart (KK-3). Record the roles before any company facts are gathered.
2. **Identity.** Establish each firm's legal name, Rechtsform, and Sitz from rank 1 to 3
   sources (UA-3). A firm without a verifiable identity stays `unbekannt` in those fields.
3. **Dimensions.** Work through UA-2 for each firm and role. Mark a dimension `nicht ermittelt`
   when no source gives it. Do not fill it from memory.
4. **Unknowns.** An unknown Anstellungsgeber is written as `unbekannt`. An unknown fact the
   documents need is marked `[ERGÄNZEN: …]` (R-1). Neither is guessed.
5. **Motivation input.** The Anschreiben's company reference (R-3) may use only facts from the
   posting or from public company statements, each with its source in `analyse.md`. Facts from
   rank 5 sources are never used as a motivation.
6. **Confidence.** Each firm gets an overall confidence: `gesichert` (identity from rank 1 or 3
   and the role confirmed by the counterpart), `wahrscheinlich` (identity from rank 2 or 4),
   or `unklar`.

## UA-5 Where the result is recorded

The analysis is split between two files. Neither copies the other.

| Information | File | Section or key | Written by | Changed by |
|---|---|---|---|---|
| Stable facts of a firm (identity, Sitz, website) | `firmen/<firma-slug>.md`, frontmatter (LS-6.2) | `rechtsform`, `sitz`, `website`, `aktualisiert` | posting-analysis, on first use and after confirmation | the user, and posting-analysis after confirmation |
| Notes about a firm | `firmen/<firma-slug>.md`, body | `## Notizen` | the user | the user only (LS-5.6) |
| The analysis of this application: roles, dimensions, sources, confidence | `analyse.md` of the Vorgang | section `## Unternehmen` | posting-analysis | posting-analysis, when the analysis is re-run |
| Classification of the counterpart | `analyse.md` of the Vorgang | keys of KK-6 | posting-analysis | the same |

### UA-5.1 Section `## Unternehmen` in `analyse.md`

```markdown
## Unternehmen

| Firma | Rolle | Identität | Quelle | Konfidenz | Stand |
|---|---|---|---|---|---|
| Musterfirma GmbH | Anstellungsgeber, Bedarfsträger | Musterfirma GmbH, Berlin | Impressum, Stellenanzeige | gesichert | 2026-10-21 |
| Beispiel Personal GmbH | Vermittler | Beispiel Personal GmbH, Hamburg | E-Mail-Signatur | wahrscheinlich | 2026-10-21 |

### Musterfirma GmbH
- Geschäft: Wartung von Industrieanlagen (Quelle: Website, Stand 2026-10-21)
- Standort/Arbeitsform: Berlin, hybrid (Quelle: Stellenanzeige)
- Technik: Python, Kubernetes (Quelle: Stellenanzeige)
- Größe: nicht ermittelt
- Bezug zur Bewerbung: Zieljob; direkter Kontakt Personalabteilung (KK-2)
```

1. The table has one row per firm and role. The rows give the identity and the confidence, not
   the details.
2. The details under each firm are short. Each line carries its source and date.
3. A re-run replaces the section and records the old `Stand` in `Verlauf` of `vorgang.md`
   (LS-6), so the history of the analysis stays visible.

### UA-5.2 Frontmatter of `firmen/<firma-slug>.md`

The firm file uses the keys of LS-6.2. The following keys are added for the role context:

```yaml
rollen: [Anstellungsgeber, Bedarfsträger]   # roles seen so far, across Vorgänge
identitaet_quelle: Impressum                 # source of the identity fields
identitaet_stand: 2026-10-21
```

1. The `rollen` list is a summary across all Vorgänge. The per-application roles stay in the
   `analyse.md` of each Vorgang, because the same firm can be a Vermittler in one application and
   an Anstellungsgeber in another.
2. A firm file is created once (LS-4) and reused. A second spelling of the same firm is a
   conflict, not a new file (LS-7.7 for slugs).

## UA-6 Consequences for generated documents

1. **Anschreiben** addresses the Anstellungsgeber. If the Anstellungsgeber is `unbekannt`, the
   letter does not name a firm; the quality gate reports a Blocker for a missing employer.
2. **Anschreiben with a recruiter.** The letter names the Anstellungsgeber only when the
   counterpart has disclosed it (KK-4.1). Before disclosure, the letter does not name the
   employer, and the Vermittler's firm is not mentioned as the addressee.
3. **Lebenslauf** does not carry company analysis. It uses the employers of the Grundlage
   (CG-2). The Anstellungsgeber of the Zieljob is not inserted into an employment entry.
4. **E-Mail** is addressed to the counterpart's channel, as KK-5 states.
5. **Motivation text** uses only UA-4.5 sources.

## UA-7 Privacy and retention

1. The analysis is local, in the Wurzel (`job-application/` by default). The Wurzel is git-ignored by
   default; a private, unpublished repository is allowed (R-6, LS-2.1, `lebenslauf-versionen` LV-4).
2. Firm files of companies the candidate no longer applies to stay until the candidate removes
   them. They are not sent anywhere. The retention and deletion of a Vorgang, including its
   `analyse.md`, follow stage S10 of `lokale-struktur/en.md` (LS-6 rule 8); `firmen/` is not
   covered by S10, because a firm file holds no application state.
3. A Vermittler's contact data is recorded only as far as KK-4.3 allows.

## UA-8 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| UA-A | Direct application, one firm | One row, role Anstellungsgeber and Bedarfsträger if the same, identity from Impressum, confidence gesichert |
| UA-B | Headhunter from a different firm, Zieljob at a client | Two rows: Vermittler (the recruiter's employer) and Anstellungsgeber (the client). Each with its own identity and source. Letter does not name the client before disclosure |
| UA-C | Zeitarbeit: agency employs, client is the Bedarfsträger | Anstellungsgeber is the agency (per contract, if known), Bedarfsträger the client. Both recorded. The CV does not show the client as employer |
| UA-D | Parent company in the posting, subsidiary employs | Anstellungsgeber is the subsidiary if named, the parent is Muttergesellschaft, context only |
| UA-E | Two sources disagree on Rechtsform | Both values recorded with sources, conflict flagged, not picked |
| UA-F | Only a rating portal says something bad | Recorded as opinion (rank 5) or not at all; not used in documents |
| UA-G | Anstellungsgeber unknown | `unbekannt` in the row; quality gate Blocker if the letter needs it |

The scenarios are checked by reviewing a generated analysis. A script check of the table and
frontmatter keys is an open point.

## UA-9 Open points

| Area | Point | Status |
|---|---|---|
| Skill integration | `job-application-posting-analysis` writes the `## Unternehmen` section and the firm files; `cover-letter-create`, `email-create`, `solution` and `quality-gate` apply UA-6 | done in the skills; deterministic check open |
| Script check | Validate the UA-5.1 table and UA-5.2 keys deterministically | open |
| Registry access | Whether a commercial-register lookup is used at all; if so, which provider and under which terms | open, decision for the user |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |
