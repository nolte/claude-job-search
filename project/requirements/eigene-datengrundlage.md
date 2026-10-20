---
title: Eigene Datengrundlage für Bewerbungsunterlagen
status: draft
created: 2026-10-20
---

# Anforderung: Eigene Datengrundlage für Bewerbungsunterlagen

## Ausgangslage

Die Skills dieses Plugins erzeugen Bewerbungsunterlagen aus einem Profil. Bisher ist
dieses Profil ein Artefakt des Repositories bzw. des Entwicklers. Jeder Nutzer soll
die Skills aber in der eigenen Struktur verwenden können. Dazu muss jeder Nutzer
seine eigene Datengrundlage schaffen können.

Die Originaldaten (Lebensläufe, Zeugnisse, Notizen, Projektbeschreibungen) werden
einmalig zu einer **vollständigen, chronologischen Datengrundlage** aufgearbeitet.
Aus dieser Grundlage entstehen die gezielten Ausgaben pro Stelle (Lebenslauf,
Anschreiben, E-Mail). Die Grundlage ist also der Übergang von den Rohdaten zu den
Zielausgaben.

## Begriffe

| Begriff | Bedeutung |
|---|---|
| **Rohdaten** | Vorhandene Unterlagen des Nutzers in beliebigem Format (PDF, DOCX, Markdown, Notizen, Zeugnisse, LinkedIn-Export). |
| **Datengrundlage** | Ausführliche, chronologische Sammlung aller relevanten Fakten des Nutzers in Markdown. Liegt im Arbeitsverzeichnis des Nutzers. |
| **Profil** | Aus der Datengrundlage abgeleitete, verdichtete Faktenbasis, die die Skills lesen (`bewerbung/profil.md`). |
| **Zielausgaben** | Stellenspezifische Dokumente: gezielter Lebenslauf, Anschreiben, Bewerbungs-E-Mail, Prüfbericht. |

## Ziel

Der Nutzer legt eine eigene, vollständige Datengrundlage an. Aus ihr erzeugen die
Skills gezielte Bewerbungen. Die Grundlage kann für beliebig viele Bewerbungen
wiederverwendet und über die Zeit gepflegt werden.

## Ablauf (Datenfluss)

```text
Rohdaten (beliebiges Format)
   │  Aufarbeitung (einmalig, danach fortschreibend)
   ▼
Datengrundlage  bewerbung/grundlage/lebenslauf-chronologisch.md   ← Quelle der Wahrheit
   │  Ableitung (Verdichtung, Quellenverweise)
   ▼
Profil          bewerbung/profil.md
   │  Stellenanalyse (pro Bewerbung)
   ▼
Zielausgaben    lebenslauf.md · anschreiben.md · email.md · pruefbericht.md
```

## Anforderungen

### Funktionale Anforderungen

**FA-1 Vorlage für die Datengrundlage**
Das Plugin stellt eine Markdown-Vorlage bereit, die den Nutzer durch die vollständige
chronologische Erfassung führt: Berufsstationen, Ausbildung, Schule, Weiterbildung,
Projekte, Kenntnisse, Sprachen, Ehrenamt. Pro Station sind Zeitraum, Rolle, Arbeitgeber,
Aufgaben, Ergebnisse und eingesetzte Werkzeuge vorgesehen.

- *Akzeptanz:* Die Vorlage enthält für jede Station die Felder aus FA-1 und einen
  Platzhalter `[ERGÄNZEN: …]` für fehlende Angaben. Ein Beispieleintrag ist enthalten.

**FA-2 Eigene Struktur des Nutzers**
Die Datengrundlage liegt im Arbeitsverzeichnis des Nutzers. Ort und Dateiname sind
festgelegt (Standard: `bewerbung/grundlage/`), können aber vom Nutzer geändert werden.
Die Skills finden die Grundlage über diesen Pfad und sind nicht an ein bestimmtes
Repository oder eine bestimmte Person gebunden.

- *Akzeptanz:* Ein Nutzer ohne Zugriff auf das Entwicklungs-Repository kann die Skills
  mit einer selbst erstellten Grundlage verwenden. Im Plugin-Code und in den Skills
  steht kein persönlicher Fakt.

**FA-3 Aufarbeitung vorhandener Rohdaten**
Ein Skill übernimmt vorhandene Unterlagen des Nutzers und überführt sie in die Vorlage
aus FA-1. Er ordnet Inhalte den Stationen zu, sortiert chronologisch und markiert
Widersprüche und Lücken, statt sie zu glätten.

- *Akzeptanz:* Aus einem bestehenden Lebenslauf (PDF oder DOCX) entsteht eine Grundlage,
  bei der jeder Eintrag auf die Rohdatenstelle verweist. Widersprüche (z. B. zwei
  unterschiedliche Zeiträume) sind als `[KLÄREN: …]` markiert.

**FA-4 Informationsverlust vermeiden**
Die Aufarbeitung übernimmt Inhalte vollständig. Kürzungen sind nur in der abgeleiteten
Ansicht zulässig, nie in der Datengrundlage selbst.

- *Akzeptanz:* Jede Information aus den Rohdaten ist in der Datengrundlage enthalten
  oder ausdrücklich als nicht relevant markiert.

**FA-5 Ableitung des Profils**
Das Profil (`bewerbung/profil.md`) wird aus der Datengrundlage erzeugt. Jeder Eintrag
im Profil verweist auf seine Stelle in der Datengrundlage.

- *Akzeptanz:* Ein Profil-Eintrag ohne Quellenverweis ist ein Fehler. Die Prüfung
  (`bewerbung-pruefen`) meldet ihn als Blocker.

