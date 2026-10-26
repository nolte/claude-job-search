#!/usr/bin/env python3
"""Learning from confirmed application results: statistics, funnel, times, retrospective and proposals (spec ergebnisauswertung EA-1 to EA-24, A-06, R-03).

Reads what is already in the Wurzel: `vorgang.md` (status, `versendet_am`, `## Verlauf`), the confirmed events in
`<vorgang>/nachverfolgung.json` (written by `kommunikation.py`, or by `ergebnis erfassen` here on the user's statement)
and, for the versions of the documents, `qualitaet.json`. It keeps no second record of the results: statistics and the
retrospective are derivations, marked as such and bound to a hash of their sources, so a changed source makes them stale.

What it never does: change a Vorgang status, a document, the Datengrundlage or `profil.md`; send anything; call a model; say why
an application succeeded or failed. A refusal without a stated reason is "Grund unbekannt", never a weakness of the person or of the
documents. A proposal changes nothing when it is accepted; the user carries it out and says so (`umgesetzt`).

It also reads, never writes, `suche/warteschlange.json` and `workflow/aufgaben.json` for the early stages of the funnel (EA-17).

State: `<wurzel>/lernen/vorschlaege.json` (proposals), `<wurzel>/lernen/retrospektive-*.md` (derivations).

Usage: lernen.py [--konfiguration PFAD] [--jetzt ISO] <befehl> ...
Commands: ergebnis (erfassen|korrigieren|verwerfen|liste), statistik, erklaere, retrospektive, aktualitaet, vorschlaege (erzeugen|liste),
vorschlag (zeige|vorlegen|entscheiden|pruefe). Output is one JSON object. Exit code 0 ok, 2 ok=false, 3 refused, 1 blocker. Standard library only.
"""

import argparse
import datetime as dt
import json
import math
import os
import re
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kommunikation as km  # noqa: E402
import stellensuche as ss  # noqa: E402
from grundlage_hash import sha256_file  # noqa: E402
from stellensuche import Blocker, Refused, atomic_write, clean_text, digest, load_json, parse_time, redact, stamp  # noqa: E402

LOCK = ("lernen", ".lernen.lock", "die Auswertung")
MIN_N = 5  # below this many applications a rate is shown but marked as limited
BESTAETIGT = ("bestaetigt", "korrigiert")
INHALTLICH = tuple(a for a in km.ARTEN_ARBEITGEBER if a not in ("eingangsbestaetigung",))  # a reply of the employer; an own step is none
STATUS_FLAGS = {  # what the status the user keeps in vorgang.md states by itself (LS-6): flags it implies
    "rückmeldung": {"rueckmeldung"}, "gespräch": {"rueckmeldung", "einladung"},
    "angebot": {"rueckmeldung", "einladung", "gespraech", "angebot"}, "verhandlung": {"rueckmeldung", "einladung", "gespraech", "angebot"},
    "zusage": {"rueckmeldung", "einladung", "gespraech", "angebot", "einstellung"}, "absage": {"rueckmeldung", "absage"},
    "abgelehnt": {"rueckmeldung", "einladung", "gespraech", "angebot", "angebot_abgelehnt"}, "zurückgezogen": {"zurueckgezogen"}, "ohne Antwort": {"ohne_antwort"}, "abgeschlossen": set(),
}
ART_FLAGS = {"eingangsbestaetigung": {"eingangsbestaetigung"}, "angebot_angenommen": {"angebot", "angenommen"}, "angebot_abgelehnt": {"angebot", "angebot_abgelehnt"},
             "gespraechseinladung": {"einladung"}, "gespraech": {"einladung", "gespraech"}, "technisches_gespraech": {"einladung", "gespraech"},
             "assessment": {"einladung", "gespraech"}, "weitere_phase": {"einladung", "gespraech", "weitere_phase"}, "angebot": {"angebot"},
             "einstellung": {"angebot", "einstellung"}, "absage": {"absage"}, "absage_nach_unterlagen": {"absage"},
             "absage_nach_gespraech": {"absage"}, "absage_nach_assessment": {"absage"}, "zurueckgezogen": {"zurueckgezogen"}}
SEGMENTE = ("arbeitgeber", "zeitraum", "kanal", "quelle", "ausrichtung", "stellenprofil", "dokumentversion", "bewertung")
FILTER = ("status", "arbeitgeber", "stellenprofil", "ausrichtung", "kanal", "quelle", "bewertung", "dokumentversion", "titel", "ergebnis")
ERGEBNIS_WERTE = ("offen", "rueckmeldung", "eingangsbestaetigung", "einladung", "gespraech", "angebot", "einstellung", "absage", "ohne_antwort", "zurueckgezogen")
REIFE_TAGE_STANDARD = 28  # a reporting convention for "old enough to have had a reply", not a deadline of any employer; `--reife-tage` changes it
NICHT_ERFASST = ("senioritaet", "branche", "standort", "arbeitsmodell")  # no field in vorgang.md: shown as not recorded, never filled in
PRE_FERTIG = ("erstellt", "geprüft")
VORSCHLAG_STATUS = ("erstellt", "zur_pruefung", "angenommen", "abgelehnt", "zurueckgestellt", "umgesetzt", "veraltet")
UEBERGANG = {"erstellt": ("zur_pruefung",), "zur_pruefung": ("angenommen", "abgelehnt", "zurueckgestellt"),
             "zurueckgestellt": ("zur_pruefung",), "angenommen": ("umgesetzt", "abgelehnt")}
GRENZEN = (
    "Die Auswertung zählt bestätigte Ergebnisse. Sie sagt nicht, warum eine Bewerbung Erfolg hatte oder nicht hatte.",
    "Eine Absage ohne genannten Grund bleibt „Grund unbekannt“: daraus folgt weder eine Schwäche der Person noch der Unterlagen.",
    "Eine bestandene Qualitätsprüfung ist kein Nachweis einer erfolgreichen Bewerbung, eine Absage kein Nachweis eines fehlerhaften Dokuments.",
    "Kleine Datenmengen (unter 5 Bewerbungen) machen eine Quote zur Momentaufnahme; Vorgänge verschiedener Stellen, Arbeitgeber und Zeiträume sind nicht ohne Prüfung vergleichbar.",
    "Offene Bewerbungen sind nicht erfolglos; sie stehen im Nenner und werden getrennt ausgewiesen.",
)


# ---------------------------------------------------------------- reading the Vorgänge

def lade_ereignisse(w, slug):
    try:
        return km.lade_nachverfolgung(w, slug)
    except Refused:
        return {"version": 1, "ereignisse": [], "wiedervorlagen": [], "defekt": True}


def dokument_stand(w, slug):
    """The versions the documents of a Vorgang had at the last quality check, and whether that fixes one version unambiguously."""
    ordner = os.path.join(w, slug)
    bericht = load_report(ordner)
    if bericht is None:
        return {"stand": None, "eindeutig": False, "grund": "kein Qualitätsbericht (qualitaet.json)"}
    import qualitaet as qa
    aktuell = qa.dokument_hashes(ordner) == bericht.get("dokumente") and qa.export_hashes(ordner) == bericht.get("exporte")
    meta = ss.vorgang_meta(os.path.join(ordner, "vorgang.md")) or {}
    versendet = bool(meta.get("anhaenge", "").strip("[] "))
    eindeutig = aktuell and versendet
    grund = "" if eindeutig else ("der Qualitätsbericht passt nicht mehr zu den Dateien" if not aktuell else "vorgang.md nennt keine versendeten Anhänge")
    return {"stand": str(bericht.get("stand", ""))[:12], "eindeutig": eindeutig, "grund": grund, "gesamt": bericht.get("gesamt"),
            "ats_umfang": (bericht.get("ats") or {}).get("umfang")}


def load_report(ordner):
    try:
        daten = load_json(os.path.join(ordner, "qualitaet.json"), None)
    except Refused:
        return None
    return daten


