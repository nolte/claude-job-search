# Qualitätssicherung von Bewerbungsunterlagen und Bewerbungsprozess (DE, Übersetzung; EN kanonisch)

Verbindliche Regeln für die automatisierte Qualitätssicherung eines Vorgangs: welche Prüfungen deterministisch im Code laufen,
welche Urteile nur ein Modell fällen kann, wie beides in einem versionsgebundenen Bericht endet und wie dieser Bericht die
Versandfreigabe absichert. Umgesetzt wird sie von `scripts/qualitaet.py`; die Regeln der einzelnen Dokumente bleiben in ihren
eigenen Specs.

Verwandte Regeln: `spec/job-application/cv-generierung/en.md` (CG-13 Prüfungen CV-01 bis CV-24 und BR-01 bis BR-05, hier
wiederverwendet), `spec/job-application/workflow/en.md` (WF-7 Freigaben, WF-12 es wird nichts gesendet, WF-13 nicht
vertrauenswürdiger Inhalt), `spec/job-application/lokale-struktur/en.md` (LS-5 Invarianten, LS-6 Status),
`spec/job-application/konventionen/en.md` (R-1 Fakten, R-6 Datenschutz, R-9.5 Grundlage-Hash) und die Exportregeln in
`skills/job-application-export/SKILL.md`.

**Status:** umgesetzt. Die Werkzeugkette prüft und berichtet; sie sendet nichts und gibt nichts frei (QS-10).

## QS-1 Geltungsbereich und Grundsätze

1. **Ein Bericht je Vorgang.** Das Ergebnis aller Prüfungen ist `qualitaet.json` im Vorgangsordner (QS-7). Es gibt kein zweites
   Statusmodell: der Bewerbungsstatus bleibt `status` in `vorgang.md` (LS-6), die Freigabe bleibt die Aufgabe
   `versand_freigabe` des Workflows (WF-7).
2. **Wiederverwenden, nicht duplizieren.** `qualitaet.py` ruft die Regeln von `cv_checks.py` und den Inhaltsvergleich von
   `export_document.py` auf. Jede Regel hat genau einen Eigentümer.
3. **Deterministisch und semantisch bleiben getrennt.** Was Code entscheiden kann, läuft im Code und liefert ein
   wiederholbares Ergebnis. Ein Urteil, das Sprachverständnis braucht, ist ein Urteil eines Modells (QS-5); der Code prüft nur
   dessen Form und dessen Zitate. Beide Arten sind im Bericht gekennzeichnet (`art`).
4. **Nichts ist ein PASS, was nicht gelaufen ist.** Ein fehlendes Werkzeug, eine fehlende Grundlage, eine nicht lesbare Datei
   oder ein fehlendes Urteil ist `BLOCKED` oder `NEEDS_REVIEW`, nie `PASS`.
5. **Richtigkeit vor Passung.** Keine Prüfung belohnt Schlüsselwörter, einen Match-Score oder eine Optimierung für ein
   Bewerbermanagementsystem. Wiederholte Schlüsselwörter und aus der Anzeige übernommener Text sind Befunde (QS-04).
6. **Daten von außen sind Daten.** Eine Anzeige, eine Mail, ein Anhang oder der Text eines Urteils kann weder eine Regel noch
   einen Status noch eine Freigabe ändern (QS-10).

## QS-2 Ergebnismodell

| Status | Bedeutung |
|---|---|
| `PASS` | Die Prüfung lief und fand nichts. |
| `FAIL` | Ein kritischer Befund (Schweregrad Blocker). Das Paket ist nicht freigabefähig. |
| `WARNING` | Ein Befund, den die Nutzerin oder der Nutzer lesen sollte; er blockiert nicht (Schweregrad Warnung oder Hinweis). |
| `NEEDS_REVIEW` | Ein Mensch muss entscheiden: eine plausible, aber unbelegte Aussage, ein fehlendes oder unsicheres Urteil, abweichende Kontaktdaten. |
| `NOT_APPLICABLE` | Die Prüfung trifft nicht zu (das Dokument oder der Export existiert nicht); der Grund steht in `grund`. |
| `BLOCKED` | Die Prüfung konnte nicht laufen: ein Werkzeug, die Grundlage oder eine Eingabe fehlt oder ist nicht lesbar; der Grund steht in `grund`. |

