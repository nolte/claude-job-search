---
name: job-application-export
description: "Exports a finished Bewerbungsdokument (Lebenslauf, Anschreiben) from its Markdown source to PDF (via LaTeX and LuaLaTeX), DOCX, HTML, or Markdown, through the Taskfile command `task export`. Carries the Datengrundlage hash into the output metadata and checks that the export has the same content as the source. Use on \"exportiere meinen Lebenslauf als PDF\", \"mach ein Word-Dokument aus dem Anschreiben\", \"HTML-Version erzeugen\", or equivalent German requests. Don't use to write or change content (use the owning job-application-* skill), for the quality review (job-application-quality-gate), or for the e-mail text itself (job-application-email-create)."
tags: [bewerbung, export, pdf, latex, docx, html, markdown]
phase: deliver
summary: "Exports a finished application document from Markdown to PDF, DOCX, HTML or Markdown via the Taskfile command."
summary_de: "Exportiert ein fertiges Bewerbungsdokument aus Markdown nach PDF, DOCX, HTML oder Markdown über den Taskfile-Befehl."
use_when:
  - "a Lebenslauf or Anschreiben is final and needs to be sent as PDF or Word"
  - "you want an HTML preview or a self-contained HTML file of a document"
dont_use_when:
  - situation: "The content still needs to be written or changed"
    alternative: job-application-cv-create
  - situation: "You want the set reviewed before sending"
    alternative: job-application-quality-gate
  - situation: "You need the sending e-mail text"
    alternative: job-application-email-create
see_also:
  - job-application-cv-create
  - job-application-cover-letter-create
  - job-application-quality-gate
---

# Bewerbung exportieren

Spec: `spec/job-application/konventionen/en.md` R-10 (output formats) and R-6 (export only on
request). Requirement: `project/requirements/ausgabeformate.md`.

The export is a Taskfile command. This skill calls it and reports the result. It does not
rewrite content.

## Command

```bash
task export -- <datei.md> --format <pdf|docx|html|md> --doc-type <cv|letter|motivation|email> [--out-dir DIR] [--name NAME]
```

- `--doc-type`: `cv` checks a maximum of two pages, `letter` one page, `motivation` two pages (a Motivationsschreiben for a job is one page by default, MS-7), `email` no page limit.
- `--out-dir`: default `<quelle>/export/`, inside the git-ignored `job-application/` folder.
- `--name`: default is the source file name. Use `Vorname_Nachname_Lebenslauf` (spec R-4).

## Formats

| Format | Werkzeug | Notes |
|---|---|---|
| `pdf` | pandoc, LuaLaTeX, `poppler-utils` | Template `templates/document.tex` (decision O-1). Fonts embedded. Page check. |
| `tex` | pandoc | LaTeX source with the same template, written as `<name>.tex`. No LuaLaTeX needed. Content check on the source read back as plain text. The source of the PDF, for compiling elsewhere. |
| `docx` | pandoc, python-docx | Neutral reference style, Arial, A4, 2.5 cm (decision O-2). Single column, Word heading styles. Recommended for ATS portals (spec R-8.3). |
| `html` | pandoc | Self-contained (`--embed-resources`), `lang="de"`, print and dark-mode CSS (`templates/style.css`). |
| `md` | none | Copy of the source with its frontmatter. |

Hash: the frontmatter `grundlage_hash` goes into the PDF and DOCX metadata, into a
`<meta name="grundlage_hash">` tag in HTML, and stays in the frontmatter for Markdown.

Content check: every word of the source must appear in the export, and no word may be added.
A difference is reported and the exit code is 2. The file is kept so you can inspect it.

## Workflow

1. Confirm the source document and the format. If the format is missing, ask once. For
   ATS or portal applications, propose `docx` (spec R-8.3).
2. Run `task export -- …` with the arguments.
3. Read the output. Report the file path, the number of pages for PDF, and the content check.
4. Warn if the PDF exceeds the page limit for its document type.

## Missing tools

If a tool is missing, the command names it and stops only that format. Install hints:

- pandoc: the system package `pandoc`, or `pip install pypandoc_binary` for a user install.
- LuaLaTeX: the system package `texlive-luatex` (decision O-3; XeLaTeX is the fallback).
- `pdfinfo` and `pdftotext`: the system package `poppler-utils`.
- python-docx (for DOCX): `pip install python-docx`.

## Hard rules

1. **The Markdown source is never edited** by the export.
2. **Export only on request** (spec R-6). Nothing is exported automatically.
3. **Personal data stays local.** Outputs go into the git-ignored `job-application/` folder. Intermediate
   LaTeX files (`.aux`, `.log`, `.out`) are removed. The `.tex` source stays.
4. **A failed content check is reported, not hidden.** Do not call the export ready while it reports a difference.
5. **Do not invent a format.** Email text is only Markdown, and the review report is only Markdown (requirement FA-O table). `tex` is an export of the Lebenslauf and the Anschreiben, not a new document type.