def bewertung_von(w, slug):
    pfad = os.path.join(w, slug, "passung.md")
    try:
        with open(pfad, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return "keine"
    for wert in ("Veto", "Klärungsbedarf", "Passt überwiegend"):
        if wert in text:
            return wert
    return "unbekannt"


def vorgang_daten(w, slug, meta, heute_datum):
    nv = lade_ereignisse(w, slug)
    bestaetigt = [e for e in nv["ereignisse"] if e.get("status") in BESTAETIGT]
    flags, quelle_ereignis = set(), set()
    for e in bestaetigt:
        f = ART_FLAGS.get(e["art"], set())
        flags |= f
        if e["art"] in INHALTLICH:
            flags.add("rueckmeldung")
        if f or e["art"] in INHALTLICH:
            quelle_ereignis.add(e["art"])
    status = meta.get("status", "")
    status_flags = STATUS_FLAGS.get(status, set())
    nur_status = sorted(status_flags - flags)
    flags |= status_flags
    quelle = meta.get("stellenquelle", "")
    host = re.sub(r"^https?://(www\.)?", "", quelle).split("/")[0] if quelle.startswith("http") else "text"
    versendet = ss.valid_date(meta.get("versendet_am", ""))
    daten = {"erfasst": ss.valid_date(meta.get("erfasst", "")), "titel_stelle": meta.get("stelle", ""), "slug": slug, "firma": meta.get("firma", ""), "stelle": meta.get("stelle", ""), "status": status, "versendet_am": versendet,
             "flags": flags, "nur_status": nur_status, "kanal": meta.get("weg") or meta.get("bewerbungsweg", "") or "unbekannt",
             "quelle": host or "unbekannt", "ausrichtung": meta.get("ausrichtung", "") or "unbekannt",
             "stellenprofil": meta.get("profil", "") or next((t.split(":", 1)[1] for t in re.findall(r"profil:[\w-]+", meta.get("tags", ""))), "") or "unbekannt",
             "ereignisse": bestaetigt, "unbestaetigt": [e for e in nv["ereignisse"] if e.get("status") in ("erkannt", "zur_pruefung")],
             "loeschen_ab": ss.valid_date(meta.get("loeschen_ab", "")), "ereignisdatei_defekt": bool(nv.get("defekt"))}
    daten["abgeschlossen"] = status in km.ENDSTATUS
    daten["offen"] = not daten["abgeschlossen"]
    return daten


def filter_grund(d, filter_, w):
    """The reason a Vorgang is outside the filter, or '' when it passes. Only data that exists is compared (a missing value is `unbekannt`)."""
    f = {k: v for k, v in (filter_ or {}).items() if v}
    for key, grund, wert in (("status", "anderer_status", d["status"]), ("stellenprofil", "anderes_stellenprofil", d["stellenprofil"]),
                             ("ausrichtung", "andere_ausrichtung", d["ausrichtung"]), ("kanal", "anderer_kanal", d["kanal"]), ("quelle", "andere_quelle", d["quelle"])):
        if key in f and wert != f[key]:
            return grund
    if "arbeitgeber" in f and ss.norm(d["firma"]) != ss.norm(f["arbeitgeber"]):
        return "anderer_arbeitgeber"
    if "titel" in f and ss.norm(f["titel"]) not in ss.norm(d["titel_stelle"]):
        return "anderer_titel"
    if "ergebnis" in f:
        if f["ergebnis"] not in ERGEBNIS_WERTE:
            raise Refused("filter_ungueltig", f"--ergebnis ist eines von: {', '.join(ERGEBNIS_WERTE)}")
        if (not d["offen"]) if f["ergebnis"] == "offen" else f["ergebnis"] not in d["flags"]:
            return "anderes_ergebnis"
    if "bewertung" in f or "dokumentversion" in f:
        d.setdefault("bewertung", bewertung_von(w, d["slug"]))
        d.setdefault("dokumente", dokument_stand(w, d["slug"]))
        if "bewertung" in f and d["bewertung"] != f["bewertung"]:
            return "andere_bewertung"
        if "dokumentversion" in f and (d["dokumente"]["stand"] if d["dokumente"]["eindeutig"] else "nicht_eindeutig") != f["dokumentversion"]:
            return "andere_dokumentversion"
    return ""


def waehle(w, now, von=None, bis=None, filter_=None):
    """-> (included list, exclusions with reasons). The population is the dispatched applications in the period (EA-4)."""
    heute_datum = km.heute(now)
    gewaehlt, ausgeschlossen = [], Counter()
    filter_ = filter_ or {}
    for slug, meta in km.alle_vorgaenge(w).items():
        d = vorgang_daten(w, slug, meta, heute_datum)
        if d["status"] in ("erfasst", "analysiert", "geplant", "erstellt", "geprüft", "in Arbeit", "") and not d["versendet_am"]:
            ausgeschlossen["nicht_versendet"] += 1
            continue
        if not d["versendet_am"]:
            ausgeschlossen["versendet_am_fehlt"] += 1
            continue
        if d["loeschen_ab"] and d["loeschen_ab"] <= heute_datum:
            ausgeschlossen["loeschfrist_erreicht"] += 1
            continue
        if (von and d["versendet_am"] < von) or (bis and d["versendet_am"] > bis):
            ausgeschlossen["ausserhalb_zeitraum"] += 1
            continue
        grund = filter_grund(d, filter_, w)
        if grund:
            ausgeschlossen[grund] += 1
            continue
        d.setdefault("dokumente", dokument_stand(w, slug))
        d.setdefault("bewertung", bewertung_von(w, slug))
        gewaehlt.append(d)
    return gewaehlt, dict(ausgeschlossen)


def waehle_alle(w, now, von=None, bis=None, filter_=None):
    """-> (all Vorgänge in the period incl. those not yet dispatched, exclusions). The period counts the day of the dispatch, else the day of `erfasst`.

    This is the population of the funnel (R-03): a Vorgang begun is not a Vorgang dispatched. A Vorgang without any date is kept when no period is
    asked for and excluded with `datum_fehlt` otherwise; its date is not guessed."""
    heute_datum = km.heute(now)
    liste, ausgeschlossen = [], Counter()
    for slug, meta in km.alle_vorgaenge(w).items():
        d = vorgang_daten(w, slug, meta, heute_datum)
        if d["loeschen_ab"] and d["loeschen_ab"] <= heute_datum:
            ausgeschlossen["loeschfrist_erreicht"] += 1
            continue
        tag = d["versendet_am"] or d["erfasst"]
        if (von or bis) and not tag:
            ausgeschlossen["datum_fehlt"] += 1
            continue
        if tag and ((von and tag < von) or (bis and tag > bis)):
            ausgeschlossen["ausserhalb_zeitraum"] += 1
            continue
        grund = filter_grund(d, filter_, w)
        if grund:
            ausgeschlossen[grund] += 1
            continue
        d.setdefault("dokumente", dokument_stand(w, slug))
        d.setdefault("bewertung", bewertung_von(w, slug))
        liste.append(d)
    return liste, dict(ausgeschlossen)


# ---------------------------------------------------------------- statistics (EA-5 to EA-8)

def wilson(zaehler, nenner):
    """95 % Wilson interval of a share, or None for an empty basis. It states how far a small count can be trusted, not why a result happened."""
    if not nenner:
        return None
    z, p = 1.96, zaehler / nenner
    nenn = 1 + z * z / nenner
    mitte = (p + z * z / (2 * nenner)) / nenn
    breite = z * math.sqrt(p * (1 - p) / nenner + z * z / (4 * nenner * nenner)) / nenn
    return [round(max(0.0, mitte - breite), 3), round(min(1.0, mitte + breite), 3)]


def quote(zaehler, nenner):
    wert = round(zaehler / nenner, 3) if nenner else None
    return {"zaehler": zaehler, "nenner": nenner, "quote": wert, "konfidenz95": wilson(zaehler, nenner), "eingeschraenkt": nenner < MIN_N,
            "aussagekraft": "gering" if nenner < MIN_N else "beschreibend",
            **({"hinweis": f"weniger als {MIN_N} Bewerbungen: eine Momentaufnahme, kein Trend"} if nenner < MIN_N else {})}


def tage(von, bis):
    return (dt.date.fromisoformat(bis) - dt.date.fromisoformat(von)).days


def antwortzeit(gruppe, filter_arten):
    """Days from dispatch to the first confirmed event of the given kinds, only where both dates are known and not contradictory."""
    werte, ohne_datum, negativ = [], 0, 0
    for d in gruppe:
        treffer = [e for e in d["ereignisse"] if e["art"] in filter_arten]
        if not treffer:
            continue
        daten = sorted(ss.valid_date(str(e.get("datum", ""))) for e in treffer if ss.valid_date(str(e.get("datum", ""))))
        if not daten:
            ohne_datum += 1
            continue
        abstand = tage(d["versendet_am"], daten[0])
        if abstand < 0:
            negativ += 1
            continue
        werte.append(abstand)
    ergebnis = {"n": len(werte), "ohne_datum": ohne_datum, "datum_vor_versand": negativ}
    if werte:
        ergebnis.update(median_tage=statistics.median(werte), min_tage=min(werte), max_tage=max(werte))
    if len(werte) < MIN_N:
        ergebnis["eingeschraenkt"] = True
    return ergebnis


def kennzahlen(gruppe):
    n = len(gruppe)
    z = lambda flag: sum(1 for d in gruppe if flag in d["flags"])
    offen_ohne = sum(1 for d in gruppe if d["status"] == "versendet" and "rueckmeldung" not in d["flags"])
    zaehler = {"bewerbungen": n, "abgeschlossen": sum(1 for d in gruppe if d["abgeschlossen"]), "offen": sum(1 for d in gruppe if d["offen"]),
               "rueckmeldung": z("rueckmeldung"), "absage": z("absage"), "einladung": z("einladung"), "gespraech": z("gespraech"),
               "angebot": z("angebot"), "einstellung": z("einstellung"), "ohne_antwort_abgeschlossen": z("ohne_antwort"),
               "offen_ohne_rueckmeldung": offen_ohne}
    abgeschlossen_ohne = zaehler["ohne_antwort_abgeschlossen"]
    return {
        "zaehler": zaehler,
        "ruecklaufquote": {"definition": "Bewerbungen mit mindestens einer inhaltlichen, bestätigten Rückmeldung (ohne bloße Eingangsbestätigung) / alle versendeten Bewerbungen im Zeitraum. Offene Bewerbungen stehen im Nenner.",
                           **quote(z("rueckmeldung"), n)},
        "ruecklaufquote_ohne_offene": {"definition": "Rückmeldungen / (Rückmeldungen + Bewerbungen, die der Nutzer als `ohne Antwort` abgeschlossen hat). Offene Bewerbungen zählen nicht.",
                                       **quote(z("rueckmeldung"), z("rueckmeldung") + abgeschlossen_ohne)},
        "uebergaenge": {
            "bewerbung_zu_rueckmeldung": quote(z("rueckmeldung"), n),
            "bewerbung_zu_einladung": quote(z("einladung"), n),
            "einladung_zu_weiterer_phase": quote(sum(1 for d in gruppe if {"einladung", "weitere_phase"} <= d["flags"]), z("einladung")),
            "einladung_zu_angebot": quote(sum(1 for d in gruppe if {"einladung", "angebot"} <= d["flags"]), z("einladung")),
            "bewerbung_zu_einstellung": quote(z("einstellung"), n)},
        "antwortzeiten": {"erste_rueckmeldung": antwortzeit(gruppe, INHALTLICH), "eingangsbestaetigung": antwortzeit(gruppe, ("eingangsbestaetigung",)),
                          "einladung": antwortzeit(gruppe, ("gespraechseinladung",)),
                          "absage": antwortzeit(gruppe, ("absage", "absage_nach_unterlagen", "absage_nach_gespraech", "absage_nach_assessment"))},
    }


def schluessel_von(d, nach):
    if nach == "arbeitgeber":
        return d["firma"] or "unbekannt"
    if nach == "zeitraum":
        return d["versendet_am"][:7]
    if nach == "kanal":
        return d["kanal"]
    if nach == "quelle":
        return d["quelle"]
    if nach == "dokumentversion":
        return d["dokumente"]["stand"] if d["dokumente"]["eindeutig"] else "nicht_eindeutig"
    return d[nach]


def datenqualitaet(w, gruppe, ausgeschlossen):
    offene_nachrichten = km.offene_vorschlaege(w)
    return {"ausgeschlossen": ausgeschlossen,
            "ergebnis_nur_durch_status": sum(1 for d in gruppe if d["nur_status"]),
            "ereignisse_zur_pruefung": sum(len(d["unbestaetigt"]) for d in gruppe),
            "nachrichten_noch_nicht_geprueft": len(offene_nachrichten),
            "ereignisdatei_defekt": sum(1 for d in gruppe if d["ereignisdatei_defekt"]),
            "dokumentversion_nicht_eindeutig": sum(1 for d in gruppe if not d["dokumente"]["eindeutig"]),
            "hinweis": "Ein Ergebnis, das nur aus `status` in vorgang.md stammt, ist vom Nutzer gepflegt, aber nicht durch ein Ereignis belegt; unbestätigte Ereignisse und ungeprüfte Nachrichten fließen nicht ein."}


QUELLDATEIEN = ("vorgang.md", "nachverfolgung.json", "passung.md", "qualitaet.json")  # every file of a Vorgang a figure reads
GLOBALE_QUELLEN = (("suche", "warteschlange.json"), ("workflow", "aufgaben.json"))  # read only


def quellen_hash(w, gruppe):
    """Hash over every file the figures read, so that a changed fit check, quality report, queue or approval makes a derivation stale."""
    teile = []
    for d in sorted(gruppe, key=lambda x: x["slug"]):
        for name in QUELLDATEIEN:
            pfad = os.path.join(w, d["slug"], name)
            teile.append(f"{d['slug']}/{name}={sha256_file(pfad) if os.path.isfile(pfad) else '-'}")
    for teil in GLOBALE_QUELLEN:
        pfad = os.path.join(w, *teil)
        teile.append(f"{'/'.join(teil)}={sha256_file(pfad) if os.path.isfile(pfad) else '-'}")
    return digest(*teile)


def statistik(w, now, von=None, bis=None, nach=None, filter_=None, gewaehlt=None, reife=REIFE_TAGE_STANDARD, belege=False, alle=None, mit_widerspruechen=True):
    gruppe, ausgeschlossen = gewaehlt or waehle(w, now, von, bis, filter_)
    if not isinstance(reife, int) or isinstance(reife, bool) or not 1 <= reife <= 365:
        raise Refused("reife_ungueltig", "--reife-tage ist eine ganze Zahl von 1 bis 365")
    population, ausgeschlossen_alle = alle or waehle_alle(w, now, von, bis, filter_)
    tasks, stellen = lade_workflow(w), lade_stellen(w)
    for d in population:
        anreichern(d, w, tasks)
    zeiten = zeitkennzahlen(population, stellen)
    aktivitaet, konversionen = aktivitaet_und_konversionen(population, stellen, reife, km.heute(now), belege)
    ergebnis = {"ok": True, "erstellt": stamp(now), "zeitraum": {"von": von, "bis": bis}, "filter": {k: v for k, v in (filter_ or {}).items() if v},
                "ausgewertet": len(gruppe), "quellen_hash": quellen_hash(w, population), "abgeleitet": True,
                **kennzahlen(gruppe), "datenqualitaet": datenqualitaet(w, gruppe, ausgeschlossen), "grenzen": list(GRENZEN),
                "population": {"begonnen": len(population), "eingereicht": len(gruppe), "ausgeschlossen_begonnen": ausgeschlossen_alle,
                               "hinweis": "Die Kennzahlen unter `aktivitaet` und `konversionen` zählen alle begonnenen Bewerbungen im Zeitraum; `zaehler` und `uebergaenge` nur die eingereichten."},
                "reife_tage": reife, "aktivitaet": aktivitaet, "konversionen": konversionen, "zeiten": zeiten,
                "nicht_erfasst": {"merkmale": list(NICHT_ERFASST), "hinweis": "Für diese Merkmale gibt es kein Feld in vorgang.md: sie sind nicht erfasst und werden weder gefiltert noch erfunden."}}
    ergebnis["datenqualitaet"]["widersprueche"] = widersprueche(w, now, population) if mit_widerspruechen else []
    ergebnis["datenqualitaet"]["ereignisse_ohne_datum"] = sum(1 for d in population for e in d["ereignisse"] if not ereignis_tag(e))
    if nach:
        if nach not in SEGMENTE:
            raise Refused("segment_unbekannt", f"Segment {redact(nach, 40)} ist nicht bekannt ({', '.join(SEGMENTE)})")
        gruppen, hinweise = segmentiere(gruppe, nach, km.heute(now))
        ergebnis["segmente"] = {"nach": nach, "gruppen": gruppen, "vergleichbarkeit": hinweise,
                                "hinweis": "Gruppen sind nur vergleichbar, wenn sie ähnliche Stellen, Seniorität und Zeiträume haben; das prüft die Nutzerin oder der Nutzer."}
    return ergebnis



# ---------------------------------------------------------------- R-03: funnel, maturity, times, explanations (EA-17 to EA-22)

def lade_workflow(w):
    """The tasks of the workflow store (read only), or None when there is no store. The workflow stays the one place of approvals (WF-7)."""
    try:
        daten = load_json(os.path.join(w, "workflow", "aufgaben.json"), None)
    except Refused:
        return None
    return daten["aufgaben"] if isinstance(daten, dict) and isinstance(daten.get("aufgaben"), dict) else None


def lade_stellen(w):
    """The postings of the Warteschlange, or None when there is none (the search is optional)."""
    try:
        queue = ss.load_queue(w)
    except Refused:
        return None
    return queue["stellen"] if os.path.isfile(ss.queue_path(w)) else None


def tag10(wert):
    return ss.valid_date(str(wert or "")[:10])


def ereignis_tag(e):
    return tag10(e.get("eingetreten_am") or e.get("datum"))


def erstes_datum(d, arten):
    """The earliest date of a confirmed event of these kinds, or '' (a missing date is never replaced)."""
    tage_ = sorted(x for x in (ereignis_tag(e) for e in d["ereignisse"] if e["art"] in arten) if x)
    return tage_[0] if tage_ else ""


ABSAGEN = ("absage", "absage_nach_unterlagen", "absage_nach_gespraech", "absage_nach_assessment")
GESPRAECHE = ("gespraech", "technisches_gespraech", "assessment")
ERGEBNISARTEN = ABSAGEN + ("angebot", "einstellung", "angebot_angenommen", "angebot_abgelehnt", "zurueckgezogen")


def anreichern(d, w, tasks):
    """Dates and facts of the funnel for one Vorgang, from what is stored. Nothing is estimated; an unknown date stays ''."""
    status = d["status"]
    d["fertig"] = status in PRE_FERTIG or bool(d["versendet_am"])
    aufgabe = (tasks or {}).get(f"unterlagen:{d['slug']}") or {}
    fertig_am = tag10((aufgabe.get("ergebnis") or {}).get("am")) if aufgabe.get("status") == "erledigt" else ""
    d["fertig_am"] = fertig_am or erstes_datum(d, ("vorbereitet", "geprueft"))
    freigabe = (tasks or {}).get(f"versand_freigabe:{d['slug']}") if tasks is not None else None
    d["freigegeben"] = None if tasks is None else bool(freigabe and (freigabe.get("entscheidung") or {}).get("art") == "erteilt")
    d["einladung_am"] = erstes_datum(d, ("gespraechseinladung",))
    d["gespraech_am"] = erstes_datum(d, GESPRAECHE)
    d["angebot_am"] = erstes_datum(d, ("angebot",))
    d["ergebnis_am"] = erstes_datum(d, ERGEBNISARTEN)
    return d


def ist(flag):
    return lambda d: flag in d["flags"]


def kennzahl(name, definition, basis, test, alter_ab, reife, heute_datum, belege):
    """One rate: numerator, denominator, interval, the same rate among applications old enough to have had a reply, and on request the Vorgänge behind it.

    `alter_ab` is the field whose date starts the clock. A Vorgang without that date is not guessed into either group (`ohne_alter`)."""
    zaehler = [d for d in basis if test(d)]
    reif = [d for d in basis if d.get(alter_ab) and tage(d[alter_ab], heute_datum) >= reife]
    jung = [d for d in basis if d.get(alter_ab) and tage(d[alter_ab], heute_datum) < reife]
    ergebnis = {"name": name, "definition": definition, **quote(len(zaehler), len(basis)),
                "reif": {"reife_tage": reife, **quote(sum(1 for d in reif if test(d)), len(reif)), "noch_jung": len(jung),
                         "noch_jung_mit_ereignis": sum(1 for d in jung if test(d)), "ohne_alter": len(basis) - len(reif) - len(jung)}}
    if belege:
        ergebnis["belege"] = {"zaehler": sorted(d["slug"] for d in zaehler), "nenner": sorted(d["slug"] for d in basis),
                              "noch_jung": sorted(d["slug"] for d in jung), "ohne_alter": sorted(d["slug"] for d in basis if not d.get(alter_ab))}
    return ergebnis


def abstaende(alle, von, bis):
    """Days between two dates of the same Vorgang, only where both exist. Counted apart: end without start, and an end before the start."""
    werte, ohne_start, negativ, beobachtet = [], 0, 0, 0
    for d in alle:
        ende = d.get(bis) if isinstance(bis, str) else bis(d)
        if not ende:
            continue
        beobachtet += 1
        start = d.get(von) if isinstance(von, str) else von(d)
        if not start:
            ohne_start += 1
            continue
        abstand = tage(start, ende)
        if abstand < 0:
            negativ += 1
            continue
        werte.append(abstand)
    ergebnis = {"n": len(werte), "ende_beobachtet": beobachtet, "ohne_startdatum": ohne_start, "ende_vor_start": negativ}
    if werte:
        ergebnis.update(median_tage=statistics.median(werte), min_tage=min(werte), max_tage=max(werte))
    if len(werte) < MIN_N:
        ergebnis["eingeschraenkt"] = True
    return ergebnis


def zeitkennzahlen(alle, stellen):
    """The times of the process from stored dates (EA-19). The date an event happened is `eingetreten_am`; when it was recorded is `erfasst`."""
    nach_vorgang = {s.get("vorgang"): s for s in (stellen or {}).values() if s.get("vorgang")}
    for d in alle:
        s = nach_vorgang.get(d["slug"])
        d["entdeckt_am"] = tag10((s or {}).get("erstmals_gesehen"))
        d["rueckmeldung_nach_gespraech_am"] = ""
        tage_ = sorted(x for x in (ereignis_tag(e) for e in d["ereignisse"] if e["art"] in INHALTLICH) if x)
        d["erste_antwort_am"] = tage_[0] if tage_ else ""
        if d["gespraech_am"]:
            nachher = sorted(x for x in (ereignis_tag(e) for e in d["ereignisse"] if e["art"] in tuple(set(INHALTLICH + ("angebot",))) and e["art"] not in GESPRAECHE and e["art"] != "gespraechseinladung") if x and x > d["gespraech_am"])
            d["rueckmeldung_nach_gespraech_am"] = nachher[0] if nachher else ""
    erfassung = []
    for d in alle:
        for e in d["ereignisse"]:
            tag, erfasst = ereignis_tag(e), tag10(e.get("erfasst"))
            if tag and erfasst:
                erfassung.append(tage(tag, erfasst))
    metriken = {
        "entdeckung_bis_beginn": abstaende(alle, "entdeckt_am", "erfasst"),
        "beginn_bis_fertig": abstaende(alle, "erfasst", "fertig_am"),
        "fertig_bis_einreichung": abstaende(alle, "fertig_am", "versendet_am"),
        "einreichung_bis_erste_antwort": abstaende(alle, "versendet_am", "erste_antwort_am"),
        "einreichung_bis_einladung": abstaende(alle, "versendet_am", "einladung_am"),
        "einladung_bis_gespraech": abstaende(alle, "einladung_am", "gespraech_am"),
        "gespraech_bis_rueckmeldung": abstaende(alle, "gespraech_am", "rueckmeldung_nach_gespraech_am"),
        "einreichung_bis_ergebnis": abstaende(alle, "versendet_am", "ergebnis_am"),
    }
    metriken["erfassung_nach_ereignis"] = {"n": len(erfassung), **({"median_tage": statistics.median(erfassung), "max_tage": max(erfassung)} if erfassung else {}),
                                           "hinweis": "Tage zwischen dem Datum, an dem etwas geschah, und dem Tag, an dem es erfasst wurde (nur Ereignisse mit beiden Angaben)"}
    letzte = sorted(str(e.get("erfasst", "")) for d in alle for e in d["ereignisse"] if e.get("erfasst"))
    return {"metriken": metriken, "datenstand": {"neueste_erfassung": letzte[-1] if letzte else "", "ereignisse": sum(len(d["ereignisse"]) for d in alle)},
            "hinweis": "Jede Zeit rechnet nur mit gespeicherten Daten. Fehlt ein Datum, steht der Fall unter ohne_startdatum und wird nicht geschätzt."}


def aktivitaet_und_konversionen(alle, stellen, reife, heute_datum, belege):
    versendet = [d for d in alle if d["versendet_am"]]
    fertige = [d for d in alle if d["fertig"]]
    relevante, uebernommen = [], []
    if stellen is not None:
        for s in stellen.values():
            if s.get("bearbeitung") != "abgelehnt" and ss.prefilter_class(s) != "veto":
                relevante.append({"slug": s["id"], "tag": tag10(s.get("erstmals_gesehen")), "uebernommen": s.get("bearbeitung") == "übernommen"})
    z = lambda flag: sum(1 for d in versendet if flag in d["flags"])  # noqa: E731
    bewertungen = Counter(d["bewertung"] for d in alle)
    akt = {
        "stellen_recherchiert": {"n": None if stellen is None else len(stellen), "quelle": "warteschlange",
                                 "hinweis": "nur Stellen der Warteschlange (Suchaufträge); die Suchprotokolle der interaktiven Suche werden nicht gezählt" if stellen is not None else "keine Warteschlange vorhanden: nicht erfasst"},
        "stellen_relevant": {"n": None if stellen is None else len(relevante), "quelle": "warteschlange", "hinweis": "nicht abgelehnt und kein Veto der Vorprüfung"},
        "stellen_uebernommen": {"n": None if stellen is None else sum(1 for r in relevante if r["uebernommen"]), "quelle": "warteschlange"},
        "bewertung_passung": {"quelle": "passung.md", **{k: v for k, v in sorted(bewertungen.items())}},
        "bewerbungen_begonnen": {"n": len(alle), "quelle": "vorgang.md"},
        "unterlagen_fertig": {"n": len(fertige), "quelle": "status (erstellt, geprüft) oder versendet_am"},
        "freigegeben": {"n": None if not alle or alle[0]["freigegeben"] is None else sum(1 for d in alle if d["freigegeben"]), "quelle": "workflow (versand_freigabe)",
                        "hinweis": "kein Workflow-Speicher: nicht erfasst" if alle and alle[0]["freigegeben"] is None else "eine ausdrückliche Freigabe im Workflow; keine Freigabe bedeutet nicht, dass nichts gesendet wurde"},
        "eingereicht": {"n": len(versendet), "quelle": "versendet_am"},
        "eingangsbestaetigung": {"n": z("eingangsbestaetigung"), "quelle": "bestätigte Ereignisse"},
        "arbeitgeberantworten": {"n": z("rueckmeldung"), "quelle": "bestätigte Ereignisse oder Status", "hinweis": "ohne bloße Eingangsbestätigung"},
        "absagen": {"n": z("absage")}, "einladungen": {"n": z("einladung"), "hinweis": "eine Einladung ist kein geführtes Gespräch"},
        "gespraeche_gefuehrt": {"n": z("gespraech"), "hinweis": "nur mit einem Ereignis `gespraech`, `technisches_gespraech` oder `assessment`"},
        "angebote": {"n": z("angebot")}, "angebote_angenommen": {"n": z("angenommen")}, "angebote_abgelehnt": {"n": z("angebot_abgelehnt")},
        "zurueckgezogen": {"n": z("zurueckgezogen")}, "ohne_antwort_abgeschlossen": {"n": z("ohne_antwort")},
        "offen_ohne_rueckmeldung": {"n": sum(1 for d in versendet if d["offen"] and "rueckmeldung" not in d["flags"]), "hinweis": "kein Misserfolg und keine Absage"},
    }
    k = lambda *a: kennzahl(*a, reife, heute_datum, belege)  # noqa: E731
    konv = [
        k("begonnen_zu_fertig", "Begonnene Bewerbungen, deren Unterlagen fertig sind / alle begonnenen Bewerbungen. Offene Bewerbungen stehen im Nenner.", alle, lambda d: d["fertig"], "erfasst"),
        k("fertig_zu_eingereicht", "Fertige Bewerbungen mit `versendet_am` / alle fertigen Bewerbungen. Eine fertige Bewerbung ist nicht eingereicht.", fertige, lambda d: bool(d["versendet_am"]), "fertig_am"),
        k("eingereicht_zu_eingangsbestaetigung", "Eingereichte Bewerbungen mit bestätigtem Bewerbungseingang / alle eingereichten Bewerbungen.", versendet, ist("eingangsbestaetigung"), "versendet_am"),
        k("eingereicht_zu_rueckmeldung", "Eingereichte Bewerbungen mit mindestens einer inhaltlichen, bestätigten Rückmeldung (ohne bloße Eingangsbestätigung) / alle eingereichten Bewerbungen. Keine Rückmeldung bekannt ist keine Absage.", versendet, ist("rueckmeldung"), "versendet_am"),
        k("eingereicht_zu_einladung", "Eingereichte Bewerbungen mit Einladung / alle eingereichten Bewerbungen.", versendet, ist("einladung"), "versendet_am"),
        k("gespraech_zu_angebot", "Bewerbungen mit geführtem Gespräch, die ein Angebot erhielten / Bewerbungen mit geführtem Gespräch.", [d for d in versendet if "gespraech" in d["flags"]], ist("angebot"), "gespraech_am"),
        k("angebot_zu_angenommen", "Bewerbungen mit Angebot, das angenommen wurde / Bewerbungen mit Angebot. Ein angenommenes Angebot ist noch keine Einstellung.", [d for d in versendet if "angebot" in d["flags"]], ist("angenommen"), "angebot_am"),
    ]
    if stellen is not None:
        konv.insert(0, {"name": "relevant_zu_begonnen", "definition": "Relevante Stellen der Warteschlange, die übernommen wurden / relevante Stellen (nicht abgelehnt, kein Veto der Vorprüfung).",
                        **quote(sum(1 for r in relevante if r["uebernommen"]), len(relevante)), "reif": None, "hinweis": "nur Stellen der Warteschlange"})
    return akt, konv


def widersprueche(w, now, gruppe):
    """Contradictions and gaps that BE-10 finds for these Vorgänge. They are shown, never repaired or hidden."""
    import bewerbung as bw  # noqa: PLC0415 - bewerbung imports this module
    befunde = []
    for d in gruppe:
        try:
            befunde += [b for b in bw.pruefe_vorgang(w, d["slug"], now) if b["grad"] in ("Fehler", "Warnung")]
        except Refused as error:
            befunde.append({"grad": "Fehler", "regel": "R03-LESEN", "vorgang": d["slug"], "ereignis": "", "befund": error.meldung})
    return befunde


# ---------------------------------------------------------------- results by the user's statement (EA-3)

def ergebnis_erfassen(w, slug, art, datum, original, optionen, now):
    km.vorgang_meta(w, slug)
    if art not in km.ARTEN:
        raise Refused("art_unbekannt", f"Ergebnisart {redact(art, 40)} ist nicht bekannt ({', '.join(km.ARTEN)})")
    if ss.valid_date(datum) != datum or not datum:
        raise Refused("datum_ungueltig", "--datum ist ein echtes Datum der Form JJJJ-MM-TT; ein fehlendes Datum wird nicht geschätzt")
    nv = km.lade_nachverfolgung(w, slug)
    interpretation = None
    if optionen.get("kategorie"):
        if not km.KATEGORIE_FORM.fullmatch(optionen["kategorie"]):
            raise Refused("kategorie_ungueltig", "--kategorie besteht aus a-z, 0-9 und _")
        interpretation = {"kategorie": optionen["kategorie"], "bezeichnung": optionen["kategorie"], "thema": clean_text(optionen.get("thema", ""), 80),
                          "aussage": clean_text(optionen.get("aussage", ""), 160), "sicherheit": "mittel", "grund_genannt": True,
                          "hinweis": "vom Nutzer erfasst; keine bestätigte Qualifikationslücke"}
    ereignis, neu = km.ereignis_bauen(nv, slug, art, datum, {"typ": "nutzer", "nachricht_id": optionen.get("nachricht", "")}, km.schwaerze(original)[:km.ORIGINAL_MAX],
                                      interpretation, "bestaetigt", now, "manuell", "bestaetigt", gewissheit="eindeutig")
    if not neu:
        return {"ok": True, "ereignis": ereignis, "neu": False, "hinweis": "Dieses Ereignis ist schon erfasst; es wird nicht doppelt gespeichert."}
    km.schreibe_verlauf(w, slug, [f"- {datum}: Ergebnis erfasst: {art} (Ereignis {ereignis['id']}, Angabe der Nutzerin oder des Nutzers)"], None)
    km.speichere_nachverfolgung(w, slug, nv)
    return {"ok": True, "ereignis": ereignis, "neu": True, "hinweis": "Der Status in vorgang.md bleibt unverändert; ihn pflegt die Nutzerin oder der Nutzer."}


def ergebnis_aendern(w, slug, ereignis_id, aktion, felder, now):
    nv = km.lade_nachverfolgung(w, slug)
    e = next((x for x in nv["ereignisse"] if x["id"] == ereignis_id), None)
    if e is None:
        raise Refused("ereignis_unbekannt", f"Kein Ereignis {redact(ereignis_id, 40)} in {slug}")
    if e["status"] == "verworfen":
        raise Refused("bereits_verworfen", "Ein verworfenes Ereignis wird nicht wieder geändert")
    vorher = {k: e.get(k) for k in ("art", "datum", "status")}
    if aktion == "verwerfen":
        e["status"] = "verworfen"
    else:
        if felder.get("art"):
            if felder["art"] not in km.ARTEN:
                raise Refused("art_unbekannt", f"Ergebnisart {redact(felder['art'], 40)} ist nicht bekannt")
            e["art"] = felder["art"]
        if felder.get("datum"):
            if ss.valid_date(felder["datum"]) != felder["datum"]:
                raise Refused("datum_ungueltig", "--datum ist ein echtes Datum der Form JJJJ-MM-TT")
            e["datum"] = felder["datum"]
            e["eingetreten_am"] = felder["datum"]
        if e["status"] in BESTAETIGT:  # a correction of a fact; an unconfirmed event stays unconfirmed (the user confirms it apart)
            e["status"] = "korrigiert"
        if e.get("schluessel"):  # the key follows kind and day, and two live events must not share one
            quelle = e.get("quelle") or {}
            e["schluessel"] = km.schluessel_von(slug, e["art"], e.get("eingetreten_am", ""), quelle.get("nachricht_id") or quelle.get("referenz") or (e.get("beschreibung") or "")[:40], quelle.get("typ"))
            if any(x is not e and x.get("schluessel") == e["schluessel"] and x.get("status") != "verworfen" for x in nv["ereignisse"]):
                raise Refused("ereignis_doppelt", "Mit dieser Art und diesem Tag gibt es das Ereignis schon: es würde doppelt gezählt")
    e.setdefault("korrekturen", []).append({"am": stamp(now), "vorher": vorher, "grund": clean_text(felder.get("grund", ""), 160)})
    km.speichere_nachverfolgung(w, slug, nv)
    return {"ok": True, "ereignis": ereignis_id, "status": e["status"]}


# ---------------------------------------------------------------- retrospective (EA-9)

def herkunft(e):
    """Who says what in a refusal (EA-6, EA-18): the employer's words, the user's own assessment, or the system's guess. Never mixed."""
    i = e.get("interpretation") or {}
    typ = (e.get("quelle") or {}).get("typ", "")
    if not i.get("grund_genannt"):
        return {"grund": "kein Grund genannt: Grund unbekannt", "kategorie": ""}
    nutzer = e.get("status") == "korrigiert" or i.get("sicherheit") != "niedrig"  # a pattern in the wording is always `niedrig`; only the user raises it
    grund = "Einschätzung der Nutzerin oder des Nutzers" if typ == "nutzer" and not e.get("original") else \
        "vom Arbeitgeber genannt (Wortlaut der Nachricht)" if typ == "nachricht" else "Quelle des Wortlauts unbekannt"
    return {"grund": grund, "kategorie": f"Kategorie „{i.get('bezeichnung', '')}“ " + ("von der Nutzerin oder dem Nutzer erfasst oder bestätigt" if nutzer
                                                                                    else "ist eine Vermutung des Systems (Muster im Wortlaut, nicht bestätigt)")}


def segmentiere(gruppe, nach, heute_datum):
    gruppen = {}
    for d in gruppe:
        gruppen.setdefault(schluessel_von(d, nach), []).append(d)
    ergebnis = {}
    for k, v in sorted(gruppen.items()):
        alter = [tage(d["versendet_am"], heute_datum) for d in v if d["versendet_am"]]
        ergebnis[k] = {"bewerbungen": len(v), "rueckmeldung": quote(sum(1 for d in v if "rueckmeldung" in d["flags"]), len(v)),
                       "einladung": quote(sum(1 for d in v if "einladung" in d["flags"]), len(v)), "vergleichbar": len(v) >= MIN_N,
                       "zusammensetzung": {"ausrichtung": dict(sorted(Counter(d["ausrichtung"] for d in v).items())),
                                           "stellenprofil": dict(sorted(Counter(d["stellenprofil"] for d in v).items())),
                                           "mittleres_alter_tage": statistics.median(alter) if alter else None}}
    vergleichbar = [g for g in ergebnis.values() if g["vergleichbar"]]
    hinweise = []
    def anteile(g):
        summe = sum(g["zusammensetzung"]["ausrichtung"].values()) or 1
        return {k_: v_ / summe for k_, v_ in g["zusammensetzung"]["ausrichtung"].items()}
    if len(vergleichbar) >= 2 and any(abs(anteile(a).get(k_, 0) - anteile(b).get(k_, 0)) > 0.25 for a in vergleichbar for b in vergleichbar
                                      for k_ in set(anteile(a)) | set(anteile(b))):
        hinweise.append("Die Gruppen unterscheiden sich in der Ausrichtung der Bewerbungen: ein Unterschied der Quoten kann daran liegen.")
    if len(vergleichbar) >= 2:
        alter = [g["zusammensetzung"]["mittleres_alter_tage"] for g in vergleichbar if g["zusammensetzung"]["mittleres_alter_tage"] is not None]
        if alter and max(alter) - min(alter) > 30:
            hinweise.append("Die Gruppen sind unterschiedlich lange beobachtet (mittleres Alter weicht um mehr als 30 Tage ab): die Quoten sind nicht gleich weit gereift.")
    if len(vergleichbar) < 2:
        hinweise.append(f"Weniger als zwei Gruppen mit mindestens {MIN_N} Bewerbungen: es gibt keinen Vergleich, nur Zahlen je Gruppe.")
    return ergebnis, hinweise


def qualitaetsbefunde(w, gruppe):
    """How often a check of the quality gate failed or blocked, over the Vorgänge: a count of observations, not a cause."""
    import qualitaet as qa  # noqa: PLC0415
    zaehler = {}
    for d in gruppe:
        bericht = load_report(os.path.join(w, d["slug"]))
        for c in (bericht or {}).get("checks", []):
            if c.get("status") in (qa.FAIL, qa.BLOCKED):
                zaehler.setdefault(c["id"], set()).add(d["slug"])
    return {k: sorted(v) for k, v in sorted(zaehler.items())}


def datenluecken(stat, stellen, population):
    luecken = []
    if stat["ausgewertet"] < MIN_N:
        luecken.append(f"Nur {stat['ausgewertet']} eingereichte Bewerbungen: unter {MIN_N} sind Quoten Momentaufnahmen. Es braucht mehr eingereichte Bewerbungen mit bekanntem Ergebnis.")
    if stellen is None:
        luecken.append("Keine Warteschlange: die Zahl recherchierter und relevanter Stellen ist nicht erfasst (nur Suchaufträge schreiben sie).")
    if population and population[0].get("freigegeben") is None:
        luecken.append("Kein Workflow-Speicher: ausdrückliche Freigaben sind nicht erfasst.")
    q = stat["datenqualitaet"]
    if q["ergebnis_nur_durch_status"]:
        luecken.append(f"{q['ergebnis_nur_durch_status']} Ergebnisse stehen nur im Status, ohne Ereignis: das Datum und der Beleg fehlen.")
    if q["ereignisse_ohne_datum"]:
        luecken.append(f"{q['ereignisse_ohne_datum']} bestätigte Ereignisse haben kein Datum: sie zählen, aber keine Zeit wird berechnet.")
    if q["dokumentversion_nicht_eindeutig"]:
        luecken.append(f"{q['dokumentversion_nicht_eindeutig']} Bewerbungen haben keine eindeutige Dokumentversion: ein Vergleich nach Fassung ist dort nicht möglich.")
    return luecken


def retrospektive(w, now, von, bis, filter_, konfiguration=None, reife=REIFE_TAGE_STANDARD):
    gewaehlt = waehle(w, now, von, bis, filter_)  # read once: the figures and the lists come from the same Vorgänge
    alle = waehle_alle(w, now, von, bis, filter_)
    stat = statistik(w, now, von, bis, None, filter_, gewaehlt, reife, False, alle)
    neue_regeln = not any((filter_ or {}).values()) and not von and not bis and reife == REIFE_TAGE_STANDARD
    if neue_regeln:  # the rules look at the whole Wurzel; a report with criteria must not write them (it only shows what exists)
        erzeuge_vorschlaege(w, now, konfiguration, reife)  # idempotent: a proposal exists once; it changes nothing until the user decides
    gruppe, population = gewaehlt[0], alle[0]
    stellen = lade_stellen(w)
    absagen, themen = [], {}
    for d in gruppe:
        for e in d["ereignisse"]:
            i = e.get("interpretation")
            if e["art"].startswith("absage"):
                absagen.append((d["slug"], e))
            if i and i.get("grund_genannt"):
                schluessel = i.get("thema") or i.get("kategorie")
                themen.setdefault(schluessel, set()).add(d["slug"])
    wiederholt = {k: sorted(v) for k, v in themen.items() if len(v) >= 2}
    heute_datum = km.heute(now)
    k, q = stat["zaehler"], stat["datenqualitaet"]
    konv = {c["name"]: c for c in stat["konversionen"]}

    def zeile(c):
        reif = c["reif"]
        text = f"{c['zaehler']} von {c['nenner']}"
        if c["konfidenz95"]:
            text += f", 95 %-Intervall {c['konfidenz95'][0]:.0%} bis {c['konfidenz95'][1]:.0%}"
        if c["eingeschraenkt"]:
            text += " – Momentaufnahme, zu wenige Fälle"
        if reif and reif["nenner"] + reif["noch_jung"]:
            text += f"; mindestens {reif['reife_tage']} Tage alt: {reif['zaehler']} von {reif['nenner']}" + (" – zu wenige Fälle" if reif["eingeschraenkt"] else "")
            if reif["noch_jung"]:
                text += f"; noch jünger: {reif['noch_jung']} (davon {reif['noch_jung_mit_ereignis']} mit Ereignis)"
        return text
    zeiten = stat["zeiten"]["metriken"]

    def zeit(name, titel):
        m = zeiten[name]
        wert = f"Median {m['median_tage']:g} Tage (n={m['n']}" + (", wenige Werte" if m.get("eingeschraenkt") else "") + ")" if m["n"] else "kein Wert (n=0)"
        return f"- {titel}: {wert}" + (f"; ohne Startdatum: {m['ohne_startdatum']}" if m["ohne_startdatum"] else "") + (f"; Ende vor Start: {m['ende_vor_start']}" if m["ende_vor_start"] else "")
    nicht_fertig = [d["slug"] for d in population if not d["fertig"] and d["erfasst"] and tage(d["erfasst"], heute_datum) >= reife]
    nicht_gesendet = [d["slug"] for d in population if d["fertig"] and not d["versendet_am"] and d.get("fertig_am") and tage(d["fertig_am"], heute_datum) >= reife]
    qualitaet = qualitaetsbefunde(w, population)
    zeilen = [
        "---", "abgeleitet: ja", f"erstellt: {stamp(now)}", f"zeitraum_von: {von or ''}", f"zeitraum_bis: {bis or ''}", f"reife_tage: {reife}",
        f"filter: {json.dumps({k_: v_ for k_, v_ in (filter_ or {}).items() if v_}, ensure_ascii=False)}",
        f"quellen_hash: {stat['quellen_hash']}", f"ausgewertet: {stat['ausgewertet']}", "---", "",
        "# Retrospektive der Bewerbungen", "",
        "Abgeleitete Auswertung: Quelle der Wahrheit bleiben `vorgang.md`, `nachverfolgung.json` und die übrigen Dateien der Vorgänge. Ändert sich eine Quelle, ist diese Datei veraltet (`lernen.py aktualitaet`). "
        "Die Beobachtungen beschreiben die erfassten Daten; sie sagen nicht, warum etwas geschah.", "",
        "## A. Zusammenfassung", "",
        f"- Betrachtet: {stat['population']['begonnen']} begonnene Bewerbungen, davon eingereicht: {stat['ausgewertet']} (Zeitraum nach Versand- oder Erfassungstag: {von or 'offen'} bis {bis or 'offen'}; Filter: "
        f"{json.dumps(stat['filter'], ensure_ascii=False) if stat['filter'] else 'keine'})",
        f"- Bekannte inhaltliche Rückmeldungen: {zeile(konv['eingereicht_zu_rueckmeldung'])}",
        f"- Eingangsbestätigungen: {zeile(konv['eingereicht_zu_eingangsbestaetigung'])}",
        f"- Einladungen: {k['einladung']}; geführte Gespräche: {k['gespraech']}; Angebote: {k['angebot']}; Einstellungen: {k['einstellung']}; Absagen: {k['absage']}",
        f"- Noch offen: {k['offen']} eingereichte Bewerbungen, davon ohne bekannte Rückmeldung: {k['offen_ohne_rueckmeldung']}. Eine fehlende Rückmeldung ist keine Absage.",
        f"- Vollständigkeit: Ergebnis nur aus Status {q['ergebnis_nur_durch_status']}; Ereignisse zur Prüfung {q['ereignisse_zur_pruefung']}; ungeprüfte Nachrichten {q['nachrichten_noch_nicht_geprueft']}; "
        f"Ereignisse ohne Datum {q['ereignisse_ohne_datum']}; Widersprüche oder Lücken nach BE-10: {len(q['widersprueche'])}; Dokumentversion nicht eindeutig {q['dokumentversion_nicht_eindeutig']}",
        f"- Ausgeschlossen (eingereicht): {', '.join(f'{a} ({n})' for a, n in sorted(q['ausgeschlossen'].items())) or 'keine'}; (begonnen): "
        f"{', '.join(f'{a} ({n})' for a, n in sorted(stat['population']['ausgeschlossen_begonnen'].items())) or 'keine'}",
        f"- Nicht erfasst (kein Feld): {', '.join(NICHT_ERFASST)}", "",
        "## B. Prozessqualität", "",
        "Jeder Punkt ist als **Prozess** (etwas bleibt liegen) oder **Datenlücke** (etwas ist nicht erfasst) gekennzeichnet; eine Datenlücke ist kein Prozessproblem.", "",
        f"- Prozess: begonnen → Unterlagen fertig: {zeile(konv['begonnen_zu_fertig'])}",
        f"- Prozess: fertig → eingereicht: {zeile(konv['fertig_zu_eingereicht'])}",
        f"- Prozess: nach mindestens {reife} Tagen nicht fertig: {len(nicht_fertig)}" + (f" ({', '.join(nicht_fertig)})" if nicht_fertig else ""),
        f"- Prozess: fertig und nach mindestens {reife} Tagen nicht eingereicht: {len(nicht_gesendet)}" + (f" ({', '.join(nicht_gesendet)})" if nicht_gesendet else ""),
        zeit("entdeckung_bis_beginn", "Von der Entdeckung der Stelle bis zum Beginn (nur mit Warteschlange erfassbar)"), zeit("beginn_bis_fertig", "Beginn bis fertige Unterlagen"),
        zeit("fertig_bis_einreichung", "Fertige Unterlagen bis Einreichung")]
    zeilen += [f"- Prozess: Prüfung {c} schlug in {len(v)} Vorgängen fehl oder blockierte ({', '.join(v)}); das ist eine Häufung, keine Ursache." for c, v in qualitaet.items() if len(v) >= 2] or \
              ["- Qualitätsprüfung: kein Check schlug in mindestens zwei Vorgängen fehl, oder es gibt keinen Bericht."]
    zeilen += ["", "## C. Reaktionen des Arbeitsmarkts", "",
               f"- Einreichung → Rückmeldung: {zeile(konv['eingereicht_zu_rueckmeldung'])}", f"- Einreichung → Einladung: {zeile(konv['eingereicht_zu_einladung'])}",
               f"- Gespräch → Angebot: {zeile(konv['gespraech_zu_angebot'])}", f"- Angebot → angenommen: {zeile(konv['angebot_zu_angenommen'])}",
               zeit("einreichung_bis_erste_antwort", "Einreichung bis erste Antwort"), zeit("einreichung_bis_einladung", "Einreichung bis Einladung"),
               zeit("einladung_bis_gespraech", "Einladung bis Gespräch"), zeit("gespraech_bis_rueckmeldung", "Gespräch bis Rückmeldung"),
               zeit("einreichung_bis_ergebnis", "Einreichung bis bekanntes Ergebnis"), ""]
    for nach in ("quelle", "ausrichtung", "kanal"):
        gruppen, hinweise = segmentiere(gruppe, nach, heute_datum)
        zeilen.append(f"Nach {nach}:")
        zeilen += [f"- {g}: {v['bewerbungen']} Bewerbungen, Rückmeldung {v['rueckmeldung']['zaehler']} von {v['rueckmeldung']['nenner']}" +
                   ("" if v["vergleichbar"] else " (zu wenig für einen Vergleich)") for g, v in gruppen.items()] or ["- keine"]
        zeilen += [f"  Hinweis: {h}" for h in hinweise] + [""]
    zeilen += ["Absagen und genannte Gründe (die Herkunft steht jeweils dabei):", ""]
    if absagen:
        for slug, e in sorted(absagen, key=lambda x: x[1].get("datum") or ""):
            i, h = e.get("interpretation") or {}, herkunft(e)
            zeilen.append(f"- {slug} ({e.get('datum') or 'Datum unbekannt'}): {h['grund']}" + (f"; {h['kategorie']}; Wortlaut: „{e.get('original', '')}“" if i.get("grund_genannt") else ""))
    else:
        zeilen.append("- Keine bestätigte Absage im Zeitraum.")
    zeilen += ["", "Wiederholt angesprochene Themen:", ""]
    zeilen += [f"- {t}: in {len(v)} Vorgängen genannt ({', '.join(v)}). Das ist eine Häufung der Aussagen, keine Ursache." for t, v in sorted(wiederholt.items())] or \
              ["- Kein Thema wurde in mindestens zwei Vorgängen genannt."]
    zeilen += ["", "## D. Verbesserungsmöglichkeiten", "",
               "Jeder Vorschlag ist dokumentiert (`lernen.py vorschlag zeige <id>`). Er ändert nichts, bis du entscheidest; auch eine Annahme ändert keine Datei.", ""]
    if not neue_regeln:
        zeilen += ["Dieser Bericht nutzt Kriterien (Zeitraum, Filter oder eine andere Reife): er legt keine neuen Vorschläge an und zeigt nur die vorhandenen.", ""]
    vorschlaege = [v for v in lade_vorschlaege(w)["vorschlaege"].values() if v["status"] in ("erstellt", "zur_pruefung", "zurueckgestellt")]
    rang = {"hoch": 0, "mittel": 1, "niedrig": 2}
    for v in sorted(vorschlaege, key=lambda x: (rang.get(x["prioritaet"], 3), x["id"])):
        zeilen += [f"### {v['id']}: {v['titel']} (Priorität {v['prioritaet']}, Status {v['status']})", "",
                   f"- Beobachtung: {v['beobachtung']}", f"- Betroffen: {', '.join(sorted({q_['vorgang'] for q_ in v['quellen']})) or '-'}",
                   f"- Mögliche Erklärung: {v.get('erklaerung') or v['begruendung']}", f"- Unsicherheit: {v['unsicherheit']}",
                   f"- Empfehlung: {v.get('empfehlung') or v['begruendung']}", f"- Erwarteter Nutzen: {v['erwarteter_nutzen']}",
                   f"- Wirksamkeit prüfen: {(v.get('pruefung') or {}).get('wie', 'nicht über eine Kennzahl prüfbar; die Nutzerin oder der Nutzer beurteilt es selbst')}", ""]
    if not vorschlaege:
        zeilen += ["Keine offenen Vorschläge: Die vorhandenen Daten tragen derzeit keinen Vorschlag.", ""]
    fehlt = datenluecken(stat, stellen, population)
    zeilen += ["Fehlende Daten, die Aussagen und Vorschläge begrenzen:", ""] + ([f"- {x}" for x in fehlt] or ["- keine bekannten Lücken"])
    zeilen += ["", "## Einschränkungen", ""] + [f"- {g}" for g in GRENZEN]
    ordner = os.path.join(w, "lernen")
    kriterien = json.dumps([von, bis, reife, sorted((k_, v) for k_, v in (filter_ or {}).items() if v)])
    name = f"retrospektive-{km.heute(now)}" + (f"-{digest(kriterien)[:6]}" if von or bis or reife != REIFE_TAGE_STANDARD or any((filter_ or {}).values()) else "") + ".md"
    pfad = os.path.join(ordner, name)  # other criteria on the same day give another file; the same criteria replace the earlier one
    os.makedirs(ordner, exist_ok=True)
    temp = pfad + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(zeilen))
    os.replace(temp, pfad)
    return {"ok": True, "datei": f"lernen/{name}", "ausgewertet": stat["ausgewertet"], "quellen_hash": stat["quellen_hash"], "wiederholte_themen": sorted(wiederholt),
            "vorschlaege_offen": len(vorschlaege), "datenluecken": len(fehlt)}


