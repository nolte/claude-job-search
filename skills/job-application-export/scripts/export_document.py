#!/usr/bin/env python3
"""Export one Bewerbungsdokument from its Markdown source.

Formats: pdf (LaTeX via LuaLaTeX), docx, html, md. The Markdown file is the only source;
nothing is edited in place (spec R-10, requirement ausgabeformate.md FA-O1).

Every export writes a manifest next to the output (<datei>.manifest.json): the hash of the source, of the
template and of the output, and the tool versions. A document with the frontmatter date `version_datum`
is frozen: the PDF dates and the PDF ID are derived from the source, so the same source, template and tools
give a byte-identical PDF (spec lebenslauf-versionen LV-6). `--reproduce` rebuilds an output from its
manifest and compares it.

The checks compare the export with its Markdown source and nothing else (key `pruefung` of the manifest): the word
multiset, the symbols of figures (`%`, `€`, `+`, ...), the order of the list items, the order of the headings and the
structure of the DOCX and HTML (headings, tables, text boxes, headers). They do not say that the text is true against the
Grundlage (that is `cv_checks.py`) or that an applicant tracking system reads the file.

Exit codes: 0 ok (or, for --reproduce, byte-identical); 1 error (missing tool, invalid arguments, unreadable input);
2 content check found a difference (words, symbols of figures or the order inside a list item); 3 --reproduce: output differs or the source hash no longer matches the manifest
(lebenslauf-versionen LV-6.4); 4 the PDF exceeds the page limit of its document type (LB-2.3, AS-7.1, MS-7). With 2 and
4 the file stays and the manifest is written. If both apply, the exit code is 2 and the page count is still reported.
The severity of a page overrun (Blocker for cv and letter, Warnung for motivation) is set by the quality gate
(LB-13, AS-12, MS-12).

The document type `email` exists only as Markdown (spec R-10.2); `--doc-type email` with another format is an error.
`--out-dir` must not lie inside the plugin repository (spec lokale-struktur LS-5.7, LS-2.4).

Defaults (spec lokale-struktur LS-3, lebenslauf-versionen LV-6): `--out-dir` is `export/` next to the source. A frozen
Version in `versionen/vNNN_<datum>.md` is exported to `../export/` of that folder, so the export sits next to the
Arbeitsstand. `--name` defaults to the source file name without `.md`. Every name is transliterated to ASCII
(`ä→ae, ö→oe, ü→ue, ß→ss`, spaces to `-`), so the file name travels through mail clients and portals unchanged (R-4).

DOCX metadata: the author fields (`dc:creator`, `cp:lastModifiedBy`) are cleared, so a portal does not read a tool
or account name as the author.

Usage:
  export_document.py INPUT.md --format {pdf,docx,html,md,tex} --doc-type {cv,letter,motivation,email}
                     [--out-dir DIR] [--name NAME]
  export_document.py --reproduce MANIFEST.json
"""

import argparse
import datetime
import hashlib
import html
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
PAGE_LIMITS = {"cv": 2, "letter": 1, "motivation": 2, "email": None}
OPEN_PLACEHOLDER = re.compile(r"\[(ERGÄNZEN|KLÄREN)")  # R-1 / R-7: not ready to send
EXIT_CONTENT = 2
EXIT_DIFFERENT = 3
EXIT_PAGES = 4
REFERENCE_DOCX = Path.home() / ".cache" / "claude-job-search" / "reference.docx"


class ExportError(Exception):
    pass


def require(tool, hint):
    path = shutil.which(tool)
    if path is None:
        raise ExportError(f"Werkzeug fehlt: {tool}. {hint}")
    return path


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# German umlauts keep their conventional two-letter form; letters without a decomposition get the nearest
# Latin letter. Everything else is decomposed (NFKD) and stripped of its accents: é -> e, ç -> c.
TRANSLITERATION = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss", " ": "-",
    "æ": "ae", "Æ": "Ae", "œ": "oe", "Œ": "Oe", "ø": "o", "Ø": "O", "ł": "l", "Ł": "L", "đ": "d", "Đ": "D",
    "ð": "d", "Ð": "D", "þ": "th", "Þ": "Th", "ı": "i",
})


def ascii_name(name):
    """File name in ASCII (R-4): umlauts and accented letters transliterated, spaces to hyphens, hyphens and
    underscores kept. Characters without a Latin equivalent are dropped."""
    name = unicodedata.normalize("NFKD", name.translate(TRANSLITERATION))
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    return re.sub(r"[^A-Za-z0-9._-]", "", name)


