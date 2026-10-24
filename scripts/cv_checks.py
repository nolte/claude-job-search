#!/usr/bin/env python3
"""Deterministic checks for a generated Lebenslauf and its posting analysis.

Implements the automated rules of spec/job-application/cv-generierung/en.md (CG-13):

  CV-01 placeholder left in the document                          Blocker
  CV-02 station header not in R-2.1 form, or a month missing      Warnung
  CV-03 more than 5 bullets in a station / station without bullets Warnung / Hinweis
  CV-04 stations not in reverse chronological order (Warnung);
        end before start (Blocker)
  CV-05 number in a bullet not found in the station record        Blocker when the number is
        nowhere in the Grundlage; Hinweis when it is in another entry of the Grundlage;
        Warnung when the station holds the number with another unit or noun
  CV-06 station period differs from the Grundlage                 Blocker
  CV-07 Muss row marked erfüllt without evidence (analysis)       Blocker
  CV-08 table in the Lebenslauf (Blocker with --ats)              Warnung
  CV-09 duplicate bullet                                          Hinweis
  CV-10 heading outside the standard headings (CG-11.2a)          Warnung
  CV-11 generic or evaluative phrase (CG-7.3, CG-8.2.3)           Warnung
  CV-12 bullet longer than two lines (about 180 characters)       Hinweis
  CV-13 employment gap over two months without a gap entry        Blocker
        between the two stations
  CV-14 analysis status vocabulary or evidence strength invalid   Warnung
  CV-15 station not found in the Grundlage                        Blocker
        (Warnung when the Grundlage has no station records)
  CV-16 personnel-leadership wording without `fuehrung: ja`        Blocker
        (`nein`, `ungeklärt` or missing; CG-13.4.3)
  CV-17 sub-bullets below a bullet (not part of R-2.1)            Hinweis
  CV-18 birthdate of a person in analyse.md or a firm file (RC-5.3 rule 5,
        RC-11 rule 4)                                             Warnung
  CV-19 entry of a list section (skills, languages, certificates, education)
        that stands nowhere in the Grundlage; a number in its qualifier
        that stands nowhere                                       Blocker
  CV-20 station used in the Lebenslauf that the Grundlage records with
        `Bestätigt: nein` (R-9.5 point 5)                         Blocker

A station header that is not in the strict form `MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort`
(for example years only) gets CV-02. Its bullets and its period are still checked: the station is
matched loosely (`<von> – <bis> | Position | Arbeitgeber`), so CV-04, CV-05, CV-13, CV-15 and
CV-16 apply to it as well.

Grundlage station records come from two forms (CG-2.4):
  - R-2.1 header lines `### MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort` in any note;
  - station notes with frontmatter `typ: station`, `titel`, `arbeitgeber`, `zeitraum_von`,
    `zeitraum_bis` (YYYY, YYYY-MM or MM/JJJJ, or `heute`), and `fuehrung` (ja, nein, ungeklärt).
Each record carries the text of its note (station note) or of its header block (header form),
so a number in a bullet is checked against its own station first (CV-05).

Usage:
  cv_checks.py lebenslauf.md [--grundlage PFAD ...] [--analyse analyse.md] [--ats]

`--grundlage` is repeatable: in directory mode pass the directory and the index note.
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
STATION_HEADER = re.compile(r"^### (\S+) – (\S+) \| ([^|]+?) \| (.+?)\s*$")
GRUNDLAGE_HEADER = STATION_HEADER
HEADER_ANY = re.compile(r"^### ")
SUB_BULLET = re.compile(r"^\s+- ")
PLACEHOLDER = re.compile(r"\[(ERGÄNZEN|KLÄREN)")
NUMBER = re.compile(r"(?<![\d.,])\d+(?:[.,]\d+)?(?![\d])")
GENERIC = re.compile(
    r"verantwortlich für|zuständig für|involved in|worked on|erfolgreich|innovativ|dynamisch|"
    r"vielfältig|\bdiverse\b|Expertise in|sicher in",
    re.IGNORECASE,
)
# Personnel leadership only (CG-7.2, CG-7.3). The unambiguous terms match alone. The lead verbs (`geleitet`,
# `führte`, `geführt`, `Führung`, …) match only together with a people object (Team, Mitarbeiter, Abteilung):
# alone they also describe technical leadership, conversations or reporting lines.
LEADERSHIP_TERMS = re.compile(
    r"\b(?:Teamleitung|Teamleiter(?:in)?|Teamlead|Personalverantwortung|Mitarbeiterführung|"
    r"Führungsverantwortung|disziplinarisch\w*)\b",
    re.IGNORECASE,
)
LEADERSHIP_VERB = re.compile(r"\b(?:geleitet|leitete|leite|geführt|führte|führe|führen|Führung)\b", re.IGNORECASE)
LEADERSHIP_OBJECT = re.compile(r"\b(?:Team|Teams|Mitarbeiter\w*|Abteilung\w*)\b", re.IGNORECASE)
# Neutral gap wording (CG-9, R-8.1). A gap entry is a line between two stations, not a bullet. The wording
# opens the entry (`Elternzeit (04/2019 – 08/2019)`, `… | Weiterbildung | …`); a job title that merely
# contains one of the words (`Referent Weiterbildung`) is a station.
GAP_ENTRY = re.compile(
    r"^(?:Auszeit|Elternzeit|Pflegezeit|Pflege eines Angehörigen|Weiterbildung|Berufliche Neuorientierung|"
    r"Bewerbungsphase|\[ERGÄNZEN: Grund der Lücke)\b"
)
STANDARD_HEADINGS = (
    "Persönliche Daten", "Kurzprofil", "Berufserfahrung", "Relevante Projekte", "Praktika",
    "Ausbildung und Studium", "Ausbildung", "Schulbildung", "Sprachkenntnisse", "IT- und Fachkenntnisse",
    "Kenntnisse", "Weiterbildung und Zertifikate", "Ehrenamt", "Interessen", "Lebenslauf",
)
# A heading may add a qualifier in parentheses (CG-11.2a), for example `Sprachkenntnisse (GER-Niveau)`.
STANDARD_HEADING = re.compile(r"^(?:" + "|".join(re.escape(h) for h in STANDARD_HEADINGS) + r")( \(.*\))?$")
# Station flags of a header-form Grundlage record (`- Team: …; Führung: ja`, `- Bestätigt: ja`). The unfilled
# template form `ja | nein | ungeklärt` does not count as an answer.
# `Fachliche Führung: ja` is no answer: the key stands at the start of the line or after `;`, `,` or `|`.
FUEHRUNG_LINE = re.compile(r"(?:^[ \t]*-?[ \t]*|[;,|][ \t]*)Führung:[ \t]*(ja|nein|ungeklärt)\b(?![ \t]*\|)", re.IGNORECASE | re.MULTILINE)
BESTAETIGT_LINE = re.compile(r"(?:^[ \t]*-?[ \t]*|[;,|][ \t]*)Bestätigt:[ \t]*(ja|nein)\b(?![ \t]*\|)", re.IGNORECASE | re.MULTILINE)
FLAG_VALUES = {"ja": "ja", "true": "ja", "yes": "ja", "nein": "nein", "false": "nein", "no": "nein", "ungeklärt": "ungeklärt"}
# List sections whose entries must stand in the Grundlage (CV-19). Free text (Kurzprofil, projects, Ehrenamt,
# Interessen) is not covered; that stays in the review (CG-13.4.6).
LIST_SECTIONS = (
    "IT- und Fachkenntnisse", "Kenntnisse", "Sprachkenntnisse", "Weiterbildung und Zertifikate",
    "Ausbildung und Studium", "Ausbildung", "Schulbildung",
)
LABEL_IS_PERIOD = re.compile(r"^[\d/\s–.\-]*(?:heute)?$")
PERIOD_PREFIX = re.compile(r"^(?:\d{1,2}/)?\d{4}(?:\s*[–-]\s*(?:(?:\d{1,2}/)?\d{4}|heute))?\s+(?=[A-Za-zÄÖÜäöü])")
ANALYSIS_STATUS = ("erfüllt", "teilweise", "nicht belegt", "unklar")
ANALYSIS_STRENGTH = ("stark", "mittel", "schwach", "—")
MAX_BULLETS = 5
MAX_BULLET_CHARS = 180
GAP_LIMIT_MONTHS = 2
EMPTY = ("", "—", "-")
EXPECTED_HEADER = "MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort"


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
    """Return (frontmatter dict, body text, full text) of a Markdown note."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    meta = {}
    body = text
    if match:
        for line in match.group(1).splitlines():
            pair = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
            if pair:
                meta[pair.group(1)] = pair.group(2).strip("\"'")
        body = text[match.end():]
    return meta, body, text