def fmt(q):
    return f"{q['zaehler']} von {q['nenner']}" + (" – eingeschränkt" if q["eingeschraenkt"] else "")


def aktualitaet(w, now, datei):
    pfad = os.path.join(w, datei)
    if not os.path.isfile(pfad):
        raise Refused("datei_fehlt", f"{redact(datei, 80)} gibt es nicht")
    meta = ss.read_frontmatter(pfad)
    von, bis = meta.get("zeitraum_von") or None, meta.get("zeitraum_bis") or None
    try:
        filter_ = json.loads(meta.get("filter") or "{}")
    except ValueError:
        filter_ = {}
    gruppe, _ = waehle_alle(w, now, von, bis, filter_ if isinstance(filter_, dict) else {})  # the same criteria the file was made with
    aktuell = quellen_hash(w, gruppe) == meta.get("quellen_hash")
    return {"ok": True, "datei": datei, "aktuell": aktuell, "hinweis": "" if aktuell else "Eine Quelle hat sich geändert (oder das Löschdatum ist erreicht): die Retrospektive neu erstellen"}


# ---------------------------------------------------------------- proposals (EA-10, EA-11)

def vorschlaege_pfad(w):
    return os.path.join(w, "lernen", "vorschlaege.json")


def lade_vorschlaege(w):
    daten = load_json(vorschlaege_pfad(w), {"version": 1, "vorschlaege": {}})
    if daten.get("version") != 1 or not isinstance(daten.get("vorschlaege"), dict):
        raise Refused("speicher_ungueltig", "lernen/vorschlaege.json hat kein bekanntes Format (version 1)")
    for vid, v in daten["vorschlaege"].items():
        if not isinstance(v, dict) or v.get("id") != vid or v.get("status") not in VORSCHLAG_STATUS or not isinstance(v.get("quellen"), list):
            raise Refused("speicher_ungueltig", f"Der Vorschlag {redact(vid, 40)} ist unvollständig")
    return daten


