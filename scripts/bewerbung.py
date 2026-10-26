#!/usr/bin/env python3
"""The result of an application: identity, phase, outcome, event history, next steps, validation and migration (spec bewerbungsergebnis BE-1 to BE-16, R-01).

Nothing here is a second model. The application is the Vorgang (`<wurzel>/<slug>/`, the folder name is its stable id and never changes,
LS-6 rule 5). Its **status** stays `status` in `vorgang.md` (LS-6 rule 2). Its **history** is `## Verlauf` of `vorgang.md` together with the
structured events of `<vorgang>/nachverfolgung.json`, the file `kommunikation.py` writes for confirmed replies. This script adds to those:

  - the rules for a change of status (one table of allowed transitions) and the events of the course of an application,
  - the separation of five things that must not be mixed: status, phase, outcome, history and data quality (`status`),
  - the check of the stored data without changing it (`pruefen`), the open next steps (`naechste`), a search over all applications that
    also finds the closed ones (`finde`), and a repeatable migration of older data that invents nothing (`migrieren`).

What it never does: send a message, contact an employer, approve anything for the user, read a mailbox, change a document, the Datengrundlage
or a profile, or conclude an outcome from the fact that a Vorgang is closed. A change needs `--ja` and an interactive session.

Usage: bewerbung.py [--konfiguration PFAD] [--jetzt ISO] <befehl> ...
Commands: anlegen, finde, status, historie, naechste, pruefen, ereignis (erfassen|bestaetigen|korrigieren|verwerfen), statuswechsel, migrieren.
Output is one JSON object. Exit code 0 ok, 2 ok=false, 3 refused, 1 blocker. Standard library only.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kommunikation as km  # noqa: E402
import lernen as lr  # noqa: E402
import stellensuche as ss  # noqa: E402
from stellensuche import Blocker, Refused, clean_text, digest, load_json, parse_time, redact, stamp  # noqa: E402

PRE = ("erfasst", "analysiert", "geplant", "erstellt", "in Arbeit", "geprüft")  # before the dispatch (LS-6 S1 to S5)
POST = km.VERLAUF_REIHE  # after the dispatch, in the order of a course
FINAL = km.ENDSTATUS
ALLE = PRE + POST + FINAL
QUELLEN = ("nutzer", "nachricht", "datei", "portal", "workflow", "verlauf", "frontmatter")
BESTAETIGUNG = ("bestaetigt", "automatisch", "unsicher")
METHODEN = ("manuell", "importiert", "nachricht", "migriert")
GUELTIG = ("bestaetigt", "korrigiert")  # the states of an event that count as a fact
TERMIN_ARTEN = ("gespraech_vereinbart", "gespraech_verschoben", "weiterer_termin")

# The status an event of this kind leads to when the user asks for it (`--status-aendern`). An absent entry: the event states a fact and no
# status follows. `angebot_angenommen` has none on purpose: an accepted offer is not yet a hire; `einstellung` (the employer's confirmation)
# leads to `zusage`. `vorbereitet` and `geprueft` are set by the skills that do the work (LS-6).
ART_STATUS = {
    "versendet": "versendet", "rueckfrage": "rückmeldung", "im_auswahlprozess": "rückmeldung", "gespraechseinladung": "gespräch",
    "gespraech_vereinbart": "gespräch", "gespraech": "gespräch", "technisches_gespraech": "gespräch", "assessment": "gespräch", "weiterer_termin": "gespräch",
    "weitere_phase": "gespräch", "angebot": "angebot", "einstellung": "zusage", "angebot_abgelehnt": "abgelehnt", "absage": "absage",
    "absage_nach_unterlagen": "absage", "absage_nach_gespraech": "absage", "absage_nach_assessment": "absage", "zurueckgezogen": "zurückgezogen",
    "abgeschlossen": "abgeschlossen",
}
# Events that only a Vorgang past the dispatch can have. A reply to an application that was never sent is a contradiction (BE-9).
NACH_VERSAND = tuple(a for a in km.ARTEN_ARBEITGEBER) + ("angebot_angenommen", "angebot_abgelehnt")


# ---------------------------------------------------------------- lifecycle (BE-3)

def uebergang_erlaubt(alt, neu):
    """-> (allowed, reason). The one table of the changes of `status`. Not every application passes every status; none goes back
    past the dispatch, and a final status is not left (a wrong one is corrected in vorgang.md by the user)."""
    if neu not in ALLE:
        return False, f"`{neu}` ist kein Statuswert (LS-6 Regel 2)"
    if alt not in ALLE:
        return False, f"der aktuelle Status `{alt}` ist unbekannt"
    if alt == neu:
        return False, "der Status ist schon so"
    if alt in FINAL:
        return False, f"`{alt}` ist ein Endstatus: ein Endstatus wird nicht verlassen (ein falscher wird von Hand in vorgang.md berichtigt)"
    if neu in PRE:
        return (True, "") if alt in PRE else (False, "nach dem Versand geht ein Vorgang nicht in die Vorbereitung zurück")
    if neu == "versendet":
        return (True, "") if alt in PRE else (False, "der Vorgang ist schon versendet")
    if neu in POST:
        if alt in POST and POST.index(neu) > POST.index(alt):
            return True, ""
        return False, f"`{neu}` ist nur nach dem Versand und nur vorwärts erlaubt (aktuell `{alt}`)"
    if neu in ("zusage", "abgelehnt"):
        return (True, "") if alt in ("angebot", "verhandlung") else (False, f"`{neu}` setzt ein Angebot voraus (aktuell `{alt}`)")
    if neu in ("absage", "ohne Antwort"):
        return (True, "") if alt in POST else (False, f"`{neu}` ist nur nach dem Versand möglich (aktuell `{alt}`)")
    return True, ""  # zurückgezogen, abgeschlossen: from any status that is not final


def bestaetigte(nv):
    return [e for e in nv["ereignisse"] if e.get("status") in GUELTIG]


def eingetreten(e):
    return e.get("eingetreten_am") or e.get("datum") or ""


def phase_von(status, ereignisse, freigabe_erledigt):
    """The phase of the course in plain terms, from the status and the confirmed events only (BE-4). Never from a closed Vorgang."""
    arten = {e["art"] for e in ereignisse}
    if status in FINAL:
        return {"zusage": "eingestellt", "absage": "abgelehnt", "abgelehnt": "angebot_abgelehnt", "zurückgezogen": "zurueckgezogen"}.get(status, "abgeschlossen")
    if status in ("angebot", "verhandlung"):
        return "angebot_angenommen" if "angebot_angenommen" in arten else "angebot"
    if status == "gespräch":
        if arten & {"gespraech", "technisches_gespraech", "assessment"}:
            return "gespraech_gefuehrt"
        if arten & {"gespraech_vereinbart", "weiterer_termin"}:
            return "gespraech_vereinbart"
        return "einladung" if arten & {"gespraechseinladung"} else "in_pruefung"
    if status == "rückmeldung":
        return "in_pruefung"
    if status == "versendet":
        return "eingang_bestaetigt" if "eingangsbestaetigung" in arten else "eingereicht"
    if status == "geprüft":
        return "freigegeben" if freigabe_erledigt else "freigabe_ausstehend"
    if status in ("analysiert", "geplant", "erstellt", "in Arbeit"):
        return "vorbereitung"
    return "entdeckt"


def ergebnis_von(status, ereignisse):
    """The outcome, apart from the phase (BE-5). Known only when a status of the user or a confirmed event states it; a closed Vorgang
    is never read as a failure."""
    arten = {e["art"] for e in ereignisse}
    if status == "zusage":
        return {"art": "eingestellt", "bekannt": True, "beleg": "status zusage"}
    if status == "absage":
        return {"art": "abgelehnt_vom_arbeitgeber", "bekannt": True, "beleg": "status absage"}
    if status == "abgelehnt":
        return {"art": "angebot_abgelehnt_vom_bewerber", "bekannt": True, "beleg": "status abgelehnt"}
    if status == "zurückgezogen":
        return {"art": "zurueckgezogen_vom_bewerber", "bekannt": True, "beleg": "status zurückgezogen"}
    if status in ("ohne Antwort", "abgeschlossen"):
        return {"art": "ohne_entscheidung_abgeschlossen", "bekannt": True, "beleg": f"status {status}",
                "hinweis": "abgeschlossen ohne Entscheidung des Arbeitgebers: kein Misserfolg und kein Erfolg"}
    if status in ("angebot", "verhandlung"):
        return {"art": "angenommen_noch_nicht_bestaetigt" if "angebot_angenommen" in arten else "angebot_offen", "bekannt": False,
                "beleg": "ereignis angebot_angenommen" if "angebot_angenommen" in arten else "status angebot"}
    return {"art": "offen" if status in POST else "noch_nicht_versendet", "bekannt": False, "beleg": ""}


# ---------------------------------------------------------------- reading

def workflow_aufgaben(w, slug):
    try:
        daten = load_json(os.path.join(w, "workflow", "aufgaben.json"), {"aufgaben": {}})
    except Refused:
        return []
    return [t for t in daten.get("aufgaben", {}).values() if isinstance(t, dict) and isinstance(t.get("bezug"), dict) and t["bezug"].get("vorgang") == slug]


def dokumente(w, slug):
    ordner = os.path.join(w, slug)
    vorhanden = {}
    for name in ("lebenslauf.md", "anschreiben.md", "motivationsschreiben.md", "email.md"):
        pfad = os.path.join(ordner, name)
        if os.path.isfile(pfad):
            meta = ss.read_frontmatter(pfad)
            vorhanden[name] = {"hash": km.sha256_file(pfad)[:12], "version_datum": meta.get("version_datum", "")}
    export = os.path.join(ordner, "export")
    exporte = sorted(n for n in os.listdir(export) if n.endswith(".manifest.json")) if os.path.isdir(export) else []
    stand = lr.dokument_stand(w, slug)
    return {"dateien": vorhanden, "exporte": exporte, "qualitaet_stand": stand["stand"], "version_eindeutig": stand["eindeutig"],
            "version_hinweis": stand["grund"]}


def ansicht(w, slug, now):
    meta = km.vorgang_meta(w, slug)
    nv = km.lade_nachverfolgung(w, slug)
    fakten = bestaetigte(nv)
    status = meta.get("status", "")
    aufgaben = workflow_aufgaben(w, slug)
    freigabe = any(t["typ"] == "versand_freigabe" and t["status"] == "erledigt" for t in aufgaben)
    firma_datei = os.path.join(w, "firmen", ss.slug(meta.get("firma", "")) + ".md")
    firmen = ss.read_frontmatter(firma_datei) if os.path.isfile(firma_datei) else {}
    versendet = ss.valid_date(meta.get("versendet_am", ""))
    unbekannt = [name for name, wert in (("versendet_am", versendet or (status not in POST + FINAL and "-")), ("weg", meta.get("weg") or (status not in POST + FINAL and "-")),
                                         ("ref_nr", meta.get("ref_nr") or meta.get("stellenquelle"))) if not wert]
    return {
        "ok": True, "id": slug, "stelle": {"firma": meta.get("firma", ""), "titel": meta.get("stelle", ""), "ref_nr": meta.get("ref_nr", ""),
                                           "quelle": meta.get("stellenquelle", ""), "sitz": firmen.get("sitz", ""), "anzeige_gesichert": os.path.isfile(os.path.join(w, slug, "stellenanzeige.md"))},
        "status": status, "phase": phase_von(status, fakten, freigabe), "ergebnis": ergebnis_von(status, fakten),
        "versand": {"versendet_am": versendet, "weg": meta.get("weg", ""), "anhaenge": meta.get("anhaenge", ""), "belegt": bool(versendet)},
        "dokumente": dokumente(w, slug), "ereignisse": {"bestaetigt": len(fakten), "zur_pruefung": sum(1 for e in nv["ereignisse"] if e.get("status") in ("zur_pruefung", "erkannt")),
                                                      "verworfen": sum(1 for e in nv["ereignisse"] if e.get("status") == "verworfen")},
        "aufgaben": [{"id": t["id"], "typ": t["typ"], "status": t["status"]} for t in aufgaben if t["status"] not in ("erledigt", "abgebrochen")],
        "unbekannt": unbekannt, "datenqualitaet": {"befunde": len(pruefe_vorgang(w, slug, now)), "hinweis": "`bewerbung.py pruefen` nennt sie"},
    }


# ---------------------------------------------------------------- next steps (BE-8)

def naechste_schritte(w, slug, now):
    meta = km.vorgang_meta(w, slug)
    status = meta.get("status", "")
    nv = km.lade_nachverfolgung(w, slug)
    fakten = bestaetigte(nv)
    arten = {e["art"] for e in fakten}
    heute_datum = km.heute(now)
    schritte = []
    if status in FINAL:
        return schritte
    for r in nv["wiedervorlagen"]:
        if r["status"] == "offen":
            schritte.append({"art": "wiedervorlage", "id": r["id"], "anlass": r["anlass"], "faellig": r["faellig"], "ist_faellig": bool(r["faellig"] and r["faellig"] <= heute_datum),
                             "verbindlichkeit": r.get("verbindlichkeit", "eigene_planung"), "hinweis": "eine Erinnerung für dich; sie sendet nichts"})
    for n in km.offene_vorschlaege(w, slug):
        schritte.append({"art": "nachricht_pruefen", "id": n["id"], "hinweis": "eine Nachricht wartet auf die Prüfung (kommunikation.py zeige, bestaetigen)"})
    for e in nv["ereignisse"]:
        if e.get("status") in ("zur_pruefung", "erkannt"):
            schritte.append({"art": "ereignis_pruefen", "id": e["id"], "hinweis": f"{e['art']} ist nicht bestätigt (bewerbung.py ereignis bestaetigen)"})
    for t in workflow_aufgaben(w, slug):
        if t["status"] not in ("erledigt", "abgebrochen", "fehlgeschlagen"):
            schritte.append({"art": "aufgabe", "id": t["id"], "status": t["status"], "hinweis": t.get("zweck", "")})
    offen = {r["anlass"] for r in nv["wiedervorlagen"] if r["status"] == "offen"}
    if status in POST and not ss.valid_date(meta.get("versendet_am", "")):
        schritte.append({"art": "information_fehlt", "feld": "versendet_am", "hinweis": "Das Versanddatum fehlt: ohne es gibt es keine Antwortzeit und keine Frist (ereignis erfassen --art versendet)"})
    if "gespraech_vereinbart" in arten and not any(e.get("termin") for e in fakten if e["art"] in TERMIN_ARTEN):
        schritte.append({"art": "information_fehlt", "feld": "termin", "hinweis": "Ein Gespräch ist vereinbart, aber sein Termin ist nicht erfasst"})
    if arten & {"gespraech", "technisches_gespraech", "assessment"} and "gespraechsnachbereitung" not in offen and not arten & {"angebot", "absage", "einstellung"}:
        schritte.append({"art": "vorschlag", "anlass": "gespraechsnachbereitung", "hinweis": "Das Gespräch hat stattgefunden: Nachbereitung als Wiedervorlage anlegen, wenn du eine willst"})
    if "angebot" in arten and not arten & {"angebot_angenommen", "angebot_abgelehnt"} and "angebot_pruefen" not in offen and "rueckmeldefrist" not in offen:
        schritte.append({"art": "information_fehlt", "feld": "frist_angebot", "hinweis": "Ein Angebot liegt vor, aber keine Frist ist erfasst: nennt der Arbeitgeber eine, als `rueckmeldefrist` mit --arbeitgeber-frist anlegen"})
    return schritte


# ---------------------------------------------------------------- validation (BE-10)

def befund(grad, regel, vorgang, text, ereignis=""):
    return {"grad": grad, "regel": regel, "vorgang": vorgang, "ereignis": ereignis, "befund": clean_text(text, 220)}


def pruefe_vorgang(w, slug, now):
    """Findings for one Vorgang. Reads only. A missing optional item is no error; an unknown date stays unknown."""
    meta = km.vorgang_meta(w, slug)
    befunde, status = [], meta.get("status", "")
    try:
        nv = km.lade_nachverfolgung(w, slug)
    except Refused as error:
        return [befund("Fehler", "BE-V06", slug, f"nachverfolgung.json ist nicht lesbar: {error.meldung}")]
    heute_datum = km.heute(now)
    versendet = ss.valid_date(meta.get("versendet_am", ""))
    if status not in ALLE:
        befunde.append(befund("Fehler", "BE-V03", slug, f"status `{status}` ist kein Wert von LS-6 Regel 2"))
    if status in ("analysiert", "geplant", "erstellt", "geprüft", "in Arbeit") + POST + FINAL and not os.path.isfile(os.path.join(w, slug, "stellenanzeige.md")):
        befunde.append(befund("Warnung", "BE-V01", slug, "stellenanzeige.md fehlt: der Bezug zur Stelle ist nicht gesichert, falls die Anzeige verschwindet"))
    if not meta.get("ref_nr") and not meta.get("stellenquelle"):
        befunde.append(befund("Hinweis", "BE-V01", slug, "weder ref_nr noch stellenquelle: die Stelle ist nur über Firma und Titel bestimmt"))
    if meta.get("versendet_am") and not versendet:
        befunde.append(befund("Fehler", "BE-V04", slug, "versendet_am ist kein Datum der Form JJJJ-MM-TT"))
    if (status in POST or status in ("zusage", "absage", "abgelehnt", "ohne Antwort")) and not versendet:
        befunde.append(befund("Warnung", "BE-V07", slug, f"status `{status}` setzt den Versand voraus, aber versendet_am ist nicht belegt"))
    if meta.get("loeschen_ab") and not ss.valid_date(meta["loeschen_ab"]):
        befunde.append(befund("Fehler", "BE-V04", slug, "loeschen_ab ist kein Datum"))
    gesehen, ids = {}, set()
    fakten = bestaetigte(nv)
    for e in nv["ereignisse"]:
        eid = e.get("id", "?")
        if eid in ids:
            befunde.append(befund("Fehler", "BE-V08", slug, "Ereignis-ID kommt doppelt vor", eid))
        ids.add(eid)
        if e.get("vorgang") and e["vorgang"] != slug:
            befunde.append(befund("Fehler", "BE-V05", slug, f"das Ereignis verweist auf den Vorgang {redact(e['vorgang'], 40)}", eid))
        if e.get("art") not in km.ARTEN:
            befunde.append(befund("Fehler", "BE-V03", slug, f"unbekannte Ereignisart `{redact(e.get('art'), 40)}`", eid))
        wann = e.get("eingetreten_am") or e.get("datum") or ""
        if wann and ss.valid_date(wann) != wann:
            befunde.append(befund("Fehler", "BE-V04", slug, f"eingetreten_am `{redact(wann, 20)}` ist kein Datum", eid))
        elif wann:
            if wann > heute_datum and e.get("art") not in TERMIN_ARTEN:
                befunde.append(befund("Warnung", "BE-V04", slug, "das Ereignis liegt in der Zukunft", eid))
            if versendet and wann < versendet and e.get("art") in NACH_VERSAND and e.get("status") in GUELTIG:
                befunde.append(befund("Warnung", "BE-V04", slug, f"{e['art']} ({wann}) liegt vor dem Versand ({versendet})", eid))
        if e.get("methode") in ("importiert", "nachricht") and not (e.get("quelle") or {}).get("nachricht_id") and not (e.get("quelle") or {}).get("referenz"):
            befunde.append(befund("Fehler", "BE-V09", slug, "ein importiertes Ereignis hat keine Quellenangabe", eid))
        if e.get("schluessel"):
            if e["schluessel"] in gesehen and e.get("status") != "verworfen":
                befunde.append(befund("Warnung", "BE-V10", slug, f"dasselbe Ereignis steht auch als {gesehen[e['schluessel']]}", eid))
            gesehen.setdefault(e["schluessel"], eid)
        if e.get("termin") and ss.valid_date(e["termin"]) != e["termin"]:
            befunde.append(befund("Fehler", "BE-V04", slug, "termin ist kein Datum", eid))
    arten = {e["art"] for e in fakten}
    if arten & {"absage", "absage_nach_unterlagen", "absage_nach_gespraech", "absage_nach_assessment"} and arten & {"einstellung", "angebot_angenommen"}:
        befunde.append(befund("Fehler", "BE-V11", slug, "widersprüchliche Endergebnisse: eine Absage und eine Annahme oder Einstellung sind beide bestätigt"))
    if "angebot_angenommen" in arten and "angebot_abgelehnt" in arten:
        befunde.append(befund("Fehler", "BE-V11", slug, "das Angebot ist als angenommen und als abgelehnt bestätigt"))
    ziel_arten = {s: [a for a, t in ART_STATUS.items() if t == s] for s in set(ART_STATUS.values())}
    if status in ziel_arten and status not in ("versendet", "abgeschlossen") and not arten & set(ziel_arten[status]):
        verworfen = [e for e in nv["ereignisse"] if e.get("status") == "verworfen" and e.get("art") in ziel_arten[status]]
        if verworfen:
            befunde.append(befund("Warnung", "BE-V12", slug, f"status `{status}`, aber das Ereignis dafür wurde verworfen und kein anderes ist bestätigt", verworfen[0]["id"]))
    if status == "versendet":
        for e in fakten:
            if e["art"] in ("rueckfrage", "gespraechseinladung", "angebot", "absage", "im_auswahlprozess"):
                befunde.append(befund("Warnung", "BE-V03", slug, f"das bestätigte Ereignis {e['art']} passt nicht zum Status `versendet`: der Status steht hinter den Ereignissen zurück", e["id"]))
                break
    for e in fakten:
        zeit = eingetreten(e)
        if status in FINAL and zeit:
            letzter = [x for x in fakten if eingetreten(x) > zeit]
            if letzter and status != "abgeschlossen" and e["art"] in ("absage", "einstellung"):
                befunde.append(befund("Warnung", "BE-V03", slug, f"nach dem Endergebnis {e['art']} gibt es noch spätere bestätigte Ereignisse", e["id"]))
                break
    verlauf_ids = re.findall(r"Gmail-ID ([A-Za-z0-9_.:@-]+?)[,)]", _verlauf_text(w, slug))
    for mid, anzahl in {m: verlauf_ids.count(m) for m in set(verlauf_ids)}.items():
        if anzahl > 1:
            befunde.append(befund("Warnung", "BE-V10", slug, f"die Nachricht {redact(mid, 40)} steht {anzahl}-mal in ## Verlauf"))
    return befunde


def _verlauf_text(w, slug):
    try:
        with open(km.vorgang_pfad(w, slug), encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def pruefe_alle(w, now, slug=None):
    vorgaenge = km.alle_vorgaenge(w)
    if slug:
        km.vorgang_meta(w, slug)
        vorgaenge = {slug: vorgaenge[slug]}
    befunde = []
    for name in vorgaenge:
        befunde += pruefe_vorgang(w, name, now)
    if not slug:
        try:
            for n in km.lade_eingang(w)["nachrichten"].values():
                if n.get("vorgang") and n["vorgang"] not in km.alle_vorgaenge(w):
                    befunde.append(befund("Fehler", "BE-V05", n["vorgang"], f"die Nachricht {redact(n['id'], 40)} verweist auf einen Vorgang, den es nicht gibt"))
        except Refused as error:
            befunde.append(befund("Fehler", "BE-V06", "-", f"eingang.json ist nicht lesbar: {error.meldung}"))
    gruppen = {}
    for name, meta in km.alle_vorgaenge(w).items():
        if meta.get("status") in ALLE and not slug:
            schluessel = (ss.norm(meta.get("firma", "")), ss.norm(meta.get("stelle", "")), (meta.get("ref_nr") or "").strip())
            gruppen.setdefault(schluessel, []).append(name)
    for namen in gruppen.values():
        offen = [n for n in namen if vorgaenge.get(n, {}).get("status") not in FINAL]
        if len(namen) > 1 and len(offen) > 1:
            befunde.append(befund("Warnung", "BE-V02", ", ".join(sorted(namen)), "mehrere offene Vorgänge für dieselbe Firma, Stelle und Referenznummer: ein Doppelt angelegter Vorgang?"))
    return befunde


# ---------------------------------------------------------------- writing (BE-6, BE-7)

def pruefe_zeit(text, name, zukunft_erlaubt=False, heute_datum=""):
    if not text:
        return ""
    if ss.valid_date(text) != text:
        raise Refused("datum_ungueltig", f"--{name} ist ein echtes Datum der Form JJJJ-MM-TT")
    if not zukunft_erlaubt and text > heute_datum:
        raise Refused("datum_in_zukunft", f"--{name} liegt in der Zukunft: ein Ereignis ist geschehen, ein Termin ist keins")
    return text


def schreibe_nv_dann_vorgang(w, slug, nv_neu, nv_alt, schreibe):
    """The event file first, then vorgang.md; when the second write fails the first is put back, so no event stays without its line."""
    km.speichere_nachverfolgung(w, slug, nv_neu)
    try:
        schreibe()
    except Refused:
        km.speichere_nachverfolgung(w, slug, nv_alt)
        raise


def wechsle(w, slug, meta, ziel, grund_text, datum, ereignis_id):
    """The lines and the change of `status` for an allowed transition; raises before anything is written."""
    alt = meta.get("status", "")
    erlaubt, grund = uebergang_erlaubt(alt, ziel)
    if not erlaubt:
        raise Refused("uebergang_nicht_erlaubt", grund)
    return [f"- {datum}: {alt} → {ziel}, bewerbung.py ({grund_text}, {ereignis_id})"]


def erfassen(w, slug, art, o, jetzt):
    meta = km.vorgang_meta(w, slug)
    heute_datum = km.heute(jetzt)
    if art not in km.ARTEN or art == "statuswechsel":
        raise Refused("art_unbekannt", f"Ereignisart {redact(art, 40)} ist nicht bekannt ({', '.join(a for a in km.ARTEN if a != 'statuswechsel')})")
    wann = pruefe_zeit(o.get("eingetreten_am") or "", "eingetreten-am", False, heute_datum)
    termin = pruefe_zeit(o.get("termin") or "", "termin", True, heute_datum)
    erinnerung = pruefe_zeit(o.get("erinnerung") or "", "erinnerung", True, heute_datum)
    if art == "versendet" and not wann:
        raise Refused("datum_fehlt", "Ein Versand braucht sein Datum (--eingetreten-am): es wird nicht geschätzt, und ohne Datum gibt es keine Antwortzeit")
    if art in TERMIN_ARTEN and art != "weiterer_termin" and not termin and art == "gespraech_vereinbart":
        raise Refused("termin_fehlt", "Ein vereinbartes Gespräch braucht seinen Termin (--termin)")
    typ, bestaetigung, methode = o.get("quelle_typ") or "nutzer", o.get("bestaetigung") or "bestaetigt", o.get("methode") or "manuell"
    if typ not in QUELLEN or bestaetigung not in BESTAETIGUNG or methode not in METHODEN:
        raise Refused("angabe_ungueltig", f"quelle-typ: {', '.join(QUELLEN)}; bestaetigung: {', '.join(BESTAETIGUNG)}; methode: {', '.join(METHODEN)}")
    referenz = clean_text(o.get("referenz") or "", 120)
    if (methode in ("importiert", "nachricht") or typ in ("nachricht", "datei", "portal")) and not referenz:
        raise Refused("quelle_fehlt", "Zu einer Nachricht, einer Datei oder einem Portal gehört eine Referenz (--referenz); sie wird nicht erfunden")
    nv_alt = km.lade_nachverfolgung(w, slug)
    nv = json.loads(json.dumps(nv_alt))
    beleg = bestaetigung == "bestaetigt"
    ereignis, neu = km.ereignis_bauen(nv, slug, art, wann, {"typ": typ, "referenz": referenz}, km.schwaerze(o.get("original") or "")[:km.ORIGINAL_MAX], None,
                                      "bestaetigt" if beleg else "zur_pruefung", jetzt, methode, bestaetigung, vorgang=slug,
                                      beschreibung=clean_text(o.get("beschreibung") or "", 200), termin=termin, status_vorher=meta.get("status", ""))
    if not neu:
        return {"ok": True, "neu": False, "ereignis": ereignis, "hinweis": "Dieses Ereignis ist schon erfasst; es wird nicht doppelt gespeichert."}
    zeilen, neuer_status, meta_aenderungen = [], None, []
    if beleg:
        datum = wann or heute_datum
        zeilen.append(f"- {datum}: Ereignis {art} erfasst (Ereignis {ereignis['id']}, Quelle {typ})")
        if o.get("status_aendern"):
            ziel = o.get("status_nach") or ART_STATUS.get(art)
            if not ziel:
                raise Refused("kein_statusziel", f"Zu `{art}` gehört kein Status; --status-nach angeben oder den Status von Hand pflegen")
            zeilen = wechsle(w, slug, meta, ziel, f"Ereignis {art}", datum, ereignis["id"])  # one line: the change of status names the event
            neuer_status = ziel
            ereignis["status_nachher"] = ziel
        if art == "versendet":
            vorher = ss.valid_date(meta.get("versendet_am", ""))
            if vorher and vorher != wann:
                raise Refused("versendet_am_abweichend", f"vorgang.md nennt als Versand den {vorher}, das Ereignis den {wann}: erst klären, welches stimmt")
            if not vorher:
                meta_aenderungen.append(("versendet_am", wann))
            if o.get("kanal") and not meta.get("weg"):
                meta_aenderungen.append(("weg", o["kanal"]))
    elif o.get("status_aendern"):
        raise Refused("nicht_bestaetigt", "Ein Ereignis, das noch nicht bestätigt ist, ändert keinen Status: erst `ereignis bestaetigen`")
    if erinnerung:
        anlass = "gespraechstermin" if art in TERMIN_ARTEN else o.get("erinnerung_anlass") or "fehlende_information"
        nv["wiedervorlagen"].append({"id": km.neues_id(nv["wiedervorlagen"], "w"), "anlass": anlass, "faellig": erinnerung, "beschreibung": f"zu {art} ({ereignis['id']})",
                                     "quelle": {"typ": "ereignis", "ereignis": ereignis["id"]}, "status": "offen", "angelegt": stamp(jetzt), "verbindlichkeit": "eigene_planung"})

    def schreibe():
        for schluessel, wert in meta_aenderungen:
            km.setze_meta(w, slug, schluessel, wert)
        if zeilen or neuer_status:
            km.schreibe_verlauf(w, slug, zeilen, neuer_status)
    schreibe_nv_dann_vorgang(w, slug, nv, nv_alt, schreibe)
    return {"ok": True, "neu": True, "ereignis": ereignis, "status": neuer_status or meta.get("status", ""), "zeilen": zeilen,
            "hinweis": "Es wurde nichts gesendet. Eine Wiedervorlage erinnert nur." if erinnerung else "Es wurde nichts gesendet."}


def ereignis_bestaetigen(w, slug, ereignis_id, jetzt):
    nv_alt = km.lade_nachverfolgung(w, slug)
    nv = json.loads(json.dumps(nv_alt))
    e = next((x for x in nv["ereignisse"] if x["id"] == ereignis_id), None)
    if e is None:
        raise Refused("ereignis_unbekannt", f"Kein Ereignis {redact(ereignis_id, 40)} in {slug}")
    if e["status"] not in ("zur_pruefung", "erkannt"):
        raise Refused("bereits_entschieden", f"{ereignis_id} ist {e['status']}")
    e["status"], e["bestaetigung"], e["bestaetigt_am"] = "bestaetigt", "bestaetigt", stamp(jetzt)
    datum = eingetreten(e) or km.heute(jetzt)
    zeilen = [f"- {datum}: Ereignis {e['art']} bestätigt (Ereignis {e['id']})"]
    schreibe_nv_dann_vorgang(w, slug, nv, nv_alt, lambda: km.schreibe_verlauf(w, slug, zeilen, None))
    return {"ok": True, "ereignis": e, "hinweis": "Der Status ändert sich dadurch nicht; dafür gibt es `statuswechsel`."}


def statuswechsel(w, slug, ziel, grund, jetzt):
    meta = km.vorgang_meta(w, slug)
    if not grund.strip():
        raise Refused("grund_fehlt", "--grund fehlt: ein Statuswechsel ist nachvollziehbar")
    datum = km.heute(jetzt)
    nv_alt = km.lade_nachverfolgung(w, slug)
    nv = json.loads(json.dumps(nv_alt))
    ereignis, _ = km.ereignis_bauen(nv, slug, "statuswechsel", datum, {"typ": "nutzer", "referenz": f"{meta.get('status', '')}->{ziel}"}, "", None, "bestaetigt", jetzt, "manuell",
                                    "bestaetigt", vorgang=slug, beschreibung=clean_text(grund, 200), status_vorher=meta.get("status", ""), status_nachher=ziel)
    zeilen = wechsle(w, slug, meta, ziel, clean_text(grund, 80), datum, ereignis["id"])
    schreibe_nv_dann_vorgang(w, slug, nv, nv_alt, lambda: km.schreibe_verlauf(w, slug, zeilen, ziel))
    return {"ok": True, "status": ziel, "ereignis": ereignis["id"], "zeilen": zeilen}


def ereignis_aendern(w, slug, ereignis_id, aktion, felder, jetzt):
    """A correction keeps the old values (`korrekturen`); the file is replaced in one piece (BE-6 rule 5)."""
    ergebnis = lr.ergebnis_aendern(w, slug, ereignis_id, aktion, felder, jetzt)
    nv = km.lade_nachverfolgung(w, slug)
    e = next(x for x in nv["ereignisse"] if x["id"] == ereignis_id)
    if aktion == "korrigieren":
        e["eingetreten_am"] = e.get("datum", "")
        e["schluessel"] = km.schluessel_von(slug, e["art"], e["eingetreten_am"], (e.get("quelle") or {}).get("nachricht_id") or (e.get("quelle") or {}).get("referenz") or (e.get("beschreibung") or "")[:40], (e.get("quelle") or {}).get("typ"))
        km.speichere_nachverfolgung(w, slug, nv)
    km.schreibe_verlauf(w, slug, [f"- {km.heute(jetzt)}: Ereignis {ereignis_id} {'korrigiert' if aktion == 'korrigieren' else 'verworfen'} ({clean_text(felder.get('grund', ''), 80) or 'ohne Grund'})"], None)
    return ergebnis


# ---------------------------------------------------------------- applications (BE-2, BE-12)

def slug_aus(firma, stelle):
    def teil(text):
        text = text.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text)).strip("-")
    return f"{teil(firma)}-{teil(stelle)}".strip("-")[:70].strip("-")


def anlegen(w, slug, firma, stelle, optionen, jetzt):
    """An application that was made outside the plugin, or before it: a minimal vorgang.md at the status `erfasst` (S1). No analysis, no invented fact."""
    if not firma.strip() or not stelle.strip():
        raise Refused("angabe_fehlt", "--firma und --stelle sind nötig")
    slug = slug or slug_aus(firma, stelle)
    if not km.KUERZEL.fullmatch(slug or ""):
        raise Refused("vorgang_ungueltig", "Der Vorgangsname besteht aus a-z, 0-9 und - (LS-7.7)")
    if os.path.exists(os.path.join(w, slug)):
        raise Refused("vorgang_existiert", f"Den Vorgang {slug} gibt es schon; ein zweiter Vorgang für dieselbe Stelle bekommt ein Zahlensuffix (LS-6 Regel 6)")
    for name, meta in km.alle_vorgaenge(w).items():
        gleich = ss.norm(meta.get("firma", "")) == ss.norm(firma) and ss.norm(meta.get("stelle", "")) == ss.norm(stelle)
        if gleich and (not optionen.get("ref_nr") or meta.get("ref_nr") == optionen["ref_nr"]) and meta.get("status") not in FINAL:
            raise Refused("vorgang_doppelt", f"Für diese Stelle gibt es schon den offenen Vorgang {name}: dort weiterarbeiten oder ihn abschließen")
    zeilen = ["---", f"firma: {clean_text(firma, 120)}", f"stelle: {clean_text(stelle, 160)}", f"ref_nr: {clean_text(optionen.get('ref_nr') or '', 60)}",
              f"stellenquelle: {clean_text(optionen.get('stellenquelle') or '', 300)}", f"bewerbungsweg: {optionen.get('weg') or ''}", "status: erfasst",
              f"erfasst: {km.heute(jetzt)}", "versendet_am:", "weg:", "anhaenge: []", "wiedervorlage:", "loeschen_ab:", "tags: []", "---", "", f"# {clean_text(firma, 120)}: {clean_text(stelle, 160)}", "",
              "## Verlauf", f"- {km.heute(jetzt)}: erfasst, bewerbung.py anlegen (nachträglich angelegt; keine Analyse, keine Anzeige gesichert)", ""]
    os.makedirs(os.path.join(w, slug))
    try:
        with open(os.path.join(w, slug, "vorgang.md"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(zeilen))
        with open(os.path.join(w, slug, "notizen.md"), "w", encoding="utf-8", newline="\n"):
            pass
    except OSError as error:
        raise Refused("speichern_fehlgeschlagen", f"Anlegen fehlgeschlagen: {redact(error)}")
    return {"ok": True, "id": slug, "status": "erfasst", "hinweis": "Die Stellenanzeige ist nicht gesichert; `job-application-posting-analysis` kann sie nachtragen."}


def finde(w, now, firma=None, status=None, ergebnis=None, ref_nr=None, abgeschlossen=False, text=None):
    zeilen = []
    for slug, meta in km.alle_vorgaenge(w).items():
        s = meta.get("status", "")
        if firma and ss.norm(firma) not in ss.norm(meta.get("firma", "")):
            continue
        if status and s != status:
            continue
        if ref_nr and meta.get("ref_nr") != ref_nr:
            continue
        if abgeschlossen and s not in FINAL:
            continue
        if text and ss.norm(text) not in ss.norm(" ".join((slug, meta.get("firma", ""), meta.get("stelle", "")))):
            continue
        try:
            nv = km.lade_nachverfolgung(w, slug)
            e = ergebnis_von(s, bestaetigte(nv))
            ph = phase_von(s, bestaetigte(nv), False)
        except Refused:
            e, ph = {"art": "unbekannt", "bekannt": False}, "unbekannt"
        if ergebnis and e["art"] != ergebnis:
            continue
        zeilen.append({"id": slug, "firma": meta.get("firma", ""), "stelle": meta.get("stelle", ""), "status": s, "phase": ph, "ergebnis": e["art"],
                       "ergebnis_bekannt": e["bekannt"], "versendet_am": ss.valid_date(meta.get("versendet_am", ""))})
    return {"ok": True, "anzahl": len(zeilen), "bewerbungen": sorted(zeilen, key=lambda z: (z["versendet_am"] or "9999", z["id"]))}


def historie(w, slug):
    meta = km.vorgang_meta(w, slug)
    nv = km.lade_nachverfolgung(w, slug)
    ereignisse = sorted(nv["ereignisse"], key=lambda e: (eingetreten(e) or "9999-99-99", e.get("erfasst", ""), e["id"]))
    verlauf = [z for z in _verlauf_text(w, slug).splitlines() if re.match(r"^- \d{4}-\d{2}-\d{2}:", z)]
    return {"ok": True, "id": slug, "status": meta.get("status", ""), "ereignisse": ereignisse, "verlauf": verlauf,
            "hinweis": "Reihenfolge nach dem Tag des Ereignisses (unbekannt zuletzt), dann nach dem Zeitpunkt der Erfassung. Korrigierte Ereignisse tragen ihre alten Werte in `korrekturen`."}


# ---------------------------------------------------------------- migration (BE-11)

VERLAUF_STATUS = re.compile(r"^- (\d{4}-\d{2}-\d{2}): ([^→\n]+?) → ([^,\n]+?)(?:, .*)?$")


def migriere_vorgang(w, slug, jetzt, anwenden):
    """Older data into the fields of R-01, additive and repeatable. It adds what the files show and nothing else: no outcome event,
    no estimated date, no change of vorgang.md. A second run finds nothing to do."""
    meta = km.vorgang_meta(w, slug)
    nv_alt = km.lade_nachverfolgung(w, slug)
    nv = json.loads(json.dumps(nv_alt))
    plan = []
    for e in nv["ereignisse"]:
        aenderung = []
        if "eingetreten_am" not in e:
            e["eingetreten_am"] = e.get("datum", "") if ss.valid_date(e.get("datum", "")) else ""
            aenderung.append("eingetreten_am")
        if "methode" not in e:
            e["methode"] = {"nachricht": "nachricht", "nutzer": "manuell"}.get((e.get("quelle") or {}).get("typ"), "migriert")
            aenderung.append("methode")
        if "bestaetigung" not in e:
            e["bestaetigung"] = "bestaetigt" if e.get("status") in GUELTIG else "automatisch"
            aenderung.append("bestaetigung")
        if "schluessel" not in e:
            quelle = e.get("quelle") or {}
            e["schluessel"] = km.schluessel_von(slug, e.get("art", ""), e["eingetreten_am"], quelle.get("nachricht_id") or quelle.get("referenz") or (e.get("beschreibung") or "")[:40], quelle.get("typ"))
            aenderung.append("schluessel")
        if aenderung:
            e["migriert"] = True
            plan.append({"ereignis": e["id"], "ergaenzt": aenderung})
    versendet = ss.valid_date(meta.get("versendet_am", ""))
    if versendet and not any(e["art"] == "versendet" and e.get("status") in GUELTIG for e in nv["ereignisse"]):
        _, neu = km.ereignis_bauen(nv, slug, "versendet", versendet, {"typ": "frontmatter", "referenz": "vorgang.md versendet_am"}, "", None, "bestaetigt", jetzt, "migriert", "bestaetigt",
                                   vorgang=slug, beschreibung="aus versendet_am in vorgang.md", migriert=True, zeitangabe="angabe des nutzers")
        if neu:
            plan.append({"neu": "versendet", "aus": "versendet_am"})
    for nummer, zeile in enumerate(_verlauf_text(w, slug).splitlines(), 1):
        treffer = VERLAUF_STATUS.match(zeile)
        if not treffer or "Gmail-ID" in zeile or re.search(r"\(Ereignis [^)]*e-\d+\)|, bewerbung\.py \(", zeile):
            continue  # a line of a mail record or of this script has its own event already
        datum, alt, neu_status = treffer.group(1), treffer.group(2).strip(), treffer.group(3).strip()
        if alt not in ALLE or neu_status not in ALLE or ss.valid_date(datum) != datum:
            continue
        _, neu = km.ereignis_bauen(nv, slug, "statuswechsel", datum, {"typ": "verlauf", "referenz": f"vorgang.md Zeile {nummer}"}, "", None, "bestaetigt", jetzt, "migriert", "bestaetigt",
                                   vorgang=slug, beschreibung="aus einer Zeile von ## Verlauf", status_vorher=alt, status_nachher=neu_status, migriert=True, zeitangabe="datum der verlaufszeile")
        if neu:
            plan.append({"neu": "statuswechsel", "aus": f"Zeile {nummer}", "von": alt, "nach": neu_status})
    if plan and anwenden:
        km.speichere_nachverfolgung(w, slug, nv)
    return plan


def migrieren(w, slug, jetzt, anwenden):
    namen = [slug] if slug else sorted(km.alle_vorgaenge(w))
    if slug:
        km.vorgang_meta(w, slug)
    ergebnis = {}
    for name in namen:
        try:
            plan = migriere_vorgang(w, name, jetzt, anwenden)
        except Refused as error:
            ergebnis[name] = [{"fehler": error.meldung}]
            continue
        if plan:
            ergebnis[name] = plan
    return {"ok": True, "angewendet": anwenden, "vorgaenge": ergebnis, "anzahl": sum(len(v) for v in ergebnis.values()),
            "hinweis": "Nur ergänzt, nichts überschrieben; kein Ergebnis und kein Datum wurde erfunden." + ("" if anwenden else " Das war ein Probelauf: mit --ja anwenden.")}


# ---------------------------------------------------------------- CLI

WRITES = (("anlegen", None), ("ereignis", ("erfassen", "bestaetigen", "korrigieren", "verwerfen")), ("statuswechsel", None))


def build_parser():
    p = argparse.ArgumentParser(description="The result of an application (R-01).")
    p.add_argument("--konfiguration", default=os.path.join(ss.DEFAULT_WURZEL, "konfiguration.md"))
    p.add_argument("--jetzt")
    sub = p.add_subparsers(dest="befehl", required=True)
    a = sub.add_parser("anlegen")
    a.add_argument("--slug")
    a.add_argument("--firma", default="")
    a.add_argument("--stelle", default="")
    a.add_argument("--ref-nr")
    a.add_argument("--stellenquelle")
    a.add_argument("--weg", choices=("email", "portal", "post"))
    a.add_argument("--ja", action="store_true")
    f = sub.add_parser("finde")
    f.add_argument("--firma")
    f.add_argument("--status")
    f.add_argument("--ergebnis")
    f.add_argument("--ref-nr")
    f.add_argument("--text")
    f.add_argument("--abgeschlossen", action="store_true")
    for name in ("status", "historie"):
        sub.add_parser(name).add_argument("vorgang")
    for name in ("naechste", "pruefen"):
        c = sub.add_parser(name)
        c.add_argument("vorgang", nargs="?")
    e = sub.add_parser("ereignis")
    e.add_argument("aktion", choices=("erfassen", "bestaetigen", "korrigieren", "verwerfen"))
    e.add_argument("vorgang")
    e.add_argument("--id")
    e.add_argument("--art")
    e.add_argument("--eingetreten-am")
    e.add_argument("--termin")
    e.add_argument("--erinnerung")
    e.add_argument("--erinnerung-anlass", choices=km.ANLAESSE)
    e.add_argument("--beschreibung", default="")
    e.add_argument("--original", default="")
    e.add_argument("--quelle-typ", choices=QUELLEN)
    e.add_argument("--referenz", default="")
    e.add_argument("--bestaetigung", choices=BESTAETIGUNG)
    e.add_argument("--methode", choices=METHODEN)
    e.add_argument("--kanal")
    e.add_argument("--status-aendern", action="store_true")
    e.add_argument("--status-nach")
    e.add_argument("--grund", default="")
    e.add_argument("--datum")
    e.add_argument("--ja", action="store_true")
    s = sub.add_parser("statuswechsel")
    s.add_argument("vorgang")
    s.add_argument("--nach", required=True)
    s.add_argument("--grund", default="")
    s.add_argument("--ja", action="store_true")
    m = sub.add_parser("migrieren")
    m.add_argument("vorgang", nargs="?")
    m.add_argument("--ja", action="store_true")
    return p


def run(args):
    now = parse_time(args.jetzt) if args.jetzt else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    w = ss.find_wurzel(args.konfiguration)
    befehl, aktion = args.befehl, getattr(args, "aktion", None)
    schreibt = befehl in ("anlegen", "statuswechsel") or (befehl == "ereignis") or (befehl == "migrieren" and args.ja)
    if schreibt:
        km.schutz_nutzer(f"{befehl} {aktion or ''}".strip())
        if not args.ja:
            raise Refused("freigabe_fehlt", "Das ändert die Daten einer Bewerbung und ist eine Aussage der Nutzerin oder des Nutzers: ausdrückliches Ja (--ja) nötig")
    if befehl == "finde":
        return finde(w, now, args.firma, args.status, args.ergebnis, args.ref_nr, args.abgeschlossen, args.text)
    if befehl == "status":
        return ansicht(w, args.vorgang, now)
    if befehl == "historie":
        return historie(w, args.vorgang)
    if befehl == "naechste":
        namen = [args.vorgang] if args.vorgang else [n for n, m in km.alle_vorgaenge(w).items() if m.get("status") not in FINAL]
        if args.vorgang:
            km.vorgang_meta(w, args.vorgang)
        return {"ok": True, "schritte": {n: s for n in namen for s in [naechste_schritte(w, n, now)] if s}}
    if befehl == "pruefen":
        befunde = pruefe_alle(w, now, args.vorgang)
        zaehler = {g: sum(1 for b in befunde if b["grad"] == g) for g in ("Fehler", "Warnung", "Hinweis")}
        return {"ok": True, "befunde": befunde, "zaehler": zaehler, "hinweis": "Die Prüfung ändert nichts. Eine unbekannte optionale Angabe ist kein Fehler."}
    if befehl == "migrieren" and not args.ja:
        return migrieren(w, args.vorgang, now, False)
    with ss.exclusive(w, *km.LOCK):
        if befehl == "anlegen":
            return anlegen(w, args.slug, args.firma, args.stelle, {"ref_nr": args.ref_nr, "stellenquelle": args.stellenquelle, "weg": args.weg}, now)
        if befehl == "migrieren":
            return migrieren(w, args.vorgang, now, True)
        if befehl == "statuswechsel":
            return statuswechsel(w, args.vorgang, args.nach, args.grund, now)
        if aktion == "erfassen":
            return erfassen(w, args.vorgang, args.art or "", {k: getattr(args, k) for k in ("eingetreten_am", "termin", "erinnerung", "erinnerung_anlass", "beschreibung", "original", "quelle_typ", "referenz",
                                                                                      "bestaetigung", "methode", "kanal", "status_aendern", "status_nach")}, now)
        if aktion == "bestaetigen":
            return ereignis_bestaetigen(w, args.vorgang, args.id or "", now)
        return ereignis_aendern(w, args.vorgang, args.id or "", aktion, {"art": args.art, "datum": args.datum, "grund": args.grund}, now)


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