def key_of(position, employer):
    return position.strip().lower(), employer.split(",")[0].strip().lower()


def is_gap_entry(position):
    return bool(GAP_ENTRY.match(position.strip()))


def is_gap_line(line):
    """A non-bullet line of Berufserfahrung that opens with neutral gap wording: a header line whose position
    field is gap wording (`### <von> – <bis> | Elternzeit | —`), a header line without a period
    (`### Elternzeit (04/2019 – 08/2019)`), or a plain paragraph."""
    match = STATION_HEADER.match(line)
    text = match.group(3) if match else line[4:] if HEADER_ANY.match(line) else line
    return is_gap_entry(text)


def cv_stations(lines):
    """Stations of a Lebenslauf: every `### <von> – <bis> | Position | Arbeitgeber` line with a readable period.

    `strict` tells whether the header has the R-2.1 form (MM/JJJJ). A loosely matched header still
    takes part in the period, order, gap and Grundlage checks.
    """
    stations = []
    for number, line in enumerate(lines, 1):
        match = STATION_HEADER.match(line)
        if not match:
            continue
        start, end, position, employer = match.groups()
        start_period, end_period = parse_period(start), parse_period(end)
        if start_period in (None, "heute") or end_period is None:
            continue
        stations.append({
            "line": number,
            "start": start_period,
            "end": end_period,
            "start_raw": start,
            "end_raw": end,
            "position": position.strip(),
            "employer": employer.split(",")[0].strip(),
            "strict": bool(CV_HEADER.match(line)),
            "gap": is_gap_entry(position),
        })
    return stations


