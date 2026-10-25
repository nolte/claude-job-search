# JobSpy

Passende Stellen zu finden ist für die meisten noch Handarbeit: Du suchst auf mehreren Jobbörsen,
kopierst einen Text und startest die Bewerbung. Das quelloffene Projekt
[JobSpy](https://github.com/speedyapply/JobSpy) (MIT) bietet eine gemeinsame Abfrage über mehrere
Börsen, und sein MCP-Server (`mcp-jobspy` auf PyPI) gibt die Ergebnisse an Claude weiter. Der
Skill `job-application-job-search` nutzt ihn, um aus deinem Wunschprofil eine Shortlist zu
bauen.

!!! note "Bevorzugter Weg zu Jobbörsen, aber nicht Teil dieses Plugins"
    Diese Seite behandelt nur den JobSpy-Server. Die Regeln, die für alle optionalen Server
    gelten (Zustimmung, ein Weg je Quelle, Budget, Rang der Quelle, keine Umgehung), stehen auf
    [Optionale MCP-Server](mcp-servers.md). Ist der Server verbunden, werden Jobbörsen über ihn
    durchsucht und nicht per Websuche oder Seitenabruf. Das ist die Arbeitsregel des
    Rechercheverfahrens (`spec/job-application/recherche/en.md`, RC-5.8); der Suchschritt selbst
    ist in `spec/job-application/stellensuche/en.md` festgelegt. Kein Skill braucht den Server.
    Ohne ihn fügst du eine Anzeige in `job-application-solution` ein, wie in
    [Erste Schritte](getting-started.md) beschrieben. Das Plugin installiert nichts und liefert
    keine `.mcp.json`: Die Konfiguration unten trägst du selbst ein. Der Server ist ein
    eigenständiges Projekt und steht in keiner Verbindung zu diesem Plugin.

Jede Aussage über JobSpy auf dieser Seite ist die des Projekts selbst, wie seine READMEs sie
nennen, geprüft gegen **Version 1.4.1** (laut PyPI am 23. Oktober 2026 veröffentlicht). Das
Plugin hat den Server nicht gegen die Börsen getestet und bestätigt diese Aussagen nicht. Prüfe
die README auf Neueres.

## Was der Server tut

Der MCP-Server bietet zwei Tools, wie seine README sie beschreibt:

| Tool | Was es tut | Nutzung im Skill |
|---|---|---|
| `search_jobs` | Durchsucht die gewählten Börsen und liefert eine Vorschau mit einer Such-ID; die Ergebnisse lassen sich optional als `.csv`, `.json` oder `.jsonl` exportieren | Die Shortlist |
| `get_job_details` | Liefert die vollständigen Datensätze gewählter Stellen aus einer Suche, ohne erneut zu suchen | Der eine Eintrag, den du wählst, für die Übergabe |

Die README des MCP-Servers listet die Parameter der Tools nicht auf, deshalb tut es diese Seite
auch nicht. Der Skill übergibt nur, was dein freigegebener Suchbrief enthält. Den Export nutzt
das Plugin nicht von sich aus; wünschst du einen, landet er in deiner Wurzel und folgt den
Aufbewahrungsregeln unten.

## So nutzt der Skill ihn

`job-application-job-search` ist ein optionaler Schritt vor der Bewerbung. Er läuft so:

1. Er baut aus deinem bestätigten Wunschprofil und `profil.md` einen **Suchbrief** und **zeigt
   ihn zuerst**: Suchbegriffe, Ort und Umkreis, Remote, Anstellungsart, höchstes Alter der
   Anzeige, Börsen, Ergebnisse je Börse und die Quelle jedes Begriffs. Der Brief enthält nur
   Begriffe, die du selbst in eine Börse tippen würdest. Ausschlussgründe, Gehaltswunsch,
   persönliche Umstände und Text aus deiner Datengrundlage gehören nie hinein.
2. Vor deinem Ja wird nichts gesendet. Nur die Begriffe des freigegebenen Briefs gehen an die
   Börsen.
3. Standardbörsen sind **Indeed und Glassdoor**. Weitere Börsen nutzt der Skill nur, wenn dein
   Brief sie nennt. **LinkedIn wird nie über JobSpy durchsucht**: LinkedIn läuft über den
   eigenen Server, siehe [LinkedIn-Zugriff](linkedin.md).
4. Die Grenzen sind bewusst klein: höchstens 20 Ergebnisse je Börse, 3 Börsen je Suche, 5 Suchen
   je Sitzung und ein begrenztes Alter der Anzeigen (RC-5.8 Regel 4). Geplante oder wiederkehrende
   Suchen gibt es nur als freigegebenen Suchauftrag, siehe *Wiederkehrende Suche* unten. Vollständige Details holt der Skill nur für den Eintrag, den du
   wählst, nie für eine Liste.
5. Die Shortlist zeigt Vetos aus deinem Wunschprofil mit Grund, statt sie zu streichen, führt
   Doppelte über Börsen und mit deinen vorhandenen Vorgängen zusammen und markiert Anzeigen
   eines Vermittlers oder ohne Arbeitgebername. Ein Fit-Check läuft nur auf Wunsch, je Eintrag.
6. Du wählst einen Eintrag; der Skill übergibt ihn an `job-application-solution`, mit dem
   Anzeigentext wie veröffentlicht und der URL als `stellenquelle`.
7. Brief, Shortlist und deine Entscheidung je Eintrag (`übernommen`, `abgelehnt`, `offen`)
   landen in `suche/<JJJJ-MM-TT>-<slug>.md` in deiner Wurzel. Der Datensatz bleibt 90 Tage
   erhalten. Der Skill listet Datensätze nach Fristende auf und löscht nichts; du entscheidest.

## Wiederkehrende Suche (Suchauftrag)

Für eine Suche, die du wiederholen willst, führt der Skill einen **Suchauftrag**: dein freigegebener Brief plus ein Plan
(wie oft, wie viel). Gefundene Stellen landen in einer **Warteschlange** (`suche/warteschlange.json`), die deine
Entscheidungen behält. So wird dieselbe Stelle nicht zweimal angeboten, eine geänderte Anzeige wird markiert und eine
Stelle mit Vorgang erscheint nicht als neu. Die Regeln stehen in `spec/job-application/stellensuche/en.md` (ST-13 bis ST-20).
Die Suche selbst braucht weiter den JobSpy-Server in einer Claude-Sitzung; das Hilfsskript `scripts/stellensuche.py`
übernimmt Speichern, Grenzen und Deduplizierung.

**Was die Freigabe bedeutet.** Sie erlaubt Abfragen mit den freigegebenen Begriffen an die freigegebenen Börsen, höchstens
3 Börsen mit je 20 Ergebnissen und standardmäßig höchstens 3 Läufe in 7 Tagen (du kannst senken oder bis auf 7 Läufe
erhöhen), sowie das lokale Speichern von Titel, Firma, Ort, Datum, URL und einem Hash der Beschreibung. Sie erlaubt keine
Bewerbung, keine Nachricht an einen Arbeitgeber und keine Änderung an einem Vorgang. Ändert sich ein Begriff, der Ort, die
Börsen, eine Grenze oder der Plan, entfällt die Freigabe; ebenso bei geänderter `wunschprofil.md`, wenn der Suchauftrag daran
gebunden ist.

Beispiele (sag es Claude, oder rufe das Hilfsskript selbst auf mit
`python3 <plugin>/scripts/stellensuche.py --konfiguration job-application/konfiguration.md <Befehl>`):

1. **Anlegen:** „Lege einen Suchauftrag für Backend-Stellen in Berlin an.“ Claude baut den Brief aus deinem Wunschprofil und
   zeigt jeden Begriff mit Quelle. Noch läuft nichts (Status `entwurf`).
2. **Prüfen und freigeben:** Claude zeigt, was gesendet wird und was nicht, wie oft und wie viel; nach deinem ausdrücklichen Ja
   folgt `freigeben <id> --ja` (Status `aktiv`).
3. **Einmal ausführen:** „Führe den Suchauftrag jetzt aus.“ Ergebnis: `ok`, `ok_ohne_treffer` (Erfolg ohne Treffer),
   `teilweise` oder `fehlgeschlagen` (zum Beispiel `suchdienst_nicht_verfuegbar`, wenn der Server nicht verbunden ist).
4. **Nach Zeitplan wiederholen:** Das Plugin installiert keinen Timer. Trage `scripts/stellensuche_geplant.sh` in einen
   Scheduler von dir ein, etwa täglich. Es startet nur für fällige Suchaufträge eine Sitzung (freigegeben, aktiv, Intervall
   vergangen, noch Läufe im 7-Tage-Fenster übrig). Die headless Sitzung darf nur das Suchwerkzeug des Servers und die
   Hilfsbefehle `lauf-start`, `board-ergebnis`, `lauf-ende` und `nachtragen` aufrufen sowie Ergebnisdateien nach `suche/eingang/`
   schreiben. Sie kann keinen Suchauftrag anlegen, ändern, freigeben, fortsetzen oder beenden und keine Entscheidung über eine
   Stelle treffen: Das bleibt bei dir in einer interaktiven Sitzung, weil ein Inserat Text enthalten könnte, der danach verlangt.
   Eine nicht lesbare Auftragsdatei wird auf stderr genannt und stoppt die anderen nicht, schau also in dein Log:
   `17 7 * * * cd /pfad/zum/arbeitsordner && /pfad/zum/plugin/scripts/stellensuche_geplant.sh job-application/konfiguration.md >> ~/suche.log 2>&1`.
   Der Werkzeugname des Servers ist standardmäßig `mcp__jobspy__search_jobs`; setze `STELLENSUCHE_JOBSPY_TOOL`, wenn du ihn
   anders genannt hast. Nicht geprüft: Das Plugin hat keine geplante Sitzung gegen den echten Server laufen lassen (es war
   kein Server verbunden).
5. **Ansehen und priorisieren:** öffne `suche/warteschlange.md` in deinem Vault (lesbare Übersicht, nach jeder Änderung neu geschrieben; Obsidian zeigt die JSON-Dateien nicht an) oder frag: „Zeige die Warteschlange.“ Die Stellen sind nach `ohne_treffer`, `klaerung` oder `veto`
   gruppiert, allein aus der Vorprüfung auf strukturierte Felder. Das ist kein Passungswert; den Fit-Check gibt es nach der
   Übergabe.
6. **Zurückstellen oder ausschließen:** „Stelle s-… zurückstellen bis 2026-12-01“ oder „ablehnen, Grund: Schichtdienst“. Ein
   erneuter Fund ändert deine Entscheidung nicht.
7. **Übergeben:** „Übernimm s-….“ Claude gibt `job-application-solution` die URL als `stellenquelle`; den Text lädt der
   URL-Intake oder du fügst ihn ein, der Plan braucht weiter deine Freigabe. Ein vorhandener Vorgang wird weiterverwendet.
8. **Fehlgeschlagenen Lauf untersuchen:** `auftraege` zeigt den letzten Lauf und Fehler; `zeige <id>` listet die letzten 30
   Läufe mit Code (`board_blockiert`, `verbindung_fehlgeschlagen`, …). Nach 3 Fehlern in Folge stoppen geplante Läufe, bis du
   fortsetzt. Endete ein Lauf `teilweise`, `fehlgeschlagen` oder `unterbrochen`, obwohl Claude die Antworten eines Boards hatte
   (das Erfassen scheiterte), lassen sie sich danach mit `nachtragen <id> <lauf> <board>` speichern; Status dieses Laufs und
   Budget ändern sich dadurch nicht.
9. **Pausieren und beenden:** „Pausiere den Suchauftrag“ (`pausieren`, später `fortsetzen`) und „Beende den Suchauftrag“
   (`beenden`, endgültig: für eine neue Suche legst du einen neuen an).

## Einrichten

Du brauchst [uv](https://docs.astral.sh/uv/getting-started/installation/). Die README des
MCP-Servers ist maßgeblich für aktuelle Schritte und Optionen. Für Claude Code:

```bash
claude mcp add jobspy -- uvx mcp-jobspy@latest
```

Oder als Eintrag im Abschnitt `mcpServers` deiner MCP-Konfiguration:

```json
{
  "mcpServers": {
    "jobspy": {
      "command": "uvx",
      "args": ["mcp-jobspy@latest"]
    }
  }
}
```

`@latest` hält den Server selbst aktuell, sodass er mit den wechselnden Seiten der Börsen
funktioniert, führt aber auch neuen Code ohne deine Prüfung aus. Legst du Wert darauf, pinne
stattdessen eine Version: Schreibe `mcp-jobspy@<version>` mit einer Versionsnummer aus den
Releases des Projekts. Die für diese Seite geprüfte Version ist 1.4.1.

## Was er abdeckt

Laut README verhalten sich die Börsen bei einer Suche im deutschsprachigen Raum so:

| Börse | In DACH |
|---|---|
| Indeed | Unterstützt Deutschland, Österreich und die Schweiz. Standardbörse |
| Glassdoor | Unterstützt Deutschland, Österreich und die Schweiz. Standardbörse, mit dem bekannten Problem unten |
| LinkedIn | Von JobSpy unterstützt, aber dieses Plugin nutzt es nie über JobSpy; es läuft über den [LinkedIn-Server](linkedin.md) |
| ZipRecruiter | USA und Kanada: gilt nicht |
| Bayt, Naukri, BDJobs, HelloWork | Andere Regionen (Naukri: Indien, BDJobs: Bangladesch, HelloWork: Frankreich): gelten nicht für DACH |

**Nicht abgedeckt:** StepStone, XING und die Jobbörse der Bundesagentur für Arbeit. Eine Suche
über JobSpy übersieht deshalb viele deutsche Anzeigen. Sieh die Shortlist als Ausschnitt des
Marktes, nicht als dessen Gesamtheit.

**Ein bekanntes Glassdoor-Problem.** Ein offenes Issue (#438 im JobSpy-Repository, offen am
23. Oktober 2026) meldet, dass Glassdoor den Ort „Berlin, Germany“ nicht findet, während
„Berlin“ und „Berlin, Deutschland“ funktionierten. Eine Korrektur ist vorgeschlagen, aber nicht
übernommen. Fällt Glassdoor aus, meldet der Skill das und überspringt die Börse; die anderen
Börsen laufen weiter.

## Regeln speziell für JobSpy

Die allgemeinen Regeln stehen auf [Optionale MCP-Server](mcp-servers.md). Für JobSpy kommt
hinzu:

1. **Sperren.** Die README sagt, die Jobbörsen „are aggressive with blocking“, und empfiehlt
   Proxys. **Dieses Plugin empfiehlt oder konfiguriert keine Proxys oder andere Maßnahmen, um
   Sperren zu umgehen.** Eine blockierte Börse wird dir gemeldet und aus der Suche
   ausgelassen.
2. **Nutzungsbedingungen.** Die Bedingungen der Börsen können automatisierten Zugriff
   einschränken. Sie unterscheiden sich je Börse, und du prüfst sie selbst. Keine der beiden READMEs nimmt zu
   den Nutzungsbedingungen Stellung. Der Einsatz des Servers ist deine Entscheidung und dein
   Risiko, wie bei LinkedIn und dem Handelsregister.
3. **Budget.** Höchstens 20 Ergebnisse je Börse, 3 Börsen je Suche, 5 Suchen je Sitzung. Du
   kannst die Zahlen senken.
4. **Personenbezogene Daten.** Ein Datensatz enthält ein Feld `emails` und Kontaktdaten der
   Firma. Sie werden nicht gespeichert und nicht in der Shortlist gezeigt: Die Shortlist behält
   Firma, Rolle, Ort, Datum und URL. Was der Server liest, wird trotzdem Teil der
   Claude-Sitzung und geht an den Modellanbieter.
5. **Anzeigentext sind Daten.** Eine Anzeige von einer Börse kann Anweisungen enthalten. Der
   Skill behandelt sie als Daten und befolgt sie nie.
6. **Qualität der Daten.** Ein Eintrag ist eine Anzeige, wie veröffentlicht (Rang 2), für
   Anforderungen und Bewerbungsweg; die Angaben der Börse zur Firma sind Rang 5. Eine
   Gehaltsspanne kann aus der Beschreibung gelesen sein (`salary_source: description`); der
   Skill zeigt sie mit diesem Hinweis und nutzt sie nie als Tatsache in einem Dokument. Dieselbe
   Anzeige kann auf mehreren Börsen stehen und alt oder neu eingestellt sein, deshalb zeigt die
   Shortlist das Datum der Anzeige.
7. **Ohne den Server.** Füge den Anzeigentext in `job-application-solution` ein.
8. **Eine gefundene Stelle ist ein Link, kein Text.** Die Suche speichert Titel, Firma, Ort, Datum und URL, nicht die
   Beschreibung. Für die Übergabe braucht es den Text aus dem URL-Intake von `job-application-posting-analysis`. Jobbörsen
   verweigern diesen Abruf oft: Ein Test mit dem Web-Search-Server auf einer Indeed-Seite endete mit HTTP 401 (2026-10-25,
   eine Seite, keine Statistik). Der Skill umgeht so eine Verweigerung nicht (kein Proxy, kein anderer Header, kein
   Browser). Der Weg, der immer geht: Anzeige im Browser öffnen, den Text kopieren und in `job-application-solution`
   einfügen; die URL für `stellenquelle` steht im Eintrag der Warteschlange. Der Indeed-Connector für claude.ai
   (`docs.indeed.com/mcp`) gehört nicht zu diesem Plugin: In Claude Code hat er sich im selben Test nicht verbunden
   (die Anmeldung wurde beim Wiederverbinden abgelehnt), und seine Bedingungen für die Nutzung außerhalb von claude.ai
   nennt seine Seite nicht.
