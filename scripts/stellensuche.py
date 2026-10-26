#!/usr/bin/env python3
"""Deterministic core of the recurring job search (spec stellensuche ST-13 to ST-20).

The model runs the searches (the JobSpy MCP server is reachable only from a Claude session) and shows
the results. Everything that must hold every time is done here: the Suchauftrag and its approval,
the limits, the run log with its lock, the identity and de-duplication of postings across runs,
the Veto pre-filter on structured fields, the Warteschlange, and the hand-off state.

All state lives below `<wurzel>/suche/`:
  auftraege/<id>.json   one Suchauftrag with its approval and its last runs
  warteschlange.json    one entry per identified posting, with the decision of the user
  warteschlange.md      readable overview of both, rewritten after every change
The script also writes the readable overview `suche/warteschlange.md` (a derivation, ST-19 rule 5) and nothing else. It never creates a Vorgang, never sends anything and never calls a
network service.

Usage: stellensuche.py [--konfiguration PFAD] [--jetzt ISO] [--text] <befehl> ...
Commands: wurzel, anlegen, aendern, pruefen, freigeben, pausieren, fortsetzen, beenden, auftraege, zeige,
faellig, lauf-start, board-ergebnis, lauf-ende, nachtragen, warteschlange, entscheiden, aenderung-gesehen, duplikat,
uebergabe, uebergabe-fertig, uebergabe-fehler.
Output is one JSON object. Exit code 0 ok, 3 refused (`code` and `meldung` say why), 1 blocker, 2 usage.
Standard library only.
"""

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import unicodedata

try:
    import fcntl
except ImportError:  # not available on Windows: commands then run without the file lock
    fcntl = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import posting_url  # noqa: E402
from grundlage_hash import DEFAULT_WURZEL, inside_plugin_repo, read_frontmatter, resolve  # noqa: E402

BOARDS = ("indeed", "glassdoor", "bayt", "naukri", "bdjobs", "hellowork", "zip_recruiter")
DEFAULT_BOARDS = ["indeed", "glassdoor"]
MAX_BOARDS = 3
MAX_RESULTS = 20
MAX_TERMS = 8
JOBTYPES = ("fulltime", "parttime", "internship", "contract")
JOBTYPE_WORDS = {"vollzeit": "fulltime", "teilzeit": "parttime", "praktikum": "internship", "vertrag": "contract"}
EXCLUDE_FIELDS = ("titel", "ort", "remote", "jobtyp")
DECISIONS = ("offen", "zurückgestellt", "abgelehnt", "übernommen")
BOARD_STATUS = ("ok", "nicht_verfuegbar", "verbindung", "blockiert", "fehler")
BOARD_CODES = {
    "nicht_verfuegbar": "suchdienst_nicht_verfuegbar",
    "verbindung": "verbindung_fehlgeschlagen",
    "blockiert": "board_blockiert",
    "fehler": "board_fehler",
}
SIGNALS = ("vermittler",)
MISSED_RUNS = 3
LOCK_MINUTES = 120
LOCK_GRACE_SECONDS = 60
LOCK_WAIT_SECONDS = 30
WINDOW_DAYS = 7
KEEP_RUNS = 30
KEEP_LOG = 50
KEEP_SEEN = 20
RETENTION_DAYS = 90
DEFAULT_PLAN = {"intervall_tage": 7, "laeufe_pro_woche": 3, "wiederholung_stunden": 24, "max_fehler_in_folge": 3}
SAME_POSTING_DAYS = 3
SPEC_KEYS = {"name", "zweck", "brief", "ausschluesse", "plan", "wunschprofil"}


class Refused(Exception):
    def __init__(self, code, meldung):
        super().__init__(meldung)
        self.code = code
        self.meldung = meldung


class Blocker(Exception):
    pass


class Defect(Exception):
    pass


# ---------------------------------------------------------------- small helpers