def flag(value, pattern, text):
    """A station flag from a frontmatter value or, failing that, from a labelled line of the note. '' when absent."""
    if value:
        return FLAG_VALUES.get(value.strip().lower(), "")
    match = pattern.search(text)
    return match.group(1).lower() if match else ""


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
        meta, body, text = read_note(note)
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
                "fuehrung": flag(meta.get("fuehrung"), FUEHRUNG_LINE, body) or "ungeklärt",
                "bestaetigt": flag(meta.get("bestaetigt"), BESTAETIGT_LINE, body),
                "team_groesse": meta.get("team_groesse", ""),
                "text": text,
            })
            continue
        body_lines = body.splitlines()
        for index, line in enumerate(body_lines):
            match = GRUNDLAGE_HEADER.match(line)
            if not match:
                continue
            end = index + 1
            while end < len(body_lines) and not re.match(r"^#{1,3} ", body_lines[end]):
                end += 1
            start, end_raw, position, employer = match.groups()
            block = "\n".join(body_lines[index:end])
            records.append({
                "file": note,
                "line": index + 1,
                "start": parse_period(start),
                "end": parse_period(end_raw),
                "start_raw": start,
                "end_raw": end_raw,
                "position": position.strip(),
                "employer": employer.split(",")[0].strip(),
                "fuehrung": flag(None, FUEHRUNG_LINE, block) or "ungeklärt",
                "bestaetigt": flag(None, BESTAETIGT_LINE, block),
                "team_groesse": "",
                "text": block,
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
            findings.append(finding("CV-06", "Blocker", file, cv["line"], f"Zeitraum weicht von der Grundlage ab (CV-06): {label} statt {source_label}"))
        return findings
    cv_start, src_start = cv["start"], source["start"]
    months_known = all(p and p[1] for p in (cv_start, cv_end, src_start, src_end))
    if not months_known:
        year_pairs = [(cv_start, src_start), (cv_end, src_end)]
        if any(c and s and c[0] != s[0] for c, s in year_pairs):
            findings.append(finding("CV-06", "Blocker", file, cv["line"], f"Jahr weicht von der Grundlage ab (CV-06): {label} statt {source_label}"))
        elif cv["strict"]:
            # A year-only CV header already carries the CV-02 header-form warning of check_cv; only a
            # Grundlage that lacks the month is reported here.
            findings.append(finding("CV-02", "Warnung", file, cv["line"], f"Monat fehlt in der Grundlage ({source_label}); Zeitraum nur auf Jahresebene geprüft (R-2.1)"))
        return findings
    if (cv_start, cv_end) != (src_start, src_end):
        findings.append(finding("CV-06", "Blocker", file, cv["line"], f"Zeitraum weicht von der Grundlage ab (CV-06): {label} statt {source_label}"))
    return findings


def select_record(station, candidates, file):
    """Pick the Grundlage record for a CV station among records with the same title and employer.

    The same title at the same employer may occur twice (another team, another period). The record whose
    period agrees with the CV station (month-exact, or by year when a month is missing) wins; next best is
    a record whose period overlaps the station. Only when no candidate fits in time is the first one taken,
    so that check_period reports the CV-06 deviation.
    """
    if len(candidates) == 1:
        return candidates[0]
    for record in candidates:
        if not any(f["regel"] == "CV-06" for f in check_period(station, record, file)):
            return record
    cv_start, cv_end = month_index(station["start"], 1), month_index(station["end"], 12)
    for record in candidates:
        start, end = month_index(record["start"], 1), month_index(record["end"], 12)
        if start is None:
            continue
        if (cv_end is None or start <= cv_end) and (end is None or cv_start <= end):
            return record
    return candidates[0]


def number_pattern(token):
    return rf"(?<![\d.,]){re.escape(token)}(?![\d])"


def check_cv(text, file, source_text=None, sources=None, ats=False):
    """Run the Lebenslauf rules. `source_text` and `sources` (station records) come from the Grundlage."""
    lines = text.splitlines()
    findings = []
    section = None
    current = None
    bullets = {}
    seen_bullets = {}
    gap_candidates = []  # line numbers of non-bullet lines with neutral gap wording in Berufserfahrung
    for number, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = line[3:].strip()
            current = None
            if not STANDARD_HEADING.match(section):
                findings.append(finding("CV-10", "Warnung", file, number, f"Überschrift nicht im Standardkatalog (CG-11.2a): „{section}“"))
        if PLACEHOLDER.search(line):
            findings.append(finding("CV-01", "Blocker", file, number, "offener Platzhalter (CV-01): " + line.strip()))
        if line.lstrip().startswith("|"):
            findings.append(finding("CV-08", "Blocker" if ats else "Warnung", file, number, "Tabelle im Lebenslauf (R-8.3)"))
        in_experience = bool(section) and section.startswith("Berufserfahrung")
        gap_line = in_experience and not line.startswith("- ") and not SUB_BULLET.match(line) and is_gap_line(line)
        if gap_line:
            gap_candidates.append(number)
        if in_experience and HEADER_ANY.match(line):
            current = number
            bullets[current] = []
            if not CV_HEADER.match(line) and not gap_line:
                findings.append(finding("CV-02", "Warnung", file, number, f"Kopfzeile nicht in der Form „{EXPECTED_HEADER}“ (R-2.1): " + line.strip()))
        if line.startswith("- ") and current is not None:
            bullets[current].append((number, line[2:].strip()))
        elif SUB_BULLET.match(line) and current is not None:
            findings.append(finding("CV-17", "Hinweis", file, number, "Unterpunkte sind nicht vorgesehen (R-2.1): " + line.strip()))

    stations = cv_stations(lines)
    if stations:
        starts = [month_index(s["start"], 1) for s in stations]
        if any(later > earlier for earlier, later in zip(starts, starts[1:])):
            findings.append(finding("CV-04", "Warnung", file, stations[0]["line"], "Stationen nicht in umgekehrt chronologischer Reihenfolge (R-2)"))
    for s in stations:
        end_index = month_index(s["end"], 12)
        if end_index is not None and end_index < month_index(s["start"], 1):
            findings.append(finding("CV-04", "Blocker", file, s["line"], f"Ende vor Beginn (CV-04): {s['start_raw']} – {s['end_raw']}"))

    station_of_line = {s["line"]: s for s in stations}
    for station_line, items in bullets.items():
        if len(items) > MAX_BULLETS:
            findings.append(finding("CV-03", "Warnung", file, station_line, f"{len(items)} Stichpunkte, Obergrenze {MAX_BULLETS} (CG-6)"))
        station = station_of_line.get(station_line)
        if not items and station_line not in gap_candidates and not (station and station["gap"]):
            findings.append(finding("CV-03", "Hinweis", file, station_line, "Station ohne Stichpunkte: „nur Kopfzeile“ bewusst entscheiden (CG-6.5)"))

    by_key = {}
    if sources is not None:
        for record in sources:
            by_key.setdefault(key_of(record["position"], record["employer"]), []).append(record)
        if not sources:
            findings.append(finding("CV-15", "Warnung", file, 0, "Grundlage hat keine Stationen; Abgleich nicht möglich (CV-15)"))
        for s in stations:
            candidates = by_key.get(key_of(s["position"], s["employer"]), [])
            if not candidates:
                if sources and not s["gap"]:
                    findings.append(finding("CV-15", "Blocker", file, s["line"], f"Station nicht in der Grundlage (CV-15): {s['position']} | {s['employer']}"))
                continue
            record = select_record(s, candidates, file)
            findings += check_period(s, record, file)
            if record.get("bestaetigt") == "nein" and not s["gap"]:
                findings.append(finding("CV-20", "Blocker", file, s["line"], f"Station in der Grundlage nicht bestätigt (`Bestätigt: nein`, CV-20): {s['position']} | {s['employer']}"))
            s["record"] = record

    for station_line, items in bullets.items():
        station = station_of_line.get(station_line)
        record = station.get("record") if station else None
        record_text = record.get("text") if record else None
        for number, bullet in items:
            key = re.sub(r"\s+", " ", bullet.lower())
            if key in seen_bullets:
                findings.append(finding("CV-09", "Hinweis", file, number, f"doppelter Stichpunkt (zuerst Zeile {seen_bullets[key]})"))
            else:
                seen_bullets[key] = number
            if GENERIC.search(bullet):
                findings.append(finding("CV-11", "Warnung", file, number, "allgemeine oder wertende Formulierung (CG-8.2.3): " + bullet))
            if len(bullet) > MAX_BULLET_CHARS:
                findings.append(finding("CV-12", "Hinweis", file, number, f"Stichpunkt länger als zwei Zeilen ({len(bullet)} Zeichen, CG-8.1)"))
            if source_text is not None:
                for match in NUMBER.finditer(bullet):
                    token = match.group(0)
                    pattern = number_pattern(token)
                    if record_text is not None and re.search(pattern, record_text):
                        if not unit_in_record(token, bullet[match.end():], record_text, bullet[:match.start()]):
                            findings.append(finding("CV-05", "Warnung", file, number, f"Zahl „{token}“ steht im Stationseintrag, aber nicht mit dieser Einheit oder diesem Bezug (CV-05): " + bullet))
                        continue
                    if re.search(pattern, source_text):
                        if record_text is not None:
                            findings.append(finding("CV-05", "Hinweis", file, number, f"Zahl „{token}“ nicht im Stationseintrag, aber an anderer Stelle der Grundlage belegt (CV-05): " + bullet))
                        continue
                    findings.append(finding("CV-05", "Blocker", file, number, f"Zahl „{token}“ nicht in der Grundlage belegt (CV-05): " + bullet))
            if record is not None and record.get("fuehrung") != "ja" and leadership_wording(bullet):
                fuehrung = record.get("fuehrung") or "ungeklärt"
                findings.append(finding("CV-16", "Blocker", file, number, f"Formulierung zur Personalführung ohne `fuehrung: ja` in der Grundlage (fuehrung: {fuehrung}, CV-16): " + bullet))

    if stations:
        ordered = sorted(stations, key=lambda s: -month_index(s["start"], 1))
        for older, newer in zip(ordered[1:], ordered):
            end_index = month_index(older["end"], 12)
            if end_index is None:
                continue
            gap = month_index(newer["start"], 1) - end_index - 1
            if gap <= GAP_LIMIT_MONTHS:
                continue
            first, last = sorted((newer["line"], older["line"]))
            if not any(first < number < last for number in gap_candidates):
                findings.append(finding("CV-13", "Blocker", file, newer["line"], f"Lücke von {gap} Monaten zwischen {older['end_raw']} und {newer['start_raw']} ohne neutralen Eintrag (CG-9)"))
    if source_text is not None:
        findings += check_list_sections(lines, file, source_text)
    return findings


def normalise(value):
    """Lower case, punctuation to spaces; `+`, `#` and inner dots stay (`C++`, `.NET`, `Node.js`)."""
    value = value.lower().translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}))
    value = re.sub(r"[^\w+#.]+", " ", value)
    return " ".join(token.rstrip(".") or token for token in value.split())


