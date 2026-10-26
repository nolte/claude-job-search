# Nachverfolgung und Lernen

Nachdem du eine Bewerbung gesendet hast, führt `job-application-follow-up` den Verlauf weiter: Rückmeldungen gelangen als Vorschläge in den
Vorgang, die du freigibst, Wiedervorlagen erinnern dich, und die bestätigten Ergebnisse vieler Bewerbungen werden zu Kennzahlen und einer
Retrospektive. Zwei kleine Skripte erledigen das, `scripts/kommunikation.py` und `scripts/lernen.py`; beide lesen und schreiben nur Dateien in
deiner Wurzel. Die Regeln stehen in `spec/job-application/mail-verwaltung/en.md` (MV-18 bis MV-27) und
`spec/job-application/ergebnisauswertung/en.md` (EA-1 bis EA-16).

## Was es tut und was nicht

| Teil | Wer | Stand |
|---|---|---|
| Eine Antwort lesen, die du übergibst (JSON-Liste oder eingefügter Text), einem Vorgang zuordnen, den Mailtyp benennen | das Skript, nach festen Regeln | funktioniert; **es wird kein Postfach gelesen**, du übergibst die Mail |
| Die Zeile für `## Verlauf`, die Statusänderung, das Ergebnis und eine Wiedervorlage vorschlagen | das Skript | funktioniert; es wird noch nichts geschrieben |
| Sie schreiben | du gibst den genauen Vorschlag frei (`bestaetigen --hash … --ja`) | bewusst nie automatisch |
| Unklare oder nicht zugeordnete Mail, unbekannter Mailtyp | du entscheidest (`zuweisen`) | wird nie geraten |
| Wiedervorlage und Grundlage eines Nachfassens | das Skript; das Datum ist deins | funktioniert; eine Wiedervorlage sendet nie |
| Die Nachfass-Mail selbst | `job-application-email-create`, danach deine Freigabe im Workflow | funktioniert als geprüfter Entwurf |
| Senden, Gmail lesen, Kalender | niemand | **nicht integriert**: kein Connector, kein Versandadapter |
| Statistik, Retrospektive, Vorschläge | das Skript, aus bestätigten Ergebnissen | funktioniert; abgeleitet, nie die Quelle |

Der Status bleibt `status` in `vorgang.md`; der Versand (S7) bleibt deine Aussage. Es wird nichts gesendet und keine Mail im Volltext gespeichert.

## Rückmeldungen verarbeiten

```bash
python3 <plugin>/scripts/kommunikation.py verarbeiten --nachrichten eingang.json   # oder: task communication -- verarbeiten …
python3 <plugin>/scripts/kommunikation.py liste --status vorgeschlagen
python3 <plugin>/scripts/kommunikation.py zeige <id>                                # der Vorschlag, wie er jetzt ist, mit Hash
python3 <plugin>/scripts/kommunikation.py bestaetigen <id> --hash <hash> --ja       # schreibt genau, was zeige gezeigt hat
```

Eine Nachricht hat `id`, `thread_id`, `von`, `betreff`, `datum`, `text` und `anhaenge`. Sie wird über Referenznummer, Absenderdomain, Thread,
Firmenname und Stellenbezeichnung zugeordnet. Kommen zwei Vorgänge infrage, wird nichts zugeordnet: Du siehst beide mit ihren Gründen und wählst
(`zuweisen <id> --vorgang … --typ …`), danach bestätigst du den neuen Vorschlag. Ein Vorschlag trägt eine Gewissheit: `eindeutig`,
`wahrscheinlich`, `unklar` oder `nicht_zuordenbar`. Ein Hash bindet deine Freigabe an die genauen Zeilen; ändert sich der Status des Vorgangs
dazwischen, ändert sich der Hash, und du schaust neu hin. Ergebnis ist eine Zeile in `## Verlauf`, optional eine Statusänderung (nur vorwärts, nur
nach `versendet`), ein Ereignis in `<vorgang>/nachverfolgung.json` und, wenn du ein Datum nennst, eine Wiedervorlage.

Gespeichert werden: Referenzen (Nachrichten-ID, Thread), die Absenderdomain, ein kurzes wörtliches Zitat (höchstens 240 Zeichen, Beträge
entfernt) und die Anhangnamen. Kein Volltext, keine Adresse, keine Gehaltszahl.

## Wiedervorlage und Nachfassen

```bash
python3 <plugin>/scripts/kommunikation.py wiedervorlage anlegen <vorgang> --anlass nachfassen --faellig 2026-11-10
python3 <plugin>/scripts/kommunikation.py nachfass <vorgang> --nach-tage 14
```

