#!/usr/bin/env python3
"""Export one Bewerbungsdokument from its Markdown source.

Formats: pdf (LaTeX via LuaLaTeX), docx, html, md. The Markdown file is the only source;
nothing is edited in place (spec R-10, requirement ausgabeformate.md FA-O1).

Usage:
  export_document.py INPUT.md --format {pdf,docx,html,md} --doc-type {cv,letter,motivation,email}
                     [--out-dir DIR] [--name NAME]
"""

import argparse
import html
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
PAGE_LIMITS = {"cv": 2, "letter": 1, "motivation": 2, "email": None}
REFERENCE_DOCX = Path.home() / ".cache" / "claude-job-search" / "reference.docx"


class ExportError(Exception):
    pass


def require(tool, hint):
    path = shutil.which(tool)
    if path is None:
        raise ExportError(f"Werkzeug fehlt: {tool}. {hint}")
    return path


def read_document(path):
    text = Path(path).read_text(encoding="utf-8")
    meta, body = {}, text
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
        body = text[match.end():]
    return meta, body


def tokens(text):
    # Hyphens are dropped before splitting, so "E-Mail" equals "E-" + line break + "Mail" in a PDF.
    # A hyphenated word and its line-broken form then count as the same word.
    text = re.sub(r"-\s*", "", text)
    return Counter(t.lower() for t in re.findall(r"[0-9A-Za-zÄÖÜäöüß]+", text))


def compare_content(source_body, exported_text):
    """FA-O6: word multiset of source and export must match."""
    expected, actual = tokens(source_body), tokens(exported_text)
    return expected - actual, actual - expected


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


