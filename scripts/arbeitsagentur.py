#!/usr/bin/env python3
"""Helper for the interactive search on the Bundesagentur für Arbeit (spec stellensuche ST-21).

It runs no search and contacts nobody: the model calls the tools of the jobsuche MCP server, this script checks what
comes back and does the parts that must be the same every time.

  abfrage       <brief.json|->   Tool arguments of `search_jobs` per term, and the criteria the server cannot enforce.
  pruefen       <antwort.json|-> Check one answer of `search_jobs`: status, normalised Stellen, defects, more pages.
  zusammenfuehren <listen.json|-> Merge the Stellen of several boards into one shortlist (same posting once).

Input is JSON on stdin or in a file; output is JSON. Exit code 0 is a usable answer, 3 a refused input. Standard
library only. A posting's description is never part of the output (ST-9).
"""

import argparse
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import stellensuche as ss  # noqa: E402

BOARD = "arbeitsagentur"
POSTING_URL = "https://www.arbeitsagentur.de/jobsuche/jobdetail/"
MAX_BYTES = 2_000_000
MAX_STELLEN = 100  # the server's own page cap; more is not stored
PLZ_SUFFIX = re.compile(r"\s*\(\d{5}\)\s*$")  # the server writes "Berlin (10115)"; other boards write "Berlin"
REFNR = re.compile(r"[0-9A-Za-z][0-9A-Za-z._-]{3,59}")

STELLE_KEYS = ("titel", "firma", "ort", "remote", "jobtyp", "datum", "board_id", "url", "url_direkt", "signale")

# search_jobs(employment_type): the values the server turns into the API's `arbeitszeit` (lib.rs parse_employment_type).
EMPLOYMENT = {"fulltime": "fulltime", "parttime": "parttime"}

# Answer statuses. The first two are answers; the others are failures and never mean "no matching jobs".
STATUS = ("ok", "ok_ohne_treffer", "nicht_verfuegbar", "verbindung", "blockiert", "authentifizierung", "ungueltig",
          "antwort_ungueltig", "fehler")
FAILURE_WORDS = (  # first match wins; the server returns the error as text, so this is a heuristic (ST-21 rule 6)
    ("authentifizierung", ("401", "unauthorized", "unauthorised", "api key", "api-key", "forbidden key")),
    ("blockiert", ("429", "rate limit", "rate-limit", "too many requests", "403", "forbidden", "captcha")),
    ("ungueltig", ("400", "bad request", "invalid", "ungültig", "unknown field", "invalid params")),
    ("verbindung", ("timeout", "timed out", "connection", "dns", "502", "503", "504", "unreachable", "network")),
    ("nicht_verfuegbar", ("not connected", "no such tool", "unknown tool", "not found: tool", "server not available")),
)


def classify_failure(text):
    low = ss.fold(ss.clean_text(text, 400)).lower() if text else ""
    for status, words in FAILURE_WORDS:
        if any(word in low for word in words):
            return status
    return "fehler"


# ---------------------------------------------------------------- brief -> tool arguments

def build_queries(brief):
    """The `search_jobs` arguments per term and the criteria the server cannot enforce (ST-21 rule 3)."""
    # The terms follow the rules of every brief (ST-2 rule 3); the board list is checked by the skill, not here.
    brief = ss.validate_brief({**brief, "boards": ["indeed"]} if isinstance(brief, dict) else brief)
    common = {"page": 1, "page_size": brief["ergebnisse_pro_board"], "published_since_days": brief["max_alter_tage"]}
    unsupported, employment = [], []
    if brief["ort"]:
        common["location"] = brief["ort"]
        if brief["radius_km"] is not None:
            common["radius_km"] = brief["radius_km"]
    elif brief["radius_km"] is not None:
        unsupported.append({"kriterium": "radius_km", "grund": "Ohne Ort gibt es keinen Mittelpunkt; der Radius entfällt"})
    if brief["jobtyp"] in EMPLOYMENT:
        employment.append(EMPLOYMENT[brief["jobtyp"]])
    elif brief["jobtyp"]:
        unsupported.append({"kriterium": "jobtyp", "grund": f"„{brief['jobtyp']}“ kann der Server nicht filtern "
                            "(`contract_type` nimmt er an, wendet ihn aber nicht an); Prüfung erst an der Stelle selbst"})
    if brief["remote"] is True:
        employment.append("home_office")  # Heim-/Telearbeit of the BA: close to remote, not identical
    elif brief["remote"] is False:
        unsupported.append({"kriterium": "remote", "grund": "„nicht remote“ kann die Suche nicht erzwingen; "
                            "die Anzeige nennt es nicht in der Trefferliste"})
    if employment:
        common["employment_type"] = employment
    queries = [{"job_title": term["text"], **common} for term in brief["begriffe"]]
    return {"ok": True, "aufrufe": queries, "nicht_unterstuetzt": unsupported,
            "hinweis": "Die Arbeitgeber- und Branchensuche des Servers wird nicht genutzt; Begriffe nur als job_title"}


