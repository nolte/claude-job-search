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
ENDSTATUS = ("zusage", "absage", "abgelehnt", "zurückgezogen", "ohne Antwort", "abgeschlossen")

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
    # R-02: the appointment, document and process mails around an invitation (MV-28). No status follows from them unless noted.
    "terminvorschlag": ("Terminvorschlag", None, "im_auswahlprozess", (
        r"terminvorschl\w+|schlagen sie .{0,60}(termin|zeitpunkt)\w*|folgende (termine|zeiten|zeitfenster|terminoptionen)|bitte (wählen|nennen) sie .{0,60}(termin|zeitpunkt)|please (choose|propose).{0,40}(time|slot|date)", None)),
    "terminbestaetigung": ("Terminbestätigung", "gespräch", "gespraech_vereinbart", (
        r"bestätigen (wir |hiermit )?(gerne )?(den |ihren |unseren )?(termin|gespräch)\w*|termin(e)? (ist|wurde|steht) (hiermit )?(fest|bestätigt|vereinbart)|wir freuen uns auf (das gespräch|sie am)|confirm(ed)? (the |your )?(interview|appointment|meeting)", None)),
    "terminverschiebung": ("Terminverschiebung", None, "gespraech_verschoben", (
        r"(termin|gespräch|interview)\w*.{0,80}(verschieb|verleg|umterminier)\w*|(verschieb|verleg|umterminier)\w*.{0,80}(termin|gespräch|interview)|reschedul\w+|postpone", None)),
    "terminabsage": ("Terminabsage", None, "gespraech_abgesagt", (
        r"(termin|gespräch|interview)\w*.{0,60}(absagen|abgesagt|entfällt|fällt aus)|(absagen|absage des).{0,40}(termin|gespräch|interview)\w*|(interview|appointment|meeting) (is |has been )?cancel+ed", None)),
    "unterlagen_anfrage": ("Bitte um Unterlagen", "rückmeldung", "rueckfrage", (
        r"bitte (reichen|senden|schicken) sie .{0,80}(unterlagen|zeugnis\w*|nachweis\w*|referenz\w*|arbeitsproben|zertifikat\w*)|(bitte|können sie).{0,60}(unterlagen|zeugnis\w*|nachweis\w*|referenz\w*|arbeitsproben|zertifikat\w*).{0,60}(nachreichen|senden|schicken|reichen|zusenden|zukommen lassen)|(nachreichen|zusenden).{0,40}(unterlagen|zeugnis\w*|nachweis\w*)|please (send|provide|submit).{0,60}(documents|certificate|reference)", None)),
    "unterlagen_eingang": ("Eingang nachgereichter Unterlagen", None, "eingangsbestaetigung", (
        r"(nachgereichten|zusätzlichen|weiteren|ergänzenden|angeforderten|fehlenden) (unterlagen|dokumente|zeugnisse|nachweise).{0,40}(erhalten|eingegangen|angekommen)|(erhalten|eingegangen).{0,40}(nachgereichten|zusätzlichen|angeforderten|fehlenden) (unterlagen|dokumente)", None)),
    "zwischenstand": ("Zwischenstand", "rückmeldung", "im_auswahlprozess", (
        r"aktuelle[rn]? (stand|status)|befinden uns (noch )?(im|in der) (auswahl|bewerbungs)\w*|(noch )?im auswahlprozess|bewerbungen (derzeit|aktuell|noch) (prüfen|sichten|auswerten)|bitten (sie )?noch um (etwas )?geduld|status update", None)),
    "angebotsrueckfrage": ("Rückfrage zum Angebot", None, "rueckfrage", (
        r"rückfrage\w*.{0,100}angebot\w*|angebot\w*.{0,100}rückfrage\w*", None)),
    "sonstiges": ("Sonstige Mitteilung", None, "kontaktaufnahme", (None, None)),  # only by hand (`zuweisen --typ sonstiges`)
}
# A more specific type wins over the generic one it contains: key -> the types it overrides when both match strongly (MV-28 rule 2).
# Two types that are not listed here stay a contradiction and go to the user.
VORRANG = {
    "unterlagen_anfrage": {"rueckfrage"}, "unterlagen_eingang": {"eingangsbestaetigung"}, "terminabsage": {"absage", "einladung", "terminverschiebung", "terminvorschlag"},
    "terminverschiebung": {"einladung", "terminvorschlag"}, "terminbestaetigung": {"einladung", "terminvorschlag", "eingangsbestaetigung"},
    "einladung": {"terminvorschlag"}, "angebotsrueckfrage": {"angebot", "rueckfrage"},
}
EINLADUNG_EXPLIZIT = r"einladung|einladen|laden sie|invite you|invitation"  # a bare "Vorstellungsgespräch" is no invitation
# What the employer did or said (a reply). Only these count as a reply of the employer in the evaluation (lernen.INHALTLICH).
ARTEN_ARBEITGEBER = tuple(v[2] for v in MAILTYPEN.values()) + (
    "kontaktaufnahme", "im_auswahlprozess", "gespraech_vereinbart", "gespraech_verschoben", "gespraech_abgesagt", "gespraech", "technisches_gespraech",
    "assessment", "weiterer_termin", "weitere_phase", "absage_nach_unterlagen", "absage_nach_gespraech", "absage_nach_assessment")
