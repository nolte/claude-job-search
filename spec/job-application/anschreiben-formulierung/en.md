# Wording of the Anschreiben (EN canonical)

Normative rules for how the text of an Anschreiben (cover letter) is worded: the proof sentence, the opening,
the sentence construction, stock phrases, the closing, the delicate cases (reason for leaving, employment gap,
career change), the register, and the handling of machine-drafted text. It adds the wording level to
`spec/job-application/anschreiben/en.md`, which owns purpose, components, layout, structure and length. It does
not repeat rules that other specs own; it refers to them.

Related specs:
- `spec/job-application/anschreiben/en.md`: AS-6 (text structure), AS-9 (wording and tone, the short form of
  this document), AS-10 (salary and start date), AS-12 (quality checks), AS-14 (scenarios).
- `spec/job-application/motivationsschreiben/en.md`: MS-3 (where motivation may come from), MS-10 (wording).
- `spec/job-application/konventionen/en.md`: R-1 (facts), R-2 and R-6 (personal data).
- `spec/job-application/cv-generierung/en.md`: CG-4 (requirement-to-evidence rows), CG-8 (evaluations), CG-9
  (gaps).
- `spec/job-application/unternehmensanalyse/en.md`: UA-4.5 (company facts and their sources).
- `spec/job-application/traumjob-interview/en.md`: WJ-7.2 (no wishes in documents).
- `spec/job-application/qualitaetssicherung/en.md`: the result model and the semantic verdicts of a model.

Rule IDs `AF-n` name the rules of this document. Each rule says whether it comes from a cited source or is a
decision of this plugin. A decision of this plugin is a default that an explicit instruction of the posting
overrides (AS-11).

## AF-1 Scope and relation to the Anschreiben spec

1. **Division of work.** `anschreiben/en.md` decides what the letter contains and where it stands. This document
   decides how a sentence is formed that carries that content. Where both speak to the same point, the rule of
   `anschreiben/en.md` stays the short form and this document is the detail. A conflict is resolved in favour of
   the stricter rule.
2. **Facts come first.** No rule of this document permits a statement that the Grundlage, the analysis, or the
   user's own words in the session do not carry (R-1). Wording rules shape true statements. They never supply
   content, and a wish for a better sentence never justifies a number, a result, or a quality the sources lack.
3. **Language of the rules.** The rules are English. Wording examples and the term lists are German because they
   are matched against German letters.
4. **Motivation letter.** MS-10 applies to the Motivationsschreiben. AF-5 to AF-8 and AF-11 apply to it unchanged;
   AF-3 and AF-4 apply where it states facts about the candidate (MS-3).

## AF-2 Evidence base and its limits

The plugin does not rest its wording rules on one study. The evidence on what makes a letter work is thin, and
this section says so, so that no later rule is read as proven.

| Finding | Source | Weight |
|---|---|---|
| 82.8 % of 1,013 HR professionals read the Anschreiben, 53.3 % read every one; 95.5 % prefer at most one page | Jobseeker survey 2025 | Online survey by a CV-tool vendor; self-reported |
| What HR values: a structured, coherent narrative (83.7 %), own wording (74 %), reference to the employer's values (68.6 %) | same | same |
| What puts HR off: spelling or grammar errors (56.6 %), irrelevant content (55.2 %), missing tailoring (53.9 %), too much text (53.8 %) | same | same |
| Unedited AI text is recognised by missing personalisation (61.1 %), a too smooth style (59.8 %), and stock phrases (57.4 %); 54 % see lower chances for it | same | same |
| A tailored letter drew 53 % more callbacks than no letter; the group sizes and a significance test are not given | ResumeGo field experiment, 7,287 fictitious applications on US job boards, 2019 to 2020 | Commercial, not peer-reviewed, US market |
| After a letter-writing AI tool arrived, the link between the textual match of a letter and callbacks fell by 51 %; time spent revising the AI draft correlates with success | arXiv 2509.25054 | Preprint, one platform, correlational for the revision result |
| Two HR professionals found an unedited ChatGPT letter full of stock phrases and Konjunktiv and would not have invited the applicant | t3n, 2023 | Anecdote, n = 2 |
| Most respondents expected the Anschreiben to disappear by 2026 | Stepstone and BPM, 2021 | A forecast, not a measurement; the 2025 survey above shows the opposite |

