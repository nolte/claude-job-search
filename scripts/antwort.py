#!/usr/bin/env python3
"""Reply drafts to messages of an employer and the guarded send (spec mail-verwaltung MV-31 to MV-35, R-02).

A draft is a file in the Vorgang folder, `antwort-NN.md`: a short header (version, Vorgang, replied-to message, channel, recipient, subject)
and the text. The approval of the workflow (`nachricht_senden`, WF-7) is bound to the hash of that whole file, so a change of the text, the
recipient, the channel, the subject or the version voids the approval. The script never sends: `adapter()` builds the function a
send integration registers in `workflow.ADAPTER`; none ships, and `workflow.py ausfuehren` answers `kein_adapter` until one is registered.

State:
  <wurzel>/<vorgang>/antwort-NN.md        the draft (what is approved is exactly this file)
  <wurzel>/<vorgang>/antworten.json       per draft: replied-to message, versions with hash, local state, the result of a send
  <wurzel>/<vorgang>/nachverfolgung.json  events of the course (`antwort_vorbereitet`, `antwort_zur_freigabe`, …; the R-01 history)
  <wurzel>/kommunikation/eingang.json    the replied-to message keeps the name of its drafts and a history line per step

Usage: antwort.py [--konfiguration PFAD] [--jetzt ISO] <befehl> ...
Commands: anlegen, zeige, aendern, vorlegen, verwerfen, liste.
Output is one JSON object. Exit code 0 ok, 2 ok=false, 3 refused, 1 blocker. Standard library only; no mail, HTTP or socket module.
"""

import argparse
import contextlib
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kommunikation as km  # noqa: E402
import stellensuche as ss  # noqa: E402
from grundlage_hash import sha256_file  # noqa: E402
from stellensuche import Blocker, Refused, atomic_write, clean_text, digest, load_json, parse_time, redact, stamp  # noqa: E402