def in_text(item, normalised_source):
    """True when the item stands in the source as whole words."""
    item = normalise(item)
    return bool(item) and re.search(rf"(?<![\w+#.]){re.escape(item)}(?![\w+#])", normalised_source) is not None


UNIT = re.compile(r"[\s-]*(%|[A-Za-zÄÖÜäöüß]+)")
IDENTIFIER_BEFORE = re.compile(r"\b(?:ISO|IEC|DIN|RFC|PCI|SOC|BSI|EN)[\s-]*(?:/IEC[\s-]*)?$", re.IGNORECASE)


def unit_stem(word):
    """First four letters of a unit or noun; `%` equals `Prozent`."""
    word = word.lower()
    return "proz" if word == "%" else word[:4]


def unit_in_record(token, after, record_text, before=""):
    """The number of a bullet stands in the station record with the same unit or noun (compared by its first four
    letters, so `Entwickler` equals `Entwicklern`, `%` equals `Prozent`). Not compared: a year, a number with no word
    after it, a standard number (`ISO 27001`), and a number that the record gives with no word after it."""
    if re.fullmatch(r"(?:19|20)\d{2}", token) or IDENTIFIER_BEFORE.search(before):
        return True
    match = UNIT.match(after)
    if not match:
        return True
    unit = unit_stem(match.group(1))
    for hit in re.finditer(number_pattern(token), record_text):
        following = UNIT.match(record_text[hit.end():])
        if not following or unit_stem(following.group(1)) == unit:
            return True
    return False