# What the applicant or the toolchain did or decided (R-01 3): own steps, never a reply and never an outcome by themselves.
ARTEN_EIGEN = ("vorbereitet", "geprueft", "freigabe_angefordert", "freigabe_erteilt", "freigabe_verweigert", "versendet", "versand_fehlgeschlagen",
               "antwort_vorbereitet", "antwort_zur_freigabe", "antwort_freigegeben", "antwort_abgelehnt", "antwort_versendet", "antwort_versand_fehlgeschlagen",
               "angebot_angenommen", "angebot_abgelehnt", "zurueckgezogen", "abgeschlossen", "statuswechsel")
ARTEN = ARTEN_ARBEITGEBER + ARTEN_EIGEN
POSITIV = ("eingangsbestaetigung", "kontaktaufnahme", "gespraechseinladung", "gespraech", "technisches_gespraech", "assessment",
           "weitere_phase", "angebot", "einstellung")
NEGATIV = ("absage", "absage_nach_unterlagen", "absage_nach_gespraech", "absage_nach_assessment", "zurueckgezogen")
ANLAESSE = ("erwartete_rueckmeldung", "rueckmeldefrist", "nachfassen", "gespraechsvorbereitung", "gespraechstermin", "gespraechsnachbereitung",
            "offene_rueckfrage", "angebot_pruefen", "fehlende_information")
VERBINDLICHKEIT = ("eigene_planung", "arbeitgeber_frist")  # a date the employer named is a deadline of the employer; every other date is the user's own planning
FOLGE_ANLASS = {"eingangsbestaetigung": "erwartete_rueckmeldung", "einladung": "gespraechsvorbereitung", "rueckfrage": "offene_rueckfrage",
                "angebot": "angebot_pruefen", "gespraechsfeedback": "gespraechsnachbereitung", "terminvorschlag": "gespraechstermin",
                "terminbestaetigung": "gespraechstermin", "terminverschiebung": "gespraechstermin", "terminabsage": "offene_rueckfrage",
                "unterlagen_anfrage": "fehlende_information", "zwischenstand": "erwartete_rueckmeldung", "angebotsrueckfrage": "angebot_pruefen"}
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


KONTAKTDATEN = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|(?:\+\d{2}|\(?0\d{2,5}\)?)[ /-]?\d[\d /-]{5,}\d")


def schwaerze(text):
    """The text of a stored quote: single line, no credentials, no amounts, no e-mail address or phone number (MV-7.3, MV-26)."""
    return KONTAKTDATEN.sub("[Kontakt entfernt]", BETRAG.sub("[Betrag entfernt]", redact(text, 2000)))


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
        # an explicit reference number outweighs the similarity of a company (MV-6 rule 2); a thread of a confirmed message keeps its Vorgang,
        # unless another candidate names its own reference number. Everything else stays with the user.
        mit_ref = [k for k in kandidaten if "ref_nr" in k["merkmale"]]
        mit_thread = [k for k in kandidaten if "thread" in k["merkmale"]]
        wahl = mit_ref[0] if len(mit_ref) == 1 else mit_thread[0] if len(mit_thread) == 1 and not mit_ref else None
        if wahl is None:
            return None, "unklar", kandidaten
        wahl["bevorzugt"] = "ref_nr" if wahl in mit_ref else "thread"
        return wahl["vorgang"], "eindeutig", kandidaten
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
    for gewinner, verdraengt in VORRANG.items():
        if gewinner in stark:
            for typ in verdraengt & set(stark):
                del stark[typ]
    if "einladung" in stark and "zwischenstand" in stark and not re.search(fold(EINLADUNG_EXPLIZIT), text):
        del stark["einladung"]  # "Vorstellungsgespräche finden statt" in a status mail is information, not an invitation
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


# ---------------------------------------------------------------- extraction (MV-29)