def vorschlag_quellen_hash(w, quellen):
    teile = []
    for q in quellen:
        pfad = os.path.join(w, q["vorgang"], "nachverfolgung.json")
        try:
            ereignisse = {e["id"]: e for e in km.lade_nachverfolgung(w, q["vorgang"])["ereignisse"]}
        except Refused:
            ereignisse = {}
        e = ereignisse.get(q.get("ereignis"))
        teile.append(f"{q['vorgang']}/{q.get('ereignis', '-')}={digest(json.dumps(e, sort_keys=True)) if e and e.get('status') in BESTAETIGT else 'weg'}"
                     if q.get("ereignis") else f"{q['vorgang']}={'da' if os.path.isfile(os.path.join(w, q['vorgang'], 'vorgang.md')) else 'weg'}")  # without an event only the existence counts
        _ = pfad
    return digest(*teile)


def aktueller_wert(w, now, name, reife=REIFE_TAGE_STANDARD):
    """(Zähler, Nenner) of a named measure now, for the check of a proposal's effect. A name that is not known is refused."""
    stat = statistik(w, now, reife=reife, mit_widerspruechen=False)
    for c in stat["konversionen"]:
        if c["name"] == name:
            return (c["reif"]["zaehler"], c["reif"]["nenner"]) if c["reif"] and name != "relevant_zu_begonnen" else (c["zaehler"], c["nenner"])
    q = stat["datenqualitaet"]
    if name in ("ergebnis_nur_durch_status", "ereignisse_zur_pruefung", "nachrichten_noch_nicht_geprueft", "dokumentversion_nicht_eindeutig", "ereignisse_ohne_datum"):
        return q[name], stat["ausgewertet"]
    if name == "begonnen_trotz_veto":
        gruppe, _ = waehle_alle(w, now)
        return sum(1 for d in gruppe if d["bewertung"] == "Veto"), len(gruppe)
    if name.startswith("qualitaet_fehler:"):
        gruppe, _ = waehle_alle(w, now)
        return len(qualitaetsbefunde(w, gruppe).get(name.split(":", 1)[1], [])), len(gruppe)
    raise Refused("kennzahl_unbekannt", f"Die Kennzahl {redact(name, 50)} gibt es nicht")


