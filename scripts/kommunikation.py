#!/usr/bin/env python3
"""Communication and follow-up of an application after the dispatch (spec mail-verwaltung MV-18 to MV-27, A-02).

Reads messages that a connector (or the user) hands over as plain JSON, assigns them to a Vorgang, classifies the mail type
and prepares proposals. Nothing is taken over without the user: a proposal becomes a line in `## Verlauf` of `vorgang.md`,
a change of `status`, a structured event and a Wiedervorlage only through `bestaetigen`, which needs the hash of the exact
proposal, `--ja` and an interactive session. The script sends nothing, opens no network connection, reads no mailbox and
writes nothing outside the Wurzel.

State:
  <wurzel>/kommunikation/eingang.json      messages as references with the proposal for each (no full mail text)
  <wurzel>/<vorgang>/nachverfolgung.json   confirmed events (structured counterpart of the Verlauf line) and Wiedervorlagen
  <wurzel>/<vorgang>/vorgang.md            status and `## Verlauf` stay the one history of an application (LS-6)

Usage: kommunikation.py [--konfiguration PFAD] [--jetzt ISO] <befehl> ...
Commands: verarbeiten, liste, zeige, zuweisen, bestaetigen, verwerfen, wiedervorlage, nachfass.
Input of `verarbeiten` (file or stdin): a JSON list of {"id", "thread_id", "von", "betreff", "datum", "text", "anhaenge"}.
Output is one JSON object. Exit code 0 ok, 2 ok=false, 3 refused, 1 blocker. Standard library only.
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
from qualitaet import unbeaufsichtigt  # noqa: E402
from stellensuche import Blocker, Refused, atomic_write, clean_text, digest, fold, load_json, parse_time, redact, stamp  # noqa: E402

KUERZEL = re.compile(r"[a-z0-9][a-z0-9-]*")
LOCK = ("kommunikation", ".kommunikation.lock", "die Kommunikation")
SCHEMA = 1
ORIGINAL_MAX = 240
BETREFF_MAX = 120
NACHRICHTEN_MAX = 500  # references kept in eingang.json; handled ones are dropped first

# the status values of LS-6 rule 2 in the order of a course after the dispatch (MV-7.4), and the final ones
VERLAUF_REIHE = ("versendet", "rückmeldung", "gespräch", "angebot", "verhandlung")
ENDSTATUS = ("zusage", "absage", "abgelehnt", "zurückgezogen", "ohne Antwort")

# Mail types of MV-3.2 plus the two the requirements ask for. rule: (strong patterns, weak patterns)
MAILTYPEN = {
    "eingangsbestaetigung": ("Eingangsbestätigung", None, "eingangsbestaetigung", (
        r"eingangsbest(ä|ae)tigung|best(ä|ae)tigen (wir |hiermit )?(den )?eingang|ihre bewerbung (ist )?(bei uns )?eingegangen|haben ihre bewerbung(sunterlagen)? erhalten|received your application",
        r"vielen dank für ihre bewerbung|vielen dank für ihr interesse")),
    "einladung": ("Einladung", "gespräch", "gespraechseinladung", (
        r"einladung|laden sie .{0,60} ein|zum (vorstellungs)?gespräch einladen|vorstellungsgespräch|invite you|interview",
        r"gespräch|termin")),
    "angebot": ("Angebot", "angebot", "angebot", (
        r"vertragsangebot|(unser|das) angebot|job offer|offer you the position|arbeitsvertrag", r"angebot")),
    "absage": ("Absage", "absage", "absage", (
        r"absage|bedauer\w*|nicht berücksichtigen|nicht weiter\w*|andere[nr]? (kandidat|bewerber)\w*|regret to inform|unfortunately,? we", r"leider")),
    "zusage": ("Zusage", "zusage", "einstellung", (
        r"zusage|herzlich willkommen im team|freuen uns,? ihnen .{0,60}einstellung", None)),
    "rueckfrage": ("Rückfrage", "rückmeldung", "rueckfrage", (
        r"rückfrage|nachreichen|bitte (senden|schicken|reichen) sie|noch (folgende|fehlende) unterlagen", r"\?")),
    "gespraechsfeedback": ("Gesprächsfeedback", None, "gespraechsfeedback", (
        r"feedback zum gespräch|nach unserem gespräch|vielen dank für das (gestrige |heutige )?gespräch", r"feedback")),
}
ARTEN = tuple(v[2] for v in MAILTYPEN.values()) + (
    "kontaktaufnahme", "gespraech", "technisches_gespraech", "assessment", "weitere_phase", "absage_nach_unterlagen",
    "absage_nach_gespraech", "absage_nach_assessment", "zurueckgezogen")
POSITIV = ("eingangsbestaetigung", "kontaktaufnahme", "gespraechseinladung", "gespraech", "technisches_gespraech", "assessment",
           "weitere_phase", "angebot", "einstellung")
NEGATIV = ("absage", "absage_nach_unterlagen", "absage_nach_gespraech", "absage_nach_assessment", "zurueckgezogen")
ANLAESSE = ("erwartete_rueckmeldung", "nachfassen", "gespraechsvorbereitung", "gespraechsnachbereitung", "offene_rueckfrage", "angebot_pruefen")
FOLGE_ANLASS = {"eingangsbestaetigung": "erwartete_rueckmeldung", "einladung": "gespraechsvorbereitung", "rueckfrage": "offene_rueckfrage",
                "angebot": "angebot_pruefen", "gespraechsfeedback": "gespraechsnachbereitung"}
GEWISSHEIT = ("eindeutig", "wahrscheinlich", "unklar", "nicht_zuordenbar")
NACHRICHT_STATUS = ("vorgeschlagen", "bestaetigt", "korrigiert", "verworfen")
FREIMAIL = {"gmail.com", "googlemail.com", "gmx.de", "gmx.net", "web.de", "outlook.com", "hotmail.com", "t-online.de", "yahoo.com", "icloud.com"}
NEWSLETTER = re.compile(r"unsubscribe|abmelden|newsletter|abbestellen", re.IGNORECASE)
ABSENDER_HINWEIS = re.compile(r"^(?:karriere|recruit\w*|personal|bewerbung\w*|talent\w*|jobs?|hr|career\w*)$", re.IGNORECASE)
RECHTSFORM = {"gmbh", "ag", "se", "kg", "ug", "mbh", "ohg", "gbr", "ev", "kgaa", "inc", "ltd", "llc", "co", "gesmbh", "sa", "bv", "nv"}
BETRAG = re.compile(r"(?i)\d[\d.,\s]*\s*(?:€|eur\b|euro\b|k\b)(?:\s*(?:brutto|netto))?|\b(?:brutto|netto)\b[^.]{0,30}\d[\d.,]*")
DATUM_IM_TEXT = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(20\d{2})\b|\b(20\d{2})-(\d{2})-(\d{2})\b")
MIN_QUELLE = 3

# feedback categories of a refusal or a feedback (A-06 11.1); extensible, a stated reason is a hint, never a finding
KATEGORIEN = (
    ("beruf_erfahrung", "Berufserfahrung", r"mehr (berufs)?erfahrung|erfahrung(en)? (im|in|mit|bei)|einschlägige erfahrung"),
    ("projekt_erfahrung", "Projekterfahrung", r"projekterfahrung|projekt(e)? (im|in)"),
    ("technische_kenntnisse", "technische Kenntnisse", r"technische (kenntnisse|skills)|fachkenntnisse"),
    ("zertifizierungen", "Zertifizierungen", r"zertifi\w+"),
    ("fuehrungserfahrung", "Führungserfahrung", r"führungserfahrung|personalverantwortung|führungsrolle"),
    ("kommunikation", "Kommunikation", r"kommunikation\w*"),
    ("sprachkenntnisse", "Sprachkenntnisse", r"(deutsch|englisch)kenntnisse|sprachkenntnisse"),
    ("verfuegbarkeit", "Verfügbarkeit", r"verfügbar\w*|eintrittstermin|kündigungsfrist"),
    ("gehaltsvorstellung", "Gehaltsvorstellungen", r"gehaltsvorstellung\w*|gehalt\w*"),
    ("organisatorisch", "organisatorische Gründe", r"stelle (wurde )?(intern )?(besetzt|gestrichen)|organisatorisch\w*|stellenplan|budget"),
    ("anderer_kandidat", "andere Bewerber bevorzugt", r"andere[nr]? (kandidat|bewerber)\w*|für (einen|eine) andere\w+ entschieden"),
)
KATEGORIE_FORM = re.compile(r"[a-z][a-z0-9_]{1,40}")


# ---------------------------------------------------------------- small helpers

def heute(now):
    return now.astimezone().date().isoformat()


def vorgang_pfad(w, slug):
    if not KUERZEL.fullmatch(slug or ""):
        raise Refused("vorgang_unbekannt", f"{redact(slug, 60)} ist kein Vorgangsname (a-z, 0-9, -)")
    return os.path.join(w, slug, "vorgang.md")


def vorgang_meta(w, slug):
    meta = ss.vorgang_meta(vorgang_pfad(w, slug))
    if meta is None:
        raise Refused("vorgang_unbekannt", f"Kein Vorgang {redact(slug, 60)} mit vorgang.md in der Wurzel")
    return meta


def alle_vorgaenge(w):
    ergebnis = {}
    for name in sorted(os.listdir(w)) if os.path.isdir(w) else []:
        meta = ss.vorgang_meta(os.path.join(w, name, "vorgang.md")) if KUERZEL.fullmatch(name) else None
        if meta is not None:
            ergebnis[name] = meta
    return ergebnis


def schutz_nutzer(befehl):
    if unbeaufsichtigt():
        raise Refused("nur_interaktiv", f"{befehl} ist in einer unbeaufsichtigten Sitzung nicht erlaubt: nur die Nutzerin oder der Nutzer entscheidet")


def kern(firma):
    teile = [t for t in re.findall(r"[a-z0-9]+", fold(firma or "")) if t not in RECHTSFORM]
    return " ".join(teile)


def domain_von(adresse):
    treffer = re.search(r"@([A-Za-z0-9.-]+\.[A-Za-z]{2,})", adresse or "")
    return treffer.group(1).lower() if treffer else ""


def basis_label(domain):
    """The name part of a domain without a legal form: `beispiel-ag.example` -> `beispiel`."""
    teile = domain.split(".")
    name = teile[-2] if len(teile) >= 2 else domain
    return "".join(t for t in name.split("-") if t not in RECHTSFORM) or name


def website_domain(w, slug_firma):
    pfad = os.path.join(w, "firmen", slug_firma + ".md")
    return domain_von("@" + re.sub(r"^https?://(www\.)?", "", ss.read_frontmatter(pfad).get("website", "")).split("/")[0]) if os.path.isfile(pfad) else ""


def schwaerze(text):
    """The text of a stored quote: single line, no credentials, no amounts (MV-7.3: salary and terms stay out)."""
    return BETRAG.sub("[Betrag entfernt]", redact(text, 2000))


# ---------------------------------------------------------------- stores

def eingang_pfad(w):
    return os.path.join(w, "kommunikation", "eingang.json")


def lade_eingang(w):
    daten = load_json(eingang_pfad(w), {"version": SCHEMA, "nachrichten": {}})
    if daten.get("version") != SCHEMA or not isinstance(daten.get("nachrichten"), dict):
        raise Refused("speicher_ungueltig", "kommunikation/eingang.json hat kein bekanntes Format (version 1)")
    for nid, n in daten["nachrichten"].items():
        if not isinstance(n, dict) or n.get("id") != nid or n.get("status") not in NACHRICHT_STATUS or not isinstance(n.get("vorschlag"), dict):
            raise Refused("speicher_ungueltig", f"Die Nachricht {redact(nid, 60)} in eingang.json ist unvollständig")
    return daten


def speichere_eingang(w, daten):
    nachrichten = daten["nachrichten"]
    if len(nachrichten) > NACHRICHTEN_MAX:  # keep the open ones; the oldest handled references go first
        erledigt = sorted((n for n in nachrichten.values() if n["status"] != "vorgeschlagen"), key=lambda n: n["erfasst"])
        for n in erledigt[:len(nachrichten) - NACHRICHTEN_MAX]:
            del nachrichten[n["id"]]
    atomic_write(eingang_pfad(w), daten)


def nachverfolgung_pfad(w, slug):
    return os.path.join(w, slug, "nachverfolgung.json")


def lade_nachverfolgung(w, slug):
    daten = load_json(nachverfolgung_pfad(w, slug), {"version": SCHEMA, "ereignisse": [], "wiedervorlagen": []})
    if daten.get("version") != SCHEMA or not isinstance(daten.get("ereignisse"), list) or not isinstance(daten.get("wiedervorlagen"), list):
        raise Refused("speicher_ungueltig", f"{slug}/nachverfolgung.json hat kein bekanntes Format (version 1)")
    for e in daten["ereignisse"]:
        if not isinstance(e, dict) or not {"id", "art", "status"} <= set(e):
            raise Refused("speicher_ungueltig", f"{slug}/nachverfolgung.json: ein Ereignis ist unvollständig")
    for r in daten["wiedervorlagen"]:
        if not isinstance(r, dict) or not {"id", "anlass", "faellig", "status"} <= set(r):
            raise Refused("speicher_ungueltig", f"{slug}/nachverfolgung.json: eine Wiedervorlage ist unvollständig")
    return daten


def speichere_nachverfolgung(w, slug, daten):
    atomic_write(nachverfolgung_pfad(w, slug), daten)


# ---------------------------------------------------------------- assignment (MV-6)

def merkmale(w, slug, meta, nachricht, bekannt):
    """-> list of (merkmal, stark, grund). `bekannt` holds the confirmed messages: threads and sender domains of this Vorgang."""
    text = fold(nachricht["betreff"] + " " + nachricht.get("text", ""))
    gefunden = []
    ref = fold(meta.get("ref_nr", "")).strip()
    if ref and re.search(rf"(?<![a-z0-9]){re.escape(ref)}(?![a-z0-9])", text):
        gefunden.append(("ref_nr", True, "Referenznummer der Stellenanzeige"))
    domain, firma = nachricht["domain"], kern(meta.get("firma", ""))
    firmen_slug = ss.slug(meta.get("firma", ""))
    bekannte_domains = {m.get("absender_domain") for m in bekannt if m.get("vorgang") == slug and m["status"] in ("bestaetigt", "korrigiert")}
    if domain and domain not in FREIMAIL:
        label = basis_label(domain)
        if (firma and label == firma.replace(" ", "")) or domain in bekannte_domains or domain == website_domain(w, firmen_slug):
            gefunden.append(("absender", True, "Absenderdomain gehört zur Firma oder zu einem bekannten Kontakt"))
    if nachricht.get("thread_id") and any(m.get("thread_id") == nachricht["thread_id"] and m.get("vorgang") == slug
                                          and m["status"] in ("bestaetigt", "korrigiert") for m in bekannt):
        gefunden.append(("thread", True, "Thread einer bereits zugeordneten Nachricht"))
    if firma and re.search(rf"(?<![a-z0-9]){re.escape(firma)}(?![a-z0-9])", text):
        gefunden.append(("firma", False, "Firmenname im Text"))
    stelle = fold(meta.get("stelle", "")).strip()
    if stelle and len(stelle) >= 8 and stelle in text:
        gefunden.append(("stelle", False, "Stellenbezeichnung im Text"))
    return gefunden


def ordne_zu(w, vorgaenge, nachricht, bekannt):
    """-> (vorgang or None, gewissheit, kandidaten). Several candidates are never decided by the script (MV-6.3)."""
    kandidaten = []
    for slug, meta in vorgaenge.items():
        gefunden = merkmale(w, slug, meta, nachricht, bekannt)
        if gefunden:
            kandidaten.append({"vorgang": slug, "merkmale": [g[0] for g in gefunden], "gruende": [g[2] for g in gefunden],
                               "stark": any(g[1] for g in gefunden)})
    if not kandidaten:
        return None, "nicht_zuordenbar", []
    if len(kandidaten) > 1:
        return None, "unklar", kandidaten
    k = kandidaten[0]
    return k["vorgang"], "eindeutig" if k["stark"] or len(k["merkmale"]) >= 2 else "wahrscheinlich", kandidaten


# ---------------------------------------------------------------- classification (MV-3.2, MV-5)

def klassifiziere(nachricht):
    """-> (typ, gewissheit, quelle, treffer). Fixed patterns, no model: the same mail gives the same answer."""
    text = fold(nachricht["betreff"] + " . " + nachricht.get("text", ""))
    stark, schwach = {}, {}
    for typ, (_, _, _, (p_stark, p_schwach)) in MAILTYPEN.items():
        s = re.search(fold(p_stark), text) if p_stark else None
        if s:
            stark[typ] = s.group(0)
        elif p_schwach and re.search(fold(p_schwach), text):
            schwach[typ] = re.search(fold(p_schwach), text).group(0)
    if len(stark) > 1:
        return "unbekannt", "unklar", "regel:widerspruch " + "+".join(sorted(stark)), stark
    if len(stark) == 1:
        typ = next(iter(stark))
        return typ, "eindeutig", f"regel:{typ}", stark
    if len(schwach) == 1:
        typ = next(iter(schwach))
        return typ, "wahrscheinlich", f"regel:{typ}:schwach", schwach
    return "unbekannt", "unklar", "regel:kein_treffer" if not schwach else "regel:widerspruch " + "+".join(sorted(schwach)), schwach


def satz_mit(text, treffer):
    """The sentence of the original that carries the decisive phrase: a literal part of the message, cut to a short quote."""
    saetze = re.split(r"(?<=[.!?])\s+|\n+", text or "")
    for satz in saetze:
        if treffer and re.search(re.escape(treffer), fold(satz)):
            return schwaerze(satz)[:ORIGINAL_MAX]
    return schwaerze(saetze[0] if saetze else "")[:ORIGINAL_MAX]


def deute_feedback(typ, original):
    """The interpretation of a refusal or a feedback. A reason that is not stated stays `unbekannt`; a stated one is a hint with low certainty."""
    if typ not in ("absage", "gespraechsfeedback"):
        return None
    fl = fold(original)
    for schluessel, bezeichnung, muster in KATEGORIEN:
        if re.search(fold(muster), fl):
            return {"kategorie": schluessel, "bezeichnung": bezeichnung, "thema": "", "aussage": "", "sicherheit": "niedrig", "grund_genannt": True,
                    "hinweis": "Muster im Wortlaut gefunden; keine bestätigte Qualifikationslücke"}
    return {"kategorie": "unbekannt" if typ == "absage" else "allgemein", "bezeichnung": "unbekannter Grund" if typ == "absage" else "allgemein",
            "thema": "", "aussage": "", "sicherheit": "niedrig", "grund_genannt": False,
            "hinweis": "kein Grund genannt: keine fachliche Schwäche und keine Dokumentenqualität als Ursache ableiten"}


# ---------------------------------------------------------------- the proposal (MV-7)

def status_vorschlag(aktuell, ziel):
    """-> (neuer Status or None, Grund). MV-7.4: only after the user stated the dispatch, only forward, never after a final status."""
    if ziel is None:
        return None, "für diesen Mailtyp ist keine Statusänderung vorgesehen"
    if aktuell in ENDSTATUS:
        return None, f"der Vorgang hat schon den Endstatus {aktuell}"
    if aktuell not in VERLAUF_REIHE:
        return None, "der Versand ist nicht eingetragen (S7 fehlt): die Zeile wird ohne Statusänderung vorgeschlagen"
    if ziel in ENDSTATUS:
        return ziel, ""
    if VERLAUF_REIHE.index(ziel) > VERLAUF_REIHE.index(aktuell):
        return ziel, ""
    return None, f"{ziel} liegt nicht nach {aktuell}: kein Schritt zurück"


def baue_vorschlag(w, nachricht, slug, typ, jetzt_status=None):
    """The exact lines that would be written, the status change, the event and the follow-up. Computed from the state now."""
    meta = vorgang_meta(w, slug) if slug else {}
    aktuell = (meta or {}).get("status", "")
    label, ziel, art, _ = MAILTYPEN[typ] if typ in MAILTYPEN else ("Mail", None, "kontaktaufnahme", None)
    neu, grund = status_vorschlag(aktuell, ziel) if slug else (None, "kein Vorgang")
    datum = nachricht["datum"]
    zeilen = []
    if slug:
        zeilen.append(f"- {datum}: Mail {label} ({'Anhang vorhanden: ' + ', '.join(nachricht['anhaenge']) + '; ' if nachricht['anhaenge'] else ''}"
                      f"Gmail-ID {nachricht['id']}, Thread {nachricht['thread_id'] or '-'})")
        if neu:
            zeilen.append(f"- {datum}: {aktuell} → {neu}, job-application-follow-up (Mail {nachricht['id']})")
    vorschlag = {"zeilen": zeilen, "status_alt": aktuell, "status_neu": neu, "status_grund": grund, "art": art,
                 "folgeaufgabe": {"anlass": FOLGE_ANLASS[typ], "faellig": ""} if typ in FOLGE_ANLASS else None}
    vorschlag["hash"] = digest(nachricht["id"], slug or "-", typ, art, aktuell, neu or "-", *zeilen)
    return vorschlag


def pruefe_nachricht(roh, index):
    if not isinstance(roh, dict) or not isinstance(roh.get("id"), str) or not re.fullmatch(r"[A-Za-z0-9_.:@-]{1,128}", roh["id"]):
        raise Refused("nachricht_ungueltig", f"Nachricht {index}: id fehlt oder ist keine Referenz (Buchstaben, Ziffern, _ . : @ -)")
    datum = ss.valid_date(str(roh.get("datum", ""))[:10])
    if not datum:
        raise Refused("nachricht_ungueltig", f"Nachricht {redact(roh['id'], 40)}: datum fehlt oder ist kein Datum (JJJJ-MM-TT)")
    anhaenge = [clean_text(a, 80) for a in roh.get("anhaenge", []) if isinstance(a, str)][:10] if isinstance(roh.get("anhaenge", []), list) else []
    return {"id": roh["id"], "thread_id": clean_text(roh.get("thread_id", ""), 128), "domain": domain_von(str(roh.get("von", ""))),
            "absender_lokal": clean_text(str(roh.get("von", "")).split("@")[0].split("<")[-1], 60),
            "betreff": clean_text(roh.get("betreff", ""), 300), "text": clean_text(roh.get("text", ""), 6000), "datum": datum, "anhaenge": anhaenge}


def relevant(nachricht, vorgang, typ_gewissheit, typ):
    if vorgang is not None or typ_gewissheit in ("eindeutig", "wahrscheinlich") and typ != "unbekannt":
        return True
    if NEWSLETTER.search(nachricht["betreff"] + " " + nachricht["text"][:300]):
        return False
    return bool(ABSENDER_HINWEIS.match(nachricht["absender_lokal"]))


def verarbeite(w, roh_liste, jetzt):
    """One run on the messages handed over (MV-2.1: started by the user). Returns the report; nothing is taken over."""
    if not isinstance(roh_liste, list):
        raise Refused("nachricht_ungueltig", "Die Eingabe ist eine JSON-Liste von Nachrichten")
    daten = lade_eingang(w)
    nachrichten = daten["nachrichten"]
    vorgaenge = alle_vorgaenge(w)
    bekannt = list(nachrichten.values())
    bericht = {"neu": [], "doppelt": [], "nicht_relevant": 0, "unzuordenbar": [], "unklar": [], "eingelesen": len(roh_liste)}
    fingerabdruecke = {n.get("fingerabdruck"): n["id"] for n in nachrichten.values()}
    for index, roh in enumerate(roh_liste):
        n = pruefe_nachricht(roh, index)
        fp = digest(n["domain"], n["betreff"], n["datum"], n["text"][:200])
        if n["id"] in nachrichten or fp in fingerabdruecke:
            bericht["doppelt"].append(n["id"])
            continue
        typ, typ_gew, quelle, treffer = klassifiziere(n)
        slug, zuordnung, kandidaten = ordne_zu(w, vorgaenge, n, bekannt)
        if not relevant(n, slug, typ_gew, typ):
            bericht["nicht_relevant"] += 1  # MV-5.3: left alone, not analysed further, not stored
            continue
        original = satz_mit(n["text"] or n["betreff"], next(iter(treffer.values()), ""))
        gesamt = GEWISSHEIT[max(GEWISSHEIT.index(zuordnung), GEWISSHEIT.index(typ_gew))] if slug else zuordnung  # the weaker of the two
        vorschlag = baue_vorschlag(w, n, slug, typ) if slug else {"zeilen": [], "status_alt": "", "status_neu": None, "status_grund": "kein Vorgang",
                                                                  "art": MAILTYPEN[typ][2] if typ in MAILTYPEN else "kontaktaufnahme", "folgeaufgabe": None,
                                                                  "hash": digest(n["id"], "-", typ)}
        eintrag = {"id": n["id"], "thread_id": n["thread_id"], "absender_domain": n["domain"], "betreff": n["betreff"][:BETREFF_MAX], "datum": n["datum"],
                   "anhaenge": n["anhaenge"], "erfasst": stamp(jetzt), "fingerabdruck": fp, "vorgang": slug, "kandidaten": kandidaten,
                   "zuordnung": zuordnung, "mailtyp": typ, "mailtyp_gewissheit": typ_gew, "quelle": quelle, "gewissheit": gesamt,
                   "original": original, "interpretation": deute_feedback(typ, original),
                   "termine_im_text": sorted({f"{m[2]}-{int(m[1]):02d}-{int(m[0]):02d}" if m[0] else f"{m[3]}-{m[4]}-{m[5]}"
                                              for m in DATUM_IM_TEXT.findall(n["text"])})[:5],
                   "vorschlag": vorschlag, "status": "vorgeschlagen", "bestaetigung": None,
                   "unsicherheit": "" if gesamt == "eindeutig" else
                   ("mehrere Vorgänge kommen infrage" if zuordnung == "unklar" else "keine sichere Zuordnung" if zuordnung == "nicht_zuordenbar"
                    else "Mailtyp unklar oder nur schwach erkannt" if typ_gew != "eindeutig" else "Zuordnung nur über schwache Merkmale")}
        nachrichten[n["id"]] = eintrag
        fingerabdruecke[fp] = n["id"]
        bekannt.append(eintrag)
        bericht["neu"].append({"id": n["id"], "vorgang": slug, "mailtyp": typ, "gewissheit": gesamt})
        if zuordnung == "nicht_zuordenbar":
            bericht["unzuordenbar"].append(n["id"])
        if zuordnung == "unklar":
            bericht["unklar"].append(n["id"])
    speichere_eingang(w, daten)
    bericht["offen"] = sum(1 for n in nachrichten.values() if n["status"] == "vorgeschlagen")
    return bericht


# ---------------------------------------------------------------- review: show, assign, confirm, reject (MV-8)

def hole(daten, nachricht_id):
    n = daten["nachrichten"].get(nachricht_id)
    if n is None:
        raise Refused("nachricht_unbekannt", f"Keine Nachricht {redact(nachricht_id, 60)} im Eingang")
    return n


def erneuere(w, n):
    """Compute the proposal from the state now (the status of the Vorgang may have moved since the run)."""
    if n["vorgang"]:
        alt = n["vorschlag"]
        n["vorschlag"] = baue_vorschlag(w, {"id": n["id"], "thread_id": n["thread_id"], "datum": n["datum"], "anhaenge": n["anhaenge"]}, n["vorgang"], n["mailtyp"])
        if alt.get("folgeaufgabe") and n["vorschlag"].get("folgeaufgabe"):
            n["vorschlag"]["folgeaufgabe"]["faellig"] = alt["folgeaufgabe"].get("faellig", "")
    return n["vorschlag"]


def ansicht(n, mit_original=True):
    kurz = {k: n[k] for k in ("id", "thread_id", "absender_domain", "betreff", "datum", "vorgang", "zuordnung", "mailtyp", "mailtyp_gewissheit",
                              "gewissheit", "unsicherheit", "status", "quelle") if k in n}
    kurz["kandidaten"] = [{"vorgang": k["vorgang"], "gruende": k["gruende"]} for k in n["kandidaten"]]
    kurz["vorschlag"] = n["vorschlag"]
    if mit_original:
        kurz["original"] = n["original"]
        kurz["interpretation"] = n["interpretation"]
    return kurz


def zuweisen(w, daten, nachricht_id, vorgang, typ):
    """The user decides an unclear case (MV-6.3): the proposal is recomputed for that Vorgang and needs its own confirmation."""
    n = hole(daten, nachricht_id)
    if n["status"] != "vorgeschlagen":
        raise Refused("bereits_entschieden", f"{nachricht_id} ist {n['status']}")
    if vorgang:
        vorgang_meta(w, vorgang)
        n["vorgang"] = vorgang
    if typ:
        if typ not in MAILTYPEN:
            raise Refused("mailtyp_unbekannt", f"Mailtyp {redact(typ, 40)} ist nicht bekannt ({', '.join(MAILTYPEN)})")
        n["mailtyp"], n["mailtyp_gewissheit"] = typ, "eindeutig"
        n["interpretation"] = deute_feedback(typ, n["original"])
    if not n["vorgang"]:
        raise Refused("vorgang_fehlt", "Ohne Vorgang gibt es nichts zu übernehmen: --vorgang angeben")
    n["zuordnung"], n["gewissheit"], n["quelle"] = "eindeutig", "eindeutig", "nutzer"
    n["unsicherheit"] = "manuell zugewiesen"
    n["manuell"] = True
    erneuere(w, n)
    return n


def neues_id(liste, praefix):
    zahlen = [int(m.group(1)) for e in liste for m in [re.fullmatch(rf"{praefix}-(\d+)", str(e.get("id", "")))] if m]
    return f"{praefix}-{max(zahlen, default=0) + 1:03d}"


def schreibe_verlauf(w, slug, zeilen, neuer_status):
    """Append lines to `## Verlauf` of vorgang.md and set `status`. Everything else in the file stays as it is."""
    pfad = vorgang_pfad(w, slug)
    with open(pfad, encoding="utf-8", newline="") as handle:
        text = handle.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    if neuer_status:
        kopf = re.match(r"^---\r?\n.*?\r?\n---(?:\r?\n|$)", text, re.S)
        if not kopf or not re.search(r"^status:.*$", kopf.group(0), re.M):
            raise Refused("vorgang_ungueltig", "vorgang.md hat kein Frontmatter mit status: die Statusänderung wird nicht geschrieben")
        text = re.sub(r"^status:.*$", f"status: {neuer_status}", text, count=1, flags=re.M)
    block = nl.join(zeilen)
    treffer = re.search(r"^## Verlauf[ \t]*\r?$", text, re.M)
    if treffer:
        rest = text[treffer.end():]
        naechste = re.search(r"^## ", rest, re.M)
        ende = treffer.end() + (naechste.start() if naechste else len(rest))
        vor, nach = text[:ende].rstrip("\r\n"), text[ende:]
        text = vor + nl + block + nl + (nl + nach if nach else "")
    else:
        text = text.rstrip("\r\n") + nl + nl + "## Verlauf" + nl + block + nl
    ordner = os.path.dirname(pfad)
    temp = os.path.join(ordner, ".vorgang.md.tmp")
    try:
        with open(temp, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(temp, pfad)
    except OSError as error:
        raise Refused("speichern_fehlgeschlagen", f"vorgang.md nicht geschrieben: {redact(error)}")


def bestaetigen(w, daten, nachricht_id, hash_wert, optionen, jetzt):
    """Take over one proposal after the user's approval of exactly this content (MV-8: approval per line)."""
    n = hole(daten, nachricht_id)
    if n["status"] != "vorgeschlagen":
        raise Refused("bereits_entschieden", f"{nachricht_id} ist schon {n['status']}: eine Nachricht wird nicht zweimal übernommen")
    if n["gewissheit"] in ("unklar", "nicht_zuordenbar") or not n["vorgang"]:
        raise Refused("pruefung_erforderlich", "Die Zuordnung ist unklar: erst mit `zuweisen --vorgang …` entscheiden und den neuen Vorschlag prüfen")
    if n["mailtyp"] == "unbekannt":
        raise Refused("pruefung_erforderlich", "Der Mailtyp ist unbekannt: erst mit `zuweisen --typ …` entscheiden")
    slug = n["vorgang"]
    jetzt_vorschlag = erneuere(w, n)
    if hash_wert != jetzt_vorschlag["hash"]:
        raise Refused("vorschlag_geaendert", f"Die Freigabe gilt nicht für den Vorschlag, wie er jetzt ist (Hash {jetzt_vorschlag['hash'][:12]}): mit `zeige` ansehen und neu freigeben")
    with open(vorgang_pfad(w, slug), encoding="utf-8", errors="replace") as handle:
        verlauf_text = handle.read()
    if re.search(rf"Gmail-ID {re.escape(n['id'])}(?![\w.:@-])", verlauf_text):
        raise Refused("bereits_erfasst", "Diese Nachricht steht schon in ## Verlauf (MV-7.7)")
    faellig = optionen.get("faellig") or ""
    if faellig and ss.valid_date(faellig) != faellig:
        raise Refused("datum_ungueltig", "--faellig ist ein echtes Datum der Form JJJJ-MM-TT")
    neu_status = jetzt_vorschlag["status_neu"] if not optionen.get("kein_status") else None
    zeilen = [z for z in jetzt_vorschlag["zeilen"] if neu_status or "→" not in z]
    nv = lade_nachverfolgung(w, slug)
    korrigiert = bool(n.get("manuell")) or bool(optionen.get("kategorie") or optionen.get("thema") or optionen.get("aussage"))
    ereignis = {"id": neues_id(nv["ereignisse"], "e"), "art": jetzt_vorschlag["art"], "datum": n["datum"],
                "quelle": {"typ": "nachricht", "nachricht_id": n["id"], "thread_id": n["thread_id"]}, "original": n["original"],
                "interpretation": n["interpretation"], "status": "korrigiert" if korrigiert else "bestaetigt", "erfasst": stamp(jetzt),
                "bestaetigt_am": stamp(jetzt), "gewissheit": n["gewissheit"], "mailtyp": n["mailtyp"]}
    if optionen.get("kategorie") and not KATEGORIE_FORM.fullmatch(optionen["kategorie"]):
        raise Refused("kategorie_ungueltig", "--kategorie besteht aus a-z, 0-9 und _")
    if optionen.get("kategorie") or optionen.get("thema") or optionen.get("aussage"):
        i = dict(ereignis["interpretation"] or {"kategorie": "allgemein", "bezeichnung": "allgemein", "thema": "", "aussage": "", "grund_genannt": True})
        i["grund_genannt"] = True
        if optionen.get("kategorie"):
            i.update(kategorie=optionen["kategorie"], bezeichnung=optionen["kategorie"])
        i.update(thema=clean_text(optionen.get("thema") or i["thema"], 80), aussage=clean_text(optionen.get("aussage") or i["aussage"], 160), sicherheit="mittel",
                 hinweis="vom Nutzer bestätigt; eine Qualifikationslücke ist es erst, wenn der Nutzer sie in die Grundlage übernimmt")
        ereignis["interpretation"] = i
    if faellig and n["vorschlag"].get("folgeaufgabe"):
        folge = n["vorschlag"]["folgeaufgabe"]
        nv["wiedervorlagen"].append({"id": neues_id(nv["wiedervorlagen"], "w"), "anlass": folge["anlass"], "faellig": faellig,
                                     "beschreibung": f"aus Mail {n['mailtyp']} vom {n['datum']}", "quelle": {"typ": "nachricht", "nachricht_id": n["id"]},
                                     "status": "offen", "angelegt": stamp(jetzt)})
    elif faellig:
        raise Refused("keine_folgeaufgabe", "Zu diesem Mailtyp gibt es keine Folgeaufgabe; --faellig weglassen oder `wiedervorlage anlegen` benutzen")
    nv["ereignisse"].append(ereignis)
    schreibe_verlauf(w, slug, zeilen, neu_status)
    speichere_nachverfolgung(w, slug, nv)
    n["status"] = "korrigiert" if korrigiert else "bestaetigt"
    n["bestaetigung"] = {"am": stamp(jetzt), "von": "nutzer", "hash": hash_wert, "status_geaendert": neu_status}
    return {"ok": True, "nachricht": n["id"], "vorgang": slug, "ereignis": ereignis["id"], "status": neu_status or jetzt_vorschlag["status_alt"],
            "zeilen": zeilen, "wiedervorlage": bool(faellig and n["vorschlag"].get("folgeaufgabe"))}