def in_plugin_repository(path):
    """True when `path` or a parent holds .claude-plugin/plugin.json of claude-job-search (LS-2.4, R-9.9)."""
    path = Path(path).resolve()
    for directory in (path, *path.parents):
        manifest = directory / ".claude-plugin" / "plugin.json"
        if manifest.is_file():
            try:
                if json.loads(manifest.read_text(encoding="utf-8")).get("name") == "claude-job-search":
                    return True
            except (OSError, ValueError):
                pass
    return False


ONE_PAGE_VARIANTS = ("stelle", "quereinstieg", "berufseinstieg")


def _key(value):
    """Frontmatter value as a comparable key: text, trimmed, lower case (a stray capital or space must not lose a limit)."""
    return str(value).strip().lower() if value is not None else ""


def page_limit_for(doc_type, meta):
    """Page limit of the document type. A Lebenslauf of the format `einseitig` is limited to one page (LB-2.3), a
    Motivationsschreiben of a job variant to one page (MS-7); a missing `variante` counts as `stelle` (MS-8)."""
    if doc_type == "cv" and _key(meta.get("format")) == "einseitig":
        return 1
    if doc_type == "motivation" and (_key(meta.get("variante")) or "stelle") in ONE_PAGE_VARIANTS:
        return 1
    return PAGE_LIMITS[doc_type]


def default_out_dir(source):
    """`export/` next to the source; for a frozen Version in `versionen/` the `export/` folder of the parent."""
    parent = source.parent
    if parent.name == "versionen":
        return parent.parent / "export"
    return parent / "export"


def source_date_epoch(meta):
    """Midnight UTC of the frontmatter date `version_datum`, or None when the document is not frozen."""
    value = meta.get("version_datum")
    if not value:
        return None
    try:
        day = datetime.date.fromisoformat(value)
    except ValueError:
        raise ExportError(f"version_datum '{value}' ist kein gültiges Datum (erwartet JJJJ-MM-TT).") from None
    return int(datetime.datetime(day.year, day.month, day.day, tzinfo=datetime.timezone.utc).timestamp())


def trailer_id(source, epoch, doc_type):
    """A PDF ID that depends only on the inputs, so the same inputs give the same PDF bytes."""
    digest = hashlib.sha256()
    for path in (source, TEMPLATES / "document.tex", TEMPLATES / "cv.lua"):
        digest.update(Path(path).read_bytes())
    digest.update(f"{epoch}:{doc_type}".encode("utf-8"))
    return digest.hexdigest()[:32].upper()


def tool_version(command):
    try:
        lines = subprocess.run(command, capture_output=True, text=True).stdout.splitlines()
    except FileNotFoundError:
        return None
    return lines[0].strip() if lines else None