def erzeuge_vorschlaege(w, now, konfiguration, reife=REIFE_TAGE_STANDARD):
    """Proposals from fixed rules over confirmed results. A rule that needs a deadline the user did not set does not run."""
    gruppe, _ = waehle(w, now)
    alle, _ = waehle_alle(w, now)
    tasks, heute_datum = lade_workflow(w), km.heute(now)
    for d in alle:
        anreichern(d, w, tasks)
    daten = lade_vorschlaege(w)
    neu = []

    def ablegen(regel, titel, bereich, beobachtung, quellen, begruendung, nutzen, unsicherheit, risiken, prioritaet, erklaerung="", empfehlung="", pruefung=None):
        vid = "lv-" + digest(regel, json.dumps(sorted((q["vorgang"], q.get("ereignis", "")) for q in quellen)), vorschlag_quellen_hash(w, quellen))[:10]  # a changed source gives a new proposal
        if vid in daten["vorschlaege"]:
            return
        daten["vorschlaege"][vid] = {"id": vid, "regel": regel, "titel": titel, "beschreibung": beobachtung, "bereich": bereich, "beobachtung": beobachtung,
                                     "quellen": quellen, "begruendung": begruendung, "erwarteter_nutzen": nutzen, "unsicherheit": unsicherheit,
                                     "risiken": risiken, "prioritaet": prioritaet, "status": "erstellt", "erstellt": stamp(now), "aendert_stammdaten": False,
                                     "quellen_hash": vorschlag_quellen_hash(w, quellen), "entscheidungen": [], "erklaerung": erklaerung or begruendung,
                                     "empfehlung": empfehlung or begruendung, "pruefung": pruefung() if callable(pruefung) else pruefung}
        neu.append(vid)

    themen = {}
    for d in gruppe:
        for e in d["ereignisse"]:
            i = e.get("interpretation")
            if e["art"].startswith("absage") and i and i.get("grund_genannt"):
                themen.setdefault(i.get("thema") or i["kategorie"], []).append({"vorgang": d["slug"], "ereignis": e["id"]})
    for thema, quellen in sorted(themen.items()):
        if len({q["vorgang"] for q in quellen}) >= 2:
            ablegen(f"thema:{thema}", f"Anforderung „{thema}“ in der Stellenprüfung genauer prüfen", "stellenbewertung",
                    f"In {len({q['vorgang'] for q in quellen})} Absagen wurde „{thema}“ als Grund genannt.", quellen,
                    "Eine Häufung genannter Gründe ist ein Hinweis, die Passung zu dieser Anforderung vor der nächsten Bewerbung genauer zu prüfen.",
                    "Bewerbungen auf Stellen mit dieser Anforderung werden bewusster ausgewählt oder vorbereitet.",
                    "mittel bis hoch: die Zuordnung der Kategorie ist ein Muster im Wortlaut; die Zahl der Fälle ist klein; kein Beleg für eine Ursache",
                    "Überinterpretation weniger Absagen; auf keinen Fall eine Qualifikation in die Datengrundlage übernehmen, die nicht belegt ist", "mittel")
    def messen(name):
        zaehler, nenner = aktueller_wert(w, now, name, reife)
        return {"kennzahl": name, "reife": reife, "ausgangswert": {"zaehler": zaehler, "nenner": nenner, "am": heute_datum}}
    nicht_fertig = [{"vorgang": d["slug"]} for d in alle if not d["fertig"] and d["erfasst"] and tage(d["erfasst"], heute_datum) >= reife]
    if nicht_fertig:
        ablegen("prozess:nicht_fertig", "Begonnene Bewerbungen abschließen oder bewusst beenden", "prozess",
                f"{len(nicht_fertig)} Bewerbungen sind seit mindestens {reife} Tagen begonnen und ohne fertige Unterlagen.", nicht_fertig,
                "Begonnene Bewerbungen, die liegen bleiben, binden Aufmerksamkeit und verzerren den Überblick.", "ein klarerer Bestand: fertig oder bewusst beendet",
                f"mittel: ob die Bewerbungen liegen bleiben, weil die Stelle nicht passt, die Zeit fehlt oder der Status nicht gepflegt ist, zeigen die Daten nicht; {reife} Tage sind eine Berichtskonvention",
                "ein vorschnelles Beenden einer Bewerbung, die noch gewollt ist", "mittel",
                erklaerung="Mögliche Gründe: die Stelle passt doch nicht, die Zeit fehlt, der Status wurde nicht nachgezogen. Das lässt sich aus den Daten nicht unterscheiden.",
                empfehlung="Jede Bewerbung einzeln ansehen: fertigstellen, mit `bewerbung.py statuswechsel` beenden oder den Status nachtragen.",
                pruefung=lambda: {**messen("begonnen_zu_fertig"), "wie": f"`lernen.py vorschlag pruefe <id>` vergleicht die Quote begonnen → fertig (mindestens {reife} Tage alt) mit dem Ausgangswert"})
    nicht_gesendet = [{"vorgang": d["slug"]} for d in alle if d["fertig"] and not d["versendet_am"] and d.get("fertig_am") and tage(d["fertig_am"], heute_datum) >= reife]
    if nicht_gesendet:
        ablegen("prozess:nicht_eingereicht", "Fertige Bewerbungen einreichen oder verwerfen", "prozess",
                f"{len(nicht_gesendet)} Bewerbungen haben seit mindestens {reife} Tagen fertige Unterlagen und sind nicht eingereicht.", nicht_gesendet,
                "Fertige Unterlagen veralten, und die Stelle kann besetzt sein.", "weniger veraltete Entwürfe",
                "mittel: der Grund (Zweifel, Zeit, vergessene Eintragung von `versendet_am`) steht nicht in den Daten", "eine überstürzte Einreichung ohne erneute Prüfung",
                "mittel", empfehlung="Prüfen, ob die Stelle noch offen ist und ob der Versand nur nicht eingetragen wurde (`versendet_am` gehört der Nutzerin oder dem Nutzer).",
                pruefung=lambda: {**messen("fertig_zu_eingereicht"), "wie": "`lernen.py vorschlag pruefe <id>` vergleicht die Quote fertig → eingereicht mit dem Ausgangswert"})
    veto = [{"vorgang": d["slug"]} for d in alle if d["bewertung"] == "Veto"]
    if len(veto) >= 2:
        ablegen("passung:veto_begonnen", "Passungsprüfung vor dem Bewerbungsbeginn ernster nehmen", "stellenauswahl",
                f"{len(veto)} Vorgänge wurden trotz Ergebnis „Veto“ der Passungsprüfung begonnen.", veto,
                "Ein Veto nennt einen Ausschlussgrund des eigenen Wunschprofils.", "weniger Aufwand für Stellen, die das eigene Profil ausschließt",
                "mittel: ein Veto kann bewusst übergangen worden sein", "eine zu enge Auswahl, wenn das Wunschprofil nicht mehr stimmt", "mittel",
                erklaerung="Möglich: das Wunschprofil ist veraltet, oder die Stelle wurde bewusst trotzdem gewählt.",
                empfehlung="Entscheiden, ob das Wunschprofil angepasst werden soll (`job-application-traumjob-interview`) oder Stellen mit Veto nicht mehr begonnen werden.",
                pruefung=lambda: {**messen("begonnen_trotz_veto"), "wie": "Die Zahl der Vorgänge mit Veto unter allen begonnenen wird später erneut gezählt"})
    for check, slugs in qualitaetsbefunde(w, alle).items():
        if len(slugs) >= 2:
            ablegen(f"qualitaet:{check}", f"Wiederkehrenden Befund der Qualitätsprüfung {check} beheben", "dokumentqualitaet",
                    f"Die Prüfung {check} schlug in {len(slugs)} Vorgängen fehl oder blockierte.", [{"vorgang": s} for s in slugs],
                    "Ein Befund, der in mehreren Vorgängen wiederkehrt, deutet auf eine Gewohnheit oder eine Vorlage hin.", "weniger Nacharbeit vor dem Versand",
                    "gering bis mittel: die Ursache im einzelnen Vorgang kann verschieden sein", "keines", "mittel",
                    empfehlung=f"Den Befund {check} in einem der Vorgänge ansehen (`task quality -- status <vorgang>`) und die Ursache an der Vorlage oder der Grundlage beheben; die Grundlage ändert nur die Nutzerin oder der Nutzer.",
                    pruefung=lambda: {**messen(f"qualitaet_fehler:{check}"), "wie": "Die Zahl der Vorgänge mit diesem Befund wird später erneut gezählt"})
    nur_status = [{"vorgang": d["slug"]} for d in gruppe if d["nur_status"]]
    if nur_status:
        ablegen("daten:ergebnis_nur_status", "Ergebnisse mit Ereignis und Datum belegen", "datenqualitaet",
                f"{len(nur_status)} Ergebnisse stehen nur im Status, ohne bestätigtes Ereignis.", nur_status,
                "Ohne Ereignis fehlen Datum und Beleg; Zeiten lassen sich nicht berechnen.", "Zeitkennzahlen und Belege werden möglich", "gering: es geht um fehlende Angaben",
                "Aufwand beim Nachtragen", "niedrig", empfehlung="Das Datum nachtragen (`bewerbung.py ereignis erfassen … --eingetreten-am JJJJ-MM-TT`), nur wenn es bekannt ist.",
                pruefung=lambda: {**messen("ergebnis_nur_durch_status"), "wie": "Die Zahl der Ergebnisse nur aus Status wird später erneut gezählt"})
    ohne_version = [{"vorgang": d["slug"]} for d in gruppe if not d["dokumente"]["eindeutig"]]
    if ohne_version:
        ablegen("dokumentversion", "Dokumentversionen der versendeten Bewerbungen nachweisbar machen", "datenqualitaet",
                f"{len(ohne_version)} versendete Bewerbungen haben keine eindeutige Dokumentversion.", ohne_version,
                "Ohne Version lässt sich ein Ergebnis keiner Fassung der Unterlagen zuordnen; Vergleiche zwischen Fassungen sind dann nicht möglich.",
                "Auswertungen nach Dokumentversion werden möglich.", "gering: es geht um fehlende Angaben, nicht um eine Deutung",
                "Aufwand beim Eintragen von `anhaenge` und beim Ausführen von `task quality`", "niedrig",
                pruefung=lambda: {**messen("dokumentversion_nicht_eindeutig"), "wie": "Die Zahl der Bewerbungen ohne eindeutige Dokumentversion wird später erneut gezählt"})
    offene = km.offene_vorschlaege(w)
    if offene:
        ablegen("nachrichten:" + digest(*sorted(n["id"] for n in offene))[:8], "Ungeprüfte Rückmeldungen im Eingang prüfen", "nachverfolgung",
                f"{len(offene)} Nachrichten warten auf die Prüfung.", [{"vorgang": n["vorgang"]} for n in offene if n["vorgang"]] or [{"vorgang": "-"}],
                "Solange Rückmeldungen nicht bestätigt sind, fließen sie nicht in die Auswertung ein.", "vollständigere Statistik", "gering", "keines", "hoch",
                pruefung=lambda: {**messen("nachrichten_noch_nicht_geprueft"), "wie": "Die Zahl der ungeprüften Nachrichten wird später erneut gezählt"})
    nachfass_tage = ss.read_frontmatter(konfiguration).get("nachfass_tage", "") if konfiguration and os.path.isfile(konfiguration) else ""
    if nachfass_tage.isdigit():
        heute_datum = km.heute(now)
        faellig = [{"vorgang": d["slug"]} for d in gruppe if d["status"] == "versendet" and "rueckmeldung" not in d["flags"]
                   and (dt.date.fromisoformat(heute_datum) - dt.date.fromisoformat(d["versendet_am"])).days >= int(nachfass_tage)]
        if faellig:
            ablegen("nachfassen:" + digest(*sorted(q["vorgang"] for q in faellig))[:8], "Nachfassen bei Bewerbungen ohne Rückmeldung prüfen", "nachverfolgung",
                    f"{len(faellig)} Bewerbungen sind seit mindestens {nachfass_tage} Tagen (nachfass_tage) ohne Rückmeldung.", faellig,
                    "Die Frist hat die Nutzerin oder der Nutzer festgelegt; nach ihr ist ein Nachfassen vorgesehen.", "weniger Bewerbungen bleiben unbeantwortet",
                    "mittel: ob nachgefasst wird, entscheidet jede Bewerbung einzeln", "eine Nachfass-Mail ist Arbeitgeberkommunikation und braucht die Freigabe", "mittel")
    veraltet = markiere_veraltet(w, daten, now)
    atomic_write(vorschlaege_pfad(w), daten)
    return {"ok": True, "neu": neu, "veraltet": veraltet, "hinweis": "Ein Vorschlag ändert nichts. Erst vorlegen, dann entscheiden."}


