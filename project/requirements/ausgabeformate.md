---
title: Ausgabeformate für Bewerbungsunterlagen (LaTeX/PDF, DOCX, Markdown, HTML)
status: implemented (PDF-Pfad mangels LuaLaTeX nicht durchlaufen getestet)
created: 2026-10-21
---

# Anforderung: Ausgabeformate für Bewerbungsunterlagen

## Ausgangslage

Die Skills erzeugen Lebenslauf, Anschreiben und E-Mail als Markdown (Spec R-6: Markdown ist
die Quelle, Export ist ein eigener Schritt). Für die Bewerbung braucht der Nutzer die Dokumente
je nach Empfänger und Kanal in unterschiedlichen Formaten. Gewünscht sind vier Ausgaben:

1. **LaTeX mit Umwandlung in PDF**, für eine gesetzte, druckfertige Fassung.
2. **Word (DOCX)**, für Empfänger, die bearbeitbare Dokumente verlangen, und für ATS-Portale.
3. **Markdown**, als Quelle und zum Weiterverwenden.
4. **HTML**, für Ansicht im Browser, zum Teilen oder als Vorschau.

Der Markdown-Text bleibt die einzige Quelle. Alle anderen Formate entstehen daraus. Eine
zweite, parallel gepflegte Fassung ist ausgeschlossen, weil sie zu Abweichungen führt.

## Grundsätze

- **Eine Quelle.** Inhalt steht nur in der Markdown-Datei. Format ist Darstellung.
- **Gleicher Inhalt.** Alle Formate enthalten denselben Text. Abweichungen sind Fehler.
- **Export auf Anforderung.** Wie in Spec R-6 wird nichts automatisch exportiert.
- **Lokal.** Exporte liegen im Bewerbungsordner und sind von Git ausgeschlossen (Spec R-6).
- **Keine Fakten im Format.** Gestaltung ändert nichts am Inhalt (Spec R-1).

## Dokumente und Formate

| Dokument | LaTeX → PDF | DOCX | Markdown | HTML |
|---|---|---|---|---|
| Lebenslauf | ja | ja | ja | ja |
| Anschreiben | ja | ja | ja | ja |
| Bewerbungs-E-Mail | nein | nein | ja (`.md`, Klartext) | nein |
| Prüfbericht | nein | nein | ja | nein |

Die E-Mail ist Klartext und wird nicht gestaltet. Sie wird als Markdown-Datei ausgegeben, die
der Nutzer in den Mail-Client kopiert. Der Prüfbericht ist ein Arbeitsdokument und kein Versanddokument.

## Anforderungen

### Gemeinsame Anforderungen

**FA-O1 Quelle bleibt Markdown.** Jeder Export liest die Markdown-Datei des Dokuments. Eine Änderung
erfolgt nur dort. Exporte werden neu erzeugt und nie von Hand angepasst.

- *Akzeptanz:* Nach einer Änderung im Markdown und erneutem Export zeigen alle Formate die Änderung.

**FA-O2 Hash-Übernahme.** Jeder Export übernimmt den `grundlage_hash` aus dem Markdown. Bei
DOCX und PDF steht der Hash in den Dokument-Eigenschaften (Metadaten), bei HTML im Meta-Tag,
bei Markdown im Frontmatter (Spec R-9.5).

- *Akzeptanz:* `bewerbung-pruefen` erkennt veraltete Exporte über den Hash in allen Formaten.

**FA-O3 Dateinamen.** Exporte folgen dem Schema aus Spec R-4: `Vorname_Nachname_<Dokument>.<ext>`,
etwa `Vorname_Nachname_Lebenslauf.pdf`. Der Nutzer kann einen Zielordner angeben.

- *Akzeptanz:* Alle Exporte eines Laufs haben denselben Präfix und die Erweiterung des Formats.

**FA-O4 Zielordner.** Exporte liegen unter `job-application/<slug>/export/`. Hilfsdateien (LaTeX-Hilfsdateien
wie `.aux`, `.log`) werden nach dem Lauf entfernt, außer der Nutzer bittet um sie.

