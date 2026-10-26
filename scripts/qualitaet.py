#!/usr/bin/env python3
"""Quality assurance of one Vorgang: deterministic checks, export checks and semantic verdicts in one versioned report.

Usage:
  qualitaet.py pruefen <vorgang-ordner> [--konfiguration K | --grundlage PFAD ...] [--urteile DATEI] [--nur-anzeigen]
  qualitaet.py status <vorgang-ordner>
  qualitaet.py entscheiden <vorgang-ordner> <pruefung> --grund TEXT --ja
  qualitaet.py katalog

`pruefen` runs the rules of cv_checks.py (CV-xx, BR-xx), the cross-document rules QS-xx, the export rules EX-xx, the
process rules PR-xx and reads the semantic verdicts SEM-xx of the model, and writes `qualitaet.json` into the Vorgang. The
report is bound to the SHA-256 of every document and export; a changed file makes it stale (`aktualitaet`).

This script reads files and runs the local tools pdftotext and pdfinfo. It sends nothing, opens no network connection and
changes no status of a Vorgang; the approval before any dispatch stays with the user (workflow.py, versand_freigabe).
A result is `PASS` only when a check ran and found nothing: a missing tool, a missing Grundlage or a missing verdict of the
model is `BLOCKED` or `NEEDS_REVIEW`, never `PASS`.

Exit codes: 0 ready to approve, 1 blocked by a FAIL, 2 not ready (BLOCKED, NEEDS_REVIEW or not checked), 3 refused.
Standard library only.
"""

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "skills", "job-application-export", "scripts"))

import cv_checks as cv  # noqa: E402
import export_document as ex  # noqa: E402
import grundlage_hash as gh  # noqa: E402
from stellensuche import Blocker, Refused, atomic_write, digest, load_json, redact, stamp  # noqa: E402

RULES = "qualitaetssicherung/en.md QS-1"
SCHEMA = 1
BERICHT = "qualitaet.json"
VERLAUF = "qualitaet-verlauf.jsonl"
ENTSCHEIDUNGEN = "qualitaet-entscheidungen.json"
URTEILE = "qualitaet-urteile.json"

# the documents of the send package (workflow.py takes this tuple) and the context the checks read
DOKUMENTE = ("lebenslauf.md", "anschreiben.md", "motivationsschreiben.md", "email.md", "anschreiben-portal.txt",
             "motivationsschreiben-portal.txt")
KONTEXT = ("analyse.md", "stellenanzeige.md")
PFLICHT = ("lebenslauf.md", "anschreiben.md")
DOC_TYPE = {"lebenslauf.md": "cv", "anschreiben.md": "letter", "motivationsschreiben.md": "motivation", "email.md": "email"}

PASS, FAIL, WARNING, REVIEW, NA, BLOCKED = "PASS", "FAIL", "WARNING", "NEEDS_REVIEW", "NOT_APPLICABLE", "BLOCKED"
STATI = (PASS, FAIL, WARNING, REVIEW, NA, BLOCKED)
FREIGABEFAEHIG = ("BEREIT", "BEREIT_MIT_WARNUNGEN", "BEREIT_NACH_MANUELLER_PRUEFUNG")

# id -> (title, kind). The order is the order of the report.
KATALOG = {
    "CV": ("Lebenslauf: Belege, Zahlen, Führung, Zeiträume, Struktur (CV-01 bis CV-24)", "deterministisch"),
    "BR-A": ("Anschreiben: Platzhalter, Zahlen, Erfahrungsdauer, Führung (BR-01 bis BR-05)", "deterministisch"),
    "BR-M": ("Motivationsschreiben (BR-01 bis BR-05)", "deterministisch"),
    "BR-E": ("E-Mail: Platzhalter und Inhalt (BR-01, BR-05)", "deterministisch"),
    "QS-01": ("Firma, Stellenbezug und fremde Arbeitgebernamen", "deterministisch"),
    "QS-02": ("Kontaktdaten über die Dokumente gleich", "deterministisch"),
    "QS-03": ("Zeitangaben „seit …“ gegen die Stationen", "deterministisch"),
    "QS-04": ("Übernommener Anzeigentext und Wortwiederholung", "deterministisch"),
    "QS-05": ("Floskeln und Satzlänge", "deterministisch"),
    "EX-01": ("Export: Integrität, Manifest und Aktualität gegen die Quelle", "deterministisch"),
    "EX-02": ("Export: Inhalt nach dem Export gleich der Quelle (Wortlaut, Zeichen, Reihenfolge)", "deterministisch"),
    "EX-03": ("Export: Textextraktion und ATS-Lesbarkeit", "deterministisch"),
    "EX-04": ("Export: Seitenzahl, Seitenlimit, leere Seiten", "deterministisch"),
    "PR-01": ("Prozess: Pflichtdokumente vorhanden", "deterministisch"),
    "PR-02": ("Prozess: Kontext der Stelle vorhanden (vorgang.md, Anzeige, Analyse)", "deterministisch"),
    "SEM-01": ("Evidenz: Aussagen gegen die Datengrundlage (Fälle A bis D)", "semantisch"),
    "SEM-02": ("Verantwortung und Seniorität sind belegt und nicht überhöht", "semantisch"),
    "SEM-03": ("Relevanz für die Zielgruppe ohne Keyword- oder Score-Optimierung", "semantisch"),
    "SEM-04": ("Sprache, Ton und Verständlichkeit", "semantisch"),
    "SEM-05": ("Konsistenz der Aussagen über alle Dokumente", "semantisch"),
}
SEM_DOKUMENTE = {"SEM-01": ("lebenslauf.md", "anschreiben.md"), "SEM-02": ("lebenslauf.md", "anschreiben.md"),
                 "SEM-03": ("anschreiben.md",), "SEM-04": DOC_TYPE, "SEM-05": ("*",)}