def stamp(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(value):
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def clean_text(value, limit):
    if value is None or isinstance(value, (dict, list)):
        return ""
    text = "".join(ch if ch.isprintable() else " " for ch in str(value))
    return " ".join(text.split())[:limit]


SECRET = re.compile(
    r"(?i)(bearer\s+\S+|(?:token|api[_-]?key|passwort|password|secret|authorization)\s*[=:]\s*\S+"
    r"|\bsk-[A-Za-z0-9_-]{8,}|://[^/\s:@]+:[^@\s]+@)"
)


def redact(value, limit=200):
    """Short, single-line text for a log: no credentials, no long external content (ST-17 rule 4)."""
    return SECRET.sub("[entfernt]", clean_text(value, 2000))[:limit]


def fold(text):
    text = unicodedata.normalize("NFKD", text.lower().replace("ß", "ss"))
    return "".join(ch for ch in text if not unicodedata.combining(ch))


GENDER = re.compile(r"\(?\b[mwfdx*]\s*[/|]\s*[mwfdx*](\s*[/|]\s*[mwfdx*])?\b\)?")


def norm(value):
    text = GENDER.sub(" ", fold(clean_text(value, 300)))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def slug(text):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", fold(text))).strip("-")[:40] or "suche"


def digest(*parts):
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def canonical_url(url):
    """Identity form of a posting URL: no tracking, no fragment, no `www.`, sorted query."""
    parts = posting_url.urlsplit(posting_url.clean(url.strip()))
    host = (parts.hostname or "").lower()
    host = host[4:] if host.startswith("www.") else host
    query = "&".join(sorted(segment for segment in parts.query.split("&") if segment))
    return f"{host}{parts.path.rstrip('/') or '/'}" + (f"?{query}" if query else "")


def atomic_write(path, data):
    directory = os.path.dirname(path)
    temp = None
    try:
        os.makedirs(directory, exist_ok=True)
        handle, temp = tempfile.mkstemp(dir=directory, prefix=".tmp-")
        with os.fdopen(handle, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2, sort_keys=True)
            out.write("\n")
        os.replace(temp, path)
    except OSError as error:
        if temp and os.path.exists(temp):
            os.unlink(temp)
        raise Refused("speichern_fehlgeschlagen", f"Speichern fehlgeschlagen: {redact(error)}")


def load_json(path, default):
    if not os.path.isfile(path):
        return default
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        raise Refused("speichern_fehlgeschlagen", f"{os.path.basename(path)} ist nicht lesbar: {redact(error)}")
    if not isinstance(data, dict):
        raise Refused("speichern_fehlgeschlagen", f"{os.path.basename(path)} hat kein gültiges Format")
    return data


# ---------------------------------------------------------------- Wurzel and storage

def find_wurzel(konfiguration):
    config = read_frontmatter(konfiguration)
    wurzel = resolve(os.path.expanduser(config.get("wurzel") or DEFAULT_WURZEL))
    if inside_plugin_repo(wurzel):
        raise Blocker(f"Der Pfad liegt im Plugin-Repository ({wurzel}). Lege die Wurzel außerhalb ab (LS-2.4).")
    return wurzel


def auftrag_path(wurzel, auftrag_id):
    if not re.fullmatch(r"a-[a-z0-9-]{1,40}", auftrag_id):
        raise Refused("auftrag_unbekannt", f"Ungültige Auftrags-ID: {redact(auftrag_id, 60)}")
    return os.path.join(wurzel, "suche", "auftraege", auftrag_id + ".json")


AUFTRAG_KEYS = {"id", "name", "status", "brief", "plan", "ausschluesse", "laeufe", "fehler_in_folge", "lauf_zaehler"}


def check_auftrag(data, name):
    missing = sorted(AUFTRAG_KEYS - set(data))
    if missing:
        raise Refused("speichern_fehlgeschlagen", f"{name} ist unvollständig (es fehlt: {', '.join(missing)})")
    return data


def load_auftrag(wurzel, auftrag_id):
    path = auftrag_path(wurzel, auftrag_id)
    if not os.path.isfile(path):
        raise Refused("auftrag_unbekannt", f"Kein Suchauftrag {auftrag_id}")
    return check_auftrag(load_json(path, {}), os.path.basename(path))


def save_auftrag(wurzel, auftrag):
    atomic_write(auftrag_path(wurzel, auftrag["id"]), auftrag)


def all_auftraege(wurzel, defects=None):
    """All Suchaufträge; an unreadable file is skipped and, when `defects` is a list, reported there."""
    directory = os.path.join(wurzel, "suche", "auftraege")
    found = []
    for name in sorted(os.listdir(directory)) if os.path.isdir(directory) else []:
        if not name.endswith(".json"):
            continue
        try:
            found.append(check_auftrag(load_json(os.path.join(directory, name), {}), name))
        except Refused as error:
            if defects is not None:
                defects.append({"datei": name, "meldung": error.meldung})
    return found


def queue_path(wurzel):
    return os.path.join(wurzel, "suche", "warteschlange.json")


def load_queue(wurzel):
    queue = load_json(queue_path(wurzel), {"version": 1, "stellen": {}})
    queue.setdefault("stellen", {})
    return queue


def wunschprofil_hash(wurzel):
    path = os.path.join(wurzel, "wunschprofil.md")
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


# ---------------------------------------------------------------- Suchauftrag: validation

def bounded_int(value, low, high):
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def validate_brief(brief):
    """Return the brief in canonical form or raise Refused. Unknown keys are refused (ST-13 rule 2)."""
    known = {"begriffe", "ort", "radius_km", "remote", "jobtyp", "max_alter_tage", "boards", "ergebnisse_pro_board"}
    if not isinstance(brief, dict):
        raise Refused("suchauftrag_ungueltig", "Suchbrief fehlt")
    if set(brief) - known:
        raise Refused("suchauftrag_ungueltig", "Der Suchbrief enthält unbekannte Felder: " + ", ".join(sorted(set(brief) - known)))
    terms = brief.get("begriffe")
    if not isinstance(terms, list) or not 1 <= len(terms) <= MAX_TERMS:
        raise Refused("suchauftrag_ungueltig", f"Der Suchbrief braucht 1 bis {MAX_TERMS} Suchbegriffe")
    checked = []
    for term in terms:
        term = term if isinstance(term, dict) else {}
        text, source = clean_text(term.get("text"), 200), clean_text(term.get("quelle"), 120)
        if not text or len(text) > 60 or len(text.split()) > 6 or "@" in text or "://" in text:
            raise Refused("suchauftrag_ungueltig", f"„{text[:40]}“ ist kein Suchbegriff (höchstens 6 Wörter, 60 Zeichen; ST-2 Regel 3)")
        if not source:
            raise Refused("suchauftrag_ungueltig", f"Der Suchbegriff „{text}“ nennt keine Quelle (ST-2 Regel 4)")
        checked.append({"text": text, "quelle": source})
    boards = brief.get("boards") or list(DEFAULT_BOARDS)
    if not isinstance(boards, list):
        raise Refused("suchauftrag_ungueltig", "Boards müssen eine Liste sein")
    boards = [clean_text(board, 30).lower() for board in boards]
    if "linkedin" in boards:
        raise Refused("suchauftrag_ungueltig", "LinkedIn wird nie über JobSpy durchsucht (RC-5.8 Regel 3)")
    if not boards or len(set(boards)) != len(boards) or any(b not in BOARDS for b in boards) or len(boards) > MAX_BOARDS:
        raise Refused("suchauftrag_ungueltig", f"Erlaubt sind höchstens {MAX_BOARDS} verschiedene Boards aus {', '.join(BOARDS)}")
    age, results, radius = brief.get("max_alter_tage", 14), brief.get("ergebnisse_pro_board", MAX_RESULTS), brief.get("radius_km")
    if not bounded_int(age, 1, 60):
        raise Refused("suchauftrag_ungueltig", "max_alter_tage muss zwischen 1 und 60 liegen")
    if not bounded_int(results, 1, MAX_RESULTS):
        raise Refused("suchauftrag_ungueltig", f"ergebnisse_pro_board muss zwischen 1 und {MAX_RESULTS} liegen (ST-3 Regel 3)")
    if radius is not None and not bounded_int(radius, 0, 200):
        raise Refused("suchauftrag_ungueltig", "radius_km muss zwischen 0 und 200 liegen")
    remote, jobtyp = brief.get("remote"), brief.get("jobtyp")
    if remote is not None and not isinstance(remote, bool):
        raise Refused("suchauftrag_ungueltig", "remote ist true, false oder leer")
    if jobtyp is not None and jobtyp not in JOBTYPES:
        raise Refused("suchauftrag_ungueltig", f"jobtyp ist einer von {', '.join(JOBTYPES)}")
    return {"begriffe": checked, "ort": clean_text(brief.get("ort"), 80), "radius_km": radius, "remote": remote,
            "jobtyp": jobtyp, "max_alter_tage": age, "boards": boards, "ergebnisse_pro_board": results}


def validate_plan(plan):
    if plan is not None and not isinstance(plan, dict):
        raise Refused("suchauftrag_ungueltig", "Der Plan ist ein Objekt mit intervall_tage, laeufe_pro_woche, …")
    plan = {**DEFAULT_PLAN, **(plan or {})}
    if set(plan) - set(DEFAULT_PLAN):
        raise Refused("suchauftrag_ungueltig", "Unbekannte Felder im Plan: " + ", ".join(sorted(set(plan) - set(DEFAULT_PLAN))))
    bounds = {"intervall_tage": (1, 90), "laeufe_pro_woche": (1, 7), "wiederholung_stunden": (1, 168), "max_fehler_in_folge": (1, 5)}
    for key, (low, high) in bounds.items():
        if not bounded_int(plan[key], low, high):
            raise Refused("suchauftrag_ungueltig", f"{key} muss zwischen {low} und {high} liegen")
    return plan


def validate_excludes(excludes):
    checked = []
    for item in excludes or []:
        item = item if isinstance(item, dict) else {}
        field, value, source = item.get("feld"), clean_text(item.get("wert"), 80), clean_text(item.get("quelle"), 120)
        if field not in EXCLUDE_FIELDS or not value or not source:
            raise Refused("suchauftrag_ungueltig", f"Ein Ausschluss braucht feld ({', '.join(EXCLUDE_FIELDS)}), wert und quelle")
        if field == "remote" and value not in ("ja", "nein"):
            raise Refused("suchauftrag_ungueltig", "Ausschluss auf remote hat den Wert ja oder nein")
        if field == "jobtyp":  # the boards report English tokens; accept the German words the user types
            value = JOBTYPE_WORDS.get(fold(value), value)
            if value not in JOBTYPES:
                raise Refused("suchauftrag_ungueltig", f"Ausschluss auf jobtyp hat einen Wert aus {', '.join(JOBTYPES)} "
                                                       f"(oder {', '.join(JOBTYPE_WORDS)})")
        checked.append({"feld": field, "wert": value, "quelle": source})
    return checked


def material_hash(auftrag):
    """Hash of everything that leaves the machine or sets how often it does (ST-14 rule 3)."""
    return digest(json.dumps({"brief": auftrag["brief"], "plan": auftrag["plan"], "abfrage": "je_begriff"},
                             sort_keys=True, ensure_ascii=True))


def check_wunschprofil(wurzel, wanted):
    if not wanted:
        return ""
    if read_frontmatter(os.path.join(wurzel, "wunschprofil.md")).get("bestaetigt") != "ja":
        raise Refused("suchauftrag_ungueltig", "Das Wunschprofil fehlt oder ist nicht bestätigt (bestaetigt: ja; ST-2 Regel 1)")
    return wunschprofil_hash(wurzel)


# ---------------------------------------------------------------- Suchauftrag: lifecycle

def create_auftrag(wurzel, spec, now):
    if not isinstance(spec, dict) or set(spec) - SPEC_KEYS:
        raise Refused("suchauftrag_ungueltig", "Erlaubt sind " + ", ".join(sorted(SPEC_KEYS)))
    name = clean_text(spec.get("name"), 80)
    if not name:
        raise Refused("suchauftrag_ungueltig", "Der Suchauftrag braucht einen Namen")
    auftrag_id = "a-" + slug(name)
    if os.path.exists(auftrag_path(wurzel, auftrag_id)):
        raise Refused("auftrag_existiert", f"Der Suchauftrag {auftrag_id} besteht schon")
    wanted = bool(spec.get("wunschprofil"))
    auftrag = {
        "id": auftrag_id, "name": name, "zweck": clean_text(spec.get("zweck"), 300), "status": "entwurf",
        "brief": validate_brief(spec.get("brief")), "ausschluesse": validate_excludes(spec.get("ausschluesse")),
        "plan": validate_plan(spec.get("plan")), "wunschprofil": wanted,
        "erstellt": stamp(now), "geaendert": stamp(now), "freigabe": None,
        "letzter_versuch": None, "letzter_erfolg": None, "fehler_in_folge": 0, "lauf_zaehler": 0,
        "letzter_lauf": None, "fehler": None, "laeufe": [],
    }
    check_wunschprofil(wurzel, wanted)
    save_auftrag(wurzel, auftrag)
    return auftrag


def change_auftrag(wurzel, auftrag_id, patch, now):
    auftrag = load_auftrag(wurzel, auftrag_id)
    if auftrag["status"] == "beendet":
        raise Refused("beendet", "Ein beendeter Suchauftrag wird nicht geändert; lege einen neuen an")
    if not isinstance(patch, dict) or set(patch) - SPEC_KEYS:
        raise Refused("suchauftrag_ungueltig", "Erlaubt sind " + ", ".join(sorted(SPEC_KEYS)))
    before = material_hash(auftrag)
    if "name" in patch:
        auftrag["name"] = clean_text(patch["name"], 80) or auftrag["name"]
    if "zweck" in patch:
        auftrag["zweck"] = clean_text(patch["zweck"], 300)
    if "brief" in patch:
        auftrag["brief"] = validate_brief({**auftrag["brief"], **(patch["brief"] if isinstance(patch["brief"], dict) else {})})
    if "plan" in patch:
        auftrag["plan"] = validate_plan({**auftrag["plan"], **(patch["plan"] if isinstance(patch["plan"], dict) else {})})
    if "ausschluesse" in patch:
        auftrag["ausschluesse"] = validate_excludes(patch["ausschluesse"])
    if "wunschprofil" in patch:
        auftrag["wunschprofil"] = bool(patch["wunschprofil"])
        check_wunschprofil(wurzel, auftrag["wunschprofil"])
    auftrag["geaendert"] = stamp(now)
    if material_hash(auftrag) != before and auftrag["status"] in ("aktiv", "pausiert"):
        auftrag["status"] = "zur_freigabe"
    save_auftrag(wurzel, auftrag)
    if "ausschluesse" in patch:
        reassess(wurzel, auftrag)
    return auftrag


def approval_problem(wurzel, auftrag):
    """Return (code, meldung) when the Suchauftrag may not run, else None (ST-14)."""
    status = auftrag["status"]
    if status == "beendet":
        return "beendet", "Der Suchauftrag ist beendet."
    if status == "pausiert":
        return "pausiert", "Der Suchauftrag ist pausiert."
    if status != "aktiv":
        return "nicht_freigegeben", "Der Suchauftrag ist nicht freigegeben."
    approval = auftrag.get("freigabe") or {}
    if approval.get("hash") != material_hash(auftrag):
        return "freigabe_veraltet", "Suchbrief oder Plan weichen von der Freigabe ab; neue Freigabe nötig."
    if auftrag.get("wunschprofil") and approval.get("wunschprofil_hash") != wunschprofil_hash(wurzel):
        return "freigabe_veraltet", "Das Wunschprofil hat sich seit der Freigabe geändert; neue Freigabe nötig."
    return None


def queries(brief):
    """Calls to the search service per run: one per term and board (ST-15 rule 1)."""
    return len(brief["begriffe"]) * len(brief["boards"])


def approval_template(wurzel, auftrag):
    """What the user sees before the yes (ST-14 rule 2)."""
    brief, plan = auftrag["brief"], auftrag["plan"]
    sent = [term["text"] for term in brief["begriffe"]]
    if brief["ort"]:
        sent.append(f"Ort: {brief['ort']}")
    if brief["radius_km"] is not None:
        sent.append(f"Umkreis: {brief['radius_km']} km")
    if brief["remote"] is not None:
        sent.append("Remote: " + ("ja" if brief["remote"] else "nein"))
    if brief["jobtyp"]:
        sent.append(f"Jobtyp: {brief['jobtyp']}")
    sent.append(f"Anzeigenalter: höchstens {brief['max_alter_tage']} Tage")
    problem = approval_problem(wurzel, auftrag) if auftrag["status"] == "aktiv" else None
    return {
        "quellen": brief["boards"],
        "suchbegriffe": brief["begriffe"],
        "filter_lokal": auftrag["ausschluesse"],
        "uebermittelt_an_jobspy": sent,
        "nicht_uebermittelt": "Ausschlüsse, Gehaltswünsche, persönliche Umstände, Text der Datengrundlage, Lebenslauf",
        "haeufigkeit": f"alle {plan['intervall_tage']} Tage, höchstens {plan['laeufe_pro_woche']} Läufe in {WINDOW_DAYS} Tagen",
        "umfang": f"je Lauf eine Abfrage pro Begriff und Board, also höchstens {queries(brief)} Abfragen mit je höchstens {brief['ergebnisse_pro_board']} Ergebnissen",
        "wiederholung": f"nach einem Fehler frühestens nach {plan['wiederholung_stunden']} Stunden, nach {plan['max_fehler_in_folge']} Fehlern in Folge Stopp bis zu deiner Entscheidung",
        "umgang_mit_ergebnissen": "Titel, Firma, Ort, Datum, URL und Hash der Beschreibung bleiben lokal in suche/warteschlange.json; keine Beschreibungstexte, keine Kontaktadressen",
        "aussenwirkung": "keine: kein Versand, keine Nachricht, keine Bewerbung; die Freigabe gilt nur für diese Suche",
        "freigabe_gueltig": auftrag["status"] == "aktiv" and problem is None,
        "freigabe_problem": problem[1] if problem else "",
    }


def approve_auftrag(wurzel, auftrag_id, now):
    auftrag = load_auftrag(wurzel, auftrag_id)
    stale = auftrag["status"] == "aktiv" and approval_problem(wurzel, auftrag) is not None
    if auftrag["status"] not in ("entwurf", "zur_freigabe") and not stale:
        raise Refused("freigabe_nicht_moeglich", f"Aus dem Status {auftrag['status']} wird nicht freigegeben")
    profile = check_wunschprofil(wurzel, auftrag.get("wunschprofil"))
    auftrag["freigabe"] = {"hash": material_hash(auftrag), "am": stamp(now), "wunschprofil_hash": profile}
    auftrag["status"] = "aktiv"
    auftrag["geaendert"] = stamp(now)
    save_auftrag(wurzel, auftrag)
    return auftrag


def pause_auftrag(wurzel, auftrag_id, now):
    auftrag = load_auftrag(wurzel, auftrag_id)
    if auftrag["status"] in ("beendet", "pausiert"):
        raise Refused("status_unveraendert", f"Der Suchauftrag ist schon {auftrag['status']}")
    auftrag["status"] = "pausiert"
    auftrag["geaendert"] = stamp(now)
    save_auftrag(wurzel, auftrag)
    return auftrag


def resume_auftrag(wurzel, auftrag_id, now):
    """pausiert -> aktiv only while the approval still holds; also clears the stop after errors (ST-16 rule 3)."""
    auftrag = load_auftrag(wurzel, auftrag_id)
    if auftrag["status"] == "beendet":
        raise Refused("beendet", "Ein beendeter Suchauftrag wird nicht fortgesetzt; lege einen neuen an")
    if auftrag["status"] in ("entwurf", "zur_freigabe"):
        raise Refused("nicht_freigegeben", "Der Suchauftrag ist noch nicht freigegeben")
    if auftrag["status"] == "pausiert":
        auftrag["status"] = "aktiv"
        if approval_problem(wurzel, auftrag):
            auftrag["status"] = "zur_freigabe"
    auftrag["fehler_in_folge"] = 0
    auftrag["fehler"] = None
    auftrag["geaendert"] = stamp(now)
    save_auftrag(wurzel, auftrag)
    return auftrag


def end_auftrag(wurzel, auftrag_id, now):
    auftrag = load_auftrag(wurzel, auftrag_id)
    if auftrag["status"] == "beendet":
        raise Refused("status_unveraendert", "Der Suchauftrag ist schon beendet")
    auftrag["status"] = "beendet"
    auftrag["geaendert"] = stamp(now)
    for run in auftrag["laeufe"]:
        if run["status"] == "laeuft":
            run.update(status="unterbrochen", ende=stamp(now),
                       fehler={"code": "lauf_unterbrochen", "meldung": "Der Suchauftrag wurde beendet."})
    release_lock(wurzel, auftrag_id)
    save_auftrag(wurzel, auftrag)
    reassess(wurzel, auftrag, drop=True)
    return auftrag


# ---------------------------------------------------------------- runs

def lock_path(wurzel, auftrag_id):
    return os.path.join(wurzel, "suche", "auftraege", auftrag_id + ".lock")


def release_lock(wurzel, auftrag_id, run_id=None):
    """Remove the run lock; with `run_id` only when that run holds it."""
    path = lock_path(wurzel, auftrag_id)
    try:
        if run_id is not None:
            try:
                if load_json(path, {}).get("lauf") != run_id:
                    return
            except Refused:
                pass
        os.unlink(path)
    except FileNotFoundError:
        pass


@contextlib.contextmanager
def exclusive(wurzel, bereich="suche", name=".stellensuche.lock", beschreibung="die Suche"):
    """One state-changing command at a time per Wurzel: queue and orders are read, changed and rewritten whole.

    `bereich` and `name` let the workflow keep its own lock next to its own files (`workflow.py`)."""
    if fcntl is None:
        yield
        return
    path = os.path.join(wurzel, bereich, name)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        handle = open(path, "a")
    except OSError as error:
        raise Refused("speichern_fehlgeschlagen", f"Sperre nicht möglich: {redact(error)}")
    deadline = time.monotonic() + LOCK_WAIT_SECONDS
    try:
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > deadline:
                    raise Refused("beschaeftigt", f"Ein anderer Befehl ändert gerade {beschreibung}; später wiederholen.")
                time.sleep(0.05)
        yield
    finally:
        handle.close()  # closing releases the flock


def due(wurzel, auftrag, now):
    """Return (faellig, grund) for a scheduled run (ST-15 rule 2, ST-16 rule 3)."""
    problem = approval_problem(wurzel, auftrag)
    if problem:
        return False, problem[0]
    plan = auftrag["plan"]
    if auftrag["fehler_in_folge"] >= plan["max_fehler_in_folge"]:
        return False, "gestoppt_nach_fehlern"
    if len(runs_in_window(auftrag, now)) >= plan["laeufe_pro_woche"]:
        return False, "budget_erschoepft"
    attempt = auftrag.get("letzter_versuch")
    if attempt is None:
        return True, "erster_lauf"
    wait = (dt.timedelta(hours=plan["wiederholung_stunden"]) if auftrag["fehler_in_folge"]
            else dt.timedelta(days=plan["intervall_tage"]))
    if now - parse_time(attempt) < wait:
        return False, "noch_nicht_faellig"
    return True, "faellig"


def runs_in_window(auftrag, now):
    start = now - dt.timedelta(days=WINDOW_DAYS)
    return [run for run in auftrag["laeufe"] if parse_time(run["start"]) > start]


def start_run(wurzel, auftrag_id, trigger, now):
    auftrag = load_auftrag(wurzel, auftrag_id)
    problem = approval_problem(wurzel, auftrag)
    if problem:
        raise Refused(*problem)
    window = runs_in_window(auftrag, now)
    limit = auftrag["plan"]["laeufe_pro_woche"]
    if len(window) >= limit:
        oldest = min(parse_time(run["start"]) for run in window)
        raise Refused("budget_erschoepft", f"{limit} Läufe in {WINDOW_DAYS} Tagen sind ausgeschöpft; "
                      f"der nächste ist ab {stamp(oldest + dt.timedelta(days=WINDOW_DAYS))} möglich.")
    if trigger == "geplant":
        ok, reason = due(wurzel, auftrag, now)
        if not ok:
            raise Refused(reason, "Der Lauf ist nicht fällig." if reason == "noch_nicht_faellig"
                          else "Der Suchauftrag ist nach wiederholten Fehlern gestoppt; erst prüfen, dann fortsetzen.")
    path = lock_path(wurzel, auftrag_id)
    interrupted = None
    handle = None
    for _ in range(3):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except OSError as error:
            if not isinstance(error, FileExistsError):
                raise Refused("speichern_fehlgeschlagen", f"Lauf nicht sperrbar: {redact(error)}")
            held = {}
            try:
                held = load_json(path, {})
            except Refused:  # empty or torn file: the writer died, or is writing right now
                try:
                    if time.time() - os.path.getmtime(path) < LOCK_GRACE_SECONDS:
                        raise Refused("lauf_aktiv", "Ein Lauf wird gerade gestartet.")
                except FileNotFoundError:
                    continue  # it vanished in between: try again
            try:
                since = parse_time(held["am"]) if held.get("am") else None
            except (ValueError, TypeError):
                since = None  # malformed: stale
            if since and now - since < dt.timedelta(minutes=LOCK_MINUTES):
                raise Refused("lauf_aktiv", f"Der Lauf {held.get('lauf', '?')} läuft noch (seit {held['am']}).")
            interrupted = held.get("lauf")
            release_lock(wurzel, auftrag_id)
    if handle is None:
        raise Refused("lauf_aktiv", "Der Lauf konnte nicht gesperrt werden")
    auftrag["lauf_zaehler"] += 1
    run_id = f"l{auftrag['lauf_zaehler']:04d}"
    with os.fdopen(handle, "w", encoding="utf-8") as out:
        json.dump({"lauf": run_id, "am": stamp(now)}, out)
    for run in auftrag["laeufe"]:
        if interrupted and run["lauf"] == interrupted and run["status"] == "laeuft":
            run.update(status="unterbrochen", ende=stamp(now),
                       fehler={"code": "lauf_unterbrochen", "meldung": "Der Lauf wurde nicht beendet."})
    auftrag["laeufe"] = (auftrag["laeufe"] + [{"lauf": run_id, "trigger": trigger, "start": stamp(now), "ende": None,
                                               "status": "laeuft", "boards": {}, "zaehlung": {}, "fehler": None}])[-KEEP_RUNS:]
    auftrag["letzter_versuch"] = stamp(now)
    try:
        save_auftrag(wurzel, auftrag)
    except Refused:
        release_lock(wurzel, auftrag_id, run_id)
        raise
    return {"ok": True, "auftrag": auftrag_id, "lauf": run_id, "unterbrochener_lauf": interrupted,
            "brief": auftrag["brief"], "boards_erlaubt": auftrag["brief"]["boards"],
            "aufrufe_erlaubt": queries(auftrag["brief"]),
            "hinweis": "Nur search_jobs, je Begriff und Board ein Aufruf mit nur diesem Begriff; kein get_job_details, kein LinkedIn."}


def find_run(auftrag, run_id):
    for run in auftrag["laeufe"]:
        if run["lauf"] == run_id:
            return run
    raise Refused("lauf_unbekannt", f"Kein Lauf {redact(run_id, 20)} in {auftrag['id']}")


# ---------------------------------------------------------------- results: normalise, identify, merge

def first(raw, *names):
    for name in names:
        if raw.get(name) not in (None, ""):
            return raw[name]
    return None


def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "ja", "yes", "remote"):
        return True
    if isinstance(value, str) and value.strip().lower() in ("false", "nein", "no"):
        return False
    return None