1. **What follows.** Three points carry across the sources and drive the rules below: a letter must be specific to
   one employer, a claim needs a proof, and a text that reads as machine-made loses its effect.
2. **No quoted effect sizes in documents or skills.** The figures above are not repeated to the user as facts
   about the plugin's output. They explain the rules.
3. **Open question.** No peer-reviewed study of the German-speaking market that isolates the effect of the
   Anschreiben was found (AF-14).
4. **Where the sources disagree.** The plugin decides and says so:

| Point | Positions | Decision |
|---|---|---|
| First person | Use "Ich" messages (Hays) against not too much "Ich" (TU Darmstadt) | Both: first person, with a limit (AF-5.5) |
| Employment gap | Explain it shortly (karriere.at, onlinemarketing.de) against do not discuss it in the letter (Karrierebibel) | Not in the letter by default; one factual sentence on the user's request (AF-9.2) |
| Salary placement | Closing part (Karrierebibel) or a PS (Karrierebibel) | Closing part, no PS (AF-8.5) |
| Humour, storytelling, a quotation or PS as eye-catcher | Allowed where the employer fits (Uni Saarland, Hays, TU Darmstadt) | Not by default; they need a fact the user supplies (AF-10.2, AF-10.3) |

## AF-3 The proof sentence

The core of the letter is a proof paragraph (AS-6.2). Its wording follows four moves (Karrierebibel). The moves
describe the content of the paragraph; they do not need four separate sentences.

| Move | Content | Where it comes from |
|---|---|---|
| Anforderung | What the posting asks for, in the posting's own term | `analyse.md` requirement row (CG-4) |
| Kompetenz | The ability or experience that answers it | Grundlage entry named in the `Nachweis` cell |
| Beleg | Where and in which scope it was used, and the result when the Grundlage states one | Grundlage entry (R-1) |
| Mehrwert | Why this matters for the task of this job | The posting's task, stated by the writer |

1. **Order.** The paragraph opens with the requirement or with the proof, never with a quality of the candidate.
   Two to four sentences. A paragraph that opens with "Ich bin ..." followed by an adjective is rewritten.
2. **Beleg.** Scope and result come from the Grundlage in its wording: employer, role, period, number of people,
   volume, technology. A result that the Grundlage does not state is not written, and no figure is estimated
   or rounded up (R-1, CG-4).
3. **Mehrwert.** The Mehrwert sentence states fit, not a promise. Allowed: "Diese Erfahrung setze ich bei Ihnen
   für die Einführung des neuen Systems ein." Not allowed: a forecast of a result ("Ich werde Ihre Kosten um
   zehn Prozent senken"), an invented goal of the employer, or a number that the Grundlage lacks. The task named
   in the Mehrwert comes from the posting or from a sourced company statement (UA-4.5).
4. **STAR as an aid.** The interview technique Situation, Task, Action, Result may be used as a check that a
   proof has all four parts. In a letter Situation and Task shrink to one clause. A missing Result is not
   replaced by an invented one; the paragraph then leads with the scope. The sources describe STAR for
   interview answers; the adaptation to a written letter is a decision of this plugin.
5. **One proof, one paragraph.** A paragraph does not combine two requirements. A requirement that has no proof
   is not padded with a quality word; AS-6.3 and AS-6.7 apply.
6. **Quantity needs a basis.** A figure ("22 Prozent kürzere Bearbeitungszeit") is written only when it stands in
   the Grundlage, with the same number and unit as there (CG-4, CV-05).

## AF-4 Einstieg (opening)

1. **Purpose.** The first sentence makes the reader read on: it says something relevant about this job. The
   phrase "hiermit bewerbe ich mich" wastes the place (Hays, Karrierebibel, Uni Saarland; AS-6.1).
2. **Allowed types.** One of four, chosen by what the Grundlage and the analysis carry (Karrierebibel):
   - *Passender Beleg:* the strongest proof for the strongest *Muss* requirement, as a fact from the
     Grundlage.
   - *Besondere Qualifikation:* a qualification the posting asks for, as a fact from the Grundlage.
   - *Bezug zum Unternehmen:* a fact about the employer from the posting or a public statement, with a source
     in `analyse.md` (UA-4.5), linked to why it matters for this application.
   - *Früherer Kontakt:* a call, a fair, or a referral, only when the user states it and the analysis records
     it (KK-5, UA-6).