def level_pair_in_source(language, level, source_text):
    """A language and its level stand together on one line of the Grundlage (`Englisch B2`, `Englisch (B2)`)."""
    language, level = normalise(language), normalise(level)
    return any(in_text(language, normalise(line)) and in_text(level, normalise(line)) for line in source_text.splitlines())


def check_list_sections(lines, file, source_text):
    """CV-19: every entry of a list section stands in the Grundlage. An entry is `<Label>: <item>, <item>`; a leading
    period (`2014`, `09/2010 – 06/2014`) is dropped, `|` separates parts, `und` and `&` join two items. The items are
    checked, the label only in Sprachkenntnisse. A language and its level must stand together on one line. A number
    in a parenthesis must stand in the Grundlage, not as part of a word (`B2` does not carry a `2`)."""
    findings = []
    normalised = normalise(source_text)
    section = None
    for number, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = re.sub(r" \(.*\)$", "", line[3:].strip())
            continue
        if section not in LIST_SECTIONS or not line.startswith("- ") or PLACEHOLDER.search(line):
            continue
        entry = re.sub(r"(?<!\w)[*_`]+|[*_`]+(?!\w)", "", line[2:].strip())

        def missing(item):
            item = item.strip()
            if not item or in_text(item, normalised):
                return False
            parts = [part for part in re.split(r"\s+(?:und|&)\s+", item) if part.strip()]
            return len(parts) < 2 or not all(in_text(part, normalised) for part in parts)

        if section == "Sprachkenntnisse":
            pair = re.match(r"^([^:(]+?)\s*(?::|\()\s*([^)]+?)\)?$", entry)
            if pair:
                language, levels = pair.group(1), [part for part in re.split(r"[,;/]", pair.group(2)) if part.strip()]
                for item in [language] + levels:
                    if missing(item):
                        findings.append(finding("CV-19", "Blocker", file, number, f"Eintrag „{item.strip()}“ steht nirgends in der Grundlage (CV-19): " + entry))
                if not any(missing(i) for i in [language] + levels):
                    for level in levels:
                        if not level_pair_in_source(language, level, source_text):
                            findings.append(finding("CV-19", "Blocker", file, number, f"Niveau „{level.strip()}“ steht in der Grundlage nicht bei „{language.strip()}“ (CV-19): " + entry))
                continue
        qualifiers = re.findall(r"\(([^)]*)\)", entry)
        items = []
        for part in re.sub(r"\([^)]*\)", "", entry).split("|"):
            colon = re.search(r":(?!\d)", part)
            label, rest = (part[:colon.start()], part[colon.end():]) if colon else ("", part)
            items += re.split(r"[,;]", rest)
            if section == "Sprachkenntnisse" and label.strip():
                items.append(label)
        for item in items:
            item = PERIOD_PREFIX.sub("", item.strip())
            if not item or LABEL_IS_PERIOD.match(item):
                continue
            if missing(item):
                findings.append(finding("CV-19", "Blocker", file, number, f"Eintrag „{item}“ steht nirgends in der Grundlage (CV-19): " + entry))
        for qualifier in qualifiers:
            for token in NUMBER.findall(qualifier):
                if not re.search(rf"(?<![\w.,]){re.escape(token)}(?![\d])", source_text):
                    findings.append(finding("CV-19", "Blocker", file, number, f"Zahl „{token}“ nicht in der Grundlage belegt (CV-19): " + entry))
    return findings


