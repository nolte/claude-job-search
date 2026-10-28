# Nachverfolgung und Lernen

Nachdem du eine Bewerbung gesendet hast, führt `job-application-follow-up` den Verlauf weiter: Rückmeldungen gelangen als Vorschläge in den
Vorgang, die du freigibst, und Wiedervorlagen erinnern dich. `job-application-result-evaluate` macht aus den bestätigten Ergebnissen vieler
Bewerbungen Kennzahlen und eine Retrospektive. Zwei kleine Skripte erledigen das, `scripts/kommunikation.py` und `scripts/lernen.py`; beide
lesen und schreiben nur Dateien in deiner Wurzel. Die Regeln stehen in `spec/job-application/mail-verwaltung/en.md` (MV-18 bis MV-27) und
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

Der Skill für diesen Teil ist `job-application-result-evaluate`; er liest, was die Nachverfolgung gespeichert hat, und schreibt nur unter `lernen/`.

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

## Nachrichten von Arbeitgebern: Import, Angaben, Antwortentwürfe (R-02)

Spec: `spec/job-application/mail-verwaltung/en.md` MV-28 bis MV-36. **Nichts hiervon sendet eine Nachricht an einen Arbeitgeber.** Es gibt keinen Gmail-Connector und keinen Versandadapter.

**Import.** Speichere Mails als `.eml`-Dateien und starte `task mail-import -- <Ordner> > nachrichten.json`, danach `task communication -- verarbeiten --nachrichten nachrichten.json`. Der Import liest nur Dateien. Die Kennung ist die `Message-ID`
(oder ein stabiler Hash, wenn es keine gibt), eine Mail ohne gültigen `Date`-Header wird nicht importiert, Anhänge werden nie geöffnet oder gespeichert (ein riskanter Dateityp steht als gesperrt in der Liste), und eine Datei, die sich nicht lesen lässt, wird mit
Klasse und ohne Inhalt gemeldet. Dieselbe Mail zweimal ist ein Datensatz. `verarbeiten --erneut` liest Nachrichten, die nur vorgeschlagen sind, noch einmal (etwa nach einem neuen Vorgang) und behält deine manuelle Zuordnung.

**Typen und Angaben.** Neben Einladung, Angebot, Absage, Rückfrage und Eingangsbestätigung kennt das Skript Terminvorschlag, -bestätigung, -verschiebung und -absage, Bitte um Unterlagen, Eingang von Unterlagen, Zwischenstand und Rückfrage zum Angebot. Passen zwei Typen,
wird nicht geraten: nur in den aufgelisteten Fällen gewinnt der speziellere, sonst entscheidest du. Das Skript liest außerdem Termin, Frist, Format, Kontaktperson, angeforderte Unterlagen und Referenznummer mit dem Satz, aus dem sie stammen. Ein Datum ohne Jahr, eine Uhrzeit
ohne Zeitzone oder „nächsten Dienstag“ ist `unsicher` und wird nie in ein Datum umgerechnet. Nichts wird von selbst übernommen:

```bash
task communication -- bestaetigen m1 --hash <hash> --ja --uebernehmen termin,kontakt_name --frist-aus-nachricht --termin-aus-nachricht
```

Eine `unsicher`e Angabe braucht `--trotz-unsicherheit`. Eine Frist, die der Arbeitgeber nennt, wird eine Wiedervorlage mit `arbeitgeber_frist`; ein vom Arbeitgeber vorgeschlagener Termin wird dein eigener Planungspunkt, markiert als noch nicht zugesagt.
Bei einer unklaren Nachricht zeigt `zeige`, was offen ist.

**Antwortentwürfe.** Nur für eine Nachricht, deren Zuordnung du bestätigt hast.

```bash
task reply -- anlegen m1 --an personal@musterfirma.example --vorlage termin_bestaetigen    # oder --text-datei antwort.txt
task reply -- zeige musterfirma-backend antwort-01.md       # Zustand, Text, offene Punkte, Versionen
task reply -- aendern musterfirma-backend antwort-01.md --text-datei neu.txt    # eine neue Version
task reply -- vorlegen musterfirma-backend antwort-01.md    # danach: task workflow -- starten / laufen
task workflow -- freigeben nachricht_senden:musterfirma-backend:antwort-01.md --ja
```

Eine Vorlage nutzt nur Angaben, die du übernommen hast; alles andere bleibt `[ERGÄNZEN: …]` (deine Antwort, deine Verfügbarkeit, dein Name), und ein Entwurf mit offener Stelle lässt sich nicht vorlegen. Den Empfänger gibst du selbst an; es ist genau eine Adresse auf der Domain
des Absenders, außer du sagst `--abweichender-empfaenger`. Die Freigabe im Workflow gilt für die ganze Entwurfsdatei: Eine Änderung an Text, Empfänger, Betreff oder Kanal macht sie ungültig. Zustände: `entwurf`, `wartet_auf_freigabe`, `freigegeben`, `abgelehnt`, `gesendet`,
`versand_fehlgeschlagen`, `versand_unklar`, `verworfen`. Jeder Schritt steht als Ereignis (`antwort_*`) im Verlauf des Vorgangs.