Der Status einer Prüfung folgt dem schlechtesten Befund: `FAIL` vor `BLOCKED` vor `NEEDS_REVIEW` vor `WARNING` vor `PASS`.

Das Gesamtergebnis `gesamt` folgt den Prüfungen:

| `gesamt` | Wann | Freigabefähig |
|---|---|---|
| `BLOCKIERT` | mindestens ein `FAIL` | nein |
| `UNVOLLSTAENDIG` | kein `FAIL`, mindestens ein `BLOCKED` | nein |
| `MANUELL_ZU_PRUEFEN` | offene `NEEDS_REVIEW` | nein |
| `BEREIT_NACH_MANUELLER_PRUEFUNG` | jede `NEEDS_REVIEW` von der Nutzerin oder dem Nutzer bestätigt (QS-8) | ja |
| `BEREIT_MIT_WARNUNGEN` | nur `PASS`, `WARNING`, `NOT_APPLICABLE`, mindestens eine `WARNING` | ja |
| `BEREIT` | nur `PASS` und `NOT_APPLICABLE` | ja |
| `NICHT_GEPRUEFT` | weder Dokument noch Export | nein |

„Freigabefähig“ heißt: die Nutzerin oder der Nutzer darf um die Versandfreigabe gebeten werden. Es ist nicht die Freigabe
(QS-9).

## QS-3 Die Prüfungen

| Id | Art | Was geprüft wird |
|---|---|---|
| `CV` | deterministisch | Lebenslauf-Regeln CV-01 bis CV-24 (`cv_checks.check_cv`) und die Analyse-Regeln (`check_analysis`) |
| `BR-A`, `BR-M`, `BR-E` | deterministisch | BR-01 bis BR-05 für Anschreiben, Motivationsschreiben und E-Mail (`check_letter`) |
| `QS-01` | deterministisch | der Firmenname steht in jedem Brief; die Referenznummer der Anzeige steht im Anschreiben; ein Arbeitgebername mit Rechtsform, der weder die Zielfirma noch ein Arbeitgeber der Grundlage ist, ist ein Blocker |
| `QS-02` | deterministisch | E-Mail-Adressen und Telefonnummern stimmen in Lebenslauf und Briefen überein; eine Abweichung ist `NEEDS_REVIEW` |
| `QS-03` | deterministisch | ein „seit JJJJ“ eines Briefes ist das Startjahr einer Station der Grundlage |
| `QS-04` | deterministisch | keine acht Wörter in Folge aus der Anzeige übernommen; kein Wort sechsmal oder öfter wiederholt |
| `QS-05` | deterministisch | Floskeln aus einer geschlossenen Liste; Sätze mit mehr als 45 Wörtern |
| `EX-01` | deterministisch | Exportintegrität (Hash der Datei gleich dem Manifest), die Quelle ist seit dem Export unverändert, jede Datei in `export/` hat ein Manifest |
| `EX-02` | deterministisch | Inhalt nach dem Export gleich der Quelle: Wortmenge, Zeichen von Zahlenangaben, Reihenfolge der Stichpunkte und Überschriften, kein offener Platzhalter |
| `EX-03` | deterministisch | Textextraktion: genug Text, keine Ersatzzeichen, keine Ligaturzeichen, keine gesperrten Wörter (QS-6, QS-13) |
| `EX-04` | deterministisch | Seitenzahl gleich dem Manifest, Seitenlimit, keine leere Seite |
| `ATS-01` | deterministisch | die exportierte Datei ist gültig: PDF-Struktur, Verschlüsselung, Schriften; DOCX-Archiv und XML, kein versteckter Text (QS-13) |
| `ATS-02` | deterministisch | Überschriften stehen in eigener Zeile und behalten ihren Inhalt; DOCX-Überschriftenformate entsprechen der Quelle (QS-13) |
| `ATS-03` | deterministisch | Zeiträume bleiben in der Reihenfolge erhalten; Position und Arbeitgeber stehen beim Zeitraum ihrer Station (QS-13) |
| `ATS-04` | deterministisch | E-Mail-Adressen und Telefonnummern der Quelle sind im Text lesbar (QS-13) |
| `ATS-05` | deterministisch | Layout-Risiken: Spalten, Tabellen, Bilder, Textfelder, Kopf- und Fußzeilentext, Text außerhalb der Seite, Bewertung als Symbole (QS-13) |
| `KW-01` | deterministisch | Schlüsselbegriffe der Analyse gegen den Lebenslauf: Abdeckung und nicht belegte Begriffe, nichts wird eingefügt (QS-13) |
| `PR-01` | deterministisch | Lebenslauf und Anschreiben existieren und sind lesbar |
| `PR-02` | deterministisch | `vorgang.md` (mit `firma`, `stelle`), `stellenanzeige.md` und `analyse.md` existieren |
| `SEM-01` | semantisch | Beleg der Aussagen gegen die Datengrundlage (QS-4) |
| `SEM-02` | semantisch | Verantwortung und Seniorität sind belegt und nicht überhöht |
| `SEM-03` | semantisch | Relevanz für die Zielgruppe ohne Schlüsselwort- oder Score-Optimierung |
| `SEM-04` | semantisch | Sprache, Ton und Verständlichkeit |
| `SEM-05` | semantisch | die Aussagen stimmen über alle Dokumente überein |

