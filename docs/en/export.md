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
| Fonts for LuaLaTeX | the template sets no font, so the `fontspec` default is used | `texlive-fonts-recommended` |
| poppler-utils | `pdfinfo` and `pdftotext`, used for the page check and the text check | `poppler-utils` |
| python-docx | DOCX only, not for PDF | `pip install python-docx` |

The table lists the typical package names. They are not verified on every system. Check the
result with `pdfinfo` and the export's content check.

For the LaTeX source alone (`--format tex`), only pandoc is needed. LuaLaTeX is not required.

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
| `--name` | File name without extension, default is the source name |
| `--out-dir` | Output folder, default `job-application/<slug>/export/` |

## Outputs

In the output folder the export writes:

- the PDF (`<name>.pdf`) and, for `--format pdf`, the LaTeX source (`<name>.tex`); the auxiliary files
  of LuaLaTeX are removed,
- the page count and the result of the content check on the console. A content check that fails is
  reported, and the export is not presented as ready.

## What is not part of the export

- The export never writes to the Markdown source.
- The export does not add personal data or metadata beyond the `grundlage_hash` of the source.
- The export does not send anything. Sending is a separate step.
