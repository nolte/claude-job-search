#!/usr/bin/env python3
"""Learning from confirmed application results: statistics, retrospective and proposals (spec ergebnisauswertung EA-1 to EA-14, A-06).

Reads what is already in the Wurzel: `vorgang.md` (status, `versendet_am`, `## Verlauf`), the confirmed events in
`<vorgang>/nachverfolgung.json` (written by `kommunikation.py`, or by `ergebnis erfassen` here on the user's statement)
and, for the versions of the documents, `qualitaet.json`. It keeps no second record of the results: statistics and the
retrospective are derivations, marked as such and bound to a hash of their sources, so a changed source makes them stale.

What it never does: change a Vorgang status, a document, the Datengrundlage or `profil.md`; send anything; call a model; say why
an application succeeded or failed. A refusal without a stated reason is "Grund unbekannt", never a weakness of the person or of the
documents. A proposal changes nothing when it is accepted; the user carries it out and says so (`umgesetzt`).

State: `<wurzel>/lernen/vorschlaege.json` (proposals), `<wurzel>/lernen/retrospektive-*.md` (derivations).

Usage: lernen.py [--konfiguration PFAD] [--jetzt ISO] <befehl> ...
Commands: ergebnis (erfassen|korrigieren|verwerfen|liste), statistik, retrospektive, aktualitaet, vorschlaege (erzeugen|liste),
vorschlag (zeige|vorlegen|entscheiden). Output is one JSON object. Exit code 0 ok, 2 ok=false, 3 refused, 1 blocker. Standard library only.
"""

import argparse
import datetime as dt
import json
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
    "abgelehnt": {"rueckmeldung", "einladung", "gespraech", "angebot"}, "zurückgezogen": set(), "ohne Antwort": {"ohne_antwort"}, "abgeschlossen": set(),
}
ART_FLAGS = {"gespraechseinladung": {"einladung"}, "gespraech": {"einladung", "gespraech"}, "technisches_gespraech": {"einladung", "gespraech"},
             "assessment": {"einladung", "gespraech"}, "weitere_phase": {"einladung", "gespraech", "weitere_phase"}, "angebot": {"angebot"},
             "einstellung": {"angebot", "einstellung"}, "absage": {"absage"}, "absage_nach_unterlagen": {"absage"},
             "absage_nach_gespraech": {"absage"}, "absage_nach_assessment": {"absage"}, "zurueckgezogen": set()}
SEGMENTE = ("arbeitgeber", "zeitraum", "kanal", "quelle", "ausrichtung", "stellenprofil", "dokumentversion", "bewertung")
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
        text = open(pfad, encoding="utf-8", errors="replace").read()
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
    daten = {"slug": slug, "firma": meta.get("firma", ""), "stelle": meta.get("stelle", ""), "status": status, "versendet_am": versendet,
             "flags": flags, "nur_status": nur_status, "kanal": meta.get("weg") or meta.get("bewerbungsweg", "") or "unbekannt",
             "quelle": host or "unbekannt", "ausrichtung": meta.get("ausrichtung", "") or "unbekannt",
             "stellenprofil": meta.get("profil", "") or next((t.split(":", 1)[1] for t in re.findall(r"profil:[\w-]+", meta.get("tags", ""))), "") or "unbekannt",
             "ereignisse": bestaetigt, "unbestaetigt": [e for e in nv["ereignisse"] if e.get("status") in ("erkannt", "zur_pruefung")],
             "loeschen_ab": ss.valid_date(meta.get("loeschen_ab", "")), "ereignisdatei_defekt": bool(nv.get("defekt"))}
    daten["abgeschlossen"] = status in km.ENDSTATUS
    daten["offen"] = not daten["abgeschlossen"]
    return daten


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
        if filter_.get("status") and d["status"] != filter_["status"]:
            ausgeschlossen["anderer_status"] += 1
            continue
        if filter_.get("arbeitgeber") and ss.norm(d["firma"]) != ss.norm(filter_["arbeitgeber"]):
            ausgeschlossen["anderer_arbeitgeber"] += 1
            continue
        if filter_.get("stellenprofil") and d["stellenprofil"] != filter_["stellenprofil"]:
            ausgeschlossen["anderes_stellenprofil"] += 1
            continue
        if filter_.get("ausrichtung") and d["ausrichtung"] != filter_["ausrichtung"]:
            ausgeschlossen["andere_ausrichtung"] += 1
            continue
        d["dokumente"] = dokument_stand(w, slug)
        d["bewertung"] = bewertung_von(w, slug)
        gewaehlt.append(d)
    return gewaehlt, dict(ausgeschlossen)


# ---------------------------------------------------------------- statistics (EA-5 to EA-8)