def unquote(value):
    """Strip one pair of enclosing YAML quotes, so `version_datum: "2026-01-01"` reads as 2026-01-01."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def read_document(path):
    text = Path(path).read_text(encoding="utf-8")
    meta, body = {}, text
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = unquote(value.strip())
        body = text[match.end():]
    return meta, body


def token_list(text):
    # Hyphens are dropped before splitting, so "E-Mail" equals "E-" + line break + "Mail" in a PDF.
    # A hyphenated word and its line-broken form then count as the same word.
    text = re.sub(r"-\s*", "", text)
    return [t.lower() for t in re.findall(r"[0-9A-Za-zÄÖÜäöüß]+", text)]


def tokens(text):
    return Counter(token_list(text))


def compare_content(source_body, exported_text):
    """FA-O6: word multiset of source and export must match."""
    # The target of a link (`[text](https://…)`) is not text of the export: PDF, DOCX and HTML carry the link text only.
    expected, actual = tokens(plain_markdown(source_body)), tokens(exported_text)
    return expected - actual, actual - expected


FIGURE_SYMBOLS = "%€$+&"  # a lost "%" turns "40 %" into "40"; the word check cannot see it
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*\S)\s*$")


def plain_markdown(text):
    """The words and symbols of a Markdown text without link targets and the markers at the start of a line."""
    text = re.sub(r"\]\([^)\s]*\)", "]", text)
    text = re.sub(r"<(?:https?://|mailto:)[^>]*>", " ", text)
    return "\n".join(re.sub(r"^\s*(?:#{1,6}|[-*+]|\d+[.)])\s+", "", line) for line in text.splitlines())


def figure_symbols(text):
    return Counter(char for char in text if char in FIGURE_SYMBOLS)


def fact_differences(source_body, exported_text):
    """Differences that the word multiset cannot see, as a list of messages (empty when none).

    1. A symbol of a figure is lost or added: `40 %` read back as `40`, `C++` as `C`.
    2. A list item (bullet) of the source does not stand in the export as the same words in the same order, or after the
       item before it: `von 800 ms auf 120 ms` read back as `von 120 ms auf 800 ms`, or two bullets swapped. Items are the
       carrier of the facts of a Lebenslauf. Headings and the station lines of level 3 are laid out in a grid and are not
       compared here (see first_order_difference).
    The words inside one item must stand next to each other; line and page breaks, hyphens and layout are no difference.
    Run it when the word multiset is equal, so that a lost word is not reported twice."""
    messages = []
    lost = figure_symbols(plain_markdown(source_body)) - figure_symbols(exported_text)
    added = figure_symbols(exported_text) - figure_symbols(plain_markdown(source_body))
    if lost:
        messages.append("Zeichen fehlen im Export: " + ", ".join(f"{symbol} ×{count}" for symbol, count in lost.items()))
    if added:
        messages.append("Zeichen kommen im Export hinzu: " + ", ".join(f"{symbol} ×{count}" for symbol, count in added.items()))
    exported = token_list(exported_text)
    cursor = 0
    for line in source_body.splitlines():
        item = LIST_ITEM.match(line)
        words = token_list(plain_markdown(item.group(1))) if item else []
        if not words:
            continue
        for start in range(cursor, len(exported) - len(words) + 1):
            if exported[start:start + len(words)] == words:
                cursor = start + len(words)
                break
        else:
            messages.append("Stichpunkt im Export nicht in Wortlaut und Reihenfolge der Quelle: „" + " ".join(words[:8]) + "…“")
            break  # the cursor is no longer reliable after a miss; the first item is the one to look at
    return messages


def first_order_difference(source_body, exported_text):
    """EXP-002: the first heading of level 1 or 2 that the export does not carry after the previous one, else None.

    The word multiset says nothing about order. The headings give the order of the sections; the words inside a
    section are not compared, because the templates move header fields (the name stands before "Persönliche Daten" in
    the CV layout) and the station lines of level 3 are laid out in a grid (CG-13.2 row 15).

    A heuristic: the words of a heading are searched after the previous heading, so a one-word heading whose word also
    stands in the text before it can hide a swap. Only `#` headings are read."""
    exported = token_list(exported_text)
    cursor = 0
    for line in source_body.splitlines():
        heading = re.match(r"#{1,2}\s+(.+?)\s*#*\s*$", line)
        words = token_list(heading.group(1)) if heading else []
        if not words:
            continue
        for start in range(cursor, len(exported) - len(words) + 1):
            if exported[start:start + len(words)] == words:
                cursor = start + len(words)
                break
        else:
            return heading.group(1)
    return None


def reference_docx(pandoc):
    """Neutral reference.docx (Arial, A4, 2.5 cm, Word heading styles) for the DOCX export, decision O-2."""
    if REFERENCE_DOCX.exists():
        return REFERENCE_DOCX
    REFERENCE_DOCX.parent.mkdir(parents=True, exist_ok=True)
    with REFERENCE_DOCX.open("wb") as handle:
        subprocess.run([pandoc, "--print-default-data-file", "reference.docx"], stdout=handle, check=True)
    from docx import Document
    from docx.shared import Cm, Pt

    doc = Document(REFERENCE_DOCX)
    for section in doc.sections:
        section.page_width, section.page_height = Cm(21), Cm(29.7)
        section.left_margin = section.right_margin = Cm(2.5)
        section.top_margin = section.bottom_margin = Cm(2.5)
    for name in ["Normal", "Body Text", "First Paragraph", "Compact", "Title", "Heading 1", "Heading 2"]:
        try:
            style = doc.styles[name]
        except KeyError:
            continue
        style.font.name = "Arial"
        if name in ("Normal", "Body Text", "First Paragraph", "Compact"):
            style.font.size = Pt(10.5)
    doc.save(REFERENCE_DOCX)
    return REFERENCE_DOCX


def export_md(source, out_file):
    shutil.copyfile(source, out_file)
    return out_file.read_text(encoding="utf-8"), None


def embed_option(version_line):
    """`--embed-resources` exists from pandoc 2.19; the image of the Dockerfile ships 2.17, which knows `--self-contained`."""
    match = re.search(r"pandoc(?:\.exe)?\s+(\d+)\.(\d+)", version_line or "")
    return "--embed-resources" if not match or (int(match.group(1)), int(match.group(2))) >= (2, 19) else "--self-contained"


def export_html(pandoc, source, out_file, grundlage_hash):
    subprocess.run(
        [pandoc, str(source), "-f", "markdown", "-t", "html5", "--standalone", embed_option(tool_version([pandoc, "--version"])),
         "--css", str(TEMPLATES / "style.css"), "-M", "lang=de", "-o", str(out_file)],
        check=True,
    )
    content = out_file.read_text(encoding="utf-8")
    if grundlage_hash:
        content = content.replace("<head>", f'<head>\n<meta name="grundlage_hash" content="{grundlage_hash}">', 1)
        out_file.write_text(content, encoding="utf-8")
    plain = re.sub(r"<(style|title)\b.*?</\1>", " ", content, flags=re.S)
    plain = html.unescape(re.sub(r"<[^>]+>", " ", plain))
    return plain, None


def export_docx(pandoc, source, out_file, name, grundlage_hash, epoch=None):
    reference = reference_docx(pandoc)
    subprocess.run(
        [pandoc, str(source), "-f", "markdown", "-t", "docx", "--reference-doc", str(reference),
         "-M", "lang=de-DE", "-o", str(out_file)],
        check=True,
    )
    from docx import Document

    doc = Document(out_file)
    doc.core_properties.title = name
    # Neutral metadata: no tool or account name as author (ATS portals show these fields).
    doc.core_properties.author = ""
    doc.core_properties.last_modified_by = ""
    doc.core_properties.comments = ""
    if grundlage_hash:
        doc.core_properties.keywords = f"grundlage_hash:{grundlage_hash}"
    moment = None
    if epoch is not None:
        # a frozen Version: the dates of the document and of its zip entries come from `version_datum`, not from the clock
        moment = datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc)
        doc.core_properties.created = doc.core_properties.modified = moment.replace(tzinfo=None)
    doc.save(out_file)
    if moment is not None:
        fix_zip_dates(out_file, moment)
    return docx_text(Document(out_file)), None


def fix_zip_dates(path, moment):
    """Rewrite a zip with one fixed date for every entry (the clock time of the export would differ by the second).

    The new file is written beside the old one and replaces it, so an interruption leaves the finished DOCX intact.
    The entries get the same creator system on every host, so the bytes do not depend on the operating system.
    """
    stamp = max(moment.timetuple()[:6], (1980, 1, 1, 0, 0, 0))
    temp = path.with_name(path.name + ".tmp")
    try:
        with zipfile.ZipFile(path) as source:
            entries = [(info, source.read(info.filename)) for info in source.infolist()]
        with zipfile.ZipFile(temp, "w") as target:
            for info, data in entries:
                fixed = zipfile.ZipInfo(info.filename, date_time=stamp)
                fixed.compress_type, fixed.external_attr, fixed.create_system = info.compress_type, info.external_attr, 3
                target.writestr(fixed, data)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def docx_text(doc):
    """Paragraphs and table cells in document order. A table is content that stays readable; that it is a table is
    reported by structure_notes, not mistaken for missing words."""
    from docx.table import Table

    lines = []
    for child in doc.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            # all runs, also those inside a hyperlink: Paragraph.text leaves them out in older python-docx
            lines.append("".join(node.text or "" for node in child.iter() if node.tag.rsplit("}", 1)[-1] == "t"))
        elif tag == "tbl":
            lines += [cell.text for row in Table(child, doc).rows for cell in row.cells]
    return "\n".join(lines)


def source_heading_levels(body):
    return Counter(len(m.group(1)) for m in (re.match(r"(#{1,6})\s+\S", line) for line in body.splitlines()) if m)


def structure_notes(fmt, out_file, body):
    """Structure of a DOCX or HTML export that a parser depends on, as notes (empty when nothing stands out).

    Reported, never blocking: headings per level against the source, tables, text boxes, images, text in headers and
    footers (DOCX). The spec asks for a single column without tables (R-10 items 6 and 7). This is a check of the file
    against its source, not a test with any applicant tracking system."""
    expected = source_heading_levels(body)
    notes = []
    if fmt == "docx":
        from docx import Document

        doc = Document(out_file)
        found = Counter()
        for paragraph in doc.paragraphs:
            match = re.match(r"(?:Heading|Überschrift)\s+(\d)$", paragraph.style.name or "")
            if match:
                found[int(match.group(1))] += 1
        xml = doc.element.xml
        if doc.tables:
            notes.append(f"{len(doc.tables)} Tabelle(n): Parser lesen Tabellen unterschiedlich, die Vorgabe ist eine Spalte ohne Tabelle (R-10)")
        if "txbxContent" in xml:
            notes.append("Textfeld im Dokument: sein Text kann von einem Parser übersprungen werden")
        if "<w:drawing" in xml or "<w:pict" in xml:
            notes.append("Bild oder Zeichnung im Dokument")
        header_text = " ".join(p.text for section in doc.sections for part in (section.header, section.footer) for p in part.paragraphs).strip()
        if header_text:
            notes.append("Text in Kopf- oder Fußzeile: nicht jeder Parser liest ihn")
    elif fmt == "html":
        content = out_file.read_text(encoding="utf-8")
        found = Counter(int(level) for level in re.findall(r"<h([1-6])\b", content))
        if "<table" in content:
            notes.append(f"{content.count('<table')} Tabelle(n) im HTML")
        if "<img" in content:
            notes.append("Bild im HTML")
    else:
        return notes
    if found != expected:
        render = lambda counter: ", ".join(f"H{level}×{count}" for level, count in sorted(counter.items())) or "keine"
        notes.append(f"Überschriften weichen von der Quelle ab: Quelle {render(expected)}, Export {render(found)}")
    return notes


# The layout macros that templates/cv.lua emits. For the content check each one reads back as its arguments
# separated by spaces, so the words of the source are compared and the layout is not.
READBACK_MACROS = "\\newcommand{\\cvheader}[4]{#1 #2 #3 #4\\par}\\newcommand{\\cvstation}[3]{#1 #2 #3\\par}\\newcommand{\\cvrow}[2]{#1 #2\\par}"


def latex_args(pandoc, source, out_file, grundlage_hash, doc_type, trailerid=None):
    """pandoc arguments for the LaTeX source. The Lebenslauf gets the layout filter; other types get the letter page."""
    args = [pandoc, str(source), "-f", "markdown", "-t", "latex", "--template", str(TEMPLATES / "document.tex"),
            "-M", "lang=de", "-o", str(out_file)]
    if doc_type == "cv":
        args += ["--lua-filter", str(TEMPLATES / "cv.lua")]
    else:
        args += ["-V", "letter=true"]
    if grundlage_hash:
        args += ["-M", f"keywords=grundlage_hash:{grundlage_hash}"]
    if trailerid:
        args += ["-M", f"trailerid={trailerid}"]
    return args


def export_tex(pandoc, source, out_file, grundlage_hash, doc_type="cv", trailerid=None):
    """LaTeX source with the Bewerbung template. Needs pandoc only, no LuaLaTeX."""
    subprocess.run(latex_args(pandoc, source, out_file, grundlage_hash, doc_type, trailerid), check=True)
    # Content check reads the LaTeX back as plain text. Only the document body counts: the preamble holds
    # the template's layout macros, which are not content and which some pandoc versions cannot read back.
    tex = out_file.read_text(encoding="utf-8")
    start = tex.index("\\begin{document}") + len("\\begin{document}")
    end = tex.rindex("\\end{document}")
    body = READBACK_MACROS + "\n".join(line for line in tex[start:end].splitlines() if not line.lstrip().startswith("%"))
    plain = subprocess.run([pandoc, "-f", "latex", "-t", "plain"], input=body,
                           capture_output=True, text=True, check=True).stdout
    return plain, None


def export_pdf(pandoc, source, out_dir, name, grundlage_hash, doc_type="cv", epoch=None):
    engine = require("lualatex", "Installiere TeX Live mit LuaLaTeX (Paket texlive-luatex) — Entscheidung O-3.")
    require("pdfinfo", "Installiere poppler-utils (pdfinfo, pdftotext).")
    tex = out_dir / f"{name}.tex"
    environment = dict(os.environ)
    trailerid = None
    if epoch is not None:
        # a frozen document: fixed PDF dates and a PDF ID derived from the inputs
        environment.update(SOURCE_DATE_EPOCH=str(epoch), FORCE_SOURCE_DATE="1")
        trailerid = trailer_id(source, epoch, doc_type)
    subprocess.run(latex_args(pandoc, source, tex, grundlage_hash, doc_type, trailerid), check=True)
    subprocess.run(
        [engine, "-interaction=nonstopmode", f"-output-directory={out_dir}", tex.name],
        cwd=out_dir, capture_output=True, text=True, env=environment,
    )
    pdf = out_dir / f"{name}.pdf"
    if not pdf.exists():
        log = (out_dir / f"{name}.log")
        tail = log.read_text(encoding="utf-8", errors="replace").splitlines()[-15:] if log.exists() else []
        raise ExportError("PDF-Erzeugung fehlgeschlagen. Letzte Log-Zeilen:\n" + "\n".join(tail))
    for suffix in (".aux", ".log", ".out", ".toc"):
        (out_dir / f"{name}{suffix}").unlink(missing_ok=True)
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    raw = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    return strip_page_numbers(raw), pages


def strip_page_numbers(text):
    """Drop the page number the template prints from the pdftotext output (pages are separated by form feeds).

    The page number is layout, not content. It is removed from the end of its own page only, so a line that
    holds just a year, as in the period column of the Lebenslauf, stays: it is content.
    """
    kept = []
    for number, page_text in enumerate(text.split("\f"), 1):
        lines = page_text.splitlines()
        while lines and not lines[-1].strip():
            lines.pop()
        if lines and lines[-1].strip() == str(number):
            lines.pop()
        kept.extend(lines)
    return "\n".join(kept)


def tool_versions(fmt):
    """The versions of the external tools an export in this format runs; lualatex only for the PDF."""
    return {
        "pandoc": tool_version(["pandoc", "--version"]),
        "lualatex": tool_version(["lualatex", "--version"]) if fmt == "pdf" else None,
        "python-docx": python_docx_version() if fmt == "docx" else None,
    }


def python_docx_version():
    try:
        return importlib.metadata.version("python-docx")
    except importlib.metadata.PackageNotFoundError:
        return None


def build_manifest(source, meta, fmt, doc_type, name, out_file, pages, epoch, limit=None, checks=None):
    reproducible = fmt in ("tex", "pdf", "docx") and epoch is not None
    return {
        "schema": 1,
        "name": name,
        "dokumenttyp": doc_type,
        "format": fmt,
        "quelle": {"pfad": os.path.relpath(source, out_file.parent), "sha256": sha256_file(source)},
        "frontmatter": {key: meta[key] for key in ("auspraegung", "version", "version_datum", "grundlage_hash", "format") if key in meta},
        "source_date_epoch": epoch,
        "byte_reproduzierbar": reproducible,
        "vorlage": {"document.tex": sha256_file(TEMPLATES / "document.tex"), "cv.lua": sha256_file(TEMPLATES / "cv.lua")},
        "werkzeuge": {**tool_versions(fmt), "python": platform.python_version()},
        "umgebung": {"plugin_revision": os.environ.get("PLUGIN_REVISION") or None, "image_id": os.environ.get("EXPORT_IMAGE_ID") or None},
        "ausgabe": {"datei": out_file.name, "sha256": sha256_file(out_file), "seiten": pages, "seitenlimit": limit,
                    "seitenlimit_ueberschritten": bool(pages is not None and limit is not None and pages > limit)},
        # Result of the checks of this run against the source. It says nothing about the truth against the Grundlage or
        # about an applicant tracking system; a manifest exists for a failed check as well.
        "pruefung": checks,
    }


def write_manifest(manifest, out_file):
    path = out_file.parent / f"{out_file.name}.manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def reproduce(manifest_path):
    """Rebuild an output from its manifest and compare it. Exit 0 identical, 3 different or source changed, 1 error."""
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = (manifest_path.parent / manifest["quelle"]["pfad"]).resolve()
    if not source.is_file():
        print(f"Fehler: Quelle nicht gefunden: {source}", file=sys.stderr)
        return 1
    if sha256_file(source) != manifest["quelle"]["sha256"]:
        print("Quelle verändert: der Hash der Quelle weicht vom Manifest ab. Eine festgeschriebene Version darf nicht "
              "bearbeitet werden (lebenslauf-versionen LV-3).", file=sys.stderr)
        return EXIT_DIFFERENT
    with tempfile.TemporaryDirectory() as tmp:
        code = main([str(source), "--format", manifest["format"], "--doc-type", manifest["dokumenttyp"],
                     "--out-dir", tmp, "--name", manifest["name"], "--no-manifest"])
        if code not in (0, EXIT_CONTENT, EXIT_PAGES):
            return 1
        # The file is named as main() names it today; an older manifest may record a name that was
        # transliterated differently (`Max_Müller` before 0.2.0), so the recorded `datei` is not used.
        rebuilt = Path(tmp) / f"{ascii_name(manifest['name'])}.{manifest['format']}"
        identical = sha256_file(rebuilt) == manifest["ausgabe"]["sha256"]
    differences = [f"{tool}: {manifest['werkzeuge'].get(tool)} -> {version}"
                   for tool, version in tool_versions(manifest["format"]).items()
                   if manifest["werkzeuge"].get(tool) != version]
    for tool in ("document.tex", "cv.lua"):
        if manifest["vorlage"].get(tool) != sha256_file(TEMPLATES / tool):
            differences.append(f"Vorlage {tool} hat sich geändert")
    print("Reproduktion: byte-identisch" if identical else "Reproduktion: abweichend")
    if manifest["ausgabe"].get("seitenlimit_ueberschritten"):
        print(f"Hinweis: Der ursprüngliche Export überschritt das Seitenlimit "
              f"({manifest['ausgabe'].get('seiten')} von {manifest['ausgabe'].get('seitenlimit')}).")
    for line in differences:
        print(f"  Unterschied: {line}")
    if not identical and not manifest["byte_reproduzierbar"]:
        print("  Hinweis: Dieser Export war nicht als byte-reproduzierbar ausgewiesen (kein version_datum oder Format).")
    return 0 if identical else EXIT_DIFFERENT


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--format", choices=["pdf", "docx", "html", "md", "tex"])
    parser.add_argument("--doc-type", choices=list(PAGE_LIMITS))
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--name", help="Dateiname ohne Erweiterung, z. B. Vorname_Nachname_Lebenslauf")
    parser.add_argument("--reproduce", type=Path, metavar="MANIFEST", help="Ausgabe aus dem Manifest neu erzeugen und vergleichen")
    parser.add_argument("--no-manifest", action="store_true", help="kein Manifest schreiben (intern, für --reproduce)")
    args = parser.parse_args(argv)
    if args.reproduce:
        try:
            return reproduce(args.reproduce)
        except subprocess.CalledProcessError as error:
            print(f"Fehler: Werkzeug schlug fehl: {error.cmd[0]} (Exit {error.returncode})", file=sys.stderr)
            return 1
        except (OSError, KeyError, ValueError, ExportError) as error:
            print(f"Fehler: Manifest nicht lesbar oder unvollständig: {error}", file=sys.stderr)
            return 1
    if not (args.input and args.format and args.doc_type):
        parser.error("INPUT, --format und --doc-type sind erforderlich (oder --reproduce MANIFEST)")

    try:
        if args.doc_type == "email" and args.format != "md":
            raise ExportError("Der Dokumenttyp email gibt es nur als Markdown (--format md, Spec R-10.2).")
        meta, body = read_document(args.input)
        grundlage_hash = meta.get("grundlage_hash")
        if not grundlage_hash:
            print("Warnung: kein grundlage_hash im Frontmatter. Der Export ist nicht prüfbar gegen die Grundlage "
                  "(R-10.3).", file=sys.stderr)
        # the whole file, frontmatter included: the same text and marker as CV-01 in the quality gate
        open_placeholders = len(OPEN_PLACEHOLDER.findall(args.input.read_text(encoding="utf-8")))
        if open_placeholders:
            print(f"Warnung: {open_placeholders} offene Platzhalter ([ERGÄNZEN …] oder [KLÄREN …]) im Dokument. Der Export "
                  "zählt die ganze Datei (Frontmatter eingeschlossen) und ist nicht versandfertig (R-7, CV-01, BR-01); der Export "
                  "blockiert nicht.",
                  file=sys.stderr)
        name = ascii_name(args.name or args.input.stem)
        if not name:
            raise ExportError("Der Dateiname ist nach der ASCII-Umschrift leer. --name angeben (R-4).")
        out_dir = (args.out_dir or default_out_dir(args.input)).resolve()
        if in_plugin_repository(out_dir):
            raise ExportError(f"Ausgabeordner {out_dir} liegt im Plugin-Repository. Es wird nur in die Wurzel "
                              "geschrieben (LS-5.7); --out-dir auf einen Ordner der Wurzel setzen.")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{name}.{args.format}"
        pandoc = require("pandoc", "Installiere pandoc (z. B. pip install pypandoc_binary oder Paket pandoc).")

        pages = None
        try:
            epoch = source_date_epoch(meta)
        except ExportError as error:
            # Only the PDF and its LaTeX source use the date (LV-6). The other formats report it and go on,
            # as they do when the date is missing.
            if args.format in ("pdf", "tex"):
                raise
            print(f"Warnung: {error} Das Datum wird für dieses Format ignoriert.", file=sys.stderr)
            epoch = None
        if args.format in ("pdf", "docx") and epoch is None:
            print(f"Hinweis: kein version_datum im Frontmatter. Die {args.format.upper()} enthält das heutige Datum und ist nicht "
                  "byte-reproduzierbar (lebenslauf-versionen LV-6).", file=sys.stderr)
        if args.format == "md":
            exported, _ = export_md(args.input, out_file)
            exported_text = None
        elif args.format == "html":
            exported_text, _ = export_html(pandoc, args.input, out_file, grundlage_hash)
        elif args.format == "tex":
            exported_text, _ = export_tex(pandoc, args.input, out_file, grundlage_hash, args.doc_type)
        elif args.format == "docx":
            exported_text, _ = export_docx(pandoc, args.input, out_file, name, grundlage_hash, epoch)
        else:
            exported_text, pages = export_pdf(pandoc, args.input, out_dir, name, grundlage_hash,
                                              args.doc_type, epoch)

        status = "ok"
        facts = []
        if exported_text is not None:
            missing, extra = compare_content(body, exported_text)
            if missing or extra:
                status = "Inhaltsabweichung"
                print(f"Fehlend im Export: {sum(missing.values())} Wörter, z. B. {list(missing)[:5]}", file=sys.stderr)
                print(f"Zusätzlich im Export: {sum(extra.values())} Wörter, z. B. {list(extra)[:5]}", file=sys.stderr)
            else:
                facts = fact_differences(body, exported_text)
                for message in facts:
                    print(f"Inhaltsabweichung: {message}", file=sys.stderr)
                if facts:
                    status = "Inhaltsabweichung"
        notes = structure_notes(args.format, out_file, body) if args.format in ("docx", "html") else []
        for note in notes:
            print(f"Struktur: {note}", file=sys.stderr)
        order = None
        if exported_text is not None and status == "ok":
            order = first_order_difference(body, exported_text)
            if order:
                print(f"Reihenfolge der Überschriften weicht ab: „{order}“ steht im Export nicht an der Stelle der Quelle", file=sys.stderr)
        limit = page_limit_for(args.doc_type, meta)
        over_limit = pages is not None and limit is not None and pages > limit
        if over_limit:
            print(f"Seitenlimit überschritten: {pages} Seiten, Grenze für diesen Dokumenttyp ist {limit} "
                  "(LB-2.3, AS-7.1, MS-7).", file=sys.stderr)
        print(f"{out_file}")
        checks = {
            "inhalt": "nicht_geprueft" if exported_text is None else ("ok" if status == "ok" else "abweichung"),
            "zeichen_und_stichpunkte": "nicht_geprueft" if exported_text is None else ("abweichung" if facts else "ok"),
            "reihenfolge_ueberschriften": "nicht_geprueft" if exported_text is None or status != "ok" else ("abweichung" if order else "ok"),
            "struktur_hinweise": notes,
            "platzhalter_offen": open_placeholders,
            "grundlage_hash_vorhanden": bool(grundlage_hash),
            "gegen": "quelle",
        }
        if not args.no_manifest:
            print(f"Manifest: {write_manifest(build_manifest(args.input.resolve(), meta, args.format, args.doc_type, name, out_file, pages, epoch, limit, checks), out_file)}")
        if pages is not None:
            print(f"Seiten: {pages}")
            print(f"Seitenlimit: {'überschritten' if over_limit else 'ok'} ({pages} von {limit})" if limit else "Seitenlimit: keines")
        print(f"Inhaltsprüfung: {status}")
        if notes:
            print(f"Struktur: {len(notes)} Hinweis(e) (Warnung, Exit-Code unverändert)")
        if order:
            print("Reihenfolge: Abweichung bei den Überschriften (Warnung, Exit-Code unverändert)")
        if not grundlage_hash:
            print("grundlage_hash: fehlt")
        if open_placeholders:
            print(f"Platzhalter: {open_placeholders} offen (nicht versandfertig)")
        if status != "ok":
            return EXIT_CONTENT
        return EXIT_PAGES if over_limit else 0
    except ExportError as error:
        print(f"Fehler: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Fehler: Datei nicht lesbar oder nicht schreibbar: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"Fehler: Werkzeug schlug fehl: {error.cmd[0]} (Exit {error.returncode})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