def leadership_wording(bullet):
    """True for personnel-leadership wording (CG-7.2, CG-7.3): a leadership term, or a lead verb (`geleitet`,
    `führte`, `geführt`, `Führung`, …) with Team, Mitarbeiter or Abteilung."""
    if LEADERSHIP_TERMS.search(bullet):
        return True
    return bool(LEADERSHIP_VERB.search(bullet) and LEADERSHIP_OBJECT.search(bullet))


MONTHS = r"(?:Januar|Februar|März|Maerz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)"
DATE_FORMS = (
    r"(?:\d{1,2}\.\d{1,2}\.(?:\d{4}|\d{2})(?![\d.-]*\d)"
    r"|\d{4}-\d{2}-\d{2}(?![\d.-]*\d)"
    r"|\d{1,2}/\d{1,2}/(?:\d{4}|\d{2})(?![\d/]*\d)"
    r"|\d{1,2}\.?\s*" + MONTHS + r"\s+(?:\d{4}|\d{2})(?!\d))"
)
# Only punctuation, `am` and whitespace may stand between the keyword and the date.
BIRTH_GAP = r"(?:[\s:,;()\u2013-]|\bam\b)*"
BIRTHDATE_KEYWORD = re.compile(
    r"(?:\bGeburtsdatum|\bgeb\.|\bgeboren\b)" + BIRTH_GAP + r"(?<![\d.\-/])" + DATE_FORMS
    # `geborene Beispiel, 03.05.1971`: one maiden-name word may stand between
    + r"|\bgeboren(?:e[rn]?)\b[\s:,;]*(?:[A-ZÄÖÜ][\wäöüß-]*[\s:,;]*)?(?<![\d.\-/])" + DATE_FORMS
    # a date before the keyword: `03.05.1971 geboren`
    + r"|(?<![\d.\-/])" + DATE_FORMS + r"[\s,;()]*(?:\bgeboren\b|\bgeb\.)",
    re.I,
)
# A bare year counts only directly after `Geburtsdatum` or `geb.`
BIRTHDATE_YEAR = re.compile(r"(?:\bGeburtsdatum|\bgeb\.)" + BIRTH_GAP + r"(?<![\d.\-/])(?:19|20)\d{2}(?![\d.\-/])", re.I)
# `Mustermann (* 03.05.1971)` / `Mustermann *03.05.1971`: a capitalised name token directly before `*` or `(*`, the
# date not followed by a closing emphasis star anywhere on the line (`Frist *31.12.2026 bis*` is emphasis).
BIRTHDATE_STAR = re.compile(r"(?<![*\w])[A-ZÄÖÜ][\wäöüß-]*[,]?\s+\(?\*\s?(?<![\d.\-/])" + DATE_FORMS + r"(?![^\n]*\*)")