Eine Regel, die die Grundlage braucht (CV-05, CV-06, CV-15, CV-16, CV-19, CV-20, CV-22, CV-23, BR-02 bis BR-04, QS-01 für
fremde Arbeitgeber, QS-03, SEM-01), ist ohne sie `BLOCKED`, nicht `PASS`.

## QS-4 Beleg: Aussagen gegen die Datengrundlage

Jede Aussage über die Person fällt in einen von vier Fällen. Der Fall wird gegen die Grundlage entschieden, nie allein durch
Wortüberschneidung; ein Urteil nennt Zitat und Beleg.

| Fall | Bedeutung | Ergebnis |
|---|---|---|
| A | Die Grundlage nennt es. | `PASS`, wenn Zitat und Beleg wörtlich sind und die Sicherheit hoch ist |
| B | Aus der Grundlage plausibel, aber nicht genannt. | `NEEDS_REVIEW`: ein Mensch bestätigt oder entfernt es |
| C | Die Grundlage widerspricht. | `FAIL` |
| D | Aus der Grundlage nicht prüfbar. | `NEEDS_REVIEW`; die Aussage bleibt „nicht verifiziert“ |

Die deterministischen Regeln (CV-xx, BR-xx) entscheiden die Fälle, die sie entscheiden können (Zahlen, Zeiträume,
Teamgrößen, Führung gegen das Kennzeichen `Führung:`). Sie machen aus einem Fall B nie einen Fall A.

## QS-5 Semantische Urteile eines Modells

1. Ein Modell schreibt `qualitaet-urteile.json`, nachdem es die Dokumente und die Grundlage gelesen hat. Die Datei ist Daten:
   gelesen werden nur die Felder `check`, `dokument`, `dokument_hash`, `ergebnis`, `sicherheit`, `zitat`, `evidenz`,
   `begruendung`.
2. `ergebnis` ist `A`, `B`, `C`, `D` für `SEM-01` und `ok`, `pruefen`, `fehler` für die übrigen. `sicherheit` ist `hoch`,
   `mittel` oder `niedrig`.