def to_number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def valid_date(text):
    """The ISO date of a record, or an empty string when it is missing or no real date."""
    try:
        return dt.date.fromisoformat(text).isoformat() if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else ""
    except ValueError:
        return ""


def normalise(raw):
    """Reduce one result record to the stored fields. Everything else, `emails` included, is dropped (ST-9)."""
    if not isinstance(raw, dict):
        raise Defect("kein Objekt")
    title = clean_text(first(raw, "title", "titel"), 200)
    if not title:
        raise Defect("Titel fehlt")
    job_type = first(raw, "job_type", "jobtyp")
    job_type = ",".join(map(str, job_type)) if isinstance(job_type, list) else job_type
    date = clean_text(first(raw, "date_posted", "datum"), 40)[:10]
    stelle = {
        "titel": title, "firma": clean_text(first(raw, "company", "firma"), 120),
        "ort": clean_text(first(raw, "location", "ort"), 120),
        "remote": to_bool(first(raw, "is_remote", "remote")),
        "jobtyp": clean_text(job_type, 60).lower(),
        "datum": valid_date(date),
        "board_id": clean_text(first(raw, "id", "board_id"), 80),
    }
    low, high = to_number(raw.get("min_amount")), to_number(raw.get("max_amount"))
    stelle["gehalt"] = ({"min": low, "max": high, "waehrung": clean_text(raw.get("currency"), 8),
                         "intervall": clean_text(raw.get("interval"), 12), "quelle": clean_text(raw.get("salary_source"), 20)}
                        if low is not None or high is not None else None)
    for key, names in (("url", ("job_url", "url")), ("url_direkt", ("job_url_direct", "url_direkt"))):
        value = clean_text(first(raw, *names), 500)
        stelle[key] = value if value and not posting_url.refusal(value) else ""
    description = clean_text(first(raw, "description", "beschreibung"), 20000)
    stelle["beschreibung_hash"] = digest(fold(description)) if description else ""
    signals = raw.get("signale")
    stelle["signale"] = sorted({s for s in signals if s in SIGNALS}) if isinstance(signals, list) else []
    return stelle


