#!/usr/bin/env python3
"""Deterministic checks for a generated Lebenslauf and its posting analysis.

Implements the automated rules of spec/job-application/cv-generierung/en.md (CG-13):

  CV-01 placeholder left in the document                          Blocker
  CV-02 station header not in R-2.1 form, or source month missing Warnung
  CV-03 more than 5 bullets in a station / station without bullets Warnung / Hinweis
  CV-04 stations not in reverse chronological order (Warnung);
        end before start (Blocker)
  CV-05 number in a bullet not found in the Grundlage             Blocker
  CV-06 station period differs from the Grundlage                 Blocker
  CV-07 Muss row marked erfüllt without evidence (analysis)       Blocker
  CV-08 table in the Lebenslauf (Blocker with --ats)              Warnung
  CV-09 duplicate bullet                                          Hinweis
  CV-10 heading outside the standard headings (CG-11.2a)          Warnung
  CV-11 generic phrase that hides the task (CG-7.3)               Hinweis
  CV-12 bullet longer than two lines (about 180 characters)       Hinweis
  CV-13 employment gap over two months without a gap entry        Blocker
  CV-14 analysis status vocabulary or evidence strength invalid   Warnung
  CV-15 station not found in the Grundlage                        Blocker
        (Warnung when the Grundlage has no station records)
  CV-16 leadership wording without leadership in the station note Blocker

Grundlage station records come from two forms (CG-2.4):
  - R-2.1 header lines `### MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort` in any note;
  - station notes with frontmatter `typ: station`, `titel`, `arbeitgeber`, `zeitraum_von`,
    `zeitraum_bis` (YYYY, YYYY-MM or MM/JJJJ, or `heute`), and `fuehrung` (ja, nein, ungeklärt).

Usage:
  cv_checks.py lebenslauf.md [--grundlage PFAD ...] [--analyse analyse.md] [--ats]

Prints a JSON report to stdout. Exits 1 when at least one Blocker is found, otherwise 0.
Standard library only. The script reads only the files it is given.
"""

import argparse
import json
import os
import re
import sys

RULE_VERSION = "cv-generierung/en.md CG-13"

CV_HEADER = re.compile(r"^### (\d{2}/\d{4}) – (\d{2}/\d{4}|heute) \| ([^|]+?) \| (.+?)\s*$")
GRUNDLAGE_HEADER = re.compile(r"^### (\S+) – (\S+) \| ([^|]+?) \| (.+?)\s*$")
HEADER_ANY = re.compile(r"^### ")
PLACEHOLDER = re.compile(r"\[(ERGÄNZEN|KLÄREN)")
NUMBER = re.compile(r"(?<![\d.,])\d+(?:[.,]\d+)?(?![\d])")
GENERIC = re.compile(
    r"verantwortlich für|zuständig für|involved in|worked on|erfolgreich|innovativ|dynamisch|"
    r"vielfältig|\bdiverse\b|Expertise in|sicher in",
    re.IGNORECASE,
)
LEADERSHIP = re.compile(
    r"\b(?:geleitet|leitete|leiten|Teamleitung|Teamleiter|Teamlead|Führung|geführt|führte|führen|"
    r"Personalverantwortung|Mitarbeiterführung|Vorgesetzte|disziplinarisch|verantwortete das Team)\b",
    re.IGNORECASE,
)
GAP_ENTRY = re.compile(r"Auszeit|Lücke|Elternzeit|Pflegezeit|ERGÄNZEN: Grund der Lücke")
STANDARD_HEADINGS = (
    "Persönliche Daten", "Kurzprofil", "Berufserfahrung", "Relevante Projekte", "Praktika",
    "Ausbildung und Studium", "Schulbildung", "Sprachkenntnisse", "IT- und Fachkenntnisse",
    "Weiterbildung und Zertifikate", "Ehrenamt", "Interessen", "Lebenslauf",
)
ANALYSIS_STATUS = ("erfüllt", "teilweise", "nicht belegt", "unklar")
ANALYSIS_STRENGTH = ("stark", "mittel", "schwach", "—")
MAX_BULLETS = 5
MAX_BULLET_CHARS = 180
GAP_LIMIT_MONTHS = 2
EMPTY = ("", "—", "-")


def finding(rule, severity, file, line, text):
    return {"regel": rule, "schweregrad": severity, "datei": file, "zeile": line, "befund": text}


