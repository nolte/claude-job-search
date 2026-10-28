# Career change and job search

**Goal:** find out what you want, find postings that fit, and apply in a field where your CV
does not read as a straight line.

**Example:** After eight years in logistics planning you want to move into data analysis.

## Steps

### 1. Record what you want

```text
/job-application:job-application-traumjob-interview
```

A seven-phase interview about wishes, priorities, exclusions and hypotheses. Nothing is written
before you confirm the summary. The result is `wunschprofil.md`, including your **vetoes**
(for example: no on-call duty, no Zeitarbeit).

### 2. Search job boards (optional)

```text
/job-application:job-application-job-search
```

The skill derives a **Suchbrief** from the Wunschprofil and `profil.md`, shows it with the source
of every search term, and searches only after your yes. It needs the optional
[JobSpy](../jobspy.md) server, which carries its own risks; read that page first. You get a
shortlist in which vetoes are visible, duplicates are merged and recruiter postings are flagged.
The list is kept in `suche/<date>-<slug>.md`. You pick one posting; the skill hands it to
`job-application-solution`.

Without JobSpy, skip this step and paste a posting you found yourself.

### 3. Check the fit before you invest

```text
/job-application:job-application-fit-check
```

Paste a posting or name a company. The result in `passung.md` is one of *Veto*, *Klärungsbedarf*
or *Passt überwiegend*. Vetoes are listed first and every value names its source. You can run
the check on its own before investing time. With a confirmed Wunschprofil,
`job-application-solution` also runs it in the analysis, and a veto stops the plan gate until
you decide, so you do not write for a job you would not take.

### 4. Apply with a career-change profile

Run `job-application-solution` for the chosen posting. For a changeover the plan typically
proposes:

- CV format `kombiniert`: a Kurzprofil of at most three sentences, then the chronological
  stations. Relevant older evidence can sit in a short *Relevante* block, only in this format.
- Anschreiben variant `quereinstieg`: it maps the posting's requirements to proofs from your
  logistics years (for example, building forecasts in Excel and SQL) and says openly where
  experience is still missing. It asks you for the reason for the change in one sentence, in
  your words; otherwise the letter carries `[ERGÄNZEN: Grund des Wechsels]`. The wishes from
  the interview do not appear in the letter.

## What remains

`wunschprofil.md`, `suche/…`, `passung.md` per checked posting, and the Vorgang folder of each
application you started.

## Good to know

- You can run the interview again later; the Wunschprofil is replaced only after you confirm.
- The fit check is a decision aid, not a gate on your freedom: *Klärungsbedarf* means questions
  to ask in the interview, not a no.