**FA-6 Gezielte Zielausgaben**
Lebenslauf, Anschreiben und E-Mail werden pro Stelle aus dem Profil erzeugt. Auswahl,
Reihenfolge und Gewichtung richten sich nach der Stellenanzeige. Die Aussagen selbst
kommen ausschließlich aus der Datengrundlage.

- *Akzeptanz:* Zwei Bewerbungen aus derselben Grundlage unterscheiden sich in Auswahl
  und Gewichtung, nicht in den Fakten.

**FA-7 Nachvollziehbarkeit der Ausgaben**
Jede faktische Aussage in einer Zielausgabe ist auf einen Eintrag der Datengrundlage
rückführbar. Der Prüfbericht zeigt diese Zuordnung.

- *Akzeptanz:* `bewerbungs-reviewer` und `bewerbung-pruefen` können für jede Aussage
  den Quelleintrag nennen.

**FA-8 Wiederverwendung und Pflege**
Die Datengrundlage ist für viele Bewerbungen nutzbar. Sie trägt ein Datum der letzten
Änderung. Ändert sich die Grundlage, werden Zielausgaben, die auf einer älteren Fassung
beruhen, als veraltet gekennzeichnet.

- *Akzeptanz:* Ein Prüflauf meldet Zielausgaben, deren Stand älter ist als die
  Datengrundlage.

**FA-9 Pflege statt Neuaufbau**
Ein Skill ergänzt oder korrigiert eine bestehende Datengrundlage gezielt, etwa nach
einer neuen Station. Er erstellt keine neue Grundlage, wenn bereits eine existiert.

- *Akzeptanz:* Eine bestehende Grundlage bleibt beim Ergänzen unverändert, bis auf die
  angefragten Einträge.

### Nicht-funktionale Anforderungen

**NFA-1 Datenschutz**
Datengrundlage, Profil und Zielausgaben liegen lokal im Arbeitsverzeichnis und sind
von Git ausgeschlossen (`bewerbung/`).

**NFA-2 Keine erfundenen Fakten**
Fakten entstehen nur aus Rohdaten oder aus Angaben des Nutzers. Fehlende Angaben werden
markiert (Spec `spec/bewerbung/konventionen/en.md`, R-1).

**NFA-3 Portables Format**
Die Datengrundlage ist reines Markdown mit einfacher Struktur (Überschriften, Listen,
Tabellen). Sie kann ohne Plugin gelesen und bearbeitet werden.

**NFA-4 Sprache**
Die Datengrundlage kann auf Deutsch geführt werden. Originaldaten in anderer Sprache
bleiben in dieser Sprache, werden aber als solche gekennzeichnet.

### Beispielausschnitt der Datengrundlage

```markdown
---
stand: 2026-10-20
---

# Chronologischer Lebenslauf — Grundlage

## Berufliche Stationen

### 2021-04 – heute · Senior Backend-Entwickler · Musterfirma GmbH, Berlin
- Quelle: `rohdaten/lebenslauf-2025.pdf`, S. 1
- Aufgaben: Betreuung der Event-Pipeline (Python, Kafka)
- Ergebnisse: Latenz der Verarbeitung von 800 ms auf 120 ms gesenkt [KLÄREN: Messmethode]
- Werkzeuge: Python, Kafka, PostgreSQL, Kubernetes

### 2018-09 – 2021-03 · Softwareentwickler · Beispiel AG, Hamburg
- Quelle: `rohdaten/lebenslauf-2025.pdf`, S. 1
- Aufgaben: [ERGÄNZEN: Aufgaben]
```

## Auswirkungen auf bestehende Bausteine

| Baustein | Änderung |
|---|---|
| `bewerbung-profil-erfassen` | Erzeugt die Datengrundlage aus Rohdaten bzw. Interview (FA-1, FA-3, FA-9) und leitet daraus das Profil ab (FA-5). |
| `bewerbung-lebenslauf-erstellen` | Liest das Profil; Quellenverweise bleiben intern erhalten (FA-7). |
| `bewerbung-anschreiben-erstellen`, `bewerbung-email-erstellen` | Unverändert in der Logik; lesen weiterhin das Profil. |
| `bewerbung-pruefen` | Zusätzlich: Quellenverweise (FA-5, FA-7) und Stand gegenüber der Grundlage (FA-8). |
| `bewerbung-solution` | Prüft als Erstes, ob eine Datengrundlage existiert; sonst Start bei `bewerbung-profil-erfassen`. |
| `bewerbungs-reviewer` | Prüft Aussagen gegen Quelleinträge (FA-7). |
| `spec/bewerbung/konventionen/en.md` | Neues Kapitel „Datengrundlage“ mit den Regeln aus FA-1 bis FA-9 und NFA-1 bis NFA-4. |

## Nicht-Ziele

- Import aus Online-Profilen (z. B. LinkedIn-API). Ein manueller Export als Rohdatei ist erlaubt.
- Speicherung in einer Cloud oder Datenbank.
- Automatische Veröffentlichung oder Versand von Bewerbungen.
- Mehrere Personen in einer Datengrundlage.

## Offene Fragen

1. Soll die Datengrundlage mehrsprachig geführt werden (DE/EN), oder genügt eine Hauptsprache?
2. Wie werden Zeugnisse in der Grundlage erfasst: nur als Verweis oder mit extrahiertem Wortlaut?
3. Soll die Grundlage automatisch aus einem bestehenden Lebenslauf vorbefüllt werden, oder nur über das Interview entstehen?
4. Ist ein Stand-Hash sinnvoll, um veraltete Zielausgaben zu erkennen, oder reicht das Datum?