def markiere_veraltet(w, daten, now):
    """A proposal is stale when a source changed or vanished, or a source Vorgang has reached its deletion date (S10)."""
    gewaehlt, faellig = [], loeschfaellig(w, now)
    for v in daten["vorschlaege"].values():
        if v["status"] in ("umgesetzt", "abgelehnt", "veraltet"):
            continue
        if vorschlag_quellen_hash(w, v["quellen"]) != v["quellen_hash"] or any(q["vorgang"] in faellig for q in v["quellen"]):
            v["status"] = "veraltet"
            v["entscheidungen"].append({"am": "automatisch", "entscheidung": "veraltet", "grund": "eine Quelle hat sich geändert, ist nicht mehr vorhanden oder hat ihr Löschdatum erreicht"})
            gewaehlt.append(v["id"])
    return gewaehlt


def loeschfaellig(w, now):
    heute_datum = km.heute(now)
    return {slug for slug, meta in km.alle_vorgaenge(w).items() if ss.valid_date(meta.get("loeschen_ab", "")) and meta["loeschen_ab"] <= heute_datum}


def vorschlag_ansicht(v):
    return {**{k: v[k] for k in ("id", "regel", "titel", "beschreibung", "bereich", "beobachtung", "quellen", "begruendung", "erwarteter_nutzen", "unsicherheit",
                                  "risiken", "prioritaet", "status", "entscheidungen", "aendert_stammdaten")},
            **{k: v.get(k) for k in ("erklaerung", "empfehlung", "pruefung")},
            "auswirkung": "Die Annahme ändert keine Datei. Persönliche Stammdaten, Qualifikationen und Dokumente ändert nur die Nutzerin oder der Nutzer selbst.",
            "naechster_schritt": {"erstellt": "vorlegen", "zur_pruefung": "entscheiden (--ja)", "zurueckgestellt": "vorlegen", "angenommen": "umsetzen und `umgesetzt` melden"}.get(v["status"], "keiner")}