def quote(zaehler, nenner):
    wert = round(zaehler / nenner, 3) if nenner else None
    return {"zaehler": zaehler, "nenner": nenner, "quote": wert, "eingeschraenkt": nenner < MIN_N,
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


def quellen_hash(w, gruppe):
    teile = []
    for d in sorted(gruppe, key=lambda x: x["slug"]):
        for name in ("vorgang.md", "nachverfolgung.json"):
            pfad = os.path.join(w, d["slug"], name)
            teile.append(f"{d['slug']}/{name}={sha256_file(pfad) if os.path.isfile(pfad) else '-'}")
    return digest(*teile)


def statistik(w, now, von=None, bis=None, nach=None, filter_=None, gewaehlt=None):
    gruppe, ausgeschlossen = gewaehlt or waehle(w, now, von, bis, filter_)
    ergebnis = {"ok": True, "erstellt": stamp(now), "zeitraum": {"von": von, "bis": bis}, "filter": {k: v for k, v in (filter_ or {}).items() if v},
                "ausgewertet": len(gruppe), "quellen_hash": quellen_hash(w, gruppe), "abgeleitet": True,
                **kennzahlen(gruppe), "datenqualitaet": datenqualitaet(w, gruppe, ausgeschlossen), "grenzen": list(GRENZEN)}
    if nach:
        if nach not in SEGMENTE:
            raise Refused("segment_unbekannt", f"Segment {redact(nach, 40)} ist nicht bekannt ({', '.join(SEGMENTE)})")
        gruppen = {}
        for d in gruppe:
            gruppen.setdefault(schluessel_von(d, nach), []).append(d)
        ergebnis["segmente"] = {"nach": nach, "gruppen": {k: {"bewerbungen": len(v), "rueckmeldung": quote(sum(1 for d in v if "rueckmeldung" in d["flags"]), len(v)),
                                                              "einladung": quote(sum(1 for d in v if "einladung" in d["flags"]), len(v)),
                                                              "vergleichbar": len(v) >= MIN_N} for k, v in sorted(gruppen.items())},
                                "hinweis": "Gruppen sind nur vergleichbar, wenn sie ähnliche Stellen, Seniorität und Zeiträume haben; das prüft die Nutzerin oder der Nutzer."}
    return ergebnis


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
        e["status"] = "korrigiert"
    e.setdefault("korrekturen", []).append({"am": stamp(now), "vorher": vorher, "grund": clean_text(felder.get("grund", ""), 160)})
    km.speichere_nachverfolgung(w, slug, nv)
    return {"ok": True, "ereignis": ereignis_id, "status": e["status"]}


# ---------------------------------------------------------------- retrospective (EA-9)

def retrospektive(w, now, von, bis, filter_):
    gewaehlt = waehle(w, now, von, bis, filter_)  # read once: the figures and the lists come from the same Vorgänge
    stat = statistik(w, now, von, bis, None, filter_, gewaehlt)
    gruppe = gewaehlt[0]
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
    gruppen = Counter((d["ausrichtung"], d["stellenprofil"]) for d in gruppe)
    k, z = stat["zaehler"], stat
    zeilen = [
        "---", "abgeleitet: ja", f"erstellt: {stamp(now)}", f"zeitraum_von: {von or ''}", f"zeitraum_bis: {bis or ''}",
        f"quellen_hash: {stat['quellen_hash']}", f"ausgewertet: {stat['ausgewertet']}", "---", "",
        "# Retrospektive der Bewerbungen", "",
        "Abgeleitete Auswertung: Quelle der Wahrheit bleiben `vorgang.md` und `nachverfolgung.json` der Vorgänge. Ändert sich eine Quelle, ist diese Datei veraltet (`lernen.py aktualitaet`).", "",
        "## Datenbasis", "",
        f"- Zeitraum (nach Versanddatum): {von or 'offen'} bis {bis or 'offen'}", f"- Ausgewertete Vorgänge: {stat['ausgewertet']}",
        f"- Offene Vorgänge: {k['offen']}", f"- Abgeschlossene Vorgänge: {k['abgeschlossen']}",
        f"- Vorgänge ohne bestätigtes Ereignis (Ergebnis nur aus `status`): {stat['datenqualitaet']['ergebnis_nur_durch_status']}",
        f"- Ereignisse zur Prüfung (nicht ausgewertet): {stat['datenqualitaet']['ereignisse_zur_pruefung']}",
        f"- Ungeprüfte Nachrichten im Eingang: {stat['datenqualitaet']['nachrichten_noch_nicht_geprueft']}",
        f"- Ausgeschlossen: {', '.join(f'{a} ({n})' for a, n in sorted(stat['datenqualitaet']['ausgeschlossen'].items())) or 'keine'}",
        f"- Kriterien: {json.dumps(stat['filter'], ensure_ascii=False) if stat['filter'] else 'keine Filter'}", "",
        "## Was passiert ist", "",
        f"- Versendet: {k['bewerbungen']}", f"- Inhaltliche Rückmeldung: {k['rueckmeldung']} (Quote {fmt(z['ruecklaufquote'])})",
        f"- Einladungen: {k['einladung']}", f"- Gespräche: {k['gespraech']}", f"- Angebote: {k['angebot']}", f"- Einstellungen: {k['einstellung']}",
        f"- Absagen: {k['absage']}", f"- Ohne Rückmeldung, noch offen: {k['offen_ohne_rueckmeldung']}", "",
        "## Absagen und genannte Gründe", ""]
    if absagen:
        for slug, e in sorted(absagen, key=lambda x: x[1].get("datum") or ""):
            i = e.get("interpretation") or {}
            zeilen.append(f"- {slug} ({e.get('datum') or 'Datum unbekannt'}): " + (f"Grund genannt, Kategorie {i['bezeichnung']} ({'vom Nutzer bestätigt' if e['status'] == 'korrigiert' else 'Muster im Wortlaut, nicht bestätigt'}); Wortlaut: „{e['original']}“"
                                                                                   if i.get("grund_genannt") else "kein Grund genannt: Grund unbekannt"))
    else:
        zeilen.append("- Keine bestätigte Absage im Zeitraum.")
    zeilen += ["", "## Wiederholt angesprochene Themen", ""]
    zeilen += [f"- {t}: in {len(v)} Vorgängen genannt ({', '.join(v)}). Das ist eine Häufung der Aussagen, keine Ursache." for t, v in sorted(wiederholt.items())] or \
              ["- Kein Thema wurde in mindestens zwei Vorgängen genannt."]
    zeilen += ["", "## Vergleichbarkeit", "", "Vorgänge nach Ausrichtung und Stellenprofil. Gruppen mit unterschiedlichen Stellen, Seniorität, Arbeitgebern oder Zeiträumen sind nicht ohne Prüfung vergleichbar.", ""]
    zeilen += [f"- {a} / {p}: {n} Vorgänge" + (" (zu wenig für eine Quote)" if n < MIN_N else "") for (a, p), n in sorted(gruppen.items())] or ["- keine"]
    zeilen += ["", "## Einschränkungen", ""] + [f"- {g}" for g in GRENZEN]
    zeilen += ["", "## Verbesserungsvorschläge", "", "Siehe `lernen.py vorschlaege liste`; jeder Vorschlag nennt Quellen, Begründung und Unsicherheit und wartet auf die Entscheidung der Nutzerin oder des Nutzers.", ""]
    ordner = os.path.join(w, "lernen")
    kriterien = json.dumps([von, bis, sorted((k, v) for k, v in (filter_ or {}).items() if v)])
    name = f"retrospektive-{km.heute(now)}" + (f"-{digest(kriterien)[:6]}" if von or bis or any((filter_ or {}).values()) else "") + ".md"
    pfad = os.path.join(ordner, name)  # other criteria on the same day give another file; the same criteria replace the earlier one
    os.makedirs(ordner, exist_ok=True)
    temp = pfad + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(zeilen))
    os.replace(temp, pfad)
    return {"ok": True, "datei": f"lernen/{name}", "ausgewertet": stat["ausgewertet"], "quellen_hash": stat["quellen_hash"], "wiederholte_themen": sorted(wiederholt)}


