# Workflow

Der Workflow behält über Sitzungen und Neustarts hinweg die Reihenfolge der Bewerbungsschritte, was jeder Schritt braucht, was
erledigt ist, was auf dich wartet und was fehlgeschlagen ist. Er besteht aus einem kleinen Hilfsskript, `scripts/workflow.py`,
und einer Datei in deiner Wurzel. Er ist **kein** Server und kein Hintergrundprozess und führt die Skills nicht für dich aus.

Die Regeln stehen in `spec/job-application/workflow/en.md` (WF-1 bis WF-14). Diese Seite erklärt die Bedienung.

## Was er tut und was nicht

| Schritt | Wer macht es | Stand der Funktion |
|---|---|---|
| Schritte planen, prüfen was bereit ist, nach Frist und Priorität ordnen | das Skript | funktioniert; läuft, wenn **du** es aufrufst oder planst |
| Analyse, Passung, Unterlagen, Qualitätscheck, Nachfass-Entwurf, Suche | ein Agent mit dem Skill, vom Workflow vorbereitet | funktioniert als Übergabe: Der Agent übernimmt die Aufgabe und meldet zurück; das Skript prüft das Ergebnis in deinen Dateien |
| Plan-Freigabe (S3), Versand (S7), Einträge zu Rückmeldungen (S8) | du | der Workflow beobachtet deine Dateien und hält, was folgt |
| Freigabe der genauen Unterlagen zum Versand | du | funktioniert (`freigeben --ja`), an den Inhalt gebunden |
| Versand durch das Programm, Mail, Kalender | noch niemand | **nicht integriert**: Es wird kein Versandadapter mitgeliefert (die Mail-Funktionen von A-02 sind nur spezifiziert) |
| Von selbst nach Zeitplan laufen | dein Cron oder Timer | **vom Plugin nicht eingerichtet** (siehe unten) |

Der Bewerbungsstatus bleibt in `vorgang.md`. Der Workflow schreibt nie in einen Vorgang und führt keinen zweiten Status.

## Kurz, wie es funktioniert

- Ein Vorgang bekommt eine Kette von Aufgaben: `analyse`, `passung` (nur mit bestätigtem Wunschprofil), `plan`, `unterlagen`,
  `pruefung`, `versand_freigabe`, `versand`. Jede Aufgabe hat einen Status (`wartend`, `bereit`, `laeuft`,
  `wartet_auf_freigabe`, `wartet_auf_eingabe`, `wiederholung_geplant`, `erledigt`, `fehlgeschlagen`, `blockiert`,
  `abgebrochen`).
- Eine Aufgabe ist **erst erledigt, wenn ihr Ergebnis in deinen Dateien steht** (zum Beispiel gibt es `analyse.md` und der
  `status` ist mindestens `analysiert`). Hast du oder ein Skill den Schritt außerhalb des Workflows erledigt, merkt die nächste
  Prüfung das und schließt die Aufgabe.
- Ein fehlgeschlagener Schritt gibt den nächsten nie frei: Die folgenden Aufgaben sind `blockiert` und nennen den Grund.
- Für jeden freigegebenen, aktiven und fälligen Suchauftrag entsteht eine Suchaufgabe, und eine Nachfass-Aufgabe, wenn die
  `wiedervorlage` einer versendeten Bewerbung erreicht ist. Aus dem Text einer Anzeige entstehen nie Aufgaben.

## Einrichten

Es ist nichts zu installieren. Der Ordner `workflow/` entsteht bei der ersten Benutzung in deiner Wurzel. Wie `suche/` enthält
er persönliche Daten und gehört nur in ein privates Repository.

```bash
# im Arbeitsordner (dem mit job-application/konfiguration.md)
python3 <plugin>/scripts/workflow.py laufen          # oder: task workflow -- laufen
```

## Beispiele

1. **Workflow für einen Vorgang starten:** `workflow.py starten musterfirma-backend`. Es legt die Kette an; nur der erste Schritt
   ist bereit.
2. **Sehen, was als Nächstes ansteht:** `workflow.py naechste`, oder `workflow/uebersicht.md` im Vault öffnen. Die Übersicht
   nennt, was für einen Agenten bereit ist, was für dich bereit ist, was auf deine Freigabe oder auf Angaben wartet, was
   fehlgeschlagen und was überfällig ist.
3. **Ein Agent erledigt einen Schritt:** Claude ruft `uebernehmen analyse:musterfirma-backend` auf (die Antwort nennt eine
   Versuchsnummer), arbeitet mit dem genannten Skill und meldet `fertig analyse:musterfirma-backend --versuch 1` (die Versuchsnummer ist Pflicht, damit eine veraltete Sitzung nicht den Versuch ihres Nachfolgers beendet). Steht das
   Ergebnis nicht in den Dateien, zählt das als fehlgeschlagener Versuch und wird nach 5, 30 und 180 Minuten wiederholt,
   höchstens dreimal. Braucht der Agent etwas von dir (Angaben, eine Freigabe, eine Berechtigung), meldet er `fehler ... --klasse
   eingabe` (oder `freigabe`, `berechtigung`, `qualitaet`): Die Aufgabe wartet dann, bis du `workflow.py weiter <aufgabe>` aufrufst.
4. **Unterlagen zum Versand freigeben:** nach dem Qualitätscheck `workflow.py freigeben versand_freigabe:musterfirma-backend
   --ja`. Ist ein Dokument nach `pruefbericht.md` geändert worden, wird die Freigabe abgelehnt (`pruefung_veraltet`): erst den
   Qualitätscheck erneut ausführen. Exit-Code 2 heißt: Der Befehl lief, meldet aber `ok: false` (etwa `fertig` ohne Ergebnis); 3
   ist eine Ablehnung. Die Freigabe gilt genau für die Unterlagen, wie sie jetzt sind. Änderst du eine, verfällt sie und der Versandschritt
   ist wieder gehalten. Das Senden ist deins: Du sendest und trägst `versendet` und `versendet_am` in `vorgang.md` ein; die
   nächste Prüfung schließt `versand`.
