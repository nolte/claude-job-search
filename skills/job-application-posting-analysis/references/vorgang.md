# Template of `vorgang.md` (LS-6.1)

Loaded by `job-application-posting-analysis` when the Vorgang folder is created (S1). Spec:
`spec/job-application/lokale-struktur/en.md` LS-5.4, LS-6, LS-6.1, LS-7.6, LS-8.1; `spec/job-application/konventionen/en.md` R-9.5.

```yaml
---
firma: <Anstellungsgeber, or unbekannt>
stelle: <role title without gender suffix>
ref_nr: <reference number, empty when the posting has none>
bewerbungsweg: email | portal | post
ausrichtung: ausschreibung | initiativ | quereinstieg | berufseinstieg | vermittler
stellenquelle: <URL, or: Text, eingefügt>
kontaktart: "<KK-6 value, or Unklar>"
status: erfasst
erfasst: JJJJ-MM-TT
grundlage_hash:                     # set by every skill that writes a status (LS-5.4), from scripts/grundlage_hash.py
versendet_am:                       # S7, user statement
weg:                                # S7
anhaenge: []                        # S7
wiedervorlage:                      # empty until sent; the user sets it with versendet_am (versendet_am plus the follow-up period of KK-5.4)
loeschen_ab:                        # S10: deletion date set by the user, or empty (LS-6 rule 8)
tags: []
---

[<Firma>](../firmen/<firma-slug>.md) · [Grundlage](<relative path to the Grundlage>) · [Analyse](analyse.md) · [Notizen](notizen.md)

## Plan

## Verlauf
- JJJJ-MM-TT: Vorgang angelegt (erfasst), job-application-posting-analysis
- JJJJ-MM-TT: erfasst → analysiert, job-application-posting-analysis
```

- The link line uses standard Markdown links with relative paths, never wikilinks (LS-8.1, LS-7.6). The path to the
  Grundlage is relative to the Vorgang folder and points to the real file of `grundlage`.
- `grundlage_hash`: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/grundlage_hash.py job-application/konfiguration.md`
  (R-9.5) and write the hash. On a `Blocker:` line, leave the field empty and report it.
- **Status rule (LS-6 rules 1, 2, 4, 7).** Set `analysiert` only while the status is `erfasst`. On a re-run of a
  Vorgang that is already `analysiert` or later (including `versendet`, `rückmeldung` and every later value,
  which are user statements), the status stays as it is and no status line is written.
- Allowed `status` values (LS-6): `erfasst, analysiert, geplant, erstellt, geprüft, in Arbeit, versendet, rückmeldung,
  gespräch, angebot, verhandlung, zusage, absage, abgelehnt, zurückgezogen, ohne Antwort, abgeschlossen`. Every actual
  change of status adds one line `- JJJJ-MM-TT: <alter> → <neuer Status>, <Skill>` to `## Verlauf`; old lines are never
  removed.