def fmt(q):
    return f"{q['zaehler']} von {q['nenner']}" + (" – eingeschränkt" if q["eingeschraenkt"] else "")


def aktualitaet(w, now, datei):
    pfad = os.path.join(w, datei)
    if not os.path.isfile(pfad):
        raise Refused("datei_fehlt", f"{redact(datei, 80)} gibt es nicht")
    meta = ss.read_frontmatter(pfad)
    von, bis = meta.get("zeitraum_von") or None, meta.get("zeitraum_bis") or None
    gruppe, _ = waehle(w, now, von, bis, None)
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


def erzeuge_vorschlaege(w, now, konfiguration):
    """Proposals from fixed rules over confirmed results. A rule that needs a deadline the user did not set does not run."""
    gruppe, _ = waehle(w, now)
    daten = lade_vorschlaege(w)
    neu = []

    def ablegen(regel, titel, bereich, beobachtung, quellen, begruendung, nutzen, unsicherheit, risiken, prioritaet):
        vid = "lv-" + digest(regel, json.dumps(sorted((q["vorgang"], q.get("ereignis", "")) for q in quellen)), vorschlag_quellen_hash(w, quellen))[:10]  # a changed source gives a new proposal
        if vid in daten["vorschlaege"]:
            return
        daten["vorschlaege"][vid] = {"id": vid, "regel": regel, "titel": titel, "beschreibung": beobachtung, "bereich": bereich, "beobachtung": beobachtung,
                                     "quellen": quellen, "begruendung": begruendung, "erwarteter_nutzen": nutzen, "unsicherheit": unsicherheit,
                                     "risiken": risiken, "prioritaet": prioritaet, "status": "erstellt", "erstellt": stamp(now), "aendert_stammdaten": False,
                                     "quellen_hash": vorschlag_quellen_hash(w, quellen), "entscheidungen": []}
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
    ohne_version = [{"vorgang": d["slug"]} for d in gruppe if not d["dokumente"]["eindeutig"]]
    if ohne_version:
        ablegen("dokumentversion", "Dokumentversionen der versendeten Bewerbungen nachweisbar machen", "datenqualitaet",
                f"{len(ohne_version)} versendete Bewerbungen haben keine eindeutige Dokumentversion.", ohne_version,
                "Ohne Version lässt sich ein Ergebnis keiner Fassung der Unterlagen zuordnen; Vergleiche zwischen Fassungen sind dann nicht möglich.",
                "Auswertungen nach Dokumentversion werden möglich.", "gering: es geht um fehlende Angaben, nicht um eine Deutung",
                "Aufwand beim Eintragen von `anhaenge` und beim Ausführen von `task quality`", "niedrig")
    offene = km.offene_vorschlaege(w)
    if offene:
        ablegen("nachrichten:" + digest(*sorted(n["id"] for n in offene))[:8], "Ungeprüfte Rückmeldungen im Eingang prüfen", "nachverfolgung",
                f"{len(offene)} Nachrichten warten auf die Prüfung.", [{"vorgang": n["vorgang"]} for n in offene if n["vorgang"]] or [{"vorgang": "-"}],
                "Solange Rückmeldungen nicht bestätigt sind, fließen sie nicht in die Auswertung ein.", "vollständigere Statistik", "gering", "keines", "hoch")
    tage = ss.read_frontmatter(konfiguration).get("nachfass_tage", "") if konfiguration and os.path.isfile(konfiguration) else ""
    if tage.isdigit():
        heute_datum = km.heute(now)
        faellig = [{"vorgang": d["slug"]} for d in gruppe if d["status"] == "versendet" and "rueckmeldung" not in d["flags"]
                   and (dt.date.fromisoformat(heute_datum) - dt.date.fromisoformat(d["versendet_am"])).days >= int(tage)]
        if faellig:
            ablegen("nachfassen:" + digest(*sorted(q["vorgang"] for q in faellig))[:8], "Nachfassen bei Bewerbungen ohne Rückmeldung prüfen", "nachverfolgung",
                    f"{len(faellig)} Bewerbungen sind seit mindestens {tage} Tagen (nachfass_tage) ohne Rückmeldung.", faellig,
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
                                  "risiken", "prioritaet", "status", "entscheidungen")},
            "auswirkung": "Die Annahme ändert keine Datei. Persönliche Stammdaten, Qualifikationen und Dokumente ändert nur die Nutzerin oder der Nutzer selbst.",
            "naechster_schritt": {"erstellt": "vorlegen", "zur_pruefung": "entscheiden (--ja)", "zurueckgestellt": "vorlegen", "angenommen": "umsetzen und `umgesetzt` melden"}.get(v["status"], "keiner")}


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
    return {k: getattr(args, k, None) for k in ("status", "arbeitgeber", "stellenprofil", "ausrichtung")}


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
    r = sub.add_parser("retrospektive")
    filter_args(r)
    a = sub.add_parser("aktualitaet")
    a.add_argument("datei")
    vs = sub.add_parser("vorschlaege")
    vs.add_argument("aktion", choices=("erzeugen", "liste"))
    vs.add_argument("--status", choices=VORSCHLAG_STATUS)
    v = sub.add_parser("vorschlag")
    v.add_argument("aktion", choices=("zeige", "vorlegen", "entscheiden"))
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
        return statistik(w, now, args.von, args.bis, args.nach, filter_aus(args))
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
            return retrospektive(w, now, args.von, args.bis, filter_aus(args))
        if befehl == "ergebnis":
            if aktion == "erfassen":
                return ergebnis_erfassen(w, args.vorgang, args.art or "", args.datum or "", args.original,
                                         {"kategorie": args.kategorie, "thema": args.thema, "aussage": args.aussage, "nachricht": args.nachricht}, now)
            return ergebnis_aendern(w, args.vorgang, args.id or "", aktion, {"art": args.art, "datum": args.datum, "grund": args.grund}, now)
        if befehl == "vorschlaege":
            return erzeuge_vorschlaege(w, now, args.konfiguration)
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
