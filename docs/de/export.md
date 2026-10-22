# Export: LaTeX-PDF des Lebenslaufs

!!! abstract "Für Fortgeschrittene (Operator-Inhalt)"
    Diese Seite richtet sich an die Person, die den Export ausführt: Sie nennt Pakete,
    Kommandozeilen und einen Container. Willst du nur eine PDF eines geprüften Dokuments, bitte
    den Export-Skill darum (`/claude-job-search:job-application-export`) und komm hierher zurück,
    wenn er ein fehlendes Werkzeug meldet.

Diese Seite beschreibt, was benötigt wird, um einen fertigen Lebenslauf mit dem LaTeX-Template
in eine PDF umzuwandeln, und welche Befehle das ausführen. Einzige Eingabe ist die
Markdown-Quelle. PDF und LaTeX-Quelle entstehen daraus.

!!! tip "Welches Format für welchen Empfänger"
    Eine Text-PDF ist der Standard, auch für Bewerbungsportale (ATS): Das Layout ist einspaltig
    ohne Tabellen, ein Parser liest den Text also in der richtigen Reihenfolge. DOCX erzeugst du
    nur, wenn ein Portal es ausdrücklich verlangt. HTML und Markdown dienen der Ansicht und
    deinen eigenen Unterlagen.

## Was benötigt wird

| Werkzeug | Wofür | Typisches Paket (Debian / Ubuntu) |
|---|---|---|
| pandoc | Markdown nach LaTeX, DOCX, HTML | `pandoc` |
| LuaLaTeX | Kompilieren der PDF aus der LaTeX-Quelle | `texlive-luatex` |
| Deutsche Sprachunterstützung für LaTeX | `babel` mit `ngerman` im Template | `texlive-lang-german` |
| Schriften für LuaLaTeX | Das Template nutzt Lato und fällt ohne Lato auf Latin Modern Sans zurück | `fonts-lato`, `texlive-fonts-recommended` |
| poppler-utils | `pdfinfo` und `pdftotext` für Seitenprüfung und Textprüfung | `poppler-utils` |
| python-docx | Nur für DOCX, nicht für PDF | `pip install python-docx` |

Die Tabelle nennt typische Paketnamen. Sie sind nicht auf jedem System geprüft. Das Ergebnis
prüfst du mit `pdfinfo` und mit der Inhaltsprüfung des Exports.

Für die LaTeX-Quelle allein (`--format tex`) reicht pandoc. LuaLaTeX ist dafür nicht nötig.

## Layout

Die PDF ist einspaltig und nutzt eine Akzentfarbe (dunkles Blau), dünne Linien unter den Abschnittsüberschriften
und farbige Aufzählungspunkte. Es gibt keine Tabellen, Symbole, Fotos oder Text in Kopf- und Fußzeile außer einer
dezenten Seitenzahl, ein Parser liest also denselben Text wie die Markdown-Quelle.

- **Kopfbereich:** Der Name steht zuerst und groß, darunter die persönlichen Angaben.
- **Stationen:** Der Zeitraum steht in einer linken Spalte, die Position fett, Arbeitgeber und Ort darunter in Grau.
  Ausbildung und Zertifikate nutzen dieselbe Spalte für ihre Zeiträume.
- **Typografie:** Lato in 10,5 pt auf 14,3 pt Zeilenabstand, Flattersatz, wenig Silbentrennung, Produktnamen wie
  `VMware Tanzu` brechen nicht um. Die Schrift wird nicht verkleinert, um zwei Seiten zu erreichen.
- **Druck und Bildschirm:** Die Farben behalten ihren Kontrast auf Weiß (Text 15,8:1, Akzent 8,7:1, Grau 6,1:1),
  und die Hierarchie bleibt in Graustufen sichtbar.
- **Brief:** Das Anschreiben nutzt dasselbe Template mit eigenen Rändern (25 mm links).

Das Design steht in `skills/job-application-export/templates/` (`document.tex` und `cv.lua`).

!!! info "Für Entwickler"
    Die Layoutregeln stehen in `spec/job-application/lebenslauf/en.md` (LB-11), die ATS-Regel in
    `spec/job-application/konventionen/en.md` (R-8.3, R-10).

## Eingabe

Die Quelle ist eine Markdown-Datei eines Bewerbungsordners oder eines Ausprägungsordners:

```text
job-application/<slug>/lebenslauf.md                       der Lebenslauf einer Bewerbung
job-application/lebenslauf-basis/lebenslauf.md             der Arbeitsstand einer Ausprägung
job-application/lebenslauf-basis/versionen/v001_2026-10-22.md   eine eingefrorene Version dieser Ausprägung
```

Der Export prüft die Seitenzahl gegen den Dokumenttyp. Ein Lebenslauf darf höchstens zwei Seiten haben.

**Eine eingefrorene Version exportieren.** Die Kopie, die du versendest, sollte aus einer
eingefrorenen Version stammen, nicht aus dem Arbeitsstand, damit sie sich später nachbauen lässt.
Gib dem Export die Datei in `versionen/`; die Ausgabe landet in `export/` desselben
Ausprägungsordners und heißt nach der Version (`v001_2026-10-22.pdf`), nicht nach dem Tag des
Exports. Für die Kopie an den Empfänger nutzt du `--name Vorname_Nachname_Lebenslauf`.

## Befehle

Führe sie im Hauptverzeichnis des Plugin-Repositorys aus, dort liegt die `Taskfile.yml`:

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
| `--doc-type letter` | Anschreiben, eine Seite |
| `--doc-type motivation` | Motivationsschreiben, höchstens zwei Seiten |
| `--name` | Dateiname ohne Endung, Standard ist der Name der Quelle |
| `--out-dir` | Ausgabeordner, Standard `export/` neben der Quelle: `job-application/<slug>/export/` bei einer Bewerbung, `job-application/<ausprägung>/export/` bei einer Ausprägung oder einer ihrer eingefrorenen Versionen |

