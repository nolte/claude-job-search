# Document type: Motivationsschreiben (EN canonical)

Normative rules for the Motivationsschreiben (motivation letter). It is a document type of its own. It
shares the page layout with the Anschreiben, but it answers a different question and follows different
content rules. This document is canonical for the type.

Related specs:
- `spec/job-application/anschreiben/en.md`: the Anschreiben, and the layout this document reuses.
- `spec/job-application/lebenslauf/en.md`: the document it supports.
- `spec/job-application/konventionen/en.md`: R-1 (facts), R-6 (data protection).
- `spec/job-application/cv-generierung/en.md`: CG-4 (evidence), CG-7 (controlled rewriting).
- `spec/job-application/unternehmensanalyse/en.md`: UA-2, UA-4.5 (company facts and sources).
- `spec/job-application/traumjob-interview/en.md`: WJ-2, WJ-3.3, WJ-7.2 (the Wunschprofil).
- `spec/job-application/kontaktklassifikation/en.md`: KK-4, KK-5.

Rule IDs `MS-n` name the rules of this document. Each rule says whether it comes from a cited source or is
a decision of this plugin.

## MS-1 Purpose and difference to the Anschreiben

1. **Purpose.** The Motivationsschreiben explains why the candidate wants this job, programme, or
   organisation, what the candidate brings, and where the candidate wants to go.
