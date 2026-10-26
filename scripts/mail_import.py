#!/usr/bin/env python3
"""Local import of saved e-mails (.eml) into the list that `kommunikation.py verarbeiten` reads (spec mail-verwaltung MV-33, R-02).

This is the one provider that ships: a folder of `.eml` files the user saved from a mailbox. It reads files only. It opens no connection, uses no
credential and sends nothing; a connector to a mailbox (Gmail, IMAP) is not part of the plugin and would only have to write the same list.

  mail_import.py [--konfiguration PFAD] [--protokoll] PFAD [PFAD …]     PFAD is an .eml file or a folder of them
  mail_import.py … | kommunikation.py verarbeiten

Output (stdout): the JSON list of messages of MV-19 (`id`, `thread_id`, `von`, `an`, `betreff`, `datum`, `text`, `anhaenge`, `anhaenge_gesperrt`,
`kanal` = `eml`, `quelle_ref`). The report (stderr, one JSON line) lists the files that could not be read, with a class and never with content.
With `--protokoll` the report is also kept in `<wurzel>/kommunikation/importprotokoll.json` (the last 50 runs).

Rules: Message-ID is the id when it has the form MV-19 allows; otherwise the id is `fp-` plus a hash of sender, date, subject and the start of the text, so
the same file imported twice gives the same id. A message without a valid Date header is not imported (the date is never guessed). The text is the
`text/plain` part (an HTML-only mail is stripped of tags and marked). Attachments are never opened, never saved and never decoded: only their names
are read, and a name with a risky extension (programs, scripts, archives, macro documents, HTML) or an attachment above 10 MB is listed in
`anhaenge_gesperrt` instead. Limits: 200 files per run, 2,000,000 bytes per file. Exit code 0 ok, 2 some files not imported, 3 refused, 1 blocker.
Standard library only.
"""

import argparse
import datetime as dt
import email
import email.policy
import email.utils
import hashlib
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import stellensuche as ss  # noqa: E402
from stellensuche import Blocker, Refused, atomic_write, clean_text, load_json, stamp  # noqa: E402

MAX_DATEIEN = 200
MAX_BYTES = 2_000_000
MAX_ANHANG = 10_000_000
TEXT_MAX = 6000
PROTOKOLL_MAX = 50
ID_FORM = re.compile(r"[A-Za-z0-9_.:@-]{1,128}")
GESPERRT = {"exe", "bat", "cmd", "com", "scr", "msi", "dll", "js", "jse", "vbs", "vbe", "wsf", "ps1", "sh", "jar", "apk", "lnk", "iso", "img", "hta", "reg",
            "zip", "rar", "7z", "gz", "tar", "docm", "xlsm", "pptm", "dotm", "html", "htm", "svg", "xhtml"}


def sichere_id(wert):
    wert = re.sub(r"[<>\s]", "", wert or "")
    return wert if ID_FORM.fullmatch(wert) else ""


def fingerabdruck(von, datum, betreff, text):
    return "fp-" + hashlib.sha256("\x1f".join((von, datum, betreff, text[:200])).encode("utf-8")).hexdigest()[:24]


def text_von(nachricht):
    """-> (text, nur_html). Prefers text/plain; HTML is reduced to its text. Attachments are skipped without being decoded."""
    teil = nachricht.get_body(preferencelist=("plain",))
    nur_html = False
    if teil is None:
        teil = nachricht.get_body(preferencelist=("html",))
        nur_html = teil is not None
    if teil is None:
        return "", False
    try:
        inhalt = teil.get_content()
    except (LookupError, UnicodeError, ValueError):
        return "", nur_html
    if nur_html:
        inhalt = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", " ", inhalt)))
    return clean_text(inhalt, TEXT_MAX), nur_html


def anhaenge_von(nachricht):
    """-> (names, blocked names). Only the file name and the declared size are looked at; the content is neither decoded nor stored."""
    frei, gesperrt = [], []
    for teil in nachricht.iter_attachments():
        name = clean_text(teil.get_filename() or "ohne-name", 80)
        endung = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        groesse = len(teil.get_payload()) * 3 // 4 if isinstance(teil.get_payload(), str) else 0  # base64 text length, no decoding
        (gesperrt if endung in GESPERRT or groesse > MAX_ANHANG else frei).append(name)
    return frei[:10], gesperrt[:10]