3. Ein Urteil zählt nur als `PASS`, wenn alles zutrifft: der `dokument_hash` gleicht dem Hash des Dokuments jetzt (bei
   `dokument: "*"` dem Hash des gesamten Satzes); das `zitat` steht wörtlich im Dokument; bei `SEM-01` steht die `evidenz`
   wörtlich in der Grundlage; die Sicherheit ist `hoch`; das Ergebnis ist `A` oder `ok`.
4. `B`, `D`, `pruefen`, eine geringe Sicherheit, ein Urteil einer älteren Version, ein nicht wörtliches Zitat oder ein nicht
   wörtlicher Beleg, ein für ein Dokument fehlendes Urteil, eine fehlende oder beschädigte Datei: `NEEDS_REVIEW`. `C` und
   `fehler`: `FAIL`.
5. Ohne Zugriff auf ein Modell gibt es die Datei nicht, und jede semantische Prüfung ist `NEEDS_REVIEW`. Der Bericht sagt dann
   `semantisch_geprueft: false`. Er wird nie als Erfolg dargestellt.
6. Dass ein Zitat wörtlich ist, prüft der Code; dass das Urteil stimmt, nicht. Das ist eine Grenze (QS-12), abgedeckt durch die
   Evals in `evals/` und durch die Durchsicht der Nutzerin oder des Nutzers.

## QS-6 Exportvalidierung und ATS-Lesbarkeit

1. Die Exportprüfungen laufen für jede Datei in `export/`, die ein Manifest `<datei>.manifest.json` hat (siehe Export-Skill).
2. Der Text des Exports wird zurückgelesen: PDF mit `pdftotext`, DOCX aus `word/document.xml`, HTML ohne Markup. Der Vergleich
   mit der Quelle ist der des Exporters (Wortmenge, Zeichen von Zahlenangaben, Reihenfolge).
3. Das PDF hat keine leere Seite und nicht mehr Seiten als das Limit (`EX-04`). Die Eigenschaften, von denen ein Parser abhängt, sind QS-13.
4. Ohne `pdftotext`, `pdfinfo`, `pdffonts` oder `pdfimages` sind die PDF-Prüfungen `BLOCKED` (die CI installiert poppler-utils).
5. **Grenze.** ATS-Lesbarkeit wird an der exportierten Datei und ihrem extrahierten Text beurteilt. Wie ein bestimmtes
   Bewerbermanagementsystem die Datei liest, ist weder getestet noch zugesagt. Farben, Ränder und der optische Eindruck werden nicht beurteilt.

## QS-7 Der Bericht

1. `qualitaet.json` enthält: `schema`, `regelwerk`, `erstellt`, `vorgang`, `stand`, `dokumente` (SHA-256 jedes Dokuments und
   jeder Kontextdatei), `exporte` (SHA-256 jeder Datei in `export/`), `grundlage_hash`, `gesamt`, `freigabefaehig`,
   `zusammenfassung` (Anzahl je Status), `ats` und `dimensionen` (QS-13), `semantisch_geprueft`, `checks` (jeweils mit `dimension`), `manuell` und `grenzen`.
2. Ein Bericht ist nur für genau diese Dateien aktuell. Ein geändertes, hinzugefügtes oder entferntes Dokument, eine
   Kontextdatei oder ein Export, oder eine geänderte Grundlage (wenn deren Hash vorliegt), macht ihn veraltet. Ein Bericht
   einer älteren Version wird nie wieder gültig. Der Status des Vorgangs ist keine Eingabe.
3. Der Bericht enthält Befunde mit höchstens 160 Zeichen Text, nie ein ganzes Dokument. `qualitaet-verlauf.jsonl` enthält je
   Lauf eine Zeile mit Zeit, Hash-Präfix, `gesamt` und den Zählern, keinen Text eines Dokuments.
4. Der Bericht liegt im Vorgangsordner, der privat ist (R-6). Er wird nicht in dieses Repository committet.

