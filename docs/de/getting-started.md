# Erste Schritte

Diese Seite führt dich vom leeren Ordner bis zur ersten geprüften Bewerbung. Du brauchst Claude
Code und einen Ordner für deine Bewerbungsdaten. Entwicklerwerkzeuge sind für die Schritte unten
nicht nötig; der PDF-Export ist der einzige optionale Schritt mit zusätzlicher Software, siehe
[Export](export.md).

## 1. Plugin installieren

Wähle einen von drei Wegen.

**Über den Marketplace, je Projekt.** Trage den Marketplace ein und aktiviere das Plugin in der
`.claude/settings.json` des Ordners, in dem du arbeitest:

```json
{
  "extraKnownMarketplaces": {
    "claude-job-search": {
      "source": {
        "source": "github",
        "repo": "nolte/claude-job-search"
      }
    }
  },
  "enabledPlugins": {
    "job-application@claude-job-search": true
  }
}
```

**Interaktiv.** Führe in Claude Code `/plugin` aus, füge den Marketplace
`nolte/claude-job-search` hinzu und installiere daraus `job-application`.

**Aus einem lokalen Checkout.** Klone das Repository und starte Claude Code mit
`claude --plugin-dir <Pfad-zum-Checkout>`.

Danach stehen die Skills als `/job-application:<skill>` bereit, zum Beispiel
`/job-application:job-application-solution`.

## 2. Konfiguration anlegen

Das Plugin liest genau eine Datei an fester Stelle: `job-application/konfiguration.md` in dem
Ordner, in dem du Claude Code startest. Alles andere findet es über diese Datei. Sie hat ein
kurzes Frontmatter und darf darunter freie Notizen enthalten.

**Minimal, eine Datei als Datengrundlage.** Alle Bewerbungsdaten liegen in `job-application/`;
die Datengrundlage ist eine Markdown-Datei:

```markdown
---
grundlage: job-application/grundlage/lebenslauf-chronologisch.md
---

# Konfiguration
```

**Verzeichnismodus mit einem Obsidian-Vault außerhalb der Wurzel.** Die Datengrundlage ist ein
Ordner mit Notizen, eine je Station, plus eine Indexnotiz mit dem Pflegeverlauf:

```markdown
---
wurzel: /home/ich/bewerbungen
grundlage: /home/ich/vault/lebenslauf
grundlage_index: /home/ich/vault/metadata/Lebenslauf.md
---

# Konfiguration

Bewerbungen in `/home/ich/bewerbungen`, die Datengrundlage in meinem Obsidian-Vault.
```

Die Schlüssel:

| Schlüssel | Nötig | Bedeutung |
|---|---|---|
| `wurzel` | optional | Wurzel aller Bewerbungsdaten. Standard: `job-application/` neben der Konfiguration. Darf überall auf deiner Platte liegen, auch in einem Ordner eines Obsidian-Vaults. |
| `grundlage` | optional | Deine Datengrundlage: eine Markdown-Datei oder ein Verzeichnis mit Notizen. Standard: `<wurzel>/grundlage/lebenslauf-chronologisch.md`. |
| `grundlage_index` | nur bei einem Verzeichnis | Die Indexnotiz des Verzeichnisses mit dem Pflegeverlauf. |

Relative Pfade werden gegen den Ordner aufgelöst, der `job-application/konfiguration.md`
enthält. Startest du einen Skill ohne diese Datei, fragt er die Pfade einmal ab und legt die
Datei für dich an.

!!! warning "Nicht im Plugin-Repository"
    Die Wurzel darf nicht in einem Checkout des Plugins selbst liegen. Wenn du das Plugin
    entwickelst und dich damit bewirbst, setze `wurzel` auf einen Ordner außerhalb des Checkouts.

## 3. Daten erfassen

Lege dein Rohmaterial in `<wurzel>/rohdaten/` ab: alte Lebensläufe, Zeugnisse, einen
LinkedIn-Export, Notizen. Hast du den optionalen LinkedIn-Server verbunden, zeigt
[LinkedIn-Zugriff](linkedin.md), wie du dein eigenes Profil einbringst. Dann führe aus:

```text
/job-application:job-application-profile-capture
```

Der Skill liest das Rohmaterial, fragt nach, wo er unsicher ist, und schreibt die
Datengrundlage (deine Stationen, Ausbildung, Kenntnisse, Sprachen, Zeugnisse, jeweils mit
Quelle) sowie das daraus abgeleitete `profil.md`. Was er nicht belegen kann, markiert er mit
`[ERGÄNZEN: …]`; die Markierung bleibt sichtbar, bis du sie auflöst. Spätere Änderungen laufen
über `/job-application:job-application-cv-maintain`, das nur nach Befunden fragt und jede
Änderung im Pflegeverlauf festhält.

