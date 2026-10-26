#!/usr/bin/env python3
"""ATS-relevant technical checks of one exported file (spec qualitaetssicherung QS-13).

A library of `qualitaet.py`, not a second quality architecture: `check_file` takes the exported file, the Markdown body
of its source and the text read back from the export, and returns findings for the checks `EX-03` and `ATS-01` to
`ATS-05`; `key_terms` returns the findings of `KW-01`. `qualitaet.py` turns them into results, binds them to the
hashes of the files and decides about the approval.

The checks look at properties a parser depends on: a valid container, text that can be read back, headings that stay
headings and stay with their content, periods that stay with their station, contact data that can be read, no hidden
text, no information that only a picture carries, no text outside the page. They do not know any applicant tracking
system: a result without findings means "nothing found", not "this system reads the file".

Reads files and runs the local tools pdfinfo, pdffonts, pdfimages and pdftotext (poppler-utils). It writes nothing,
sends nothing and opens no network connection. Findings never contain the text of an address or a number.
Standard library only.
"""

import html
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter

import cv_checks as cv

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"(?<![\w/])(?:\+|00)?\d[\d ()/-]{7,}\d")
PERIOD = re.compile(r"(?<![\d/])((?:\d{1,2}/)?\d{4})\s*[–—-]\s*((?:\d{1,2}/)?\d{4}|heute|jetzt|aktuell)(?![\d])", re.IGNORECASE)
HEADING = re.compile(r"^(#{1,2})\s+(.+?)\s*#*\s*$")
RATING_SYMBOLS = re.compile(r"[★☆●○◐◑■□▪▫▰▱█▓▒░]{3,}")
LIGATURES = "ﬀﬁﬂﬃﬄﬅﬆ"
STANDARD_FONT = re.compile(r"^(?:[A-Z]{6}\+)?(?:Helvetica|Times|Courier|Symbol|ZapfDingbats)", re.IGNORECASE)
MIN_WORDS = 30
STATION_WINDOW = 3  # lines before and after the period line in which position and employer must stand
SECTION_SHARE = 0.8  # share of the words of a section that must stand between its heading and the next one
GUTTER = 24.0  # points of free space that make a gap between two words a column gap
FORMATS = ("pdf", "docx", "html")  # md and tex are copies of the source: they say nothing about a parser


def stumpf(value):
    """Without spaces, line breaks and hyphens, in lower case: a break inside a word does not matter."""
    return re.sub(r"[\s\-‐‑–]", "", value).casefold()


def flat(value):
    return re.sub(r"\s+", " ", re.sub(r"[*_`#\[\]]", "", value)).strip().casefold()


def no_links(text):
    return re.sub(r"\]\([^)\s]*\)", "]", text)


def periods(text):
    return [f"{a}–{b.casefold()}" for a, b in PERIOD.findall(no_links(text))]


def phone_numbers(text):
    """The phone numbers of a text as normalised digit strings. A period or a pair of years is not a number."""
    found = set()
    for number in PHONE.findall(text.replace("\n", " ")):
        if re.search(r"\d{1,2}/\d{4}", number):
            continue
        digits = re.sub(r"\D", "", number)
        digits = "0" + digits[4:] if digits.startswith("0049") else "0" + digits[2:] if digits.startswith("49") else digits
        if not re.fullmatch(r"(?:19|20)\d{2}(?:19|20)\d{2}", digits):
            found.add(digits)
    return found


def note(check_id, severity, text):
    return (check_id, severity, text)


# ---------------------------------------------------------------- the file (ATS-01)