def identity_keys(stelle, board):
    keys = []
    if stelle["board_id"]:
        keys.append(f"id:{board}:{stelle['board_id']}")
    for url in (stelle["url_direkt"], stelle["url"]):
        if url:
            keys.append("url:" + canonical_url(url))
    if not keys:
        keys.append("inh:" + digest(norm(stelle["firma"]), norm(stelle["titel"]), norm(stelle["ort"]), stelle["datum"])[:24])
    return keys


def triple(stelle):
    parts = (norm(stelle["firma"]), norm(stelle["titel"]), norm(stelle["ort"]))
    return "|".join(parts) if all(parts) else ""


def content_hash(stelle):
    return digest(stelle["titel"], stelle["firma"], stelle["ort"], str(stelle["remote"]), stelle["jobtyp"],
                  json.dumps(stelle["gehalt"], sort_keys=True), stelle["beschreibung_hash"])


def days_apart(first_date, second_date):
    """Days between two stored dates; 0 when one is unknown (stored dates are valid, see `valid_date`)."""
    if not first_date or not second_date:
        return 0
    try:
        return abs((dt.date.fromisoformat(first_date) - dt.date.fromisoformat(second_date)).days)
    except ValueError:
        return 0


def word_match(wanted, value):
    """Whole words, ignoring case and diacritics; a value of 5+ letters also matches inside a German compound."""
    needle, hay = norm(wanted), norm(value)
    if not needle:
        return False
    return f" {needle} " in f" {hay} " or (len(needle) >= 5 and needle in hay)


def prefilter(auftrag, stelle):
    """Veto on structured fields only (ST-5 rule 2). A missing field is `unklar`, never a Veto (ST-18 rule 2)."""
    if not auftrag["ausschluesse"]:
        return {"geprueft": False, "veto": [], "unklar": []}
    veto, unclear = [], []
    for item in auftrag["ausschluesse"]:
        field, wanted = item["feld"], fold(item["wert"])
        value = stelle[field]
        if value in (None, ""):
            unclear.append(field)
        elif field == "remote":
            if value == (wanted == "ja"):
                veto.append({**item, "grund": "Remote-Angabe steht auf den Ausschlüssen"})
        elif word_match(item["wert"], value):
            veto.append({**item, "grund": f"{field.capitalize()} enthält „{item['wert']}“"})
    return {"geprueft": True, "veto": veto, "unklar": sorted(set(unclear))}


def prefilter_class(entry):
    check = entry["vorpruefung"]
    if check["veto"]:
        return "veto"
    if check["unklar"] or entry["unvollstaendig"] or entry["signale"] or not check["geprueft"]:
        return "klaerung"
    return "ohne_treffer"


def vorgang_meta(path):
    """Frontmatter of a vorgang.md; tolerant of CRLF and a BOM, None when the file cannot be read."""
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            text = handle.read().replace("\r\n", "\n")
    except OSError:
        return None
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.S)
    data = {}
    for line in (match.group(1).splitlines() if match else []):
        pair = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
        if pair:
            data[pair.group(1)] = pair.group(2).strip("\"'")
    return data


def scan_vorgaenge(wurzel):
    found = []
    for name in sorted(os.listdir(wurzel)) if os.path.isdir(wurzel) else []:
        path = os.path.join(wurzel, name, "vorgang.md")
        if os.path.isfile(path):
            meta = vorgang_meta(path)
            if meta is None:
                continue
            found.append({"slug": name, "firma": meta.get("firma", ""), "stelle": meta.get("stelle", ""),
                          "quelle": meta.get("stellenquelle", ""), "status": meta.get("status", "")})
    return found


def match_vorgang(entry, vorgaenge):
    urls = {key for key in entry["schluessel"] if key.startswith("url:")}
    for vorgang in vorgaenge:
        if vorgang["quelle"] and not posting_url.refusal(vorgang["quelle"]) \
                and "url:" + canonical_url(vorgang["quelle"]) in urls:
            return vorgang["slug"]
        if norm(vorgang["firma"]) and norm(vorgang["firma"]) == norm(entry["firma"]) \
                and norm(vorgang["stelle"]) and norm(vorgang["stelle"]) == norm(entry["titel"]):
            return vorgang["slug"]
    return ""


def log(entry, now, text):
    entry["verlauf"] = (entry["verlauf"] + [{"am": stamp(now), "ereignis": text}])[-KEEP_LOG:]


def new_entry(stelle, keys, now):
    entry = {
        "id": "s-" + digest(*keys)[:10], "schluessel": list(keys), "titel": stelle["titel"], "firma": stelle["firma"],
        "ort": stelle["ort"], "remote": stelle["remote"], "jobtyp": stelle["jobtyp"], "datum": stelle["datum"],
        "gehalt": stelle["gehalt"], "boards": [], "url": stelle["url_direkt"] or stelle["url"],
        "beschreibung_hash": stelle["beschreibung_hash"], "inhalt_hash": content_hash(stelle),
        "signale": list(stelle["signale"]), "vorpruefung": {}, "unvollstaendig": [],
        "erstmals_gesehen": stamp(now), "zuletzt_gesehen": stamp(now), "zuletzt_lauf": "", "gefunden_in": [],
        "nicht_gesehen_zaehler": 0, "verfuegbarkeit": "verfuegbar", "bearbeitung": "offen", "grund": "", "bis": "",
        "entschieden_am": "", "vorgang": "", "uebergabe": None, "aenderung": None, "hinweise": [],
        "duplikat_kandidaten": [], "verlauf": [],
    }
    log(entry, now, "erstmals gefunden")
    return entry


def combine_prefilter(entry):
    results = list(entry.get("vorpruefung_je_auftrag", {}).values())
    entry["vorpruefung"] = {
        "geprueft": any(r["geprueft"] for r in results),
        "veto": [v for r in results for v in r["veto"]],
        "unklar": sorted({u for r in results for u in r["unklar"]}),
    }


def reassess(wurzel, auftrag, drop=False):
    """Judge the open Stellen of an order again after its exclusions changed, or forget its judgement when it ended."""
    queue = load_queue(wurzel)
    for entry in queue["stellen"].values():
        if not any(seen["auftrag"] == auftrag["id"] for seen in entry["gefunden_in"]):
            continue
        if drop:
            entry.setdefault("vorpruefung_je_auftrag", {}).pop(auftrag["id"], None)
            combine_prefilter(entry)
        elif entry["bearbeitung"] in ("offen", "zurückgestellt"):
            entry.setdefault("vorpruefung_je_auftrag", {})[auftrag["id"]] = prefilter(auftrag, entry)
            combine_prefilter(entry)
    atomic_write(queue_path(wurzel), queue)