DATEI = re.compile(r"antwort-(\d{2})\.md")
KANAELE = ("email",)
ADRESSE = re.compile(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
KOPF_FELDER = ("version", "vorgang", "in_antwort_auf", "kanal", "an", "betreff", "empfaenger_abweichend")
TEXT_MAX = 8000
BETREFF_MAX = 150
VERSIONEN_MAX = 20
OFFEN = re.compile(r"\[ERGÄNZEN[^\]]*\]")
ZUSTAENDE = ("entwurf", "wartet_auf_freigabe", "freigegeben", "abgelehnt", "gesendet", "versand_fehlgeschlagen", "versand_unklar", "verworfen")
VORLAGEN = ("termin_bestaetigen", "rueckfrage_beantworten", "unterlagen_nachreichen", "eingang_bestaetigen", "angebot_rueckfrage")


class NichtGesendet(Exception):
    """Raised by a provider that is sure nothing has left the machine."""


# ---------------------------------------------------------------- the draft file

def entwurf_pfad(w, slug, datei):
    if not DATEI.fullmatch(datei or ""):
        raise Refused("entwurf_unbekannt", f"{redact(datei, 40)} ist kein Entwurfsname (antwort-NN.md)")
    km.vorgang_pfad(w, slug)  # checks the name of the Vorgang
    return os.path.join(w, slug, datei)


def inhalt_hash(w, slug, datei):
    """The hash the workflow stores with an approval of `nachricht_senden` (`workflow.hash_von`): one file, `name=sha256`, digested."""
    pfad = entwurf_pfad(w, slug, datei)
    return digest(f"{datei}={sha256_file(pfad)}") if os.path.isfile(pfad) else ""


def schreibe_entwurf(pfad, kopf, text):
    zeilen = [f"{k}: {kopf[k]}" for k in KOPF_FELDER if kopf.get(k) not in (None, "")]
    atomic_text(pfad, "---\n" + "\n".join(zeilen) + "\n---\n" + text.strip("\n") + "\n")


def atomic_text(pfad, inhalt):
    temp = pfad + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(inhalt)
        os.replace(temp, pfad)
    except OSError as error:
        raise Refused("speichern_fehlgeschlagen", f"{os.path.basename(pfad)} nicht geschrieben: {redact(error)}")


def lies_entwurf(w, slug, datei):
    """-> (header dict, text). Strict: unknown keys, a second recipient, a line break in a value or a missing field are refused."""
    pfad = entwurf_pfad(w, slug, datei)
    if not os.path.isfile(pfad):
        raise Refused("entwurf_unbekannt", f"Es gibt {datei} im Vorgang {slug} nicht")
    with open(pfad, encoding="utf-8") as handle:
        roh = handle.read()
    treffer = re.fullmatch(r"---\n(.*?)\n---\n(.*)", roh, re.S)
    if not treffer:
        raise Refused("entwurf_ungueltig", f"{datei} hat keinen Kopf zwischen `---`-Zeilen")
    kopf = {}
    for zeile in treffer.group(1).split("\n"):
        schluessel, _, wert = zeile.partition(": ")
        if schluessel not in KOPF_FELDER or schluessel in kopf:
            raise Refused("entwurf_ungueltig", f"{datei}: Kopfzeile `{redact(schluessel, 30)}` ist unbekannt oder doppelt")
        kopf[schluessel] = wert.strip()
    fehlt = [k for k in KOPF_FELDER[:6] if not kopf.get(k)]
    if fehlt:
        raise Refused("entwurf_ungueltig", f"{datei}: Kopf ohne {', '.join(fehlt)}")
    if not re.fullmatch(r"\d{1,3}", kopf["version"]) or kopf["vorgang"] != slug:
        raise Refused("entwurf_ungueltig", f"{datei}: version oder vorgang im Kopf passt nicht")
    return kopf, treffer.group(2).strip("\n")


def pruefe_empfaenger(kopf, nachricht):
    """One address, in the form of an address, at the domain of the sender of the replied-to message unless the user marked it (MV-32 rule 3)."""
    an = kopf["an"]
    if not ADRESSE.fullmatch(an) or len(an) > 120:
        raise Refused("empfaenger_ungueltig", "Der Empfänger ist genau eine E-Mail-Adresse (keine Liste, kein Anzeigename, kein Zeilenumbruch)")
    if kopf["kanal"] not in KANAELE:
        raise Refused("kanal_nicht_unterstuetzt", f"Kanal `{redact(kopf['kanal'], 20)}` wird nicht unterstützt (nur {', '.join(KANAELE)})")
    domain, absender = an.split("@", 1)[1].lower(), (nachricht or {}).get("absender_domain", "")
    plausibel = bool(absender) and (domain == absender or domain.endswith("." + absender) or absender.endswith("." + domain))
    if not plausibel and kopf.get("empfaenger_abweichend") != "ja":
        raise Refused("empfaenger_unplausibel", f"Die Domain `{domain}` ist nicht die des Absenders der Nachricht (`{absender or '-'}`). "
                                                 "Wenn es richtig ist: --abweichender-empfaenger; die Freigabe zeigt es dann ausdrücklich")
    return an


# ---------------------------------------------------------------- the store per Vorgang

def antworten_pfad(w, slug):
    km.vorgang_meta(w, slug)
    return os.path.join(w, slug, "antworten.json")


def lade_antworten(w, slug):
    daten = load_json(antworten_pfad(w, slug), {"version": 1, "entwuerfe": {}})
    if daten.get("version") != 1 or not isinstance(daten.get("entwuerfe"), dict):
        raise Refused("speicher_ungueltig", f"{slug}/antworten.json hat kein bekanntes Format (version 1)")
    for datei, e in daten["entwuerfe"].items():
        if not DATEI.fullmatch(datei) or not isinstance(e, dict) or not {"nachricht", "status", "versionen"} <= set(e) or not isinstance(e["versionen"], list):
            raise Refused("speicher_ungueltig", f"{slug}/antworten.json: der Eintrag {redact(datei, 30)} ist unvollständig")
    return daten


def speichere_antworten(w, slug, daten):
    atomic_write(antworten_pfad(w, slug), daten)


def naechster_name(w, slug, daten):
    vorhanden = {int(m.group(1)) for name in os.listdir(os.path.join(w, slug)) for m in [DATEI.fullmatch(name)] if m} | \
                {int(DATEI.fullmatch(n).group(1)) for n in daten["entwuerfe"]}
    nummer = max(vorhanden, default=0) + 1
    if nummer > 99:
        raise Refused("entwurf_grenze", "Mehr als 99 Entwürfe in einem Vorgang")
    return f"antwort-{nummer:02d}.md"


def version_vermerken(eintrag, kopf, hash_wert, jetzt, von):
    eintrag["versionen"].append({"version": int(kopf["version"]), "hash": hash_wert, "am": stamp(jetzt), "von": von, "an": kopf["an"], "kanal": kopf["kanal"]})
    del eintrag["versionen"][:-VERSIONEN_MAX]


# ---------------------------------------------------------------- history: events of the course and the line at the message

def ereignis(w, slug, art, datei, jetzt, detail="", von="system", version=None, gesperrt=False):
    """Record a step of a reply in the R-01 history (`nachverfolgung.json`). The same step twice gives back the first (idempotent).

    `gesperrt`: the caller already holds the lock of the communication (the commands of this file do)."""
    with (contextlib.nullcontext() if gesperrt else ss.exclusive(w, *km.LOCK)):
        nv = km.lade_nachverfolgung(w, slug)
        eintrag = lade_antworten(w, slug)["entwuerfe"].get(datei, {})
        stand = version or (eintrag["versionen"][-1]["version"] if eintrag.get("versionen") else 0)
        hash_wert = inhalt_hash(w, slug, datei)[:12] if eintrag.get("versionen") else ""
        e, neu = km.ereignis_bauen(nv, slug, art, km.heute(jetzt), {"typ": "workflow", "referenz": f"{datei}#v{stand}:{art}"}, "", None, "bestaetigt", jetzt,
                                   "manuell", "bestaetigt" if von == "nutzer" else "automatisch", beschreibung=clean_text(detail, 160), entwurf=datei,
                                   entwurf_version=stand, inhalt_hash=hash_wert, nachricht_id=eintrag.get("nachricht"))
        if neu:
            km.speichere_nachverfolgung(w, slug, nv)
        vermerke(w, eintrag.get("nachricht"), jetzt, art, von, f"{datei} v{stand}: {detail}")
    return e


def vermerke(w, nachricht_id, jetzt, art, von, detail):
    """One line in the history of the replied-to message; a message that is gone from the queue (500 limit) is simply skipped."""
    if not nachricht_id:
        return
    try:
        daten = km.lade_eingang(w)
    except Refused:
        return
    n = daten["nachrichten"].get(nachricht_id)
    if n is not None:
        km.historie(n, jetzt, art, von, detail)
        km.speichere_eingang(w, daten)


# ---------------------------------------------------------------- derived state

def zustand(w, slug, datei, eintrag=None, daten_wf=None):
    """The state of a draft, read from the local store and the workflow task (never kept twice, so it cannot drift)."""
    eintrag = eintrag or lade_antworten(w, slug)["entwuerfe"].get(datei)
    if eintrag is None:
        raise Refused("entwurf_unbekannt", f"Es gibt {datei} im Vorgang {slug} nicht")
    versand = eintrag.get("versand") or {}
    if versand.get("status") == "gesendet":
        return "gesendet"
    if eintrag["status"] == "verworfen":
        return "verworfen"
    import workflow as wf  # noqa: PLC0415 - workflow imports this module for the history hooks
    try:
        task = (daten_wf or wf.lade(w))["aufgaben"].get(f"nachricht_senden:{slug}:{datei}")
    except Refused:
        task = None
    if task is None:
        return "versand_fehlgeschlagen" if versand.get("status") == "fehlgeschlagen" else "entwurf"
    status, entscheidung = task["status"], task["entscheidung"] or {}
    if status == wf.ERLEDIGT:
        return "gesendet"
    if status == wf.ABGEBROCHEN:
        return "abgelehnt" if entscheidung.get("art") == "abgelehnt" else "verworfen"
    if status == wf.EINGABE and task["extern_begonnen"]:
        return "versand_unklar"
    if status == wf.FEHLGESCHLAGEN:
        return "versand_fehlgeschlagen"
    if status in (wf.BEREIT, wf.LAEUFT) and wf.freigabe_gueltig(w, task):
        return "freigegeben"
    return "wartet_auf_freigabe"


def ansicht(w, slug, datei, mit_text=True):
    daten = lade_antworten(w, slug)
    eintrag = daten["entwuerfe"].get(datei)
    if eintrag is None:
        raise Refused("entwurf_unbekannt", f"Es gibt {datei} im Vorgang {slug} nicht")
    kopf, text = lies_entwurf(w, slug, datei)
    ergebnis = {"datei": datei, "vorgang": slug, "zustand": zustand(w, slug, datei, eintrag), "lokal": eintrag["status"], "kopf": kopf,
                "offene_punkte": OFFEN.findall(text), "inhalt_hash": inhalt_hash(w, slug, datei)[:12], "versionen": eintrag["versionen"],
                "versand": eintrag.get("versand"), "aufgabe": f"nachricht_senden:{slug}:{datei}"}
    if kopf.get("empfaenger_abweichend") == "ja":
        ergebnis["empfaenger_hinweis"] = "Der Empfänger liegt auf einer anderen Domain als der Absender der Nachricht; das steht so im Entwurf"
    if mit_text:
        ergebnis["text"] = text
    return ergebnis


# ---------------------------------------------------------------- templates (no invented content)

def bestaetigte(n):
    return {f["feld"]: f for f in n.get("extraktion", []) if f.get("bestaetigt")}


def entwurfstext(vorlage, n, meta):
    """Text from a template. Only facts the user has taken over (`bestaetigen --uebernehmen`) are used; every other point stays `[ERGÄNZEN: …]`."""
    fakten = bestaetigte(n)
    kontakt = fakten["kontakt_name"]["wert"] if "kontakt_name" in fakten else ""
    anrede = f"Sehr geehrte Damen und Herren, sehr geehrte(r) {kontakt}," if kontakt else "[ERGÄNZEN: Anrede]"
    stelle = meta.get("stelle") or "[ERGÄNZEN: Stelle]"
    dank = f"vielen Dank für Ihre Nachricht vom {n['datum']}"
    if vorlage == "termin_bestaetigen":
        termin = fakten.get("termin", {}).get("wert") or {}
        wann = " ".join(x for x in (termin.get("datum"), termin.get("uhrzeit"), termin.get("zeitzone") if termin.get("zeitzone") != "nicht genannt" else "") if x)
        mitte = (f"{dank}. Sie haben mir als Termin {wann} genannt." if wann else f"{dank}. [ERGÄNZEN: genannter Termin (nicht übernommen)]") + \
                "\n\n[ERGÄNZEN: Zusage, Gegenvorschlag oder Absage zum Termin, nur nach eigener Prüfung der Verfügbarkeit]"
    elif vorlage == "rueckfrage_beantworten":
        mitte = f"{dank}.\n\n[ERGÄNZEN: Antwort auf die Rückfrage]"
    elif vorlage == "unterlagen_nachreichen":
        punkte = fakten.get("unterlagen", {}).get("wert")
        liste = ", ".join(punkte) if isinstance(punkte, list) and punkte else "[ERGÄNZEN: angeforderte Unterlagen (nicht übernommen)]"
        mitte = f"{dank}. Sie haben um folgende Unterlagen gebeten: {liste}.\n\n[ERGÄNZEN: ob und wie die Unterlagen übermittelt werden; Dateianhänge sendet dieses Werkzeug nicht]"
    elif vorlage == "eingang_bestaetigen":
        mitte = f"{dank}. Ich bestätige den Eingang.\n\n[ERGÄNZEN: ggf. weitere organisatorische Hinweise]"
    elif vorlage == "angebot_rueckfrage":
        mitte = f"{dank} und für das Angebot.\n\n[ERGÄNZEN: Rückfrage zum Angebot; keine Zusage und keine Gehaltsangabe ohne eigene Entscheidung]"
    else:
        raise Refused("vorlage_unbekannt", f"Vorlage `{redact(vorlage, 30)}` ist nicht bekannt ({', '.join(VORLAGEN)})")
    return f"{anrede}\n\n{mitte}\n\nZur Stelle: {stelle}\n\nMit freundlichen Grüßen\n[ERGÄNZEN: Name]"


def betreff_zu(n):
    roh = re.sub(r"^(?:(?:re|aw|antw|fwd?|wg)\s*:\s*)+", "", n.get("betreff", ""), flags=re.I).strip()
    return clean_text("Re: " + roh, BETREFF_MAX)


# ---------------------------------------------------------------- commands

def anlegen(w, nachricht_id, optionen, jetzt):
    eingang = km.lade_eingang(w)
    n = km.hole(eingang, nachricht_id)
    if n["status"] not in ("bestaetigt", "korrigiert") or not n["vorgang"]:
        raise Refused("nachricht_nicht_bestaetigt", "Eine Antwort entsteht nur auf eine Nachricht, deren Zuordnung die Nutzerin oder der Nutzer bestätigt hat "
                                                    "(sonst könnte sie an die falsche Bewerbung gehen)")
    slug = n["vorgang"]
    meta = km.vorgang_meta(w, slug)
    daten = lade_antworten(w, slug)
    if not optionen.get("neu"):
        offen = [d for d, e in daten["entwuerfe"].items() if e["nachricht"] == n["id"] and zustand(w, slug, d, e) not in ("gesendet", "verworfen", "abgelehnt")]
        if offen:
            raise Refused("entwurf_existiert", f"Zu dieser Nachricht gibt es schon den offenen Entwurf {offen[0]}: ändern, verwerfen oder mit --neu einen weiteren anlegen")
    kanal = optionen.get("kanal") or "email"
    text = optionen.get("text")
    if optionen.get("vorlage"):
        if text:
            raise Refused("angaben_widersprechen", "Entweder --vorlage oder ein eigener Text")
        text = entwurfstext(optionen["vorlage"], n, meta)
    if not text or not text.strip():
        raise Refused("text_fehlt", "Ohne --vorlage oder Text (--text-datei, Standardeingabe) gibt es keinen Entwurf")
    if len(text) > TEXT_MAX:
        raise Refused("text_zu_lang", f"Der Text ist länger als {TEXT_MAX} Zeichen")
    kopf = {"version": "1", "vorgang": slug, "in_antwort_auf": n["id"], "kanal": kanal, "an": clean_text(optionen.get("an"), 120),
            "betreff": clean_text(optionen.get("betreff"), BETREFF_MAX) or betreff_zu(n)}
    if optionen.get("abweichender_empfaenger"):
        kopf["empfaenger_abweichend"] = "ja"
    pruefe_empfaenger(kopf, n)
    datei = naechster_name(w, slug, daten)
    pfad = entwurf_pfad(w, slug, datei)
    schreibe_entwurf(pfad, kopf, text)
    eintrag = {"nachricht": n["id"], "status": "entwurf", "erstellt": stamp(jetzt), "versionen": [], "versand": None}
    version_vermerken(eintrag, kopf, inhalt_hash(w, slug, datei), jetzt, "nutzer" if optionen.get("text") else "system")
    daten["entwuerfe"][datei] = eintrag
    speichere_antworten(w, slug, daten)
    n.setdefault("antworten", []).append(datei)
    km.historie(n, jetzt, "antwort_entwurf", "nutzer", f"{datei} v1")
    km.speichere_eingang(w, eingang)
    ereignis(w, slug, "antwort_vorbereitet", datei, jetzt, f"Entwurf auf Nachricht {n['id']}", "system", 1, gesperrt=True)
    return {"ok": True, **ansicht(w, slug, datei), "hinweis": "Ein Entwurf ist keine gesendete Nachricht. Nächster Schritt: prüfen, ggf. `aendern`, dann `vorlegen`."}


def aendern(w, slug, datei, optionen, jetzt):
    daten = lade_antworten(w, slug)
    eintrag = daten["entwuerfe"].get(datei)
    if eintrag is None:
        raise Refused("entwurf_unbekannt", f"Es gibt {datei} im Vorgang {slug} nicht")
    stand = zustand(w, slug, datei, eintrag)
    if stand in ("gesendet", "versand_unklar"):
        raise Refused("entwurf_gesperrt", f"{datei} ist {stand}: ein gesendeter Entwurf wird nicht geändert und nicht stillschweigend erneut gesendet; lege einen neuen an")
    if stand == "verworfen":
        raise Refused("entwurf_gesperrt", f"{datei} ist verworfen")
    kopf, text = lies_entwurf(w, slug, datei)
    n = km.hole(km.lade_eingang(w), eintrag["nachricht"])
    if optionen.get("text") is not None:
        text = optionen["text"]
    if optionen.get("an"):
        kopf["an"] = clean_text(optionen["an"], 120)
    if optionen.get("betreff"):
        kopf["betreff"] = clean_text(optionen["betreff"], BETREFF_MAX)
    if optionen.get("abweichender_empfaenger"):
        kopf["empfaenger_abweichend"] = "ja"
    elif optionen.get("an"):
        kopf.pop("empfaenger_abweichend", None)
    if not text.strip() or len(text) > TEXT_MAX:
        raise Refused("text_ungueltig", f"Der Text ist leer oder länger als {TEXT_MAX} Zeichen")
    pruefe_empfaenger(kopf, n)
    pfad = entwurf_pfad(w, slug, datei)
    alt_kopf, alt_text = lies_entwurf(w, slug, datei)
    if ({k: v for k, v in kopf.items() if k != "version"}, text.strip("\n")) == ({k: v for k, v in alt_kopf.items() if k != "version"}, alt_text):
        raise Refused("nichts_geaendert", "Der Entwurf ist unverändert")
    kopf["version"] = str(int(kopf["version"]) + 1)
    schreibe_entwurf(pfad, kopf, text)
    version_vermerken(eintrag, kopf, inhalt_hash(w, slug, datei), jetzt, "nutzer")
    speichere_antworten(w, slug, daten)
    ereignis(w, slug, "antwort_vorbereitet", datei, jetzt, f"Version {kopf['version']}", "nutzer", int(kopf["version"]), gesperrt=True)
    return {"ok": True, **ansicht(w, slug, datei),
            "hinweis": "Eine früher erteilte Freigabe gilt für diese Fassung nicht mehr; sie wird im Workflow neu angefordert (`workflow.py freigeben`)."}


def vorlegen(w, slug, datei, jetzt):
    daten = lade_antworten(w, slug)
    eintrag = daten["entwuerfe"].get(datei)
    if eintrag is None:
        raise Refused("entwurf_unbekannt", f"Es gibt {datei} im Vorgang {slug} nicht")
    stand = zustand(w, slug, datei, eintrag)
    if stand in ("gesendet", "versand_unklar", "verworfen", "abgelehnt"):
        raise Refused("entwurf_gesperrt", f"{datei} ist {stand}")
    kopf, text = lies_entwurf(w, slug, datei)
    offen = OFFEN.findall(text)
    if offen:
        raise Refused("offene_punkte", f"{len(offen)} offene Stelle(n) im Text ({', '.join(offen[:3])}): erst ausfüllen, dann vorlegen")
    pruefe_empfaenger(kopf, km.hole(km.lade_eingang(w), eintrag["nachricht"]))
    if eintrag["status"] != "vorgelegt":
        eintrag["status"] = "vorgelegt"
        speichere_antworten(w, slug, daten)
        ereignis(w, slug, "antwort_zur_freigabe", datei, jetzt, f"Version {kopf['version']} an {kopf['an']}", "system", int(kopf["version"]), gesperrt=True)
    return {"ok": True, **ansicht(w, slug, datei),
            "weiter": f"`workflow.py starten`/`laufen` legt die Aufgabe `nachricht_senden:{slug}:{datei}` an; die Freigabe erteilst du dort mit "
                      f"`workflow.py freigeben nachricht_senden:{slug}:{datei} --ja` für genau diese Fassung. Gesendet wird nur mit registriertem Adapter."}


def verwerfen(w, slug, datei, grund, jetzt):
    daten = lade_antworten(w, slug)
    eintrag = daten["entwuerfe"].get(datei)
    if eintrag is None:
        raise Refused("entwurf_unbekannt", f"Es gibt {datei} im Vorgang {slug} nicht")
    stand = zustand(w, slug, datei, eintrag)
    if stand in ("gesendet", "versand_unklar"):
        raise Refused("entwurf_gesperrt", f"{datei} ist {stand}")
    if stand in ("wartet_auf_freigabe", "freigegeben", "versand_fehlgeschlagen"):
        raise Refused("aufgabe_offen", f"Zu {datei} gibt es die Aufgabe nachricht_senden:{slug}:{datei}: im Workflow mit `ablehnen` (Freigabe verweigern) beenden")
    if not clean_text(grund, 200):
        raise Refused("grund_fehlt", "--grund fehlt")
    eintrag["status"] = "verworfen"
    eintrag["verworfen"] = {"am": stamp(jetzt), "grund": clean_text(grund, 200)}
    speichere_antworten(w, slug, daten)
    vermerke(w, eintrag["nachricht"], jetzt, "antwort_verworfen", "nutzer", f"{datei}: {grund}")
    return {"ok": True, "datei": datei, "zustand": "verworfen"}


def vorgelegt(w, slug):
    """The drafts the user presented for approval and that are still open: the planner makes a `nachricht_senden` task of each."""
    try:
        daten = lade_antworten(w, slug)
    except Refused:
        return []
    return sorted(d for d, e in daten["entwuerfe"].items() if e["status"] == "vorgelegt" and not (e.get("versand") or {}).get("status") == "gesendet")


def liste(w, slug):
    daten = lade_antworten(w, slug)
    return [{"datei": d, "nachricht": e["nachricht"], "zustand": zustand(w, slug, d, e), "version": e["versionen"][-1]["version"] if e["versionen"] else 0}
            for d, e in sorted(daten["entwuerfe"].items())]


# ---------------------------------------------------------------- the send: the function an integration registers

def adapter(w, anbieter):
    """-> function(task, freigabe) for `workflow.ADAPTER["nachricht_senden"]`.

    `anbieter` has `kanaele` and `senden(an, betreff, text, kanal, schluessel) -> {"id": <id the provider reports>}`, and raises `NichtGesendet`
    when it is sure that nothing left. The function sends only the file the approval covers, once, and reports `gesendet` only on an id from
    the provider (MV-34). A second call for a draft that was sent does not call the provider again."""
    def senden(task, freigabe):
        slug, datei = task["bezug"]["vorgang"], task["bezug"]["datei"]
        jetzt = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        sicher_nein = {"gesendet": False, "sicher": True}
        if not freigabe or freigabe.get("art") != "erteilt" or inhalt_hash(w, slug, datei) != freigabe.get("kontext_hash"):
            return sicher_nein | {"grund": "Die Freigabe gilt nicht für den Inhalt, wie er jetzt ist"}
        with ss.exclusive(w, *km.LOCK):
            daten = lade_antworten(w, slug)
            eintrag = daten["entwuerfe"].get(datei)
            if eintrag is None:
                return sicher_nein | {"grund": "Der Entwurf ist nicht registriert"}
            if (eintrag.get("versand") or {}).get("status") == "gesendet":
                return {"gesendet": True, "sicher": True, "beleg": eintrag["versand"]["beleg"], "bereits_gesendet": True}
            try:
                kopf, text = lies_entwurf(w, slug, datei)
                n = km.hole(km.lade_eingang(w), eintrag["nachricht"])
                pruefe_empfaenger(kopf, n)
                if OFFEN.search(text):
                    raise Refused("offene_punkte", "Der Text hat offene Stellen")
                if kopf["kanal"] not in getattr(anbieter, "kanaele", ()):
                    raise Refused("kanal_nicht_unterstuetzt", f"Der Anbieter kann den Kanal {kopf['kanal']} nicht")
            except Refused as error:
                versand_vermerken(w, slug, daten, datei, "fehlgeschlagen", jetzt, error.code, "")
                return sicher_nein | {"grund": error.meldung}
            schluessel = digest(slug, datei, freigabe["kontext_hash"])
            try:
                antwort = anbieter.senden(kopf["an"], kopf["betreff"], text, kopf["kanal"], schluessel)
            except NichtGesendet as error:
                versand_vermerken(w, slug, daten, datei, "fehlgeschlagen", jetzt, "anbieter_nicht_gesendet", "")
                return sicher_nein | {"grund": redact(error)}
            beleg = clean_text(antwort.get("id") if isinstance(antwort, dict) else "", 200)
            if not beleg:
                raise ValueError("Der Anbieter meldet keine Nachrichten-ID: ob gesendet wurde, ist unklar")  # the workflow keeps it unclear
            versand_vermerken(w, slug, daten, datei, "gesendet", jetzt, "", beleg, hash_wert=freigabe["kontext_hash"])
        return {"gesendet": True, "sicher": True, "beleg": beleg}
    return senden


def versand_vermerken(w, slug, daten, datei, status, jetzt, fehler, beleg, hash_wert=""):
    """Write the result of an attempt. A failure to write after a send is not allowed to hide the send: it is reported by the caller's return."""
    eintrag = daten["entwuerfe"][datei]
    alt = eintrag.get("versand") or {}
    eintrag["versand"] = {"status": status, "am": stamp(jetzt), "beleg": beleg, "fehler": fehler, "hash": hash_wert, "versuche": alt.get("versuche", 0) + 1}
    try:
        speichere_antworten(w, slug, daten)
    except Refused:
        pass


# ---------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(description="Reply drafts and the guarded send (R-02).")
    p.add_argument("--konfiguration", default=os.path.join(ss.DEFAULT_WURZEL, "konfiguration.md"))
    p.add_argument("--jetzt")
    sub = p.add_subparsers(dest="befehl", required=True)
    a = sub.add_parser("anlegen")
    a.add_argument("nachricht")
    a.add_argument("--an", required=True, help="the recipient address: one address, chosen by the user")
    a.add_argument("--vorlage", choices=VORLAGEN)
    a.add_argument("--text-datei", help="own text; stdin when neither --vorlage nor this is given")
    a.add_argument("--betreff")
    a.add_argument("--kanal", default="email")
    a.add_argument("--abweichender-empfaenger", action="store_true")
    a.add_argument("--neu", action="store_true", help="another draft although an open one exists for the message")
    for name in ("zeige", "vorlegen"):
        s = sub.add_parser(name)
        s.add_argument("vorgang")
        s.add_argument("datei")
    c = sub.add_parser("aendern")
    c.add_argument("vorgang")
    c.add_argument("datei")
    c.add_argument("--text-datei")
    c.add_argument("--an")
    c.add_argument("--betreff")
    c.add_argument("--abweichender-empfaenger", action="store_true")
    v = sub.add_parser("verwerfen")
    v.add_argument("vorgang")
    v.add_argument("datei")
    v.add_argument("--grund", default="")
    sub.add_parser("liste").add_argument("vorgang")
    return p


USER_ONLY = ("anlegen", "aendern", "vorlegen", "verwerfen")


def lies_text(pfad):
    if pfad:
        with open(pfad, encoding="utf-8") as handle:
            return handle.read(TEXT_MAX + 1)
    return sys.stdin.read(TEXT_MAX + 1)


def run(args):
    now = parse_time(args.jetzt) if args.jetzt else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    w = ss.find_wurzel(args.konfiguration)
    befehl = args.befehl
    if befehl in USER_ONLY:
        km.schutz_nutzer(befehl)
    if befehl == "zeige":
        return {"ok": True, **ansicht(w, args.vorgang, args.datei)}
    if befehl == "liste":
        return {"ok": True, "entwuerfe": liste(w, args.vorgang)}
    with ss.exclusive(w, *km.LOCK):
        if befehl == "anlegen":
            text = None if args.vorlage else lies_text(args.text_datei)
            return anlegen(w, args.nachricht, {"an": args.an, "vorlage": args.vorlage, "text": text, "betreff": args.betreff, "kanal": args.kanal,
                                               "abweichender_empfaenger": args.abweichender_empfaenger, "neu": args.neu}, now)
        if befehl == "aendern":
            text = lies_text(args.text_datei) if args.text_datei else None
            return aendern(w, args.vorgang, args.datei, {"text": text, "an": args.an, "betreff": args.betreff,
                                                         "abweichender_empfaenger": args.abweichender_empfaenger}, now)
        if befehl == "vorlegen":
            return vorlegen(w, args.vorgang, args.datei, now)
        return verwerfen(w, args.vorgang, args.datei, args.grund, now)


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
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result.get("ok") is False else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