def lies_eml(pfad):
    """-> message dict. Raises Refused with a class for a file that cannot be imported."""
    try:
        if os.path.getsize(pfad) > MAX_BYTES:
            raise Refused("zu_gross", f"größer als {MAX_BYTES} Bytes")
        with open(pfad, "rb") as handle:
            nachricht = email.message_from_binary_file(handle, policy=email.policy.default)
    except Refused:
        raise
    except (OSError, ValueError, LookupError) as error:
        raise Refused("nicht_lesbar", type(error).__name__)
    datum_roh = str(nachricht.get("Date", ""))
    try:
        datum = email.utils.parsedate_to_datetime(datum_roh).date().isoformat()
    except (TypeError, ValueError, IndexError):
        raise Refused("datum_fehlt", "kein lesbarer Date-Header: das Datum wird nicht geschätzt")
    von = clean_text(str(nachricht.get("From", "")), 200)
    betreff = clean_text(str(nachricht.get("Subject", "")), 300)
    text, nur_html = text_von(nachricht)
    if not (text or betreff):
        raise Refused("kein_text", "weder Text noch Betreff")
    frei, gesperrt = anhaenge_von(nachricht)
    mid = sichere_id(str(nachricht.get("Message-ID", "")))
    nachricht_id = mid or fingerabdruck(von, datum, betreff, text)
    referenzen = str(nachricht.get("References", "")).split()
    thread = sichere_id(referenzen[0] if referenzen else str(nachricht.get("In-Reply-To", ""))) or nachricht_id
    return {"id": nachricht_id, "thread_id": thread, "von": von, "an": clean_text(str(nachricht.get("To", "")).split(",")[0], 200), "betreff": betreff,
            "datum": datum, "text": text, "anhaenge": frei, "anhaenge_gesperrt": gesperrt, "kanal": "eml",
            "quelle_ref": clean_text(os.path.basename(pfad), 80), "id_quelle": "message-id" if mid else "fingerabdruck", "nur_html": nur_html}


def sammle(pfade):
    dateien = []
    for pfad in pfade:
        if os.path.isdir(pfad):
            dateien += [os.path.join(pfad, n) for n in sorted(os.listdir(pfad)) if n.lower().endswith(".eml")]
        elif os.path.isfile(pfad):
            dateien.append(pfad)
        else:
            raise Refused("quelle_nicht_lesbar", f"{ss.redact(os.path.basename(pfad), 60)} ist weder Datei noch Ordner")
    if len(dateien) > MAX_DATEIEN:
        raise Refused("zu_viele_dateien", f"{len(dateien)} Dateien; höchstens {MAX_DATEIEN} je Lauf")
    return dateien


def importiere(pfade):
    """-> (messages, report). One bad file is reported and does not stop the others; the same message twice in a run is kept once."""
    nachrichten, fehler, gesehen, doppelt = [], [], set(), 0
    for pfad in sammle(pfade):
        try:
            n = lies_eml(pfad)
        except Refused as error:
            fehler.append({"datei": clean_text(os.path.basename(pfad), 80), "klasse": error.code, "grund": error.meldung})
            continue
        if n["id"] in gesehen:
            doppelt += 1
            continue
        gesehen.add(n["id"])
        nachrichten.append(n)
    bericht = {"gelesen": len(nachrichten), "doppelt_im_lauf": doppelt, "fehler": fehler,
               "ohne_message_id": sum(1 for n in nachrichten if n["id_quelle"] == "fingerabdruck"),
               "mit_gesperrtem_anhang": sum(1 for n in nachrichten if n["anhaenge_gesperrt"])}
    return nachrichten, bericht


def protokolliere(w, bericht, jetzt):
    pfad = os.path.join(w, "kommunikation", "importprotokoll.json")
    daten = load_json(pfad, {"version": 1, "laeufe": []})
    if not isinstance(daten.get("laeufe"), list):
        raise Refused("speicher_ungueltig", "kommunikation/importprotokoll.json hat kein bekanntes Format")
    daten["laeufe"] = (daten["laeufe"] + [{"am": stamp(jetzt), **bericht}])[-PROTOKOLL_MAX:]
    atomic_write(pfad, daten)


def main(argv):
    parser = argparse.ArgumentParser(description="Import saved .eml files for kommunikation.py verarbeiten.")
    parser.add_argument("--konfiguration", default=os.path.join(ss.DEFAULT_WURZEL, "konfiguration.md"))
    parser.add_argument("--protokoll", action="store_true", help="keep the report in kommunikation/importprotokoll.json")
    parser.add_argument("pfade", nargs="+")
    args = parser.parse_args(argv[1:])
    try:
        nachrichten, bericht = importiere(args.pfade)
        if args.protokoll:
            protokolliere(ss.find_wurzel(args.konfiguration), bericht, dt.datetime.now(dt.timezone.utc).replace(microsecond=0))
    except Blocker as error:
        print(f"Blocker: {error}", file=sys.stderr)
        return 1
    except Refused as error:
        print(json.dumps({"ok": False, "code": error.code, "meldung": error.meldung}, ensure_ascii=False), file=sys.stderr)
        return 3
    print(json.dumps(nachrichten, ensure_ascii=False, indent=2))
    print(json.dumps({"importbericht": bericht}, ensure_ascii=False), file=sys.stderr)
    return 2 if bericht["fehler"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