def verwerfen(daten, nachricht_id, grund, jetzt):
    n = hole(daten, nachricht_id)
    if n["status"] != "vorgeschlagen":
        raise Refused("bereits_entschieden", f"{nachricht_id} ist schon {n['status']}")
    if not grund.strip():
        raise Refused("grund_fehlt", "--grund fehlt")
    n["status"] = "verworfen"
    n["bestaetigung"] = {"am": stamp(jetzt), "von": "nutzer", "grund": clean_text(grund, 200)}
    return {"ok": True, "nachricht": nachricht_id, "status": "verworfen"}


# ---------------------------------------------------------------- Wiedervorlagen (7.3) and follow-up (8)

def wiedervorlage_anlegen(w, slug, anlass, faellig, beschreibung, jetzt):
    vorgang_meta(w, slug)
    if anlass not in ANLAESSE:
        raise Refused("anlass_unbekannt", f"Anlass {redact(anlass, 40)} ist nicht bekannt ({', '.join(ANLAESSE)})")
    if ss.valid_date(faellig) != faellig or not faellig:
        raise Refused("datum_ungueltig", "--faellig ist ein echtes Datum der Form JJJJ-MM-TT: eine Frist legt die Nutzerin oder der Nutzer fest")
    nv = lade_nachverfolgung(w, slug)
    if any(r["anlass"] == anlass and r["faellig"] == faellig and r["status"] == "offen" for r in nv["wiedervorlagen"]):
        raise Refused("wiedervorlage_existiert", "Diese Wiedervorlage gibt es schon (Anlass und Datum)")
    eintrag = {"id": neues_id(nv["wiedervorlagen"], "w"), "anlass": anlass, "faellig": faellig, "beschreibung": clean_text(beschreibung, 160),
               "quelle": {"typ": "nutzer"}, "status": "offen", "angelegt": stamp(jetzt)}
    nv["wiedervorlagen"].append(eintrag)
    speichere_nachverfolgung(w, slug, nv)
    return {"ok": True, "wiedervorlage": eintrag, "hinweis": "Eine Wiedervorlage erzeugt eine Aufgabe und keine Nachricht."}