GRENZEN = (
    "Die Prüfung ist kein Beweis der Richtigkeit: sie findet Widersprüche und fehlende Belege, ein PASS heißt „nichts gefunden“.",
    "ATS-Lesbarkeit wird am extrahierten Text geprüft (pdftotext, DOCX-XML); wie ein bestimmtes Bewerbermanagementsystem den Export liest, ist nicht geprüft und nicht zugesagt.",
    "Schriften, Farben, Seitenränder und das optische Erscheinungsbild werden nicht bewertet.",
    "Semantische Urteile (SEM-xx) stammen von einem Modell; geprüft wird nur, dass Zitat und Evidenz wörtlich vorkommen, nicht ob das Urteil stimmt.",
    "Die Freigabe des Versandpakets und der Versand selbst bleiben bei der Nutzerin oder dem Nutzer.",
)

FIRM_NAME = re.compile(r"\b([A-ZÄÖÜ][\wÄÖÜäöüß&.-]*(?:\s+[A-ZÄÖÜ][\wÄÖÜäöüß&.-]*){0,3})\s+(?:GmbH|AG|SE|KG|UG|mbH|KGaA)\b")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"(?<![\w/])(?:\+|00)?\d[\d ()/-]{7,}\d")
SEIT = re.compile(r"\bseit\s+(?:dem\s+)?(?:\d{1,2}/)?((?:19|20)\d{2})\b", re.IGNORECASE)
FLOSKELN = ("hiermit bewerbe ich mich", "wie sie meinem lebenslauf entnehmen", "teamfaehig", "belastbar", "hochmotiviert",
            "ueberdurchschnittlich")
SATZ_MAX_WOERTER = 45
UEBERNAHME_FENSTER = 8
HAEUFUNG_AB = 6
STOP = {"dieser", "diese", "dieses", "werden", "wurde", "haben", "bereits", "gerne", "durch", "sowie", "dabei", "dafuer",
        "dazu", "meine", "meiner", "meinen", "ihrer", "ihren", "damit", "dieser", "aufgaben"}


# ---------------------------------------------------------------- results

def clip(text, limit=160):
    return redact(text, limit)


def befund(regel, schweregrad, datei, zeile, text):
    return cv.finding(regel, schweregrad, datei, zeile, clip(text))


def ergebnis(check_id, befunde=(), blockiert="", nicht_anwendbar=""):
    """One check of the report. FAIL wins over BLOCKED, BLOCKED over NEEDS_REVIEW, NEEDS_REVIEW over WARNING."""
    titel, art = KATALOG[check_id]
    befunde = list(befunde)
    grade = {b["schweregrad"] for b in befunde}
    if nicht_anwendbar:
        status = NA
    elif "Blocker" in grade:
        status = FAIL
    elif blockiert:
        status = BLOCKED
    elif "Prüfung" in grade:
        status = REVIEW
    elif befunde:
        status = WARNING
    else:
        status = PASS
    check = {"id": check_id, "titel": titel, "art": art, "status": status, "befunde": befunde}
    if blockiert and status == BLOCKED:
        check["grund"] = blockiert
    if nicht_anwendbar:
        check["grund"] = nicht_anwendbar
    return check


def gesamt(checks):
    if not checks:
        return "NICHT_GEPRUEFT"
    stati = [c["status"] for c in checks]
    if FAIL in stati:
        return "BLOCKIERT"
    if BLOCKED in stati:
        return "UNVOLLSTAENDIG"
    review = [c for c in checks if c["status"] == REVIEW]
    if any(not c.get("manuell_akzeptiert") for c in review):
        return "MANUELL_ZU_PRUEFEN"
    if review:
        return "BEREIT_NACH_MANUELLER_PRUEFUNG"
    return "BEREIT_MIT_WARNUNGEN" if WARNING in stati else "BEREIT"


# ---------------------------------------------------------------- inputs

def lies(path):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return None


def datei_hash(path):
    return gh.sha256_file(path) if os.path.isfile(path) else ""


def dokument_hashes(ordner):
    """Hash of every document and context file of the Vorgang that exists."""
    return {name: datei_hash(os.path.join(ordner, name)) for name in sorted(DOKUMENTE + KONTEXT) if os.path.isfile(os.path.join(ordner, name))}


def export_dateien(ordner):
    pfad = os.path.join(ordner, "export")
    if not os.path.isdir(pfad):
        return []
    return sorted(n for n in os.listdir(pfad) if not n.startswith(".") and os.path.isfile(os.path.join(pfad, n)))


def export_hashes(ordner):
    return {"export/" + n: datei_hash(os.path.join(ordner, "export", n)) for n in export_dateien(ordner)}


def dokumente_stand(ordner):
    """One hash over all documents: the version a verdict about the whole set (`dokument: "*"`) belongs to."""
    return digest(*[f"{k}={v}" for k, v in sorted(dokument_hashes(ordner).items())])


def stand_von(dokumente, exporte, grundlage_hash):
    return digest(*[f"{k}={v}" for k, v in sorted({**dokumente, **exporte}.items())], grundlage_hash or "-")


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", (text or "").replace("\r\n", "\n"), re.S)
    meta = {}
    for line in (match.group(1).splitlines() if match else []):
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = ex.unquote(value.strip())
    return meta