- *Akzeptanz:* Nach einem PDF-Export liegt im Zielordner nur die PDF und die `.tex`-Quelle.

**FA-O5 Deutsche Sprache.** Alle Formate setzen Sprache Deutsch (Silbentrennung, Anführungszeichen,
Datumsformat). Im HTML trägt das Dokument `lang="de"`.

- *Akzeptanz:* Umlaute und ß werden korrekt dargestellt. Die Sprachmarkierung ist gesetzt.

**FA-O6 Inhaltsgleichheit.** Ein Vergleich zwischen Markdown und den Exporten (Wortfolge ohne
Formatierung) zeigt keine inhaltlichen Abweichungen.

- *Akzeptanz:* Die Prüfung meldet keine fehlenden oder zusätzlichen Wörter in den Exporten.

**FA-O7 Abhängigkeiten prüfen.** Vor einem Export prüft der Skill, ob die benötigten Werkzeuge
vorhanden sind (siehe Tooling). Fehlt eines, nennt er das Werkzeug und den Installationsweg und
erzeugt die übrigen Formate weiter.

- *Akzeptanz:* Fehlt LaTeX, schlägt nur der PDF-Export fehl, die anderen Formate entstehen.

### Format 1: LaTeX mit PDF-Umwandlung

**FA-O8 LaTeX-Quelle.** Der Skill erzeugt eine `.tex`-Datei aus dem Markdown. Sie wird mit einer
Vorlage gesetzt, die Deutsch (Babel `ngerman`), Schrift, Seitenränder und Kopfzeilen festlegt.

**FA-O9 Layout des Anschreibens.** Das Anschreiben folgt dem Layout nach DIN 5008 (Spec R-3):
Absender, Empfängeranschrift, Ort und Datum, Betreff fett, Anrede, Schlussformel. Die Vorlage
erzeugt keine Seitenzahlen auf einseitigen Briefen.

**FA-O10 Layout des Lebenslaufs.** Der Lebenslauf ist einspaltig, mit einer Zeile je Station
(Spec R-2.1). Keine Tabellen, keine Textfelder.

- *Akzeptanz:* Das PDF ist einspaltig und hat die Kopfzeile je Station in einer Zeile.

**FA-O11 PDF-Erzeugung.** Die `.tex`-Datei wird mit einer LuaLaTeX- oder XeLaTeX-Engine kompiliert,
die Umlaute und Schriften als Unicode verarbeitet. Die Schriften werden eingebettet.

- *Akzeptanz:* `pdffonts` zeigt nur eingebettete Schriften. Umlaute sind als Text auswählbar.

**FA-O12 Textlage.** Das PDF ist eine Textdatei und kein Scan. Der Text lässt sich markieren und
mit `pdftotext` auslesen (ATS-Anforderung aus Spec R-8.3).

- *Akzeptanz:* `pdftotext` liefert den vollständigen Text in der Lesereihenfolge.

**FA-O13 Seitenbegrenzung.** Der Lebenslauf hat in der Standardausgabe höchstens zwei Seiten, das
Anschreiben genau eine. Überschreitet das PDF die Grenze, meldet der Export das und schreibt
trotzdem die Datei, markiert als „überlang“.

- *Akzeptanz:* `pdfinfo` zeigt die Seitenzahl, die Prüfung meldet eine Überschreitung.

**FA-O14 Metadaten.** Titel, Autor und Betreff sind im PDF gesetzt. Der Hash steht im Metadatenfeld
(FA-O2).

### Format 2: Word (DOCX)

**FA-O15 Erzeugung.** Der DOCX-Export nutzt pandoc mit einer Referenzvorlage (`reference.docx`).
Die Vorlage legt Schriften, Abstände und Stile fest.