def refresh_derived(entry, auftrag):
    entry["unvollstaendig"] = [name for name, value in (("firma", entry["firma"]), ("ort", entry["ort"]), ("url", entry["url"]))
                               if not value]
    signals = set(entry["signale"]) - {"kein_arbeitgeber"}
    entry["signale"] = sorted(signals | (set() if entry["firma"] else {"kein_arbeitgeber"}))
    if entry["bearbeitung"] in ("offen", "zurückgestellt"):
        # each Suchauftrag judges with its own exclusions; the Stelle shows the union of the orders that found it
        entry.setdefault("vorpruefung_je_auftrag", {})[auftrag["id"]] = prefilter(auftrag, entry)
        combine_prefilter(entry)


def flag_duplicates(entries, entry, others):
    for other in others:
        if other == entry["id"] or other not in entries:
            continue
        if other in entry.get("kein_duplikat", []) or entry["id"] in entries[other].get("kein_duplikat", []):
            continue  # the user already decided these are two postings
        for left, right in ((entry, other), (entries[other], entry["id"])):
            if right not in left["duplikat_kandidaten"]:
                left["duplikat_kandidaten"].append(right)
            left["hinweise"] = sorted(set(left["hinweise"]) | {"moegliches_duplikat"})


FIELDS = ("titel", "firma", "ort", "remote", "jobtyp", "gehalt")


def blank(value):
    return value is None or value == ""


def ingest_records(queue, auftrag, run_id, board, records, now, vorgaenge, seen=True):
    """Merge the records of one board into the queue. A bad record is counted and skipped (ST-17 rule 1).

    A change is a difference from what the same board reported before (ST-17 rule 3); a field the record leaves
    blank changes nothing. With `seen=False` (a later entry for an old run) availability is not touched.
    """
    entries = queue["stellen"]
    index = {key: entry_id for entry_id, entry in entries.items() for key in entry["schluessel"]}
    count = dict.fromkeys(("neu", "unveraendert", "aktualisiert", "bereits_ausgewaehlt", "im_vorgang", "entschieden",
                           "moegliches_duplikat"), 0)
    defects, neue = [], []
    for number, raw in enumerate(records):
        try:
            stelle = normalise(raw)
        except Defect as error:
            defects.append({"nr": number, "grund": str(error)})
            continue
        keys = identity_keys(stelle, board)
        hits = sorted({index[key] for key in keys if key in index})
        others, created = [], False
        if hits:
            entry, others = entries[hits[0]], hits[1:]
        else:
            same = [e for e in entries.values() if triple(stelle) and triple(e) == triple(stelle)]
            merge = [e for e in same if board not in {b["board"] for b in e["boards"]}
                     and days_apart(e["datum"], stelle["datum"]) <= SAME_POSTING_DAYS]
            if merge:
                entry = merge[0]
            else:
                entry, created = new_entry(stelle, keys, now), True
                others = [e["id"] for e in same]
                entries[entry["id"]] = entry
        for key in keys:  # a changed URL or a second id stays the same posting
            if key not in entry["schluessel"]:
                entry["schluessel"].append(key)
            index[key] = entry["id"]
        source = next((b for b in entry["boards"] if b["board"] == board), None)
        if source is None:
            source = {"board": board, "url": stelle["url"], "url_direkt": stelle["url_direkt"], "stand": {}}
            entry["boards"].append(source)
        else:
            source["url"], source["url_direkt"] = stelle["url"] or source["url"], stelle["url_direkt"] or source["url_direkt"]
        stand = source.setdefault("stand", {})  # the last non-blank value this board gave per field
        changed = []
        for field in FIELDS + ("beschreibung_hash",):
            new = stelle[field]
            if blank(new):
                continue
            if not created and not blank(stand.get(field)) and stand[field] != new:
                changed.append("beschreibung" if field == "beschreibung_hash" else field)
            stand[field] = new
        for field in FIELDS + ("beschreibung_hash",):
            if not blank(stelle[field]) and (blank(entry[field]) or ("beschreibung" if field == "beschreibung_hash" else field) in changed):
                entry[field] = stelle[field]
        if changed:
            entry["inhalt_hash"] = content_hash(entry)
            entry["aenderung"] = {"felder": changed, "am": stamp(now), "gesehen": False}
            log(entry, now, "Anzeige geändert: " + ", ".join(changed))
        entry["datum"] = stelle["datum"] or entry["datum"]
        entry["url"] = entry["url"] or stelle["url_direkt"] or stelle["url"]
        entry["signale"] = sorted(set(entry["signale"]) | set(stelle["signale"]))
        if seen or created:
            entry.update(zuletzt_gesehen=stamp(now), zuletzt_lauf=f"{auftrag['id']}/{run_id}", nicht_gesehen_zaehler=0,
                         verfuegbarkeit="verfuegbar")
        if not any(s["auftrag"] == auftrag["id"] and s["lauf"] == run_id and s["board"] == board for s in entry["gefunden_in"]):
            entry["gefunden_in"] = (entry["gefunden_in"] + [{"auftrag": auftrag["id"], "lauf": run_id, "am": stamp(now),
                                                              "board": board}])[-KEEP_SEEN:]
        if not entry["vorgang"]:
            entry["vorgang"] = match_vorgang(entry, vorgaenge)
            if entry["vorgang"]:
                entry["hinweise"] = sorted(set(entry["hinweise"]) | {"bereits_beworben"})
        flag_duplicates(entries, entry, others)
        refresh_derived(entry, auftrag)
        # the one place that classifies an observation (ST-15 rule 4)
        if created:
            kind = "im_vorgang" if entry["vorgang"] else ("moegliches_duplikat" if entry["duplikat_kandidaten"] else "neu")
            if kind in ("neu", "moegliches_duplikat"):
                neue.append(entry["id"])
        elif changed:
            kind = "aktualisiert"
        elif entry["vorgang"]:
            kind = "im_vorgang"
        elif entry["bearbeitung"] == "übernommen":
            kind = "bereits_ausgewaehlt"
        elif entry["bearbeitung"] in ("abgelehnt", "zurückgestellt"):
            kind = "entschieden"
        else:
            kind = "unveraendert"
        count[kind] += 1
    return count, defects, neue


def record_board(wurzel, auftrag_id, run_id, board, payload, now):
    auftrag = load_auftrag(wurzel, auftrag_id)
    run = find_run(auftrag, run_id)
    if run["status"] != "laeuft":
        raise Refused("lauf_nicht_aktiv", f"Der Lauf {run_id} ist {run['status']}")
    if board not in auftrag["brief"]["boards"]:
        raise Refused("board_nicht_freigegeben", f"{redact(board, 30)} gehört nicht zu den freigegebenen Boards")
    if board in run["boards"]:
        return {"ok": True, "bereits_erfasst": True, "board": board, **run["boards"][board]}
    if not isinstance(payload, dict) or payload.get("status") not in BOARD_STATUS:
        raise Refused("ergebnisdaten_unvollstaendig", f"status ist einer von {', '.join(BOARD_STATUS)}")
    records = payload.get("ergebnisse") or []
    if not isinstance(records, list):
        raise Refused("ergebnisdaten_unvollstaendig", "ergebnisse muss eine Liste sein")
    per_term = payload.get("je_begriff")
    if per_term is not None and not (isinstance(per_term, list) and len(per_term) == len(auftrag["brief"]["begriffe"])
                                      and all(bounded_int(n, 0, 1000) for n in per_term)):
        raise Refused("ergebnisdaten_unvollstaendig", "je_begriff ist eine Liste von Anzahlen, genau eine je Suchbegriff")
    entry = {"status": payload["status"], "grund": redact(payload.get("grund")), "anzahl": 0, "abgeschnitten": 0,
             "defekt": 0, "zaehlung": {}, "neue": [], "je_begriff": per_term}
    if payload["status"] == "ok":
        limit = auftrag["brief"]["ergebnisse_pro_board"] * len(auftrag["brief"]["begriffe"])
        taken = records[:limit]
        queue = load_queue(wurzel)
        count, defects, neue = ingest_records(queue, auftrag, run_id, board, taken, now, scan_vorgaenge(wurzel))
        entry.update(anzahl=len(taken) - len(defects), abgeschnitten=max(0, len(records) - limit), defekt=len(defects),
                     zaehlung=count, neue=neue, defekte=defects[:10])
        atomic_write(queue_path(wurzel), queue)
    run["boards"][board] = entry
    save_auftrag(wurzel, auftrag)
    return {"ok": True, "board": board, **entry}


def add_later(wurzel, auftrag_id, run_id, board, payload, now):
    """Store the answers of a board for a Lauf that ended without them (ST-15 rule 7).

    Only for a `teilweise`, `fehlgeschlagen` or `unterbrochen` Lauf, only for an approved board that did not report `ok`, once per board.
    The Lauf keeps its status; no success time, failure count, availability or budget changes. Storing is idempotent
    (a posting already known is `unveraendert`), so a repeat after a failed save of the order is harmless.
    """
    auftrag = load_auftrag(wurzel, auftrag_id)
    run = find_run(auftrag, run_id)
    if run["status"] not in ("teilweise", "fehlgeschlagen", "unterbrochen"):
        raise Refused("nachtrag_nicht_moeglich", f"Der Lauf {run_id} ist {run['status']}; nachgetragen wird nur nach einem Fehler, Teilerfolg oder Abbruch")
    problem = approval_problem(wurzel, auftrag)
    if problem:
        raise Refused(*problem)
    if board not in auftrag["brief"]["boards"]:
        raise Refused("board_nicht_freigegeben", f"{redact(board, 30)} gehört nicht zu den freigegebenen Boards")
    if run["boards"].get(board, {}).get("status") == "ok" or board in run.setdefault("nachtraege", {}):
        raise Refused("nachtrag_nicht_moeglich", f"Für {board} liegen im Lauf {run_id} schon Ergebnisse vor")
    if not isinstance(payload, dict) or payload.get("status") != "ok" or not isinstance(payload.get("ergebnisse"), list):
        raise Refused("ergebnisdaten_unvollstaendig", 'Ein Nachtrag braucht {"status": "ok", "ergebnisse": [...]}')
    limit = auftrag["brief"]["ergebnisse_pro_board"] * len(auftrag["brief"]["begriffe"])
    taken = payload["ergebnisse"][:limit]
    queue = load_queue(wurzel)
    count, defects, neue = ingest_records(queue, auftrag, run_id, board, taken, now, scan_vorgaenge(wurzel), seen=False)
    result = {"am": stamp(now), "anzahl": len(taken) - len(defects), "abgeschnitten": max(0, len(payload["ergebnisse"]) - limit),
              "defekt": len(defects), "zaehlung": count, "neue": neue}
    atomic_write(queue_path(wurzel), queue)
    run["nachtraege"][board] = result
    save_auftrag(wurzel, auftrag)
    return {"ok": True, "lauf": run_id, "lauf_status": run["status"], "board": board, **result}


