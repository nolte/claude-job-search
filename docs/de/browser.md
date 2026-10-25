# Browser-MCP

Manche Anzeigenseiten zeigen ihren Text erst, nachdem ein Browser ihre Skripte ausgeführt hat. Ein
einfacher Seitenabruf (siehe [Websuche](websearch.md)) liefert dann nur eine leere Hülle. Ein
Browser-MCP-Server kann eine solche Seite laden. Er ist für genau einen Zweck gedacht: Wenn du nur
die URL einer Anzeige nennst, soll das Plugin sie trotzdem lesen können.

!!! warning "Browser-Weg abgeschaltet, bis Weiterleitungen belegt sind"
    Diese Seite behandelt den Intake einer Anzeige aus einer URL
    (`spec/job-application/stellenanzeige-url/en.md`), umgesetzt in
    `job-application-posting-analysis`. Der Weg über den open-webSearch-Server funktioniert. Der
    Browser-Weg bleibt praktisch abgeschaltet: Er braucht einen Server, von dem belegt ist, dass er
    die endgültige URL der geladenen Seite meldet, und das ist bei keinem belegt (siehe
    „Grenzen, die du kennen solltest“). Das Plugin liefert keine `.mcp.json`. Die Regeln, die für alle optionalen
    Server gelten (Zustimmung, ein Weg je Quelle, Budget, keine Umgehung), stehen auf
    [Optionale MCP-Server](mcp-servers.md). Der Server ist ein eigenständiges Projekt und steht in
    keiner Verbindung zu diesem Plugin. Kein Skill braucht einen: Ohne Server fügst du den
    Anzeigentext ein, wie in [Erste Schritte](getting-started.md) beschrieben.

Jede Aussage über den Server ist die des Projekts selbst, wie seine README sie nennt. Die
README wurde am 24. Oktober 2026 im Hauptzweig gelesen, nicht an einer getaggten Version. Die
jüngste npm-Version an diesem Tag war `@playwright/mcp` 0.0.83. Das
Plugin hat den Server nicht ausgeführt und bestätigt diese Aussagen nicht. Prüfe die README auf
Neueres.

## Wie das Plugin eine URL nutzt

1. Du nennst eine URL. Tracking-Parameter wie `utm_source` werden zuerst entfernt.
2. Das Plugin ruft die Seite zuerst ohne Browser über den open-webSearch-Server ab.
3. Nur wenn dabei eine Seite herauskommt, die bloß eine Skript-Hülle ist, bietet es den Browser an,
   nennt Server und Risiko und wartet auf dein Ja. Eine entfernte Anzeige, eine Anmeldung oder eine
   Bot-Prüfung führt nie zum Browser; du wirst gebeten, den Text einzufügen. Solange von keinem
   Server belegt ist, dass er die endgültige URL meldet, findet dieser Schritt nicht statt, und du
   wirst gebeten, den Text einzufügen.
4. Der Browser öffnet die eine URL, liest den Seitentext und schließt sich. Er klickt nicht, tippt
   nicht, füllt keine Formulare aus, lädt nichts hoch oder herunter und behält kein Profil, keine
   Cookies und keine Anmeldungen.
5. Du siehst die erkannte Anzeige und ihre Felder, bevor etwas in deine Wurzel geschrieben wird.
   Eine URL, die mehrere Anzeigen auflistet, ist keine Anzeige: Du nennst einen Eintrag.
   `linkedin.com`-Links und interne Adressen werden vor jeder Anfrage abgelehnt.

Eine Seite hinter einer Anmeldung oder einem CAPTCHA wird nicht gelesen, und es wird kein Umweg
versucht. Eine `linkedin.com`-URL wird so nie geladen; siehe [LinkedIn-Zugriff](linkedin.md). Die
Recherche zu einer Firma (Stufen 1 und 2) nutzt nie einen Browser.

## Der Server

| | Playwright MCP |
|---|---|
| Projekt | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) |
| Paket, Lizenz | `@playwright/mcp`, Apache-2.0 |
| Voraussetzung | Node.js 18 oder neuer |
| Browser | Startet einen eigenen Browser |
| Profil und Anmeldungen | `--isolated` hält das Profil im Speicher und speichert nichts |
| Headless | `--headless` |