**Senden.** Ohne Adapter antwortet `workflow.py ausfuehren` mit `kein_adapter`, und ein freigegebener Entwurf bleibt ein freigegebener Entwurf. `antwort.adapter(wurzel, anbieter)` ist die abgesicherte Funktion, die eine Anbindung registrieren kann: Sie sendet nur die freigegebene
Datei, genau einmal, und meldet Erfolg nur mit einer Kennung des Anbieters. Getestet ist sie nur mit einem simulierten Anbieter; eine echte Mail-Anbindung (OAuth mit dem engsten Umfang, Geheimnisse außerhalb des Repositorys) baust und prüfst du selbst.

### Trichter, Quoten, Zeiten und Retrospektive (R-03)

Spec: `spec/job-application/ergebnisauswertung/en.md` EA-17 bis EA-24. Die Auswertung liest, was R-01 und R-02 schon speichern; sie führt keine zweite Datenhaltung, ändert keine Daten, schreibt nur unter `lernen/` und **sendet nichts**.

```bash
task learn -- statistik --reife-tage 28 --kanal portal            # Trichter, Konversionen, Zeiten; Filter: --kanal --quelle --titel --ergebnis --bewertung --dokumentversion ...
task learn -- erklaere eingereicht_zu_rueckmeldung                 # die Vorgänge hinter Zähler und Nenner
task learn -- retrospektive                                        # A Zusammenfassung, B Prozess, C Reaktionen, D Verbesserungen
task learn -- vorschlag pruefe <id>                                # nach deiner Annahme: hat sich die Kennzahl bewegt?
```

- **Trichter:** recherchierte und relevante Stellen (aus der Warteschlange), begonnen, Unterlagen fertig, freigegeben (Workflow), eingereicht, Eingang bestätigt, Antworten, Absagen, Einladungen, geführte Gespräche, Angebote, angenommen, abgelehnt, zurückgezogen. Die Stufen bleiben getrennt: Eine fertige
  Bewerbung ist nicht eingereicht, eine Einladung ist kein geführtes Gespräch, keine Antwort ist keine Absage. Eine Quelle, die es nicht gibt, steht als „nicht erfasst“, nicht als 0.
- **Quoten** tragen Zähler, Nenner, ein 95-%-Intervall und eine Kennzeichnung für kleine Stichproben (unter 5). `reif` wiederholt jede Quote für Bewerbungen, die mindestens `--reife-tage` (Standard 28) alt sind, und zählt jüngere getrennt: Eine frische Bewerbung gilt so nicht als unbeantwortet.
- **Zeiten** (Entdeckung bis Beginn, Beginn bis fertig, fertig bis Einreichung, Einreichung bis erste Antwort, Einladung, Ergebnis; Einladung bis Gespräch; Gespräch bis Antwort) nutzen nur gespeicherte Daten des Ereignisses. Ein fehlender Start wird getrennt gezählt und nie ergänzt.
- **Nicht erfasst:** Seniorität, Branche, Standort und Arbeitsmodell haben kein Feld; sie stehen als nicht erfasst da und lassen sich nicht filtern.
- **Retrospektive:** vier Teile, jede Zeile in Teil B als Prozess oder Datenlücke gekennzeichnet, Absagegründe mit Herkunft (Wortlaut des Arbeitgebers, deine eigene Einschätzung oder ein vom System vermutetes Muster) und Teil D mit den Vorschlägen und den noch fehlenden Daten.
- **Vorschläge** haben zusätzliche Regeln für begonnen-nicht-fertig, fertig-nicht-eingereicht, begonnen trotz Veto, wiederkehrende Befunde der Qualitätsprüfung und Ergebnisse nur im Status. Jeder nennt Beobachtung, betroffene Vorgänge, mögliche Erklärung, Unsicherheit, Empfehlung und wie sich die Wirkung prüfen lässt.
  Du entscheidest mit `--ja`; die Annahme ändert keine Datei. `vorschlag pruefe` vergleicht die Kennzahl mit ihrem damaligen Wert und sagt, wenn die Daten nicht reichen; er behauptet nie, eine Änderung habe einen Unterschied verursacht.

Grenzen: nur mit erfundenen Daten getestet; die Aufzeichnungen der interaktiven Suche zählen nicht als recherchiert; Seniorität und Branche sind nicht erfasst; eine durch ein geändertes Dokument ungültig gewordene Freigabe ist im Workflow-Speicher nicht mehr sichtbar.

## Grenzen

- Es werden weder ein Gmail-Connector noch ein Versandadapter mitgeliefert; die Schnittstelle ist die JSON-Liste und die Freigabeaufgabe `nachricht_senden`.
- Mailtypen und Gründe werden an festen deutschen Mustern erkannt; ungewöhnlicher Wortlaut ist `unbekannt` und braucht deine Entscheidung.
- Die Dokumentversion eines Vorgangs ist nur mit aktuellem `qualitaet.json` und genannten Anhängen in `vorgang.md` eindeutig.
- Läufe starten, wenn du es verlangst; das Plugin richtet keinen Timer ein.