def list_not_full(result, auftrag, cap):
    """A board's answer is complete when no single term hit the cap. Without per-term counts: an empty answer, or one term."""
    per_term = result.get("je_begriff")
    if per_term:
        return max(per_term) < cap
    if len(auftrag["brief"]["begriffe"]) == 1:
        return result["anzahl"] + result["defekt"] < cap
    return result["anzahl"] + result["defekt"] == 0


def mark_missing(queue, auftrag, seen_key, complete):
    """Count a posting as not seen only on boards whose list was not full: on a full list (the cap of the search is
    reached) a missing posting may just rank lower (ST-17 rule 5)."""
    count = 0
    for entry in queue["stellen"].values():
        mine = any(seen["auftrag"] == auftrag["id"] for seen in entry["gefunden_in"])
        searched = {b["board"] for b in entry["boards"]} & set(auftrag["brief"]["boards"])
        if mine and searched and searched <= complete and entry["zuletzt_lauf"] != seen_key:
            entry["nicht_gesehen_zaehler"] += 1
            if entry["nicht_gesehen_zaehler"] == MISSED_RUNS:
                entry["verfuegbarkeit"] = "nicht_mehr_gesehen"
                count += 1
    return count


def finish_run(wurzel, auftrag_id, run_id, now):
    auftrag = load_auftrag(wurzel, auftrag_id)
    run = find_run(auftrag, run_id)
    if run["status"] != "laeuft":
        return {"ok": True, "bereits_abgeschlossen": True, "lauf": run_id, "status": run["status"],
                "zaehlung": run["zaehlung"], "fehler": run["fehler"]}
    boards, expected = run["boards"], auftrag["brief"]["boards"]
    ok_boards = [b for b, r in boards.items() if r["status"] == "ok"]
    failed = [b for b in expected if b not in ok_boards]
    total = {}
    for result in boards.values():
        for key, value in result["zaehlung"].items():
            total[key] = total.get(key, 0) + value
    found = sum(r["anzahl"] for r in boards.values())
    warnings, error = [], None
    if not ok_boards:
        reported = next((boards[b] for b in expected if b in boards), None)
        error = ({"code": BOARD_CODES.get(reported["status"], "board_fehler"), "meldung": reported["grund"] or "Kein Board hat geantwortet."}
                 if reported else {"code": "lauf_unterbrochen", "meldung": "Kein Board wurde erfasst."})
        status = "fehlgeschlagen"
    elif failed:
        status = "teilweise"
        warnings = [{"board": b, "code": BOARD_CODES.get(boards[b]["status"], "board_fehler") if b in boards else "lauf_unterbrochen",
                     "grund": boards[b]["grund"] if b in boards else "nicht abgefragt"} for b in failed]
    else:
        status = "ok" if found else "ok_ohne_treffer"
    if any(r["defekt"] for r in boards.values()):
        warnings.append({"code": "ergebnisdaten_unvollstaendig", "anzahl": sum(r["defekt"] for r in boards.values())})
    if total.get("moegliches_duplikat"):
        warnings.append({"code": "duplikat_unklar", "anzahl": total["moegliches_duplikat"]})
    queue = load_queue(wurzel)
    if status in ("ok", "ok_ohne_treffer"):
        cap = auftrag["brief"]["ergebnisse_pro_board"]
        complete = {b for b, r in boards.items() if r["status"] == "ok" and not r["abgeschnitten"] and list_not_full(r, auftrag, cap)}
        run["vollstaendige_boards"] = sorted(complete)
        total["nicht_mehr_gesehen"] = mark_missing(queue, auftrag, f"{auftrag_id}/{run_id}", complete)
        atomic_write(queue_path(wurzel), queue)
        auftrag["letzter_erfolg"] = stamp(now)
    run.update(status=status, ende=stamp(now), zaehlung=total, fehler=error, warnungen=warnings)
    auftrag["fehler_in_folge"] = auftrag["fehler_in_folge"] + 1 if status == "fehlgeschlagen" else 0
    auftrag["fehler"] = error
    auftrag["letzter_lauf"] = {"lauf": run_id, "status": status, "am": stamp(now), "zaehlung": total}
    save_auftrag(wurzel, auftrag)
    release_lock(wurzel, auftrag_id, run_id)
    new = [{"id": e["id"], "titel": e["titel"], "firma": e["firma"], "ort": e["ort"], "vorpruefung": prefilter_class(e)}
           for r in boards.values() for e in (queue["stellen"].get(i) for i in r.get("neue", [])) if e]
    return {"ok": status != "fehlgeschlagen", "lauf": run_id, "status": status, "zaehlung": total, "fehler": error,
            "warnungen": warnings, "neue_stellen": new, "fehler_in_folge": auftrag["fehler_in_folge"]}


# ---------------------------------------------------------------- queue and decisions

def get_entry(queue, entry_id):
    if entry_id not in queue["stellen"]:
        raise Refused("stelle_unbekannt", f"Keine Stelle {redact(entry_id, 40)} in der Warteschlange")
    return queue["stellen"][entry_id]


def view(entry, vorgaenge):
    status = next((v["status"] for v in vorgaenge if v["slug"] == entry["vorgang"]), "")
    keys = ("id", "titel", "firma", "ort", "remote", "datum", "url", "bearbeitung", "grund", "bis", "vorgang",
            "verfuegbarkeit", "signale", "hinweise", "unvollstaendig", "erstmals_gesehen", "zuletzt_gesehen",
            "aenderung", "uebergabe", "vorpruefung", "duplikat_kandidaten")
    return {**{k: entry[k] for k in keys}, "boards": [b["board"] for b in entry["boards"]],
            "klasse": prefilter_class(entry), "vorgang_status": status}


def list_queue(wurzel, status, auftrag_id, klasse, now):
    queue = load_queue(wurzel)
    vorgaenge = scan_vorgaenge(wurzel)
    today = now.date().isoformat()
    result = []
    for entry in queue["stellen"].values():
        if auftrag_id and not any(seen["auftrag"] == auftrag_id for seen in entry["gefunden_in"]):
            continue
        item = view(entry, vorgaenge)
        if status == "aktuell":
            postponed = entry["bearbeitung"] == "zurückgestellt" and (not entry["bis"] or entry["bis"] > today)
            if entry["bearbeitung"] not in ("offen", "zurückgestellt") or postponed or entry["vorgang"]:
                continue
        elif status != "alle" and entry["bearbeitung"] != status:
            continue
        if klasse == "geaendert" and not (entry["aenderung"] and not entry["aenderung"]["gesehen"]):
            continue
        if klasse in ("veto", "klaerung", "ohne_treffer") and item["klasse"] != klasse:
            continue
        if klasse == "unvollstaendig" and not entry["unvollstaendig"]:
            continue
        result.append(item)
    order = {"ohne_treffer": 0, "klaerung": 1, "veto": 2}
    result.sort(key=lambda i: (order[i["klasse"]], -int(i["datum"].replace("-", "") or 0), i["firma"], i["id"]))
    cutoff = stamp(now - dt.timedelta(days=RETENTION_DAYS))
    overdue = sorted(e["id"] for e in queue["stellen"].values()
                     if e["zuletzt_gesehen"] < cutoff and e["bearbeitung"] in ("offen", "abgelehnt") and not e["vorgang"])
    return {"ok": True, "anzahl": len(result), "stellen": result, "aelter_als_90_tage": overdue,
            "hinweis": "Die Vorprüfung nutzt nur strukturierte Felder; die Passung prüft job-application-fit-check nach der Übergabe."}


def decide(wurzel, entry_id, decision, reason, until, now):
    if decision not in ("offen", "zurückgestellt", "abgelehnt"):
        raise Refused("entscheidung_ungueltig", "Entscheidungen: offen, zurückgestellt, abgelehnt (übernommen setzt die Übergabe)")
    if decision == "abgelehnt" and not clean_text(reason, 200):
        raise Refused("entscheidung_ungueltig", "Eine Ablehnung braucht einen kurzen Grund (ST-8 Regel 2)")
    if until and valid_date(until) != until:
        raise Refused("entscheidung_ungueltig", "bis ist ein echtes Datum der Form JJJJ-MM-TT")
    queue = load_queue(wurzel)
    entry = get_entry(queue, entry_id)
    if entry["bearbeitung"] == "übernommen" or entry["vorgang"]:
        raise Refused("entscheidung_ungueltig", f"Die Stelle ist im Vorgang {entry['vorgang'] or '?'}; der Status gehört dem Vorgang")
    entry.update(bearbeitung=decision, grund=redact(reason) if decision != "offen" else "",
                 bis=until if decision == "zurückgestellt" else "", entschieden_am=stamp(now))
    log(entry, now, f"Entscheidung: {decision}" + (f" ({entry['grund']})" if entry["grund"] else ""))
    atomic_write(queue_path(wurzel), queue)
    return view(entry, scan_vorgaenge(wurzel))


def acknowledge_change(wurzel, entry_id, now):
    queue = load_queue(wurzel)
    entry = get_entry(queue, entry_id)
    if entry["aenderung"]:
        entry["aenderung"]["gesehen"] = True
        log(entry, now, "Änderung zur Kenntnis genommen")
        atomic_write(queue_path(wurzel), queue)
    return view(entry, scan_vorgaenge(wurzel))


def drop_flag(entry):
    if not entry["duplikat_kandidaten"]:
        entry["hinweise"] = [h for h in entry["hinweise"] if h != "moegliches_duplikat"]