def grundlage_laden(pfade, konfiguration):
    """-> (text, records, hash, grund). `grund` says why there is none."""
    index = None
    try:
        if not pfade:
            info = gh.compute(konfiguration)
            pfade = [info["grundlage"]]
            index = gh.read_frontmatter(konfiguration).get("grundlage_index")
            if index:
                pfade.append(gh.resolve(index))
            wert = info["hash"]
        else:
            wert = digest(*[gh.sha256_file(p) for p in pfade if os.path.isfile(p)]) if all(os.path.exists(p) for p in pfade) else None
        if wert is None:
            return None, None, None, "Grundlage nicht gefunden"
        return cv.read_sources(pfade), cv.load_records(pfade), wert, ""
    except (Blocker, gh.Blocker) as error:
        return None, None, None, clip(str(error), 200)
    except (OSError, UnicodeDecodeError) as error:
        return None, None, None, f"Grundlage nicht lesbar ({error.__class__.__name__})"


def kontext_laden(ordner, pfade, konfiguration):
    texte, unlesbar = {}, []
    for name in DOKUMENTE + KONTEXT + ("vorgang.md",):
        pfad = os.path.join(ordner, name)
        if os.path.isfile(pfad):
            text = lies(pfad)
            if text is None:
                unlesbar.append(name)
            else:
                texte[name] = text
    text, records, wert, grund = grundlage_laden(pfade, konfiguration)
    meta = frontmatter(texte.get("vorgang.md", ""))
    return {"ordner": ordner, "texte": texte, "unlesbar": unlesbar, "grundlage": text, "records": records, "grundlage_hash": wert,
            "grundlage_grund": grund, "meta": meta, "kontext": "\n".join(texte.get(n, "") for n in KONTEXT)}


# ---------------------------------------------------------------- the rules of cv_checks (CV, BR)

def pruefe_regeln(ctx):
    checks = []
    for name, check_id in (("lebenslauf.md", "CV"), ("anschreiben.md", "BR-A"), ("motivationsschreiben.md", "BR-M"), ("email.md", "BR-E")):
        text = ctx["texte"].get(name)
        if text is None:
            checks.append(ergebnis(check_id, nicht_anwendbar=f"{name} liegt nicht vor"))
            continue
        quelle, records = ctx["grundlage"], ctx["records"]
        if name == "lebenslauf.md":
            befunde = cv.check_cv(text, name, quelle, records, ats=frontmatter(text).get("format") == "ats")
            if "analyse.md" in ctx["texte"]:
                befunde += cv.check_analysis(ctx["texte"]["analyse.md"], "analyse.md")
        else:
            befunde = cv.check_letter(text, name, DOC_TYPE[name], quelle, records, ctx["kontext"])
        befunde = [cv.finding(b["regel"], b["schweregrad"], b["datei"], b["zeile"], clip(b["befund"])) for b in befunde]
        offen = "" if quelle is not None or name == "email.md" else f"Grundlage nicht verfügbar ({ctx['grundlage_grund']}): die Belegprüfung gegen die Grundlage ist nicht möglich"
        checks.append(ergebnis(check_id, befunde, blockiert=offen))
    return checks


# ---------------------------------------------------------------- cross-document rules (QS)

def kern(firma):
    return re.sub(r"\b(?:GmbH|AG|SE|KG|UG|mbH|KGaA|&|Co\.?)\b", " ", firma or "").strip()


def qs_firma(ctx):
    firma, ref = ctx["meta"].get("firma", ""), ctx["meta"].get("ref_nr", "")
    briefe = [n for n in ("anschreiben.md", "motivationsschreiben.md", "email.md") if n in ctx["texte"]]
    if not briefe:
        return ergebnis("QS-01", nicht_anwendbar="kein Anschreiben, Motivationsschreiben oder E-Mail vorhanden")
    if not firma:
        return ergebnis("QS-01", blockiert="`firma` fehlt in vorgang.md: der Stellenbezug ist nicht prüfbar")
    befunde, bekannt = [], cv.normalise(kern(firma))
    grundlage = cv.normalise(ctx["grundlage"] or "")
    for name in briefe:
        text = ctx["texte"][name]
        if bekannt and bekannt not in cv.normalise(text):
            befunde.append(befund("QS-01", "Warnung", name, 1, f"Der Name der Firma „{firma}“ kommt nicht vor: kein erkennbarer Stellenbezug"))
        if ref and name == "anschreiben.md" and ref not in text:
            befunde.append(befund("QS-01", "Hinweis", name, 1, f"Die Referenznummer „{ref}“ der Anzeige fehlt im Anschreiben"))
        for number, line in enumerate(text.splitlines(), 1):
            for match in FIRM_NAME.finditer(line):
                name_norm = cv.normalise(match.group(1))
                if name_norm and name_norm != bekannt and bekannt not in name_norm and name_norm not in bekannt \
                        and (not grundlage or name_norm not in grundlage):
                    befunde.append(befund("QS-01", "Blocker", name, number, f"Arbeitgebername „{match.group(0)}“ ist weder die Zielfirma noch ein Arbeitgeber der Grundlage"))
    offen = "" if ctx["grundlage"] is not None else "ohne Grundlage lässt sich ein fremder Arbeitgebername nicht von einem eigenen unterscheiden"
    return ergebnis("QS-01", befunde, blockiert=offen)