DATUM_VOLL = re.compile(r"\b(\d{1,2})\.\s?(\d{1,2})\.\s?(\d{4}|\d{2})?(?!\d)|\b(20\d{2})-(\d{2})-(\d{2})\b|\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
UHRZEIT = re.compile(r"\b(\d{1,2}):(\d{2})\b|\b(\d{1,2})\.(\d{2})\s*(?:uhr|h)\b|\bum (\d{1,2})\s*uhr\b", re.IGNORECASE)
ZEITZONE = re.compile(r"\b(MEZ|MESZ|CET|CEST|UTC|GMT)\b")
RELATIV = re.compile(r"(?i)\b(?:(?:nächste[nrm]?|kommende[nrm]?|übernächste[nrm]?) (?:woche|montag|dienstag|mittwoch|donnerstag|freitag)|"
                     r"(?:montag|dienstag|mittwoch|donnerstag|freitag)|übermorgen|morgen|in (?:ein|zwei|drei) wochen|kw ?\d{1,2})\b")
FRIST_WORT = re.compile(r"(?i)\bbis (?:zum |spätestens |einschließlich |zur )*(?=\d)|\bfrist\b|\bspätestens\b|\bdeadline\b")
TERMIN_WORT = re.compile(r"(?i)termin|gespräch|interview|treffen|vorstellung|\buhr\b|zeitfenster")
FORMATE = (("video", r"videokonferenz|videocall|video-call|videogespräch|teams|zoom|webex|google meet|video"),
           ("telefon", r"telefonisch|telefoninterview|telefongespräch|per telefon"),
           ("vor_ort", r"vor ort|persönlich|in unseren räumen|in unserem büro|an unserem standort"))
NAME_NACH_GRUSS = re.compile(r"(?i:mit freundlichen grüßen|freundliche grüße|viele grüße|beste grüße|herzliche grüße|kind regards|best regards)[,\s]+"
                             r"((?:Dr\.\s|Prof\.\s)?[A-ZÄÖÜ][\w-]+\s+[A-ZÄÖÜ][\w-]+)(\s+[A-ZÄÖÜ][\w-]+)?")
NAME_ANSPRECH = re.compile(r"(?i:ansprechpartner(?:in)?|ihr kontakt|kontaktperson)\s*:?\s*((?:Dr\.\s|Prof\.\s)?[A-ZÄÖÜ][\w-]+\s+[A-ZÄÖÜ][\w-]+)")
REFERENZ = re.compile(r"(?i)\b(?:referenz(?:nummer)?|ref\.?-?(?:nr\.?)?|kennziffer|stellen-?id)\s*:?\s*([A-Za-z0-9][A-Za-z0-9/_.-]{2,29})")


def datum_aus(treffer, bezug):
    """-> (ISO date or '', unsicher, Hinweis) from one DATUM_VOLL match. A missing year is taken from the day of the mail and marked."""
    tag, monat, jahr, j2, m2, t2, m3, _, _ = treffer.groups()
    if j2:
        jahr_n, monat_n, tag_n, hinweis = int(j2), int(m2), int(t2), ""
    elif m3:  # 3/4/2026 reads as day/month or month/day
        return "", True, "Schrägstrich-Datum: Tag und Monat nicht eindeutig"
    else:
        tag_n, monat_n, hinweis = int(tag), int(monat), ""
        if jahr and len(jahr) == 4:
            jahr_n = int(jahr)
        elif jahr:
            jahr_n, hinweis = 2000 + int(jahr), "Jahr nur zweistellig angegeben"
        else:
            jahr_n, hinweis = int(bezug[:4]), "Jahr nicht genannt, vom Datum der Nachricht übernommen"
    try:
        wert = dt.date(jahr_n, monat_n, tag_n)
    except ValueError:
        return "", True, "kein gültiges Kalenderdatum"
    if hinweis.startswith("Jahr nicht") and wert.isoformat() < bezug:
        wert = wert.replace(year=wert.year + 1)
    return wert.isoformat(), bool(hinweis), hinweis


def uhrzeit_aus(treffer):
    """-> 'HH:MM' from one UHRZEIT match, or '' when it is no time of a day."""
    if not treffer:
        return ""
    g = treffer.groups()
    stunde, minute = (g[0], g[1]) if g[0] else (g[2], g[3]) if g[2] else (g[4], "00")
    return f"{int(stunde):02d}:{minute}" if int(stunde) < 24 and int(minute) < 60 else ""


def zitat(satz):
    return schwaerze(satz)[:ORIGINAL_MAX]


def fakt(feld, wert, art, satz, unsicher=False, hinweis="", **zusatz):
    return {"feld": feld, "wert": wert, "art": art, "quelle": zitat(satz), "unsicher": bool(unsicher), "hinweis": hinweis, "bestaetigt": False, **zusatz}


def extrahiere(nachricht):
    """-> list of facts read from the text: what is stated (`ausdruecklich`) and what is derived (`abgeleitet`), each with its quote.

    A fact is a proposal until the user takes it over (`bestaetigen --uebernehmen`). Nothing is invented: a missing year, a
    relative day, a missing time zone or two dates in one sentence are marked `unsicher`; a relative day is not turned into a date."""
    text, bezug = nachricht.get("text", ""), nachricht["datum"]
    saetze = [s.strip() for s in re.split(r"(?<=[!?])\s+|(?<=[a-zäöüß\)\d])\.\s+(?=[A-ZÄÖÜ])|\n+", text) if s.strip()]
    fakten, frist_gefunden, termin_gefunden = [], False, False
    for satz in saetze:
        daten = [(m, *datum_aus(m, bezug)) for m in DATUM_VOLL.finditer(satz)]
        frist_dat = None
        if FRIST_WORT.search(satz):
            frist_dat = next((d for d in daten if re.search(r"(?i)(?:bis|spätestens|frist)[^0-9]{0,30}$", satz[:d[0].start()])), None)
        if frist_dat and not frist_gefunden:
            fakten.append(fakt("frist", frist_dat[1], "ausdruecklich", satz, frist_dat[2] or not frist_dat[1], frist_dat[3]))
            frist_gefunden = True
        rest = [d for d in daten if d is not frist_dat]
        if rest and TERMIN_WORT.search(satz) and not termin_gefunden:
            _, iso, unsicher, hinweis = rest[0]
            uhr, zone = UHRZEIT.search(satz), ZEITZONE.search(satz)
            uhrzeit = uhrzeit_aus(uhr)
            hinweise = [h for h in (hinweis, "mehrere Daten in einem Satz: das erste ist angezeigt" if len(rest) > 1 else "",
                                    "keine Uhrzeit genannt" if not uhr else "",
                                    "Zeitzone nicht genannt: vor einer Zusage klären" if uhr and not zone else "") if h]
            fakten.append(fakt("termin", {"datum": iso, "uhrzeit": uhrzeit, "zeitzone": zone.group(1) if zone else "nicht genannt"}, "ausdruecklich", satz,
                               unsicher or not iso or len(rest) > 1 or (bool(uhr) and not zone), "; ".join(hinweise),
                               alternativen=[d[1] for d in rest[1:] if d[1]]))
            termin_gefunden = True
        elif not daten and TERMIN_WORT.search(satz) and RELATIV.search(satz) and not termin_gefunden:
            fakten.append(fakt("termin", {"datum": "", "uhrzeit": "", "zeitzone": "nicht genannt"}, "ausdruecklich", satz, True,
                               "relative Zeitangabe („" + RELATIV.search(satz).group(0) + "“) wird nicht in ein Datum umgerechnet"))
            termin_gefunden = True
    folded = fold(text)
    gefunden = [name for name, muster in FORMATE if re.search(fold(muster), folded)]
    if gefunden:
        muster = dict(FORMATE)[gefunden[0]]
        satz = next((s for s in saetze if re.search(fold(muster), fold(s))), text[:ORIGINAL_MAX])
        fakten.append(fakt("format", gefunden[0], "abgeleitet", satz, len(gefunden) > 1,
                           "mehrere Formate genannt: " + ", ".join(gefunden) if len(gefunden) > 1 else "", alternativen=gefunden[1:]))
    if "vor_ort" in gefunden:
        satz = next((s for s in saetze if re.search(r"(?i)adresse|standort|straße|str\.|vor ort|persönlich|räume|büro", s)), "")
        if satz:
            fakten.append(fakt("ort", zitat(satz)[:120], "abgeleitet", satz, True, "Ort ist der Wortlaut des Satzes, nicht eine geprüfte Adresse"))
    name = NAME_NACH_GRUSS.search(text)
    if name:
        drei = bool(name.group(2))
        fakten.append(fakt("kontakt_name", name.group(1).strip(), "ausdruecklich", name.group(0), drei,
                           "ein dritter großgeschriebener Begriff folgt (Titel, Abteilung oder Teil des Namens)" if drei else ""))
    elif NAME_ANSPRECH.search(text):
        name = NAME_ANSPRECH.search(text)
        fakten.append(fakt("kontakt_name", name.group(1).strip(), "ausdruecklich", name.group(0)))
    wege = [k for k, m in (("e-mail", r"[\w.+-]+@[\w-]+\.[a-z]{2,}"), ("telefon", r"(?:\+\d{2}|\(?0\d{2,5}\)?)[ /-]?\d[\d /-]{5,}\d")) if re.search(m, text, re.I)]
    if wege:
        fakten.append(fakt("kontaktwege", wege, "ausdruecklich", "(Kontaktdaten stehen in der Nachricht und werden nicht gespeichert)", False,
                           "nur die Art der Angabe; die Daten bleiben in der Originalnachricht"))
    anfrage = next((s for s in saetze if re.search(r"(?i)unterlagen|zeugnis|nachweis|referenzen|arbeitsproben|zertifikat", s)
                    and re.search(r"(?i)bitte|nachreichen|senden|schicken|zusenden|please", s)), "")
    if anfrage:
        liste = anfrage.split(":", 1)[1] if ":" in anfrage else ""
        punkte = [clean_text(p, 60) for p in re.split(r"\s*(?:,|;|•|\bund\b|\boder\b)\s*", liste) if clean_text(p, 60)][:10]
        fakten.append(fakt("unterlagen", punkte or zitat(anfrage)[:120], "ausdruecklich" if punkte else "abgeleitet", anfrage, not punkte,
                           "" if punkte else "keine Aufzählung nach einem Doppelpunkt: der Satz selbst ist die Angabe"))
    ref = REFERENZ.search(text)
    if ref:
        fakten.append(fakt("referenz", ref.group(1).rstrip(".-/"), "ausdruecklich", ref.group(0)))
    return fakten


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
    gesperrt = [clean_text(a, 80) for a in roh.get("anhaenge_gesperrt", []) if isinstance(a, str)][:10] if isinstance(roh.get("anhaenge_gesperrt", []), list) else []
    kanal = clean_text(roh.get("kanal", ""), 20).lower() or "manuell"
    if not re.fullmatch(r"[a-z][a-z0-9_-]{1,19}", kanal):
        raise Refused("nachricht_ungueltig", f"Nachricht {redact(roh['id'], 40)}: kanal besteht aus a-z, 0-9, _ und -")
    return {"id": roh["id"], "thread_id": clean_text(roh.get("thread_id", ""), 128), "domain": domain_von(str(roh.get("von", ""))),
            "anhaenge_gesperrt": gesperrt, "kanal": kanal, "empfaenger_domain": domain_von(str(roh.get("an", ""))), "quelle_ref": clean_text(roh.get("quelle_ref", ""), 80),
            "absender_lokal": clean_text(str(roh.get("von", "")).split("@")[0].split("<")[-1], 60),
            "betreff": clean_text(roh.get("betreff", ""), 300), "text": clean_text(roh.get("text", ""), 6000), "datum": datum, "anhaenge": anhaenge}


def relevant(nachricht, vorgang, typ_gewissheit, typ):
    if vorgang is not None:
        return True
    if NEWSLETTER.search(nachricht["betreff"] + " " + nachricht["text"][:300]) and typ_gewissheit != "eindeutig":
        return False  # a weak word such as "Angebot" in a newsletter does not make it a message of an employer
    if typ_gewissheit in ("eindeutig", "wahrscheinlich") and typ != "unbekannt":
        return True
    return bool(ABSENDER_HINWEIS.match(nachricht["absender_lokal"]))


def neu_verarbeiten(w, alt, n, vorgaenge, bekannt, jetzt):
    """Read a still-proposed message again from the text handed over now. History is kept; a manual decision of the user stays."""
    typ, typ_gew, quelle, treffer = klassifiziere(n)
    gemerkt = (alt["mailtyp"], alt["zuordnung"], alt["vorgang"])
    if not alt.get("manuell"):
        slug, zuordnung, kandidaten = ordne_zu(w, vorgaenge, n, [b for b in bekannt if b["id"] != alt["id"]])
        alt.update(vorgang=slug, zuordnung=zuordnung, kandidaten=kandidaten, mailtyp=typ, mailtyp_gewissheit=typ_gew, quelle=quelle)
        alt["gewissheit"] = GEWISSHEIT[max(GEWISSHEIT.index(zuordnung), GEWISSHEIT.index(typ_gew))] if slug else zuordnung
        alt["original"] = satz_mit(n["text"] or n["betreff"], next(iter(treffer.values()), ""))
        alt["interpretation"] = deute_feedback(typ, alt["original"])
    alt["extraktion"] = extrahiere(n)
    erneuere(w, alt)
    historie(alt, jetzt, "neu_verarbeitet", "system", f"vorher {gemerkt[0]}/{gemerkt[1]}, jetzt {alt['mailtyp']}/{alt['zuordnung']}"
             + (" (manuelle Zuordnung bleibt)" if alt.get("manuell") else ""))


def verarbeite(w, roh_liste, jetzt, erneut=False):
    """One run on the messages handed over (MV-2.1: started by the user). Returns the report; nothing is taken over.

    `erneut`: a message that is still only proposed is classified, assigned and read again (for example after a better rule or a new
    Vorgang). A decided message is never changed, and a manual assignment of the user stays (MV-30)."""
    if not isinstance(roh_liste, list):
        raise Refused("nachricht_ungueltig", "Die Eingabe ist eine JSON-Liste von Nachrichten")
    daten = lade_eingang(w)
    nachrichten = daten["nachrichten"]
    vorgaenge = alle_vorgaenge(w)
    bekannt = list(nachrichten.values())
    bericht = {"neu": [], "doppelt": [], "nicht_relevant": 0, "newsletter": 0, "unzuordenbar": [], "unklar": [], "eingelesen": len(roh_liste), "neu_verarbeitet": [],
               "uebersprungen": []}
    fingerabdruecke = {n.get("fingerabdruck"): n["id"] for n in nachrichten.values()}
    for index, roh in enumerate(roh_liste):
        n = pruefe_nachricht(roh, index)
        fp = digest(n["domain"], n["betreff"], n["datum"], n["text"][:200])
        if erneut and n["id"] in nachrichten:
            alt = nachrichten[n["id"]]
            if alt["status"] != "vorgeschlagen":
                bericht["uebersprungen"].append({"id": n["id"], "grund": f"schon {alt['status']}"})
                continue
            neu_verarbeiten(w, alt, n, vorgaenge, bekannt, jetzt)
            bericht["neu_verarbeitet"].append(n["id"])
            continue
        if n["id"] in nachrichten or fp in fingerabdruecke:
            bericht["doppelt"].append(n["id"])
            continue
        typ, typ_gew, quelle, treffer = klassifiziere(n)
        slug, zuordnung, kandidaten = ordne_zu(w, vorgaenge, n, bekannt)
        if not relevant(n, slug, typ_gew, typ):
            bericht["nicht_relevant"] += 1  # MV-5.3: left alone, not analysed further, not stored
            bericht["newsletter"] += bool(NEWSLETTER.search(n["betreff"] + " " + n["text"][:300]))
            continue
        original = satz_mit(n["text"] or n["betreff"], next(iter(treffer.values()), ""))
        gesamt = GEWISSHEIT[max(GEWISSHEIT.index(zuordnung), GEWISSHEIT.index(typ_gew))] if slug else zuordnung  # the weaker of the two
        vorschlag = baue_vorschlag(w, n, slug, typ) if slug else {"zeilen": [], "status_alt": "", "status_neu": None, "status_grund": "kein Vorgang",
                                                                  "art": MAILTYPEN[typ][2] if typ in MAILTYPEN else "kontaktaufnahme", "folgeaufgabe": None,
                                                                  "hash": digest(n["id"], "-", typ)}
        eintrag = {"id": n["id"], "thread_id": n["thread_id"], "absender_domain": n["domain"], "betreff": redact(n["betreff"], BETREFF_MAX), "datum": n["datum"],
                   "anhaenge": n["anhaenge"], "erfasst": stamp(jetzt), "fingerabdruck": fp, "vorgang": slug, "kandidaten": kandidaten,
                   "zuordnung": zuordnung, "mailtyp": typ, "mailtyp_gewissheit": typ_gew, "quelle": quelle, "gewissheit": gesamt,
                   "original": original, "interpretation": deute_feedback(typ, original),
                   "termine_im_text": sorted({f"{m[2]}-{int(m[1]):02d}-{int(m[0]):02d}" if m[0] else f"{m[3]}-{m[4]}-{m[5]}"
                                              for m in DATUM_IM_TEXT.findall(n["text"])})[:5],
                   "anhaenge_gesperrt": n["anhaenge_gesperrt"], "kanal": n["kanal"], "empfaenger_domain": n["empfaenger_domain"], "quelle_ref": n["quelle_ref"], "extraktion": extrahiere(n),
                   "antworten": [], "historie": [],
                   "vorschlag": vorschlag, "status": "vorgeschlagen", "bestaetigung": None,
                   "unsicherheit": "" if gesamt == "eindeutig" else
                   ("mehrere Vorgänge kommen infrage" if zuordnung == "unklar" else "keine sichere Zuordnung" if zuordnung == "nicht_zuordenbar"
                    else "Mailtyp unklar oder nur schwach erkannt" if typ_gew != "eindeutig" else "Zuordnung nur über schwache Merkmale")}
        historie(eintrag, jetzt, "erfasst", "system", f"Kanal {n['kanal']}, Datum der Nachricht {n['datum']}")
        historie(eintrag, jetzt, "verarbeitet", "system", f"{typ} ({typ_gew}), Zuordnung {zuordnung}, {len(eintrag['extraktion'])} Angaben gelesen")
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
    kurz.update(kanal=n.get("kanal", "manuell"), erfasst=n.get("erfasst", ""), quelle_ref=n.get("quelle_ref", ""), antworten=n.get("antworten", []),
                anhaenge_gesperrt=n.get("anhaenge_gesperrt", []))
    kurz["vorschlag"] = n["vorschlag"]
    if mit_original:
        kurz["original"] = n["original"]
        kurz["interpretation"] = n["interpretation"]
        kurz["extraktion"] = n.get("extraktion", [])
        kurz["historie"] = n.get("historie", [])
        kurz["offen"] = [f"{f['feld']}: {f['hinweis'] or 'Bestätigung nötig'}" for f in n.get("extraktion", []) if f["unsicher"]]
    return kurz


def zuweisen(w, daten, nachricht_id, vorgang, typ, jetzt=None):
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
    if jetzt:
        historie(n, jetzt, "zugewiesen", "nutzer", f"Vorgang {n['vorgang']}, Typ {n['mailtyp']}")
    return n


def schluessel_von(slug, art, eingetreten, referenz, typ):
    """The key that makes recording the same fact twice a no-op (R-01 3): same Vorgang, kind, day, source and reference."""
    return digest(slug, art, eingetreten or "-", referenz or "-", typ or "-")


def ereignis_bauen(nv, slug, art, eingetreten, quelle, original, interpretation, status, jetzt, methode, bestaetigung, **zusatz):
    """-> (event, new). One place that builds an event, so every writer fills the same fields. A fact already recorded gives back the first.

    `eingetreten_am` is when it happened (empty when unknown, never estimated), `erfasst` when the toolchain learned of it. `datum`
    stays as the older name of `eingetreten_am` for the files written before R-01."""
    referenz = quelle.get("nachricht_id") or quelle.get("referenz") or zusatz.get("beschreibung", "")[:40]
    schluessel = schluessel_von(slug, art, eingetreten, referenz, quelle.get("typ"))
    for e in nv["ereignisse"]:
        if e.get("schluessel") == schluessel and e.get("status") != "verworfen":
            return e, False
    ereignis = {"id": neues_id(nv["ereignisse"], "e"), "art": art, "datum": eingetreten or "", "eingetreten_am": eingetreten or "", "erfasst": stamp(jetzt),
                "quelle": quelle, "methode": methode, "bestaetigung": bestaetigung, "original": original, "interpretation": interpretation, "status": status,
                "bestaetigt_am": stamp(jetzt) if status in ("bestaetigt", "korrigiert") else "", "schluessel": schluessel}
    ereignis.update({k: v for k, v in zusatz.items() if v not in (None, "")})
    nv["ereignisse"].append(ereignis)
    return ereignis, True


def setze_meta(w, slug, schluessel, wert):
    """Set one key of the frontmatter of vorgang.md (the key line is replaced, a missing one is added); the body stays as it is."""
    pfad = vorgang_pfad(w, slug)
    with open(pfad, encoding="utf-8", newline="") as handle:
        text = handle.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    kopf = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not kopf:
        raise Refused("vorgang_ungueltig", "vorgang.md hat kein Frontmatter")
    zeile = f"{schluessel}: {wert}"
    if re.search(rf"^{re.escape(schluessel)}:.*$", kopf.group(1), re.M):
        neu = re.sub(rf"^{re.escape(schluessel)}:.*$", lambda _: zeile, kopf.group(1), count=1, flags=re.M)
    else:
        neu = kopf.group(1) + nl + zeile
    text = text[:kopf.start(1)] + neu + text[kopf.end(1):]
    temp = os.path.join(os.path.dirname(pfad), ".vorgang.md.tmp")
    try:
        with open(temp, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(temp, pfad)
    except OSError as error:
        raise Refused("speichern_fehlgeschlagen", f"vorgang.md nicht geschrieben: {redact(error)}")


def neues_id(liste, praefix):
    zahlen = [int(m.group(1)) for e in liste for m in [re.fullmatch(rf"{praefix}-(\d+)", str(e.get("id", "")))] if m]
    return f"{praefix}-{max(zahlen, default=0) + 1:03d}"


def historie(n, jetzt, ereignis, von="system", detail=""):
    """One line in the history of a message. Nothing is overwritten: a correction is a new line (MV-30)."""
    n.setdefault("historie", []).append({"am": stamp(jetzt), "ereignis": ereignis, "von": von, "detail": clean_text(detail, 160)})
    del n["historie"][:-60]


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


def waehle_fakten(n, optionen):
    """-> (adopted facts, deadline fact, appointment fact). Checked before anything is written (MV-29 rule 4)."""
    fakten = {f["feld"]: f for f in n.get("extraktion", [])}
    namen = [x.strip() for x in (optionen.get("uebernehmen") or "").split(",") if x.strip()]
    if optionen.get("frist_aus_nachricht") and "frist" not in namen:
        namen.append("frist")
    if optionen.get("termin_aus_nachricht") and "termin" not in namen:
        namen.append("termin")
    uebernahme = {}
    for name in namen:
        f = fakten.get(name)
        if f is None:
            raise Refused("extraktion_unbekannt", f"Die Nachricht enthält keine gelesene Angabe `{redact(name, 30)}` (vorhanden: {', '.join(sorted(fakten)) or 'keine'})")
        if f["unsicher"] and not optionen.get("trotz_unsicherheit"):
            raise Refused("extraktion_unsicher", f"`{name}` ist unsicher ({f['hinweis'] or 'Bestätigung nötig'}): prüfen und mit --trotz-unsicherheit ausdrücklich übernehmen, "
                                                 "oder die Angabe selbst eintragen (`wiedervorlage anlegen`)")
        uebernahme[name] = {k: f[k] for k in ("wert", "art", "quelle", "unsicher", "hinweis")}
    frist = fakten.get("frist") if optionen.get("frist_aus_nachricht") else None
    termin = fakten.get("termin") if optionen.get("termin_aus_nachricht") else None
    for name, f in (("frist", frist), ("termin", termin)):
        datum_ = (f["wert"].get("datum") if isinstance(f and f["wert"], dict) else f and f["wert"]) if f else None
        if f and not ss.valid_date(datum_ or ""):
            raise Refused("extraktion_ohne_datum", f"`{name}` hat kein Datum, das sich übernehmen ließe ({f['hinweis'] or 'relative Angabe'}): selbst eintragen")
    return uebernahme, frist, termin


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
    uebernahme, frist_fakt, termin_fakt = waehle_fakten(n, optionen)
    neu_status = jetzt_vorschlag["status_neu"] if not optionen.get("kein_status") else None
    zeilen = [z for z in jetzt_vorschlag["zeilen"] if neu_status or "→" not in z]
    nv = lade_nachverfolgung(w, slug)
    korrigiert = bool(n.get("manuell")) or bool(optionen.get("kategorie") or optionen.get("thema") or optionen.get("aussage"))
    ereignis, neues_ereignis = ereignis_bauen(nv, slug, jetzt_vorschlag["art"], n["datum"], {"typ": "nachricht", "nachricht_id": n["id"], "thread_id": n["thread_id"]}, n["original"],
                                    n["interpretation"], "korrigiert" if korrigiert else "bestaetigt", jetzt, "nachricht", "bestaetigt",
                                    gewissheit=n["gewissheit"], mailtyp=n["mailtyp"], status_vorher=jetzt_vorschlag["status_alt"], status_nachher=neu_status or "",
                                    extraktion=uebernahme or None,
                                    termin=(uebernahme.get("termin", {}).get("wert") or {}).get("datum") or None)
    if not neues_ereignis:
        raise Refused("bereits_erfasst", f"Dieselbe Tatsache ist schon als Ereignis {ereignis['id']} erfasst: verwerfen oder dort korrigieren, nicht doppelt übernehmen")
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
    # Dates the user took over from the text: a deadline the employer named stays marked as such; a proposed appointment is the user's own planning.
    for fakt_, anlass, verbindlichkeit, text in ((frist_fakt, "rueckmeldefrist", "arbeitgeber_frist", f"Frist laut Mail {n['mailtyp']} vom {n['datum']}"),
                                                 (termin_fakt, "gespraechstermin", "eigene_planung",
                                                  f"Termin laut Mail {n['mailtyp']} vom {n['datum']}; als Vorschlag des Arbeitgebers, nicht von der Nutzerin oder dem Nutzer zugesagt")):
        if fakt_:
            datum_ = fakt_["wert"]["datum"] if isinstance(fakt_["wert"], dict) else fakt_["wert"]
            if not any(r["anlass"] == anlass and r["faellig"] == datum_ and r["status"] == "offen" for r in nv["wiedervorlagen"]):
                nv["wiedervorlagen"].append({"id": neues_id(nv["wiedervorlagen"], "w"), "anlass": anlass, "faellig": datum_, "beschreibung": text,
                                             "quelle": {"typ": "nachricht", "nachricht_id": n["id"], "zitat": fakt_["quelle"]}, "status": "offen",
                                             "angelegt": stamp(jetzt), "verbindlichkeit": verbindlichkeit})
    schreibe_verlauf(w, slug, zeilen, neu_status)
    speichere_nachverfolgung(w, slug, nv)
    n["status"] = "korrigiert" if korrigiert else "bestaetigt"
    n["bestaetigung"] = {"am": stamp(jetzt), "von": "nutzer", "hash": hash_wert, "status_geaendert": neu_status, "ereignis": ereignis["id"]}
    for f in n.get("extraktion", []):
        f["bestaetigt"] = f["feld"] in uebernahme
    historie(n, jetzt, "bestaetigt" if not korrigiert else "korrigiert_bestaetigt", "nutzer",
             f"Ereignis {ereignis['id']}" + (f", übernommen: {', '.join(uebernahme)}" if uebernahme else ""))
    return {"ok": True, "nachricht": n["id"], "vorgang": slug, "ereignis": ereignis["id"], "status": neu_status or jetzt_vorschlag["status_alt"],
            "zeilen": zeilen, "wiedervorlage": bool(faellig and n["vorschlag"].get("folgeaufgabe")),
            "uebernommen": sorted(uebernahme), "wiedervorlagen_aus_nachricht": [x for x, f in (("frist", frist_fakt), ("termin", termin_fakt)) if f]}


def verwerfen(daten, nachricht_id, grund, jetzt):
    n = hole(daten, nachricht_id)
    if n["status"] != "vorgeschlagen":
        raise Refused("bereits_entschieden", f"{nachricht_id} ist schon {n['status']}")
    if not grund.strip():
        raise Refused("grund_fehlt", "--grund fehlt")
    n["status"] = "verworfen"
    n["bestaetigung"] = {"am": stamp(jetzt), "von": "nutzer", "grund": clean_text(grund, 200)}
    historie(n, jetzt, "verworfen", "nutzer", grund)
    return {"ok": True, "nachricht": nachricht_id, "status": "verworfen"}


# ---------------------------------------------------------------- Wiedervorlagen (7.3) and follow-up (8)

def wiedervorlage_anlegen(w, slug, anlass, faellig, beschreibung, jetzt, verbindlichkeit="eigene_planung"):
    vorgang_meta(w, slug)
    if anlass not in ANLAESSE:
        raise Refused("anlass_unbekannt", f"Anlass {redact(anlass, 40)} ist nicht bekannt ({', '.join(ANLAESSE)})")
    if ss.valid_date(faellig) != faellig or not faellig:
        raise Refused("datum_ungueltig", "--faellig ist ein echtes Datum der Form JJJJ-MM-TT: eine Frist legt die Nutzerin oder der Nutzer fest")
    if verbindlichkeit not in VERBINDLICHKEIT:
        raise Refused("verbindlichkeit_unbekannt", f"Verbindlichkeit {redact(verbindlichkeit, 40)} ist nicht bekannt ({', '.join(VERBINDLICHKEIT)})")
    nv = lade_nachverfolgung(w, slug)
    if any(r["anlass"] == anlass and r["faellig"] == faellig and r["status"] == "offen" for r in nv["wiedervorlagen"]):
        raise Refused("wiedervorlage_existiert", "Diese Wiedervorlage gibt es schon (Anlass und Datum)")
    eintrag = {"id": neues_id(nv["wiedervorlagen"], "w"), "anlass": anlass, "faellig": faellig, "beschreibung": clean_text(beschreibung, 160),
               "quelle": {"typ": "nutzer"}, "status": "offen", "angelegt": stamp(jetzt), "verbindlichkeit": verbindlichkeit}
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
    v.add_argument("--erneut", action="store_true", help="read still-proposed messages again (no new record, no event, no task)")
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
    b.add_argument("--uebernehmen", help="comma list of the read facts to take over (termin, frist, unterlagen, kontakt_name, format, ort, referenz)")
    b.add_argument("--trotz-unsicherheit", action="store_true", help="also take over a fact marked unsicher")
    b.add_argument("--frist-aus-nachricht", action="store_true", help="Wiedervorlage rueckmeldefrist from the deadline named in the mail")
    b.add_argument("--termin-aus-nachricht", action="store_true", help="Wiedervorlage gespraechstermin from the appointment named in the mail")
    vw = sub.add_parser("verwerfen")
    vw.add_argument("nachricht")
    vw.add_argument("--grund", default="")
    w = sub.add_parser("wiedervorlage")
    w.add_argument("aktion", choices=("anlegen", "erledigen", "verwerfen", "liste"))
    w.add_argument("vorgang")
    w.add_argument("--anlass")
    w.add_argument("--faellig", default="")
    w.add_argument("--text", default="")
    w.add_argument("--arbeitgeber-frist", action="store_true", help="the date is a deadline the employer named")
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
            return {"ok": True, **verarbeite(w, roh, now, args.erneut)}
        if befehl == "wiedervorlage":
            if args.aktion == "anlegen":
                return wiedervorlage_anlegen(w, args.vorgang, args.anlass or "", args.faellig, args.text, now,
                                             "arbeitgeber_frist" if args.arbeitgeber_frist else "eigene_planung")
            return wiedervorlage_abschliessen(w, args.vorgang, args.id or "", "erledigt" if args.aktion == "erledigen" else "verworfen", now)
        daten = lade_eingang(w)
        if befehl == "zuweisen":
            n = zuweisen(w, daten, args.nachricht, args.vorgang, args.typ, now)
            speichere_eingang(w, daten)
            return {"ok": True, "nachricht": ansicht(n), "hinweis": "Neuer Vorschlag: mit `bestaetigen --hash …` freigeben"}
        if befehl == "bestaetigen":
            ergebnis = bestaetigen(w, daten, args.nachricht, args.hash, {"kein_status": args.kein_status, "faellig": args.faellig,
                                                                        "kategorie": args.kategorie, "thema": args.thema, "aussage": args.aussage,
                                                                        "uebernehmen": args.uebernehmen, "trotz_unsicherheit": args.trotz_unsicherheit,
                                                                        "frist_aus_nachricht": args.frist_aus_nachricht, "termin_aus_nachricht": args.termin_aus_nachricht}, now)
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
