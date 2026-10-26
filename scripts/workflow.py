#!/usr/bin/env python3
"""Workflow orchestration of the application process (spec workflow WF-1 to WF-14).

One persistent store of tasks with dependencies, attempts, leases, retries and approvals. The facts stay where
they live: the status of an application is `status` in `vorgang.md` (LS-6), a search is a Suchauftrag
(`stellensuche.py`). The workflow keeps no second application status. It reads the files, decides which task may
run next, and checks the postcondition of a task before the task counts as done.

It runs no skill itself: an agent takes a ready task (`uebernehmen`), does the work with the named skill and reports
(`fertig` or `fehler`). Approvals and everything that only the user may do (the plan, sending) stay with the user.

State: `<wurzel>/workflow/aufgaben.json`; readable derivation: `<wurzel>/workflow/uebersicht.md`.

Usage: workflow.py [--konfiguration PFAD] [--jetzt ISO] <befehl> ...
Commands: wurzel, starten, abgleichen, laufen, naechste, uebernehmen, fertig, fehler, weiter, freigeben, ablehnen, ausfuehren,
ausgang, wiederholen, abbrechen, anlegen, zeige, uebersicht, grenzen.
Output is one JSON object. Exit code 0 ok, 2 the command ran but reports ok=false (for example `fertig` with a missing result), 3 refused (`code` and `meldung`), 1 blocker. Standard library only.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import stellensuche as ss  # noqa: E402
from grundlage_hash import sha256_file  # noqa: E402
from stellensuche import Blocker, Refused, atomic_write, clean_text, digest, load_json, parse_time, redact, stamp  # noqa: E402

DEFAULT_LIMITS = {"laufende_max": 2, "neu_max_je_lauf": 10, "aufgaben_max": 200, "lease_minuten": 60, "versuche_max": 3}
LIMIT_BOUNDS = {"laufende_max": (1, 10), "neu_max_je_lauf": (1, 50), "aufgaben_max": (10, 1000), "lease_minuten": (5, 1440),
                "versuche_max": (1, 10)}
BACKOFF_MINUTES = (5, 30, 180)
KEEP_LOG = 50
LOCK = ("workflow", ".workflow.lock")

# status values of a task (German, like the status values of a Vorgang)
WARTEND, BEREIT, LAEUFT = "wartend", "bereit", "laeuft"
FREIGABE, EINGABE, WIEDERHOLUNG = "wartet_auf_freigabe", "wartet_auf_eingabe", "wiederholung_geplant"
ERLEDIGT, FEHLGESCHLAGEN, BLOCKIERT, ABGEBROCHEN = "erledigt", "fehlgeschlagen", "blockiert", "abgebrochen"
STATUS = (WARTEND, BEREIT, LAEUFT, FREIGABE, EINGABE, WIEDERHOLUNG, ERLEDIGT, FEHLGESCHLAGEN, BLOCKIERT, ABGEBROCHEN)
OFFEN = (WARTEND, BEREIT, LAEUFT, FREIGABE, EINGABE, WIEDERHOLUNG, BLOCKIERT)  # neither finished nor given up

# the matrix of allowed transitions (WF-4); anything else is refused
UEBERGAENGE = {
    WARTEND: {BEREIT, FREIGABE, EINGABE, BLOCKIERT, ABGEBROCHEN, ERLEDIGT},
    BEREIT: {LAEUFT, WARTEND, FREIGABE, EINGABE, BLOCKIERT, ABGEBROCHEN, ERLEDIGT},
    LAEUFT: {ERLEDIGT, WIEDERHOLUNG, FEHLGESCHLAGEN, EINGABE, BLOCKIERT, FREIGABE, ABGEBROCHEN},
    FREIGABE: {BEREIT, WARTEND, EINGABE, ERLEDIGT, BLOCKIERT, ABGEBROCHEN},
    EINGABE: {BEREIT, WARTEND, FREIGABE, ERLEDIGT, BLOCKIERT, ABGEBROCHEN},
    WIEDERHOLUNG: {BEREIT, WARTEND, EINGABE, FREIGABE, FEHLGESCHLAGEN, BLOCKIERT, ERLEDIGT, ABGEBROCHEN},
    FEHLGESCHLAGEN: {BEREIT, ABGEBROCHEN},
    BLOCKIERT: {WARTEND, BEREIT, FREIGABE, EINGABE, ERLEDIGT, ABGEBROCHEN},
    ERLEDIGT: {FREIGABE},  # only an approval whose content changed afterwards
    ABGEBROCHEN: set(),
}

# error classes an agent reports with `fehler` (WF-8)
RETRY_KLASSEN = {"vorlaeufig", "dienst", "zeitlimit", "abbruch", "ergebnis_fehlt"}
KLASSEN = RETRY_KLASSEN | {"eingabe", "freigabe", "berechtigung", "qualitaet", "daten", "dauerhaft", "unklar"}

# status chain of a Vorgang (LS-6) as ranks; `in Arbeit` lies between erstellt and geprüft
RANG = {"erfasst": 1, "analysiert": 2, "geplant": 3, "erstellt": 4, "in Arbeit": 4.5, "geprüft": 5, "versendet": 6}
ENDSTATUS = {"zusage", "absage", "abgelehnt", "zurückgezogen", "ohne Antwort"}
DOKUMENTE = ("lebenslauf.md", "anschreiben.md", "motivationsschreiben.md", "email.md", "anschreiben-portal.txt",
             "motivationsschreiben-portal.txt")
KUERZEL = re.compile(r"[a-z0-9][a-z0-9-]*")
DATEINAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.(?:md|txt)")

OPTIONAL = {"passung"}  # a step the user may cancel without blocking what follows (the fit check is advice, not a gate)
ADAPTER = {}  # task type -> function(task, freigabe) -> {"gesendet": bool, "sicher": bool, "beleg": str}; none ships (WF-7)


# ---------------------------------------------------------------- helpers

def rang(meta):
    status = (meta or {}).get("status", "")
    return 7 if status in ENDSTATUS or status in ("rückmeldung", "gespräch", "angebot", "verhandlung") else RANG.get(status, 0)


def datei_hash(path):
    return sha256_file(path) if os.path.isfile(path) else ""


def hash_von(wurzel, vorgang, dateien):
    """Hash over the named files of a Vorgang (existing ones only), or '' when none exists."""
    teile = [(name, datei_hash(os.path.join(wurzel, vorgang, name))) for name in sorted(dateien)]
    return digest(*[f"{name}={h}" for name, h in teile if h]) if any(h for _, h in teile) else ""


def heute(now):
    """The local date of the machine: the dates the user types (`ab`, `faellig`, `wiedervorlage`) are local dates."""
    return now.astimezone().date().isoformat()


def vorgang_dir(w, t):
    return os.path.join(w, t["bezug"]["vorgang"])


def meta_von(w, t):
    return ss.vorgang_meta(os.path.join(vorgang_dir(w, t), "vorgang.md"))


def hat(w, t, name):
    return os.path.isfile(os.path.join(vorgang_dir(w, t), name))


# ---------------------------------------------------------------- the catalog of task types (WF-3)

def v_analyse(w, t, now):
    if meta_von(w, t) is None or not hat(w, t, "stellenanzeige.md"):
        return "eingabe", "stellenanzeige.md oder vorgang.md fehlt: erst die Stelle erfassen (S1)"
    return None


def a_analyse(w, t, now):
    ok = rang(meta_von(w, t)) >= RANG["analysiert"] and hat(w, t, "analyse.md")
    return ok, "vorgang.md steht noch vor `analysiert` oder analyse.md fehlt"


def a_datei(name):
    return lambda w, t, now: (hat(w, t, name), f"{name} fehlt")


def a_plan(w, t, now):
    meta, plan = meta_von(w, t), False
    if meta is not None:
        try:
            with open(os.path.join(vorgang_dir(w, t), "vorgang.md"), encoding="utf-8-sig", errors="replace") as handle:
                plan = re.search(r"^## Plan\s*$", handle.read(), re.M) is not None
        except OSError:  # the file vanished or is being rewritten: not recognised now, the next reconciliation looks again
            plan = False
    return rang(meta) >= RANG["geplant"] and plan, "der Plan ist nicht freigegeben und gespeichert (Plan-Gate von job-application-solution)"


def a_unterlagen(w, t, now):
    ok = rang(meta_von(w, t)) >= RANG["erstellt"] and hat(w, t, "lebenslauf.md") and hat(w, t, "anschreiben.md")
    return ok, "Lebenslauf oder Anschreiben fehlt, oder vorgang.md steht noch vor `erstellt`"


def a_pruefung(w, t, now):
    return rang(meta_von(w, t)) >= RANG["geprüft"], "der Qualitätscheck steht nicht auf `geprüft` (offene Blocker)"


def a_versand(w, t, now):
    meta = meta_von(w, t) or {}
    return rang(meta) >= RANG["versendet"] and bool(meta.get("versendet_am")), \
        "der Nutzer hat den Versand noch nicht in vorgang.md eingetragen (S7)"


def v_nachfassen(w, t, now):
    if rang(meta_von(w, t)) < RANG["versendet"]:
        return "warten", "die Bewerbung ist noch nicht versendet"
    return None


def a_nachfassen(w, t, now):
    path = os.path.join(vorgang_dir(w, t), "email-nachfassen.md")
    return os.path.isfile(path) and os.path.getmtime(path) >= t["epoch"], "email-nachfassen.md wurde nicht neu geschrieben"


def v_suche(w, t, now):
    try:
        auftrag = ss.load_auftrag(w, t["bezug"]["auftrag"])
    except Refused as error:
        return "blockiert", error.meldung
    problem = ss.approval_problem(w, auftrag)
    if problem:
        if problem[0] in ("beendet", "pausiert"):
            return "blockiert", f"Suchauftrag {problem[0]}: {problem[1]}"
        return "freigabe", f"{problem[1]} (die Freigabe gehört der Stellensuche, nicht dem Workflow)"
    return None


def a_suche(w, t, now):
    try:
        auftrag = ss.load_auftrag(w, t["bezug"]["auftrag"])
    except Refused:
        return False, "Suchauftrag nicht lesbar"
    letzter = auftrag.get("letzter_lauf") or {}
    neu = auftrag["lauf_zaehler"] > t["bezug"].get("zaehler", -1) and letzter.get("am", "") >= t["erstellt"]
    return neu and letzter.get("status") in ("ok", "ok_ohne_treffer", "teilweise"), \
        "kein erfolgreicher Lauf seit Anlage der Aufgabe (`stellensuche.py auftraege`)"


def e_vorgang(*namen):
    return lambda w, t: [f"{t['bezug']['vorgang']}/{n}" for n in namen]


TYPEN = {
    "analyse": dict(ausfuehrung="agent", skill="job-application-posting-analysis", prio=3, voraussetzung=v_analyse,
                    abschluss=a_analyse, eingaben=e_vorgang("stellenanzeige.md"), ergebnis="analyse.md",
                    zweck="Stellenanzeige analysieren (S2)"),
    "passung": dict(ausfuehrung="agent", skill="job-application-fit-check", prio=3, abschluss=a_datei("passung.md"),
                    eingaben=e_vorgang("analyse.md"), ergebnis="passung.md", zweck="Passung gegen das Wunschprofil prüfen"),
    "plan": dict(ausfuehrung="nutzer", skill="job-application-solution (Plan-Gate, Schritt 3)", prio=5, abschluss=a_plan,
                 eingaben=e_vorgang("analyse.md"), ergebnis="vorgang.md", zweck="Plan prüfen und freigeben (S3)"),
    "unterlagen": dict(ausfuehrung="agent", skill="job-application-solution (Schritte 4 und 5)", prio=3, abschluss=a_unterlagen,
                       eingaben=e_vorgang("analyse.md"), ergebnis="lebenslauf.md", zweck="Unterlagen erstellen (S4)"),
    "pruefung": dict(ausfuehrung="agent", skill="job-application-quality-gate", prio=3, abschluss=a_pruefung,
                     eingaben=e_vorgang(*DOKUMENTE), ergebnis="pruefbericht.md", zweck="Qualitätscheck ausführen (S5)"),
    "versand_freigabe": dict(ausfuehrung="nutzer", skill="Entscheidung des Nutzers", prio=5, nur_freigabe=True,
                             inhalt=lambda w, t: hash_von(w, t["bezug"]["vorgang"], DOKUMENTE),
                             zweck="Versandpaket freigeben (genau diese Unterlagen)"),
    "versand": dict(ausfuehrung="nutzer", skill="der Nutzer sendet selbst (S7); kein Versandadapter ausgeliefert", prio=5,
                    extern=True, abschluss=a_versand, eingaben=e_vorgang(*DOKUMENTE),
                    zweck="Bewerbung senden und in vorgang.md eintragen (S7)"),
    "nachfassen": dict(ausfuehrung="agent", skill="job-application-email-create (Variante nachfassen)", prio=4,
                       voraussetzung=v_nachfassen, abschluss=a_nachfassen, ergebnis="email-nachfassen.md",
                       zweck="Nachfass-Entwurf vorbereiten (Wiedervorlage fällig)"),
    "suche": dict(ausfuehrung="agent", skill="job-application-job-search (Suchauftrag)", prio=2, voraussetzung=v_suche,
                  abschluss=a_suche, zweck="Suchauftrag ausführen"),
    "nachricht_senden": dict(ausfuehrung="adapter", skill="Versandadapter (A-02, nicht ausgeliefert)", prio=4, extern=True,
                             freigabe=True, inhalt=lambda w, t: hash_von(w, t["bezug"]["vorgang"], [t["bezug"].get("datei", "-")]),
                             zweck="Nachricht senden (nur mit Adapter und gültiger Freigabe)"),
}

BEWERBUNG = (("analyse", ()), ("passung", ("analyse",)), ("plan", ("analyse", "passung")), ("unterlagen", ("plan",)),
             ("pruefung", ("unterlagen",)), ("versand_freigabe", ("pruefung",)), ("versand", ("versand_freigabe",)))


# ---------------------------------------------------------------- store

def store_path(wurzel):
    return os.path.join(wurzel, "workflow", "aufgaben.json")


FELDER = {"id", "typ", "bezug", "status", "nach", "versuche", "entscheidung", "lease", "verlauf"}
TYPEN_DER_FELDER = {"bezug": dict, "nach": list, "versuche": list, "verlauf": list}


def standardwerte(task):
    """Fields a task may lack (an older or hand-written file): filled with their defaults, never invented results."""
    return {"hinweis": "", "erstellt": "", "geaendert": "", "epoch": 0, "ab": "", "faellig": "", "zweck": TYPEN[task["typ"]]["zweck"],
            "prioritaet": TYPEN[task["typ"]]["prio"], "versuche_ab": 0, "letzter_fehler": None, "ergebnis": None, "eingaben": {},
            "veraltet": False, "extern_begonnen": "", "naechster_versuch": "", "halt": ""}


def lade(wurzel):
    daten = load_json(store_path(wurzel), {"version": 1, "grenzen": dict(DEFAULT_LIMITS), "aufgaben": {}})
    if daten.get("version") != 1 or not isinstance(daten.get("aufgaben"), dict):
        raise Refused("speicher_ungueltig", "workflow/aufgaben.json hat kein bekanntes Format (version 1)")
    for task_id, task in daten["aufgaben"].items():
        if not isinstance(task, dict) or FELDER - set(task) or task["id"] != task_id \
                or not isinstance(task["typ"], str) or not isinstance(task["status"], str) \
                or task["typ"] not in TYPEN or task["status"] not in STATUS or any(not isinstance(task[k], t) for k, t in TYPEN_DER_FELDER.items()) \
                or not (task["lease"] is None or isinstance(task["lease"], dict) and "bis" in task["lease"]) \
                or not all(isinstance(d, str) for d in task["nach"]):
            raise Refused("speicher_ungueltig", f"Die Aufgabe {redact(task_id, 60)} in workflow/aufgaben.json ist unvollständig oder unbekannt")
        try:
            pruefe_bezug(task["typ"], task["bezug"])
        except Refused as error:
            raise Refused("speicher_ungueltig", f"Die Aufgabe {redact(task_id, 60)}: {error.meldung}")
        if any(not isinstance(v, dict) or not {"nr", "ergebnis"} <= set(v) for v in task["versuche"]) or not (
                task["entscheidung"] is None or isinstance(task["entscheidung"], dict) and {"art", "kontext_hash"} <= set(task["entscheidung"])):
            raise Refused("speicher_ungueltig", f"Die Aufgabe {redact(task_id, 60)} hat unvollständige Versuche oder eine unvollständige Entscheidung")
        for feld, wert in standardwerte(task).items():
            task.setdefault(feld, wert)
    gespeichert = daten.get("grenzen", {})
    if not isinstance(gespeichert, dict) or any(k in LIMIT_BOUNDS and not (isinstance(v, int) and not isinstance(v, bool)
                                                and LIMIT_BOUNDS[k][0] <= v <= LIMIT_BOUNDS[k][1]) for k, v in gespeichert.items()):
        raise Refused("speicher_ungueltig", "Die Grenzen in workflow/aufgaben.json sind keine Zahlen im erlaubten Bereich")
    daten["grenzen"] = {**DEFAULT_LIMITS, **gespeichert}
    try:
        reihenfolge(daten)
    except Refused as error:  # a dangling reference or a cycle in the file: stop before any command changes anything
        raise Refused("speicher_ungueltig", error.meldung)
    return daten


def sichere(wurzel, daten):
    atomic_write(store_path(wurzel), daten)


def verlauf(task, now, text):
    task["verlauf"] = (task["verlauf"] + [{"am": stamp(now), "ereignis": clean_text(text, 200)}])[-KEEP_LOG:]


def setze(task, neu, now, text="", hinweis=None):
    """Change a status through the matrix of allowed transitions (WF-4)."""
    if neu == task["status"]:
        if hinweis is not None:
            task["hinweis"] = hinweis
        return False
    if neu not in UEBERGAENGE[task["status"]]:
        raise Refused("uebergang_unzulaessig", f"{task['id']}: {task['status']} -> {neu} ist nicht erlaubt")
    verlauf(task, now, f"{task['status']} -> {neu}" + (f": {text}" if text else ""))
    task["status"], task["geaendert"] = neu, stamp(now)
    task["hinweis"] = hinweis if hinweis is not None else ""
    return True


def pruefe_bezug(typ, bezug):
    """The reference of a task: exactly the kind the type needs, written as slugs and a plain file name (WF-13 rule 3)."""
    gebraucht = "auftrag" if typ == "suche" else "vorgang"
    if not isinstance(bezug, dict) or not bezug.get(gebraucht) or (bezug.get("vorgang") and bezug.get("auftrag")):
        raise Refused("aufgabe_ungueltig", f"Eine Aufgabe vom Typ {typ} hat als bezug genau {'einen Suchauftrag' if gebraucht == 'auftrag' else 'einen Vorgang'}")
    if not all(isinstance(bezug.get(k, "x"), str) and KUERZEL.fullmatch(bezug.get(k, "x")) for k in ("vorgang", "auftrag")) or \
            (bezug.get("datei") is not None and not (isinstance(bezug["datei"], str) and DATEINAME.fullmatch(bezug["datei"]))):
        raise Refused("aufgabe_ungueltig", "bezug.vorgang und bezug.auftrag sind Kürzel aus a-z, 0-9 und -; datei ist ein Dateiname")


def neue_aufgabe(daten, typ, bezug, now, nach=(), ab="", faellig="", suffix=""):
    """Create a task from the catalog. An id is stable: the same id twice gives back the first task (WF-6)."""
    if typ not in TYPEN:
        raise Refused("aufgabentyp_unbekannt", f"Aufgabentyp {redact(typ, 40)} ist nicht im Katalog")
    pruefe_bezug(typ, bezug)
    if (ab and ss.valid_date(ab) != ab) or (faellig and ss.valid_date(faellig) != faellig):
        raise Refused("aufgabe_ungueltig", "ab und faellig sind echte Daten der Form JJJJ-MM-TT")
    if not suffix and typ == "nachricht_senden" and bezug.get("datei"):
        suffix = bezug["datei"]  # one message per file: the approval covers exactly that file
    task_id = f"{typ}:{bezug.get('vorgang') or bezug.get('auftrag')}" + (f":{suffix}" if suffix else "")
    if task_id in daten["aufgaben"]:
        vorhanden = daten["aufgaben"][task_id]
        if vorhanden["bezug"] != bezug or (ab and ab != vorhanden["ab"]) or (faellig and faellig != vorhanden["faellig"]):
            raise Refused("aufgabe_existiert", f"{task_id} gibt es schon mit anderen Angaben (bezug, ab, faellig); sie wird nicht stillschweigend weiterverwendet")
        return daten["aufgaben"][task_id], False
    if len(daten["aufgaben"]) >= daten["grenzen"]["aufgaben_max"]:
        raise Refused("budget_erschoepft", f"Es gibt schon {daten['grenzen']['aufgaben_max']} Aufgaben (aufgaben_max)")
    katalog = TYPEN[typ]
    task = {"id": task_id, "typ": typ, "bezug": bezug, "zweck": katalog["zweck"], "status": WARTEND, "hinweis": "",
            "erstellt": stamp(now), "geaendert": stamp(now), "epoch": int(now.timestamp()), "ab": ab, "faellig": faellig,
            "prioritaet": katalog["prio"], "nach": list(nach), "versuche": [], "versuche_ab": 0, "letzter_fehler": None,
            "ergebnis": None, "eingaben": {}, "veraltet": False, "entscheidung": None, "lease": None,
            "extern_begonnen": "", "naechster_versuch": "", "halt": "", "verlauf": []}
    verlauf(task, now, "angelegt")
    daten["aufgaben"][task_id] = task
    try:
        reihenfolge(daten)
    except Refused:
        del daten["aufgaben"][task_id]
        raise
    return task, True


def reihenfolge(daten):
    """Tasks in dependency order. A missing reference or a cycle is refused (WF-5)."""
    tasks, fertig, unterwegs, ordnung = daten["aufgaben"], set(), [], []

    def besuche(task_id):
        if task_id in fertig:
            return
        if task_id in unterwegs:
            raise Refused("zyklus", "Zirkuläre Abhängigkeit: " + " -> ".join(unterwegs[unterwegs.index(task_id):] + [task_id]))
        unterwegs.append(task_id)
        for dep in tasks[task_id]["nach"]:
            if dep not in tasks:
                raise Refused("abhaengigkeit_unbekannt", f"{task_id} verweist auf {dep}, das es nicht gibt")
            besuche(dep)
        unterwegs.pop()
        fertig.add(task_id)
        ordnung.append(task_id)

    for task_id in sorted(tasks):
        besuche(task_id)
    return ordnung


# ---------------------------------------------------------------- approvals

def braucht_freigabe(task):
    katalog = TYPEN[task["typ"]]
    return bool(katalog.get("freigabe") or katalog.get("nur_freigabe"))


def freigabe_gueltig(w, task):
    """True when no approval is needed, or the approval of the user covers exactly the content as it is now (WF-7)."""
    if not braucht_freigabe(task):
        return True
    entscheidung, aktuell = task["entscheidung"], TYPEN[task["typ"]]["inhalt"](w, task)
    return bool(entscheidung and entscheidung["art"] == "erteilt" and aktuell and entscheidung["kontext_hash"] == aktuell)


# ---------------------------------------------------------------- reconcile (WF-6)

def schnappschuss(w, task):
    liste = TYPEN[task["typ"]].get("eingaben")
    return {path: datei_hash(os.path.join(w, path)) for path in (liste(w, task) if liste else [])}


def pruefe_veraltet(w, task):
    """A finished result is stale when an input changed after it was made; it is shown and never reset by itself."""
    task["veraltet"] = bool(task["eingaben"]) and any(datei_hash(os.path.join(w, p)) != h for p, h in task["eingaben"].items())


def schliesse_versuch(task, now, ergebnis, klasse="", grund=""):
    if task["versuche"] and task["versuche"][-1]["ergebnis"] == "laeuft":
        task["versuche"][-1].update(ende=stamp(now), ergebnis=ergebnis, klasse=klasse, grund=redact(grund))


def erledige(w, task, now, text, ref=None, hash_wert=None):
    setze(task, ERLEDIGT, now, text)
    katalog = TYPEN[task["typ"]]
    task["eingaben"] = schnappschuss(w, task)
    pfad = ref if ref is not None else katalog.get("ergebnis")
    if hash_wert is None:
        hash_wert = datei_hash(os.path.join(vorgang_dir(w, task), pfad)) if pfad and task["bezug"].get("vorgang") else ""
    task["ergebnis"] = {"ref": pfad or "", "hash": hash_wert, "am": stamp(now)}
    task["lease"], task["veraltet"], task["halt"], task["naechster_versuch"] = None, False, "", ""
    task["extern_begonnen"] = ""  # the outcome is known now
    schliesse_versuch(task, now, "ok")


def beende_laufenden(task, now, grund):
    """A running task that is stopped from outside (its Vorgang is gone or finished): the lease and the open attempt end too."""
    if task["lease"] or (task["versuche"] and task["versuche"][-1]["ergebnis"] == "laeuft"):
        schliesse_versuch(task, now, "fehler", "abbruch", grund)
    task["lease"] = None


def zustand(task):
    return task["status"], task["hinweis"]


def bewerte(w, daten, task, now):
    """Bring one task in line with the files, its dependencies and the clock. Returns True when it changed."""
    katalog, vorher, tasks = TYPEN[task["typ"]], zustand(task), daten["aufgaben"]
    vorgang = task["bezug"].get("vorgang")
    if task["status"] == ABGEBROCHEN:
        return False
    if vorgang and not os.path.isdir(os.path.join(w, vorgang)):
        if task["status"] in OFFEN:
            beende_laufenden(task, now, "Vorgangsordner fehlt")
            setze(task, BLOCKIERT, now, "Vorgangsordner fehlt", "Den Ordner des Vorgangs gibt es nicht mehr")
        return zustand(task) != vorher
    meta = meta_von(w, task) if vorgang else None
    if task["status"] == ERLEDIGT:
        if katalog.get("nur_freigabe") and not freigabe_gueltig(w, task) and not any(
                tasks[o]["status"] == ERLEDIGT and task["id"] in tasks[o]["nach"] for o in tasks):
            task["entscheidung"] = None
            setze(task, FREIGABE, now, "Inhalt seit der Freigabe geändert", "Die Unterlagen haben sich seit der Freigabe geändert")
        pruefe_veraltet(w, task)
        return zustand(task) != vorher
    if meta is not None and meta.get("status") in ENDSTATUS:
        beende_laufenden(task, now, "Vorgang abgeschlossen")
        setze(task, ABGEBROCHEN, now, "Vorgang abgeschlossen", f"Der Vorgang hat den Endstatus {meta.get('status')}")
        return True
    # reality wins: work done outside the workflow is recognised from the files (never an external action of an adapter)
    if katalog.get("abschluss") and katalog["ausfuehrung"] != "adapter" and task["status"] not in (FEHLGESCHLAGEN, LAEUFT):
        if katalog["abschluss"](w, task, now)[0]:
            ohne = [d for d in task["nach"] if tasks[d]["status"] != ERLEDIGT]
            erledige(w, task, now, "Zustand aus dem Vorgang übernommen")
            if ohne:
                task["hinweis"] = "Voraussetzungen im Workflow waren nicht erledigt; der Vorgang zeigt den Stand schon"
            for dep in ohne:  # an approval is never recognised from files; it is no longer needed once the step is done
                if TYPEN[tasks[dep]["typ"]].get("nur_freigabe") and tasks[dep]["status"] in OFFEN:
                    setze(tasks[dep], ABGEBROCHEN, now, "nicht mehr nötig", f"Nicht mehr nötig: {task['id']} ist schon erledigt")
            return True
    if task["status"] == FEHLGESCHLAGEN:
        return False
    if task["status"] == EINGABE and task["extern_begonnen"]:
        return False  # the outcome of an external action is unclear: only `ausgang` of the user resolves it, never time or a retry
    if task["halt"] and task["status"] in (EINGABE, FREIGABE, BLOCKIERT):
        return False  # an agent reported that it needs something: only the user's `weiter` lifts this, never the next reconciliation
    if task["status"] != LAEUFT:
        for dep in task["nach"]:  # a failed, blocked or cancelled step never releases what follows
            if tasks[dep]["status"] in (FEHLGESCHLAGEN, BLOCKIERT) or (tasks[dep]["status"] == ABGEBROCHEN and tasks[dep]["typ"] not in OPTIONAL):
                setze(task, BLOCKIERT, now, f"Voraussetzung {dep} ist {tasks[dep]['status']}",
                      f"Voraussetzung {dep} ist {tasks[dep]['status']}")
                return zustand(task) != vorher
        offene = [d for d in task["nach"] if tasks[d]["status"] != ERLEDIGT and not (tasks[d]["status"] == ABGEBROCHEN and tasks[d]["typ"] in OPTIONAL)]
        if offene:
            setze(task, WARTEND, now, "", "wartet auf: " + ", ".join(offene))
            return zustand(task) != vorher
    if task["status"] == LAEUFT:
        return lease_pruefen(w, daten, task, now)
    if task["status"] == WIEDERHOLUNG and task["naechster_versuch"] > stamp(now):
        return False
    if task["ab"] and heute(now) < task["ab"]:
        setze(task, WARTEND, now, "", f"frühestens ab {task['ab']}")
        return zustand(task) != vorher
    if katalog.get("voraussetzung"):
        problem = katalog["voraussetzung"](w, task, now)
        if problem:
            art, text = problem
            setze(task, {"eingabe": EINGABE, "blockiert": BLOCKIERT, "freigabe": FREIGABE, "warten": WARTEND}[art], now, text, text)
            return zustand(task) != vorher
    if braucht_freigabe(task):
        aktuell = katalog["inhalt"](w, task)
        if not aktuell:
            setze(task, EINGABE, now, "nichts zu genehmigen", "Es gibt noch keine Unterlagen, die freigegeben werden könnten")
            return zustand(task) != vorher
        if task["entscheidung"] and task["entscheidung"]["kontext_hash"] != aktuell:
            task["entscheidung"] = None
            verlauf(task, now, "Freigabe verfallen: Inhalt geändert")
        if task["entscheidung"] and task["entscheidung"]["art"] == "abgelehnt":
            setze(task, ABGEBROCHEN, now, "Freigabe abgelehnt")
            return True
        if not freigabe_gueltig(w, task):
            setze(task, FREIGABE, now, "Freigabe des Nutzers nötig", "Die Freigabe des Nutzers für genau diesen Inhalt fehlt")
            return zustand(task) != vorher
        if katalog.get("nur_freigabe"):
            erledige(w, task, now, "Freigabe liegt vor", ref="freigabe", hash_wert=task["entscheidung"]["kontext_hash"])
            return True
    setze(task, BEREIT, now, "", "")
    return zustand(task) != vorher


def lease_pruefen(w, daten, task, now):
    """A running task whose lease ran out: an internal one counts as an aborted attempt, an external one is unclear."""
    if not task["lease"] or task["lease"]["bis"] > stamp(now):
        return False
    if TYPEN[task["typ"]].get("extern") and task["extern_begonnen"]:
        schliesse_versuch(task, now, "fehler", "unklar", "Lease abgelaufen nach begonnener externer Aktion")
        setze(task, EINGABE, now, "Lease abgelaufen nach begonnener externer Aktion",
              "Ausgang unklar: prüfe, ob die Aktion ausgeführt wurde, und entscheide mit `ausgang`")
        task["lease"] = None
        return True
    versuch_endet(daten, task, now, "abbruch", "Die Sitzung hat sich nicht zurückgemeldet (Lease abgelaufen)")
    return True


def versuch_endet(daten, task, now, klasse, grund):
    """The running attempt failed with an error class: decide what follows (WF-8). External actions are never repeated."""
    if klasse not in KLASSEN:
        raise Refused("klasse_unbekannt", f"Fehlerklasse ist eine aus: {', '.join(sorted(KLASSEN))}")
    schliesse_versuch(task, now, "fehler", klasse, grund)
    task["lease"] = None
    task["letzter_fehler"] = {"klasse": klasse, "grund": redact(grund), "am": stamp(now)}
    extern = bool(TYPEN[task["typ"]].get("extern"))
    anzahl = len(task["versuche"]) - task["versuche_ab"]
    text = f"{klasse}: {redact(grund, 120)}"
    if klasse in ("eingabe", "freigabe", "berechtigung", "qualitaet"):
        task["halt"] = klasse  # stays until the user lifts it with `weiter`
    if klasse == "eingabe":
        setze(task, EINGABE, now, text, "Es fehlen Angaben: " + redact(grund, 160))
    elif klasse == "freigabe":
        setze(task, FREIGABE, now, text, "Eine Freigabe des Nutzers fehlt: " + redact(grund, 160))
    elif klasse in ("berechtigung", "qualitaet"):
        setze(task, BLOCKIERT, now, text, redact(grund, 200))
    elif klasse in ("daten", "dauerhaft"):
        setze(task, FEHLGESCHLAGEN, now, text, redact(grund, 200))
    elif extern and (klasse == "unklar" or task["extern_begonnen"]):
        setze(task, EINGABE, now, text, "Ausgang unklar: prüfe, ob die Aktion ausgeführt wurde, und entscheide mit `ausgang`")
    elif extern or anzahl >= daten["grenzen"]["versuche_max"]:
        setze(task, FEHLGESCHLAGEN, now, text, redact(grund, 200) + (" (keine automatische Wiederholung einer externen Aktion)" if extern else ""))
    else:
        warte = BACKOFF_MINUTES[min(anzahl, len(BACKOFF_MINUTES)) - 1]
        task["naechster_versuch"] = stamp(now + dt.timedelta(minutes=warte))
        setze(task, WIEDERHOLUNG, now, f"{text}; Versuch {anzahl + 1} frühestens in {warte} Minuten",
              f"nächster Versuch ab {task['naechster_versuch']}")


def abgleichen(w, daten, now):
    """Reconcile every task in dependency order. Returns the ids of the changed tasks."""
    return [task_id for task_id in reihenfolge(daten) if bewerte(w, daten, daten["aufgaben"][task_id], now)]


# ---------------------------------------------------------------- planning (WF-9)

def starte_vorgang(w, daten, slug, now):
    """Create the chain of a Vorgang, all of it or nothing (a chain cut off by the cap would never be completed)."""
    if not KUERZEL.fullmatch(slug or "") or not os.path.isfile(os.path.join(w, slug, "vorgang.md")):
        raise Refused("vorgang_unbekannt", f"Kein Vorgang {redact(slug, 60)} mit vorgang.md in der Wurzel")
    mit_passung = kettenlaenge(w) == len(BEWERBUNG)
    fehlend = sum(1 for typ, _ in BEWERBUNG if (typ != "passung" or mit_passung) and f"{typ}:{slug}" not in daten["aufgaben"])
    if len(daten["aufgaben"]) + fehlend > daten["grenzen"]["aufgaben_max"]:
        raise Refused("budget_erschoepft", f"Die Kette braucht {fehlend} Aufgaben, aufgaben_max ({daten['grenzen']['aufgaben_max']}) reicht nicht")
    neu, ids = [], {}
    nach_vorher = {i: list(t["nach"]) for i, t in daten["aufgaben"].items()}
    for typ, nach in BEWERBUNG:
        if typ == "passung" and not mit_passung and f"passung:{slug}" not in daten["aufgaben"]:
            continue
        task, angelegt = neue_aufgabe(daten, typ, {"vorgang": slug}, now, nach=[ids[d] for d in nach if d in ids])
        ids[typ] = task["id"]
        if angelegt:
            neu.append(task["id"])
        for dep in (ids[d] for d in nach if d in ids):  # repair: a step added later (the fit check) joins what follows
            if dep not in task["nach"] and task["status"] in (WARTEND, BEREIT, FREIGABE, EINGABE, BLOCKIERT):
                task["nach"].append(dep)
    try:
        reihenfolge(daten)
    except Refused:  # a repair that would close a cycle (a hand-edited store) is undone before anything is saved
        for task_id in neu:
            del daten["aufgaben"][task_id]
        for task_id, nach in nach_vorher.items():
            daten["aufgaben"][task_id]["nach"] = nach
        raise
    return neu


def kettenlaenge(w):
    """Number of tasks the chain of a new Vorgang creates (the fit check only with a confirmed Wunschprofil)."""
    mit_passung = ss.read_frontmatter(os.path.join(w, "wunschprofil.md")).get("bestaetigt") == "ja"
    return sum(1 for typ, _ in BEWERBUNG if typ != "passung" or mit_passung)


def plane(w, daten, now):
    """Create what is due from the state that exists, within the budget per run. Executes nothing (WF-9)."""
    budget, neu, zurueck, uebersprungen, defekte = daten["grenzen"]["neu_max_je_lauf"], [], [], [], []

    def anlegen(*args, **kwargs):
        nonlocal budget
        if budget <= 0:
            zurueck.append(args[0] + ":" + str(args[1].get("vorgang") or args[1].get("auftrag")))
            return None
        task, angelegt = neue_aufgabe(daten, *args, **kwargs)
        if angelegt:
            budget -= 1
            neu.append(task["id"])
        return task

    try:
        mit_workflow = {t["bezug"].get("vorgang") for t in daten["aufgaben"].values()}
        for slug in sorted(os.listdir(w)) if os.path.isdir(w) else []:
            meta = ss.vorgang_meta(os.path.join(w, slug, "vorgang.md")) if KUERZEL.fullmatch(slug) else None
            if meta is None or meta.get("status") in ENDSTATUS or slug in mit_workflow:
                continue
            if budget < min(kettenlaenge(w), daten["grenzen"]["neu_max_je_lauf"]):  # a chain longer than the whole budget still comes, first in its run
                zurueck.append(f"workflow:{slug}")
                continue
            try:
                for task_id in starte_vorgang(w, daten, slug, now):
                    budget -= 1
                    neu.append(task_id)
            except Refused as error:  # the whole chain or none: the rest waits for room
                if error.code != "budget_erschoepft":
                    raise
                zurueck.append(f"workflow:{slug} (aufgaben_max)")
                break
        offene_suchen = {t["bezug"]["auftrag"] for t in daten["aufgaben"].values() if t["typ"] == "suche" and t["status"] in OFFEN}
        for auftrag in ss.all_auftraege(w, defekte):  # one unreadable order does not stop the planning of the others
            if auftrag["id"] not in offene_suchen and ss.due(w, auftrag, now)[0]:
                vorhanden = daten["aufgaben"].get(f"suche:{auftrag['id']}:n{auftrag['lauf_zaehler']}")
                if vorhanden and vorhanden["status"] in (ABGEBROCHEN, FEHLGESCHLAGEN):
                    # not replaced by itself: a cancelled search stays cancelled, a failed one waits for `wiederholen`
                    uebersprungen.append(f"{vorhanden['id']}: {vorhanden['status']}")
                    continue
                anlegen("suche", {"auftrag": auftrag["id"], "zaehler": auftrag["lauf_zaehler"]}, now, suffix=f"n{auftrag['lauf_zaehler']}")
        for slug in sorted({t["bezug"].get("vorgang") for t in daten["aufgaben"].values()} - {None}):
            meta = ss.vorgang_meta(os.path.join(w, slug, "vorgang.md"))
            tag = (meta or {}).get("wiedervorlage", "")
            if meta and rang(meta) == RANG["versendet"] and ss.valid_date(tag) == tag and tag <= heute(now):
                anlegen("nachfassen", {"vorgang": slug}, now, ab=tag, faellig=tag, suffix=tag)
    except Refused as error:
        if error.code != "budget_erschoepft":
            raise
        zurueck.append("aufgaben_max erreicht")
    return neu, zurueck, uebersprungen, defekte


# ---------------------------------------------------------------- queries

def sortiert(tasks, now):
    def schluessel(t):
        return (0 if t["faellig"] and t["faellig"] < heute(now) else 1, -t["prioritaet"], t["faellig"] or "9999", t["erstellt"])
    return sorted(tasks, key=schluessel)


def kurz(t):
    return {k: t[k] for k in ("id", "typ", "status", "hinweis", "faellig", "prioritaet", "veraltet")} | {
        "zweck": t["zweck"], "wer": TYPEN[t["typ"]]["ausfuehrung"], "skill": TYPEN[t["typ"]]["skill"]}


def uebersicht(w, daten, now):
    tasks = sortiert(daten["aufgaben"].values(), now)
    gruppe = lambda test: [kurz(t) for t in tasks if test(t)]  # noqa: E731
    adapter_fehlt = lambda t: TYPEN[t["typ"]]["ausfuehrung"] == "adapter" and t["typ"] not in ADAPTER  # noqa: E731
    try:
        stellen_warten = ss.list_queue(w, "aktuell", None, None, now)["anzahl"]
    except Refused:
        stellen_warten = None
    return {
        "bereit_agent": gruppe(lambda t: t["status"] == BEREIT and TYPEN[t["typ"]]["ausfuehrung"] == "agent"),
        "bereit_nutzer": gruppe(lambda t: t["status"] == BEREIT and TYPEN[t["typ"]]["ausfuehrung"] == "nutzer"),
        "wartet_auf_freigabe": gruppe(lambda t: t["status"] == FREIGABE),
        "wartet_auf_eingabe": gruppe(lambda t: t["status"] == EINGABE),
        "laeuft": gruppe(lambda t: t["status"] == LAEUFT),
        "wiederholung_geplant": gruppe(lambda t: t["status"] == WIEDERHOLUNG),
        "blockiert": gruppe(lambda t: t["status"] == BLOCKIERT),
        "fehlgeschlagen": gruppe(lambda t: t["status"] == FEHLGESCHLAGEN),
        "ueberfaellig": gruppe(lambda t: t["status"] in OFFEN and t["faellig"] and t["faellig"] < heute(now)),
        "veraltet": gruppe(lambda t: t["status"] == ERLEDIGT and t["veraltet"]),
        "nicht_integriert": gruppe(lambda t: t["status"] in OFFEN and adapter_fehlt(t)),
        "stellen_warten_auf_entscheidung": stellen_warten,
        "anzahl": {s: sum(1 for t in tasks if t["status"] == s) for s in STATUS},
    }


def schreibe_uebersicht(w, daten, now):
    ueb = uebersicht(w, daten, now)
    zeilen = ["# Workflow", "", f"Ableitung aus `aufgaben.json`, Stand {stamp(now)}. Nicht von Hand ändern: Änderungen laufen über "
              "`scripts/workflow.py`. Der Bewerbungsstatus steht allein in `vorgang.md`.", ""]
    if ueb["stellen_warten_auf_entscheidung"]:
        zeilen += [f"**{ueb['stellen_warten_auf_entscheidung']} Stellen** der Stellensuche warten auf deine Entscheidung "
                   "(`suche/warteschlange.md`).", ""]
    titel = (("bereit_agent", "Bereit für einen Agenten"), ("bereit_nutzer", "Bereit für dich"),
             ("wartet_auf_freigabe", "Wartet auf deine Freigabe"), ("wartet_auf_eingabe", "Wartet auf Angaben"),
             ("laeuft", "Läuft"), ("wiederholung_geplant", "Wiederholung geplant"), ("blockiert", "Blockiert"),
             ("fehlgeschlagen", "Fehlgeschlagen"), ("ueberfaellig", "Überfällig"), ("veraltet", "Ergebnis veraltet"),
             ("nicht_integriert", "Noch nicht integriert"))
    for schluessel, name in titel:
        zeilen += [f"## {name} ({len(ueb[schluessel])})", ""]
        if not ueb[schluessel]:
            zeilen += ["Keine.", ""]
            continue
        zeilen += ["| Aufgabe | Zweck | Wer | Fällig | Hinweis |", "|---|---|---|---|---|"]
        for t in ueb[schluessel]:
            zeilen.append(f"| {ss.cell(t['id'])} | {ss.cell(t['zweck'])} | {ss.cell(t['wer'])} | {t['faellig'] or ''} | {ss.cell(t['hinweis'])} |")
        zeilen.append("")
    path = os.path.join(w, "workflow", "uebersicht.md")
    temp = path + ".tmp"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(temp, "w", encoding="utf-8") as out:
            out.write("\n".join(zeilen) + "\n")
        os.replace(temp, path)
    except OSError as error:
        if os.path.exists(temp):
            os.unlink(temp)
        raise Refused("speichern_fehlgeschlagen", f"Übersicht nicht schreibbar: {redact(error)}")


# ---------------------------------------------------------------- commands

def hole(daten, task_id):
    if task_id not in daten["aufgaben"]:
        raise Refused("aufgabe_unbekannt", f"Keine Aufgabe {redact(task_id, 80)}")
    return daten["aufgaben"][task_id]


def laufende(daten, now):
    return sum(1 for t in daten["aufgaben"].values() if t["status"] == LAEUFT and t["lease"] and t["lease"]["bis"] > stamp(now))


SUCHE_AUFBEWAHRUNG_TAGE = 30


def raeume_auf(daten, now):
    """Finished search tasks older than 30 days go; their ids carry a run counter and never come back (aufgaben_max stays usable)."""
    grenze = stamp(now - dt.timedelta(days=SUCHE_AUFBEWAHRUNG_TAGE))
    genannt = {d for t in daten["aufgaben"].values() for d in t["nach"]}
    weg = [i for i, t in daten["aufgaben"].items() if t["typ"] == "suche" and t["status"] == ERLEDIGT and t["geaendert"] < grenze and i not in genannt]
    for task_id in weg:
        del daten["aufgaben"][task_id]
    return weg


def uebernehmen(w, daten, task_id, now):
    task = hole(daten, task_id)
    katalog = TYPEN[task["typ"]]
    if task["status"] == LAEUFT:
        raise Refused("laeuft_bereits", f"{task_id} läuft schon (Lease bis {(task['lease'] or {}).get('bis', '?')})")
    if katalog["ausfuehrung"] != "agent":
        raise Refused("nur_nutzer" if katalog["ausfuehrung"] == "nutzer" else "nur_adapter",
                      f"{task_id} ist keine Aufgabe für einen Agenten ({katalog['ausfuehrung']})")
    if task["status"] != BEREIT:
        raise Refused("nicht_bereit", f"{task_id} ist {task['status']}: {task['hinweis']}")
    if laufende(daten, now) >= daten["grenzen"]["laufende_max"]:
        raise Refused("budget_erschoepft", f"Es laufen schon {daten['grenzen']['laufende_max']} Aufgaben (laufende_max)")
    if len(task["versuche"]) - task["versuche_ab"] >= daten["grenzen"]["versuche_max"]:
        raise Refused("versuche_erschoepft", f"{task_id} hatte schon {daten['grenzen']['versuche_max']} Versuche; `wiederholen` ist Sache des Nutzers")
    bis = stamp(now + dt.timedelta(minutes=daten["grenzen"]["lease_minuten"]))
    task["versuche"].append({"nr": len(task["versuche"]) + 1, "start": stamp(now), "ende": "", "ergebnis": "laeuft", "klasse": "", "grund": ""})
    task["lease"] = {"von": stamp(now), "bis": bis}
    setze(task, LAEUFT, now, f"Versuch {len(task['versuche'])}")
    nr = task["versuche"][-1]["nr"]
    return {"ok": True, "aufgabe": task_id, "versuch": nr, "skill": katalog["skill"], "zweck": task["zweck"], "bezug": task["bezug"],
            "nachbedingung": katalog["abschluss"](w, task, now)[1], "lease_bis": bis,
            "danach": f"workflow.py fertig {task_id} --versuch {nr}  oder  workflow.py fehler {task_id} --versuch {nr} --klasse <klasse> --grund <kurz>"}


def eigener_versuch(task, versuch):
    """A report names the attempt it belongs to; a session whose lease ran out cannot end the attempt of its successor."""
    if versuch is not None and (not task["versuche"] or task["versuche"][-1]["nr"] != versuch):
        raise Refused("veraltete_sitzung", f"{task['id']}: Versuch {versuch} gehört nicht mehr zu dieser Aufgabe (eine andere Sitzung hat sie übernommen)")


def fertig(w, daten, task_id, now, versuch=None):
    task = hole(daten, task_id)
    if task["status"] != LAEUFT:
        raise Refused("nicht_laufend", f"{task_id} ist {task['status']}; nur eine übernommene Aufgabe wird als fertig gemeldet")
    eigener_versuch(task, versuch)
    ok, text = TYPEN[task["typ"]]["abschluss"](w, task, now)
    if ok:
        erledige(w, task, now, "vom Agenten gemeldet, Nachbedingung geprüft")
        return {"ok": True, "aufgabe": task_id, "status": task["status"], "ergebnis": task["ergebnis"]}
    versuch_endet(daten, task, now, "ergebnis_fehlt", f"Nachbedingung nicht erfüllt: {text}")
    return {"ok": False, "aufgabe": task_id, "status": task["status"], "grund": text, "hinweis": task["hinweis"]}


def fehler(daten, task_id, klasse, grund, now, versuch=None):
    task = hole(daten, task_id)
    if task["status"] != LAEUFT:
        raise Refused("nicht_laufend", f"{task_id} ist {task['status']}; einen Fehler meldet nur die übernommene Aufgabe")
    eigener_versuch(task, versuch)
    versuch_endet(daten, task, now, klasse, grund)
    return {"ok": True, "aufgabe": task_id, "status": task["status"], "hinweis": task["hinweis"],
            "naechster_versuch": task["naechster_versuch"]}


def pruefbericht_veraltet(w, daten, task):
    """A send approval covers documents the quality gate has seen: the report may not be older than a document (S5 before S6)."""
    for dep in task["nach"]:
        if daten["aufgaben"][dep]["typ"] != "pruefung":
            continue
        bericht = os.path.join(vorgang_dir(w, task), "pruefbericht.md")
        if not os.path.isfile(bericht):
            continue  # the status `geprüft` in vorgang.md is then the only record
        neuer = [d for d in DOKUMENTE if os.path.isfile(os.path.join(vorgang_dir(w, task), d))
                 and os.stat(os.path.join(vorgang_dir(w, task), d)).st_mtime_ns > os.stat(bericht).st_mtime_ns]
        if neuer:
            raise Refused("pruefung_veraltet", f"{', '.join(neuer)} ist nach dem Prüfbericht geändert worden; erst den Qualitätscheck erneut ausführen")


def freigeben(w, daten, task_id, now):
    task = hole(daten, task_id)
    if not braucht_freigabe(task):
        raise Refused("keine_freigabe", f"{task_id} braucht keine Freigabe im Workflow (Plan und Suchauftrag werden dort freigegeben, wo sie liegen)")
    if task["status"] != FREIGABE:
        raise Refused("nicht_wartend", f"{task_id} ist {task['status']}, nicht {FREIGABE}: {task['hinweis']}")
    pruefbericht_veraltet(w, daten, task)
    aktuell = TYPEN[task["typ"]]["inhalt"](w, task)
    if not aktuell:
        raise Refused("nichts_zu_genehmigen", "Es gibt keinen Inhalt, den die Freigabe abdecken könnte")
    task["entscheidung"] = {"art": "erteilt", "kontext_hash": aktuell, "am": stamp(now), "von": "nutzer"}
    verlauf(task, now, "Freigabe erteilt für Inhalt " + aktuell[:12])
    bewerte(w, daten, task, now)
    return {"ok": True, "aufgabe": task_id, "status": task["status"], "inhalt": aktuell[:12]}


def ablehnen(w, daten, task_id, grund, now):
    task = hole(daten, task_id)
    if not braucht_freigabe(task) or task["status"] != FREIGABE:
        raise Refused("nicht_wartend", f"{task_id} wartet nicht auf eine Freigabe")
    task["entscheidung"] = {"art": "abgelehnt", "kontext_hash": TYPEN[task["typ"]]["inhalt"](w, task), "am": stamp(now),
                            "von": "nutzer", "grund": redact(grund)}
    bewerte(w, daten, task, now)
    return {"ok": True, "aufgabe": task_id, "status": task["status"]}


def ausfuehren(w, daten, task_id, now):
    """Hand an approved action to its adapter. The state `laeuft` with `extern_begonnen` is saved before the call (WF-7)."""
    task = hole(daten, task_id)
    katalog = TYPEN[task["typ"]]
    if katalog["ausfuehrung"] != "adapter":
        raise Refused("kein_adapter_typ", f"{task_id} wird nicht von einem Adapter ausgeführt")
    if task["typ"] not in ADAPTER:
        raise Refused("kein_adapter", "Es ist kein Versandadapter registriert (A-02 ist nicht ausgeliefert); der Nutzer sendet selbst")
    if task["status"] != BEREIT or not freigabe_gueltig(w, task):
        raise Refused("keine_gueltige_freigabe", f"{task_id} ist {task['status']} und die Freigabe gilt nicht für den aktuellen Inhalt")
    if laufende(daten, now) >= daten["grenzen"]["laufende_max"]:
        raise Refused("budget_erschoepft", "laufende_max erreicht")
    task["versuche"].append({"nr": len(task["versuche"]) + 1, "start": stamp(now), "ende": "", "ergebnis": "laeuft", "klasse": "", "grund": ""})
    task["lease"] = {"von": stamp(now), "bis": stamp(now + dt.timedelta(minutes=daten["grenzen"]["lease_minuten"]))}
    task["extern_begonnen"] = stamp(now)
    setze(task, LAEUFT, now, "externe Aktion begonnen")
    sichere(w, daten)
    try:
        if not freigabe_gueltig(w, task):  # the content may have changed since the check above: nothing has left yet
            task["extern_begonnen"], task["entscheidung"], task["lease"] = "", None, None
            schliesse_versuch(task, now, "fehler", "vorlaeufig", "Inhalt seit der Freigabe geändert; nichts gesendet")
            setze(task, FREIGABE, now, "Inhalt seit der Freigabe geändert", "Die Unterlagen haben sich seit der Freigabe geändert; nichts gesendet")
            return {"ok": False, "aufgabe": task_id, "status": task["status"], "hinweis": task["hinweis"]}
        antwort = ADAPTER[task["typ"]](task, task["entscheidung"])
        if not isinstance(antwort, dict):
            raise TypeError("Antwort des Adapters ist kein Objekt")
    except Exception as error:  # the outcome of an external action is unknown after an exception or an answer that cannot be read
        versuch_endet(daten, task, now, "unklar", f"Adapter: {type(error).__name__}")
        return {"ok": False, "aufgabe": task_id, "status": task["status"], "hinweis": task["hinweis"]}
    if antwort.get("gesendet"):
        erledige(w, task, now, "Adapter meldet: gesendet", ref="beleg", hash_wert=digest(str(antwort.get("beleg", ""))))
        return {"ok": True, "aufgabe": task_id, "status": task["status"]}
    if antwort.get("sicher"):
        task["extern_begonnen"] = ""  # the adapter is sure nothing left: this is a plain failure, not an unclear outcome
    versuch_endet(daten, task, now, "vorlaeufig" if antwort.get("sicher") else "unklar", "Adapter meldet: nicht gesendet")
    return {"ok": False, "aufgabe": task_id, "status": task["status"], "hinweis": task["hinweis"]}


def ausgang(w, daten, task_id, gesendet, now):
    task = hole(daten, task_id)
    if task["status"] != EINGABE or not task["extern_begonnen"]:
        raise Refused("kein_unklarer_ausgang", f"{task_id} hat keinen unklaren externen Ausgang")
    if gesendet:
        erledige(w, task, now, "Nutzer bestätigt: gesendet", ref="beleg", hash_wert=digest("nutzer-bestaetigt", task["extern_begonnen"]))
    else:
        task["extern_begonnen"], task["entscheidung"] = "", None  # sending again needs a new approval
        verlauf(task, now, "Nutzer bestätigt: nicht gesendet; neue Freigabe nötig")
        setze(task, WARTEND, now)
        bewerte(w, daten, task, now)
    return {"ok": True, "aufgabe": task_id, "status": task["status"]}


def wiederholen(w, daten, task_id, now):
    task = hole(daten, task_id)
    if task["status"] != FEHLGESCHLAGEN:
        raise Refused("nicht_fehlgeschlagen", f"{task_id} ist {task['status']}; wiederholt wird nur eine fehlgeschlagene Aufgabe")
    task["versuche_ab"] = len(task["versuche"])
    verlauf(task, now, "Wiederholung durch den Nutzer")
    setze(task, BEREIT, now)
    bewerte(w, daten, task, now)
    return {"ok": True, "aufgabe": task_id, "status": task["status"]}


def weiter(w, daten, task_id, now):
    """The user lifts a hold an agent reported (missing information, a needed approval, a missing permission, quality)."""
    task = hole(daten, task_id)
    if not task["halt"]:
        raise Refused("kein_halt", f"{task_id} hat keinen Halt, den der Nutzer aufheben müsste (Status {task['status']})")
    verlauf(task, now, f"Halt ({task['halt']}) vom Nutzer aufgehoben")
    task["halt"], task["versuche_ab"] = "", len(task["versuche"])  # waiting for the user does not use up the attempts
    if task["status"] != WARTEND:
        setze(task, WARTEND, now)
    bewerte(w, daten, task, now)
    return {"ok": True, "aufgabe": task_id, "status": task["status"]}


def abbrechen(daten, ziel, now):
    """Cancel one task, or every open task of a Vorgang (by its slug)."""
    alle = daten["aufgaben"].values()
    treffer = [t for t in alle if t["id"] == ziel]  # an exact id first, then a Vorgang, then a Suchauftrag: never two groups at once
    treffer = treffer or [t for t in alle if t["bezug"].get("vorgang") == ziel] or [t for t in alle if t["bezug"].get("auftrag") == ziel]
    if not treffer:
        raise Refused("aufgabe_unbekannt", f"Keine Aufgabe und kein Vorgang {redact(ziel, 80)}")
    unklar = [t["id"] for t in treffer if t["extern_begonnen"] and t["status"] in OFFEN]
    if unklar:  # the record that a send may have happened stays until the user decides with `ausgang`; nothing is cancelled half
        raise Refused("ausgang_unklar", f"Ob die externe Aktion lief, ist unklar ({', '.join(unklar)}); erst `ausgang` entscheiden, dann abbrechen")
    beendet = []
    for task in treffer:
        if task["status"] in OFFEN or task["status"] == FEHLGESCHLAGEN:
            setze(task, ABGEBROCHEN, now, "vom Nutzer abgebrochen")
            task["lease"] = None
            schliesse_versuch(task, now, "fehler", "abbruch", "vom Nutzer abgebrochen")
            beendet.append(task["id"])
    return {"ok": True, "abgebrochen": beendet}


def grenzen(daten, werte):
    for eintrag in werte:
        schluessel, _, wert = eintrag.partition("=")
        if schluessel not in LIMIT_BOUNDS or not re.fullmatch(r"[0-9]{1,6}", wert) or not LIMIT_BOUNDS[schluessel][0] <= int(wert) <= LIMIT_BOUNDS[schluessel][1]:
            raise Refused("grenze_ungueltig", f"{redact(eintrag, 40)}: erlaubt sind " + ", ".join(f"{k}={a}..{b}" for k, (a, b) in LIMIT_BOUNDS.items()))
        daten["grenzen"][schluessel] = int(wert)
    return {"ok": True, "grenzen": daten["grenzen"]}


# ---------------------------------------------------------------- CLI

def build_parser():
    parser = argparse.ArgumentParser(description="Workflow orchestration of the application process (WF-1 to WF-14).")
    parser.add_argument("--konfiguration", default=os.path.join(ss.DEFAULT_WURZEL, "konfiguration.md"))
    parser.add_argument("--jetzt", help="ISO time JJJJ-MM-TTTHH:MM:SSZ instead of the clock (tests, reproduction)")
    sub = parser.add_subparsers(dest="befehl", required=True)

    def add(name, *positional, **options):
        command = sub.add_parser(name)
        for argument in positional:
            command.add_argument(argument)
        for flag, kwargs in options.items():
            command.add_argument("--" + flag.replace("_", "-"), **kwargs)
        return command

    add("wurzel")
    add("starten", "vorgang")
    add("abgleichen")
    add("laufen")
    add("naechste", n={"type": int, "default": 5})
    add("uebernehmen", "aufgabe")
    add("fertig", "aufgabe", versuch={"type": int, "required": True})
    add("fehler", "aufgabe", klasse={"required": True}, grund={"default": ""}, versuch={"type": int, "required": True})
    add("weiter", "aufgabe")
    add("freigeben", "aufgabe", ja={"action": "store_true"})
    add("ablehnen", "aufgabe", grund={"default": ""})
    add("ausfuehren", "aufgabe")
    add("ausgang", "aufgabe", gesendet={"action": "store_true"}, nicht_gesendet={"action": "store_true"})
    add("wiederholen", "aufgabe")
    add("abbrechen", "ziel")
    add("anlegen", "typ", vorgang={}, auftrag={}, datei={}, nach={"action": "append", "default": []}, ab={"default": ""}, faellig={"default": ""})
    add("zeige", "aufgabe")
    add("uebersicht")
    command = sub.add_parser("grenzen")
    command.add_argument("werte", nargs="*")
    return parser


READ_ONLY = ("wurzel", "zeige")
# what only the user does: never in an unattended session, whatever its prompt says (WF-7, WF-13)
USER_ONLY = ("anlegen", "weiter", "freigeben", "ablehnen", "ausfuehren", "ausgang", "wiederholen", "abbrechen", "grenzen")


def unbeaufsichtigt():
    return bool(os.environ.get("WORKFLOW_UNBEAUFSICHTIGT") or os.environ.get("STELLENSUCHE_GEPLANT"))


def dispatch(args, w, daten, now):
    cmd = args.befehl
    if cmd == "starten":
        return {"ok": True, "neu": starte_vorgang(w, daten, args.vorgang, now), "geaendert": abgleichen(w, daten, now)}
    if cmd == "abgleichen":
        return {"ok": True, "geaendert": abgleichen(w, daten, now)}
    if cmd == "laufen":
        aufgeraeumt = raeume_auf(daten, now)
        abgleichen(w, daten, now)
        neu, zurueck, uebersprungen, defekte = plane(w, daten, now)
        geaendert = abgleichen(w, daten, now)
        bereit = [kurz(t) for t in sortiert([t for t in daten["aufgaben"].values() if t["status"] == BEREIT], now)]
        return {"ok": True, "neu": neu, "zurueckgestellt": zurueck, "nicht_ersetzt": uebersprungen, "defekte_auftraege": defekte, "aufgeraeumt": aufgeraeumt, "geaendert": geaendert, "bereit": bereit,
                "hinweis": "Der Lauf plant und gleicht ab; er führt nichts aus und sendet nichts."}
    if cmd == "naechste":
        abgleichen(w, daten, now)
        bereit = sortiert([t for t in daten["aufgaben"].values() if t["status"] == BEREIT], now)
        return {"ok": True, "agent": [kurz(t) for t in bereit if TYPEN[t["typ"]]["ausfuehrung"] == "agent"][: args.n],
                "nutzer": [kurz(t) for t in bereit if TYPEN[t["typ"]]["ausfuehrung"] == "nutzer"],
                "freigabe": [kurz(t) for t in sortiert([t for t in daten["aufgaben"].values() if t["status"] == FREIGABE], now)]}
    if cmd == "uebernehmen":
        abgleichen(w, daten, now)
        return uebernehmen(w, daten, args.aufgabe, now)
    if cmd == "fertig":
        return fertig(w, daten, args.aufgabe, now, args.versuch)
    if cmd == "fehler":
        return fehler(daten, args.aufgabe, args.klasse, args.grund, now, args.versuch)
    if cmd == "weiter":
        return weiter(w, daten, args.aufgabe, now)
    if cmd == "freigeben":
        if not args.ja:
            raise Refused("freigabe_nicht_bestaetigt", "Die Freigabe braucht das ausdrückliche Ja des Nutzers (--ja)")
        abgleichen(w, daten, now)
        return freigeben(w, daten, args.aufgabe, now)
    if cmd == "ablehnen":
        return ablehnen(w, daten, args.aufgabe, args.grund, now)
    if cmd == "ausfuehren":
        abgleichen(w, daten, now)  # a finished or vanished Vorgang cancels the task before anything is sent
        return ausfuehren(w, daten, args.aufgabe, now)
    if cmd == "ausgang":
        if args.gesendet == args.nicht_gesendet:
            raise Refused("ausgang_ungueltig", "Entweder --gesendet oder --nicht-gesendet")
        return ausgang(w, daten, args.aufgabe, args.gesendet, now)
    if cmd == "wiederholen":
        return wiederholen(w, daten, args.aufgabe, now)
    if cmd == "abbrechen":
        return abbrechen(daten, args.ziel, now)
    if cmd == "anlegen":
        bezug = {k: v for k, v in (("vorgang", args.vorgang), ("auftrag", args.auftrag), ("datei", args.datei)) if v}
        task, angelegt = neue_aufgabe(daten, args.typ, bezug, now, nach=args.nach, ab=args.ab, faellig=args.faellig)
        abgleichen(w, daten, now)
        return {"ok": True, "aufgabe": task["id"], "neu": angelegt, "status": task["status"]}
    if cmd == "zeige":
        return {"ok": True, "aufgabe": hole(daten, args.aufgabe)}
    if cmd == "uebersicht":
        abgleichen(w, daten, now)
        return {"ok": True, **uebersicht(w, daten, now)}
    return grenzen(daten, args.werte) if args.werte else {"ok": True, "grenzen": daten["grenzen"]}


def haltbar_abgleichen(w, now):
    """After a refused command: reconcile the stored state afresh (nothing of the failed command is kept) and save what changed."""
    try:
        frisch = lade(w)
        vorher = json.dumps(frisch, sort_keys=True)
        abgleichen(w, frisch, now)
        if json.dumps(frisch, sort_keys=True) != vorher:
            sichere(w, frisch)
    except Refused:
        pass


def run(args):
    w = ss.find_wurzel(args.konfiguration)
    now = parse_time(args.jetzt) if args.jetzt else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    if unbeaufsichtigt() and args.befehl in USER_ONLY:
        raise Refused("nur_interaktiv", f"{args.befehl} ist in einer unbeaufsichtigten Sitzung nicht erlaubt (WF-13)")
    if args.befehl == "wurzel":
        return {"ok": True, "wurzel": w}  # no store needed: this works even when aufgaben.json is damaged
    if args.befehl in READ_ONLY:
        return dispatch(args, w, lade(w), now)
    with ss.exclusive(w, *LOCK):
        daten = lade(w)
        vorher = json.dumps(daten, sort_keys=True)
        try:
            result = dispatch(args, w, daten, now)
        except Refused:
            haltbar_abgleichen(w, now)  # the refusal must not undo a lease that ran out meanwhile
            raise
        try:  # the state a command leaves behind is already reconciled (dependents follow at once)
            abgleichen(w, daten, now)
        except Refused as error:
            result["warnung_abgleich"] = error.meldung
        if json.dumps(daten, sort_keys=True) != vorher or not os.path.isfile(store_path(w)):
            sichere(w, daten)
        try:  # the overview is a derivation: its failure must not hide the outcome of the command
            schreibe_uebersicht(w, daten, now)
        except Refused as error:
            result["warnung_uebersicht"] = error.meldung
            print(f"uebersicht.md nicht aktualisiert: {error.meldung}", file=sys.stderr)
    return result


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
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result.get("ok") is False else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
