# Export: LaTeX PDF of the Lebenslauf

!!! abstract "For advanced users (operator content)"
    This page is for the person who runs the export: it names packages, command lines and a
    container. If you only want a PDF of a checked document, ask the export skill
    (`/claude-job-search:job-application-export`) and come back here when it reports a missing
    tool.

This page lists what you need to turn a finished Lebenslauf into a PDF with the LaTeX template,
and the commands that do it. The Markdown source is the only input. The PDF and the LaTeX
source are generated from it.

!!! tip "Which format for which recipient"
    A text PDF is the default, also for application portals (ATS): the layout is one column
    without tables, which parsers in general read in order. That is a layout rule and a check of the extracted text
    (see "What the export checks"), not a statement about any particular ATS. Produce DOCX only when a portal
    explicitly demands it. HTML and Markdown are for viewing and for your own records.

## What is needed

| Tool | Needed for | Typical package (Debian / Ubuntu) |
|---|---|---|
| pandoc | Markdown to LaTeX, DOCX, HTML | `pandoc` |
| LuaLaTeX | compiling the PDF from the LaTeX source | `texlive-luatex` |
| German language support for LaTeX | `babel` with `ngerman` in the template | `texlive-lang-german` |
| Fonts for LuaLaTeX | the template uses Lato and falls back to Latin Modern Sans when Lato is missing | `fonts-lato`, `texlive-fonts-recommended` |
| poppler-utils | `pdfinfo` and `pdftotext`, used for the page check and the text check | `poppler-utils` |
| python-docx | DOCX only, not for PDF | `pip install python-docx` |

The table lists the typical package names. They are not verified on every system. Check the
result with `pdfinfo` and the export's content check.

For the LaTeX source alone (`--format tex`), only pandoc is needed. LuaLaTeX is not required.

## Layout

The PDF is one column with one accent colour (dark blue), thin rules under the section headings and coloured
bullets. There are no tables, icons, photos or text in the header and footer apart from a quiet page number, so a
parser reads the same text as the Markdown source.

- **Header:** the name stands first and large, the personal data below it.
- **Stations:** the period stands in a left column, the position in bold, the employer and place below it in grey.
  Education and certificates use the same column for their periods.
- **Typography:** Lato at 10.5 pt on 14.3 pt leading, ragged right, little hyphenation, product names such as
  `VMware Tanzu` do not break. The size is not reduced to fit two pages.
- **Print and screen:** the colours keep their contrast on white (text 15.8:1, accent 8.7:1, grey 6.1:1) and the
  hierarchy stays visible in grayscale.
- **Letter:** the Anschreiben uses the same template with its own margins (25 mm left).

The design is in `skills/job-application-export/templates/` (`document.tex` and `cv.lua`).

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Export done |
| `1` | Error, for example `email` with a format other than `md` |
| `2` | The content of the export differs from the source; the file is kept, but it is not ready to send |
| `3` | `--reproduce`: different output or a changed source |
| `4` | Page limit of the document type exceeded; file and manifest are kept. A Lebenslauf with `format: einseitig` has a limit of one page. The quality gate sets the severity |

The environment variables `PLUGIN_REVISION` and `EXPORT_IMAGE_ID` are written to the manifest under `umgebung`.

!!! info "For developers"
    The layout rules are `spec/job-application/lebenslauf/en.md` (LB-11), the ATS rule is
    `spec/job-application/konventionen/en.md` (R-8.3, R-10).

## Input

The source is a Markdown file of an application folder or of a CV variant folder:

```text
job-application/<slug>/lebenslauf.md                       the Lebenslauf of one application
job-application/lebenslauf-basis/lebenslauf.md             the working copy of a variant
job-application/lebenslauf-basis/versionen/v001_2026-10-22.md   a frozen version of that variant
```

The export checks the page count against the document type. A Lebenslauf may have at most two pages.

