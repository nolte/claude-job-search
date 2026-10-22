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

Spec: `spec/job-application/konventionen/en.md` R-10 (output formats), R-4 (file names), R-6 (export only on
request), R-8.3 and `spec/job-application/cv-generierung/en.md` CG-11.5 (file format for portals). Paths:
`spec/job-application/lokale-struktur/en.md` LS-2.6, LS-3; frozen Versionen: `spec/job-application/lebenslauf-versionen/en.md`
LV-3, LV-6. Requirement: `project/requirements/ausgabeformate.md`.

The export is a Taskfile command. This skill calls it and reports the result. It does not
rewrite content.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`) from its
frontmatter. Relative paths resolve against the working directory that contains `job-application/konfiguration.md`
(LS-2.6). Sources are `<wurzel>/<slug>/<dokument>.md` (a Vorgang) or `<wurzel>/<ausprägung>/lebenslauf.md` and
`<wurzel>/<ausprägung>/versionen/vNNN_<datum>.md` (an Ausprägung without a posting).

## Command

```bash
task export -- <datei.md> --format <pdf|docx|html|md|tex> --doc-type <cv|letter|motivation|email> [--out-dir DIR] [--name NAME]
```

- `--doc-type`: `cv` checks a maximum of two pages, `letter` one page, `motivation` two pages (a Motivationsschreiben for a job is one page by default, MS-7), `email` no page limit. There is no other document type.
- `--out-dir`: default `export/` next to the source. For a frozen Version in `versionen/vNNN_<datum>.md` the default is
  `../export/` of that folder, so `<ausprägung>/export/vNNN_<datum>.<ext>` sits next to the Arbeitsstand (LS-3, LV-6).
- `--name`: default is the source file name without `.md` (`vNNN_<datum>` for a frozen Version). For a document that is
  sent, use `Vorname_Nachname_Lebenslauf`, `Vorname_Nachname_Anschreiben`, `Vorname_Nachname_Zeugnisse` (spec R-4). The
  script writes every name in ASCII: `ä→ae, ö→oe, ü→ue, ß→ss`, a hyphen stays, a space in the name part becomes `-`
  (`Anna-Lena_Mueller_Lebenslauf.pdf`).

## Formats

| Format | Werkzeug | Notes |
|---|---|---|
| `pdf` | pandoc, LuaLaTeX, `poppler-utils` | Template `templates/document.tex` (decision O-1). Fonts embedded. Page check. |
| `tex` | pandoc | LaTeX source with the same template, written as `<name>.tex`. No LuaLaTeX needed. Content check on the source read back as plain text. The source of the PDF, for compiling elsewhere. |
| `docx` | pandoc, python-docx | Neutral reference style, Arial, A4, 2.5 cm (decision O-2). Single column, Word heading styles. Only when the portal asks for DOCX (CG-11.5, D2); the author fields of the file (`dc:creator`, `cp:lastModifiedBy`) are cleared, so no tool or account name reaches the portal. |
| `html` | pandoc | Self-contained (`--embed-resources`), `lang="de"`, print and dark-mode CSS (`templates/style.css`). |
| `md` | none | Copy of the source with its frontmatter. |

Hash: the frontmatter `grundlage_hash` goes into the PDF and DOCX metadata, into a
`<meta name="grundlage_hash">` tag in HTML, and stays in the frontmatter for Markdown. The manifest records the
frontmatter keys `grundlage_hash`, `format`, `auspraegung`, `version`, `version_datum`; a `situation` key is not
expected.

Line breaks in the PDF: the Lebenslauf filter (`templates/cv.lua`) keeps product names on one line. Two consecutive
capitalised words with an inner capital or a digit (`Argo CD`, `GitLab CI`, `VMware Tanzu`) are bound automatically; other
names are listed in the document's frontmatter key `keep_together: [Docker Compose]`.

Content check: every word of the source must appear in the export, and no word may be added.
A difference is reported and the exit code is 2. The file is kept so you can inspect it.

## Workflow

1. Confirm the source document and the format. If the format is missing, ask once. The default for sending is a
   text PDF (`pdf`), also for ATS and portal applications; propose `docx` only when the posting or the portal asks for
   a Word file (CG-11.5, R-8.3.5, D2).
2. Run `task export -- …` with the arguments.
3. Read the output. Report the file path, the number of pages for PDF, and the content check.
4. Warn if the PDF exceeds the page limit for its document type.
5. Report the reproduction level from the manifest (`byte_reproduzierbar`, spec `lebenslauf-versionen` LV-5). Export a
   frozen Version (frontmatter `version_datum`) when the PDF is to be sent. To rebuild an earlier export, run
   `export_document.py --reproduce <name>.manifest.json`.

## Missing tools

If a tool is missing, the command names it and stops only that format. Install hints:

- pandoc: the system package `pandoc`, or `pip install pypandoc_binary` for a user install.
- LuaLaTeX: the system package `texlive-luatex` (decision O-3; XeLaTeX is the fallback).
- `pdfinfo` and `pdftotext`: the system package `poppler-utils`.
- python-docx (for DOCX): `pip install python-docx`.

## Hard rules

1. **The Markdown source is never edited** by the export.
2. **Export only on request** (spec R-6). Nothing is exported automatically.
3. **Personal data stays local.** Outputs go into the `export/` folder of the Vorgang or the Ausprägung inside the
   Wurzel (LS-5.7). Intermediate LaTeX files (`.aux`, `.log`, `.out`) are removed. The `.tex` source stays.
4. **A failed content check is reported, not hidden.** Do not call the export ready while it reports a difference.
5. **Do not invent a format.** Email text is only Markdown, and the review report is only Markdown (requirement FA-O table). `tex` is an export of the Lebenslauf and the Anschreiben, not a new document type.