## QS-8 Manuelle Prüfung und Bestätigung

1. Eine `NEEDS_REVIEW`-Prüfung bestätigt nur die Nutzerin oder der Nutzer: `qualitaet.py entscheiden <vorgang> <check> --grund … --ja`.
   Die Bestätigung ist an die genauen Befunde und die genaue Version gebunden (`qualitaet-entscheidungen.json`); ein geändertes
   Dokument macht sie ungültig.
2. `FAIL` und `BLOCKED` lassen sich nicht bestätigen. Sie werden behoben oder ihre Ursache wird beseitigt.
3. Der Befehl wird ohne `--ja`, ohne Begründung und in einer unbeaufsichtigten Sitzung (`WORKFLOW_UNBEAUFSICHTIGT`,
   `STELLENSUCHE_GEPLANT`) abgelehnt.
4. Eine bestätigte Prüfung behält ihren Status `NEEDS_REVIEW` und erhält `manuell_akzeptiert: true`: der Bericht sagt, dass ein
   Mensch und nicht eine Prüfung sie geschlossen hat.

## QS-9 Das Gate im Workflow

1. Die Aufgabe `pruefung` ist erledigt, wenn `status` mindestens `geprüft` ist **und** `qualitaet.json` aktuell und `gesamt`
   freigabefähig ist (QS-2). Der Workflow fügt keinen Status hinzu; er liest den Bericht (`qualitaet.aktualitaet`).
2. Der Workflow vergleicht außerdem den `grundlage_hash` des Berichts mit der Datengrundlage jetzt (über den Anker). Eine
   geänderte Grundlage oder eine, die sich nicht hashen lässt, macht den Bericht veraltet (`qualitaet_veraltet`).
3. `workflow.py freigeben` der Aufgabe `versand_freigabe` wird andernfalls mit `qualitaet_fehlt`, `qualitaet_veraltet` oder
   `qualitaet_nicht_freigabefaehig` abgelehnt. Die Freigabe bleibt die ausdrückliche Entscheidung der Nutzerin oder des Nutzers
   über die genauen Dokumente (WF-7); der Bericht ist eine Voraussetzung, nie ein Ersatz.
4. Der Skill des Qualitätschecks führt zuerst `qualitaet.py pruefen` aus und setzt `geprüft` nur, wenn der Bericht
   freigabefähig ist.

## QS-10 Sicherheit und Datenintegrität

1. `qualitaet.py` sendet nichts und öffnet keine Netzwerkverbindung. Es importiert kein Mail-, HTTP- oder Socket-Modul und
   führt nur `pdftotext`, `pdfinfo`, `pdffonts` und `pdfimages` aus. Ein Test erzwingt das.
2. Ein bestandener Lauf löst keine externe Kommunikation aus und gibt nichts frei. Die Freigabe aus A-02
   (`versand_freigabe`) und der Versand selbst bleiben bei der Nutzerin oder dem Nutzer.
3. Der Lauf ändert kein Dokument und keinen Status. Er schreibt `qualitaet.json`, `qualitaet-verlauf.jsonl` und, auf Befehl
   der Nutzerin oder des Nutzers, `qualitaet-entscheidungen.json`.
4. Text einer Anzeige, einer Mail, eines Anhangs oder eines Urteils ist Daten. Er wird für Prüfungen gelesen und nie
   ausgeführt, nie als Regel, Status oder Freigabe genommen.

## QS-11 Automatisierung und CI

1. `task quality -- pruefen <vorgang-ordner> [--grundlage …]` führt die Prüfungen aus. `task test` führt die Tests der
   Werkzeugkette mit synthetischen Fixtures aus (`tests/test_qualitaet.py`); `ci.yml` führt sie einmal aus, mit installiertem
   poppler-utils.
2. Die Urteile eines Modells sind nicht Teil der CI: sie brauchen ein Modell und kosten Geld. Die Evals (`evals/`, Workflow
   `evals.yml`) bleiben manuell und getrennt. Eine grüne CI sagt, dass die Werkzeugkette funktioniert, nicht dass eine
   Bewerbung richtig ist.

