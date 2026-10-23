# Lebenslauf variants, versions and reproducible PDFs (EN canonical)

Normative rules for keeping the generated Lebenslauf as Markdown in several variants (Ausprägungen) and
versions, so that a PDF sent in one application can be rebuilt years later for another. This document is
canonical for the topic. It applies to every document type the export handles, and names the Lebenslauf as
the main case.

Related specs:
- `spec/job-application/lebenslauf/en.md`: the document type, its frontmatter (LB-11).
- `spec/job-application/konventionen/en.md`: R-6 (data protection), R-9.5 (Grundlage hash), R-10 (output formats, exit codes).
- `spec/job-application/lokale-struktur/en.md`: the Wurzel, the Vorgang folders, LS-9 (privacy).

## LV-1 Terms

| Term | Meaning |
|---|---|
| Ausprägung | A variant of the Lebenslauf with its own focus, for example `lebenslauf-basis` or `lebenslauf-teamleitung`, or one made for a single Vorgang. It is a folder under the Wurzel. |
| Arbeitsstand | `lebenslauf.md` in the Ausprägung folder. It is edited. |
| Version | An immutable copy of the Arbeitsstand, `versionen/v<NNN>_<YYYY-MM-DD>.md`. |
| Manifest | `<datei>.manifest.json` next to an export. It records how the file was made. |
| Reproduction | Rebuilding an export from a Version and its Manifest. |

## LV-2 Layout

```text
<wurzel>/<ausprägung>/                 for example lebenslauf-basis/ (LS-3)
  lebenslauf.md                      Arbeitsstand (edited)
  pruefbericht.md                    Auswahl Lebenslauf and Prüfung (LS-7.4)
  versionen/v001_2026-10-22.md       frozen Versionen (never edited)
  export/
    v001_2026-10-22.pdf              export of one Version (LV-2.3)
    v001_2026-10-22.pdf.manifest.json
```

1. The Ausprägung name is the folder name. It is lowercase, with hyphens (`lebenslauf-basis`,
   `<firma>-<stelle>` for one Vorgang). An Ausprägung folder sits directly in the Wurzel next to the Vorgänge
   and carries no `vorgang.md`; this is how a skill tells it from a Vorgang (`lokale-struktur/en.md` LS-3).
2. A Vorgang that needs a changed Lebenslauf gets its own Ausprägung, derived from an existing Version. It
   never edits another Ausprägung. The Vorgang folder then holds `lebenslauf.md`, `versionen/` and `export/`
   like any Ausprägung, plus its Vorgang files.
3. An export of a frozen Version `versionen/vNNN_<datum>.md` is written to
   `<ausprägung>/export/vNNN_<datum>.<ext>` with its Manifest `vNNN_<datum>.<ext>.manifest.json`. Exports are
   named after the Version they were made from, not after the date of the export. The copy that is sent to a
   recipient is additionally named `Vorname_Nachname_Lebenslauf.<ext>` with the ASCII transliteration of R-4
   (LB-11.13, R-10.4). An export of the Arbeitsstand (not frozen) keeps the name
   `Vorname_Nachname_Lebenslauf.<ext>` and is not stored in git (LV-4).

## LV-3 Frontmatter and freezing a Version

1. The Arbeitsstand carries these keys in addition to LB-11: `auspraegung` (the folder name), `version`
   (integer, starting at 1) and `version_datum` (`YYYY-MM-DD`, the day the Version is frozen).
2. **Freezing** copies the Arbeitsstand to `versionen/v<NNN>_<datum>.md`, with `version` and `version_datum`
   set. After that the file is read-only by convention: a frozen Version is never edited. A correction is a new
   Version with the next number.
3. The Arbeitsstand moves to the next `version` number when the first change after a freeze is made.
4. A skill that sees a Version whose hash differs from the one in a Manifest reports it and stops (LV-6.4).
   It does not repair the file.
5. A Version holds the facts as they were. It is not updated when the Grundlage changes. `grundlage_hash`
   records which Grundlage state it came from (R-9.5).
6. Which facts a new Version may take over is decided by the rules of the Lebenslauf (R-1). Freezing adds no
   content.

## LV-4 What is stored in git

The Wurzel may sit in a private repository that is not published. This is the case of the maintainer's
Obsidian vault (decision of the user, 2026-10-22). The plugin repository itself never holds personal data.

| Stored | Not stored |
|---|---|
| Arbeitsstand, frozen Versionen | LaTeX auxiliary files (`.aux`, `.log`, `.out`) |
| The Manifest of every export | Exports that were never sent (they can be rebuilt) |
| The PDF that was actually sent, with its Manifest | Scans in `rohdaten/` unless the user decides otherwise |

1. **Only sent PDFs.** The repository stores a PDF only when it was actually sent to a recipient. Exports
   of the Arbeitsstand and test exports are git-ignored.
2. **Ignore rule.** `.gitignore` of the Wurzel ignores `**/export/*.pdf` and `**/export/*.docx` and
   re-includes the sent Versionen by negation, `!**/export/v[0-9][0-9][0-9]_*.pdf`, or the user moves
   the sent file into `export/versendet/` and ignores only `**/export/*.pdf`. Manifeste (`*.manifest.json`)
   are never ignored.
3. **After deletion of a Vorgang** (LS-6 S10) the sent PDF and its Manifest stay in the repository; the
   user keeps them in the Ausprägung the Lebenslauf came from or in the `export/` folder alone.