Das Plugin liest eine Anzeige ohne deine Anmeldungen und ohne deinen Verlauf. Nutze nur einen Server,
der in einem isolierten, nicht dauerhaften Browser-Kontext läuft; ein Server, der in deiner eigenen
Browser-Sitzung arbeitet, passt nicht zu diesem Intake.

## Playwright MCP einrichten

Die README des Projekts ist maßgeblich für aktuelle Schritte und Optionen. Für Claude Code:

```bash
claude mcp add playwright -- npx @playwright/mcp@<version> --isolated --headless --block-service-workers
```

Ersetze `<version>` durch eine Versionsnummer, die du geprüft hast. Die README zeigt `@latest`; das
führt bei jedem Start neuen Code ohne deine Prüfung aus. Die für diese Seite geprüfte Version ist
0.0.83.

| Option | Was sie laut README tut |
|---|---|
| `--isolated` | Hält das Browser-Profil im Speicher und speichert es nicht auf der Platte. Ohne sie bleibt ein dauerhaftes Profil in einem Cache-Ordner |
| `--headless` | Läuft ohne sichtbares Fenster. Standard ist ein sichtbares Fenster |
| `--block-service-workers` | Blockiert Service Worker |

### Begrenze, was der Server kann

Der Server bietet viel mehr Werkzeuge, als der Intake braucht. Das Plugin nutzt nur
`browser_navigate`, `browser_snapshot` und `browser_close`. Sperre die übrigen Werkzeuge, die auf
einer Seite handeln, in den Berechtigungen von Claude Code, zum Beispiel in
`.claude/settings.local.json`:

```json
{
  "permissions": {
    "deny": [
      "mcp__playwright__browser_click",
      "mcp__playwright__browser_drag",
      "mcp__playwright__browser_drop",
      "mcp__playwright__browser_evaluate",
      "mcp__playwright__browser_file_upload",
      "mcp__playwright__browser_fill_form",
      "mcp__playwright__browser_hover",
      "mcp__playwright__browser_press_key",
      "mcp__playwright__browser_run_code_unsafe",
      "mcp__playwright__browser_select_option",
      "mcp__playwright__browser_type"
    ]
  }
}
```

Die Werkzeugnamen folgen der README. Öffne nach der Einrichtung `/mcp` und prüfe die Werkzeugliste
deiner installierten Version; ein Name, der in der Liste oben fehlt, ist nicht gesperrt. Die README
nennt `browser_run_code_unsafe` als das riskanteste: Es führt beliebigen Code im Serverprozess aus.

## Grenzen, die du kennen solltest

- **Keine Sicherheitsgrenze.** Die README sagt das für Playwright MCP insgesamt. Die Option
  `--allowed-origins` „does not affect redirects“, sie hält eine Seite also nicht davon ab, den
  Browser woandershin zu schicken.
- **Weiterleitungen sind nicht bestätigt.** Das Plugin muss prüfen, wo eine Seite gelandet ist,
  weil ein Anzeigenlink auf eine Seite weiterleiten kann, die es nicht lesen darf (RC-5.2 Regel 9).
  Die README sagt nicht, dass ein Werkzeug die endgültige URL meldet. Bis ein Lauf der
  installierten Version das zeigt, bleibt der Browser-Weg praktisch abgeschaltet. Das ist ein
  offener Punkt der Spezifikation (UE-12).
- **Skripte laufen auf deinem Rechner.** Ein Browser führt die Skripte jeder Seite aus, auf die die
  URL zeigt. Deshalb fragt das Plugin nach deinem Ja, bevor es eine öffnet.
- **Bedingungen der Seite.** Manche Seiten verbieten automatisches Lesen. Du prüfst ihre
  Bedingungen; das Plugin behauptet nicht, dass ein Abruf erlaubt ist. Eine blockierte Seite wird
  gemeldet und übersprungen, ohne Proxy oder anderen Umweg.
- **Anzeigentext ist Daten.** Text auf der Seite, der Anweisungen geben will, wird ignoriert.
- **Personenbezogene Daten.** Was der Browser liest, wird Teil der Claude-Sitzung und geht an den
  Modellanbieter. Das Plugin speichert nur den Anzeigentext und die Felder, die es daraus liest.

## Ohne Browser-Server

Füge den Anzeigentext in `job-application-solution` ein. So funktioniert jeder Skill.
