---
name: job-application-fit-check
description: "Checks one real posting or company against the confirmed Wunschprofil and writes passung.md with a verdict (Veto, Klärungsbedarf, Passt überwiegend), vetoes first, each value sourced. Use on \"passt die Stelle zu mir\", \"Stelle gegen meine Wünsche prüfen\", \"ist das was für mich\", or equivalent German requests. Don't use to elicit the wishes (job-application-traumjob-interview), to analyse the posting requirements (job-application-posting-analysis), or to decide whether to apply (the candidate decides)."
tags: [bewerbung, passung, wunschprofil, deutsch]
phase: analyse
summary: "Compares a posting or company with the confirmed wishes and reports vetoes and sourced deviations."
summary_de: "Vergleicht eine Stelle oder ein Unternehmen mit den bestätigten Wünschen und meldet Vetos und belegte Abweichungen."
use_when:
  - "you want to know whether a posting fits what you want from work"
  - "a posting looks promising and you want to check it against your wishes before applying"
dont_use_when:
  - situation: "You do not have a confirmed Wunschprofil yet"
    alternative: job-application-traumjob-interview
  - situation: "You want the requirements matched against your Grundlage"
    alternative: job-application-posting-analysis
see_also:
  - job-application-traumjob-interview
  - job-application-posting-analysis
  - job-application-solution
---

# Bewerbung Passungsprüfung

Spec: `spec/job-application/traumjob-interview/en.md` WJ-6 (fit check), WJ-7 (use in the process), WJ-8
(privacy). Company facts and their sources: `spec/job-application/unternehmensanalyse/en.md` UA-3 and UA-5.

## Inputs

- `<wurzel>/wunschprofil.md` with `bestaetigt: ja`. Without it, stop and point to `job-application-traumjob-interview`
  (WJ-6.1).
- `job-application/<slug>/analyse.md`, including the requirements and the section `## Unternehmen`. If it is missing,
  run `job-application-posting-analysis` first.
- The working conditions from the posting: location, form of work, hours, contract form, salary if stated, team and
  leadership if stated.

## Workflow

1. **Load the profile.** Read the wishes, their priorities and the Ausschlüsse. Note the version and the date.
2. **Collect the facts.** For each wish, find what the posting or the company analysis states about it. Keep the
   quote or the source for every fact. Facts from rating portals are not used (UA-2.1).
3. **Value each wish** with one of these values (WJ-6.2):
   - `passt`: the posting states something that matches, with a source;
   - `teilweise`: partly matches, or the posting is silent on part of it;
   - `passt nicht`: the posting states something that contradicts it, with a source;
   - `unklar`: the posting is ambiguous on the point;
   - `nicht ermittelt`: the posting says nothing about it.
   `nicht ermittelt` is never `passt nicht`. Silence is a question for the counterpart (KK-5), not a contradiction.
4. **Apply the veto rule** (WJ-6.3). An Ausschluss with `passt nicht` is a veto. A Muss with `passt nicht` is a strong
   negative, a Soll with `passt nicht` is a negative, a Kann is a note. A Hypothese never triggers a veto; show its
   value marked as Hypothese.
5. **Do not score.** Count matches and contradictions if useful, but do not turn them into a total number. A number
   hides which wish is in conflict.
6. **Set the verdict.** `Veto` if any veto exists. `Klärungsbedarf` if a Muss or Soll is `unklar`, `teilweise` or
   `nicht ermittelt`. `Passt überwiegend` otherwise. Never give `Passt überwiegend` while a Muss is `nicht ermittelt`.
7. **Write `passung.md`** in the Vorgang folder, in the form below.

## Output

`job-application/<slug>/passung.md`:

```markdown
---
stand: YYYY-MM-DD
wunschprofil_version: 1
gesamturteil: Veto | Klärungsbedarf | Passt überwiegend
---

## Vetos
- Ausschluss „…“: Stellenanzeige „…“ (Quelle). Oder: keine.

## Abweichungen
| Wunsch | Priorität | Passung | Quelle |
|---|---|---|---|

## Passt
| Wunsch | Priorität | Passung | Quelle |
|---|---|---|---|

## Nicht ermittelt
- Wunsch … Frage an den Kontakt (KK-5).

## Hinweise
- Hypothese „…“: Passung nicht beurteilbar, bis Nachweis vorliegt.
```

Vetos come first. Every value names its source.

## Use in the application process

- **Before the plan gate.** Run the fit check before `job-application-solution` step 3. A veto stops the plan gate
  until the candidate decides: continue despite the veto, or stop this application. Record the decision in `vorgang.md`
  under `Verlauf`.
- **The documents do not change.** The CV and the letter state facts and evidence (CG-4), never the candidate's wishes.
- **Questions to the counterpart** for `nicht ermittelt` values are written only after the counterpart and the
  disclosure are known (KK-4, KK-5), by `job-application-email-create`.

## Hard rules

1. **Never change the Wunschprofil.** The fit check reports conflicts. A change of wish comes from the candidate
   (WJ-5.1).
2. **Never send.** `passung.md` is for the candidate. It is never sent to a counterpart and never copied into a document
   (WJ-8.2).
3. **No inferred values.** Do not value a wish from the company's reputation or from silence in the posting.
4. **Stay local.** No web search carries wishes or interview content (WJ-8.2, UA-3.3).