A repository that is, or may become, public stores none of these files (R-6).

## LV-5 Reproduction levels

| Level | Promise | Needs |
|---|---|---|
| Content-identical | Same words in the same order, same layout rules | The Version and the plugin template |
| Byte-identical | The same file, bit for bit | The Version, the same template, the same toolchain (container image), the date from `version_datum` |

1. The Manifest states which level applies (`byte_reproduzierbar`).
2. Byte-identity is promised only for a Version with `version_datum`. Without it the PDF carries the day of
   the export and the exporter prints a notice.
3. Byte-identity holds for the same toolchain. A different pandoc, LuaLaTeX or font package may change line
   breaks. `--reproduce` then reports the tool differences next to the result.

## LV-6 The Manifest and the export rules

The document types, formats, page limits and exit codes of the export are defined in R-10
(`konventionen/en.md`). This section adds what the reproduction needs.

1. The exporter derives the PDF dates from `version_datum` (midnight UTC, `SOURCE_DATE_EPOCH` with
   `FORCE_SOURCE_DATE=1`).
2. The exporter sets the PDF trailer ID from a hash of the Version, `document.tex`, `cv.lua`, the epoch and
   the document type. The random ID of LuaLaTeX would otherwise differ on every run.
3. Every export writes `<datei>.manifest.json` with: schema number, document type, format, the relative path
   and SHA-256 of the source, the frontmatter keys `format`, `auspraegung`, `version`, `version_datum` and
   `grundlage_hash` (not `situation`, which is a working note of the Arbeitsstand and does not describe
   the file), the epoch, the SHA-256 of `document.tex` and `cv.lua`, the
   tool versions (pandoc, LuaLaTeX, Python), the plugin revision and image id when the environment supplies
   them (`PLUGIN_REVISION`, `EXPORT_IMAGE_ID`), and the file name, SHA-256 and page count of the output.
4. `export_document.py --reproduce <manifest>` rebuilds the output in a temporary folder and compares the
   hash. The exit codes are those of R-10.10: `0` when identical, `3` when different or when the source hash
   no longer matches, `1` on an error. It lists differing tool versions and a changed template.
5. The Manifest holds no personal data beyond file names and hashes.

## LV-7 Toolchain retention

Byte-identity over years needs the same toolchain. The container image of the Dockerfile fixes the base image
by digest, but the Debian packages (pandoc, TeX Live, fonts) are resolved at build time and float.

1. Keep the image that produced a sent PDF: `docker save` to an archive, or push a tagged image to a registry
   the user controls. Record its id in the Manifest through `EXPORT_IMAGE_ID`.
2. Without the image, only content-identity is promised (LV-5).
3. The skills never push an image anywhere on their own.

## LV-8 Skills

1. `job-application-cv-create` writes the Arbeitsstand with the keys of LV-3 and asks before freezing.
2. `job-application-export` exports from a frozen Version, writes the Manifest and states the reproduction
   level in its report.
3. No skill edits a frozen Version, renames an Ausprägung or deletes a Version without the user's request.

## LV-9 Open points

| Point | Status |
|---|---|
| A stable `dokument_id` (UUID or derived) across Versionen | Decision for the user. Until then `auspraegung` plus `version` identify a document. |
| Floating Debian packages in the image | Mitigated by archiving the image (LV-7). A pinned snapshot repository would remove it. |
| Mapping the same Version to several PDF layouts | Not specified. A layout change of the plugin changes `document.tex` and is visible in the Manifest. |
| Freezing is done by a skill step, not enforced by a hook | Accepted. A changed hash is detected at reproduction (LV-6.4). |
| Versioning of Anschreiben and Motivationsschreiben | Not specified. Both are written per Vorgang and are not frozen; whether a sent letter needs the same Version and Manifest rules is open. |
| Manifest key `situation` | Removed from the Manifest (LV-6.3); `export_document.py` writes no `situation` (done, export, 0.2.0). |
| Export path of a frozen Version | `<ausprägung>/export/vNNN_<datum>.<ext>` (LV-2.3); `export_document.py` resolves `versionen/` to the `export/` folder of the Ausprägung (done, export, 0.2.0). |

## LV-10 Acceptance scenarios

| ID | Scenario | Expected behaviour |
|---|---|---|
| LV-A | A Version is exported twice with the same image | The two PDFs have the same SHA-256 |
| LV-B | `--reproduce` on an untouched Version and Manifest | Exit `0`, report "byte-identisch" |
| LV-C | The frozen Version was edited | Exit `3`, message that the source hash differs |
| LV-D | The image has another pandoc version | The result is reported, with the tool difference listed |
| LV-E | The Arbeitsstand has no `version_datum` | The PDF is made, with a notice that it is not byte-reproducible |
| LV-F | A Vorgang needs another focus | A new Ausprägung is derived from a Version; the old one is unchanged |
| LV-G | The Wurzel is in a repository that is not private | No personal files are committed (R-6) |

## LV-11 Sources

Own measurements of 2026-10-22 with the container image of this repository: two exports of the same source
differed in the PDF `/ID` and in the creation date; with a fixed epoch and a fixed trailer ID, 0 bytes
differed. External references for the mechanisms (not re-retrieved when this spec was written):

- reproducible-builds.org, `SOURCE_DATE_EPOCH` specification.
- LuaTeX reference manual, `pdf.settrailerid` and `FORCE_SOURCE_DATE`.