## QS-12 Grenzen (ehrlich)

- Die deterministischen Prüfungen finden Widersprüche und fehlende Belege; ein `PASS` heißt „nichts gefunden“.
- Semantische Urteile werden nur auf Form und wörtliche Zitate geprüft.
- ATS-Lesbarkeit wird am extrahierten Text beurteilt, ohne Gewähr für ein bestimmtes System.
- Layout und optische Qualität, der Ton eines Briefes und die Passung zu einer Person sind Sache eines Menschen.
- Ohne die Grundlage, ein Modell oder poppler-utils sind die betroffenen Prüfungen `BLOCKED` oder `NEEDS_REVIEW`; die
  Werkzeugkette verbirgt das nicht.
- Der Bericht ist nicht manipulationssicher. Das Gate berechnet `gesamt` aus den gespeicherten Prüfungen neu und lehnt einen inkonsistenten Bericht ab, doch wer in den Vorgangsordner schreiben kann, kann einen konsistenten schreiben. Er ist eine Voraussetzung der Freigabe, keine Sicherheitsgrenze; die Freigabe bleibt das `--ja` der Nutzerin oder des Nutzers.
- `entscheiden` ist durch `--ja` und die Sperre für unbeaufsichtigte Sitzungen geschützt, nicht durch einen Kanal, den nur die Nutzerin oder der Nutzer hat. Der Skill verbietet dem Modell, es auszuführen.
- `--grundlage <Pfad>` sieht Dateien an und bindet keinen Grundlage-Hash; nur ein Lauf über den Anker (`--konfiguration`) tut das.
- Der Bericht ist veraltet, sobald sich eine Datei ändert; vor der Freigabe führt die Nutzerin oder der Nutzer die Prüfung
  erneut aus.

## QS-13 Technische ATS-Validierung

`scripts/ats_checks.py` ist eine Bibliothek von `qualitaet.py`. Sie ergänzt den einen Bericht um Eigenschaften der exportierten
Datei; sie hat kein eigenes Statusmodell, keinen Score und keinen eigenen Ablauf.

1. **Definition.** Ein Dokument gilt als *technisch ATS-validiert*, wenn `EX-01` bis `EX-04` und `ATS-01` bis `ATS-05` für seinen
   Export gelaufen und mit `PASS` oder `WARNING` geendet sind. Das ist keine Zusage für ein externes Bewerbermanagementsystem und
   keine Aussage über die Eignung der Person. Bericht und Skills sagen das.
2. **Umfang.** Die Prüfungen laufen für Exporte in Formaten, die ein Parser liest (`pdf`, `docx`, `html`). `md` und `tex` sind
   Kopien der Quelle: ohne Export in einem der drei Formate sind die `ATS-xx`-Prüfungen `NOT_APPLICABLE`, nie `PASS`.
3. **Datei (`ATS-01`).** PDF: Kopf und Dateiende, von `pdfinfo` lesbar, kein Kopierverbot für Text (Blocker); Schriften vom Typ 3
   oder nicht eingebettete Schriften (außer den Standard-14) sind eine `WARNING`. DOCX: unversehrtes Archiv, `document.xml` und
   Content-Types vorhanden und wohlgeformt (Blocker); versteckter Text (`vanish`), weißer Text oder Text von 2 pt und weniger ist ein Blocker.
4. **Text (`EX-03`).** Mindestens 30 Wörter in PDF und DOCX, kein Ersatzzeichen und kein `(cid:`, beides Blocker; Ligaturzeichen
   und gesperrte Wörter sind eine `WARNING`.