def qs_kontakt(ctx):
    namen = [n for n in ("lebenslauf.md", "anschreiben.md", "motivationsschreiben.md") if n in ctx["texte"]]
    if len(namen) < 2:
        return ergebnis("QS-02", nicht_anwendbar="weniger als zwei Dokumente mit Absender")
    mails, telefone = {}, {}
    for name in namen:
        text = ctx["texte"][name]
        for mail in EMAIL.findall(text):
            mails.setdefault(mail.lower(), name)
        for nummer in PHONE.findall(text):
            ziffern = re.sub(r"\D", "", nummer)
            ziffern = "0" + ziffern[4:] if ziffern.startswith("0049") else "0" + ziffern[2:] if ziffern.startswith("49") else ziffern
            if not re.fullmatch(r"(?:19|20)\d{2}(?:19|20)\d{2}", ziffern):  # a period `2019 – 2022`, not a number
                telefone.setdefault(ziffern, name)
    befunde = []
    for art, werte in (("E-Mail-Adressen", mails), ("Telefonnummern", telefone)):
        if len(werte) > 1:
            befunde.append(befund("QS-02", "Prüfung", "*", 0, f"Verschiedene {art} in den Dokumenten ({', '.join(sorted(set(werte.values())))}): der Absender muss überall gleich sein"))
    return ergebnis("QS-02", befunde)


def qs_zeitangaben(ctx):
    if ctx["records"] is None:
        return ergebnis("QS-03", blockiert="ohne Grundlage sind die Stationszeiträume nicht bekannt")
    jahre = {r["start"][0] for r in ctx["records"] if isinstance(r.get("start"), tuple)}
    befunde = []
    for name in ("anschreiben.md", "motivationsschreiben.md"):
        for number, line in enumerate(ctx["texte"].get(name, "").splitlines(), 1):
            for match in SEIT.finditer(line):
                if int(match.group(1)) not in jahre:
                    befunde.append(befund("QS-03", "Warnung", name, number, f"„{match.group(0)}“ entspricht keinem Stationsbeginn der Grundlage"))
    if not any(n in ctx["texte"] for n in ("anschreiben.md", "motivationsschreiben.md")):
        return ergebnis("QS-03", nicht_anwendbar="kein Brief vorhanden")
    return ergebnis("QS-03", befunde)


def brief_woerter(text):
    first, body = cv.letter_text(text)
    return cv.normalise(" ".join(body)).split()


def qs_uebernahme(ctx):
    anzeige = ctx["texte"].get("stellenanzeige.md")
    briefe = [n for n in ("anschreiben.md", "motivationsschreiben.md") if n in ctx["texte"]]
    if not briefe:
        return ergebnis("QS-04", nicht_anwendbar="kein Brief vorhanden")
    befunde = []
    firma = set(cv.normalise(ctx["meta"].get("firma", "")).split())
    for name in briefe:
        woerter = brief_woerter(ctx["texte"][name])
        if anzeige:
            vorlage = " " + " ".join(cv.normalise(anzeige).split()) + " "
            for start in range(len(woerter) - UEBERNAHME_FENSTER + 1):
                if " " + " ".join(woerter[start:start + UEBERNAHME_FENSTER]) + " " in vorlage:
                    befunde.append(befund("QS-04", "Warnung", name, 0, f"Mindestens {UEBERNAHME_FENSTER} Wörter in Folge stehen wörtlich in der Anzeige: „{' '.join(woerter[start:start + UEBERNAHME_FENSTER])}“"))
                    break
        zaehler = Counter(w for w in woerter if len(w) >= 6 and w not in STOP and w not in firma)
        for wort, anzahl in zaehler.most_common(1):
            if anzahl >= HAEUFUNG_AB:
                befunde.append(befund("QS-04", "Warnung", name, 0, f"„{wort}“ kommt {anzahl}-mal vor: Wiederholung wirkt wie Schlagwortfüllung"))
    return ergebnis("QS-04", befunde, blockiert="" if anzeige else "stellenanzeige.md fehlt: ein übernommener Anzeigentext ist nicht erkennbar")


def qs_floskeln(ctx):
    briefe = [n for n in ("anschreiben.md", "motivationsschreiben.md") if n in ctx["texte"]]
    if not briefe:
        return ergebnis("QS-05", nicht_anwendbar="kein Brief vorhanden")
    befunde = []
    for name in briefe:
        first, body = cv.letter_text(ctx["texte"][name])
        text = cv.normalise(" ".join(body))
        for floskel in FLOSKELN:
            if floskel in text:
                befunde.append(befund("QS-05", "Hinweis", name, 0, f"Floskel „{floskel}“: konkret belegen statt behaupten"))
        for satz in re.split(r"(?<=[.!?])\s+", " ".join(body)):
            if len(satz.split()) > SATZ_MAX_WOERTER:
                befunde.append(befund("QS-05", "Hinweis", name, 0, f"Satz mit {len(satz.split())} Wörtern: „{satz[:60]}…“"))
    return ergebnis("QS-05", befunde)


# ---------------------------------------------------------------- the exports (EX)