5. **Einen Fehler untersuchen:** `workflow.py zeige <aufgabe>` zeigt Versuche, Fehlerklasse, Grund und Verlauf. `workflow.py
   wiederholen <aufgabe>` lässt eine fehlgeschlagene Aufgabe neu versuchen.
6. **Abbrechen:** `workflow.py abbrechen musterfirma-backend` beendet alle offenen und fehlgeschlagenen Aufgaben dieses Vorgangs.
   Eine abgebrochene oder fehlgeschlagene Suchaufgabe wird nicht von selbst ersetzt; `laufen` nennt sie unter `nicht_ersetzt`
   (mit `wiederholen` neu versuchen oder den Suchauftrag pausieren). Eine Aufgabe mit unklarem Ausgang einer Sendung wird nicht
   abgebrochen; erst mit `ausgang` entscheiden. `laufen` entfernt erledigte Suchaufgaben nach 30 Tagen (`aufgeraeumt`).
7. **Grenzen:** `workflow.py grenzen` zeigt sie, `workflow.py grenzen laufende_max=1 neu_max_je_lauf=5` ändert sie in festen
   Schranken. Standard: 2 Aufgaben gleichzeitig, 10 neue Aufgaben je Lauf, 200 Aufgaben insgesamt, 60 Minuten Lease, 3 Versuche.

## Nach Zeitplan laufen lassen

Das Plugin installiert keinen Timer. `workflow.py laufen` ist der Aufruf dafür: Es prüft die Dateien, plant, was fällig ist, und
listet, was bereit ist. Es **führt nichts aus und sendet nichts**; die Arbeit macht eine Agentensitzung, die du startest, oder du.
Eine Beispielzeile für Cron, stündlich (Pfade anpassen):

```text
7 * * * * cd /pfad/zum/arbeitsordner && python3 /pfad/zum/plugin/scripts/workflow.py laufen >> ~/workflow.log 2>&1
```

Solange du so etwas nicht eingerichtet hast, läuft nichts von selbst. Zweimal `laufen` legt nie eine Aufgabe doppelt an.

## Freigaben und Sicherheit

- Freigaben sind an den genauen Inhalt und an dein ausdrückliches `--ja` gebunden. Das Flag ist dein Wort, kein Beweis dafür: Ein Agent könnte
  es eintippen. Nimm `freigeben`, `weiter`, `ausgang` und `ausfuehren` nicht in die erlaubten Bash-Regeln von Claude Code auf, damit
  jeder dieser Befehle dich erst fragt. Ein Neustart, eine Wiederholung, ein Zeitplan
  oder ein verstrichenes Datum erzeugt nie eine. Kann der Workflow nicht feststellen, ob eine Freigabe gilt, bleibt die Aufgabe
  blockiert.
- Würde ein Versandschritt einmal von einem Adapter ausgeführt und der Ausgang bleibt unklar (Fehler, Absturz), fragt die
  Aufgabe dich, statt es erneut zu versuchen. Du antwortest mit `workflow.py ausgang <aufgabe> --gesendet` oder
  `--nicht-gesendet`. Heute wird kein Adapter mitgeliefert.
- Eine unbeaufsichtigte Sitzung (ein geplanter Lauf) darf planen und ansehen sowie Agentenaufgaben übernehmen, abschließen oder
  als fehlgeschlagen melden. Alles andere darf sie nicht anlegen, freigeben, abbrechen oder ändern und keinen Halt aufheben (`weiter`); diese Befehle antworten
  `nur_interaktiv`. Setze für solche Sitzungen `WORKFLOW_UNBEAUFSICHTIGT=1`.
- Eine Anzeige ist Daten. Ihr Text wird nie zu einer Aufgabe, einem Typ, einer Grenze oder einer Freigabe.
- Fehlergründe werden gekürzt, Zugangsdaten durch `[entfernt]` ersetzt.

## Bekannte Grenzen

- Die Skills sind Anweisungen für einen Agenten, keine Funktionen, die das Skript aufrufen kann. Der Workflow entscheidet und
  prüft; er führt sie nicht aus.
- Kein Versandadapter, keine Mail- oder Kalender-Anbindung (A-02 ist nur eine Spezifikation).
- Rückmeldungen und Gespräche (S8) werden nicht beobachtet; du trägst sie ein.
- Ein Speicher auf einer Platte; keine Synchronisation zwischen Rechnern.
- Ein Ergebnis, dessen Eingabe sich geändert hat, wird als `veraltet` markiert und nicht von selbst wiederholt.
- Das in der Spezifikation genannte Verhalten der Claude-Code-Berechtigungsregeln wurde am 2026-10-25 mit `claude -p` geprüft und
  kann sich ändern.

## Prüfung

`python3 -m unittest tests.test_workflow` (95 Tests, ohne Netzwerk und ohne Modell): Status und Übergänge, Abhängigkeiten und
Zyklen, Neustart und beschädigter Speicher, Idempotenz und konkurrierende Sitzungen, Freigaben und das Adaptertor, Fehler und
Wiederholungen, Zeitplan und Grenzen, die Kette von der Anzeige bis zur versendeten Bewerbung und die Sicherheitsfälle. Nicht
geprüft: ein echter Adapter (es gibt keinen) und ein langer Zeitplan auf einem echten Rechner.