## 4. Optional: sagen, was du suchst

```text
/job-application:job-application-traumjob-interview
```

Ein Interview in sieben Phasen, das deine Wünsche, Prioritäten und Vetos als `wunschprofil.md`
festhält. Geschrieben wird erst, wenn du die Zusammenfassung bestätigst. Mit einem bestätigten
Wunschprofil vergleicht `/job-application:job-application-fit-check` eine Stelle oder eine
Firma damit, bevor du Zeit in Unterlagen steckst, und ein Veto stoppt den Plan in Schritt 5.

## 5. Die erste Bewerbung

```text
/job-application:job-application-solution
```

Füge den Text der Stellenanzeige ein oder gib den Link an. Ein Link allein genügt: Der Skill
entfernt Tracking-Parameter, lädt die Seite über den optionalen open-webSearch-Server und zeigt dir
die erkannte Anzeige zur Bestätigung, bevor etwas gespeichert wird. Lässt sich die Seite nicht
lesen (entfernt, Anmeldung, Bot-Prüfung, braucht JavaScript, kein Server verbunden), wirst du
gebeten, den Text einzufügen. LinkedIn-Links werden nie geladen. Der Skill

1. prüft, ob Datengrundlage und Profil aktuell sind,
2. legt den Bewerbungsordner an und analysiert die Anzeige (welche Anforderungen du belegt
   erfüllst, welche teilweise, welche nicht abgedeckt sind),
3. ordnet die Gegenpartei ein (Arbeitgeber direkt, Headhunter, Vermittler, Plattform,
   Empfehlung), siehe [Gegenpartei](counterparts.md),
4. zeigt dir einen **Plan**: welche Unterlagen in welchem Format, welche Stationen und
   Stichpunkte er verwendet, welche Lücken bleiben,
5. wartet auf deine Freigabe,
6. erstellt die Unterlagen in Reihenfolge (Lebenslauf, dann Anschreiben, dann die E-Mail, wenn
   du dich per E-Mail bewirbst) und
7. führt die Qualitätsprüfung aus.

Der Plan ist eine Schranke, keine Formsache: Kein Dokument entsteht, bevor du Ja sagst. Passt
der Plan nicht, sagst du, was anders sein soll, und der Skill zeigt einen neuen Plan.

## 6. Was im Bewerbungsordner liegt

Jede Bewerbung bekommt einen Ordner unter der Wurzel, benannt nach Firma und Stelle, zum
Beispiel `musterfirma-senior-backend/`:

| Datei | Inhalt | Geschrieben von |
|---|---|---|
| `vorgang.md` | Firma, Stelle, Referenznummer, Bewerbungsweg, Status, Daten, der freigegebene Plan, der Verlauf | den Skills für ihre Schritte; von dir für Versand und alles danach |
| `notizen.md` | Deine freien Notizen: Eindrücke, Fragen für das Gespräch, Namen aus Telefonaten | nur von dir; kein Skill ändert sie |
| `stellenanzeige.md` | Die Anzeige im Wortlaut | Stellenanalyse |
| `analyse.md` | Anforderungsabgleich mit Belegen, die Gegenpartei, die beteiligten Firmen | Stellenanalyse |
| `passung.md` | Passung zu deinem Wunschprofil, nur wenn du die Passungsprüfung ausgeführt hast | Passungsprüfung |
| `lebenslauf.md` | Der Lebenslauf für diese Bewerbung | Lebenslauf-Skill |
| `anschreiben.md` | Das Anschreiben | Anschreiben-Skill |
| `motivationsschreiben.md` | Nur wenn verlangt | Motivationsschreiben-Skill |
| `email.md` | Nur bei Bewerbung per E-Mail | E-Mail-Skill |
| `pruefbericht.md` | Welche Stationen ausgewählt wurden und warum; das Ergebnis der Qualitätsprüfung | Lebenslauf-Skill, Qualitätsprüfung |
| `export/` | PDF, DOCX, HTML, nur wenn du einen Export anforderst | Export-Skill |

Neben den Bewerbungsordnern liegen `grundlage/` (wenn deine Datengrundlage dort liegt),
`profil.md`, `wunschprofil.md`, `rohdaten/`, `firmen/` (eine Datei je Firma mit festen Fakten
und deinen Notizen) und die Lebenslauf-Ausprägungen. Eine **Ausprägung** ist ein Lebenslauf mit
eigenem Schwerpunkt, den du über mehrere Bewerbungen wiederverwendest, etwa
`lebenslauf-basis/` oder `lebenslauf-teamleitung/`. Jeder Ausprägungsordner enthält sein
`lebenslauf.md`, sein `pruefbericht.md`, eingefrorene Versionen in `versionen/` und deren
Exporte in `export/`.