def extrahiere(pfad, fmt):
    """-> (text, struktur, grund). `text` is None when the text cannot be read; `struktur` counts tables and images."""
    struktur = {"tabellen": 0, "bilder": 0}
    try:
        if fmt == "pdf":
            if not shutil.which("pdftotext"):
                return None, struktur, "pdftotext (poppler-utils) ist nicht installiert: die Textextraktion des PDF ist nicht prüfbar"
            lauf = subprocess.run(["pdftotext", "-enc", "UTF-8", pfad, "-"], capture_output=True, timeout=60)
            if lauf.returncode != 0:
                return None, struktur, "pdftotext konnte das PDF nicht lesen"
            return lauf.stdout.decode("utf-8", "replace"), struktur, ""
        if fmt == "docx":
            with zipfile.ZipFile(pfad) as archiv:
                xml = archiv.read("word/document.xml").decode("utf-8", "replace")
                struktur["bilder"] = len([n for n in archiv.namelist() if n.startswith("word/media/")])
            struktur["tabellen"] = len(re.findall(r"<w:tbl>", xml))
            absaetze = re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)
            return "\n".join(html.unescape("".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", p, re.S))) for p in absaetze), struktur, ""
        text = lies(pfad)
        if text is None:
            return None, struktur, "Datei nicht lesbar"
        if fmt == "html":
            struktur["tabellen"] = len(re.findall(r"<table", text, re.I))
            struktur["bilder"] = len(re.findall(r"<img", text, re.I))
            text = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style|title)\b.*?</\1>", " ", text, flags=re.S | re.I)))
        return text, struktur, ""
    except (OSError, zipfile.BadZipFile, KeyError, subprocess.TimeoutExpired) as error:
        return None, struktur, f"Extraktion fehlgeschlagen ({error.__class__.__name__})"


def seitenzahl(pfad):
    if not shutil.which("pdfinfo"):
        return None
    try:
        lauf = subprocess.run(["pdfinfo", pfad], capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    treffer = re.search(rb"^Pages:\s+(\d+)", lauf.stdout, re.M)
    return int(treffer.group(1)) if treffer else None


def pruefe_exporte(ctx):
    ordner = ctx["ordner"]
    dateien = export_dateien(ordner)
    manifeste = [n for n in dateien if n.endswith(".manifest.json")]
    if not dateien:
        return [ergebnis(i, nicht_anwendbar="kein Export vorhanden (export/ fehlt oder ist leer)") for i in ("EX-01", "EX-02", "EX-03", "EX-04")]
    integritaet, inhalt, ats, seiten = [], [], [], []
    luecken = {"EX-02": [], "EX-03": [], "EX-04": []}
    abgedeckt = set()
    for name in manifeste:
        rel = "export/" + name
        try:
            manifest = json.loads(lies(os.path.join(ordner, rel)) or "")
            datei = manifest["ausgabe"]["datei"]
            soll = manifest["ausgabe"]["sha256"]
            fmt = manifest["format"]
        except (ValueError, KeyError, TypeError):
            integritaet.append(befund("EX-01", "Blocker", rel, 0, "Manifest nicht lesbar oder unvollständig"))
            continue
        abgedeckt.add(datei)
        pfad = os.path.join(ordner, "export", datei)
        if datei_hash(pfad) != soll:
            integritaet.append(befund("EX-01", "Blocker", rel, 0, f"{datei} fehlt oder weicht vom Hash des Manifests ab: der Export wurde nach dem Erzeugen verändert"))
            continue
        quelle = os.path.normpath(os.path.join(ordner, "export", manifest.get("quelle", {}).get("pfad", "")))
        if datei_hash(quelle) != manifest.get("quelle", {}).get("sha256"):
            integritaet.append(befund("EX-01", "Blocker", rel, 0, f"Der Export {datei} ist veraltet: die Quelle wurde nach dem Export geändert"))
            continue
        if ctx["grundlage_hash"] and manifest.get("frontmatter", {}).get("grundlage_hash") not in (None, ctx["grundlage_hash"]):
            integritaet.append(befund("EX-01", "Warnung", rel, 0, "Der Export wurde mit einem anderen Stand der Datengrundlage erzeugt"))
        text, struktur, grund = extrahiere(pfad, fmt)
        if text is None:
            for kennung in luecken:
                luecken[kennung].append(f"{datei}: {grund}")
            continue
        meta, body = ex.read_document(quelle)
        seiten_roh = text.split("\f")  # the form feeds separate the pages; strip_page_numbers joins them
        text = ex.strip_page_numbers(text) if fmt == "pdf" else text
        fehlt, zuviel = ex.compare_content(body, text)
        if fehlt or zuviel:
            inhalt.append(befund("EX-02", "Blocker", rel, 0, f"Wortlaut weicht ab; fehlt: {' '.join(sorted(fehlt))[:60] or '-'}; zusätzlich: {' '.join(sorted(zuviel))[:60] or '-'}"))
        else:
            for meldung in ex.fact_differences(body, text):
                inhalt.append(befund("EX-02", "Blocker", rel, 0, meldung))
            reihenfolge = ex.first_order_difference(body, text)
            if reihenfolge:
                inhalt.append(befund("EX-02", "Blocker", rel, 0, f"Reihenfolge weicht ab: {reihenfolge}"))
        if cv.PLACEHOLDER.search(text):
            inhalt.append(befund("EX-02", "Blocker", rel, 0, "offener Platzhalter im Export"))
        if fmt in ("pdf", "docx") and len(text.split()) < 30:
            ats.append(befund("EX-03", "Blocker", rel, 0, "Aus dem Export lässt sich kaum Text lesen (Bild statt Text?): ein ATS sieht ihn leer"))
        for kontakt in EMAIL.findall(body):
            if kontakt not in text:
                ats.append(befund("EX-03", "Blocker", rel, 0, "Eine E-Mail-Adresse der Quelle steht nicht im extrahierten Text"))
        if struktur["tabellen"]:
            ats.append(befund("EX-03", "Warnung", rel, 0, f"{struktur['tabellen']} Tabelle(n): manche ATS lesen Tabellen spaltenweise falsch"))
        if struktur["bilder"]:
            ats.append(befund("EX-03", "Warnung", rel, 0, f"{struktur['bilder']} Bild(er): der Inhalt eines Bildes ist für ein ATS nicht lesbar"))
        if fmt == "pdf":
            seiten_ist = seitenzahl(pfad)
            leer = [i for i, s in enumerate(seiten_roh[:seiten_ist], 1) if not s.strip()] if seiten_ist else []
            if seiten_ist is None:
                luecken["EX-04"].append(f"{datei}: pdfinfo fehlt, die Seitenzahl ist nicht prüfbar")
            else:
                if manifest["ausgabe"].get("seiten") not in (None, seiten_ist):
                    seiten.append(befund("EX-04", "Blocker", rel, 0, f"Seitenzahl {seiten_ist} weicht vom Manifest ({manifest['ausgabe'].get('seiten')}) ab"))
                grenze = manifest["ausgabe"].get("seitenlimit")
                if grenze and seiten_ist > grenze:
                    seiten.append(befund("EX-04", "Blocker", rel, 0, f"{seiten_ist} Seiten, Limit {grenze}"))
                for nummer in leer:
                    seiten.append(befund("EX-04", "Blocker", rel, 0, f"Seite {nummer} ist leer"))
    for name in dateien:  # a file without a manifest is not an export of this toolchain
        if not name.endswith(".manifest.json") and name not in abgedeckt:
            integritaet.append(befund("EX-01", "Blocker", "export/" + name, 0, "Datei ohne gültiges Manifest: Herkunft und Aktualität sind nicht belegt"))
    daten = {"EX-01": integritaet, "EX-02": inhalt, "EX-03": ats, "EX-04": seiten}
    return [ergebnis(i, daten[i], blockiert="; ".join(luecken.get(i, []))) for i in ("EX-01", "EX-02", "EX-03", "EX-04")]


# ---------------------------------------------------------------- the process (PR)

def pruefe_prozess(ctx):
    fehlt = [n for n in PFLICHT if n not in ctx["texte"]]
    pr1 = [befund("PR-01", "Blocker", n, 0, "Pflichtdokument fehlt oder ist nicht lesbar") for n in fehlt]
    luecken = [n for n in ("vorgang.md",) + KONTEXT if n not in ctx["texte"]]
    pr2 = [] if ctx["meta"].get("firma") and ctx["meta"].get("stelle") else [befund("PR-02", "Warnung", "vorgang.md", 0, "`firma` oder `stelle` fehlt in vorgang.md")]
    return [ergebnis("PR-01", pr1), ergebnis("PR-02", pr2, blockiert=("fehlt: " + ", ".join(luecken)) if luecken else "")]


# ---------------------------------------------------------------- semantic verdicts of the model (SEM)

def urteile_laden(pfad):
    """-> (liste, grund). The file is data written by a model: only the fields below are read, nothing in it is an instruction."""
    if not pfad or not os.path.isfile(pfad):
        return None, "keine semantischen Urteile vorhanden (Modell nicht ausgeführt oder nicht verfügbar)"
    try:
        with open(pfad, encoding="utf-8") as handle:
            daten = json.load(handle)
        liste = daten["urteile"]
        if not isinstance(liste, list):
            raise TypeError
    except (OSError, ValueError, KeyError, TypeError):
        return None, f"{os.path.basename(pfad)} ist nicht lesbar oder hat kein gültiges Format"
    return [u for u in liste if isinstance(u, dict)], ""


def pruefe_urteil(ctx, urteil, stand_dokumente):
    """-> (status 'ok'|'pruefen'|'fehler', Text). A verdict counts only when quote and evidence stand literally in the files."""
    check_id, name = urteil.get("check"), urteil.get("dokument")
    wert = urteil.get("ergebnis")
    erlaubt = ("A", "B", "C", "D") if check_id == "SEM-01" else ("ok", "pruefen", "fehler")
    if check_id not in SEM_DOKUMENTE or wert not in erlaubt or not isinstance(name, str):
        return "pruefen", "Urteil hat ein ungültiges Format"
    soll = stand_dokumente if name == "*" else dokument_hashes(ctx["ordner"]).get(name)
    if not soll or urteil.get("dokument_hash") != soll:
        return "pruefen", f"Urteil zu {name} gehört zu einer anderen Version des Dokuments"
    if name != "*":
        zitat = urteil.get("zitat")
        if not isinstance(zitat, str) or not cv.normalise(zitat) or cv.normalise(zitat) not in cv.normalise(ctx["texte"].get(name, "")):
            return "pruefen", f"Das Zitat steht nicht wörtlich in {name}"
    ziel = clip(urteil.get("begruendung") if isinstance(urteil.get("begruendung"), str) else "", 120)
    if wert in ("fehler", "C"):
        return "fehler", f"Widerspruch zur Grundlage oder zum Dokumentsatz: {ziel}"
    if wert in ("pruefen", "B", "D"):
        return "pruefen", f"{'plausibel, aber nicht belegt' if wert == 'B' else 'nicht prüfbar' if wert == 'D' else 'zu prüfen'}: {ziel}"
    if urteil.get("sicherheit") != "hoch":
        return "pruefen", "Das Modell war nicht sicher"
    if check_id == "SEM-01":
        evidenz = urteil.get("evidenz")
        if ctx["grundlage"] is None or not isinstance(evidenz, str) or not cv.normalise(evidenz) \
                or cv.normalise(evidenz) not in cv.normalise(ctx["grundlage"]):
            return "pruefen", "Die Evidenz steht nicht wörtlich in der Datengrundlage"
    return "ok", ""


def pruefe_semantik(ctx, urteile_pfad):
    liste, grund = urteile_laden(urteile_pfad)
    stand_dokumente = dokumente_stand(ctx["ordner"])
    checks = []
    for check_id, ziele in SEM_DOKUMENTE.items():
        if check_id == "SEM-05" and len([n for n in DOC_TYPE if n in ctx["texte"]]) < 2:
            checks.append(ergebnis(check_id, nicht_anwendbar="weniger als zwei Dokumente"))
            continue
        pflicht = [n for n in ziele if n == "*" or n in ctx["texte"]]
        if not pflicht:
            checks.append(ergebnis(check_id, nicht_anwendbar="das zu prüfende Dokument liegt nicht vor"))
            continue
        if check_id == "SEM-01" and ctx["grundlage"] is None:
            checks.append(ergebnis(check_id, blockiert=f"Datengrundlage nicht verfügbar ({ctx['grundlage_grund']})"))
            continue
        if liste is None:
            checks.append(ergebnis(check_id, [befund(check_id, "Prüfung", "*", 0, grund)]))
            continue
        befunde, belegt = [], set()
        for urteil in (u for u in liste if u.get("check") == check_id):
            art, text = pruefe_urteil(ctx, urteil, stand_dokumente)
            name = urteil.get("dokument") if isinstance(urteil.get("dokument"), str) else "?"
            if art == "ok":
                belegt.add(name)
            else:
                befunde.append(befund(check_id, "Blocker" if art == "fehler" else "Prüfung", name, 0, text))
                belegt.add(name)  # a verdict exists; the finding carries the result
        fehlend = [n for n in pflicht if n not in belegt]
        if fehlend:
            befunde.append(befund(check_id, "Prüfung", "*", 0, "kein semantisches Urteil für: " + ", ".join(fehlend)))
        checks.append(ergebnis(check_id, befunde))
    return checks


# ---------------------------------------------------------------- run, report, decisions

def entscheidungen_von(ordner):
    daten = load_json(os.path.join(ordner, ENTSCHEIDUNGEN), {"schema": SCHEMA, "entscheidungen": []})
    liste = daten.get("entscheidungen")
    return liste if isinstance(liste, list) else []


def schluessel(stand, check):
    return digest(stand, check["id"], json.dumps(check["befunde"], sort_keys=True, ensure_ascii=False))


def lauf(ordner, grundlage_pfade=(), konfiguration=None, urteile=None, jetzt=None):
    """Run every check; returns the report (not yet written)."""
    ctx = kontext_laden(ordner, list(grundlage_pfade), konfiguration or os.path.join(gh.DEFAULT_WURZEL, "konfiguration.md"))
    checks = pruefe_regeln(ctx)
    checks += [qs_firma(ctx), qs_kontakt(ctx), qs_zeitangaben(ctx), qs_uebernahme(ctx), qs_floskeln(ctx)]
    checks += pruefe_exporte(ctx)
    checks += pruefe_prozess(ctx)
    checks += pruefe_semantik(ctx, urteile if urteile is not None else os.path.join(ordner, URTEILE))
    for name in ctx["unlesbar"]:
        checks.append({"id": "PR-01", "titel": KATALOG["PR-01"][0], "art": "deterministisch", "status": BLOCKED,
                       "befunde": [], "grund": f"{name} ist nicht lesbar (Kodierung?)"})
    checks.sort(key=lambda c: list(KATALOG).index(c["id"]))
    dokumente, exporte = dokument_hashes(ordner), export_hashes(ordner)
    stand = stand_von(dokumente, exporte, ctx["grundlage_hash"])
    akzeptiert = {e.get("schluessel") for e in entscheidungen_von(ordner) if isinstance(e, dict)}
    for check in checks:
        if check["status"] == REVIEW and schluessel(stand, check) in akzeptiert:
            check["manuell_akzeptiert"] = True
    ergebnis_gesamt = gesamt(checks if (dokumente or exporte) else [])
    zaehler = {s: sum(1 for c in checks if c["status"] == s) for s in STATI}
    return {
        "schema": SCHEMA, "regelwerk": RULES, "erstellt": stamp(jetzt or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)),
        "vorgang": os.path.basename(os.path.normpath(ordner)), "stand": stand, "dokumente_stand": dokumente_stand(ordner), "dokumente": dokumente, "exporte": exporte,
        "grundlage_hash": ctx["grundlage_hash"], "gesamt": ergebnis_gesamt, "freigabefaehig": ergebnis_gesamt in FREIGABEFAEHIG,
        "zusammenfassung": zaehler,
        "semantisch_geprueft": any(c["art"] == "semantisch" and c["status"] in (PASS, WARNING, FAIL) for c in checks),
        "checks": checks,
        "manuell": ["Freigabe des Versandpakets durch die Nutzerin oder den Nutzer (Workflow: versand_freigabe)",
                    "Versand durch die Nutzerin oder den Nutzer selbst; diese Prüfung sendet nichts"],
        "grenzen": list(GRENZEN),
    }


def speichere(ordner, bericht):
    atomic_write(os.path.join(ordner, BERICHT), bericht)
    zeile = {"am": bericht["erstellt"], "stand": bericht["stand"][:12], "gesamt": bericht["gesamt"], "zusammenfassung": bericht["zusammenfassung"]}
    with open(os.path.join(ordner, VERLAUF), "a", encoding="utf-8") as handle:  # counters and a hash prefix only, no document text
        handle.write(json.dumps(zeile, ensure_ascii=False, sort_keys=True) + "\n")


def lade_bericht(ordner):
    try:
        daten = load_json(os.path.join(ordner, BERICHT), None)
    except Refused:
        return None
    return daten


def aktualitaet(ordner, grundlage_hash=None):
    """None when the report is current and may be approved, else (code, message). Used by workflow.py (the gate)."""
    bericht = lade_bericht(ordner)
    if bericht is None:
        return "qualitaet_fehlt", f"{BERICHT} fehlt: erst `qualitaet.py pruefen` ausführen"
    if bericht.get("schema") != SCHEMA or bericht.get("dokumente") != dokument_hashes(ordner) or bericht.get("exporte") != export_hashes(ordner):
        return "qualitaet_veraltet", "Dokumente oder Exporte haben sich seit dem Qualitätsbericht geändert: erneut prüfen"
    if grundlage_hash and bericht.get("grundlage_hash") not in (None, grundlage_hash):
        return "qualitaet_veraltet", "Die Datengrundlage hat sich seit dem Qualitätsbericht geändert: erneut prüfen"
    if bericht.get("gesamt") not in FREIGABEFAEHIG:
        return "qualitaet_nicht_freigabefaehig", f"Der Qualitätsbericht steht auf {bericht.get('gesamt')}: nicht freigabefähig"
    return None


def entscheiden(ordner, check_id, grund, bericht):
    """Record that the user reviewed one NEEDS_REVIEW check of this exact report. FAIL and BLOCKED cannot be accepted."""
    check = next((c for c in bericht["checks"] if c["id"] == check_id), None)
    if check is None or check["status"] != REVIEW:
        raise Refused("nicht_entscheidbar", f"{check_id} steht nicht auf {REVIEW}: nur eine manuelle Prüfung lässt sich bestätigen, FAIL und BLOCKED nicht")
    if not grund.strip():
        raise Refused("grund_fehlt", "Die Entscheidung braucht einen Grund")
    liste = entscheidungen_von(ordner)
    liste.append({"check": check_id, "schluessel": schluessel(bericht["stand"], check), "am": stamp(dt.datetime.now(dt.timezone.utc).replace(microsecond=0)),
                  "von": "nutzer", "grund": clip(grund, 200)})
    atomic_write(os.path.join(ordner, ENTSCHEIDUNGEN), {"schema": SCHEMA, "entscheidungen": liste})


def unbeaufsichtigt():
    return bool(os.environ.get("WORKFLOW_UNBEAUFSICHTIGT") or os.environ.get("STELLENSUCHE_GEPLANT"))


# ---------------------------------------------------------------- command line

def anzeige(bericht):
    kurz = {k: v for k, v in bericht.items() if k not in ("checks", "dokumente", "exporte")}
    kurz["checks"] = [{k: c[k] for k in ("id", "status", "titel", "art", "grund", "manuell_akzeptiert", "befunde") if k in c} for c in bericht["checks"]]
    return kurz


def exit_code(bericht):
    return 0 if bericht["freigabefaehig"] else 1 if bericht["gesamt"] == "BLOCKIERT" else 2


def build_parser():
    parser = argparse.ArgumentParser(description="Quality assurance report of one Vorgang (QS-1 to QS-12).")
    sub = parser.add_subparsers(dest="befehl", required=True)
    for name in ("pruefen", "status", "entscheiden"):
        command = sub.add_parser(name)
        command.add_argument("vorgang")
        if name == "entscheiden":
            command.add_argument("pruefung")
            command.add_argument("--grund", default="")
            command.add_argument("--ja", action="store_true")
        if name != "status":
            command.add_argument("--konfiguration", default=os.path.join(gh.DEFAULT_WURZEL, "konfiguration.md"))
            command.add_argument("--grundlage", action="append", default=[])
            command.add_argument("--urteile")
        if name == "pruefen":
            command.add_argument("--nur-anzeigen", action="store_true", help="write no report")
    sub.add_parser("katalog")
    return parser


def run(args):
    if args.befehl == "katalog":
        print(json.dumps({k: {"titel": t, "art": a} for k, (t, a) in KATALOG.items()}, ensure_ascii=False, indent=2))
        return 0
    ordner = os.path.abspath(args.vorgang)
    if not os.path.isdir(ordner):
        raise Refused("vorgang_fehlt", f"Kein Vorgang-Ordner: {args.vorgang}")
    if args.befehl == "status":
        bericht = lade_bericht(ordner)
        problem = aktualitaet(ordner)
        print(json.dumps({"vorhanden": bericht is not None, "gesamt": (bericht or {}).get("gesamt"), "aktuell": problem is None or problem[0] == "qualitaet_nicht_freigabefaehig",
                          "freigabefaehig": problem is None, "problem": problem[1] if problem else ""}, ensure_ascii=False, indent=2))
        return 0 if problem is None else 2
    if args.befehl == "entscheiden":
        if unbeaufsichtigt():
            raise Refused("nur_interaktiv", "Eine manuelle Bestätigung ist in einer unbeaufsichtigten Sitzung nicht erlaubt")
        if not args.ja:
            raise Refused("entscheidung_nicht_bestaetigt", "Die Bestätigung braucht das ausdrückliche Ja der Nutzerin oder des Nutzers (--ja)")
        bericht = lauf(ordner, args.grundlage, args.konfiguration, args.urteile)
        entscheiden(ordner, args.pruefung, args.grund, bericht)
    bericht = lauf(ordner, args.grundlage, args.konfiguration, args.urteile)
    if args.befehl == "entscheiden" or not args.nur_anzeigen:
        speichere(ordner, bericht)
    print(json.dumps(anzeige(bericht), ensure_ascii=False, indent=2))
    return exit_code(bericht)


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except Refused as error:
        print(json.dumps({"ok": False, "code": error.code, "meldung": error.meldung}, ensure_ascii=False))
        return 3


if __name__ == "__main__":
    sys.exit(main())
