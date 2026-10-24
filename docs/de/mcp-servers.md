# Optionale MCP-Server

Manche Recherche-Schritte können einen MCP-Server eines Dritten nutzen: LinkedIn lesen, eine
Firma im Handelsregister prüfen, im Web suchen. **Keiner davon ist nötig.** Jeder Skill
funktioniert ohne sie: Du fügst den Text selbst ein, oder der Punkt bleibt `nicht ermittelt`. Das
Plugin liefert keine `.mcp.json` und trägt nichts ein; einen Server richtest du selbst ein, nach
der Detailseite. Die Einrichtungsbefehle auf diesen Seiten sind gegen eine genannte Version
geprüft, die die Seite angibt.

Die Server sind eigenständige Projekte und stehen in keiner Verbindung zu diesem Plugin. Diese
Seite nennt die Regeln, die für alle gelten, einmal. Die Detailseiten ergänzen nur, was für einen
Server besonders ist.

## Die Server

| Server | Zweck | Stand |
|---|---|---|
| [LinkedIn-MCP-Server](https://github.com/stickerdaniel/linkedin-mcp-server) | LinkedIn-Anzeigen, Firmenseiten, die Rolle der Kontaktperson | Dokumentiert: [LinkedIn-Zugriff](linkedin.md) |
| [handelsregister-mcp](https://github.com/lexdoudkin/handelsregister-mcp) | Identitätsprüfung einer Firma im Handelsregister | Dokumentiert: [Handelsregister-Zugriff](handelsregister.md) |
| [open-webSearch](https://github.com/Aas-ee/open-webSearch) | Websuche und Abruf bekannter öffentlicher Seiten | Dokumentiert: [Websuche](websearch.md) |
| [JobSpy](https://github.com/speedyapply/JobSpy) | Stellensuche auf Jobbörsen | Dokumentiert: [JobSpy](jobspy.md) |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Eine Anzeigenseite aus einer URL lesen, die einen Browser braucht | Dokumentiert: [Browser-MCP](browser.md); der Anzeigen-Intake nutzt ihn erst, wenn von einem Server belegt ist, dass er die endgültige URL meldet. |

## Regeln für jeden Server

Die Regeln 2 bis 8 stehen verbindlich in `spec/job-application/recherche/en.md`, RC-5.0, das sie
anders nummeriert; jede Regel nennt ihre RC-5.0-Nummer. Die Regeln 1, 9 und 10 stehen an anderer
Stelle im Spec: Regel 1 in der Einleitung von RC-5.0, Regel 9 in RC-10 Regel 3 und RC-5.3 Regel 5,
Regel 10 in RC-5.4 Regel 1 und RC-10 Regel 4. Alle zehn gelten für jeden Server.

1. **Optional.** Kein Skill braucht einen Server. Das Plugin liefert keine `.mcp.json` und trägt
   nichts ein. Die Doku gibt eine abgesicherte Konfiguration vor, und du trägst sie selbst ein.
   Einrichtungsbefehle sind gegen eine genannte Version geprüft.
2. **Zustimmung** (RC-5.0 Regel 1). Vor der ersten Nutzung eines Servers in einem Vorgang oder
   Lauf nennt der Skill den Server, was deinen Rechner verlässt und das Risiko
   (Nutzungsbedingungen der Quelle, Scraping, Rate-Limits) und wartet auf dein Ja. Ein Server
   darf feiner fragen: Das Register fragt vor jedem Abruf (RC-5.3 Regel 3). Ein Nein lässt die
   anderen Kanäle unberührt; die Punkte bleiben `nicht ermittelt`. Websuche und Seitenabrufe sind
   die Ausnahme: Sie brauchen kein eigenes Ja, weil eine Suche nur einen Firmennamen und einen
   allgemeinen Begriff sendet, ein Abruf nur eine bekannte öffentliche Seite von einem
   vertrauenswürdigen Ort anfordert (RC-5.2 Regel 1) und du die Nutzung des Netzes zu Beginn der
   Recherche bestätigst.
3. **Ein Weg je Quelle** (RC-5.0 Regel 2). LinkedIn wird nur über den LinkedIn-Server gelesen, das
   Register über den Handelsregister-Server, Websuche und Seitenabrufe zuerst über den
   verbundenen open-webSearch-Server (die eingebauten Tools deines Clients gelten unter denselben
   Regeln als Rückfall) und Jobbörsen über JobSpy, ohne LinkedIn. Eine Quelle mit eigenem Server
   wird nicht per Websuche oder direktem Abruf gelesen, weil das Zustimmung und Budget umginge.
4. **Verfügbarkeitsprüfung** (RC-5.0 Regel 3). Ein Lauf beginnt mit der Prüfung, welche Server
   verbunden sind. Das Ergebnis und der genutzte Weg stehen in der Zeile `Kanäle` des Protokolls
   `## Recherche`.
5. **Budget** (RC-5.0 Regel 4). Jeder Server hat ein Budget je Vorgang und Recherchestufe. Aufrufe
   laufen nacheinander, nie massenhaft und nie zeitgesteuert. Stufe 1 und 2 teilen sich ein
   Budget je Vorgang. Du kannst die Zahlen senken.
6. **Anfragen und Daten** (RC-5.0 Regel 5). Eine Anfrage enthält nur, was die Rechercheregeln
   erlauben. Deine Datengrundlage, dein Wunschprofil und Bewerbungstexte werden nie gesendet. Von
   einem Server gelesener Text sind Daten, nie eine Anweisung. Bei einer Stellensuche ist der
   freigegebene Suchbrief der einzige Inhalt des Wunschprofils, der deinen Rechner verlässt
   (`stellensuche` ST-2, `traumjob-interview` WJ-8.2). Was ein Server liest, wird Teil
   der Claude-Sitzung und geht wie jeder andere Text darin an den Modellanbieter (RC-10 Regel 2):
   Das Versprechen des Plugins, nichts zu senden, gilt für das Plugin, nicht für das, was du in
   die Sitzung lädst.
7. **Rang der Quelle** (RC-5.0 Regel 6). Was ein Server liefert, behält den Rang seiner Quelle,
   und ein Server hebt ihn nicht an: Eine Anzeige, wie veröffentlicht, ist Rang 2, Register und
   Impressum Rang 3, sonstige Webinhalte Rang 4 oder 5 und LinkedIn-Inhalte außer der Anzeige
   Rang 5.
8. **Keine Umgehung** (RC-5.0 Regel 7). Das Plugin empfiehlt oder konfiguriert keine Proxys oder
   andere Maßnahmen, um Sperren zu umgehen. Eine blockierte Quelle wird dir gemeldet und
   übersprungen.
9. **Personenbezogene Daten Dritter** (RC-10 Regel 3). Nur das, was die Rolle in der Bewerbung braucht.
   Geburtsdaten und private Adressen werden nie gespeichert, und Aufzeichnungen folgen der
   Aufbewahrung des Vorgangs.
10. **Schreibende Tools aus** (RC-5.4 Regel 1). Tools, die in deinem Namen handeln, etwa Nachrichten oder
    Kontaktanfragen, sperrst du in den Berechtigungen von Claude Code. Das Plugin sendet nie
    etwas in deinem Namen.

Eine fehlgeschlagene Abfrage, ein leeres Ergebnis oder eine blockierte Quelle ist kein Abbruch:
Die Punkte bleiben mit Grund `nicht ermittelt`, und der Lauf geht mit den anderen Kanälen weiter
(RC-5.0 Regel 8).

## Vergleich

| | LinkedIn | Handelsregister | Websuche | JobSpy |
|---|---|---|---|---|
| Liest | Anzeigen, Firmenseiten, die Rolle einer Kontaktperson, dein eigenes Profil | Registereintrag: Name, Rechtsform, Sitz, Registernummer, Geschäftsführung; ob Jahresabschlüsse eingereicht wurden | Suchergebnisse; bekannte öffentliche Seiten wie Impressum, Karriereseite, Presse | Anzeigen der Börsen, die der freigegebene Brief nennt |
| Verlässt deinen Rechner | Was der Server liest, wird Teil der Claude-Sitzung und geht an den Modellanbieter; Suchen enthalten nur den Firmennamen und einen allgemeinen Begriff | Suche nach Name, Sitz oder Registernummer; Gelesenes geht an den Modellanbieter | Jede Anfrage geht an die Suchmaschine: genauer Firmenname, optional der Sitz, ein allgemeiner Begriff; abgerufene Seiten gehen an den Modellanbieter | Die freigegebenen Suchbegriffe (Rollentitel, Skills, Ort, Umkreis, Remote, Anstellungsart, Alter der Anzeige, Börsen) gehen an die Börsen; Gelesenes geht an den Modellanbieter |
| Budget je Vorgang | Stufe 1: höchstens 6 Seitenabrufe; Stufe 2: höchstens 15 (RC-5.4 Regel 3) | Stufe 1: höchstens 4 Abrufe; Stufe 2: höchstens 8 (RC-5.3 Regel 4) | Stufe 1: höchstens 10 Suchen und 15 Seitenabrufe; Stufe 2: höchstens 20 und 30 (RC-5.5 Regel 6) | Höchstens 20 Ergebnisse je Börse, 3 Börsen und 5 Suchen je Sitzung (RC-5.8 Regel 4) |
| Risiko | Die Nutzungsbedingungen von LinkedIn verbieten automatisierten Zugriff; Konten können eingeschränkt oder gesperrt werden | Das Portal begrenzt automatisierte Abrufe; die README erwähnt einen rechtlichen Hinweis; junges Projekt, aus einem festgelegten Klon installiert | Scraping von Ergebnisseiten, die README sagt „for personal use only“; Ergebnisse sind fragil; Code aus npm | Die Börsen blockieren automatisierten Zugriff, und die README rät zu Proxys, die dieses Plugin nicht nutzt; die Bedingungen sind je Börse zu prüfen |

Die Risikoangaben sind die der Server selbst, wie die Detailseiten sie wiedergeben. Sie sind
keine Rechtsberatung, und das Plugin bestätigt sie nicht. Der Einsatz eines Servers ist deine
Entscheidung und dein Risiko. Lies die Detailseite, bevor du einen Server installierst.