def birthdate_findings(text, file):
    """CV-18 (RC-11 rule 4): a birthdate in analyse.md or a firm file. `Geburtsdatum`, `geb.` or `geboren` with a date
    on the same line, or a word followed by `*` and a date. Plain dates (`Stand: 2026-10-23`, a Frist) and a `*` that
    opens a list item or emphasis do not match."""
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        if BIRTHDATE_KEYWORD.search(line) or BIRTHDATE_YEAR.search(line) or BIRTHDATE_STAR.search(line):
            findings.append(finding("CV-18", "Warnung", file, number, "Geburtsdatum einer Person (RC-5.3 Regel 5, RC-11 Regel 4): nicht erfassen, mit Zustimmung entfernen"))
    return findings


def check_analysis(text, file):
    """Run the rules for analyse.md (CG-4): Muss evidence and status vocabulary."""
    findings = birthdate_findings(text, file)
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
            findings.append(finding("CV-14", "Warnung", file, number, f"unbekannter Status „{status}“ (CG-4)"))
        if strength and strength not in ANALYSIS_STRENGTH:
            findings.append(finding("CV-14", "Warnung", file, number, f"unbekannte Stärke „{strength}“ (CG-4)"))
        if priority == "Muss" and status == "erfüllt":
            if evidence in EMPTY:
                findings.append(finding("CV-07", "Blocker", file, number, "Muss-Anforderung als erfüllt markiert ohne Nachweis (CG-4.5): " + row.get("Anforderung", "")))
            if strength in ("schwach", "—", ""):
                findings.append(finding("CV-14", "Warnung", file, number, "erfüllt setzt Stärke mittel oder stark voraus (CG-4.1)"))
        if priority == "Muss" and status in ("nicht belegt", "teilweise"):
            findings.append(finding("CV-07", "Warnung", file, number, f"Muss-Lücke ({status}), Verwendung prüfen (CG-4.5): " + row.get("Anforderung", "")))
    return findings