def wirksamkeit(w, now, vid, reife=REIFE_TAGE_STANDARD):
    """Compare the measure of an accepted proposal with the value when it was made. A description of the data, not a proof of an effect (EA-21)."""
    v = lade_vorschlaege(w)["vorschlaege"].get(vid)
    if v is None:
        raise Refused("vorschlag_unbekannt", f"Kein Vorschlag {redact(vid, 40)}")
    if v["status"] not in ("angenommen", "umgesetzt"):
        raise Refused("nicht_angenommen", f"Die Wirkung eines Vorschlags wird erst nach der Annahme geprüft (Status: {v['status']})")
    pruefung = v.get("pruefung")
    if not pruefung:
        return {"ok": True, "vorschlag": vid, "pruefbar": False, "hinweis": "Dieser Vorschlag hat keine Kennzahl; die Nutzerin oder der Nutzer beurteilt die Wirkung selbst."}
    reife = pruefung.get("reife", reife)  # measured the way the baseline was
    zaehler, nenner = aktueller_wert(w, now, pruefung["kennzahl"], reife)
    vorher = pruefung["ausgangswert"]
    neu_n = nenner - vorher["nenner"]
    vor, jetzt = wilson(vorher["zaehler"], vorher["nenner"]), wilson(zaehler, nenner)
    ueberlappt = bool(vor and jetzt and not (jetzt[1] < vor[0] or vor[1] < jetzt[0]))
    if neu_n < MIN_N:
        aussage = f"Die Daten reichen noch nicht für eine Aussage: seit dem Vorschlag kamen nur {max(neu_n, 0)} Fälle dazu (mindestens {MIN_N}). Weitere Bewerbungen wären nötig."
    elif ueberlappt:
        aussage = "Die beobachtete Änderung liegt innerhalb der Unsicherheit; die Daten zeigen keinen belastbaren Unterschied."
    else:
        aussage = "In den bisher erfassten Daten zeigt sich ein Unterschied zum Ausgangswert. Das ist eine Beobachtung und kein Beleg, dass die Umsetzung ihn bewirkt hat."
    return {"ok": True, "vorschlag": vid, "pruefbar": True, "kennzahl": pruefung["kennzahl"], "reife_tage": reife, "ausgangswert": vorher, "aktuell": {"zaehler": zaehler, "nenner": nenner},
            "neue_faelle": neu_n, "konfidenz95_vorher": vor, "konfidenz95_jetzt": jetzt, "aussage": aussage}


