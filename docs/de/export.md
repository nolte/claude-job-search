# Export: LaTeX-PDF des Lebenslaufs

Diese Seite beschreibt, was benötigt wird, um einen fertigen Lebenslauf mit dem LaTeX-Template
in eine PDF umzuwandeln, und welche Befehle das ausführen. Einzige Eingabe ist die
Markdown-Quelle. PDF und LaTeX-Quelle entstehen daraus.

## Was benötigt wird

| Werkzeug | Wofür | Typisches Paket (Debian / Ubuntu) |
|---|---|---|
| pandoc | Markdown nach LaTeX, DOCX, HTML | `pandoc` |
| LuaLaTeX | Kompilieren der PDF aus der LaTeX-Quelle | `texlive-luatex` |
| Deutsche Sprachunterstützung für LaTeX | `babel` mit `ngerman` im Template | `texlive-lang-german` |
| Schriften für LuaLaTeX | Das Template setzt keine Schrift, es gilt der Standard von `fontspec` | `texlive-fonts-recommended` |
| poppler-utils | `pdfinfo` und `pdftotext` für Seitenprüfung und Textprüfung | `poppler-utils` |
| python-docx | Nur für DOCX, nicht für PDF | `pip install python-docx` |

Die Tabelle nennt typische Paketnamen. Sie sind nicht auf jedem System geprüft. Das Ergebnis
prüfst du mit `pdfinfo` und mit der Inhaltsprüfung des Exports.

Für die LaTeX-Quelle allein (`--format tex`) reicht pandoc. LuaLaTeX ist dafür nicht nötig.

## Eingabe

Die Quelle ist eine Markdown-Datei des Bewerbungsordners:

```text
job-application/<slug>/lebenslauf.md
```

Der Export prüft die Seitenzahl gegen den Dokumenttyp. Ein Lebenslauf darf höchstens zwei Seiten haben.

## Befehle

Führe sie im Wurzelverzeichnis des Plugin-Repos aus, dort liegt die `Taskfile.yml`:

```bash
task export -- job-application/<slug>/lebenslauf.md --format pdf --doc-type cv
task export -- job-application/<slug>/lebenslauf.md --format pdf --doc-type cv --name Vorname_Nachname_Lebenslauf
task export -- job-application/<slug>/lebenslauf.md --format tex --doc-type cv
```

| Option | Bedeutung |
|---|---|
| `--format pdf` | PDF, kompiliert mit LuaLaTeX |
| `--format tex` | Nur die LaTeX-Quelle, ohne Kompilieren |
| `--format docx` | Word-Dokument, braucht `python-docx` |
| `--format html` oder `md` | HTML- oder Markdown-Kopie |
| `--doc-type cv` | Lebenslauf, höchstens zwei Seiten |
| `--name` | Dateiname ohne Endung, Standard ist der Name der Quelle |
| `--out-dir` | Ausgabeordner, Standard `job-application/<slug>/export/` |

## Ergebnisse

Im Ausgabeordner entstehen:

- die PDF (`<name>.pdf`) und bei `--format pdf` die LaTeX-Quelle (`<name>.tex`). Die Hilfsdateien
  von LuaLaTeX werden gelöscht.
- Seitenzahl und Ergebnis der Inhaltsprüfung auf der Konsole. Eine fehlgeschlagene Inhaltsprüfung wird
  gemeldet, und der Export gilt dann nicht als fertig.

## Im Container ausführen

Das `Dockerfile` enthält pandoc, LuaLaTeX, die deutsche Sprachunterstützung und poppler-utils, sodass
nichts weiter installiert werden muss. Das Image läuft mit dem numerischen User `10001`.

```bash
docker build -t claude-job-search-export .
docker run --rm --user 10001:10001 -v "$PWD:/work" claude-job-search-export \
  job-application/<slug>/lebenslauf.md --format pdf --doc-type cv
```

Der eingebundene Ordner muss für den User `10001` beschreibbar sein. Nur der Export-Skill wird ins Image
kopiert (`.dockerignore`), personenbezogene Daten unter `job-application/` gelangen also nie in den Build-Kontext.

## Was der Export nicht tut

- Er ändert die Markdown-Quelle nie.
- Er fügt keine personenbezogenen Daten oder Metadaten hinzu, außer dem `grundlage_hash` der Quelle.
- Er versendet nichts. Der Versand ist ein eigener Schritt.
