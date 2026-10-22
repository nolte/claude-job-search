# Export: LaTeX PDF of the Lebenslauf

This page lists what you need to turn a finished Lebenslauf into a PDF with the LaTeX template,
and the commands that do it. The Markdown source is the only input. The PDF and the LaTeX
source are generated from it.

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
parser reads the same text as before (spec R-8.3).

- **Header:** the name stands first and large, the personal data below it.
- **Stations:** the period stands in a left column, the position in bold, the employer and place below it in grey.
  Education and certificates use the same column for their periods.
- **Typography:** Lato at 10.5 pt on 14.3 pt leading, ragged right, little hyphenation, product names such as
  `VMware Tanzu` do not break. The size is not reduced to fit two pages.
- **Print and screen:** the colours keep their contrast on white (text 15.8:1, accent 8.7:1, grey 6.1:1) and the
  hierarchy stays visible in grayscale.
- **Letter:** the Anschreiben uses the same template with its own margins (25 mm left).

The design is in `skills/job-application-export/templates/` (`document.tex` and `cv.lua`); the rules are in
`spec/job-application/lebenslauf/en.md` (LB-11).

## Input

The source is a Markdown file of the application folder:

```text
job-application/<slug>/lebenslauf.md
```

The export checks the page count against the document type. A Lebenslauf may have at most two pages.

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
| `--doc-type motivation` | Motivationsschreiben, at most two pages |
| `--name` | File name without extension, default is the source name |
| `--out-dir` | Output folder, default `job-application/<slug>/export/` |

## Outputs

In the output folder the export writes:

- the PDF (`<name>.pdf`) and, for `--format pdf`, the LaTeX source (`<name>.tex`); the auxiliary files
  of LuaLaTeX are removed,
- the page count and the result of the content check on the console. A content check that fails is
  reported, and the export is not presented as ready.

## Run in a container, in another repository

The export usually runs in the repository that holds your application data, not in the plugin
repository. The `Dockerfile` bundles pandoc, LuaLaTeX, the German language support and poppler-utils,
so nothing else has to be installed there. Only Docker is needed.

Build the image once. The plugin repository is the build source, you do not clone it:

```bash
docker build -t claude-job-search-export https://github.com/nolte/claude-job-search.git#develop
```

Replace `develop` with a release tag once one exists, so the image does not change under you.

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

Check the result after every export: the console must print `Inhaltsprüfung: ok`. A PDF that is only a
few kilobytes large and has no text is a failed export, even if a file exists. Only the export skill is
copied into the image (`.dockerignore`), so personal data of your repository never enters the build context.

## What is not part of the export

- The export never writes to the Markdown source.
- The export does not add personal data or metadata beyond the `grundlage_hash` of the source.
- The export does not send anything. Sending is a separate step.