## 7. Status pflegen und Übersicht

`vorgang.md` trägt ein Feld `status` mit festen Werten. Die ersten Werte setzen die Skills; ab
dem Versand setzt du sie selbst:

| Setzen die Skills | Setzt du |
|---|---|
| `erfasst` (Anzeige erfasst), `analysiert`, `geplant` (Plan freigegeben), `erstellt` (Unterlagen erstellt), `geprüft` (Qualitätsprüfung bestanden) oder `in Arbeit` (Blocker offen) | `versendet`, `rückmeldung`, `gespräch`, `angebot`, `verhandlung`, `zusage`, `absage`, `abgelehnt` (du hast abgesagt), `zurückgezogen`, `ohne Antwort`, `abgeschlossen` |

Jede Statusänderung bekommt eine Zeile im Abschnitt *Verlauf* von `vorgang.md` mit Datum, damit
die Geschichte lesbar bleibt. Beim Versand trägst du dort auch Datum, Weg und Anhänge ein;
`wiedervorlage` hält das Datum deiner nächsten Nachfrage. Freier Text gehört in `notizen.md`.

**Übersicht über alle Bewerbungen.** Ist deine Wurzel ein Obsidian-Vault (oder ein Ordner
darin), listet eine Bases-Datei alle Bewerbungen nach Status, ohne zusätzliches Plugin.
Speichere sie als `bewerbungen.base` im Vault:

```yaml
filters:
  and:
    - 'file.name == "vorgang"'

properties:
  firma:
    displayName: Firma
  stelle:
    displayName: Stelle
  status:
    displayName: Status
  wiedervorlage:
    displayName: Wiedervorlage

views:
  - type: table
    name: Offen
    filters:
      and:
        - 'status != "zusage"'
        - 'status != "absage"'
        - 'status != "abgelehnt"'
        - 'status != "zurückgezogen"'
        - 'status != "ohne Antwort"'
        - 'status != "abgeschlossen"'
    groupBy:
      property: status
      direction: ASC
    order:
      - firma
      - stelle
      - status
      - wiedervorlage
      - file.folder

  - type: table
    name: Abgeschlossen
    filters:
      or:
        - 'status == "zusage"'
        - 'status == "absage"'
        - 'status == "abgelehnt"'
        - 'status == "zurückgezogen"'
        - 'status == "ohne Antwort"'
        - 'status == "abgeschlossen"'
    order:
      - firma
      - stelle
      - status
      - loeschen_ab
      - file.folder
```

Öffne die Datei in Obsidian: Die erste Ansicht gruppiert die offenen Bewerbungen nach Status,
die zweite listet die abgeschlossenen mit ihrem Löschdatum. Ohne Obsidian liefert
`grep -r "^status:" */vorgang.md` in der Wurzel dieselbe Liste auf der Kommandozeile.

## 8. Export auf Wunsch

Unterlagen bleiben Markdown, bis du einen Export anforderst. Führe
`/job-application:job-application-export` oder `task export` aus für eine PDF-, DOCX-, HTML-
oder Markdown-Kopie. Eine Text-PDF ist der Standard, auch für Bewerbungsportale; DOCX erzeugst
du nur, wenn ein Portal es ausdrücklich verlangt. Details, Voraussetzungen und der Container,
der alles mitbringt, stehen auf der Seite [Export](export.md).

## 9. Aufbewahrung und Löschung

Eine abgeschlossene Bewerbung behält ihren Ordner. Bei jedem Endstatus außer `zusage` sollen
die Daten sechs Monate nach Abschluss gelöscht werden: Setze beim Abschluss `loeschen_ab` in
`vorgang.md` auf dieses Datum. Kein Skill löscht etwas; die Löschung ist dein Schritt, und die
Bases-Ansicht oben zeigt dir, welche Daten erreicht sind.

!!! info "Für Entwickler"
    Die Regeln hinter dieser Seite: `spec/job-application/lokale-struktur/en.md` (Begriffe, Layout,
    Konfigurationsschlüssel, Lifecycle und Statuswerte, Aufbewahrung),
    `spec/job-application/konventionen/en.md` (Faktentreue, Datenschutz, Ausgabeformate),
    `spec/job-application/lebenslauf-versionen/en.md` (Ausprägungen und eingefrorene Versionen),
    `spec/job-application/traumjob-interview/en.md` (Wunschprofil und Passung),
    `spec/job-application/kontaktklassifikation/en.md` (Gegenpartei).