## Ergebnisse

Im Ausgabeordner entstehen:

- die PDF (`<name>.pdf`) und bei `--format pdf` die LaTeX-Quelle (`<name>.tex`). Die Hilfsdateien
  von LuaLaTeX werden gelöscht.
- Seitenzahl und Ergebnis der Inhaltsprüfung auf der Konsole. Eine fehlgeschlagene Inhaltsprüfung wird
  gemeldet, und der Export gilt dann nicht als fertig.
- ein Manifest (`<name>.<ext>.manifest.json`): Hash von Quelle, Vorlage und Ausgabe, Werkzeugversionen und das
  verwendete Datum.

### Reproduzierbare PDFs

Eine Quelle mit dem Frontmatter-Schlüssel `version_datum` (`JJJJ-MM-TT`) ist eine festgeschriebene Version. Der
Export leitet dann Datum und PDF-ID der PDF aus der Quelle ab. Gleiche Quelle, gleiche Vorlage und gleiches
Container-Image ergeben eine byte-identische PDF. Ohne `version_datum` trägt die PDF den Tag des Exports, und der
Export gibt einen Hinweis aus.

```bash
python3 skills/job-application-export/scripts/export_document.py --reproduce lebenslauf.pdf.manifest.json
```

Der Befehl baut die Datei in einem temporären Ordner neu und vergleicht den Hash. Exit-Code `0` heißt identisch,
`3` heißt abweichend oder geänderte Quelle; abweichende Werkzeugversionen werden aufgelistet. Bewahre das
Container-Image einer versendeten PDF auf (`docker save`), weil sich die Debian-Pakete darin mit der Zeit ändern.

!!! info "Für Entwickler"
    Ausprägungen, Versionen und Ordneraufbau stehen in
    `spec/job-application/lebenslauf-versionen/en.md`.

## Im Container ausführen, in einem anderen Repository

Der Export läuft meist in dem Repository, das deine Bewerbungsdaten enthält, nicht im Plugin-Repository.
Das `Dockerfile` enthält pandoc, LuaLaTeX, die deutsche Sprachunterstützung und poppler-utils, dort muss
also nichts weiter installiert werden. Nötig ist nur Docker.

Baue das Image einmal. Das Plugin-Repository ist die Build-Quelle, du musst es nicht klonen:

```bash
docker build -t claude-job-search-export https://github.com/nolte/claude-job-search.git#develop
```

Ersetze `develop` durch das Release-Tag, zum Beispiel `v0.2.0`, damit sich das Image nicht unter dir ändert.

Starte es im Wurzelverzeichnis deines Daten-Repositories, dort liegt `job-application/`:

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" claude-job-search-export \
  job-application/<slug>/lebenslauf.md --format pdf --doc-type cv
```

- `--user "$(id -u):$(id -g)"` sorgt dafür, dass die Dateien in `export/` dir gehören. Das Image akzeptiert jede User-ID.
- Das Ergebnis liegt in `job-application/<slug>/export/` deines Repositories. Die Quelle wird nicht verändert.
- `--format tex`, `docx`, `html` und `md` funktionieren genauso. `--name Vorname_Nachname_Lebenslauf` setzt den Dateinamen.
- Starte den Befehl nach jeder Änderung am Lebenslauf neu. Eine alte PDF aktualisiert sich nicht von selbst.

Mit [Task](https://taskfile.dev) im Daten-Repository verkürzt diese `Taskfile.yml` den Aufruf:

```yaml
version: '3'

vars:
  EXPORT_IMAGE: '{{.EXPORT_IMAGE | default "claude-job-search-export"}}'
  EXPORT_SOURCE: '{{.EXPORT_SOURCE | default "https://github.com/nolte/claude-job-search.git#develop"}}'
  APPLICATION_ROOT: '{{.APPLICATION_ROOT | default "job-application"}}'

tasks:
  export:image:
    desc: Build the export image from the plugin repository
    cmds:
      - docker build -t {{.EXPORT_IMAGE}} {{.EXPORT_SOURCE}}

  export:
    desc: "Export a document: task export SLUG=<vorgang> [DOC=lebenslauf] [FORMAT=pdf] [TYPE=cv]"
    requires:
      vars: [SLUG]
    vars:
      DOC: '{{.DOC | default "lebenslauf"}}'
      FORMAT: '{{.FORMAT | default "pdf"}}'
      TYPE: '{{.TYPE | default "cv"}}'
    cmds:
      - >-
        docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" {{.EXPORT_IMAGE}}
        {{.APPLICATION_ROOT}}/{{.SLUG}}/{{.DOC}}.md --format {{.FORMAT}} --doc-type {{.TYPE}}
```

```bash
task export:image
task export SLUG=<slug>
task export SLUG=<slug> FORMAT=tex
```

Prüfe das Ergebnis nach jedem Export: Die Konsole muss `Inhaltsprüfung: ok` ausgeben. Eine PDF mit nur
wenigen Kilobyte und ohne Text ist ein fehlgeschlagener Export, auch wenn die Datei existiert. Nur der
Export-Skill wird ins Image kopiert (`.dockerignore`), personenbezogene Daten deines Repositories gelangen
also nie in den Build-Kontext.

## Was der Export nicht tut

- Er ändert die Markdown-Quelle nie.
- Er fügt keine personenbezogenen Daten oder Metadaten hinzu, außer dem `grundlage_hash` der Quelle.
- Er versendet nichts. Der Versand ist ein eigener Schritt.
