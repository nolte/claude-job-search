---
name: job-application-export
description: "Exports a finished Bewerbungsdokument (Lebenslauf, Anschreiben, Motivationsschreiben) from its Markdown source to PDF (via LaTeX and LuaLaTeX), DOCX, HTML, LaTeX source, or Markdown, through the Taskfile command `task export`; the Bewerbungs-E-Mail exists only as Markdown. Reports page-limit overruns with their own exit code, and rebuilds an export from its manifest (`--reproduce`). Carries the Datengrundlage hash into the output metadata and checks that the export has the same content as the source. Use on \"exportiere meinen Lebenslauf als PDF\", \"mach ein Word-Dokument aus dem Anschreiben\", \"HTML-Version erzeugen\", or equivalent German requests. Don't use to write or change content (use the owning job-application-* skill), for the quality review (job-application-quality-gate), or for the e-mail text itself (job-application-email-create)."
tags: [bewerbung, export, pdf, latex, docx, html, markdown]
phase: deliver
summary: "Exports a finished application document from Markdown to PDF, DOCX, HTML or Markdown via the Taskfile command."
summary_de: "Exportiert ein fertiges Bewerbungsdokument aus Markdown nach PDF, DOCX, HTML oder Markdown über den Taskfile-Befehl."
use_when:
  - "a Lebenslauf, Anschreiben or Motivationsschreiben is final and needs to be sent as PDF or Word"
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
  - job-application-motivation-letter-create
  - job-application-quality-gate
---

# Bewerbung exportieren

Spec: `spec/job-application/konventionen/en.md` R-10 (output formats), R-4 (file names), R-6 (export only on
request), R-7 (quality gates), R-8.3 and `spec/job-application/cv-generierung/en.md` CG-11.5, CG-12 (file format for portals,
output consistency). Page limits: `lebenslauf/en.md` LB-2.3, LB-13; `anschreiben/en.md` AS-7.1, AS-12;
`motivationsschreiben/en.md` MS-7, MS-12. Paths: `spec/job-application/lokale-struktur/en.md` LS-2…LS-6; frozen Versionen:
`spec/job-application/lebenslauf-versionen/en.md` LV-2…LV-8. Requirement: `project/requirements/ausgabeformate.md`.

The export is a Taskfile command. This skill calls it and reports the result. It does not
rewrite content.

## Paths

Read `job-application/konfiguration.md` first (the Anker, LS-2.3). Take `wurzel` (default `job-application/`) from its
frontmatter. If the file is missing, ask once for the path of the Wurzel and write it there; keys are only `wurzel`,
`grundlage`, `grundlage_index` (LS-2.5). Relative paths resolve against the working directory that contains
`job-application/konfiguration.md` (LS-2.6). Sources are `<wurzel>/<slug>/<dokument>.md` (a Vorgang) or
`<wurzel>/<ausprägung>/lebenslauf.md` and `<wurzel>/<ausprägung>/versionen/vNNN_<datum>.md` (an Ausprägung without a
posting).

**Repository boundary (LS-2.4, R-9.9).** Before exporting, resolve the absolute path of the Wurzel and walk up from it,
including the directory itself. If a directory contains `.claude-plugin/plugin.json` with `"name": "claude-job-search"`,
refuse and report: *Die Wurzel liegt im Plugin-Repository. Lege sie außerhalb ab und trage den Pfad in
`job-application/konfiguration.md` unter `wurzel` ein.* Write nothing in that case.

## Command

```bash
task export -- <datei.md> --format <pdf|docx|html|md|tex> --doc-type <cv|letter|motivation|email> [--out-dir DIR] [--name NAME]
```

- `--doc-type`: `cv` checks a maximum of two pages (one page for the format `einseitig`, LB-2.3), `letter` one page
  (AS-7.1), `motivation` one page for the job variants `stelle` (default), `quereinstieg` and `berufseinstieg`, two pages for `studium` and `stipendium` (MS-7, read from the frontmatter key `variante`), `email`
  no page limit. `email` is accepted only with `--format md` (R-10.2); any other format is an error (exit 1). There is no
  other document type.
- `--out-dir`: must lie inside the Wurzel (LS-5.7); the script refuses a folder inside the plugin repository. Default
  `export/` next to the source. For a frozen Version in `versionen/vNNN_<datum>.md` the default is
  `../export/` of that folder, so `<ausprägung>/export/vNNN_<datum>.<ext>` sits next to the Arbeitsstand (LS-3, LV-6).
- `--name`: default is the source file name without `.md` (`vNNN_<datum>` for a frozen Version). For a document that is
  sent, use `Vorname_Nachname_Lebenslauf`, `Vorname_Nachname_Anschreiben`, `Vorname_Nachname_Zeugnisse` (spec R-4). The
  script writes every name in ASCII: `ä→ae, ö→oe, ü→ue, ß→ss`, a hyphen stays, a space in the name part becomes `-`
  (`Anna-Lena_Mueller_Lebenslauf.pdf`).

A frozen Version (LV-2.3) is exported under its Version name, `<ausprägung>/export/vNNN_<datum>.<ext>` with
`vNNN_<datum>.<ext>.manifest.json`. The copy that goes to the recipient is exported once more with
`--name Vorname_Nachname_Lebenslauf`, or copied under that name, so the Version file and the sent file stay
identical in content. An export of the Arbeitsstand (no `version_datum`) keeps the sent name and is not stored in git (LV-4).

