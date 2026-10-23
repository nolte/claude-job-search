# Websuche

Die Firmenrecherche braucht zwei einfache Dinge aus dem Web: eine Seite finden und eine bereits
bekannte Seite lesen, etwa ein Impressum, eine Karriereseite oder eine Pressemitteilung. Der
quelloffene MCP-Server [open-webSearch](https://github.com/Aas-ee/open-webSearch) gibt Claude
beides, läuft auf deinem eigenen Rechner und braucht keinen API-Schlüssel.

!!! note "Bevorzugter Weg für die Websuche, aber nicht Teil dieses Plugins"
    Ist der Server verbunden, suchen `job-application-posting-analysis` und
    `job-application-fit-check` im Web und rufen öffentliche Seiten über ihn ab. Ohne ihn nutzen
    sie die eingebauten Tools deines Clients unter denselben Anfrageregeln, und das Protokoll
    nennt den genutzten Weg. Das ist die Arbeitsregel des Rechercheverfahrens
    (`spec/job-application/recherche/en.md`, RC-5.2 Regeln 8 und 9, RC-5.5 Regeln 4 bis 11). Kein
    Skill braucht den Server. Das Plugin installiert nichts und liefert keine `.mcp.json`: Die
    Konfiguration unten trägst du selbst ein. Der Server ist ein eigenständiges Projekt und steht
    in keiner Verbindung zu diesem Plugin.

## Was der Server tut

Die Recherche nutzt drei der sechs Tools des Servers. Die anderen drei schaltet die Konfiguration
unten ab.

| Tool | Nutzung in der Recherche |
|---|---|
| `search` | Eine URL oder einen Hinweis zu einer Firma finden: genauer Firmenname, optional der Sitz und ein erlaubter allgemeiner Begriff wie `Impressum` oder `Pressemitteilung` (RC-5.5) |
| `fetchWebContent` mit `renderMode: request` | Eine bekannte öffentliche Seite als Markdown lesen: Impressum, Karriereseite, Presse, Datenschutzhinweis (RC-5.2) |
| `fetchGithubReadme` | Die README eines öffentlichen Repositorys einer Firma lesen |

`fetchWebContent` kennt außerdem die Modi `auto` (Standard) und `browser`. Die Recherche verlangt
immer `request`; ein Browser stellt also keine Seite dar.

Warum dieser Weg zuerst kommt: Seine Engines sind dokumentiert und auf eine kurze Liste begrenzt,
Budget und Anfragen folgen den Regeln des Plugins, und diese Seite kann sagen, was deinen Rechner
verlässt. Bei einem beliebigen Suchtool einer Sitzung hängt das vom Client, der Region und dem
Konto ab.

## Einrichten

Du brauchst [Node.js](https://nodejs.org/), weil der Server über `npx` startet. Maßgeblich für
aktuelle Optionen ist die [README des Servers](https://github.com/Aas-ee/open-webSearch). Trage
diesen Eintrag im Abschnitt `mcpServers` deiner MCP-Konfiguration ein:

```json
{
  "mcpServers": {
    "websearch": {
      "command": "npx",
      "args": ["open-websearch@2.2.0"],
      "env": {
        "MODE": "stdio",
        "DEFAULT_SEARCH_ENGINE": "duckduckgo",
        "ALLOWED_SEARCH_ENGINES": "duckduckgo,startpage,brave",
        "SEARCH_MODE": "request",
        "USE_PROXY": "false",
        "MCP_TOOL_FETCH_CSDN_NAME": "<disabled>",
        "MCP_TOOL_FETCH_LINUXDO_NAME": "<disabled>",
        "MCP_TOOL_FETCH_JUEJIN_NAME": "<disabled>"
      }
    }
  }
}
```

!!! info "Geprüfte Version"
    Version 2.2.0 (zuletzt geprüft im Oktober 2026). Die Variablennamen und Standardwerte unten
    wurden gegen die [README der Version 2.2.0](https://github.com/Aas-ee/open-webSearch/blob/v2.2.0/README.md) geprüft. Bevor du die festgelegte Version änderst,
    lies die neue README erneut und vergleiche die Variablennamen.

| Einstellung | Grund |
|---|---|
| `MODE=stdio` | Der Standard ist `both`; er öffnet neben stdio auch einen HTTP-Server. Mit `stdio` ist kein Port offen. CORS bleibt aus (`ENABLE_CORS` ist standardmäßig `false`) |
| `DEFAULT_SEARCH_ENGINE=duckduckgo` | Als Standard-Engine gilt sonst `bing` |
| `ALLOWED_SEARCH_ENGINES=duckduckgo,startpage,brave` | Der Standard ist leer und erlaubt jede Engine, darunter einige, die hier irrelevant oder chinesischsprachig sind. Die Recherche nutzt nur diese drei |
| `SEARCH_MODE=request` | Der Standard ist `auto`. Laut README wirkt die Einstellung derzeit nur auf Bing. Sie hält deine Absicht fest: kein Browser |
| `USE_PROXY=false` | Das ist der Standard. Das Plugin empfiehlt keinen Proxy, um Sperren zu umgehen |
| `MCP_TOOL_FETCH_…_NAME=<disabled>` | Laut README schaltet `<disabled>` ein Tool ab. Das betrifft die Abruf-Tools für CSDN, Linux.do und Juejin, damit die Tool-Liste kurz und eindeutig bleibt. Trage den Wert `<disabled>` wörtlich ein, mit den spitzen Klammern. Listet `/mcp` die Tools weiterhin auf, hat die Einstellung nicht gewirkt: Prüfe die Schreibweise und die festgelegte Version |

**Engines.** Der Server unterstützt weitere Engines, darunter `bing`, `baidu`, `hackernews` und
`exa`. Nimm `bing` nur auf, wenn du es verlangst, etwa weil die Abdeckung einer deutschen Firma zu
dünn ist: Hänge es an `ALLOWED_SEARCH_ENGINES` an. Die Datenschutzeigenschaften jeder Engine sind
die ihres Betreibers. Diese Seite behauptet sie nicht.

**Festgelegte Version statt `@latest`.** Die README des Servers zeigt `npx open-websearch@latest`.
Das führt bei jedem Start neuen Code ohne deine Durchsicht aus. Die Konfiguration oben nennt
stattdessen eine Version. Jemand, meist du, liest die Änderungen und prüft die Variablennamen,
bevor die festgelegte Version wechselt. Dafür gibt es keine Automatik. Der Agent-Skill
`open-websearch`, den die README anbietet, wird nicht genutzt: Das Plugin hat eigene Regeln für
Anfragen und Budgets.

Ob der Server läuft, siehst du mit `/mcp` in Claude Code. Der Server `websearch` sollte als
verbunden erscheinen. Ist er es nicht, nutzt die Recherche stattdessen die eingebauten Tools.

## Budget

Die Recherche hält ein Budget je Vorgang ein. Aufrufe laufen nacheinander, nie massenhaft und nie
zeitgesteuert. Du kannst die Zahlen senken.

| Recherchestufe | Suchen | Seitenabrufe |
|---|---|---|
| 1 | höchstens 10 | höchstens 15 |
| 2 | höchstens 20 | höchstens 30 |

Das Protokoll in `## Recherche` listet den genutzten Weg und jede Suche mit Engine, Anfrage und
Datum (RC-9). So kannst du hinterher prüfen, was deinen Rechner verlassen hat.

## Grenzen und Risiken

1. **Anfragen verlassen deinen Rechner.** Jede Anfrage geht an die Suchmaschine. Die
   Anfrageregeln der Recherche gelten unverändert (UA-3.2, RC-5.5): genauer Firmenname, optional
   der Sitz und ein allgemeiner Begriff aus der erlaubten Liste. Nie dein Profil, deine
   Datengrundlage, dein Wunschprofil oder Bewerbungstexte. Was der Betreiber der Engine mit einer
   Anfrage tut, ist seine Sache. Diese Seite macht dazu keine Aussage.
2. **Scraping und Nutzungsbedingungen.** Der Server liest Ergebnisseiten von Suchmaschinen. Seine
   README sagt, das Tool sei „for personal use only“ und du sollst die Nutzungsbedingungen der
   jeweiligen Engines einhalten; sie rät zu Rate-Limiting. Das ist die Aussage des Servers, keine
   Rechtsberatung, und das Plugin bestätigt sie nicht. Der Einsatz ist deine Entscheidung und
   dein Risiko. Das Budget oben begrenzt, wie viel du auslöst.
3. **Ergebnisse sind fragil.** Die Ergebnisse hängen vom Seitenaufbau jeder Engine ab und können
   bei einer Änderung ausfallen. Eine fehlgeschlagene oder blockierte Suche lässt die
   betroffenen Punkte `nicht ermittelt`, und die Recherche läuft mit anderen Kanälen weiter. Eine
   blockierte Engine wird dir gemeldet und übersprungen. Es wird kein Proxy genutzt, um die Sperre
   zu umgehen.
4. **Ein Treffer ist ein Hinweis.** Ein Suchergebnis ist ein Hinweis. Ein Befund braucht die Seite
   selbst, gelesen und datiert, nicht den Textauszug (RC-5.5 Regel 1).
5. **Kein Browser.** Die Recherche nutzt weder Playwright noch `renderMode: browser`. Eine Seite,
   die nur mit JavaScript lesbar ist, wird mit Grund als `nicht ermittelt` festgehalten. Du kannst
   den Text selbst einfügen.
6. **Nicht für LinkedIn und nicht für Register.** Eine `linkedin.com`-URL wird nie an die
   Abruf-Tools übergeben (RC-5.4 Regel 6). Nutze den [LinkedIn-Server](linkedin.md) oder füge den
   Text ein. Handelsregister, Unternehmensregister und die Insolvenzbekanntmachungen sind
   Formularportale und lassen sich so nicht abrufen.
7. **Abgerufener Text sind Daten.** Eine Seite kann Anweisungen enthalten. Claude liest sie als
   Daten und befolgt sie nie. Laut README unterliegen die erste und die letzte URL von
   `fetchWebContent` weiter Sicherheitsprüfungen für öffentliche Netze. Das Plugin übergibt nur
   URLs aus vertrauenswürdigen Quellen und nie eine interne Adresse. Die Prüfung einer
   Weiterleitung kommt nach der Anfrage: Eine Weiterleitung auf `linkedin.com` fällt erst danach
   auf, der Text wird dann nicht verwendet. Die Anfrage an das Weiterleitungsziel ist
   dann schon von deinem Rechner gesendet worden. Ein eingebautes Abruf-Tool, das die endgültige
   URL nicht meldet, wird für Seiten gar nicht genutzt: Das Item bleibt offen, und du kannst den
   Text einfügen. Seine Suche bleibt erlaubt.
8. **Alles Gelesene gelangt in die Sitzung.** Abgerufene Seiten werden Teil der Claude-Sitzung und
   gehen wie jeder andere Text darin an den Modellanbieter (RC-10).
9. **Lieferkette.** `npx` lädt Code aus der npm-Registry und führt ihn aus. Eine festgelegte
   Version beschränkt das auf den Code eines Releases, ersetzt aber keine Durchsicht. Die Lizenz
   wird hier nicht wiedergegeben; sie steht im Repository des Projekts.
10. **Keine mitgelieferte Konfiguration.** Fremden Code ohne einen eigenen Schritt von dir zu
    starten ist nicht vertretbar, daher trägt das Plugin den Server nicht ein. Entfernst du den
    Eintrag, fällt die Recherche auf die eingebauten Tools zurück.