def wiedervorlage_abschliessen(w, slug, wid, status, jetzt):
    nv = lade_nachverfolgung(w, slug)
    eintrag = next((r for r in nv["wiedervorlagen"] if r["id"] == wid), None)
    if eintrag is None or eintrag["status"] != "offen":
        raise Refused("wiedervorlage_unbekannt", f"Keine offene Wiedervorlage {redact(wid, 40)} im Vorgang {slug}")
    eintrag["status"], eintrag["abgeschlossen"] = status, stamp(jetzt)
    speichere_nachverfolgung(w, slug, nv)
    return {"ok": True, "wiedervorlage": wid, "status": status}


def faellige_wiedervorlagen(w, slug, now):
    try:
        nv = lade_nachverfolgung(w, slug)
    except Refused:
        return []
    return [r for r in nv["wiedervorlagen"] if r["status"] == "offen" and ss.valid_date(r["faellig"]) and r["faellig"] <= heute(now)]


def offene_vorschlaege(w, slug=None):
    try:
        daten = lade_eingang(w)
    except Refused:
        return []
    return [n for n in daten["nachrichten"].values() if n["status"] == "vorgeschlagen" and (slug is None or n["vorgang"] == slug)]


def nachfass(w, slug, now, nach_tage, konfiguration):
    """The basis of a follow-up mail (8.1, 8.2). No deadline of its own: the user sets one, or the Anker does. Writes nothing."""
    meta = vorgang_meta(w, slug)
    status = meta.get("status", "")
    if status != "versendet":
        raise Refused("kein_nachfassbedarf", f"Der Vorgang steht auf `{status}`: nachgefasst wird nur nach `versendet` und ohne Rückmeldung")
    versendet = ss.valid_date(meta.get("versendet_am", ""))
    if not versendet:
        raise Refused("versand_unbekannt", "versendet_am fehlt in vorgang.md: das Ausgangsdatum trägt die Nutzerin oder der Nutzer ein (S7)")
    offen = offene_vorschlaege(w, slug)
    if offen:
        raise Refused("pruefung_offen", f"{len(offen)} Nachricht(en) dieses Vorgangs sind noch nicht geprüft: erst die Rückmeldung prüfen, dann nachfassen")
    nv = lade_nachverfolgung(w, slug)
    antworten = [e for e in nv["ereignisse"] if e["status"] in ("bestaetigt", "korrigiert")]
    if any(e["art"] != "eingangsbestaetigung" for e in antworten):
        raise Refused("kein_nachfassbedarf", "Es gibt schon eine inhaltliche Rückmeldung")
    tage = nach_tage
    quelle = "Option --nach-tage"
    if tage is None and konfiguration:
        wert = ss.read_frontmatter(konfiguration).get("nachfass_tage", "")
        tage, quelle = (int(wert), "nachfass_tage in konfiguration.md") if wert.isdigit() else (None, quelle)
    datum = None
    if tage is None and ss.valid_date(meta.get("wiedervorlage", "")):
        datum, quelle = meta["wiedervorlage"], "wiedervorlage in vorgang.md"
    elif tage is not None:
        datum = (dt.date.fromisoformat(versendet) + dt.timedelta(days=tage)).isoformat()
    if datum is None:
        raise Refused("frist_fehlt", "Es ist keine Frist festgelegt (weder --nach-tage noch nachfass_tage noch wiedervorlage): die Nutzerin oder der Nutzer legt sie fest")
    faellig = datum <= heute(now)
    datei = "email-nachfassen.md"
    pfad = os.path.join(w, slug, datei)
    return {"ok": True, "vorgang": slug, "versendet_am": versendet, "rueckmeldungen": [{"art": e["art"], "datum": e.get("datum")} for e in antworten],
            "grund": f"Seit {versendet} ohne inhaltliche Rückmeldung; Frist {datum} ({quelle}) {'erreicht' if faellig else 'noch nicht erreicht'}",
            "vorgeschlagenes_datum": datum, "faellig": faellig,
            "entwurf": {"datei": datei, "vorhanden": os.path.isfile(pfad),
                        "schreiben": "job-application-email-create (Variante nachfassen); der Entwurf nennt nur Tatsachen aus dem Vorgang",
                        "inhalt_hash": sha256_file(pfad) if os.path.isfile(pfad) else ""},
            "freigabe": {"aufgabe": f"nachricht_senden:{slug}:{datei}", "regel": "Vor dem Versand: Nachricht, Empfänger und Vorgang anzeigen, dann die ausdrückliche Freigabe im Workflow; ohne Adapter bleibt es ein geprüfter Entwurf"},
            "versand": "Das Skript sendet nichts."}