def parse_period(value):
    """'MM/JJJJ', 'JJJJ-MM', 'JJJJ' -> (year, month or None); 'heute' -> 'heute'; else None."""
    value = value.strip()
    if value == "heute":
        return "heute"
    match = re.fullmatch(r"(\d{2})/(\d{4})", value)
    if match:
        return int(match.group(2)), int(match.group(1))
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = re.fullmatch(r"(\d{4})", value)
    if match:
        return int(match.group(1)), None
    return None


def month_index(period, default_month):
    """Absolute month number for a parsed period; a missing month is replaced by default_month."""
    if period in (None, "heute"):
        return None
    year, month = period
    return year * 12 + (month or default_month) - 1


def read_note(path):
    """Return (frontmatter dict, body text) of a Markdown note."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    meta = {}
    if match:
        for line in match.group(1).splitlines():
            pair = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
            if pair:
                meta[pair.group(1)] = pair.group(2).strip("\"'")
        text = text[match.end():]
    return meta, text


def key_of(position, employer):
    return position.strip().lower(), employer.split(",")[0].strip().lower()


def cv_stations(lines):
    """Stations of a Lebenslauf with strict R-2.1 headers (MM/JJJJ)."""
    stations = []
    for number, line in enumerate(lines, 1):
        match = CV_HEADER.match(line)
        if match:
            start, end, position, employer = match.groups()
            stations.append({
                "line": number,
                "start": parse_period(start),
                "end": parse_period(end),
                "start_raw": start,
                "end_raw": end,
                "position": position.strip(),
                "employer": employer.split(",")[0].strip(),
            })
    return stations


def grundlage_records(path):
    """Station records of one Grundlage note or of every note below a directory."""
    paths = []
    if os.path.isdir(path):
        for root, dirs, names in os.walk(path):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            paths += [os.path.join(root, n) for n in sorted(names) if n.endswith(".md") and not n.startswith(".")]
    else:
        paths = [path]
    records = []
    for note in paths:
        meta, body = read_note(note)
        if meta.get("typ") == "station":
            records.append({
                "file": note,
                "line": 0,
                "start": parse_period(meta.get("zeitraum_von", "")),
                "end": parse_period(meta.get("zeitraum_bis", "")),
                "start_raw": meta.get("zeitraum_von", ""),
                "end_raw": meta.get("zeitraum_bis", ""),
                "position": meta.get("titel", ""),
                "employer": meta.get("arbeitgeber", ""),
                "fuehrung": meta.get("fuehrung", "ungeklärt"),
                "team_groesse": meta.get("team_groesse", ""),
            })
        for number, line in enumerate(body.splitlines(), 1):
            match = GRUNDLAGE_HEADER.match(line)
            if match and not meta.get("typ") == "station":
                start, end, position, employer = match.groups()
                records.append({
                    "file": note,
                    "line": number,
                    "start": parse_period(start),
                    "end": parse_period(end),
                    "start_raw": start,
                    "end_raw": end,
                    "position": position.strip(),
                    "employer": employer.split(",")[0].strip(),
                    "fuehrung": "ungeklärt",
                    "team_groesse": "",
                })
    return records


def read_sources(paths):
    """Concatenate the text of all Markdown notes below the given files or directories."""
    texts = []
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, names in os.walk(path):
                dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                for name in sorted(names):
                    if name.endswith(".md") and not name.startswith("."):
                        with open(os.path.join(root, name), encoding="utf-8") as handle:
                            texts.append(handle.read())
        else:
            with open(path, encoding="utf-8") as handle:
                texts.append(handle.read())
    return "\n".join(texts)


def check_period(cv, source, file):
    """Compare a CV station with its source record (CV-06, CV-02)."""
    findings = []
    label = f"{cv['start_raw']} – {cv['end_raw']}"
    source_label = f"{source['start_raw']} – {source['end_raw']}"
    cv_end = cv["end"]
    src_end = source["end"]
    if cv_end == "heute" or src_end == "heute":
        if cv_end != src_end:
            findings.append(finding("CV-06", "Blocker", file, cv["line"], f"Zeitraum weicht von der Grundlage ab: {label} statt {source_label}"))
        return findings
    cv_start, src_start = cv["start"], source["start"]
    months_known = all(p and p[1] for p in (cv_start, cv_end, src_start, src_end))
    if not months_known:
        year_pairs = [(cv_start, src_start), (cv_end, src_end)]
        if any(c and s and c[0] != s[0] for c, s in year_pairs):
            findings.append(finding("CV-06", "Blocker", file, cv["line"], f"Jahr weicht von der Grundlage ab: {label} statt {source_label}"))
        else:
            findings.append(finding("CV-02", "Warnung", file, cv["line"], f"Grundlage ohne Monat ({source_label}); Zeitraum nur auf Jahresebene geprüft"))
        return findings
    if (cv_start, cv_end) != (src_start, src_end):
        findings.append(finding("CV-06", "Blocker", file, cv["line"], f"Zeitraum weicht von der Grundlage ab: {label} statt {source_label}"))
    return findings


def check_cv(text, file, source_text=None, sources=None, ats=False):
    """Run the Lebenslauf rules. `source_text` and `sources` (station records) come from the Grundlage."""
    lines = text.splitlines()
    findings = []
    section = None
    current = None
    bullets = {}
    seen_bullets = {}
    gap_lines = []
    for number, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = line[3:].strip()
            if not section.startswith(STANDARD_HEADINGS):
                findings.append(finding("CV-10", "Warnung", file, number, f"Überschrift nicht im Standardkatalog: „{section}“"))
        if PLACEHOLDER.search(line):
            findings.append(finding("CV-01", "Blocker", file, number, "offener Platzhalter: " + line.strip()))
        if line.lstrip().startswith("|"):
            findings.append(finding("CV-08", "Blocker" if ats else "Warnung", file, number, "Tabelle im Lebenslauf (R-8.3)"))
        if section and section.startswith("Berufserfahrung") and GAP_ENTRY.search(line):
            gap_lines.append(number)
        if section and section.startswith("Berufserfahrung") and HEADER_ANY.match(line):
            if CV_HEADER.match(line):
                current = number
                bullets[current] = []
            else:
                current = None
                findings.append(finding("CV-02", "Warnung", file, number, "Kopfzeile nicht in Form Zeitraum | Position | Arbeitgeber, Ort (R-2.1): " + line.strip()))
        elif line.startswith("## "):
            current = None
        if line.startswith("- ") and current is not None:
            bullets[current].append((number, line[2:].strip()))

    stations = cv_stations(lines)
    if stations:
        starts = [s["start"] for s in stations]
        if any(later > earlier for earlier, later in zip(starts, starts[1:])):
            findings.append(finding("CV-04", "Warnung", file, stations[0]["line"], "Stationen nicht in umgekehrt chronologischer Reihenfolge (R-2)"))
    for s in stations:
        if isinstance(s["end"], tuple) and s["start"] and s["end"][0] * 12 + (s["end"][1] - 1) < s["start"][0] * 12 + (s["start"][1] - 1):
            findings.append(finding("CV-04", "Blocker", file, s["line"], f"Ende vor Beginn: {s['start_raw']} – {s['end_raw']}"))

    for station_line, items in bullets.items():
        if len(items) > MAX_BULLETS:
            findings.append(finding("CV-03", "Warnung", file, station_line, f"{len(items)} Stichpunkte, Obergrenze {MAX_BULLETS} (CG-6)"))
        if not items:
            findings.append(finding("CV-03", "Hinweis", file, station_line, "Station ohne Stichpunkte: „nur Kopfzeile“ bewusst entscheiden (CG-6.5)"))

    by_key = {}
    if sources is not None:
        for record in sources:
            by_key.setdefault(key_of(record["position"], record["employer"]), record)
        if not sources:
            findings.append(finding("CV-15", "Warnung", file, 0, "Grundlage hat keine Stationen; Abgleich nicht möglich"))
        for s in stations:
            record = by_key.get(key_of(s["position"], s["employer"]))
            if record is None:
                if sources:
                    findings.append(finding("CV-15", "Blocker", file, s["line"], f"Station nicht in der Grundlage: {s['position']} | {s['employer']}"))
                continue
            findings += check_period(s, record, file)
            s["record"] = record

    station_of_line = {s["line"]: s for s in stations}
    for station_line, items in bullets.items():
        for number, bullet in items:
            key = re.sub(r"\s+", " ", bullet.lower())
            if key in seen_bullets:
                findings.append(finding("CV-09", "Hinweis", file, number, f"doppelter Stichpunkt (zuerst Zeile {seen_bullets[key]})"))
            else:
                seen_bullets[key] = number
            if GENERIC.search(bullet):
                findings.append(finding("CV-11", "Hinweis", file, number, "allgemeine Formulierung: " + bullet))
            if len(bullet) > MAX_BULLET_CHARS:
                findings.append(finding("CV-12", "Hinweis", file, number, f"Stichpunkt länger als zwei Zeilen ({len(bullet)} Zeichen)"))
            if source_text is not None:
                for token in NUMBER.findall(bullet):
                    if not re.search(rf"(?<![\d.,]){re.escape(token)}(?![\d])", source_text):
                        findings.append(finding("CV-05", "Blocker", file, number, f"Zahl „{token}“ nicht in der Grundlage belegt: " + bullet))
            station = station_of_line.get(station_line)
            record = station.get("record") if station else None
            if record is not None and record.get("fuehrung") != "ja" and LEADERSHIP.search(bullet):
                findings.append(finding("CV-16", "Blocker", file, number, f"Führungsbegriff ohne belegte Führungsverantwortung (fuehrung: {record.get('fuehrung')}): " + bullet))

    if stations:
        ordered = sorted(stations, key=lambda s: -month_index(s["start"], 1))
        for older, newer in zip(ordered[1:], ordered):
            end_index = month_index(older["end"], 12)
            if end_index is None:
                continue
            gap = month_index(newer["start"], 1) - end_index - 1
            if gap > GAP_LIMIT_MONTHS and not gap_lines:
                findings.append(finding("CV-13", "Blocker", file, newer["line"], f"Lücke von {gap} Monaten ohne Eintrag (CG-9)"))
    return findings


def check_analysis(text, file):
    """Run the rules for analyse.md (CG-4): Muss evidence and status vocabulary."""
    findings = []
    columns = None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            columns = None if line.strip() == "" else columns
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if columns is None:
            if "Priorität" in cells and "Status" in cells:
                columns = {name: idx for idx, name in enumerate(cells)}
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        row = dict(zip(columns, cells + [""] * (len(columns) - len(cells))))
        status = row.get("Status", "")
        priority = row.get("Priorität", "")
        evidence = row.get("Nachweis", "")
        strength = row.get("Stärke", "")
        if status == "fehlt":
            findings.append(finding("CV-14", "Warnung", file, number, "Status „fehlt“ ist durch „nicht belegt“ zu ersetzen (CG-4.3)"))
        elif status not in ANALYSIS_STATUS:
            findings.append(finding("CV-14", "Warnung", file, number, f"unbekannter Status „{status}“"))
        if strength and strength not in ANALYSIS_STRENGTH:
            findings.append(finding("CV-14", "Warnung", file, number, f"unbekannte Stärke „{strength}“"))
        if priority == "Muss" and status == "erfüllt":
            if evidence in EMPTY:
                findings.append(finding("CV-07", "Blocker", file, number, "Muss-Anforderung als erfüllt markiert ohne Nachweis: " + row.get("Anforderung", "")))
            if strength in ("schwach", "—", ""):
                findings.append(finding("CV-14", "Warnung", file, number, "erfüllt setzt Stärke mittel oder stark voraus (CG-4.1)"))
        if priority == "Muss" and status in ("nicht belegt", "teilweise"):
            findings.append(finding("CV-07", "Warnung", file, number, f"Muss-Lücke ({status}), Verwendung prüfen: " + row.get("Anforderung", "")))
    return findings


def load_records(paths):
    records = []
    for path in paths:
        records += grundlage_records(path)
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deterministic checks for a Lebenslauf (CG-13).")
    parser.add_argument("lebenslauf", help="path to lebenslauf.md")
    parser.add_argument("--grundlage", action="append", default=[], help="Grundlage file or directory (repeatable)")
    parser.add_argument("--analyse", help="path to analyse.md")
    parser.add_argument("--ats", action="store_true", help="treat tables as Blocker (posting requires ATS)")
    args = parser.parse_args(argv)

    with open(args.lebenslauf, encoding="utf-8") as handle:
        text = handle.read()
    source_text = read_sources(args.grundlage) if args.grundlage else None
    sources = load_records(args.grundlage) if args.grundlage else None

    findings = check_cv(text, args.lebenslauf, source_text, sources, ats=args.ats)
    if args.analyse:
        with open(args.analyse, encoding="utf-8") as handle:
            findings += check_analysis(handle.read(), args.analyse)

    summary = {level: sum(1 for f in findings if f["schweregrad"] == level) for level in ("Blocker", "Warnung", "Hinweis")}
    report = {
        "regeln": RULE_VERSION,
        "abgleich": "mit Grundlage" if args.grundlage else "ohne Grundlage (CV-05, CV-06, CV-15, CV-16 nicht geprüft)",
        "grundlage_stationen": len(sources) if sources is not None else None,
        "zusammenfassung": summary,
        "befunde": findings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if summary["Blocker"] else 0


if __name__ == "__main__":
    sys.exit(main())
