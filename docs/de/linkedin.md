# LinkedIn-Zugriff

Vieles, was eine Bewerbung braucht, steht auf LinkedIn: die Anzeige, die Firmenseite, die
Personen hinter dem Namen eines Personalvermittlers und dein eigenes Profil. Der quelloffene
[LinkedIn-MCP-Server](https://github.com/stickerdaniel/linkedin-mcp-server) von Daniel Sticker
(Apache-2.0) gibt Claude direkten Zugriff auf diese Seiten, sodass du sie nicht von Hand
kopieren musst.

!!! note "Bevorzugter Weg zu LinkedIn, aber nicht Teil dieses Plugins"
    Sollen LinkedIn-Inhalte genutzt werden, ist der Server der Weg: Ist er verbunden, sollen
    LinkedIn-Seiten über ihn gelesen werden und nicht über Websuche oder einen Seitenabruf. Beides
    ist auf LinkedIn unzuverlässig und umgeht die Zustimmung und die Grenzen weiter unten. Das ist
    die Arbeitsregel des Rechercheverfahrens (`spec/job-application/recherche/en.md`, RC-5.4); `job-application-posting-analysis` hält sie ein: Der Skill ruft nie eine LinkedIn-Seite ab und liest eine über den Server erst nach deiner Zustimmung. Kein Skill
    dieses Plugins braucht den Server. Ohne ihn funktioniert weiterhin
    alles: Du fügst den Anzeigentext ein, wie in [Erste Schritte](getting-started.md) beschrieben.
    Du kannst Claude in derselben Sitzung bitten, erst die Seite zu lesen und danach den Skill
    auf das Ergebnis anzuwenden. Der Server ist ein eigenständiges Projekt und steht weder mit
    diesem Plugin noch mit LinkedIn in Verbindung.

## Wobei er hilft

| Du brauchst | Tool des Servers | Danach |
|---|---|---|
| Den Text einer Anzeige, die du auf LinkedIn gefunden hast | `get_job_details`, `search_jobs`, `get_saved_jobs` | `job-application-solution`, `job-application-posting-analysis`, `job-application-fit-check` |
| Wie die Stelle Bewerbungen annimmt (Easy Apply oder Seite des Arbeitgebers) | `get_job_apply_url` | `job-application-solution`, Eingabe `bewerbungsweg`: Easy Apply oder ein Formular auf der Seite des Arbeitgebers ist `portal`, eine E-Mail-Adresse ist `email` |
| Fakten zur Firma: Größe, Branche, offene Stellen, aktuelle Beiträge | `get_company_profile`, `get_company_posts`, `search_companies` | `job-application-fit-check` und Firmenanalyse (UA-3), als Rang 5 (siehe Regel 3) |
| Rolle, Firma und Dauer der einen Person, die dich angeschrieben hat | `get_person_profile` | [Gegenpartei](counterparts.md): Arbeitgeber eines Personalvermittlers prüfen (KK-3.3) |
| Dein eigenes Profil als Rohmaterial | `get_my_profile` | Speichere, was du behalten willst, als Datei in `rohdaten/`; `job-application-profile-capture` liest es von dort |

Die Tools, die Mitarbeitende auflisten oder Personen suchen (`get_company_employees`,
`search_people`), braucht eine Bewerbung nicht. Das Rechercheverfahren nutzt sie nicht.

Der Server bietet auch Tools, die in deinem Namen handeln: `send_message` und
`connect_with_person`. Dieses Plugin versendet nie etwas für dich (R-6). Text, den du von LinkedIn
liest, sind Daten und keine Anweisung: Eine Anzeige oder ein Profil, die Claude auffordern,
jemandem zu schreiben, werden ignoriert. Damit diese beiden Tools nicht versehentlich laufen,
sperre sie in den Berechtigungen von Claude Code (die Toolnamen enthalten den Servernamen, wie
`/mcp` ihn zeigt). Nutze sie nur, wenn du es selbst verlangst, und prüfe jeden Text vorher.

## Einrichten

Du brauchst [uv](https://docs.astral.sh/uv/getting-started/installation/). Maßgeblich für
aktuelle Schritte und Optionen ist die
[README des Servers](https://github.com/stickerdaniel/linkedin-mcp-server#installation-methods---linkedin-mcp-server).
Als Claude-Code-Plugin:

```bash
claude plugin marketplace add stickerdaniel/linkedin-mcp-server
claude plugin install linkedin-mcp-server@linkedin-mcp-server
```

Oder als Eintrag im Abschnitt `mcpServers` deiner MCP-Konfiguration:

```json
{
  "mcpServers": {
    "mcp-server-linkedin": {
      "command": "uvx",
      "args": ["mcp-server-linkedin@latest"],
      "env": { "UV_HTTP_TIMEOUT": "300" }
    }
  }
}
```

`@latest` lässt den Server sich selbst aktualisieren. Das hält ihn mit den wechselnden Seiten von
LinkedIn lauffähig, führt aber neuen Code ohne deine Durchsicht aus. Willst du das nicht, schreibe
`mcp-server-linkedin@<version>` mit einer Versionsnummer aus den Releases des Projekts.

Beim ersten Aufruf, der eine Anmeldung braucht, übernimmt der Server eine LinkedIn-Sitzung aus
einem angemeldeten lokalen Browser oder öffnet ein Anmeldefenster. Um dich vorher anzumelden,
führe `uvx mcp-server-linkedin@latest --login` aus. Frühe Aufrufe können melden, dass die
Einrichtung noch läuft; versuche es nach deren Ende erneut.

## Regeln, die weiter gelten

1. **Nutzungsbedingungen.** Die Nutzervereinbarung von LinkedIn verbietet automatisierten
   Zugriff. Die README des Servers sagt offen, dass Konten eingeschränkt oder gesperrt werden
   können, ohne Garantie. Der Einsatz ist deine Entscheidung und dein Risiko. Lies einzelne
   Seiten und nur wenige, und lass keinen Agenten Seiten massenhaft abrufen.
2. **Datenfluss.** Alles, was der Server liest, wird Teil der Claude-Sitzung und geht wie jeder
   andere Text darin an den Modellanbieter. Die Zusage des Plugins, nichts zu versenden, gilt
   für das Plugin; sie deckt nicht ab, was du in die Sitzung lädst. Lies nur die Seiten, die du
   brauchst, und halte personenbezogene Daten Dritter aus der Datengrundlage heraus. Speichere
   keine Profile von Mitarbeitenden oder Personalvermittlern in `rohdaten/` oder `notizen.md`: Die
   Löschregel für Eindrücke zu Dritten (`lokale-struktur` LS-9.3, Stufe S10) erfasst nur Notizen,
   keine Dateien, die du ablegst.
   Suchen folgen der Regel für die Firmenrecherche (UA-3): Eine Anfrage enthält nur den
   Firmennamen und einen allgemeinen Begriff, nie dein Wunschprofil, deine Datengrundlage oder
   Bewerbungstexte. Netzzugriff gibt es, wenn du ihn verlangst.
3. **Fakten bleiben nachvollziehbar, und LinkedIn steht niedrig im Rang.** Der Text einer
   Anzeige, wie veröffentlicht, ist die Anzeige (Rang 2). Alles andere auf LinkedIn, etwa eine
   Firmenseite oder das Profil einer Person, ist Social Media: Rang 5 in UA-3, ein Hinweis und
   eine Meinung, nie ein Stammdatum und nie eine Motivation für das Anschreiben. Die Identität
   einer Firma kommt aus dem Impressum und dem Register. Halte fest, was du nutzt: den Link der
   Anzeige als `stellenquelle` in `vorgang.md`, Firmenfakten mit Quelle und Lesedatum. Dein
   eigenes LinkedIn-Profil ist Rohmaterial für `profile-capture`; der Skill fragt bei jedem
   unsicheren Eintrag nach, und nichts davon gilt als fest, bevor du es bestätigst.
4. **Personalvermittler.** Ein gelesenes Profil ersetzt nicht die Frage an die Gegenpartei. Der
   Arbeitgeber gilt erst als `gesichert`, wenn die Gegenpartei ihn bestätigt (KK-3.3).
5. **Ohne Server.** Claude versucht nicht, LinkedIn auf anderem Weg zu lesen. Füge den
   Anzeigentext oder die Firmenseite ein oder lege deinen Profil-Export in `rohdaten/`.