Eine fällige Wiedervorlage wird zu einer Aufgabe für dich (`workflow.py laufen`). `nachfass` sagt, ob ein Nachfassen sinnvoll ist: gesendet, keine
inhaltliche Rückmeldung, nichts wartet auf die Prüfung und **eine Frist, die du gesetzt hast** (`--nach-tage`, `nachfass_tage` in
`konfiguration.md` oder `wiedervorlage` in `vorgang.md`). Ohne Frist fragt es dich; es gibt keinen Standardwert. Den Entwurf schreibt
`job-application-email-create`; vor jedem Versand siehst du Nachricht, Empfänger und Vorgang und gibst die genaue Datei im Workflow frei.

## Ergebnisse und Auswertung

```bash
python3 <plugin>/scripts/lernen.py statistik --von 2026-10-01 --nach zeitraum      # oder: task learn -- statistik …
python3 <plugin>/scripts/lernen.py retrospektive
python3 <plugin>/scripts/lernen.py vorschlaege erzeugen
```

| Kennzahl | So wird gezählt |
|---|---|
| Rücklaufquote | Bewerbungen mit bestätigter, inhaltlicher Rückmeldung / alle versendeten Bewerbungen im Zeitraum. **Offene Bewerbungen bleiben im Nenner** und werden getrennt ausgewiesen; `ruecklaufquote_ohne_offene` lässt sie weg |
| Übergänge | Bewerbung zu Rückmeldung, zu Einladung; Einladung zu weiterer Phase und zu Angebot; Bewerbung zu Einstellung |
| Antwortzeiten | Tage von `versendet_am` bis zu einem datierten Ereignis; ein Ereignis ohne Datum wird gezählt, nie geschätzt |
| Segmente | nach Arbeitgeber, Monat, Kanal, Quelle, Ausrichtung, Profil, Dokumentversion, Passungsurteil; eine Gruppe unter 5 gilt als nicht vergleichbar |

Es zählen nur bestätigte Ergebnisse: Ein Vorschlag ist kein Ergebnis, und eine noch nicht geprüfte Nachricht steht unter `datenqualitaet`. Eine
Kennzahl, die nur auf dem Status beruht, wird als solche gezeigt. Ein Nenner unter 5 ist eine Momentaufnahme. Die Retrospektive nennt ihre
Grundlage (Zeitraum, ausgewertete und offene Vorgänge, Ausschlüsse) und ist veraltet, sobald sich eine Quelle ändert (`aktualitaet`). Ein Vorgang
mit abgelaufenem `loeschen_ab` fällt aus den Zahlen.

**Was die Auswertung nicht sagt.** Sie sagt nicht, warum eine Bewerbung scheiterte. Eine Absage ohne genannten Grund ist „Grund unbekannt“ und
ergibt keine Schwäche von dir oder der Unterlagen. Ein genannter Grund ist ein Hinweis mit niedriger Sicherheit, bis du ihn bestätigst. Ein Thema in
zwei Absagen ist „in zwei Vorgängen genannt“, keine Ursache. Eine bestandene Qualitätsprüfung beweist keinen Erfolg, eine Absage keine fehlerhaften
Unterlagen; der Qualitätsstatus ist nicht Teil einer Quote.

**Vorschläge.** Regeln erzeugen Vorschläge (ein genannter Grund in zwei Vorgängen, Vorgänge ohne nachweisbare Dokumentversion, ungeprüfte
Nachrichten, Bewerbungen ohne Antwort nach deinem `nachfass_tage`). Jeder hat Quellen, Begründung, Wirkung, Risiko und Unsicherheit. Du lässt ihn
dir vorlegen (`vorlegen`) und entscheidest mit `--ja`. Die Annahme ändert **keine Datei**: Datengrundlage und `profil.md` änderst nur du, in
`job-application-cv-maintain`, mit Beleg.

## Grenzen

- Es werden weder ein Gmail-Connector noch ein Versandadapter mitgeliefert; die Schnittstelle ist die JSON-Liste und die Freigabeaufgabe `nachricht_senden`.
- Mailtypen und Gründe werden an festen deutschen Mustern erkannt; ungewöhnlicher Wortlaut ist `unbekannt` und braucht deine Entscheidung.
- Die Dokumentversion eines Vorgangs ist nur mit aktuellem `qualitaet.json` und genannten Anhängen in `vorgang.md` eindeutig.
- Läufe starten, wenn du es verlangst; das Plugin richtet keinen Timer ein.
