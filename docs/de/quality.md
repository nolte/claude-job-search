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
| Technische ATS-Prüfung der exportierten Datei (`ATS-01` bis `ATS-05`): gültige Datei, Schriften, versteckter Text, Überschriften beim Inhalt, Zeiträume und Stationen, Kontaktdaten, Spalten, Tabellen, Bilder, Symbolbewertung | das Skript (`pdffonts`, `pdfimages` zusätzlich), nur für PDF, DOCX und HTML | funktioniert; ohne die Werkzeuge `BLOCKED` |
| Schlüsselbegriffe der Analyse im Lebenslauf (`KW-01`) | das Skript; fügt nie etwas ein | funktioniert |
| Beleg jeder Aussage gegen die Datengrundlage, Verantwortung und Seniorität, Relevanz, Sprache, Konsistenz | ein Modell schreibt Urteile (`qualitaet-urteile.json`); das Skript prüft, dass Zitat und Beleg wörtlich vorkommen | **braucht ein Modell**; ohne Modell stehen die Prüfungen auf `NEEDS_REVIEW` |
| Eine offene Prüfung bestätigen | du (`entscheiden … --ja`) | bewusst nicht automatisch |
| Das Paket freigeben und versenden | du | **nie durch die Werkzeugkette**: keine Prüfung sendet etwas oder gibt etwas frei |

Ein `PASS` heißt „nichts gefunden“, nicht „richtig“. ATS-Lesbarkeit wird an der exportierten Datei und ihrem extrahierten Text
beurteilt; wie ein bestimmtes Bewerbermanagementsystem deine Datei liest, ist nicht getestet und nicht zugesagt.

## Technische ATS-Prüfung

Der Bericht hat einen Block `ats`: `umfang` ist `vollstaendig`, `teilweise` oder `nicht_geprueft`, `technisch_validiert` ist nur
bei einem vollständigen Lauf ohne `FAIL`, `BLOCKED` oder offene Prüfung wahr. Das heißt: die festgelegten Prüfungen sind
bestanden. Es heißt nicht, dass ein bestimmtes System die Datei liest, und nichts über deine fachliche Passung. Es gibt keinen
Gesamtscore; jede Prüfung hat eine `dimension` (`technisch`, `evidenz`, `formal`, `schluesselbegriffe`, `passung`).

| Prüfung | Was sie findet | Schwere |
|---|---|---|
| `EX-03` | kaum Text, Ersatzzeichen, Ligaturzeichen, gesperrte Wörter | Blocker bzw. Warnung |
| `ATS-01` | kaputte PDF-/DOCX-Struktur, Kopierverbot, versteckter, weißer oder winziger Text; Schriften vom Typ 3 oder nicht eingebettet | Blocker bzw. Warnung |
| `ATS-02` | Überschrift nicht als eigene Zeile, Inhalt nicht unter seiner Überschrift, DOCX-Überschriftenformate anders als die Quelle | Warnung |
| `ATS-03` | verlorener oder vertauschter Zeitraum; Position und Arbeitgeber nicht beim Zeitraum; gemischte Datumsformate | Blocker bzw. Warnung |
| `ATS-04` | E-Mail oder Telefonnummer der Quelle nicht lesbar (auch: nur in Kopf-/Fußzeile); Lebenslauf ohne E-Mail | Blocker bzw. Warnung |
| `ATS-05` | Spalten, Tabellen, Bilder, Textfelder, Kopf-/Fußzeilentext, Wörter außerhalb der Seite; Bewertung nur als Sterne oder Balken | Warnung bzw. `NEEDS_REVIEW` |
| `KW-01` | belegte Kompetenz fehlt als Begriff; Begriff steht im Lebenslauf, die Analyse belegt ihn nicht | Warnung bzw. `NEEDS_REVIEW` |

`md` und `tex` sind Kopien der Quelle: ohne PDF, DOCX oder HTML im Ordner `export/` sind die `ATS-xx`-Prüfungen
`NOT_APPLICABLE`. Eine Warnung zu Spalten oder Tabellen ist ein Risiko, kein Fehler. Layout, überlagerte Elemente und schöne
Seitenumbrüche siehst du selbst an; die Prüfungen ersetzen das nicht. Die Prüfungen brauchen kein Modell.

!!! note "Noch nicht an einem echten LaTeX-PDF gemessen"
    Die Prüfungen der PDF-Stationen (`ATS-03`, Spaltenerkennung) sind mit synthetischen PDFs getestet. Am echten LuaLaTeX-PDF
    des Templates sind sie in dieser Umgebung noch nicht gelaufen (LuaLaTeX fehlt dort). Zeige das nächste echte PDF mit
    `task quality` und melde Fehlalarme.

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