def read_optional(path, rule, label, findings):
    """Read an optional input file. A missing or unreadable file is a Warnung in `findings`, no crash; returns None then."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError) as error:
        findings.append(finding(rule, "Warnung", path, 0, f"{label} nicht lesbar ({error.__class__.__name__}), Prüfung nicht möglich"))
        return None


def load_records(paths):
    records = []
    for path in paths:
        records += grundlage_records(path)
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deterministic checks for a Lebenslauf (CG-13).")
    parser.add_argument("lebenslauf", help="path to lebenslauf.md")
    parser.add_argument("--grundlage", action="append", default=[], help="Grundlage file or directory (repeatable: directory and index note)")
    parser.add_argument("--analyse", help="path to analyse.md")
    parser.add_argument("--firma", action="append", default=[], help="firm file in <wurzel>/firmen/ (repeatable): birthdate check CV-18")
    parser.add_argument("--ats", action="store_true", help="treat tables as Blocker (posting requires ATS)")
    args = parser.parse_args(argv)

    with open(args.lebenslauf, encoding="utf-8") as handle:
        text = handle.read()
    source_text = read_sources(args.grundlage) if args.grundlage else None
    sources = load_records(args.grundlage) if args.grundlage else None

    findings = check_cv(text, args.lebenslauf, source_text, sources, ats=args.ats)
    if args.analyse:
        analysis_text = read_optional(args.analyse, "CV-14", "Analyse", findings)
        if analysis_text is not None:
            findings += check_analysis(analysis_text, args.analyse)

    for firm_path in args.firma:
        firm_text = read_optional(firm_path, "CV-18", "Firmendatei", findings)
        if firm_text is not None:
            findings += birthdate_findings(firm_text, firm_path)

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
