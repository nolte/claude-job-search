---
name: bewerbung-lebenslauf-erstellen
description: "Produces a German tabellarischer Lebenslauf (rückwärts chronologisch, typically 1–2 pages) from bewerbung/profil.md, ordered and weighted for one posting when an analysis exists. Marks gaps and missing data as [ERGÄNZEN] instead of inventing them. Writes Markdown only. Use on \"erstelle meinen Lebenslauf\", \"Lebenslauf für diese Stelle anpassen\", \"tabellarischen Lebenslauf schreiben\", or equivalent German requests. Don't use for the cover letter (bewerbung-anschreiben-erstellen), for the profile intake (bewerbung-profil-erfassen), or for the English CV format (out of scope for this plugin)."
tags: [bewerbung, lebenslauf, cv, deutsch, dach]
phase: create
summary: "Builds a German tabular CV, reverse chronological, from the profile and optionally tailored to one posting."
summary_de: "Erstellt einen tabellarischen deutschen Lebenslauf, rückwärts chronologisch, aus dem Profil und optional auf eine Stelle zugeschnitten."
use_when:
  - "you need a German CV from your profile"
  - "you want the CV ordered and emphasised for a specific posting"
dont_use_when:
  - situation: "You need the cover letter"
    alternative: bewerbung-anschreiben-erstellen
  - situation: "The profile does not exist yet"
    alternative: bewerbung-profil-erfassen
see_also:
  - bewerbung-profil-erfassen
  - bewerbung-stellenanzeige-analysieren
  - bewerbung-anschreiben-erstellen
  - bewerbung-pruefen
---

# Bewerbung Lebenslauf erstellen

Spec: `spec/bewerbung/konventionen/en.md` R-1 (facts) and R-2 (form). This skill
only reshapes facts that already exist in the profile.

## Inputs

- `bewerbung/profil.md` (required).
- `bewerbung/<slug>/analyse.md` (optional). When present, its *erfüllt* rows decide
  which entries get more room and which skills are listed first.

## Output

`bewerbung/<slug>/lebenslauf.md` in this order:

```markdown
# Lebenslauf

## Persönliche Daten
Name, Anschrift, Telefon, E-Mail, LinkedIn (optional)

## Beruflicher Werdegang
| Zeitraum | Position, Arbeitgeber, Ort | Aufgaben und Ergebnisse |
|---|---|---|
| 04/2021 – heute | Senior Backend-Entwickler, Musterfirma GmbH, Berlin | … |

## Ausbildung und Studium
## Schulbildung
## Sprachkenntnisse
## IT- und Fachkenntnisse
## Weiterbildung und Zertifikate

Ort, Datum
```

Use `MM/JJJJ` for dates everywhere. Use the profile's exact titles, employer names,
and certificate names.

## Workflow

1. Read the profile. Stop and report any `[ERGÄNZEN]` item that blocks a section.
2. Order entries by date, most recent first (R-2).
3. If an analysis exists, shorten entries that do not support any *Muss* requirement
   and give the matching ones fuller wording. Reorder skills so the posting's terms
   come first, but only for skills the profile really covers.
4. Keep the total within about two pages. Trim older or irrelevant entries before
   trimming recent ones.
5. Write the file.

## Hard rules

1. **Reverse chronological, tabular** (R-2). No free-form narrative CV.
2. **Only profile facts.** Tailoring changes emphasis and order, never content.
3. **Gaps stay visible.** Show them as the user described them, or as
   `[ERGÄNZEN: Grund der Lücke]`.
4. **Optional personal data stays out** unless the profile explicitly includes it.
5. **Signature line:** Ort, Datum. Add a handwritten signature line only if the user
   plans to send a paper copy.