5. **Abschnitte (`ATS-02`).** Für PDF und DOCX steht jede Überschrift der Ebene 1 und 2 als eigene Zeile im extrahierten Text
   (sonst `WARNING`), und mindestens 80 % der Wörter ihres Abschnitts stehen zwischen ihr und der nächsten Überschrift. Die
   DOCX-Überschriftenformate je Ebene entsprechen denen der Quelle. Die Überschriften stammen aus der Quelle; kein Wortlaut ist vorgegeben.
6. **Stationen und Zeiträume (`ATS-03`).** Die Zeiträume der Quelle (`MM/JJJJ – MM/JJJJ`, `JJJJ – JJJJ`, `heute`) stehen in
   derselben Reihenfolge im extrahierten Text; ein verlorener, veränderter oder vertauschter Zeitraum ist ein Blocker. Zu jeder
   Stationszeile stehen Position und Arbeitgeber binnen drei Zeilen beim Zeitraum (`WARNING`). Gemischte Datumsformate in der Quelle sind
   eine `WARNING`. Fehlende Zeiträume werden nicht erfunden; ob ein Zeitraum stimmt, prüfen `CV-xx` und die Grundlage.
7. **Kontakt (`ATS-04`).** Jede E-Mail-Adresse und Telefonnummer der Quelle ist im extrahierten Text lesbar (Blocker bei Verlust,
   mit Hinweis, wenn sie nur in Kopf- oder Fußzeile eines DOCX steht). Ein Lebenslauf ohne E-Mail-Adresse ist eine `WARNING`; ein
   fehlender optionaler Punkt ist kein Befund. Befunde enthalten nie die Adresse oder die Nummer.
8. **Layout (`ATS-05`).** Tabellen, Bilder (auch im PDF, `pdfimages`), Textfelder, Spalten (DOCX-Abschnitte; PDF nach der Lage
   der Wörter), Text in Kopf- und Fußzeile, Wörter außerhalb der Seite: `WARNING`. Eine Bewertung nur als Symbolreihe (Sterne,
   Punkte, Balken) ist `NEEDS_REVIEW`: das Niveau muss ein Wort sein, und die Toolchain ergänzt es nicht. Die Spaltenerkennung ist
   eine Heuristik: die Lesereihenfolge selbst prüft `EX-02`.
9. **Schlüsselbegriffe (`KW-01`).** Die Kompetenzen aus `analyse.md` gegen den Lebenslauf. Eine belegte Kompetenz, die der
   Lebenslauf nicht nennt, ist eine `WARNING`. Eine Kompetenz, die die Analyse als `nicht belegt` oder `unklar` zeigt und die im
   Lebenslauf steht, ist `NEEDS_REVIEW`: ein Wort der Anzeige ist keine Qualifikation. Es wird nichts eingefügt und nichts in
   einen Score gerechnet; Wiederholung bleibt Befund von `QS-04`.
10. **Dimensionen.** Jede Prüfung hat eine `dimension` (`technisch`, `evidenz`, `formal`, `schluesselbegriffe`, `passung`), der
    Bericht zählt je Dimension. `ats.umfang` ist `vollstaendig`, `teilweise` oder `nicht_geprueft`; `ats.technisch_validiert` ist nur
    bei vollständigem Lauf ohne `FAIL`, `BLOCKED` oder offene Prüfung wahr. Es gibt keinen Gesamtscore: ein kritischer Befund wird nie weggemittelt.
11. **Versionen.** Die Prüfungen gehören zu den Hashes des Berichts (QS-7). Ein geänderter Export wird neu geprüft; die Zeile des
    alten Laufs bleibt in `qualitaet-verlauf.jsonl`.
12. **Kein Modell.** Alle Prüfungen von QS-13 sind deterministisch. Der semantische Teil (Relevanz, Beleg) bleibt bei `SEM-xx`.
13. **Nicht abgedeckt.** Überlagerte Elemente, innerhalb der Seite abgeschnittener Text, unschöne Seitenumbrüche, genaue Farben
    und das Verhalten eines bestimmten Bewerbermanagementsystems. Das Layout sieht ein Mensch an.