**Exporting a frozen version.** The copy you send should come from a frozen version, not from the
working copy, so it can be rebuilt later. Point the export at the file in `versionen/`; the output
goes to `export/` of the same variant folder and is named after the version
(`v001_2026-10-22.pdf`), not after the day of the export. Use `--name Vorname_Nachname_Lebenslauf`
for the copy that goes to the recipient.

## Commands

Run them from the root of the plugin repository, where `Taskfile.yml` is:

```bash
task export -- job-application/<slug>/lebenslauf.md --format pdf --doc-type cv
task export -- job-application/<slug>/lebenslauf.md --format pdf --doc-type cv --name Vorname_Nachname_Lebenslauf
task export -- job-application/<slug>/lebenslauf.md --format tex --doc-type cv
```

| Option | Meaning |
|---|---|
| `--format pdf` | PDF, compiled with LuaLaTeX |
| `--format tex` | LaTeX source only, no compilation |
| `--format docx` | Word document, needs `python-docx` |
| `--format html` or `md` | HTML or Markdown copy |
| `--doc-type cv` | Lebenslauf, at most two pages |
| `--doc-type letter` | Anschreiben, one page |
| `--doc-type motivation` | Motivationsschreiben, one page for the job variants, two pages for `studium` and `stipendium` (frontmatter key `variante`) |
| `--doc-type email` | E-mail text, only with `--format md` |
| `--name` | File name without extension, default is the source name |
| `--out-dir` | Output folder, default `export/` next to the source: `job-application/<slug>/export/` for an application, `job-application/<variant>/export/` for a variant or one of its frozen versions |

## Outputs

In the output folder the export writes:

- the PDF (`<name>.pdf`) and, for `--format pdf`, the LaTeX source (`<name>.tex`); the auxiliary files
  of LuaLaTeX are removed,
- the page count and the result of the content check on the console. A content check that fails is
  reported, and the export is not presented as ready,
- a manifest (`<name>.<ext>.manifest.json`): hash of the source, of the template and of the output, tool
  versions, the date used, and under `pruefung` the result of the checks of this run (below).

## What the export checks

!!! warning "A successful export is not a correct CV and not an ATS guarantee"
    The checks compare the exported file with its Markdown source. They do not compare it with your Datengrundlage
    (that is `cv_checks.py` in the quality gate), and no check involves an applicant tracking system. A manifest
    exists for a failed check as well; it records what was checked, it does not certify the CV.

| Question | Check | Result |
|---|---|---|
| Was the file produced? | tool exit code, file written, page count (`pdfinfo`) | error (exit 1) |
| Are all words there, and only those? | word multiset of the source against the text read back from the export (link targets are not text) | exit 2, `Fehlend` / `Zusätzlich` |
| Are figures and facts intact? | the symbols of figures (`% € $ + &`) count the same; every list item stands as the same words in the same order, after the item before it (`von 800 ms auf 120 ms` is not `von 120 ms auf 800 ms`) | exit 2, `Inhaltsabweichung` |
| Are the sections in order? | the headings of level 1 and 2 follow the source (heuristic) | warning `Reihenfolge`, exit code unchanged |
| Is the structure as intended? | DOCX and HTML: headings per level against the source, tables, text boxes, images, text in headers and footers | warning `Struktur`, exit code unchanged |
| Is it too long? | page limit of the document type (PDF) | exit 4 |
| Is it ready to send? | open `[ERGÄNZEN …]` / `[KLÄREN …]` over the whole file | warning, listed |
| Is it the same on a second run? | `--reproduce MANIFEST` rebuilds and compares the bytes | exit 3 on a difference |

The read-back is the plain text of the file: `pdftotext` for the PDF, the paragraphs and table cells for the DOCX, the
HTML without tags, the LaTeX body for `tex`. Markdown is a copy of the source and is recorded as `nicht_geprueft`. Line
and page breaks, hyphenation at the line end, bullet signs, the page number and the position of header fields do not
count as differences.

What is tested in this repository (`tests/test_export.py`, synthetic data only) and what is not:

| Statement | Basis |
|---|---|
| Text of the PDF can be extracted, the station line reads period, position, employer in order, no figure or symbol is lost over several pages | tested with `pdftotext` |
| DOCX has Word heading styles in the source order, bullets, no table for a normal CV; a table or a text box is reported | tested with python-docx |
| HTML has `lang="de"`, headings and lists from the source | tested |
| Any particular ATS reads the file correctly | **not tested and not claimed.** Parsers differ in rules and formats, and no real application data goes to an external parser |
| The text is true against your Datengrundlage | not checked by the export (`cv_checks.py`, reviewer) |
| Layout looks right (overflow, ugly page break, empty areas) | not checked automatically; open the PDF |

Where the checks run: the DOCX, HTML, Markdown and `tex` tests run in the CI on every pull request (pandoc and
python-docx are installed there). The PDF tests need LuaLaTeX and are skipped in the CI. They run locally, or in the export
image (its pandoc is older; the exporter handles that):

```bash
docker build -t claude-job-search-export .
docker run --rm --entrypoint sh -v "$PWD:/src:ro" claude-job-search-export \
  -c 'cp -r /src /tmp/w && cd /tmp/w && python3 -m unittest tests.test_export'
```

### Reproducible PDFs

A source with the frontmatter key `version_datum` (`YYYY-MM-DD`) is a frozen version. The export then derives
the PDF dates and the PDF ID from the source, so the same source, template and container image give a
byte-identical PDF. Without `version_datum` the PDF carries the day of the export and the exporter prints a
notice. A DOCX of a frozen version is byte-identical too: its document dates and zip entry dates come from
`version_datum`. A DOCX without it carries the time of the export, so `--reproduce` can report a difference when the two
exports fall in different seconds.

```bash
python3 skills/job-application-export/scripts/export_document.py --reproduce lebenslauf.pdf.manifest.json
```

The command rebuilds the file in a temporary folder and compares the hash. Exit code `0` means identical,
`3` means different or a changed source, and it lists differing tool versions. Keep the container image of a
sent PDF (`docker save`), because the Debian packages inside it change over time.

!!! info "For developers"
    Variants, versions and the folder layout are specified in
    `spec/job-application/lebenslauf-versionen/en.md`.

## Run in a container, in another repository

The export usually runs in the repository that holds your application data, not in the plugin
repository. The `Dockerfile` bundles pandoc, LuaLaTeX, the German language support and poppler-utils,
so nothing else has to be installed there. Only Docker is needed.

Build the image once. The plugin repository is the build source, you do not clone it:

```bash
docker build -t claude-job-search-export https://github.com/nolte/claude-job-search.git#develop
```

Replace `develop` with the release tag, for example `v0.2.0`, so the image does not change under you.

Run it from the root of your data repository, where `job-application/` lies:

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/work" claude-job-search-export \
  job-application/<slug>/lebenslauf.md --format pdf --doc-type cv
```

- `--user "$(id -u):$(id -g)"` makes the files in `export/` belong to you. The image accepts any user ID.
- The export is written to `job-application/<slug>/export/` in your repository. The source is not changed.
- `--format tex`, `docx`, `html` and `md` work the same way. `--name Vorname_Nachname_Lebenslauf` sets the file name.
- Run the command again after you changed the Lebenslauf. An old PDF is not updated by itself.

With [Task](https://taskfile.dev) in the data repository, this `Taskfile.yml` shortens the call:

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

Check the result after every export: the console must print `Inhaltsprüfung: ok` and no line `Reihenfolge: Abweichung` or `Struktur: …` (a section stands in another order than in the source, or a table or text box is in the file; warnings, the exit code stays 0). A PDF that is only a
few kilobytes large and has no text is a failed export, even if a file exists. Only the export skill is
copied into the image (`.dockerignore`), so personal data of your repository never enters the build context.

## What is not part of the export

- The export never writes to the Markdown source.
- The export does not add personal data or metadata beyond the `grundlage_hash` of the source.
- The export does not send anything. Sending is a separate step.
