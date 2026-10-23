# Handelsregister-Zugriff

Wer steht hinter einer Anzeige, und gibt es die Firma in der Form, die sie angibt? Das
Handelsregister beantwortet das: Firmenname, Rechtsform, Sitz, Registernummer und
Geschäftsführung. Der quelloffene
[Handelsregister-MCP-Server](https://github.com/lexdoudkin/handelsregister-mcp) von lexdoudkin
(Apache-2.0) lässt Claude eine Firma bei der Recherche im Registerportal nachschlagen, sodass du
das Portal nicht von Hand durchsuchen musst.

!!! note "Bevorzugter Weg zum Register, aber optional und nicht Teil dieses Plugins"
    Ist der Server verbunden und hast du zugestimmt, wird das Register über ihn gelesen und über
    keinen anderen Weg; Websuche und Seitenabruf werden für `handelsregister.de` nicht genutzt,
    weil sie deine Zustimmung und das Budget weiter unten umgehen. Das ist die Arbeitsregel des
    Rechercheverfahrens (`spec/job-application/recherche/en.md`, RC-5.3). Kein Skill dieses Plugins
    braucht den Server, und das Plugin installiert nichts. Ohne ihn funktioniert weiterhin alles:
    Die Recherche sagt es, und du kannst die Registerdaten selbst eintragen oder die Punkte als
    `nicht ermittelt` lassen. Der Server ist ein eigenständiges Projekt und steht weder mit diesem
    Plugin noch mit dem Registerportal in Verbindung.
    Die Regeln, die für alle optionalen Server gelten, stehen auf
    [Optionale MCP-Server](mcp-servers.md).

## Wann die Abfrage angeboten wird

- Nur in Recherchestufe 1 oder 2, nie in Stufe 0.
- Automatisch bei einem Vorgang, dessen Gegenpartei ein Vermittler ist (Personalberatung,
  Personalvermittlung, Zeitarbeit), und für die Firma des Personalvermittlers selbst.
- Bei einem direkten Arbeitgeber nur, wenn du es verlangst.
- Immer mit deinem Ja. Vor der ersten Abfrage eines Vorgangs nennt Claude die Grenzen und Risiken
  weiter unten und wartet. Ein Nein lässt die übrigen Kanäle unberührt; die Registerpunkte bleiben
  `nicht ermittelt`.

## Was die Recherche nutzt

| Bedarf | Tool des Servers |
|---|---|
| Die Firma nach Name, Sitz oder Registernummer finden | `search_company` |
| Registereintrag: Name, Rechtsform, Sitz, Registernummer, Geschäftsführung | `get_company` |
| Aktueller Auszug (nur Dokumenttyp `AD`) | `fetch_document` |
| Ob und wann Jahresabschlüsse eingereicht wurden (nur Existenz und Datum) | `list_filed_documents` |
| Verbleibendes Stundenkontingent | `rate_limit_status` |

Die Recherche nutzt nicht `get_shareholders`, `fetch_filed_document`, `fetch_document` mit einem
anderen Typ als `AD` (`HD`, `CD`, `SI`, `UT`, `VÖ`) und keine Massen- oder Nachbarabfragen. Sie
dienen der Gesellschafterrecherche und dem Profiling, was eine Bewerbung nicht braucht
(RC-5.3 Regel 1).

## Grenzen und Regeln

1. **Budget.** Höchstens 4 Abrufe pro Vorgang in Recherchestufe 1 und höchstens 8 in Stufe 2
   (`rate_limit_status` zählt nicht). Beide Stufen teilen sich ein Budget pro Vorgang, auch über
   Sitzungen hinweg: Der Stand wird aus der Zeile `Kanäle` im Protokoll gelesen. Aufrufe laufen
   nacheinander. Claude erhöht nie die Variable `HANDELSREGISTER_MAX_PER_HOUR` des Servers
   (Standard 60); du kannst die Zahlen senken. Ist das Budget oder das Stundenkontingent
   aufgebraucht, bleiben die offenen Punkte `nicht ermittelt` mit dem Grund `Abrufgrenze erreicht`.
2. **Datensparsamkeit.** Geburtsdaten und private Anschriften von Geschäftsführenden werden nicht
   in `analyse.md` oder eine Firmendatei übernommen. Namen und Funktionen werden nur so weit
   festgehalten, wie die Identitätsprüfung sie braucht (RC-5.3 Regel 5).
3. **Ein Treffer allein bestätigt nichts.** Ein Registertreffer bestätigt die Identität der Firma
   nur zusammen mit dem Impressum. Zwei Firmen mit gleichem Namen werden über Sitz und
   Registernummer getrennt; klären Anzeige oder Impressum nicht, welche gemeint ist, lautet der
   Status `Identität nicht bestätigt`, und du entscheidest (RC-5.3 Regeln 6 und 8).
4. **Ein Fehlschlag ist kein Abbruch.** Eine fehlgeschlagene Abfrage, ein leeres Ergebnis oder
   eine offene Mehrdeutigkeit lässt den Punkt `nicht ermittelt` mit dem Grund, und die Recherche
   läuft weiter (Regel 8).
5. **Protokoll.** Die Zeile `Kanäle` nennt den Weg und die Zahl, etwa
   `Handelsregister über handelsregister-mcp (2 Abrufe)` (bei einem einzigen Abruf `1 Abruf`), oder warum keine Abfrage lief
   (RC-9 Regel 8).

## Was er nicht abdeckt

Der Server liest das Handelsregister. Veröffentlichte Jahresabschlüsse (Unternehmensregister,
Bundesanzeiger) und amtliche Insolvenzbekanntmachungen bleiben Handarbeit: Die Recherche führt sie
als `nicht ermittelt`, oder du schlägst sie selbst nach. Kostenpflichtige Datenanbieter sind hier
ebenfalls nicht abgedeckt.

## Risiken

- **Bedingungen und Recht.** Die README des Servers nennt, dass das Portal automatisierte Abrufe
  begrenzt, setzt eine Grenze von 60 Abrufen pro Stunde und gibt an, dass das Portal warnt,
  automatisierte Massenabfragen könnten strafbar sein. Das sind Aussagen der README, kein
  gesichertes Recht und von dieser Dokumentation nicht bestätigt. Der Einsatz ist deine
  Entscheidung und dein Risiko. Schlage einzelne Firmen nach und nur wenige.
- **Personenbezogene Daten.** Das Register enthält personenbezogene Daten der Geschäftsführung.
  Alles, was der Server liest, wird Teil der Claude-Sitzung und geht wie jeder andere Text darin an
  den Modellanbieter. Halte Geburtsdaten und private Anschriften aus deinen Dateien heraus.
- **Ein junges Projekt.** Das Repository wurde am 2026-06-21 angelegt und hat wenige Mitwirkende.
  Bei der Prüfung am 2026-10-23 war es nicht auf PyPI (HTTP 404 auf pypi.org), es wird also aus
  einem Klon installiert. Prüfe den Code, bevor du ihn ausführst, und pinne einen Commit. Der für
  diese Seite geprüfte Commit ist `26e616beb808bc653ed0504c0c9cd525235082fc` (2026-06-21). Nichts
  aktualisiert den Pin automatisch; lies das Diff, bevor du ihn verschiebst.
- **Änderungen am Portal.** Der Server liest ein laufendes Portal aus. Ändert sich das Portal,
  können Abfragen scheitern oder falsche Felder liefern. Die Recherche fällt dann auf
  `nicht ermittelt` zurück.
- **Das Extra `[ocr]` nicht installieren.** Es zieht PyMuPDF nach (AGPL-3.0 oder kommerzielle
  Lizenz) und wird für die genannten Abfragen nicht gebraucht.

## Einrichten

Maßgeblich für aktuelle Schritte und Optionen ist die
[README des Servers](https://github.com/lexdoudkin/handelsregister-mcp). Kurz: Klone das
Repository, checke den geprüften Commit aus und installiere aus dem Klon ohne das Extra `[ocr]`:

```bash
git clone https://github.com/lexdoudkin/handelsregister-mcp
cd handelsregister-mcp
git checkout 26e616beb808bc653ed0504c0c9cd525235082fc
pip install -e .
```

Registriere ihn dann in Claude Code, wie die README es beschreibt:

```bash
claude mcp add handelsregister -- handelsregister-mcp
```

Prüfe mit `/mcp`, dass der Server verbunden ist. Lass `HANDELSREGISTER_MAX_PER_HOUR` auf dem
Standardwert.