**FA-O16 ATS-Struktur.** Das DOCX ist einspaltig. Überschriften verwenden die Word-Formatvorlagen
„Überschrift 1“ und „Überschrift 2“, nicht Fettdruck als Ersatz. Keine Tabellen, Textfelder oder
Kopfzeilen mit Inhalt (Spec R-8.3).

- *Akzeptanz:* Die Stilnamen der Überschriften sind vorhanden und die Dokumentstruktur enthält keine Tabelle.

**FA-O17 Bearbeitbarkeit.** Das DOCX bleibt bearbeitbar: Absätze sind echte Absätze, Listen sind
Word-Listen, keine Zeilenumbrüche von Hand.

**FA-O18 Standardformat.** Für ATS-Portale und Stellenanzeigen mit ausdrücklicher DOCX-Forderung
ist DOCX das vorgeschlagene Format (Spec R-8.3). Die PDF bleibt die Standardausgabe für den Versand per E-Mail.

### Format 3: Markdown

**FA-O19 Markdown ist die Quelle.** Der Markdown-Export ist die Quelldatei, mit Frontmatter
(Hash, Stand, Format). Er wird nicht umgeformt.

**FA-O20 Lesbar ohne Plugin.** Der Markdown-Export nutzt nur Standardelemente: Überschriften,
Listen, Fettdruck. Keine proprietären Erweiterungen.

- *Akzeptanz:* Die Datei lässt sich in jedem Markdown-Editor lesen und ergibt dieselbe Gliederung.

### Format 4: HTML

**FA-O21 Eigenständige Datei.** Die HTML-Datei enthält Stil (CSS) und Inhalt in einer Datei. Sie
lädt keine externen Ressourcen. Keine Schriften von Drittanbietern.

- *Akzeptanz:* Die Datei funktioniert offline und ohne Netzwerkzugriff.

**FA-O22 Darstellung.** Die HTML-Datei ist lesbar auf Bildschirm und Smartphone (responsive Breite,
Mindestschriftgröße 16 px) und druckbar (`@media print` mit A4-Seitengröße und ohne Hintergrundfarben).

**FA-O23 Struktur.** Das HTML verwendet semantische Elemente (`<main>`, `<h1>`, `<h2>`, `<ul>`).
Keine Layout-Tabellen.

- *Akzeptanz:* Ein Screenreader liest die Überschriften in der richtigen Reihenfolge.

### Nicht-funktionale Anforderungen

**NFA-O1 Reproduzierbarkeit.** Gleiche Eingabe und gleiche Vorlage ergeben denselben Export.
Zeitstempel im Export werden nur aus dem `stand` übernommen, nicht aus der Systemzeit.

**NFA-O2 Datenschutz.** Exporte enthalten personenbezogene Daten. Sie liegen im gitignorierten
Ordner `job-application/` (Spec R-6). Die Vorlagen enthalten keine persönlichen Angaben.

**NFA-O3 Keine Netzwerkabhängigkeit.** Der Export funktioniert ohne Netzwerk. Vorlagen liegen im
Repository oder im Bewerbungsordner des Nutzers.

**NFA-O4 Fehlermeldungen.** Fehlt ein Werkzeug oder scheitert eine Umwandlung, nennt die Meldung
das Werkzeug, den Befehl und die Ursache. Die Meldung enthält keine Dokumentinhalte.

## Tooling

| Format | Werkzeug | Zweck |
|---|---|---|
| LaTeX → PDF | pandoc, LuaLaTeX oder XeLaTeX, `babel-german`, `poppler-utils` (`pdfinfo`, `pdffonts`, `pdftotext`) | Setzen und Prüfen des PDFs |
| DOCX | pandoc mit `reference.docx` | Word-Export |
| Markdown | keines | Quelle |
| HTML | pandoc mit eigenem CSS | Eigenständige HTML-Datei |

Die Werkzeuge werden vor dem ersten Lauf geprüft (FA-O7). Die Versionen werden in der Dokumentation
angegeben. pandoc ist das gemeinsame Werkzeug für DOCX, HTML und die LaTeX-Erzeugung.

