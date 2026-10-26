# Qualitätssicherung

`scripts/qualitaet.py` prüft einen Vorgang und schreibt einen Bericht, `qualitaet.json`, in dessen Ordner. Die Regeln stehen in
`spec/job-application/qualitaetssicherung/en.md` (QS-1 bis QS-12). Diese Seite sagt, worauf du dich verlassen kannst und was
du selbst tun musst.

```bash
task quality -- pruefen <wurzel>/<slug> --konfiguration job-application/konfiguration.md
```

## Was sie tut und was nicht

| Teil | Wer | Stand |
|---|---|---|
| Regeln für Lebenslauf und Briefe (Zahlen, Zeiträume, Führung, Platzhalter), Kontaktdaten, Firmenname, übernommener Anzeigentext, Floskeln | das Skript, wiederholbar | funktioniert |
| Rücklesen des Exports: Hash, Quelle unverändert, Wortlaut, Reihenfolge, Text extrahierbar, Seitenlimit, leere Seiten | das Skript (PDF braucht `pdftotext` und `pdfinfo` aus poppler-utils) | funktioniert; ohne die Werkzeuge ist die Prüfung `BLOCKED` |
| Beleg jeder Aussage gegen die Datengrundlage, Verantwortung und Seniorität, Relevanz, Sprache, Konsistenz | ein Modell schreibt Urteile (`qualitaet-urteile.json`); das Skript prüft, dass Zitat und Beleg wörtlich vorkommen | **braucht ein Modell**; ohne Modell stehen die Prüfungen auf `NEEDS_REVIEW` |
| Eine offene Prüfung bestätigen | du (`entscheiden … --ja`) | bewusst nicht automatisch |
| Das Paket freigeben und versenden | du | **nie durch die Werkzeugkette**: keine Prüfung sendet etwas oder gibt etwas frei |

Ein `PASS` heißt „nichts gefunden“, nicht „richtig“. ATS-Lesbarkeit wird am extrahierten Text beurteilt; wie ein bestimmtes
Bewerbermanagementsystem deine Datei liest, ist nicht getestet und nicht zugesagt.

## Ergebnisse

Jede Prüfung endet in `PASS`, `FAIL`, `WARNING`, `NEEDS_REVIEW`, `NOT_APPLICABLE` oder `BLOCKED`. Das Gesamtergebnis entscheidet,
ob das Paket dir zur Freigabe vorgelegt werden darf: nur bei `BEREIT`, `BEREIT_MIT_WARNUNGEN` und
`BEREIT_NACH_MANUELLER_PRUEFUNG` (jede offene Prüfung von dir bestätigt).

Der Bericht ist an den Hash jedes Dokuments und jedes Exports gebunden. Ändert sich eine Datei, ist er veraltet: Prüfung erneut
ausführen. Ohne aktuellen, freigabefähigen Bericht ist die Workflow-Aufgabe `pruefung` nicht erledigt und die Versandfreigabe
wird abgelehnt. Die Freigabe selbst bleibt bei dir.

## Wo sie aufhört

- Die deterministischen Prüfungen lesen keine Bedeutung. Ein falscher Satz ohne Zahl, Datum oder Namen kann durchgehen.
- Ein semantisches Urteil wird nur auf Form und wörtliche Zitate geprüft, nicht darauf, ob es stimmt.
- Layout, Schriften, Ton und die Passung zu dir sind Sache eines Menschen; die Evals (`evals.md`) sind getrennt und manuell.