## Das Ergebnis einer Bewerbung

`scripts/bewerbung.py` (`task result -- …`, Regeln `spec/job-application/bewerbungsergebnis/en.md` BE-1 bis BE-17) beantwortet, wie eine Bewerbung steht, was wann geschah und was fehlt. Es
legt keine zweite Datenhaltung an: Die Bewerbung ist der Vorgangsordner, der Status bleibt `status` in `vorgang.md`, und die Ereignisse sind die Datei `nachverfolgung.json`, die auch die
Rückmeldungsverarbeitung schreibt.

| Frage | Befehl |
|---|---|
| Eine Bewerbung finden, auch eine abgeschlossene | `bewerbung.py finde --firma Musterfirma` · `finde --abgeschlossen` · `finde --ergebnis ohne_entscheidung_abgeschlossen` |
| Wie steht sie? | `bewerbung.py status <vorgang>`: Status, Phase, Ergebnis (bekannt oder nicht), Versand, Dokumentversionen, offene Aufgaben, Unbekanntes |
| Was geschah wann? | `bewerbung.py historie <vorgang>`: nach dem Tag des Ereignisses, mit dem Tag der Erfassung |
| Eine Tatsache erfassen | `bewerbung.py ereignis erfassen <vorgang> --art versendet --eingetreten-am 2026-10-02 --kanal email --status-aendern --ja` |
| Den Status ändern | `bewerbung.py statuswechsel <vorgang> --nach abgeschlossen --grund "…" --ja` |
| Ein Ereignis korrigieren oder verwerfen | `bewerbung.py ereignis korrigieren <vorgang> --id e-002 --datum 2026-10-03 --grund "…" --ja` · `ereignis verwerfen …` |
| Was steht an? | `bewerbung.py naechste [<vorgang>]`: Erinnerungen, zu prüfende Nachrichten, fehlende Angaben |
| Sind die Daten stimmig? | `bewerbung.py pruefen [<vorgang>]` (liest nur) |
| Ältere Daten übernehmen | `bewerbung.py migrieren` (Probelauf), dann `migrieren --ja` |
| Eine Bewerbung, die außerhalb des Plugins entstand | `bewerbung.py anlegen --firma … --stelle … --ja` |

**Status, Phase, Ergebnis.** Der Status sagt, wo die Bewerbung im Lebenszyklus steht. Die Phase sagt dasselbe in Klartext (eingereicht, Eingang bestätigt, Gespräch vereinbart, Angebot, …). Das Ergebnis
ist, wie sie ausging, und es ist nur *bekannt*, wenn dein Status oder ein bestätigtes Ereignis es sagt. Eine Eingangsbestätigung ist keine Rückmeldung, eine Einladung kein Angebot, ein angenommenes
Angebot noch keine Einstellung, eine zurückgezogene Bewerbung keine Absage, und eine abgeschlossene (`abgeschlossen`, `ohne Antwort`) weder Erfolg noch Misserfolg.

**Zulässige Wechsel.** Eine Tabelle (BE-3): nach dem Versand nur vorwärts; eine Absage nur nach dem Versand; `zusage` und `abgelehnt` nur aus einem Angebot; `zurückgezogen` und `abgeschlossen` aus jedem
offenen Status; ein Endstatus wird nicht verlassen. `abgeschlossen` ist neu: Du hörst auf, an der Bewerbung zu arbeiten, und nennst keine Entscheidung des Arbeitgebers.

**Ereignisse.** Sie tragen den Tag des Geschehens (`eingetreten_am`, leer wenn unbekannt), den Tag der Erfassung (`erfasst`), die Quelle und eine Gewissheit (`bestaetigt`, `automatisch`, `unsicher`). Dieselbe
Tatsache zweimal erfasst wird einmal gespeichert. Eine gefundene, aber unsichere Tatsache wartet auf `ereignis bestaetigen` und ändert vorher nichts. Ein Versand braucht seinen Tag; er wird nie eingesetzt.

**Erinnerungen.** Ein Datum ist deine eigene Planung, außer der Arbeitgeber hat es genannt (`--arbeitgeber-frist`). Eine Erinnerung ist eine Aufgabe für dich und sendet nichts. Nichts in diesem Skript sendet oder
beantwortet eine Nachricht, und keine Freigabe für eine frühere Nachricht gilt für eine neue.

**Ältere Daten.** `migrieren` ergänzt die neuen Felder bei älteren Ereignissen und leitet nur ein `versendet`-Ereignis und `statuswechsel`-Ereignisse aus dem ab, was `vorgang.md` nennt. Es leitet keine Absage und
kein Ergebnis ab, schätzt kein Datum und ändert weder `vorgang.md` noch deine Notizen. Ein zweiter Lauf findet nichts.

Offen: Der Hash der tatsächlich versendeten Dateien wird beim Versand nicht gespeichert; die Dokumentversion ist daher nur so genau wie der letzte Qualitätsbericht (BE-15).