def pdf_file(path):
    """-> (findings, gaps). Structure, encryption and fonts of a PDF."""
    findings, gaps = [], []
    with open(path, "rb") as handle:
        head = handle.read(1024)
        handle.seek(0, os.SEEK_END)
        handle.seek(max(0, handle.tell() - 1024))
        tail = handle.read()
    if b"%PDF-" not in head or b"%%EOF" not in tail:
        return [note("ATS-01", "Blocker", "Keine gültige PDF-Struktur (Kopf oder Dateiende fehlt): ein Parser kann die Datei nicht öffnen")], gaps
    if not shutil.which("pdfinfo"):
        gaps.append("pdfinfo (poppler-utils) fehlt: die PDF-Struktur ist nicht prüfbar")
    else:
        try:
            info = subprocess.run(["pdfinfo", path], capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            info = None
        if info is None or info.returncode != 0:
            findings.append(note("ATS-01", "Blocker", "pdfinfo kann das PDF nicht lesen: die Datei ist beschädigt oder nicht lesbar"))
        elif re.search(rb"^Encrypted:\s+yes.*copy:no", info.stdout, re.M):
            findings.append(note("ATS-01", "Blocker", "Das PDF verbietet das Kopieren von Text: ein Parser darf den Text nicht auslesen"))
    if not shutil.which("pdffonts"):
        return findings, gaps + ["pdffonts (poppler-utils) fehlt: die Schriften sind nicht prüfbar"]
    try:
        fonts = subprocess.run(["pdffonts", path], capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return findings, gaps + ["pdffonts konnte nicht ausgeführt werden"]
    type3 = loose = 0
    for line in fonts.stdout.decode("utf-8", "replace").splitlines()[2:]:
        row = re.match(r"^(\S+)\s+(.+?)\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
        if not row:
            continue
        type3 += row.group(2) == "Type 3"
        loose += row.group(3) == "no" and not STANDARD_FONT.match(row.group(1))
    if type3:
        findings.append(note("ATS-01", "Warnung", f"{type3} Schrift(en) vom Typ 3 (Bitmap oder Zeichnung): ihr Text lässt sich oft nicht zuverlässig auslesen"))
    if loose:
        findings.append(note("ATS-01", "Warnung", f"{loose} Schrift(en) nicht eingebettet: Darstellung und Textabbildung hängen vom Rechner des Empfängers ab"))
    return findings, gaps


def w_text(xml):
    return html.unescape("".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", xml, re.S)))


def docx_parts(path):
    """-> (document.xml text or None, text of headers and footers, findings)."""
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                return None, "", [note("ATS-01", "Blocker", "Das DOCX-Archiv ist beschädigt")]
            names = archive.namelist()
            if "word/document.xml" not in names or "[Content_Types].xml" not in names:
                return None, "", [note("ATS-01", "Blocker", "Keine gültige DOCX-Struktur (document.xml oder Content-Types fehlt)")]
            xml = archive.read("word/document.xml").decode("utf-8", "replace")
            header = " ".join(w_text(archive.read(n).decode("utf-8", "replace")) for n in names if re.match(r"word/(?:header|footer)\d*\.xml$", n))
    except (OSError, zipfile.BadZipFile) as error:
        return None, "", [note("ATS-01", "Blocker", f"Das DOCX lässt sich nicht öffnen ({error.__class__.__name__})")]
    try:
        ET.fromstring(xml)
    except ET.ParseError:
        return None, "", [note("ATS-01", "Blocker", "document.xml ist kein gültiges XML: Word und Parser lesen die Datei nicht")]
    findings = []
    hidden = len(re.findall(r'<w:vanish\s*/>|<w:vanish w:val="(?:1|true|on)"', xml))
    white = len(re.findall(r'<w:color w:val="FFFFFF"', xml, re.IGNORECASE))
    tiny = len([s for s in re.findall(r'<w:sz w:val="(\d+)"', xml) if int(s) <= 4])
    if hidden or white or tiny:
        findings.append(note("ATS-01", "Blocker", f"Versteckter Text ({hidden} ausgeblendet, {white} weiß, {tiny} winzig): ein ATS liest ihn, die Leserin nicht"))
    return xml, header, findings


# ---------------------------------------------------------------- text (EX-03)

def text_quality(text, fmt):
    findings = []
    if fmt in ("pdf", "docx") and len(text.split()) < MIN_WORDS:
        findings.append(note("EX-03", "Blocker", "Aus dem Export lässt sich kaum Text lesen (Bild statt Text?): ein ATS sieht ihn leer"))
    if "�" in text or "(cid:" in text:
        findings.append(note("EX-03", "Blocker", "Der extrahierte Text enthält Ersatzzeichen oder Glyphen-Nummern: die Schrift hat keine Textabbildung"))
    if any(char in text for char in LIGATURES):
        findings.append(note("EX-03", "Warnung", "Ligatur-Zeichen (zum Beispiel „ﬁ“) im extrahierten Text: eine Stichwortsuche nach dem Wort findet es nicht"))
    if re.search(r"(?<!\S)(?:\w ){7,}\w(?!\S)", text):
        findings.append(note("EX-03", "Warnung", "Wörter stehen als einzelne Buchstaben im Text (Sperrung): Stichwörter werden nicht erkannt"))
    return findings


# ---------------------------------------------------------------- sections and order (ATS-02)

def source_sections(body):
    """-> [(heading, set of the words of its content)] for the headings of level 1 and 2."""
    sections, current = [], None
    for line in body.splitlines():
        match = HEADING.match(line)
        if match:
            current = (match.group(2), [])
            sections.append(current)
        elif current is not None:
            current[1].append(line)
    return [(heading, set(re.findall(r"[\wÄÖÜäöüß]{4,}", flat(no_links("\n".join(lines)))))) for heading, lines in sections]


def section_notes(body, text, fmt):
    if fmt not in ("pdf", "docx"):
        return []
    findings = []
    lines = text.splitlines()
    flat_lines = [flat(line) for line in lines]
    sections = source_sections(body)
    positions, start = [], 0
    for heading, _ in sections:
        index = next((i for i in range(start, len(lines)) if flat_lines[i] == flat(heading)), None)
        positions.append(index)
        if index is None:
            findings.append(note("ATS-02", "Warnung", f"Überschrift „{heading[:40]}“ steht nicht als eigene Zeile im extrahierten Text: ein Parser erkennt den Abschnitt nicht sicher"))
        else:
            start = index + 1
    for number, (heading, words) in enumerate(sections):
        if positions[number] is None or len(words) < 3:
            continue
        end = next((p for p in positions[number + 1:] if p is not None), len(lines))
        segment = flat(" ".join(lines[positions[number] + 1:end]))
        found = sum(1 for word in words if word in segment)
        if found < SECTION_SHARE * len(words):
            findings.append(note("ATS-02", "Warnung", f"Der Inhalt des Abschnitts „{heading[:40]}“ steht nicht unter seiner Überschrift ({found} von {len(words)} Wörtern)"))
    return findings


def docx_heading_notes(xml, body):
    expected = Counter(len(m.group(1)) for m in (HEADING.match(line) for line in body.splitlines()) if m)
    found = Counter(int(level) for level in re.findall(r'<w:pStyle w:val="(?:Heading|berschrift|Überschrift)(\d)"', xml))
    found = Counter({level: count for level, count in found.items() if level <= 2})
    if found == expected:
        return []
    show = lambda counter: ", ".join(f"H{level}×{count}" for level, count in sorted(counter.items())) or "keine"
    return [note("ATS-02", "Warnung", f"Überschriften-Formatvorlagen weichen von der Quelle ab: Quelle {show(expected)}, DOCX {show(found)}: ein Parser erkennt Abschnitte an der Formatvorlage")]


# ---------------------------------------------------------------- stations and periods (ATS-03)

def station_notes(body, text):
    findings = []
    source, exported = periods(body), periods(text)
    missing, extra = Counter(source) - Counter(exported), Counter(exported) - Counter(source)
    if missing:
        findings.append(note("ATS-03", "Blocker", f"{sum(missing.values())} Zeitraum/Zeiträume der Quelle stehen nicht (mehr) als Zeitraum im extrahierten Text, zum Beispiel {next(iter(missing))}"))
    elif source != exported and not extra:
        findings.append(note("ATS-03", "Blocker", "Die Zeiträume stehen im extrahierten Text in einer anderen Reihenfolge als in der Quelle"))
    if extra:
        findings.append(note("ATS-03", "Warnung", f"{sum(extra.values())} zusätzliche(r) Zeitraum/Zeiträume im extrahierten Text, die in der Quelle nicht stehen"))
    if len({bool(re.match(r"\d{1,2}/", a)) for a, _ in PERIOD.findall(no_links(body))}) > 1:
        findings.append(note("ATS-03", "Warnung", "Uneinheitliche Datumsformate in der Quelle (MM/JJJJ und nur JJJJ): ein Parser rechnet Zeiträume unterschiedlich"))
    if missing:
        return findings
    lines = text.splitlines()
    for station in cv.cv_stations(body.splitlines()):
        if not station["strict"] or station["gap"]:
            continue
        marker, position, employer = station["start_raw"], stumpf(station["position"]), stumpf(station["employer"])
        at = [i for i, line in enumerate(lines) if marker in line]
        windows = [stumpf(" ".join(lines[max(0, i - STATION_WINDOW):i + STATION_WINDOW + 1])) for i in at]
        if windows and not any(position in w and employer in w for w in windows):
            findings.append(note("ATS-03", "Warnung", f"Zeitraum {marker}: Position und Arbeitgeber stehen im extrahierten Text nicht in der Nähe des Zeitraums: ein Parser ordnet sie sonst falsch zu"))
    return findings


# ---------------------------------------------------------------- contact data (ATS-04)

def contact_notes(body, text, doc_type, header_text):
    findings = []
    own, own_header = re.sub(r"[\s-]", "", text), re.sub(r"[\s-]", "", header_text)
    emails = EMAIL.findall(body)
    for mail in emails:
        wanted = re.sub(r"[\s-]", "", mail)
        if wanted not in own:
            where = " (er steht nur in der Kopf- oder Fußzeile)" if wanted in own_header else ""
            findings.append(note("ATS-04", "Blocker", f"Eine E-Mail-Adresse der Quelle steht nicht im extrahierten Text{where}"))
    in_text, in_header = phone_numbers(text), phone_numbers(header_text)
    for number in phone_numbers(body):
        if number not in in_text:
            where = " (sie steht nur in der Kopf- oder Fußzeile)" if number in in_header else ""
            findings.append(note("ATS-04", "Blocker", f"Eine Telefonnummer der Quelle steht nicht im extrahierten Text{where}"))
    if doc_type == "cv" and not emails:
        findings.append(note("ATS-04", "Warnung", "Der Lebenslauf enthält keine E-Mail-Adresse: ein ATS legt die Person ohne Kontakt an"))
    return findings


# ---------------------------------------------------------------- layout risks (ATS-05)

def pdf_layout(path):
    """-> (findings, gaps). Images, text outside the page and columns of a PDF."""
    findings, gaps = [], []
    if not shutil.which("pdfimages"):
        gaps.append("pdfimages (poppler-utils) fehlt: Bilder im PDF sind nicht prüfbar")
    else:
        try:
            images = subprocess.run(["pdfimages", "-list", path], capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            images = None
        if images is None or images.returncode != 0:
            gaps.append("pdfimages konnte das PDF nicht lesen")
        else:
            count = len([line for line in images.stdout.decode("utf-8", "replace").splitlines()[2:] if re.match(r"^\s*\d+\s+\d+\s+image\b", line)])
            if count:
                findings.append(note("ATS-05", "Warnung", f"{count} Bild(er) im PDF: der Inhalt eines Bildes ist für ein ATS nicht lesbar"))
    try:
        box = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        box = None
    if box is None or box.returncode != 0:
        return findings, gaps + ["pdftotext -bbox konnte das PDF nicht lesen: Spalten und Seitenränder sind nicht prüfbar"]
    pages = []
    for block in box.stdout.decode("utf-8", "replace").split("<page ")[1:]:
        size = re.match(r'width="([\d.]+)" height="([\d.]+)"', block)
        words = [tuple(float(v) for v in m) for m in re.findall(r'<word xMin="([\d.-]+)" yMin="([\d.-]+)" xMax="([\d.-]+)" yMax="([\d.-]+)"', block)]
        if size:
            pages.append((float(size.group(1)), float(size.group(2)), words))
    cut = sum(1 for width, height, words in pages for x0, y0, x1, y1 in words if x0 < -1 or y0 < -1 or x1 > width + 1 or y1 > height + 1)
    if cut:
        findings.append(note("ATS-05", "Warnung", f"{cut} Wort/Wörter liegen außerhalb der Seite (abgeschnitten): der Inhalt ist nicht vollständig sichtbar"))
    if any(has_columns(width, words) for width, _, words in pages):
        findings.append(note("ATS-05", "Warnung", "Mehrspaltige Anordnung: die Lesereihenfolge hängt vom Parser ab (Wortlaut und Reihenfolge des Exports prüft EX-02)"))
    return findings, gaps


def has_columns(width, words):
    """A gap between two words that lies at the same place in many lines and near the middle of the page."""
    lines = {}
    for x0, y0, x1, _ in words:
        lines.setdefault(round(y0 / 3), []).append((x0, x1))
    centers = []
    for row in lines.values():
        row.sort()
        centers += [(a1 + b0) / 2 for (_, a1), (b0, _) in zip(row, row[1:]) if b0 - a1 >= GUTTER and 0.25 * width <= (a1 + b0) / 2 <= 0.75 * width]
    if len(lines) < 8 or not centers:
        return False
    centers.sort()
    best, run = 0, [centers[0]]
    for value in centers[1:]:
        run = run + [value] if value - run[0] <= 12 else [value]
        best = max(best, len(run))
    return best >= 6 and best >= 0.4 * len(lines)


def layout_notes(fmt, xml, header_text, structure, body):
    findings = []
    if structure["tabellen"]:
        findings.append(note("ATS-05", "Warnung", f"{structure['tabellen']} Tabelle(n): manche ATS lesen Tabellen spaltenweise falsch"))
    if structure["bilder"] and fmt != "pdf":
        findings.append(note("ATS-05", "Warnung", f"{structure['bilder']} Bild(er): der Inhalt eines Bildes ist für ein ATS nicht lesbar"))
    if fmt == "docx" and xml is not None:
        if "txbxContent" in xml:
            findings.append(note("ATS-05", "Warnung", "Textfeld im Dokument: sein Text kann von einem Parser übersprungen werden"))
        if re.search(r'<w:cols w:num="[2-9]"', xml):
            findings.append(note("ATS-05", "Warnung", "Mehrspaltiger Abschnitt im DOCX: die Lesereihenfolge hängt vom Parser ab"))
        if header_text.strip():
            findings.append(note("ATS-05", "Warnung", "Text in Kopf- oder Fußzeile: nicht jeder Parser liest ihn"))
    if RATING_SYMBOLS.search(body):
        findings.append(note("ATS-05", "Prüfung", "Eine Bewertung steht als Symbolreihe (Sterne, Punkte, Balken): das Niveau fehlt als Text. Als Wort ergänzen (zum Beispiel „sehr gut“), nicht automatisch"))
    return findings


# ---------------------------------------------------------------- entry point

def check_file(path, fmt, doc_type, body, text, structure):
    """-> (findings [(check id, severity, text)], gaps {check id: [reason]}). For pdf, docx and html."""
    findings, gaps = text_quality(text, fmt), {"ATS-01": [], "ATS-05": []}
    xml, header = None, ""
    if fmt == "pdf":
        for found, missing, check_id in ((*pdf_file(path), "ATS-01"), (*pdf_layout(path), "ATS-05")):
            findings += found
            gaps[check_id] += missing
    elif fmt == "docx":
        xml, header, found = docx_parts(path)
        findings += found
        if xml is not None:
            findings += docx_heading_notes(xml, body)
    findings += section_notes(body, text, fmt) + station_notes(body, text) + contact_notes(body, text, doc_type, header)
    findings += layout_notes(fmt, xml, header, structure, body)
    return findings, {key: value for key, value in gaps.items() if value}


# ---------------------------------------------------------------- key terms of the posting (KW-01)

def analysis_rows(analysis):
    """-> [{column: cell}] of the requirement table of analyse.md."""
    columns, rows = None, []
    for line in analysis.splitlines():
        if not line.lstrip().startswith("|"):
            columns = None if not line.strip() else columns
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if columns is None:
            if "Priorität" in cells and "Status" in cells:
                columns = {name: i for i, name in enumerate(cells)}
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        rows.append(dict(zip(columns, cells + [""] * (len(columns) - len(cells)))))
    return rows


def term_in(term, text):
    """All words of the term of four letters or more stand in the text, compared by their first five letters."""
    words = [w for w in re.findall(r"[\wÄÖÜäöüß]+", term.casefold()) if len(w) >= 4]
    return bool(words) and all(w[:5] in text for w in words)


def key_terms(analysis, cv_source):
    """Coverage of the competences of the analysis in the Lebenslauf, never a change of it.

    A term the analysis shows as evidenced but the Lebenslauf does not name is a note (a parser looks for the word). A
    term the analysis does not evidence (`nicht belegt`, `unklar`) that stands in the Lebenslauf is a review: a word of
    the posting must not become a qualification of the applicant. Nothing is inserted."""
    findings, text = [], flat(no_links(cv_source))
    for row in analysis_rows(analysis):
        status = row.get("Status", "")
        for term in re.split(r"\s*[/,;]\s*", row.get("Kompetenz", "")):
            if not term or term in cv.EMPTY:
                continue
            present = term_in(term, text)
            if status == "erfüllt" and "Lebenslauf" in row.get("Verwendung", "") and not present:
                findings.append(note("KW-01", "Warnung", f"Belegte Kompetenz „{term[:40]}“ steht im Lebenslauf nicht als Begriff: ein Stichwortabgleich findet sie nicht (nur ergänzen, wenn es den Beleg richtig benennt)"))
            elif status in ("nicht belegt", "unklar") and present:
                findings.append(note("KW-01", "Prüfung", f"Der Begriff „{term[:40]}“ steht im Lebenslauf, die Analyse belegt ihn aber nicht ({status}): ein Begriff der Anzeige ist keine Qualifikation"))
    return findings