## Formats

| Format | Werkzeug | Notes |
|---|---|---|
| `pdf` | pandoc, LuaLaTeX, `poppler-utils` | Template `templates/document.tex` (decision O-1). Fonts embedded. Page check. |
| `tex` | pandoc | LaTeX source with the same template, written as `<name>.tex`. No LuaLaTeX needed. Content check on the source read back as plain text. The source of the PDF, for compiling elsewhere. |
| `docx` | pandoc, python-docx | Neutral reference style, Arial, A4, 2.5 cm (decision O-2). Single column, Word heading styles. Only when the portal asks for DOCX (CG-11.5, R-8.3.4); the author fields of the file (`dc:creator`, `cp:lastModifiedBy`) are cleared, so no tool or account name reaches the portal. |
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
A difference is reported and the exit code is 2. The file is kept so you can inspect it. CG-12.2 says a difference
"blocks the export": in practice the file stays, the manifest is written, and the document is not ready to send.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Export ok; with `--reproduce`: byte-identical |
| 1 | Error: missing tool, invalid arguments (for example `email` with another format, `--out-dir` in the plugin repository), unreadable input |
| 2 | Content check found a difference (CG-12.2). File and manifest stay |
| 3 | `--reproduce` only: output differs, or the source hash no longer matches the manifest (LV-6.4, LV-3.4) |
| 4 | The PDF exceeds the page limit of its document type. File and manifest stay. If the content check also failed, the code is 2 and the page count is still reported |

Severity of code 4 is set by the quality gate: Blocker for `cv` (LB-13) and `letter` (AS-12), Warnung for `motivation`
(MS-12). The Warnung of the old text (stderr only) is gone.

## Workflow

1. Resolve the Wurzel and check the repository boundary (see Paths). Confirm the source document and the format. If the
   format is missing, ask once. The default for sending is a text PDF (`pdf`), also for ATS and portal applications;
   propose `docx` only when the posting or the portal asks for a Word file (CG-11.5, R-8.3.4). The e-mail text is
   exported only as `md`.
2. Run `task export -- …` with the arguments. Set `--out-dir` only to a folder inside the Wurzel.
3. Read the output and the exit code. Report the file path, the number of pages for PDF, and the content check.
4. On exit 4, report the page overrun with the limit and say that the severity is decided by the quality gate
   (Blocker for Lebenslauf and Anschreiben). Do not shorten the document here: the owning skill does that. On exit 2,
   report the difference and do not call the export ready.
5. If the output has the line `Platzhalter: n offen`, tell the user that the document still holds open `[ERGÄNZEN …]` or
   `[KLÄREN …]` placeholders: they stand visibly in the export, the export is not ready to send, and the quality gate
   reports them as a Blocker (CV-01, BR-01). The export does not block and the exit code stays 0 (R-6: export only on
   request, no hidden refusal).
6. If the report says `grundlage_hash: fehlt`, tell the user that the output cannot be checked against the Grundlage
   (R-10.3) and that the quality gate cannot compare it.
7. Report the reproduction level from the manifest (`byte_reproduzierbar`, spec `lebenslauf-versionen` LV-5). Export a
   frozen Version (frontmatter `version_datum`) when the PDF is to be sent, then make the sent copy
   `Vorname_Nachname_Lebenslauf.<ext>` (LV-2.3). Only the PDF that was actually sent goes into a private Git
   repository, with its manifest; Arbeitsstand and test exports stay out (LV-4).

## Reproduce

```bash
task export -- --reproduce <datei>.manifest.json
```

(also `python3 <plugin-root>/skills/job-application-export/scripts/export_document.py --reproduce …`). The script
rebuilds the output in a temporary folder and compares the hash (LV-6.4). Exit 0 identical, 3 different, 1 error. If the
hash of the source differs from the manifest, it stops with exit 3 and does not repair the file: a frozen Version is
never edited (LV-3.4). It lists differing tool versions and a changed template.

## Toolchain record (LV-6.3, LV-7)

The script reads two optional environment variables and writes them into the manifest key `umgebung`:
`PLUGIN_REVISION` (commit or version of the plugin) and `EXPORT_IMAGE_ID` (id of the container image that ran the
export). Byte-identity over years needs the same toolchain, so keep the image that produced a sent PDF (`docker save`
or a tagged image in a registry the user controls) and record its id in `EXPORT_IMAGE_ID` (LV-7.1). Without the image
only content-identity is promised (LV-7.2). The skill never pushes an image anywhere (LV-7.3).

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
   Wurzel (LS-5.7). `--out-dir` points only into the Wurzel; the script refuses the plugin repository, and the skill
   refuses a Wurzel inside it. Intermediate LaTeX files (`.aux`, `.log`, `.out`) are removed. The `.tex` source stays.
4. **A failed content check is reported, not hidden.** Do not call the export ready while it reports a difference.
5. **Do not invent a format.** Email text is only Markdown, and the review report is only Markdown (requirement FA-O table). `tex` is an export of the Lebenslauf, the Anschreiben and the Motivationsschreiben, not a new document type.
6. **Export does not change status.** S6 leaves `status` in `vorgang.md` as it is (LS-6).