def export_html(pandoc, source, out_file, grundlage_hash):
    subprocess.run(
        [pandoc, str(source), "-f", "markdown", "-t", "html5", "--standalone", "--embed-resources",
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


def export_docx(pandoc, source, out_file, name, grundlage_hash):
    reference = reference_docx(pandoc)
    subprocess.run(
        [pandoc, str(source), "-f", "markdown", "-t", "docx", "--reference-doc", str(reference),
         "-M", "lang=de-DE", "-o", str(out_file)],
        check=True,
    )
    from docx import Document

    doc = Document(out_file)
    doc.core_properties.title = name
    if grundlage_hash:
        doc.core_properties.keywords = f"grundlage_hash:{grundlage_hash}"
    doc.save(out_file)
    text = "\n".join(paragraph.text for paragraph in Document(out_file).paragraphs)
    return text, None


# The layout macros that templates/cv.lua emits. For the content check each one reads back as its arguments
# separated by spaces, so the words of the source are compared and the layout is not.
READBACK_MACROS = "\\newcommand{\\cvheader}[4]{#1 #2 #3 #4\\par}\\newcommand{\\cvstation}[3]{#1 #2 #3\\par}\\newcommand{\\cvrow}[2]{#1 #2\\par}"


def latex_args(pandoc, source, out_file, grundlage_hash, doc_type):
    """pandoc arguments for the LaTeX source. The Lebenslauf gets the layout filter; other types get the letter page."""
    args = [pandoc, str(source), "-f", "markdown", "-t", "latex", "--template", str(TEMPLATES / "document.tex"),
            "-M", "lang=de", "-o", str(out_file)]
    if doc_type == "cv":
        args += ["--lua-filter", str(TEMPLATES / "cv.lua")]
    else:
        args += ["-V", "letter=true"]
    if grundlage_hash:
        args += ["-M", f"keywords=grundlage_hash:{grundlage_hash}"]
    return args


def export_tex(pandoc, source, out_file, grundlage_hash, doc_type="cv"):
    """LaTeX source with the Bewerbung template. Needs pandoc only, no LuaLaTeX."""
    subprocess.run(latex_args(pandoc, source, out_file, grundlage_hash, doc_type), check=True)
    # Content check reads the LaTeX back as plain text. Only the document body counts: the preamble holds
    # the template's layout macros, which are not content and which some pandoc versions cannot read back.
    tex = out_file.read_text(encoding="utf-8")
    start = tex.index("\\begin{document}") + len("\\begin{document}")
    end = tex.rindex("\\end{document}")
    body = READBACK_MACROS + "\n".join(line for line in tex[start:end].splitlines() if not line.lstrip().startswith("%"))
    plain = subprocess.run([pandoc, "-f", "latex", "-t", "plain"], input=body,
                           capture_output=True, text=True, check=True).stdout
    return plain, None


def export_pdf(pandoc, source, out_dir, name, grundlage_hash, page_limit, doc_type="cv"):
    engine = require("lualatex", "Installiere TeX Live mit LuaLaTeX (Paket texlive-luatex) — Entscheidung O-3.")
    require("pdfinfo", "Installiere poppler-utils (pdfinfo, pdftotext).")
    tex = out_dir / f"{name}.tex"
    subprocess.run(latex_args(pandoc, source, tex, grundlage_hash, doc_type), check=True)
    result = subprocess.run(
        [engine, "-interaction=nonstopmode", f"-output-directory={out_dir}", tex.name],
        cwd=out_dir, capture_output=True, text=True,
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
    if page_limit and pages > page_limit:
        print(f"Warnung: {pages} Seiten, Grenze für diesen Dokumenttyp ist {page_limit} (FA-O13).", file=sys.stderr)
    raw = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    # The page number printed by the template is layout, not content. Drop it from the end of its page only:
    # a line that holds just a year, as in the period column of the Lebenslauf, is content.
    kept = []
    for number, page_text in enumerate(raw.split("\f"), 1):
        lines = page_text.splitlines()
        while lines and not lines[-1].strip():
            lines.pop()
        if lines and lines[-1].strip() == str(number):
            lines.pop()
        kept.extend(lines)
    return "\n".join(kept), pages


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", required=True, choices=["pdf", "docx", "html", "md", "tex"])
    parser.add_argument("--doc-type", required=True, choices=list(PAGE_LIMITS))
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--name", help="Dateiname ohne Erweiterung, z. B. Vorname_Nachname_Lebenslauf")
    args = parser.parse_args(argv)

    try:
        meta, body = read_document(args.input)
        grundlage_hash = meta.get("grundlage_hash")
        if not grundlage_hash:
            print("Warnung: kein grundlage_hash im Frontmatter. Der Export ist nicht prüfbar gegen die Grundlage.",
                  file=sys.stderr)
        name = args.name or args.input.stem
        out_dir = (args.out_dir or args.input.parent / "export").resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{name}.{args.format}"
        pandoc = require("pandoc", "Installiere pandoc (z. B. pip install pypandoc_binary oder Paket pandoc).")

        pages = None
        if args.format == "md":
            exported, _ = export_md(args.input, out_file)
            exported_text = None
        elif args.format == "html":
            exported_text, _ = export_html(pandoc, args.input, out_file, grundlage_hash)
        elif args.format == "tex":
            exported_text, _ = export_tex(pandoc, args.input, out_file, grundlage_hash, args.doc_type)
        elif args.format == "docx":
            exported_text, _ = export_docx(pandoc, args.input, out_file, name, grundlage_hash)
        else:
            exported_text, pages = export_pdf(pandoc, args.input, out_dir, name, grundlage_hash,
                                              PAGE_LIMITS[args.doc_type], args.doc_type)

        status = "ok"
        if exported_text is not None:
            missing, extra = compare_content(body, exported_text)
            if missing or extra:
                status = "Inhaltsabweichung"
                print(f"Fehlend im Export: {sum(missing.values())} Wörter, z. B. {list(missing)[:5]}", file=sys.stderr)
                print(f"Zusätzlich im Export: {sum(extra.values())} Wörter, z. B. {list(extra)[:5]}", file=sys.stderr)
        print(f"{out_file}")
        if pages is not None:
            print(f"Seiten: {pages}")
        print(f"Inhaltsprüfung: {status}")
        return 0 if status == "ok" else 2
    except ExportError as error:
        print(f"Fehler: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"Fehler: Werkzeug schlug fehl: {error.cmd[0]} (Exit {error.returncode})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