3. **No empty praise.** "Ihr Unternehmen steht für Qualität und Kundenorientierung" is a sentence that fits every
   employer. A statement about the employer is used only when it is a sourced fact (AF-7).
4. **First word.** The first sentence does not begin with "Ich" and does not only name the channel ("Auf Ihre
   Anzeige bei ... bewerbe ich mich"). The channel may appear as part of a longer sentence when the posting
   asks for it.
5. **Length.** One to two sentences, the first of at most 25 words (decision of this plugin).
6. **No biography.** An anecdote from childhood or a quotation as an opening is not written (AF-10.3).
7. **Initiativ.** The opening names the target area and the reason for choosing this employer, from a sourced
   fact (AS-8). Without a sourced fact the marker `[ERGÄNZEN: konkreter Bezug zum Unternehmen]` stays (AS-6.6).

## AF-5 Sentence construction

The rules rest on the Hamburger Verständlichkeitskonzept (Einfachheit, Gliederung-Ordnung, Kürze-Prägnanz,
anregende Zusätze), in which simplicity weighs most, and on the sources of the letter genre. The numeric limits
are decisions of this plugin because no source gives one for a letter.

1. **Verbal style.** Use verbs for actions, not nouns made from verbs: "Ich habe die Abrechnung umgestellt"
   instead of "Die Umstellung der Abrechnung erfolgte durch mich". Avoid noun chains of three or more nouns
   (TU Darmstadt, Hays).
2. **Active voice.** The candidate's own actions are active. Passive is used only when the agent is unknown or
   unimportant.
3. **No Konjunktiv for own statements.** Statements about the candidate's ability, wish, or the closing are in
   the Indikativ: "Ich freue mich auf das Gespräch", not "Ich würde mich freuen". The forms `würde`, `könnte`,
   `hätte`, `wäre`, `dürfte` count as Konjunktiv markers; `möchte` does not, because it is the common form of
   a statement of intent. Konjunktiv is allowed in indirect speech and in a conditional that the posting
   itself sets up. Konjunktiv reads as doubt (TU Darmstadt, Robert Half, Karrierebibel, Hays; t3n).
4. **Sentence length.** The average is at most 20 words and no sentence exceeds 30 words. A sentence has one
   main clause and at most one subordinate clause level; a nested sentence is split. A figure or a name is not
   split from the verb it belongs to.
5. **"Ich" count.** At most one in three sentences begins with "Ich", and never more than two in a row. Vary
   the subject: the task, the project, the result (AS-9.2).
6. **Positive wording.** State what the candidate has, not what is missing. Negations about oneself ("leider
   noch keine Erfahrung mit ...") and criticism of a former employer are not written (TU Darmstadt, Hays).
   A gap sentence under AS-6.7 is worded as related evidence and willingness to learn.
7. **Words.** Concrete verbs and nouns of the job. No filler words that carry no meaning ("eigentlich",
   "durchaus", "gewissermaßen", "sehr", "ziemlich"), no doubled intensifiers, no exclamation marks, no
   emoticons, no abbreviations outside the posting's own terms. An English term is used where the posting
   uses it or where the field has no German term; the same term is used throughout.
8. **Paragraphs.** One idea per paragraph. The first sentence of a paragraph names the idea (Gliederung-Ordnung).
9. **Numbers and dates.** As in the Grundlage and the Lebenslauf (AS-6.5). A number in a sentence is not
   repeated in the next sentence in another form.

## AF-6 Stock phrases and empty attributes

1. **Stock phrases** are formulas that a reader has read many times and that carry no information about this
   candidate or this job. The lists below are the check basis (AF-12). Each list entry is a stem; inflected and
   punctuation variants match.

   | Class | Examples (German, as written) | Source |
   |---|---|---|
   | Opening formula | `hiermit bewerbe ich mich`, `mit großem Interesse habe ich ... gelesen`, `auf der Suche nach einer neuen Herausforderung`, `durch Zufall bin ich auf ... gestoßen` | `hiermit bewerbe ich mich`: Hays, Uni Saarland, Karrierebibel; the others are decisions |
   | Empty attribute | `teamfähig`, `belastbar`, `hochmotiviert`, `motiviert und engagiert`, `flexibel`, `diszipliniert`, `kommunikativ`, `dynamisch`, `zielorientiert`, `eigenverantwortlich` | `teamfähig`, `belastbar`, `hochmotiviert`, `motiviert`, `diszipliniert`: Uni Saarland, Hays; the others are decisions |
   | Empty claim | `ich bin überzeugt, dass ich die richtige Wahl bin`, `ich bringe alle Voraussetzungen mit`, `ich bin der ideale Kandidat` | decision |
   | Weak closing | `über eine Einladung würde ich mich freuen`, `ich würde mich über eine positive Rückmeldung freuen`, `wann darf ich Sie überzeugen`, `sind Sie neugierig geworden` | Robert Half (all four); Hays for the Konjunktiv form |
   | Padding | `wie Sie meinem Lebenslauf entnehmen können`, `in meiner derzeitigen Position`, followed by a list | decision |

2. **Empty attributes need a behaviour.** An attribute from the list is replaced by what the candidate does,
   as far as a Grundlage entry shows it. "Teamfähig" becomes "Ich habe ein Team von fünf Personen geleitet" only
   when the Grundlage states the team (TU Darmstadt, Hays; R-1, CG-8.2). Where the Grundlage shows no behaviour,
   the attribute is dropped, not kept and not turned into an invented example.
3. **Attributes the posting uses.** A word that the posting itself uses is not forbidden. It stands in the
   same paragraph as its proof, or it is dropped (AS-9.4, AS-9.5).
4. **Closing exception.** `ich freue mich auf Ihre Rückmeldung` and `ich freue mich auf ein persönliches
   Kennenlernen` are not stock phrases of AS-9.3 when they follow a closing sentence with content (AF-8.1). Robert
   Half names them as good closings.

## AF-7 Specificity: the exchange test

1. **Exchange test.** A sentence that stays true and meaningful when the employer's name and the job are replaced
   by those of another posting is generic. A generic sentence is rewritten with a posting term or a sourced
   company fact, or it is cut. The sources name missing tailoring as a main reason for rejection (Jobseeker,
   TU Darmstadt, Karrierebibel).
2. **Two anchors per paragraph.** A proof paragraph holds at least one element of the posting (a task, a term, a
   product, a tool) and at least one element of the Grundlage (a station, a project, a number).
3. **Employer facts.** A sentence about the employer states a fact with a source in `analyse.md` (UA-4.5), not
   an opinion about its quality. Rating-portal statements are not used (UA-2.1).
4. **No mass wording.** Sentences are not copied from another Vorgang's letter. A reused sentence is checked for
   employer, role and figure before it stays (R-7 consistency; one Vorgang per Stellenanzeige, AS-1.5).
5. **Keywords.** A term of the posting is written in the posting's own spelling where the Grundlage supports it.
   A term without support is not written. A term repeated only to match the posting is padding (R-1.4, CG-4.6,
   AF-12).

## AF-8 Schluss (closing)

1. **Content.** The closing has one sentence with content and one sentence for the conversation. The content
   sentence names what the candidate will discuss or offer (for example the first topic of the job, or the
   availability), so that the closing is not the only formula of the letter (AS-9.3).
2. **Wish for a conversation.** Direct, in the Indikativ, short: "Ich freue mich auf das Gespräch" or "Gern
   erläutere ich Ihnen im persönlichen Gespräch, wie ...". A video call may be offered (Robert Half).
3. **Length.** At most two sentences, together at most two lines (Robert Half). The salary and start-date
   sentence of AS-10 stands before them and is not counted.
4. **Tone.** Confident and polite, on equal terms; not pleading, not pushing. No rhetorical question, no
   challenge ("Laden Sie mich ein!"), no demand for a decision (Robert Half).
5. **Salary and start date.** Placement and form follow AS-10. This document adds: the sentence is in the
   Indikativ; it is not the last sentence of the letter; it is not moved to a PS, because a PS is not a
   component of AS-2 and the portal reduction (AS-8.1) would drop it; "ab sofort" is not used as a date, a date
   or a notice period in the user's words is (Karrierebibel).
6. **Confidentiality.** A request to treat the application as confidential is written only when the user asks
   for it.

## AF-9 Delicate cases

1. **Reason for leaving.** The letter does not state why the candidate leaves the current or last employer
   (Hays). It states what the candidate wants to work on, from the user's words and the posting (MS-3).
   Criticism of an employer is not written (AF-5.6).
2. **Employment gap.** The Lebenslauf shows the period (CG-9). The letter does not explain it by default
   (Karrierebibel). When the user wants a sentence, it is one factual sentence from the user's words: what the
   time was ("Weiterbildung zu ...", "Elternzeit", "Arbeitssuche"), without apology and without justification;
   "arbeitssuchend" or "Bewerbungsphase" is preferred to "arbeitslos" (Karrierebibel, onlinemarketing.de). A
   link to the new position is only made where it exists in the Grundlage. The skill asks once, and the user
   decides.
3. **No health data.** Illness, disability, pregnancy and similar data are special categories of personal
   data and are not named in the letter, not even to explain a gap (R-2, R-6; Art. 9 GDPR).
4. **Career change.** The letter leads with two to three transferable competences, each with one proof from
   the Grundlage (karriere.at, Karrierebibel; AS-8). One sentence gives the reason for the change from the
   user's words, positive and without apology. The word "Quereinsteiger" is not used in any document of the
   set, because it puts the missing qualification in front (Karrierebibel; decision of this plugin). A claim of
   fit with the employer's culture needs a sourced company fact (UA-4.5); it does not replace a missing proof.
5. **Entry level.** The proofs lead with education, projects, internships, and practical work from the Grundlage
   (AS-8). The sentence "Leider habe ich noch keine Berufserfahrung" is not written (AF-5.6).
6. **Employer's name for a recruiter.** A letter to a Vermittler names no Auftraggeber that has not been
   disclosed (AS-5.5, KK-4).

## AF-10 Register and personality

1. **Register follows the posting.** Three registers, taken from the tone recorded in `analyse.md`: *formell*
   (Sie, full sentences, no colloquialisms), *sachlich-modern* (Sie, shorter sentences, plain words, no stiff
   formulas), *du* (the posting uses du; the salutation follows AS-5.6). The register is the same in the
   Anrede, the text, and the Grußformel.
2. **Personality through content.** The sources ask for individuality and "Ecken und Kanten" (Uni Saarland). The
   plugin gets individuality from the choice of proofs, from the posting's terms and from concrete wording, not
   from anecdotes or humour. Humour, irony, wordplay and idioms are written only when the user supplies them
   and the register is *sachlich-modern* or *du* (decision of this plugin).
3. **No invented biography.** A story ("Schon als Kind habe ich ...") is a fact about the candidate and needs
   the user's statement and a Grundlage entry (R-1). A quotation or a PS used as an eye-catcher is not written
   by default (decision of this plugin; the TU Darmstadt guide names both).
4. **Consistency with the set.** Terms, spellings and job titles are the same as in the Lebenslauf and the
   E-Mail (R-7).
5. **No wishes.** WJ-7.2 and AS-6.8 apply.

## AF-11 Machine-drafted text

This plugin drafts letters with a language model, so the failure modes of unedited machine text are the main
risk to the wording. The sources show that HR recognises such text by missing personalisation, a too smooth
style, and stock phrases (AF-2).

1. **Draft, not result.** A generated letter is a draft for the user. The skill says which sentences are the
   least tied to the Grundlage and the posting, and asks the user to adjust them in their own words. The
   arXiv preprint finds that time spent revising a draft correlates with success; that is correlational and is
   not used as a promise.
2. **Patterns to avoid.** Series of three adjectives or abstract nouns ("innovativ, dynamisch und
   zukunftsorientiert"), stacked superlatives, abstract openers ("Im Zuge der fortschreitenden Digitalisierung"),
   sentences that begin with a participle phrase of praise, and parallel sentence rhythm over a whole
   paragraph. These patterns are decisions of this plugin from the observed behaviour of generated text; no
   source lists them.
3. **Translationese.** Sentences that read as translated from English ("Ich bin ein engagierter Profi mit
   Leidenschaft für ...") are rewritten in idiomatic German (t3n).
4. **No detection claims.** The plugin does not claim that a letter passes or fails an AI detector. No source
   shows reliable detection. The aim is a specific, true, edited text.
5. **Instruction of the posting.** A posting or a portal that forbids or restricts AI help is an instruction
   under AS-11. The analysis records it, and the skill tells the user before the letter is drafted.

## AF-12 Quality checks

The checks extend AS-12. All of them concern wording, so they are `Warnung` or `Hinweis`. A wording check is
never a Blocker; only a fact check is (R-1, AS-12). Today they are review items. The term lists of AF-6 and the
limits of AF-5 are written so that a deterministic script can take over the first rows (AF-14).

| Check | Rule | Kind | Severity |
|---|---|---|---|
| Stock phrase from AF-6 class opening formula, claim, weak closing, padding | AF-6.1 | automatable by term list; today review | Warnung |
| Empty attribute without behaviour in the same paragraph | AF-6.2, AF-6.3 | review | Warnung |
| Konjunktiv marker (`würde`, `könnte`, `hätte`, `wäre`, `dürfte`) in a statement of the candidate or in the closing | AF-5.3 | automatable by term list; today review | Warnung |
| Letter opens with "Ich", or the opening only names the channel | AF-4.4 | automatable; today review | Hinweis |
| First sentence longer than 25 words | AF-4.5 | automatable | Hinweis |
| Average sentence longer than 20 words, or a sentence over 30 words | AF-5.4 | automatable | Hinweis |
| More than one in three sentences begins with "Ich", or three in a row | AF-5.5 | automatable | Hinweis |
| Negative self-description or criticism of an employer | AF-5.6 | review | Warnung |
| Filler word, exclamation mark, emoticon | AF-5.7 | automatable for marks and a short word list | Hinweis |
| Exchange test fails for a paragraph | AF-7.1 | review (semantic verdict of a model, QS) | Warnung |
| A proof paragraph without a posting element or without a Grundlage element | AF-7.2 | review | Warnung |
| Mehrwert sentence promises a result or a number not in the Grundlage | AF-3.3 | review | Blocker (fact, R-1) |
| A figure or result that the Grundlage does not state | AF-3.2, AF-3.6 | numbers automated (BR-02, CG-13.6); the rest review | Blocker |
| Closing longer than two sentences, rhetorical question, or demand | AF-8.3, AF-8.4 | review | Hinweis |
| Salary sentence as the last sentence, in a PS, or with "ab sofort" as a date | AF-8.5 | review | Hinweis |
| Reason for leaving stated | AF-9.1 | review | Warnung |
| Health data in the letter | AF-9.3 | review | Blocker (R-6) |
| The word "Quereinsteiger" in a document of the set | AF-9.4 | automatable | Warnung |
| Machine pattern or translationese | AF-11.2, AF-11.3 | review | Hinweis |
| Anecdote, quotation, or humour without the user's statement | AF-10.2, AF-10.3 | review | Warnung |

The semantic checks (exchange test, machine pattern) are verdicts of a model. They follow the rules for such
verdicts in `qualitaetssicherung/en.md` and are never set to PASS without a reason that can be checked.

## AF-13 Examples (fictional)

The examples show the wording rules. Names and facts are fictional. In a real letter every fact comes from the
Grundlage or the analysis (R-1).

| Case | Weak | Better | Rule |
|---|---|---|---|
| Opening | `Hiermit bewerbe ich mich auf die ausgeschriebene Stelle als Teamleiterin Service bei Ihrem Unternehmen.` | `Die Musterfirma GmbH baut ihr Servicegeschäft in Süddeutschland aus. Für diese Aufgabe bringe ich Erfahrung in der Leitung eines Serviceteams mit 12 Personen mit.` | AF-4 |
| Empty attribute | `Ich bin teamfähig, belastbar und kommunikativ.` | `Bei der Beispiel AG habe ich die wöchentliche Abstimmung zwischen Entwicklung, Vertrieb und Support geleitet.` | AF-6.2 |
| Proof with Mehrwert | `Ich habe viel Erfahrung mit Prozessen.` | `Sie suchen jemanden, der den Service in drei Standorten vereinheitlicht. Bei der Beispiel AG habe ich 2019 die Serviceprozesse von zwei Standorten zusammengeführt. Diese Erfahrung setze ich bei Ihnen für den dritten Standort ein.` | AF-3 |
| Konjunktiv | `Ich würde gerne meine Erfahrung bei Ihnen einbringen.` | `Ich bringe meine Erfahrung bei Ihnen ein.` | AF-5.3 |
| Gap sentence | `Leider habe ich noch keine Erfahrung mit dem System Beispiel-ERP.` | `Das System Beispiel-ERP kenne ich bisher nicht; die Prozesse, die es abbildet, kenne ich aus [System der Grundlage], und ich arbeite mich zügig ein.` | AF-5.6, AS-6.7, user decides |
| Closing | `Über die Einladung zu einem Vorstellungsgespräch würde ich mich sehr freuen.` | `Gern erläutere ich Ihnen im Gespräch, wie ich die drei Standorte angleiche, auch per Video. Ich freue mich auf Ihre Rückmeldung.` | AF-8 |
| Salary | `Meine Gehaltsvorstellung würde bei 65.000 Euro liegen, ab sofort.` | `Meine Gehaltsvorstellung liegt bei 65.000 € brutto pro Jahr; ich bin ab dem 01.04. verfügbar.` | AF-8.5, AS-10.1 |

## AF-14 Open points

| Area | Point | Status |
|---|---|---|
| Evidence | No peer-reviewed study of the German-speaking market that isolates the Anschreiben was found. The figures of AF-2 come from vendors, one commercial experiment and a preprint | open |
| Hamburger Verständlichkeitskonzept | Read through secondary sources. The criteria and the limits of AF-5.4 are not checked against the original book (Langer, Schulz von Thun, Tausch) | open |
| Limits of AF-5 | The values 20 and 30 words, one in three "Ich" and 25 words for the opening are decisions. They are to be checked against real letters of the user and adjusted | open |
| Automation | The rows of AF-12 marked automatable are to move to `scripts/qualitaet.py` (term lists AF-6, Konjunktiv markers, sentence statistics, "Ich" ratio, "Quereinsteiger"). The term lists should then be data files, not code | open |
| German phrase list | The lists of AF-6 are short. A corpus of letters would give a better list; none is licensed for this repository | open |
| Employment gap | Sources disagree (AF-2.4). The default of AF-9.2 may be changed by user decision per Vorgang | open |
| Writing sample | Whether the user can name an earlier own letter as a sample of their register, and how to keep company facts out of it, is not decided | open |
| Whether to write a letter | Some employers drop the Anschreiben; the 2025 survey says HR mostly reads it. A rule for "no letter asked" belongs to the workflow, not here | open |
| Skill | `job-application-cover-letter-create` and `job-application-motivation-letter-create` cite AF and apply AF-3 to AF-11 | done (skill) |
| AS-9 | AS-9.3 names "ich freue mich über eine Einladung" as a stock phrase when it is the only closing; AF-6.4 and AF-8 refine this. AS-9 is to point here | done in the same change |
| German translation | This spec is English canonical; the German version follows via the `spec` skill | open |

## AF-15 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| AF-A | The draft opens with "Hiermit bewerbe ich mich" | Rewritten with one of the four types of AF-4.2; the check reports a Warnung before the rewrite |
| AF-B | A paragraph says "teamfähig" and the Grundlage shows no team | The attribute is dropped; no example is invented (AF-6.2) |
| AF-C | The Grundlage states a team of five and a project | The paragraph names the team and the project; the attribute is not written |
| AF-D | A Mehrwert sentence promises "zehn Prozent Kostensenkung" | Blocker; the sentence is rewritten as fit with the task (AF-3.3) |
| AF-E | The closing says "würde mich freuen" | Rewritten in the Indikativ with a content sentence (AF-8.1, AF-5.3) |
| AF-F | The user wants to explain a gap of eight months | One factual sentence in the user's words, no apology; a health reason is not named (AF-9.2, AF-9.3) |
| AF-G | Career change into a new field | Two or three transferable proofs, one positive sentence for the reason, no word "Quereinsteiger" (AF-9.4) |
| AF-H | A paragraph that stays true for any employer | Fails the exchange test; rewritten with a posting term and a sourced employer fact, or cut (AF-7.1) |
| AF-I | The salary is asked for and the user gives a value | The sentence stands in the closing part in the Indikativ, before the wish for a conversation, not in a PS (AF-8.5) |
| AF-J | The posting forbids AI help | Recorded in `analyse.md`; the skill tells the user before drafting (AF-11.5, AS-11) |
| AF-K | The user supplies a joke for the opening | Written only in the *sachlich-modern* or *du* register; in the *formell* register the skill tells the user and asks (AF-10.2) |
| AF-L | Three sentences in a row begin with "Ich" | Hinweis; the subject of the sentences is varied (AF-5.5) |

## AF-16 Sources

All retrieved 2026-10-26. "Full text" means the page was read; "Summary" means only a search summary was
available. Where sources disagree, AF-2.4 records the decision.

| Source | Type | Read |
|---|---|---|
| [Hays, Anschreiben für die Bewerbung: Leitfaden, Beispiele, Vorlagen](https://www.hays.de/blog/karriere-und-entwicklung/anschreiben-fuer-bewerbung-leitfaden-beispiele-vorlagen) | Recruiter blog | Full text |
| [TU Darmstadt, SchreibCenter, Bewerbungen I: das Anschreiben](https://www.owl.tu-darmstadt.de/media/owl/schreibtechniken_und__uebungen/Leitfaden_Anschreiben.pdf) | University guide, after Hesse and Schrader (2017), Püttjer and Schnierda (2011), Slaghuis (2016) | Full text |
| [Universität des Saarlandes, Career Center, Das Bewerbungsanschreiben](https://www.uni-saarland.de/fileadmin/upload/einrichtung/career-center/Material/Dokumente/Doks_DEU/2_Anschreiben.pdf) | University guide | Full text (first page) |
| [Karrierebibel, Bewerbungsschreiben](https://karrierebibel.de/bewerbungsschreiben/) | Ratgeber | Full text |
| [Karrierebibel, Gehaltsvorstellung](https://karrierebibel.de/gehaltsvorstellung/) | Ratgeber | Full text |
| [Karrierebibel, Arbeitslosigkeit im Lebenslauf](https://karrierebibel.de/arbeitslosigkeit-im-lebenslauf/) | Ratgeber | Full text |
| [Karrierebibel, Bewerbung als Quereinsteiger](https://karrierebibel.de/bewerbung-quereinsteiger/) | Ratgeber | Full text |
| [Robert Half, Der gute Schlusssatz für Ihre Bewerbung](https://www.roberthalf.com/de/de/insights/bewerbungs-tipps/kein-ende-mit-schrecken-der-gute-schlusssatz-fuer-ihre-bewerbung) | Recruiter blog | Full text |
| [Jobseeker, Bewerbungstrends 2026: HR-Profis und Lebensläufe](https://www.jobseeker.com/de/lebenslauf/artikel/bewerbungstrends-einstellungsstatistiken) | Vendor survey, 1,013 HR professionals, 2025 | Full text |
| [ResumeGo, Cover letters: just how important are they?](https://resumego.net/research/cover-letters) | Commercial field experiment, 2019 to 2020, US | Full text; group figures only in charts |
| [arXiv 2509.25054, Signaling in the Age of AI: Evidence from Cover Letters](https://arxiv.org/abs/2509.25054) | Preprint, version 2, 2025 | Abstract page |
| [t3n, KI-Bewerbung: So reagieren Personaler auf ChatGPT-Anschreiben](https://t3n.de/news/ki-bewerbung-chatgpt-anschreiben-so-reagieren-personaler-1529440/) | Trade press, 2023, n = 2 | Full text |
| [Personalwirtschaft, Studie zeigt Recruiting-Trends bis 2026 (Stepstone, BPM)](https://www.personalwirtschaft.de/recruiting/artikel/studie-zeigt-recruiting-trends-bis-2026-stepstone-bpm.html) | Trade press on a 2021 survey | Full text |
| [karriere.at, Bewerbung als Quereinsteiger](https://www.karriere.at/c/a/bewerbung-quereinsteiger) | Ratgeber | Summary |
| [onlinemarketing.de, Lücke im Lebenslauf](https://onlinemarketing.de/karriere/karriere-tipps/luecke-im-lebenslauf) | Ratgeber | Summary |
| [Stepstone, STAR-Methode](https://stepstone.de/magazin/artikel/star-methode) | Ratgeber, interview technique | Summary |
| Langer, Schulz von Thun, Tausch: Sich verständlich ausdrücken; as described in [Lutz, Verständlichkeit, trans-kom 10 (3)](https://www.trans-kom.eu/bd10nr03/trans-kom_10_03_02_Lutz_Verstaendlichkeit.20171221.pdf) and [Universität Wien, Verständlichkeit von Texten](https://wishare.univie.ac.at/fileadmin/user_upload/p_wishare/Verstaendlichkeit_von_Texten.pdf) | Textbook, read through secondary sources | Summary |