# ---------------------------------------------------------------- CLI

def liste(daten, status, vorgang):
    return [ansicht(n, False) for n in sorted(daten["nachrichten"].values(), key=lambda n: (n["datum"], n["id"]))
            if (not status or n["status"] == status) and (not vorgang or n["vorgang"] == vorgang)]


def build_parser():
    p = argparse.ArgumentParser(description="Communication and follow-up after the dispatch (A-02).")
    p.add_argument("--konfiguration", default=os.path.join(ss.DEFAULT_WURZEL, "konfiguration.md"))
    p.add_argument("--jetzt")
    sub = p.add_subparsers(dest="befehl", required=True)
    v = sub.add_parser("verarbeiten")
    v.add_argument("--nachrichten", help="JSON file; stdin when missing")
    for name in ("liste",):
        s = sub.add_parser(name)
        s.add_argument("--status", choices=NACHRICHT_STATUS)
        s.add_argument("--vorgang")
    z = sub.add_parser("zeige")
    z.add_argument("nachricht")
    zu = sub.add_parser("zuweisen")
    zu.add_argument("nachricht")
    zu.add_argument("--vorgang")
    zu.add_argument("--typ")
    b = sub.add_parser("bestaetigen")
    b.add_argument("nachricht")
    b.add_argument("--hash", required=True)
    b.add_argument("--ja", action="store_true")
    b.add_argument("--kein-status", action="store_true")
    b.add_argument("--faellig")
    b.add_argument("--kategorie")
    b.add_argument("--thema")
    b.add_argument("--aussage")
    vw = sub.add_parser("verwerfen")
    vw.add_argument("nachricht")
    vw.add_argument("--grund", default="")
    w = sub.add_parser("wiedervorlage")
    w.add_argument("aktion", choices=("anlegen", "erledigen", "verwerfen", "liste"))
    w.add_argument("vorgang")
    w.add_argument("--anlass")
    w.add_argument("--faellig", default="")
    w.add_argument("--text", default="")
    w.add_argument("--id")
    n = sub.add_parser("nachfass")
    n.add_argument("vorgang")
    n.add_argument("--nach-tage", type=int)
    return p