## Skill

Die Umsetzung erfolgt in einem eigenen Skill `job-application-export`. Er nimmt ein Dokument und ein
Format entgegen und erzeugt die Datei im Zielordner. Er verändert die Markdown-Quelle nicht.

Eingaben: Dokument (`lebenslauf`, `anschreiben`, `email`), Format (`pdf`, `docx`, `md`, `html`),
Zielordner (optional, Standard `job-application/<slug>/export/`).

## Auswirkungen auf bestehende Bausteine

| Baustein | Änderung |
|---|---|
| Spec `spec/job-application/konventionen/en.md`, R-6 | Neues Kapitel „Ausgabeformate“ mit den Regeln aus FA-O1 bis FA-O23 |
| Spec R-8.3 (ATS) | Verweis auf FA-O16 und FA-O18 |
| `job-application-quality-gate` | Prüft Hash, Seitenzahl, Textlage und Inhaltsgleichheit der Exporte |
| `job-application-solution` | Fragt am Ende, ob und in welchen Formaten exportiert wird; schlägt DOCX bei ATS vor |
| `.gitignore` | Enthält bereits `/job-application/`, `*.pdf` und `*.docx`. `*.tex`, `*.html` sind durch `/job-application/` abgedeckt |
| Neuer Skill `job-application-export` | Führt den Export aus |

## Nicht-Ziele

- Gestaltung mit Foto oder Logo. Das Foto ist in der Standardausgabe nicht vorgesehen (Spec R-8.2).
- Eine eigene Layout-Software oder ein Designsystem.
- Automatischer Versand oder Upload in Bewerbungsportale.
- Eine englische Fassung. Sie ist kein Teil dieser Anforderung.
- Digitale Signatur oder Verschlüsselung der PDF-Datei.

## Entscheidungen

Am 2026-10-21 durch den Nutzer übernommen, jeweils mit der unten genannten Empfehlung.

**O-1 DIN-5008-Layout: Vorlage oder eigenes Layout?** Empfehlung: eigene LaTeX-Vorlage mit
Fensterbriefmaßen nach DIN 5008, ohne zusätzliche Pakete wie KOMA-Script. Begründung: wenige Abhängigkeiten
und nachvollziehbare Maße. Die Vorlage wird im Repository abgelegt.

**O-2 Referenzvorlage für DOCX.** Empfehlung: eine neutrale `reference.docx` im Repository mit
Schrift Arial oder Calibri, Überschriften als Word-Formatvorlagen, A4 und 2,5 cm Ränder
(entspricht den Quellen aus `lebenslauf-formate.md`). Der Nutzer kann eine eigene Vorlage angeben.

**O-3 LuaLaTeX oder XeLaTeX.** Empfehlung: LuaLaTeX, weil es Unicode und OpenType-Schriften
ohne Zusatzaufwand unterstützt. XeLaTeX ist als Ausweichlösung vorgesehen.

**O-4 Hash im Dokument.** Empfehlung: Der Hash steht in den Metadaten (PDF, DOCX) und im Frontmatter
(Markdown), nicht sichtbar im gedruckten Dokument. Sichtbar wäre er nur für die interne Prüfung.

**O-5 Format-Vorgabe pro Stellenanzeige.** Empfehlung: Die Anzeige hat Vorrang (Spec R-8.3). Ohne
Vorgabe liefert der Skill PDF und DOCX, Markdown und HTML nur auf Wunsch.

## Quellen

Die Empfehlungen stützen sich auf die Spec (R-2, R-2.1, R-3, R-4, R-6, R-8.3, R-9.5) und auf die
Quellen in `project/requirements/lebenslauf-formate.md`, besonders zur ATS-Eignung von DOCX und
Text-PDF. Die Werkzeugwahl (pandoc, LuaLaTeX, `poppler-utils`) ist nicht durch eine eigene Recherche
belegt. Sie wird vor der Umsetzung anhand der Dokumentation der Werkzeuge geprüft.