2. **Difference.** The Anschreiben relates to a concrete job and connects the posting with the Lebenslauf. The
   Motivationsschreiben deals with personal reasons, values, and long-term goals, and is often an addition
   for study places, scholarships, or demanding positions. Sources:
   [business-on.de](https://www.business-on.de/unterschied-anschreiben-und-motivationsschreiben.html),
   [karriere.at](https://www.karriere.at/c/a/anschreiben),
   [Kickresume](https://www.kickresume.com/de/blog/motivation-letter-vs-cover-letter/).
3. **Terms are used loosely.** In everyday use "Motivationsschreiben" and "Anschreiben" are often used for the
   same text. This plugin separates them, because the content rules differ (MS-3). The posting's own wording
   decides which type is written (MS-2).

## MS-2 When to write which document

| The posting or programme asks for | Document |
|---|---|
| "Anschreiben", "Bewerbungsschreiben", or names no cover document | Anschreiben |
| "Motivationsschreiben", "Motivationsbrief", "Statement of purpose", or "Begründung Ihrer Motivation" | Motivationsschreiben |
| Both | Both. They do not repeat each other (MS-9) |
| Something unclear | The skill asks the user once; the answer is recorded in the analysis |

1. **Typical uses.** The sources name study places, scholarships, and demanding positions. They give no
   specific rule for internships or training positions. For those, the posting's wording decides.
2. **The institution's own rules.** A university or a funder may prescribe length, structure, language, and
   questions. These rules override this document (MS-11). The skill asks the user for them.
3. **Online forms.** A free-text field on a portal that asks for motivation is not a letter. Its rules are not
   defined here (open point MS-13).

## MS-3 Where the content may come from

A Motivationsschreiben contains two kinds of statements. They follow different rules.

| Kind | Example | Source allowed |
|---|---|---|
| **Fact about the candidate** | A project, a role, a certificate, a result | The Grundlage only (R-1, CG-4) |
| **Statement of motivation** | "I want to work on infrastructure that other teams build on" | The user's own words in the session, or a Wunschprofil entry that the user confirms for this letter |
| **Fact about the counterpart** | The programme's focus, a company's product | The posting or a public statement of the counterpart, with a source in `analyse.md` (UA-4.5) |

1. **Motivation is the candidate's statement.** The skill does not infer it from the Grundlage. A past role
   shows what the candidate did, not what the candidate wants (WJ-2.5).
2. **No invented personal story.** The skill writes no childhood interest, no turning-point anecdote, no
   admiration for a person, and no emotion that the user did not state (R-1).
3. **Wunschprofil.** A wish from a confirmed Wunschprofil may be used only after the user has confirmed the
   sentence for this letter. A wish marked `hypothese: ja` is not used (WJ-3.3).
4. **Missing motivation.** If the user states no reason for a part of the letter, the marker
   `[ERGÄNZEN: Beweggrund]` stays. It is a Blocker for the quality gate (R-1).
5. **Counterpart facts.** A rating-portal statement is not used (UA-2.1). The letter names the programme,
   institution, or company correctly (UA-4, name and Rechtsform as verified).

## MS-4 Components and layout

1. **Components.** Absender, Empfängeranschrift, Ort und Datum, Betreff, Anrede, text, Grußformel,
   Unterschrift, Anlagen. The order and the layout rules of `anschreiben/en.md` AS-2 and AS-3 apply. A source
   names the same formal parts and adds a heading ([medi-karriere](https://medi-karriere.de/bewerbung/professionelles-motivationsschreiben)).
2. **Betreff.** `Motivationsschreiben: <Stelle, Programm oder Stipendium>` with the reference number when one
   exists (decision of this plugin).
3. **Anrede.** A named person is expected. One source calls the generic "Sehr geehrte Damen und Herren"
   unsuitable ([Karrierebibel](https://karrierebibel.de/motivationsschreiben/)); it is a single source. The
   plugin treats the generic salutation as a Warnung and allows it only when the user says that no name is
   available (decision of this plugin).
4. **Grußformel and signature.** As in `anschreiben/en.md` AS-5.3 and AS-5.4.

## MS-5 Structure of the text

The text has five parts. The three-part core (interest, qualification, personal competences) follows
[Karrierebibel](https://karrierebibel.de/motivationsschreiben/). The Einstieg and the Schluss frame it
(decision of this plugin).

| Part | Question it answers | Content |
|---|---|---|
| Einstieg | What is this letter about? | The target and the central reason, in one or two sentences |
| Beweggründe | Why this organisation, programme, or field? | The candidate's reasons (MS-3), tied to facts of the counterpart (UA-4.5) |
| Qualifikation | What does the candidate bring? | Two or three proofs from the Grundlage, each with scope and result when stated (CG-4, CG-8) |
| Persönliche Kompetenzen und Ziele | Where does the candidate want to go, and what supports it? | Goals in the user's words; each competence backed by a proof (MS-6) |
| Schluss | What happens next? | A wish for a conversation; optionally the earliest start date |

1. **Order.** The parts keep this order. Beweggründe come before Qualifikation, because the question of the
   letter is *why*. The Anschreiben leads with proof instead (`anschreiben/en.md` AS-6).
2. **One idea per paragraph.** A paragraph has one idea and at most six lines.
3. **No Lebenslauf in prose.** The text does not retell the career. It selects proofs (AS-1.3).

## MS-6 Evidence rule for personal competences

1. **A competence needs a proof.** A competence such as Teamfähigkeit, Eigeninitiative, or Belastbarkeit is
   written only together with one proof from the Grundlage. Without a proof it is not written (CG-7.2).
2. **Do not upgrade.** Participation does not become ownership, assistance does not become leadership,
   exposure does not become expertise (CG-7.2). A leadership statement needs `fuehrung: ja` in the station
   note (CV-16).
3. **Goals are not facts.** A goal ("I want to lead a platform team in three years") is the user's statement.
   It is written as a goal, never as a claim of a present ability.
4. **No adjectives without proof.** "Leidenschaftlich", "innovativ", "erfolgreich" and similar words are not
   used without a source (CG-8.2).

## MS-7 Length

1. **Default.** One page for a job application, up to two pages for a study place or a scholarship. A
   comparison source gives one to two pages for a Motivationsschreiben
   ([Kickresume](https://www.kickresume.com/de/blog/motivation-letter-vs-cover-letter/)); another says that
   content counts more than length ([news.at](https://www.news.at/wirtschaft/bewerbungsschreiben)). The
   distinction between job and study is a decision of this plugin.
2. **Word count.** About 300 to 600 words for the text part (decision of this plugin). The page limit decides.
3. **Hard limit.** Two pages. A prescribed limit of the institution replaces this limit (MS-11).

## MS-8 Variants

| Variant | When | Difference |
|---|---|---|
| `stelle` | Job application that asks for a Motivationsschreiben | Beweggründe tie to the employer and the role. Length one page |
| `studium` | Study place | Beweggründe tie to the programme and the field. Qualification names education, projects, and relevant experience. Up to two pages. The university's own questions come first |
| `stipendium` | Scholarship | The funder's criteria and questions structure the text. Goals and the planned use of the funding are stated in the user's words. Up to two pages |
| `quereinstieg` | Change of field | The reason for the change is stated in one or two sentences without apology. Transferable proofs carry the Qualifikation. The history is not disguised (CG-3.2) |
| `berufseinstieg` | Entry level | Education, projects, and internships carry the Qualifikation (CG-3.3) |

Internships and training positions use `stelle` or `berufseinstieg`, as the posting's wording requires.

## MS-9 Relation to the Anschreiben and the Lebenslauf

1. **No duplicate.** If both an Anschreiben and a Motivationsschreiben are asked for, the Anschreiben carries
   the proof for the requirements and the Motivationsschreiben carries the reasons and goals. A proof used in
   both is stated with a different focus, and it is not copied.
2. **Same facts.** Every fact equals the Lebenslauf and the Grundlage (R-1, rule 4 of `CLAUDE.md`).
3. **Fit check first.** If a confirmed Wunschprofil exists, the fit check runs before the letter is written. A
   veto stops the plan until the user decides (WJ-7.1). The Motivationsschreiben does not hide a veto.

## MS-10 Wording and tone

1. **Address.** Sie, unless the counterpart uses du.
2. **Voice.** First person, concrete, calm. The letter is personal in its reasons, not in its tone.
3. **Concrete.** A reason names a thing: a topic, a project, a problem. A sentence that fits any employer is cut.
4. **No stock phrases.** The list of `anschreiben/en.md` AS-9.3 applies.
5. **German.** Original wording in another language stays unchanged (R-9, rule 2). A programme that asks for a
   letter in English is an instruction of the counterpart (MS-11); the letter is then written in English, with
   the same rules.

## MS-11 Overrides by the counterpart

A prescribed format, length, language, structure, or list of questions of the counterpart overrides the
defaults of this document. The analysis records the instruction and the quality gate checks it (CG-11.6). A
mandatory instruction that is not met is a Blocker.

## MS-12 Quality checks

| Check | Source rule | Kind | Severity |
|---|---|---|---|
| A motivation statement that the user did not state or confirm | MS-3.1, MS-3.2 | review | Blocker |
| `[ERGÄNZEN: Beweggrund]` left | MS-3.4 | review | Blocker |
| A fact not traceable to the Grundlage | R-1 | review | Blocker |
| A competence without a proof | MS-6.1 | review | Warnung |
| A leadership claim without `fuehrung: ja` | MS-6.2 | review (CV-16 is only run on the Lebenslauf) | Blocker |
| A wish used from a Wunschprofil without the user's confirmation, or a `hypothese: ja` wish | MS-3.3 | review | Blocker |
| Counterpart fact without source, or from a rating portal | MS-3.5 | review | Blocker |
| The text retells the Lebenslauf | MS-5.3 | review | Warnung |
| Longer than the limit of the variant | MS-7 | export page check, as far as the document type is set | Warnung |
| Generic salutation | MS-4.3 | review | Warnung |
| Stock phrase | MS-10.4 | review | Warnung |
| The counterpart's mandatory instruction is not met | MS-11 | review | Blocker |

The export has page limits for `cv`, `letter`, `motivation`, and `email`. The `motivation` limit is two pages; the
stricter one page of the variant `stelle` is checked by hand (MS-13).

## MS-13 Open points

| Area | Point | Status |
|---|---|---|
| Sources | The structure and the length come from ratgeber pages. Study and scholarship rules were not found in the search. The institution's own rules are the authority | open |
| Internship and training | No source for a specific rule. The posting's wording decides | open |
| Online forms | Rules for a motivation text field on a portal (character limit, no letter layout) are not defined | open |
| Export | The `motivation` document type with a two-page limit exists in `export_document.py`. A one-page limit for the variant `stelle` is not enforced and is checked by hand | done, variant limit open |
| Skill | `job-application-motivation-letter-create` writes the document. `job-application-cover-letter-create` no longer lists the word in its triggers and points to the new skill | done |
| WJ-7.2 | `traumjob-interview/en.md` WJ-7.2 forbids wishes in documents. MS-3.3 allows a confirmed wish in this document type only. WJ-7.2 refers here | done in the same change |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |

## MS-14 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| MS-A | The user gives two reasons for the application | Both appear in Beweggründe in the user's words; no third reason is added |
| MS-B | The user gives no reason | `[ERGÄNZEN: Beweggrund]` stays; the quality gate reports a Blocker |
| MS-C | The Wunschprofil holds a matching wish | The skill proposes the sentence; it is written only after the user confirms it |
| MS-D | A competence is claimed without an example | The competence is not written or the skill asks for the proof |
| MS-E | Scholarship with the funder's questions | The funder's questions structure the text; the length follows the funder |
| MS-F | Posting asks for Anschreiben and Motivationsschreiben | Two documents; no copied paragraphs |
| MS-G | Career change | One or two sentences for the reason, transferable proofs, the history unchanged |
| MS-H | The user wants a leadership statement and `fuehrung` is `ungeklärt` | The statement is not written; the skill asks |

## MS-15 Sources

All retrieved 2026-10-22. They are ratgeber and portal pages (secondary sources). They disagree on length and
on the salutation; the plugin's own decisions are marked.

- [business-on.de, Unterschied Anschreiben und Motivationsschreiben](https://www.business-on.de/unterschied-anschreiben-und-motivationsschreiben.html)
- [karriere.at, Anschreiben](https://www.karriere.at/c/a/anschreiben)
- [Kickresume, Motivation letter vs cover letter](https://www.kickresume.com/de/blog/motivation-letter-vs-cover-letter/)
- [Karrierebibel, Motivationsschreiben: Aufbau, Beispiele und Vorlagen](https://karrierebibel.de/motivationsschreiben/)
- [medi-karriere, Professionelles Motivationsschreiben](https://medi-karriere.de/bewerbung/professionelles-motivationsschreiben)
- [news.at, Bewerbungsschreiben](https://www.news.at/wirtschaft/bewerbungsschreiben)