# ---------------------------------------------------------------- answer -> checked Stellen

def stelle_from_job(job):
    """One `search_jobs` job to the stored fields of a Stelle, or raise ss.Defect."""
    if not isinstance(job, dict):
        raise ss.Defect("kein Objekt")
    refnr = ss.clean_text(job.get("reference_number"), 60)
    if not REFNR.fullmatch(refnr):
        raise ss.Defect("Referenznummer fehlt oder hat ein unerwartetes Format")
    raw = {"id": refnr, "title": job.get("title"), "company": job.get("employer"), "location": PLZ_SUFFIX.sub("", ss.clean_text(job.get("location"), 120)),
           "date_posted": job.get("published_date"), "job_url": POSTING_URL + refnr,
           "job_url_direct": job.get("external_url")}
    stelle = ss.normalise(raw)
    stelle["board"] = BOARD
    return stelle


def check_answer(answer):
    """Classify one tool answer (the object `search_jobs` returned, or {"fehler": "<text>"}) (ST-21 rule 6)."""
    if not isinstance(answer, dict):
        return {"ok": False, "status": "antwort_ungueltig", "grund": "Die Antwort ist kein Objekt", "stellen": []}
    if answer.get("fehler"):
        status = classify_failure(str(answer["fehler"]))
        return {"ok": False, "status": status, "grund": ss.redact(answer["fehler"]), "stellen": []}
    jobs = answer.get("jobs")
    if not isinstance(jobs, list):  # a missing list is a failure, not an empty result
        return {"ok": False, "status": "antwort_ungueltig", "grund": "Die Antwort enthält keine Liste `jobs`", "stellen": []}
    total = answer.get("total_results")
    total = total if isinstance(total, int) and not isinstance(total, bool) and total >= 0 else None
    stellen, defects, seen, repeated = [], [], set(), 0
    for number, job in enumerate(jobs[:MAX_STELLEN]):
        try:
            stelle = stelle_from_job(job)
        except ss.Defect as error:
            defects.append({"nr": number, "grund": str(error)})
            continue
        if stelle["board_id"] in seen:
            repeated += 1
            continue
        seen.add(stelle["board_id"])
        stellen.append(stelle)
    page = answer.get("current_page") if isinstance(answer.get("current_page"), int) else 1
    page_size = answer.get("page_size") if isinstance(answer.get("page_size"), int) else None
    more = bool(total and page_size and total > page * page_size)
    if not stellen and not defects:
        status = "ok_ohne_treffer" if not jobs and total in (0, None) else "antwort_ungueltig"
    elif not stellen:
        status = "antwort_ungueltig"
    else:
        status = "ok"
    result = {"ok": status in ("ok", "ok_ohne_treffer"), "status": status, "gesamt": total, "seite": page,
              "weitere_seiten": more, "stellen": stellen, "defekt": len(defects), "defekte": defects[:10],
              "doppelt_in_antwort": repeated, "abgeschnitten": max(0, len(jobs) - MAX_STELLEN)}
    if status == "antwort_ungueltig":
        result["grund"] = "Keine Anzeige der Antwort war lesbar" if jobs else "Trefferzahl und Liste passen nicht zusammen"
    if status == "ok" and total is not None and total > len(jobs) and not more:
        result.setdefault("hinweise", []).append("Die Trefferzahl ist größer als die gelieferte Liste")
    return result