def resolve_duplicate(wurzel, entry_id, other_id, now):
    """With `other_id`: the two are one posting, entry is merged into other. Without: entry is a separate posting."""
    queue = load_queue(wurzel)
    stellen = queue["stellen"]
    entry = get_entry(queue, entry_id)
    if other_id is None:
        for other in entry["duplikat_kandidaten"]:
            if other in stellen:
                stellen[other]["duplikat_kandidaten"] = [i for i in stellen[other]["duplikat_kandidaten"] if i != entry_id]
                stellen[other]["kein_duplikat"] = sorted(set(stellen[other].get("kein_duplikat", [])) | {entry_id})
                drop_flag(stellen[other])
        entry["kein_duplikat"] = sorted(set(entry.get("kein_duplikat", [])) | set(entry["duplikat_kandidaten"]))
        entry["duplikat_kandidaten"] = []
        drop_flag(entry)
        log(entry, now, "kein Duplikat (Entscheidung des Nutzers)")
        result = entry
    else:
        target = get_entry(queue, other_id)
        if entry_id == other_id or other_id not in entry["duplikat_kandidaten"]:
            raise Refused("duplikat_ungueltig", "Zusammenführen nur mit einem genannten Kandidaten")
        if entry["vorgang"] and target["vorgang"] and entry["vorgang"] != target["vorgang"]:
            raise Refused("duplikat_ungueltig", "Beide Stellen gehören zu verschiedenen Vorgängen")
        target["schluessel"] = sorted(set(target["schluessel"]) | set(entry["schluessel"]))
        known = {b["board"] for b in target["boards"]}
        target["boards"] += [b for b in entry["boards"] if b["board"] not in known]
        target["gefunden_in"] = (target["gefunden_in"] + entry["gefunden_in"])[-KEEP_SEEN:]
        target["vorgang"] = target["vorgang"] or entry["vorgang"]
        if entry["bearbeitung"] == "übernommen" or (entry["bearbeitung"] == "abgelehnt" and target["bearbeitung"] == "offen"):
            target.update(bearbeitung=entry["bearbeitung"], grund=entry["grund"], entschieden_am=entry["entschieden_am"])
        del stellen[entry_id]
        for rest in stellen.values():
            rest["duplikat_kandidaten"] = [i for i in rest["duplikat_kandidaten"] if i != entry_id]
        target["duplikat_kandidaten"] = sorted(set(target["duplikat_kandidaten"] + entry["duplikat_kandidaten"]) - {entry_id, other_id})
        target["duplikat_kandidaten"] = [i for i in target["duplikat_kandidaten"] if i in stellen]
        drop_flag(target)
        log(target, now, f"zusammengeführt mit {entry_id} (Entscheidung des Nutzers)")
        result = target
    atomic_write(queue_path(wurzel), queue)
    return view(result, scan_vorgaenge(wurzel))


# ---------------------------------------------------------------- hand-off (ST-19)

def prepare_handoff(wurzel, entry_id, now):
    queue = load_queue(wurzel)
    entry = get_entry(queue, entry_id)
    if entry["vorgang"]:
        return {"ok": True, "status": "vorhanden", "vorgang": entry["vorgang"],
                "hinweis": "Der Vorgang besteht; er wird weiterverwendet, kein zweiter wird angelegt."}
    if entry["bearbeitung"] == "abgelehnt":
        raise Refused("stelle_abgelehnt", "Die Stelle ist abgelehnt; erst mit `entscheiden --als offen` wieder öffnen")
    if entry["verfuegbarkeit"] != "verfuegbar":
        return {"ok": False, "status": "nicht_moeglich", "gruende": ["nicht_mehr_gesehen"],
                "hinweis": "Die Anzeige wurde mehrfach nicht mehr gefunden; Anzeige prüfen oder Text selbst einfügen."}
    missing = [name for name, value in (("titel", entry["titel"]), ("firma", entry["firma"]), ("url", entry["url"])) if not value]
    notes = (["veto"] if entry["vorpruefung"]["veto"] else []) + (
        ["aenderung_ungesehen"] if entry["aenderung"] and not entry["aenderung"]["gesehen"] else [])
    status = "unvollstaendig" if missing else "bereit"
    entry["uebergabe"] = {"status": "vorbereitet" if not missing else "unvollstaendig", "am": stamp(now), "grund": ""}
    atomic_write(queue_path(wurzel), queue)
    return {"ok": not missing, "status": status, "fehlend": missing, "hinweise": notes,
            "stelle": {k: entry[k] for k in ("id", "titel", "firma", "ort", "datum")},
            "stellenquelle": entry["url"],
            "herkunft": {"boards": [b["board"] for b in entry["boards"]], "gefunden_in": entry["gefunden_in"][-3:],
                         "erstmals_gesehen": entry["erstmals_gesehen"]},
            "vorpruefung": entry["vorpruefung"],
            "anzeigentext": "nicht gespeichert: über den URL-Intake von job-application-posting-analysis (UE-1 bis UE-13) laden oder vom Nutzer einfügen lassen",
            "naechster_schritt": "job-application-solution mit stellenquelle; der Plan braucht weiterhin die Freigabe des Nutzers"}


def complete_handoff(wurzel, entry_id, slug_value, now):
    queue = load_queue(wurzel)
    entry = get_entry(queue, entry_id)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug_value or "") or not os.path.isfile(os.path.join(wurzel, slug_value, "vorgang.md")):
        raise Refused("uebergabe_fehlgeschlagen", f"Es gibt keinen Vorgang {redact(slug_value, 60)} mit vorgang.md in der Wurzel")
    if entry["vorgang"] and entry["vorgang"] != slug_value:
        raise Refused("vorgang_besteht", f"Die Stelle gehört schon zum Vorgang {entry['vorgang']}; kein zweiter Vorgang")
    if entry["vorgang"] == slug_value and entry["bearbeitung"] == "übernommen":
        return {**view(entry, scan_vorgaenge(wurzel)), "bereits_uebernommen": True}
    entry.update(vorgang=slug_value, bearbeitung="übernommen", entschieden_am=stamp(now), grund="", bis="",
                 uebergabe={"status": "abgeschlossen", "am": stamp(now), "grund": ""})
    log(entry, now, f"übernommen in Vorgang {slug_value}")
    atomic_write(queue_path(wurzel), queue)
    return view(entry, scan_vorgaenge(wurzel))


def fail_handoff(wurzel, entry_id, reason, now):
    queue = load_queue(wurzel)
    entry = get_entry(queue, entry_id)
    entry["uebergabe"] = {"status": "fehlgeschlagen", "am": stamp(now), "grund": redact(reason)}
    log(entry, now, "Übergabe fehlgeschlagen")
    atomic_write(queue_path(wurzel), queue)
    return {"ok": False, "code": "uebergabe_fehlgeschlagen", "wiederholbar": True, "stelle": entry_id}


# ---------------------------------------------------------------- overview (ST-19 rule 5)

def cell(value):
    """Text of a table cell from untrusted board content: every Markdown and HTML punctuation is escaped."""
    return re.sub(r"([\\`*_\[\]<>|~&])", r"\\\1", clean_text(value, 200))


SAFE_URL = re.compile(r"https?://[A-Za-z0-9._~:/?#@$&'*+,;=%-]+")


def write_overview(wurzel, now):
    """Write `suche/warteschlange.md`, a readable derivation of the JSON state; never read back."""
    queue, vorgaenge = load_queue(wurzel), scan_vorgaenge(wurzel)
    items = [view(entry, vorgaenge) for entry in queue["stellen"].values()]
    lines = ["# Warteschlange Stellensuche", "",
             f"Ableitung aus `warteschlange.json`, Stand {stamp(now)}. Nicht von Hand ändern: Entscheidungen laufen über "
             "`scripts/stellensuche.py` (`entscheiden`). Die Klasse beschreibt nur die Vorprüfung auf strukturierte Felder, "
             "keine Passung.", "", "## Suchaufträge", "", "| Auftrag | Status | Letzter Lauf | Fehler |", "|---|---|---|---|"]
    for auftrag in all_auftraege(wurzel):
        last = auftrag["letzter_lauf"] or {}
        error = (auftrag["fehler"] or {}).get("code", "")
        lines.append(f"| {cell(auftrag['id'])} | {auftrag['status']} | {last.get('status', '–')} {last.get('am', '')} | {error} |")
    groups = (("Offen und fällig", lambda i: i["bearbeitung"] == "offen" and not i["vorgang"]),
              ("Zurückgestellt", lambda i: i["bearbeitung"] == "zurückgestellt" and not i["vorgang"]),
              ("In einem Vorgang", lambda i: bool(i["vorgang"])),
              ("Abgelehnt", lambda i: i["bearbeitung"] == "abgelehnt" and not i["vorgang"]))
    order = {"ohne_treffer": 0, "klaerung": 1, "veto": 2}
    for title, test in groups:
        rows = sorted((i for i in items if test(i)), key=lambda i: (order[i["klasse"]], -int(i["datum"].replace("-", "") or 0), i["id"]))
        lines += ["", f"## {title} ({len(rows)})", ""]
        if not rows:
            lines.append("Keine.")
            continue
        lines += ["| Stelle | Firma | Titel | Ort | Datum | Klasse | Hinweise | Quelle |", "|---|---|---|---|---|---|---|---|"]
        for i in rows:
            notes = list(i["hinweise"]) + list(i["signale"]) + (["geändert"] if i["aenderung"] and not i["aenderung"]["gesehen"] else []) \
                + (["nicht mehr gesehen"] if i["verfuegbarkeit"] != "verfuegbar" else []) \
                + ([f"Vorgang {i['vorgang']}"] if i["vorgang"] else []) + ([f"bis {i['bis']}"] if i["bis"] else []) \
                + ([f"Grund: {i['grund']}"] if i["grund"] else [])
            label = cell(",".join(i["boards"]))
            link = f"[{label}]({i['url']})" if SAFE_URL.fullmatch(i["url"] or "") else label
            lines.append(f"| {i['id']} | {cell(i['firma']) or '?'} | {cell(i['titel'])} | {cell(i['ort']) or '?'} | {i['datum']} | "
                         f"{i['klasse']} | {cell(', '.join(notes))} | {link} |")
    path = os.path.join(wurzel, "suche", "warteschlange.md")
    temp = None
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        handle, temp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-")
        with os.fdopen(handle, "w", encoding="utf-8") as out:
            out.write("\n".join(lines) + "\n")
        os.replace(temp, path)
    except OSError as error:
        if temp and os.path.exists(temp):
            os.unlink(temp)
        raise Refused("speichern_fehlgeschlagen", f"Übersicht nicht schreibbar: {redact(error)}")


