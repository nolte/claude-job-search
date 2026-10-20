---
name: bewerbung-pruefen
description: "Quality gate for an application folder: checks completeness, identical role, company and reference data across documents, traceability of every claim to bewerbung/profil.md, German spelling and grammar, length limits, leftover [ERGÄNZEN] placeholders, and attachment names. Writes bewerbung/<slug>/pruefbericht.md with blockers, warnings, and notes. Use on \"prüfe meine Bewerbung\", \"ist die Bewerbung versandfertig\", \"check die Unterlagen\", or equivalent German requests. Don't use to write or rewrite documents (use the owning skill), or for an independent whole-set review (use the bewerbungs-reviewer agent)."
tags: [bewerbung, pruefung, qualitaet, deutsch]
phase: review
summary: "Quality gate that reports blockers, warnings and notes for one application folder before it is sent."
summary_de: "Qualitätsprüfung eines Bewerbungsordners mit Blockern, Warnungen und Hinweisen, bevor er versendet wird."
use_when:
  - "you have a set of application documents and want to know whether they are ready to send"
  - "you changed one document and need to confirm consistency"
dont_use_when:
  - situation: "You want the documents written or rewritten"
    alternative: bewerbung-solution
  - situation: "You want an independent, read-only review of the full set"
    alternative: bewerbungs-reviewer
see_also:
  - bewerbungs-reviewer
  - bewerbung-solution
---

# Bewerbung prüfen

Spec: `spec/bewerbung/konventionen/en.md` R-1 … R-7. R-7 defines what "ready to send" means.

## Inputs

- The folder `bewerbung/<slug>/`, with `profil.md` and `analyse.md` in `bewerbung/`
  and the documents in the slug folder.

## Checks

| Check | Severity when it fails |
|---|---|
| `[ERGÄNZEN` placeholder left in any document | Blocker |
| Required document missing (Lebenslauf, Anschreiben, E-Mail if `email`, Zeugnisse if requested) | Blocker |
| Company, role, reference number, or contact name differ between documents | Blocker |
| Claim in a document not traceable to `profil.md` (R-1) | Blocker |
| E-Mail attachment list names a file that is not in the folder | Blocker |
| Anschreiben longer than one page (about 400+ words) | Warning |
| Lebenslauf longer than two pages | Warning |
| Mixed date formats or inconsistent Zeiträume | Warning |
| Spelling or grammar errors in German text | Warning |
| Anrede not matching the Ansprechpartner, or generic when a name is known | Warning |
| Requirement marked *Muss* in the analysis not addressed in the Anschreiben | Warning |
| Stock phrase ("hiermit bewerbe ich mich") | Warning |
| Optional personal data present without the user's request | Note |
| Missing Ort, Datum, or Unterschrift line where R-2 expects them | Note |

## Output

`bewerbung/<slug>/pruefbericht.md`:

```markdown
# Prüfbericht — <Stelle> (<Firma>)

Stand: YYYY-MM-DD · Verdict: BLOCKED | READY-WITH-WARNINGS | READY

## Blocker
- [ ] <Dokument>: <Befund> — <Vorschlag>

## Warnungen
- [ ] …

## Hinweise
- …
```

`READY` requires zero blockers and zero warnings. `READY-WITH-WARNINGS` requires zero
blockers. Any blocker means `BLOCKED`.

## Workflow

1. Read the analysis and the profile first, then each document.
2. Run the checks above. Quote the exact passage for every finding.
3. Write the report. Show the user the verdict and the blockers in chat as well.
4. Fix blockers only with the user's agreement, through the owning skill.

## Hard rules

1. **Report, do not silently fix.** Edits to the documents happen only through the owning skill.
2. **Every finding quotes its source** with the file name and the passage.
3. **Traceability is strict.** A claim the report cannot find in `profil.md` is a blocker,
   even if it sounds plausible.