USER_ONLY = ("zuweisen", "bestaetigen", "verwerfen")


def run(args):
    now = parse_time(args.jetzt) if args.jetzt else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    w = ss.find_wurzel(args.konfiguration)
    befehl = args.befehl
    if befehl in USER_ONLY or (befehl == "wiedervorlage" and args.aktion != "liste"):
        schutz_nutzer(befehl)
    if befehl == "bestaetigen" and not args.ja:
        raise Refused("freigabe_fehlt", "Die Übernahme braucht die ausdrückliche Freigabe der Nutzerin oder des Nutzers (--ja) für genau diesen Vorschlag")
    if befehl in ("liste", "zeige"):
        daten = lade_eingang(w)
        if befehl == "liste":
            return {"ok": True, "nachrichten": liste(daten, args.status, args.vorgang)}
        n = hole(daten, args.nachricht)
        if n["status"] == "vorgeschlagen":
            erneuere(w, n)  # shown as it is now; nothing is saved by looking, `bestaetigen` computes it again
        return {"ok": True, "nachricht": ansicht(n)}
    if befehl == "nachfass":
        return nachfass(w, args.vorgang, now, args.nach_tage, args.konfiguration)
    if befehl == "wiedervorlage" and args.aktion == "liste":
        vorgang_meta(w, args.vorgang)
        return {"ok": True, "wiedervorlagen": lade_nachverfolgung(w, args.vorgang)["wiedervorlagen"]}
    with ss.exclusive(w, *LOCK):
        if befehl == "verarbeiten":
            if args.nachrichten:
                with open(args.nachrichten, encoding="utf-8") as handle:
                    quelle = handle.read()
            else:
                quelle = sys.stdin.read()
            try:
                roh = json.loads(quelle)
            except ValueError:
                raise Refused("nachricht_ungueltig", "Die Eingabe ist kein JSON")
            return {"ok": True, **verarbeite(w, roh, now)}
        if befehl == "wiedervorlage":
            if args.aktion == "anlegen":
                return wiedervorlage_anlegen(w, args.vorgang, args.anlass or "", args.faellig, args.text, now)
            return wiedervorlage_abschliessen(w, args.vorgang, args.id or "", "erledigt" if args.aktion == "erledigen" else "verworfen", now)
        daten = lade_eingang(w)
        if befehl == "zuweisen":
            n = zuweisen(w, daten, args.nachricht, args.vorgang, args.typ)
            speichere_eingang(w, daten)
            return {"ok": True, "nachricht": ansicht(n), "hinweis": "Neuer Vorschlag: mit `bestaetigen --hash …` freigeben"}
        if befehl == "bestaetigen":
            ergebnis = bestaetigen(w, daten, args.nachricht, args.hash, {"kein_status": args.kein_status, "faellig": args.faellig,
                                                                        "kategorie": args.kategorie, "thema": args.thema, "aussage": args.aussage}, now)
            speichere_eingang(w, daten)
            return ergebnis
        ergebnis = verwerfen(daten, args.nachricht, args.grund, now)
        speichere_eingang(w, daten)
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
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result.get("ok") is False else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