READ_ONLY = ("wurzel", "pruefen", "zeige", "auftraege", "faellig", "warteschlange")


# ---------------------------------------------------------------- CLI

def summary(auftrag, wurzel, now):
    ok, reason = due(wurzel, auftrag, now)
    return {"id": auftrag["id"], "name": auftrag["name"], "status": auftrag["status"], "faellig": ok, "grund": reason,
            "letzter_versuch": auftrag["letzter_versuch"], "letzter_erfolg": auftrag["letzter_erfolg"],
            "letzter_lauf": auftrag["letzter_lauf"], "fehler": auftrag["fehler"], "fehler_in_folge": auftrag["fehler_in_folge"]}


def read_payload(args):
    try:
        if args.datei:
            with open(args.datei, encoding="utf-8") as handle:
                return json.load(handle)
        return json.load(sys.stdin)
    except (OSError, ValueError) as error:
        raise Refused("ergebnisdaten_unvollstaendig", f"Eingabe ist kein gültiges JSON: {redact(error)}")


def text_table(items):
    return "\n".join(f"{i['id']} | {i['klasse']} | {i['firma'] or '?'} | {i['titel']} | {i['ort'] or '?'} | "
                     f"{','.join(i['boards'])} | {i['bearbeitung']}" + (f" | {','.join(i['hinweise'])}" if i["hinweise"] else "")
                     for i in items)


def build_parser():
    parser = argparse.ArgumentParser(description="Recurring job search: Suchauftrag, run log, Warteschlange (ST-13 to ST-20).")
    parser.add_argument("--konfiguration", default=os.path.join(DEFAULT_WURZEL, "konfiguration.md"))
    parser.add_argument("--jetzt", help="ISO time JJJJ-MM-TTTHH:MM:SSZ instead of the clock (tests, reproduction)")
    parser.add_argument("--text", action="store_true", help="table instead of JSON for warteschlange")
    sub = parser.add_subparsers(dest="befehl", required=True)

    def add(name, *positional, **options):
        command = sub.add_parser(name)
        for argument in positional:
            command.add_argument(argument)
        for flag, kwargs in options.items():
            command.add_argument("--" + flag.replace("_", "-"), **kwargs)
        return command

    add("wurzel")
    add("anlegen", datei={})
    add("aendern", "id", datei={})
    for name in ("pruefen", "pausieren", "fortsetzen", "beenden", "zeige"):
        add(name, "id")
    add("freigeben", "id", ja={"action": "store_true", "help": "the explicit yes of the user"})
    add("auftraege")
    add("faellig", nur_ids={"action": "store_true"})
    add("lauf-start", "id", trigger={"choices": ("manuell", "geplant"), "default": "manuell"})
    add("board-ergebnis", "id", "lauf", "board", datei={})
    add("lauf-ende", "id", "lauf")
    add("nachtragen", "id", "lauf", "board", datei={})
    add("warteschlange", status={"default": "aktuell", "choices": ("aktuell", "alle") + DECISIONS}, auftrag={},
        klasse={"choices": ("veto", "klaerung", "ohne_treffer", "geaendert", "unvollstaendig")})
    add("entscheiden", "stelle", als={"required": True}, grund={"default": ""}, bis={"default": ""})
    add("aenderung-gesehen", "stelle")
    add("duplikat", "stelle", mit={}, kein={"action": "store_true"})
    add("uebergabe", "stelle")
    add("uebergabe-fertig", "stelle", vorgang={"required": True})
    add("uebergabe-fehler", "stelle", grund={"default": ""})
    return parser


def consume_input(args, wurzel):
    """Delete a result file once its answers are stored; only in `<wurzel>/suche/eingang/` (ST-16 rule 5)."""
    if args.befehl not in ("board-ergebnis", "nachtragen") or not args.datei:
        return
    path = os.path.realpath(args.datei)
    if inside_eingang(wurzel, path) and os.path.isfile(path):
        os.unlink(path)


USER_ONLY = ("anlegen", "aendern", "freigeben", "fortsetzen", "beenden", "entscheiden", "duplikat",
             "aenderung-gesehen", "uebergabe", "uebergabe-fertig", "uebergabe-fehler")


def inside_eingang(wurzel, path):
    return os.path.dirname(os.path.realpath(path)) == os.path.realpath(os.path.join(wurzel, "suche", "eingang"))


def check_scheduled(args, wurzel):
    """What a scheduled (unattended) session may not do, whatever its prompt says (ST-16 rule 5)."""
    if args.befehl in USER_ONLY:
        raise Refused("nur_interaktiv", f"{args.befehl} ist in einem geplanten Lauf nicht erlaubt (ST-16 Regel 5)")
    if args.befehl == "lauf-start" and args.trigger != "geplant":
        raise Refused("nur_interaktiv", "Ein geplanter Lauf startet nur mit --trigger geplant (ST-16 Regel 5)")
    if args.befehl in ("board-ergebnis", "nachtragen") and not (args.datei and inside_eingang(wurzel, args.datei)):
        raise Refused("nur_interaktiv", "Ein geplanter Lauf liest Ergebnisse nur aus <wurzel>/suche/eingang/ (ST-16 Regel 5)")


def run(args):
    wurzel = find_wurzel(args.konfiguration)
    now = parse_time(args.jetzt) if args.jetzt else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    if os.environ.get("STELLENSUCHE_GEPLANT"):
        check_scheduled(args, wurzel)
    if args.befehl in READ_ONLY:
        return dispatch(args, wurzel, now)
    with exclusive(wurzel):
        result = dispatch(args, wurzel, now)
        consume_input(args, wurzel)
        if os.path.isdir(os.path.join(wurzel, "suche")):
            try:  # the overview is a derivation: its failure must not hide the outcome of the command
                write_overview(wurzel, now)
            except Refused as error:
                result["warnung_uebersicht"] = error.meldung
                print(f"warteschlange.md nicht aktualisiert: {error.meldung}", file=sys.stderr)
    return result


def dispatch(args, wurzel, now):
    cmd = args.befehl
    if cmd == "wurzel":
        return {"ok": True, "wurzel": wurzel}
    if cmd == "anlegen":
        return {"ok": True, "auftrag": create_auftrag(wurzel, read_payload(args), now)}
    if cmd == "aendern":
        return {"ok": True, "auftrag": change_auftrag(wurzel, args.id, read_payload(args), now)}
    if cmd == "pruefen":
        auftrag = load_auftrag(wurzel, args.id)
        return {"ok": True, "status": auftrag["status"], "freigabe": approval_template(wurzel, auftrag)}
    if cmd == "freigeben":
        if not args.ja:
            raise Refused("freigabe_nicht_bestaetigt", "Die Freigabe braucht das ausdrückliche Ja des Nutzers (--ja)")
        return {"ok": True, "auftrag": approve_auftrag(wurzel, args.id, now)}
    if cmd == "pausieren":
        return {"ok": True, "auftrag": pause_auftrag(wurzel, args.id, now)}
    if cmd == "fortsetzen":
        return {"ok": True, "auftrag": resume_auftrag(wurzel, args.id, now)}
    if cmd == "beenden":
        return {"ok": True, "auftrag": end_auftrag(wurzel, args.id, now)}
    if cmd == "zeige":
        return {"ok": True, "auftrag": load_auftrag(wurzel, args.id)}
    if cmd in ("auftraege", "faellig"):
        defects = []
        items = [summary(a, wurzel, now) for a in all_auftraege(wurzel, defects)]
        if cmd == "auftraege":
            return {"ok": True, "auftraege": items, "defekte_auftraege": defects}
        return {"ok": True, "faellig": [i["id"] for i in items if i["faellig"]],
                "uebrige": [{"id": i["id"], "grund": i["grund"]} for i in items if not i["faellig"]],
                "defekte_auftraege": defects}
    if cmd == "lauf-start":
        return start_run(wurzel, args.id, args.trigger, now)
    if cmd == "board-ergebnis":
        return record_board(wurzel, args.id, args.lauf, args.board, read_payload(args), now)
    if cmd == "nachtragen":
        return add_later(wurzel, args.id, args.lauf, args.board, read_payload(args), now)
    if cmd == "lauf-ende":
        return finish_run(wurzel, args.id, args.lauf, now)
    if cmd == "warteschlange":
        return list_queue(wurzel, args.status, args.auftrag, args.klasse, now)
    if cmd == "entscheiden":
        return {"ok": True, "stelle": decide(wurzel, args.stelle, args.als, args.grund, args.bis, now)}
    if cmd == "aenderung-gesehen":
        return {"ok": True, "stelle": acknowledge_change(wurzel, args.stelle, now)}
    if cmd == "duplikat":
        if bool(args.mit) == args.kein:
            raise Refused("duplikat_ungueltig", "Entweder --mit <stelle> oder --kein")
        return {"ok": True, "stelle": resolve_duplicate(wurzel, args.stelle, args.mit, now)}
    if cmd == "uebergabe":
        return prepare_handoff(wurzel, args.stelle, now)
    if cmd == "uebergabe-fertig":
        return {"ok": True, "stelle": complete_handoff(wurzel, args.stelle, args.vorgang, now)}
    return fail_handoff(wurzel, args.stelle, args.grund, now)


def main(argv):
    args = build_parser().parse_args(argv[1:])
    try:
        result = run(args)
    except Blocker as error:
        print(f"Blocker: {error}", file=sys.stderr)
        return 1
    except Refused as error:
        print(json.dumps({"ok": False, "code": error.code, "meldung": error.meldung}, ensure_ascii=False))
        print(f"{error.code}: {error.meldung}", file=sys.stderr)
        return 3
    for defect in result.get("defekte_auftraege", []):
        print(f"defekter Suchauftrag {defect['datei']}: {defect['meldung']}", file=sys.stderr)
    if args.befehl == "faellig" and args.nur_ids:
        print("\n".join(result["faellig"]))
    elif args.text and args.befehl == "warteschlange":
        print(text_table(result["stellen"]))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
