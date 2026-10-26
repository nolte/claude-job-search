# Arbeitsagentur (Bundesagentur für Arbeit)

Die Jobsuche der Bundesagentur für Arbeit (BA, [arbeitsagentur.de/jobsuche](https://www.arbeitsagentur.de/jobsuche)) führt viele
deutsche Stellen, die [JobSpy](jobspy.md) nicht erreicht. Der Skill `job-application-job-search` kann sie als zweite Quelle über den
Community-MCP-Server [jobsuche-mcp-server](https://github.com/wunderfrucht/jobsuche-mcp-server) (MIT) lesen.

!!! warning "Nur interaktiv, und rechtlich ungeklärt"
    Die BA bietet für die Jobsuche **keine offizielle API** an. Der Server nutzt eine Schnittstelle, die das Community-Projekt
    [bundesAPI/jobsuche-api](https://github.com/bundesAPI/jobsuche-api) dokumentiert, mit einem gemeinsamen öffentlichen Client-Schlüssel. Die
    [Nutzungsbedingungen](https://www.arbeitsagentur.de/nutzungsbedingungen) (Abschnitt 2a, Absatz 3) verbieten Robots und verbieten, eine
    Schnittstelle entgegen ihrem Zweck zur Datensammlung und -auswertung auszulesen. Ob eine Suche, die *du* für *deine* Bewerbung startest,
    noch in diesem Zweck liegt, entscheidet der Text nicht. Deshalb nutzt das Plugin die BA **nur auf deine Bitte in einer interaktiven
    Sitzung**, nie in einem wiederkehrenden Suchauftrag, nie nach Zeitplan, und legt kein BA-Ergebnis in der Warteschlange ab. Die Nutzung ist deine
    Entscheidung und dein Risiko. Das ist keine Rechtsberatung.

Die Regeln für alle optionalen Server stehen auf [Optionale MCP-Server](mcp-servers.md); normativ sind
`spec/job-application/stellensuche/en.md` ST-21 und `recherche/en.md` RC-5.9. Das Plugin installiert nichts und liefert keine `.mcp.json`.
Der Server ist ein eigenständiges Projekt und weder mit diesem Plugin noch mit der BA verbunden.

## Was der Server ist (geprüft am 26.10.2026)

| Punkt | Befund |
|---|---|
| Quelle | Rust-Server um die Bibliothek `jobsuche`; Endpunkt `rest.arbeitsagentur.de/jobboerse/jobsuche-service` |
| Zugangsdaten | Keine von dir; der gemeinsame öffentliche Schlüssel steckt in der Bibliothek. `JOBSUCHE_API_KEY` kann ihn ersetzen |
| Pflege | 3 Sterne, letzte Code-Änderung 23.10.2025, 6 offene Issues; Tests nur für die Parameter, keine gegen den Live-Dienst |
| Werkzeuge | `search_jobs`, `get_job_details`, `search_jobs_with_details`, `batch_search_jobs`, `get_server_status` |
| Vom Skill genutzt | Nur `search_jobs` und `get_job_details`. Die beiden Sammel-Werkzeuge werden nie genutzt |
| Grenzen | Seiten bis 100; Wiederholungen mit Backoff übernimmt die Bibliothek; der Server fügt in seinen Sammel-Werkzeugen Pausen von 100/200 ms ein |
| Nicht verfügbar | Kontaktdaten und Bewerbungsfrist; Gehalt, `fulltime` und Stellenart nur im vollen Datensatz |
| Bekannter Mangel | `contract_type` wird angenommen, aber in `search_jobs` **nicht angewendet** |

Das Plugin hat diesen Server **nicht gegen den Live-Dienst der BA laufen lassen**. Die Feldnamen stammen aus dem Quellcode des Servers; prüfe sie
gegen die Version, die du installierst.

## Einrichten

Du brauchst Node.js (npm) oder eine Rust-Toolchain. Aktuelle Schritte stehen in der README des Servers. Für Claude Code:

```bash
claude mcp add jobsuche -- npx @wunderfrucht/jobsuche-mcp-server
```

`npx` ohne Version führt aus, was gerade veröffentlicht ist. Lege eine Version fest, die du angesehen hast
(`@wunderfrucht/jobsuche-mcp-server@<version>`), wenn du das willst. Die Werkzeugnamen lauten dann `mcp__jobsuche__search_jobs` und
`mcp__jobsuche__get_job_details`. Entfernen: `claude mcp remove jobsuche`; sonst ändert sich im Plugin nichts.

## Wie der Skill ihn nutzt

Nenne `arbeitsagentur` als Board im Suchbrief (es zählt als eines der drei Boards). Nach deinem Ja für genau diesen Brief:

1. `scripts/arbeitsagentur.py abfrage` macht aus dem Brief einen `search_jobs`-Aufruf je Suchbegriff. Kriterien, die der Server nicht erzwingen kann, zeigt der Skill
   dir mit Grund und lässt sie nicht stillschweigend fallen.
2. Nach jedem Aufruf prüft `scripts/arbeitsagentur.py pruefen` die Antwort. **Ein Fehler wird nie als „keine Stellen“ gemeldet**: der Skill unterscheidet keine Treffer
   (`ok_ohne_treffer`), einen fehlenden Server, ein Verbindungsproblem, Begrenzung oder Sperre, einen abgelehnten Schlüssel, eine abgelehnte Anfrage und eine
   unlesbare Antwort.
3. `scripts/arbeitsagentur.py zusammenfuehren` führt BA- und JobSpy-Einträge zusammen: gleiche Kennung oder URL, oder gleiche Firma, gleicher Titel und gleicher Ort innerhalb
   von drei Tagen ist eine Stelle mit allen Boards und URLs. Ein ähnlicher Titel allein führt nichts zusammen.
4. Du wählst einen Eintrag; der Skill lädt seinen vollen Datensatz und gibt die Beschreibung **wie veröffentlicht** an `job-application-solution`.
   Anforderungsabgleich, Passungsprüfung und Qualitätsprüfung sind die bestehenden.

| Brief | An den Server | |
|---|---|---|
| Suchbegriff | `job_title`, ein Aufruf je Begriff | direkt |
| Ort, Radius | `location`, `radius_km` (Radius nur mit Ort) | direkt |
| Höchstalter | `published_since_days` | direkt |
| Ergebnisse je Board | `page_size` (höchstens 20) | direkt |
| Vollzeit, Teilzeit | `employment_type` | direkt |
| Remote: ja | `employment_type: home_office` (Heim-/Telearbeit, nahe an Remote) | näherungsweise |
| Praktikum, Vertragsart | – | nicht angewendet |
| Remote: nein | – | nicht angewendet |

Remote, Stellenart und Gehalt stehen nicht in der Trefferliste und bleiben leer. Auch die Beschreibung fehlt in der Liste; die Übergabe lädt sie.

## Regeln für die BA-Quelle

1. **Zustimmung.** Vor der ersten Nutzung nennt der Skill den Server, was deinen Rechner verlässt (nur die Briefbegriffe) und das Risiko oben, und wartet auf dein Ja.
2. **Budget.** Höchstens 20 Ergebnisse je Aufruf, 3 Boards je Suche, 5 Suchen je Sitzung; eine weitere Seite zählt als Suche und wird nur auf deine Bitte geholt.
3. **Keine Umgehung.** Kein Proxy, kein anderer Schlüssel, keine Wiederholungsschleife.
4. **Anzeigentext ist Daten.** Ein Titel oder eine Beschreibung kann Anweisungen enthalten. Der Skill ignoriert sie, und das Skript übernimmt keine Beschreibung in seine Ausgabe.
5. **Personenbezogene Daten.** Dein Profil gelangt nie in eine Anfrage. Was der Server liest, wird Teil der Claude-Sitzung und geht wie jeder Text darin an den Modellanbieter.

## Fehlersuche

| Meldung des Skills | Bedeutung und nächster Schritt |
|---|---|
| `nicht_verfuegbar` | Der Server ist nicht verbunden. Prüfe `/mcp`; oder füge die Anzeige in `job-application-solution` ein |
| `verbindung` | Netzproblem oder Zeitüberschreitung. Später erneut versuchen |
| `blockiert` | Die BA hat begrenzt oder abgelehnt. Warten; das Plugin setzt keinen Proxy |
| `authentifizierung` | Der Schlüssel wurde abgelehnt. Such keinen anderen; die Schnittstelle kann sich geändert haben |
| `ungueltig` | Der Server hat die Anfrage abgelehnt. Begriff kürzen oder Ort prüfen |
| `antwort_ungueltig` | Die Antwort hatte keine brauchbare Liste. Die Serverversion passt womöglich nicht; lies seine README |
| `ok_ohne_treffer` | Gesucht, nichts gefunden. Begriffe oder Höchstalter erweitern |

## Tests

`python3 -m unittest tests.test_arbeitsagentur` (oder `task test`). Die Tests nutzen erfundene Antworten und brauchen weder Server noch Netz.
Ein Live-Test gehört nicht zum Plugin.