# ---------------------------------------------------------------- merge across boards

def merge_lists(lists):
    """One shortlist from the Stellen of several boards (ST-4, ST-21 rule 5).

    The same posting is a shared identity key (board id, URL) or the same firm, title and place on another board within
    `ss.SAME_POSTING_DAYS`. The same triple that does not fit this stays two entries marked as a possible duplicate;
    a similar title alone merges nothing.
    """
    merged = []
    for item in lists:
        board = ss.clean_text(item.get("board"), 30).lower()
        if not board:
            raise ss.Refused("liste_ungueltig", "Jede Liste braucht den Namen ihres Boards")
        records = item.get("stellen")
        if records is None:
            try:
                records = [ss.normalise(raw) for raw in item.get("ergebnisse", [])]
            except ss.Defect as error:
                raise ss.Refused("liste_ungueltig", f"Ein Ergebnis von {board} ist unbrauchbar: {error}") from error
        if not isinstance(records, list) or not all(isinstance(s, dict) and set(STELLE_KEYS) <= set(s) for s in records):
            raise ss.Refused("liste_ungueltig", f"Die Stellen von {board} sind nicht in der gespeicherten Form")
        for stelle in records:
            keys = ss.identity_keys(stelle, board)
            source = {"board": board, "url": stelle["url"], "url_direkt": stelle["url_direkt"], "board_id": stelle["board_id"]}
            target = next((m for m in merged if set(keys) & set(m["schluessel"])), None)
            if target is None:
                same = [m for m in merged if ss.triple(stelle) and ss.triple(m) == ss.triple(stelle)]
                target = next((m for m in same if board not in {s["board"] for s in m["boards"]}
                               and ss.days_apart(m["datum"], stelle["datum"]) <= ss.SAME_POSTING_DAYS), None)
                if target is None:
                    entry = {key: stelle[key] for key in STELLE_KEYS[:6] + ("signale",)}
                    entry.update(schluessel=[], boards=[], moegliches_duplikat=[m["nr"] for m in same], nr=len(merged) + 1)
                    for other in same:
                        other["moegliches_duplikat"].append(entry["nr"])
                    merged.append(entry)
                    target = entry
            target["schluessel"] = sorted(set(target["schluessel"]) | set(keys))
            if source not in target["boards"]:
                target["boards"].append(source)
            for key in ("remote", "jobtyp", "datum", "firma", "ort"):
                if ss.blank(target[key]) and not ss.blank(stelle[key]):
                    target[key] = stelle[key]
            target["signale"] = sorted(set(target["signale"]) | set(stelle["signale"]))
    for entry in merged:
        entry["moegliches_duplikat"] = sorted(set(entry["moegliches_duplikat"]))
        del entry["schluessel"]
    return {"ok": True, "stellen": merged, "anzahl": len(merged)}


# ---------------------------------------------------------------- command line

def read_json(source):
    if source == "-":
        data = sys.stdin.read(MAX_BYTES + 1)
    else:
        with open(source, encoding="utf-8") as handle:
            data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ss.Refused("eingabe_zu_gross", f"Die Eingabe ist größer als {MAX_BYTES} Zeichen")
    try:
        return json.loads(data)
    except ValueError as error:
        raise ss.Refused("eingabe_kein_json", f"Die Eingabe ist kein JSON: {error}") from error


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="befehl", required=True)
    for name in ("abfrage", "pruefen", "zusammenfuehren"):
        sub.add_parser(name).add_argument("datei", nargs="?", default="-", help="JSON file, or - for stdin")
    return parser


def main(argv):
    args = build_parser().parse_args(argv[1:])
    try:
        data = read_json(args.datei)
        if args.befehl == "abfrage":
            result = build_queries(data)
        elif args.befehl == "pruefen":
            result = check_answer(data)
        else:
            if not isinstance(data, dict) or not isinstance(data.get("listen"), list):
                raise ss.Refused("liste_ungueltig", 'Erwartet {"listen": [{"board": …, "stellen": […]}]}')
            result = merge_lists(data["listen"])
    except ss.Refused as error:
        print(json.dumps({"ok": False, "code": error.code, "meldung": error.meldung}, ensure_ascii=False))
        return 3
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