def vorschlag_entscheiden(w, daten, vid, entscheidung, grund, now):
    v = daten["vorschlaege"].get(vid)
    if v is None:
        raise Refused("vorschlag_unbekannt", f"Kein Vorschlag {redact(vid, 40)}")
    if entscheidung not in VORSCHLAG_STATUS or entscheidung not in UEBERGANG.get(v["status"], ()):
        raise Refused("uebergang_nicht_erlaubt", f"Von `{v['status']}` geht es nur nach: {', '.join(UEBERGANG.get(v['status'], ())) or 'nirgends mehr'}")
    if not grund.strip():
        raise Refused("grund_fehlt", "--grund fehlt")
    if vorschlag_quellen_hash(w, v["quellen"]) != v["quellen_hash"]:
        raise Refused("vorschlag_veraltet", "Eine Quelle des Vorschlags hat sich geändert: er ist veraltet und wird neu erzeugt (`vorschlaege erzeugen`)")
    v["status"] = entscheidung
    v["entscheidungen"].append({"am": stamp(now), "von": "nutzer", "entscheidung": entscheidung, "grund": clean_text(grund, 200)})
    return {"ok": True, "vorschlag": vid, "status": entscheidung, "hinweis": "Es wurde nichts geändert außer diesem Status."}


# ---------------------------------------------------------------- CLI

USER_ONLY = (("ergebnis", ("erfassen", "korrigieren", "verwerfen")), ("vorschlag", ("entscheiden",)))


def filter_aus(args):
    return {k: getattr(args, k, None) for k in FILTER}


def build_parser():
    p = argparse.ArgumentParser(description="Learning from confirmed application results (A-06).")
    p.add_argument("--konfiguration", default=os.path.join(ss.DEFAULT_WURZEL, "konfiguration.md"))
    p.add_argument("--jetzt")
    sub = p.add_subparsers(dest="befehl", required=True)

    def filter_args(s):
        s.add_argument("--von")
        s.add_argument("--bis")
        s.add_argument("--status")
        s.add_argument("--arbeitgeber")
        s.add_argument("--stellenprofil")
        s.add_argument("--ausrichtung")
        s.add_argument("--kanal")
        s.add_argument("--quelle")
        s.add_argument("--bewertung")
        s.add_argument("--dokumentversion")
        s.add_argument("--titel")
        s.add_argument("--ergebnis", choices=ERGEBNIS_WERTE)
        s.add_argument("--reife-tage", type=int, default=REIFE_TAGE_STANDARD)

    e = sub.add_parser("ergebnis")
    e.add_argument("aktion", choices=("erfassen", "korrigieren", "verwerfen", "liste"))
    e.add_argument("vorgang")
    e.add_argument("--id")
    e.add_argument("--art")
    e.add_argument("--datum")
    e.add_argument("--original", default="")
    e.add_argument("--kategorie")
    e.add_argument("--thema", default="")
    e.add_argument("--aussage", default="")
    e.add_argument("--nachricht", default="")
    e.add_argument("--grund", default="")
    e.add_argument("--ja", action="store_true")
    s = sub.add_parser("statistik")
    filter_args(s)
    s.add_argument("--nach", choices=SEGMENTE)
    s.add_argument("--belege", action="store_true", help="name the Vorgänge behind every numerator and denominator")
    ex = sub.add_parser("erklaere")
    filter_args(ex)
    ex.add_argument("kennzahl")
    r = sub.add_parser("retrospektive")
    filter_args(r)
    a = sub.add_parser("aktualitaet")
    a.add_argument("datei")
    vs = sub.add_parser("vorschlaege")
    vs.add_argument("aktion", choices=("erzeugen", "liste"))
    vs.add_argument("--status", choices=VORSCHLAG_STATUS)
    v = sub.add_parser("vorschlag")
    v.add_argument("aktion", choices=("zeige", "vorlegen", "entscheiden", "pruefe"))
    v.add_argument("--reife-tage", type=int, default=REIFE_TAGE_STANDARD)
    v.add_argument("id")
    v.add_argument("--entscheidung", choices=("angenommen", "abgelehnt", "zurueckgestellt", "umgesetzt"))
    v.add_argument("--grund", default="")
    v.add_argument("--ja", action="store_true")
    return p


def run(args):
    now = parse_time(args.jetzt) if args.jetzt else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    w = ss.find_wurzel(args.konfiguration)
    befehl = args.befehl
    aktion = getattr(args, "aktion", None)
    if any(befehl == b and aktion in a for b, a in USER_ONLY):
        km.schutz_nutzer(f"{befehl} {aktion}")
        if not args.ja:
            raise Refused("freigabe_fehlt", "Das ist eine Entscheidung der Nutzerin oder des Nutzers und braucht ihr ausdrückliches Ja (--ja)")
    for name in ("von", "bis"):
        if getattr(args, name, None) and ss.valid_date(getattr(args, name)) != getattr(args, name):
            raise Refused("datum_ungueltig", f"--{name} ist ein echtes Datum der Form JJJJ-MM-TT")
    if befehl == "statistik":
        return statistik(w, now, args.von, args.bis, args.nach, filter_aus(args), reife=args.reife_tage, belege=args.belege)
    if befehl == "erklaere":
        stat = statistik(w, now, args.von, args.bis, None, filter_aus(args), reife=args.reife_tage, belege=True)
        treffer = [c for c in stat["konversionen"] if c["name"] == args.kennzahl]
        if not treffer:
            raise Refused("kennzahl_unbekannt", f"Die Kennzahl {redact(args.kennzahl, 50)} gibt es nicht ({', '.join(c['name'] for c in stat['konversionen'])})")
        return {"ok": True, "kennzahl": treffer[0], "zeitraum": stat["zeitraum"], "filter": stat["filter"], "quellen_hash": stat["quellen_hash"],
                "ausgeschlossen": {"eingereicht": stat["datenqualitaet"]["ausgeschlossen"], "begonnen": stat["population"]["ausgeschlossen_begonnen"]}}
    if befehl == "vorschlag" and aktion == "pruefe":
        return wirksamkeit(w, now, args.id, args.reife_tage)
    if befehl == "aktualitaet":
        return aktualitaet(w, now, args.datei)
    if befehl == "ergebnis" and aktion == "liste":
        return {"ok": True, "ereignisse": km.lade_nachverfolgung(w, args.vorgang)["ereignisse"] if km.vorgang_meta(w, args.vorgang) is not None else []}
    if befehl == "vorschlaege" and aktion == "liste":
        daten = lade_vorschlaege(w)
        return {"ok": True, "vorschlaege": [vorschlag_ansicht(v) for v in daten["vorschlaege"].values() if not args.status or v["status"] == args.status]}
    if befehl == "vorschlag" and aktion == "zeige":
        v = lade_vorschlaege(w)["vorschlaege"].get(args.id)
        if v is None:
            raise Refused("vorschlag_unbekannt", f"Kein Vorschlag {redact(args.id, 40)}")
        return {"ok": True, "vorschlag": vorschlag_ansicht(v), "quellen_aktuell": vorschlag_quellen_hash(w, v["quellen"]) == v["quellen_hash"]}
    with ss.exclusive(w, *LOCK):
        if befehl == "retrospektive":
            return retrospektive(w, now, args.von, args.bis, filter_aus(args), args.konfiguration, args.reife_tage)
        if befehl == "ergebnis":
            if aktion == "erfassen":
                return ergebnis_erfassen(w, args.vorgang, args.art or "", args.datum or "", args.original,
                                         {"kategorie": args.kategorie, "thema": args.thema, "aussage": args.aussage, "nachricht": args.nachricht}, now)
            return ergebnis_aendern(w, args.vorgang, args.id or "", aktion, {"art": args.art, "datum": args.datum, "grund": args.grund}, now)
        if befehl == "vorschlaege":
            return erzeuge_vorschlaege(w, now, args.konfiguration, getattr(args, "reife_tage", REIFE_TAGE_STANDARD))
        daten = lade_vorschlaege(w)
        if aktion == "vorlegen":
            v = daten["vorschlaege"].get(args.id)
            if v is None or v["status"] not in ("erstellt", "zurueckgestellt"):
                raise Refused("uebergang_nicht_erlaubt", "Nur ein erstellter oder zurückgestellter Vorschlag wird vorgelegt")
            v["status"] = "zur_pruefung"
            atomic_write(vorschlaege_pfad(w), daten)
            return {"ok": True, "vorschlag": vorschlag_ansicht(v)}
        if not args.entscheidung:
            raise Refused("entscheidung_fehlt", "--entscheidung fehlt")
        if markiere_veraltet(w, daten, now):  # a source changed since the proposal was made: it is stale and decided no more
            atomic_write(vorschlaege_pfad(w), daten)
        ergebnis = vorschlag_entscheiden(w, daten, args.id, args.entscheidung, args.grund, now)
        atomic_write(vorschlaege_pfad(w), daten)
        return ergebnis


def main(argv):
    args = build_parser().parse_args(argv[1:])
    try:
        result = run(args)
    except Blocker as error:
        print(f"Blocker: {error}", file=sys.stderr)
        return 1
    except Refused as error:
        print(json.dumps({"ok": False, "code": error.code, "meldung": error.meldung}, ensure_ascii=False))
        return 3
    print(json.dumps(result, ensure_ascii=False, indent=2, default=list))
    return 2 if result.get("ok") is False else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
