"""Tests of the evaluation of confirmed results `scripts/lernen.py` (spec ergebnisauswertung EA-1 to EA-14, A-06).

Groups: the statistics (counts, denominators, open applications, small data), response times, the document versions and the
separation of quality and result, the retrospective, results by the user's statement, proposals and their approval, the link to
the communication and the workflow. All data is invented (Musterfirma GmbH, Beispiel AG).
"""

import contextlib
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
import unittest.mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import kommunikation as km  # noqa: E402
import lernen as lr  # noqa: E402
import qualitaet as qa  # noqa: E402
import workflow as wf  # noqa: E402

NOW = "2026-10-26T10:00:00Z"


def ereignis(eid, art, datum="2026-10-10", status="bestaetigt", original="", interpretation=None):
    return {"id": eid, "art": art, "datum": datum, "status": status, "original": original, "interpretation": interpretation,
            "quelle": {"typ": "nutzer"}, "erfasst": NOW, "bestaetigt_am": NOW}


def inhalt(pfad):
    with open(pfad, "rb") as handle:
        return handle.read()


def grund(kategorie, thema=""):
    return {"kategorie": kategorie, "bezeichnung": kategorie, "thema": thema, "aussage": "", "sicherheit": "niedrig", "grund_genannt": True, "hinweis": "x"}


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.w = os.path.join(self._tmp.name, "wurzel")
        self.konfig = os.path.join(self._tmp.name, "konfiguration.md")
        os.makedirs(self.w)
        self.schreibe_konfig()

    def schreibe_konfig(self, extra=""):
        with open(self.konfig, "w", encoding="utf-8") as handle:
            handle.write(f"---\nwurzel: {self.w}\n{extra}---\n")

    def vorgang(self, slug, firma, status, versendet="2026-10-02", ereignisse=(), extra="", stelle="Senior Backend-Entwickler"):
        ordner = os.path.join(self.w, slug)
        os.makedirs(ordner, exist_ok=True)
        meta = f"firma: {firma}\nstelle: {stelle}\nstatus: {status}\n" + (f"versendet_am: {versendet}\n" if versendet else "") + extra
        with open(os.path.join(ordner, "vorgang.md"), "w", encoding="utf-8") as handle:
            handle.write(f"---\n{meta}---\n# V\n\n## Verlauf\n- 2026-10-02: x\n")
        if ereignisse:
            with open(os.path.join(ordner, "nachverfolgung.json"), "w", encoding="utf-8") as handle:
                json.dump({"version": 1, "ereignisse": list(ereignisse), "wiedervorlagen": []}, handle)

    def cli(self, modul, *argumente, umgebung=None, jetzt=NOW):
        out = io.StringIO()
        with unittest.mock.patch.dict(os.environ, umgebung or {}, clear=False), contextlib.redirect_stdout(out):
            code = modul.main(["x", "--konfiguration", self.konfig, "--jetzt", jetzt, *argumente])
        text = out.getvalue().strip()
        return code, (json.loads(text) if text.startswith("{") else text)

    def stat(self, *argumente):
        code, antwort = self.cli(lr, "statistik", *argumente)
        self.assertEqual(code, 0, antwort)
        return antwort

    def lies(self, *teile):
        with open(os.path.join(self.w, *teile), encoding="utf-8") as handle:
            return handle.read()

    def sechs(self):
        self.vorgang("a-offen", "Firma A", "versendet")
        self.vorgang("b-gespraech", "Firma B", "gespräch", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-10")])
        self.vorgang("c-absage", "Firma C", "absage", ereignisse=[ereignis("e-001", "absage", "2026-10-20")])
        self.vorgang("d-keine-antwort", "Firma D", "ohne Antwort")
        self.vorgang("e-zusage", "Firma E", "zusage")
        self.vorgang("f-nur-eingang", "Firma F", "versendet", ereignisse=[ereignis("e-001", "eingangsbestaetigung", "2026-10-03")])


class StatisticsTests(Base):
    def test_counts_denominators_and_open_applications(self):
        self.sechs()
        s = self.stat()
        z = s["zaehler"]
        self.assertEqual((z["bewerbungen"], z["offen"], z["abgeschlossen"]), (6, 3, 3))
        self.assertEqual((z["rueckmeldung"], z["absage"], z["einladung"], z["angebot"], z["einstellung"]), (3, 1, 2, 1, 1))
        self.assertEqual((z["offen_ohne_rueckmeldung"], z["ohne_antwort_abgeschlossen"]), (2, 1))
        q = s["ruecklaufquote"]
        self.assertEqual((q["zaehler"], q["nenner"], q["quote"], q["eingeschraenkt"]), (3, 6, 0.5, False))
        self.assertIn("Offene Bewerbungen stehen im Nenner", q["definition"])
        o = s["ruecklaufquote_ohne_offene"]
        self.assertEqual((o["zaehler"], o["nenner"], o["quote"]), (3, 4, 0.75))  # open applications are neither failures nor in this denominator
        self.assertEqual(s["uebergaenge"]["einladung_zu_angebot"]["zaehler"], 1)
        self.assertEqual(s["uebergaenge"]["einladung_zu_angebot"]["nenner"], 2)

    def test_a_bare_confirmation_of_receipt_is_no_reply_and_an_open_application_is_no_failure(self):
        self.vorgang("f", "Firma F", "versendet", ereignisse=[ereignis("e-001", "eingangsbestaetigung")])
        s = self.stat()
        self.assertEqual(s["zaehler"]["rueckmeldung"], 0)
        self.assertEqual(s["zaehler"]["absage"], 0)
        self.assertEqual(s["antwortzeiten"]["eingangsbestaetigung"]["n"], 1)
        self.assertEqual(s["antwortzeiten"]["erste_rueckmeldung"]["n"], 0)

    def test_small_numbers_are_marked_as_limited(self):
        self.vorgang("a", "Firma A", "gespräch")
        s = self.stat()
        self.assertTrue(s["ruecklaufquote"]["eingeschraenkt"])
        self.assertIn("Momentaufnahme", s["ruecklaufquote"]["hinweis"])
        self.assertTrue(any("5 Bewerbungen" in g for g in s["grenzen"]))

    def test_the_population_is_the_dispatched_applications_in_the_period_without_data_due_for_deletion(self):
        self.vorgang("a", "Firma A", "versendet", versendet="2026-09-01")
        self.vorgang("b", "Firma B", "versendet", versendet="2026-10-05")
        self.vorgang("c", "Firma C", "erstellt", versendet="")
        self.vorgang("d", "Firma D", "versendet", versendet="")
        self.vorgang("e", "Firma E", "absage", versendet="2026-10-05", extra="loeschen_ab: 2026-10-01\n")
        s = self.stat("--von", "2026-10-01")
        self.assertEqual(s["ausgewertet"], 1)
        self.assertEqual(s["datenqualitaet"]["ausgeschlossen"], {"ausserhalb_zeitraum": 1, "nicht_versendet": 1, "versendet_am_fehlt": 1, "loeschfrist_erreicht": 1})
        self.assertEqual(self.stat("--status", "absage")["ausgewertet"], 0)

    def test_unconfirmed_discarded_and_unchecked_results_are_not_counted(self):
        self.vorgang("a", "Firma A", "versendet", ereignisse=[ereignis("e-001", "absage", status="erkannt"), ereignis("e-002", "gespraechseinladung", status="zur_pruefung"),
                                                             ereignis("e-003", "angebot", status="verworfen")])
        s = self.stat()
        self.assertEqual((s["zaehler"]["absage"], s["zaehler"]["einladung"], s["zaehler"]["angebot"]), (0, 0, 0))
        self.assertEqual(s["datenqualitaet"]["ereignisse_zur_pruefung"], 2)
        self.assertEqual(s["zaehler"]["offen_ohne_rueckmeldung"], 1)

    def test_a_result_that_only_the_status_states_is_counted_and_shown_as_such(self):
        self.vorgang("a", "Firma A", "absage")
        s = self.stat()
        self.assertEqual(s["zaehler"]["absage"], 1)
        self.assertEqual(s["datenqualitaet"]["ergebnis_nur_durch_status"], 1)

    def test_the_statistics_are_reproducible_and_marked_as_derived(self):
        self.sechs()
        erste, zweite = self.stat(), self.stat()
        self.assertEqual(erste, zweite)
        self.assertTrue(erste["abgeleitet"])
        self.vorgang("a-offen", "Firma A", "versendet", extra="tags: [x]\n")
        self.assertNotEqual(self.stat()["quellen_hash"], erste["quellen_hash"])  # a changed source gives another hash

    def test_segments_group_by_the_data_that_exists_and_flag_small_groups(self):
        self.sechs()
        s = self.stat("--nach", "arbeitgeber")
        self.assertEqual(sorted(s["segmente"]["gruppen"]), [f"Firma {c}" for c in "ABCDEF"])
        self.assertTrue(all(not g["vergleichbar"] for g in s["segmente"]["gruppen"].values()))
        self.assertIn("nur vergleichbar, wenn sie ähnliche Stellen", self.stat("--nach", "zeitraum")["segmente"]["hinweis"])
        self.assertEqual(self.stat("--nach", "zeitraum")["segmente"]["gruppen"]["2026-10"]["bewerbungen"], 6)

    def test_a_filter_by_employer_and_profile_only_uses_the_data_that_exists(self):
        self.vorgang("a", "Musterfirma GmbH", "versendet", extra="profil: backend\n")
        self.vorgang("b", "Beispiel AG", "versendet", extra="tags: [profil:admin]\n")
        self.assertEqual(self.stat("--arbeitgeber", "musterfirma gmbh")["ausgewertet"], 1)
        self.assertEqual(self.stat("--stellenprofil", "admin")["ausgewertet"], 1)
        self.assertEqual(self.stat("--nach", "stellenprofil")["segmente"]["gruppen"].keys(), {"backend", "admin"})


class ResponseTimeTests(Base):
    def test_response_times_come_only_from_dates_that_exist_and_are_never_estimated(self):
        self.vorgang("a", "A", "gespräch", versendet="2026-10-01", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-09")])
        self.vorgang("b", "B", "gespräch", versendet="2026-10-01", ereignisse=[ereignis("e-001", "gespraechseinladung", "")])
        self.vorgang("c", "C", "gespräch", versendet="2026-10-10", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-05")])
        self.vorgang("d", "D", "versendet", versendet="2026-10-01")
        z = self.stat()["antwortzeiten"]["einladung"]
        self.assertEqual((z["n"], z["median_tage"], z["ohne_datum"], z["datum_vor_versand"]), (1, 8, 1, 1))
        self.assertTrue(z["eingeschraenkt"])

    def test_the_kinds_of_reply_are_kept_apart(self):
        self.vorgang("a", "A", "absage", versendet="2026-10-01", ereignisse=[ereignis("e-001", "eingangsbestaetigung", "2026-10-02"), ereignis("e-002", "absage", "2026-10-15")])
        a = self.stat()["antwortzeiten"]
        self.assertEqual((a["eingangsbestaetigung"]["median_tage"], a["absage"]["median_tage"], a["erste_rueckmeldung"]["median_tage"]), (1, 14, 14))
        self.assertEqual(a["einladung"]["n"], 0)


class VersionTests(Base):
    def schreibe_bericht(self, slug, gesamt="BEREIT"):
        ordner = os.path.join(self.w, slug)
        with open(os.path.join(ordner, "lebenslauf.md"), "w", encoding="utf-8") as handle:
            handle.write("# CV\n")
        bericht = {"stand": "abcdef123456789", "gesamt": gesamt, "dokumente": qa.dokument_hashes(ordner), "exporte": qa.export_hashes(ordner), "ats": {"umfang": "teilweise"}}
        with open(os.path.join(ordner, "qualitaet.json"), "w", encoding="utf-8") as handle:
            json.dump(bericht, handle)

    def test_a_version_is_unambiguous_only_with_a_current_report_and_named_attachments(self):
        self.vorgang("a", "A", "versendet", extra="anhaenge: [lebenslauf.pdf]\n")
        self.vorgang("b", "B", "versendet", extra="anhaenge: [lebenslauf.pdf]\n")
        self.vorgang("c", "C", "versendet")
        self.schreibe_bericht("a")
        self.schreibe_bericht("b")
        self.schreibe_bericht("c")
        with open(os.path.join(self.w, "b", "lebenslauf.md"), "a", encoding="utf-8") as handle:
            handle.write("später geändert\n")
        gruppen = self.stat("--nach", "dokumentversion")["segmente"]["gruppen"]
        self.assertEqual({k: v["bewerbungen"] for k, v in gruppen.items()}, {"abcdef123456": 1, "nicht_eindeutig": 2})
        self.assertEqual(self.stat()["datenqualitaet"]["dokumentversion_nicht_eindeutig"], 2)

    def test_a_passed_quality_check_does_not_change_the_result_numbers(self):
        for gesamt in ("BEREIT", "BLOCKIERT"):
            self.vorgang("a", "A", "absage", extra="anhaenge: [x.pdf]\n")
            self.schreibe_bericht("a", gesamt)
            s = self.stat()
            self.assertEqual((s["zaehler"]["absage"], s["ruecklaufquote"]["quote"]), (1, 1.0))
        text = json.dumps(self.stat())
        self.assertNotIn("qualitaet_gesamt", text)  # quality and result stay apart; the statistics make no statement about causes


class RetrospectiveTests(Base):
    def test_the_retrospective_documents_its_basis_and_marks_itself_as_derived(self):
        self.sechs()
        code, antwort = self.cli(lr, "retrospektive", "--von", "2026-10-01")
        self.assertEqual((code, antwort["datei"]), (0, "lernen/retrospektive-2026-10-26.md"))
        text = self.lies("lernen", "retrospektive-2026-10-26.md")
        self.assertIn("abgeleitet: ja", text)
        for erwartet in ("## Datenbasis", "Zeitraum (nach Versanddatum): 2026-10-01 bis offen", "Ausgewertete Vorgänge: 6", "Offene Vorgänge: 3",
                         "## Vergleichbarkeit", "## Einschränkungen", "Offene Bewerbungen sind nicht erfolglos"):
            self.assertIn(erwartet, text)
        self.assertEqual(len(re.findall(r"quellen_hash: [0-9a-f]{64}", text)), 1)

    def test_a_refusal_without_a_reason_stays_unknown_and_nothing_is_called_a_cause(self):
        self.vorgang("a", "A", "absage", ereignisse=[ereignis("e-001", "absage", "2026-10-20", original="Leider eine Absage.",
                                                              interpretation={"kategorie": "unbekannt", "bezeichnung": "unbekannter Grund", "grund_genannt": False, "thema": "", "aussage": "", "sicherheit": "niedrig"})])
        self.vorgang("b", "B", "absage", ereignisse=[ereignis("e-001", "absage", "2026-10-21", original="Wir suchen mehr Erfahrung im Betrieb von Kubernetes.",
                                                              interpretation=grund("beruf_erfahrung"))])
        self.cli(lr, "retrospektive")
        text = self.lies("lernen", "retrospektive-2026-10-26.md")
        self.assertIn("kein Grund genannt: Grund unbekannt", text)
        self.assertIn("Muster im Wortlaut, nicht bestätigt", text)
        self.assertIn("Kein Thema wurde in mindestens zwei Vorgängen genannt", text)
        self.assertNotRegex(text, r"führte zu|verursacht|aufgrund Ihrer|liegt an|wegen der Unterlagen")

    def test_a_theme_named_in_two_applications_is_shown_as_a_count_not_as_a_cause(self):
        for slug in ("a", "b"):
            self.vorgang(slug, slug.upper(), "absage", ereignisse=[ereignis("e-001", "absage", interpretation=grund("beruf_erfahrung", "Kubernetes Operations"))])
        self.cli(lr, "retrospektive")
        text = self.lies("lernen", "retrospektive-2026-10-26.md")
        self.assertIn("Kubernetes Operations: in 2 Vorgängen genannt", text)
        self.assertIn("Das ist eine Häufung der Aussagen, keine Ursache", text)

    def test_a_changed_source_makes_the_retrospective_stale(self):
        self.sechs()
        self.cli(lr, "retrospektive")
        self.assertTrue(self.cli(lr, "aktualitaet", "lernen/retrospektive-2026-10-26.md")[1]["aktuell"])
        self.vorgang("a-offen", "Firma A", "absage")
        antwort = self.cli(lr, "aktualitaet", "lernen/retrospektive-2026-10-26.md")[1]
        self.assertFalse(antwort["aktuell"])
        self.assertIn("neu erstellen", antwort["hinweis"])

    def test_the_retrospective_writes_only_into_the_lernen_folder(self):
        self.sechs()
        vorher = {os.path.join(d, f): inhalt(os.path.join(d, f)) for d, _, fs in os.walk(self.w) for f in fs}
        self.cli(lr, "retrospektive")
        nachher = {os.path.join(d, f) for d, _, fs in os.walk(self.w) for f in fs} - set(vorher)
        self.assertTrue(all(os.sep + "lernen" + os.sep in p for p in nachher if not p.endswith(".lock")), nachher)
        self.assertTrue(all(inhalt(p) == b for p, b in vorher.items()))


class ResultByStatementTests(Base):
    def test_a_result_stated_by_the_user_is_recorded_with_a_verlauf_line_and_the_status_stays(self):
        self.vorgang("a", "A", "gespräch")
        code, antwort = self.cli(lr, "ergebnis", "erfassen", "a", "--art", "technisches_gespraech", "--datum", "2026-10-20", "--original", "Gespräch mit dem Team", "--ja")
        self.assertEqual((code, antwort["ereignis"]["status"]), (0, "bestaetigt"))
        text = self.lies("a", "vorgang.md")
        self.assertIn("status: gespräch", text)
        self.assertIn("Ergebnis erfasst: technisches_gespraech (Ereignis e-001", text)
        self.assertEqual(self.stat()["zaehler"]["gespraech"], 1)

    def test_a_missing_date_is_not_estimated_and_an_unknown_kind_is_refused(self):
        self.vorgang("a", "A", "gespräch")
        self.assertEqual(self.cli(lr, "ergebnis", "erfassen", "a", "--art", "gespraech", "--ja")[1]["code"], "datum_ungueltig")
        self.assertEqual(self.cli(lr, "ergebnis", "erfassen", "a", "--art", "triumph", "--datum", "2026-10-20", "--ja")[1]["code"], "art_unbekannt")
        self.assertEqual(self.cli(lr, "ergebnis", "erfassen", "a", "--art", "gespraech", "--datum", "2026-13-40", "--ja")[1]["code"], "datum_ungueltig")

    def test_a_result_needs_the_yes_and_an_interactive_session(self):
        self.vorgang("a", "A", "gespräch")
        self.assertEqual(self.cli(lr, "ergebnis", "erfassen", "a", "--art", "gespraech", "--datum", "2026-10-20")[1]["code"], "freigabe_fehlt")
        for variable in ("WORKFLOW_UNBEAUFSICHTIGT", "STELLENSUCHE_GEPLANT"):
            antwort = self.cli(lr, "ergebnis", "erfassen", "a", "--art", "gespraech", "--datum", "2026-10-20", "--ja", umgebung={variable: "1"})[1]
            self.assertEqual(antwort["code"], "nur_interaktiv")
        self.assertNotIn("nachverfolgung.json", os.listdir(os.path.join(self.w, "a")))

    def test_a_correction_keeps_the_old_value_and_a_discarded_result_leaves_the_statistics(self):
        self.vorgang("a", "A", "gespräch", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-09")])
        self.cli(lr, "ergebnis", "korrigieren", "a", "--id", "e-001", "--art", "gespraech", "--datum", "2026-10-11", "--grund", "falsch eingetragen", "--ja")
        e = json.loads(self.lies("a", "nachverfolgung.json"))["ereignisse"][0]
        self.assertEqual((e["art"], e["datum"], e["status"], e["korrekturen"][0]["vorher"]["art"]), ("gespraech", "2026-10-11", "korrigiert", "gespraechseinladung"))
        self.assertEqual(self.stat()["zaehler"]["gespraech"], 1)
        self.cli(lr, "ergebnis", "verwerfen", "a", "--id", "e-001", "--ja")
        s = self.stat()["zaehler"]
        self.assertEqual((s["gespraech"], s["einladung"]), (0, 1))  # the status `gespräch` still states an invitation; the discarded event no longer counts
        self.assertEqual(self.cli(lr, "ergebnis", "korrigieren", "a", "--id", "e-001", "--art", "angebot", "--ja")[1]["code"], "bereits_verworfen")

    def test_the_same_event_is_not_processed_twice_from_a_mail(self):
        self.vorgang("a", "Musterfirma GmbH", "versendet", extra="ref_nr: 77\n")
        datei = os.path.join(self._tmp.name, "m.json")
        with open(datei, "w", encoding="utf-8") as handle:
            json.dump([{"id": "m1", "thread_id": "t", "von": "jobs@musterfirma.example", "betreff": "Absage 77", "datum": "2026-10-20", "text": "Leider eine Absage."}], handle)
        self.cli(km, "verarbeiten", "--nachrichten", datei)
        h = self.cli(km, "zeige", "m1")[1]["nachricht"]["vorschlag"]["hash"]
        self.assertEqual(self.stat()["zaehler"]["absage"], 0)  # a proposal is no result
        self.assertEqual(self.cli(km, "bestaetigen", "m1", "--hash", h, "--ja")[0], 0)
        self.assertEqual(self.stat()["zaehler"]["absage"], 1)
        self.assertEqual(self.cli(km, "bestaetigen", "m1", "--hash", h, "--ja")[1]["code"], "bereits_entschieden")
        self.assertEqual(self.stat()["zaehler"]["absage"], 1)
        self.assertEqual(self.stat()["datenqualitaet"]["ergebnis_nur_durch_status"], 0)


class ProposalTests(Base):
    def zwei_absagen(self, thema="Kubernetes Operations"):
        for slug in ("a", "b"):
            self.vorgang(slug, slug.upper(), "absage", ereignisse=[ereignis("e-001", "absage", interpretation=grund("beruf_erfahrung", thema))])

    def erzeuge(self, regel=None):
        """Run the rules; with `regel` only the new proposals of that rule (the version rule fires on every fixture without a report)."""
        antwort = self.cli(lr, "vorschlaege", "erzeugen")[1]
        if regel:
            regeln = {v["id"]: v["regel"] for v in self.cli(lr, "vorschlaege", "liste")[1]["vorschlaege"]}
            antwort["neu"] = [i for i in antwort["neu"] if regeln[i].startswith(regel)]
            antwort["veraltet"] = antwort["veraltet"]
        return antwort

    def test_a_proposal_names_observation_sources_reasons_and_uncertainty(self):
        self.zwei_absagen()
        self.assertEqual(len(self.erzeuge("thema:")["neu"]), 1)
        v = next(v for v in self.cli(lr, "vorschlaege", "liste")[1]["vorschlaege"] if v["regel"].startswith("thema:"))
        for feld in ("id", "titel", "beschreibung", "bereich", "beobachtung", "quellen", "begruendung", "erwarteter_nutzen", "unsicherheit", "risiken", "prioritaet", "status"):
            self.assertTrue(v[feld], feld)
        self.assertEqual((v["status"], sorted(q["vorgang"] for q in v["quellen"])), ("erstellt", ["a", "b"]))
        self.assertIn("kein Beleg für eine Ursache", v["unsicherheit"])
        self.assertIn("Qualifikation", v["risiken"])
        self.assertEqual(self.erzeuge("thema:")["neu"], [])  # the same observation gives no second proposal

    def test_no_proposal_comes_from_one_case_or_from_a_missing_reason(self):
        self.vorgang("a", "A", "absage", ereignisse=[ereignis("e-001", "absage", interpretation=grund("beruf_erfahrung", "X"))])
        self.vorgang("b", "B", "absage", ereignisse=[ereignis("e-001", "absage", interpretation={"kategorie": "unbekannt", "bezeichnung": "u", "grund_genannt": False, "thema": ""})])
        self.assertEqual(self.erzeuge("thema:")["neu"], [])

    def test_a_proposal_is_shown_first_and_decided_only_with_the_yes_of_the_user(self):
        self.zwei_absagen()
        vid = self.erzeuge("thema:")["neu"][0]
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "ok", "--ja")[1]["code"], "uebergang_nicht_erlaubt")
        self.cli(lr, "vorschlag", "vorlegen", vid)
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "ok")[1]["code"], "freigabe_fehlt")
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "", "--ja")[1]["code"], "grund_fehlt")
        for variable in ("WORKFLOW_UNBEAUFSICHTIGT", "STELLENSUCHE_GEPLANT"):
            self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "ok", "--ja", umgebung={variable: "1"})[1]["code"], "nur_interaktiv")
        self.assertEqual(self.cli(lr, "vorschlag", "zeige", vid)[1]["vorschlag"]["status"], "zur_pruefung")

    def test_an_accepted_proposal_changes_no_personal_data_and_no_document(self):
        grundlage = os.path.join(self.w, "grundlage")
        os.makedirs(grundlage)
        for name in ("erfahren.md", "profil.md"):
            with open(os.path.join(self.w, name if name == "profil.md" else "grundlage/" + name), "w", encoding="utf-8") as handle:
                handle.write("Station A\n")
        self.zwei_absagen()
        vor = {d + f: hashlib.sha256(inhalt(os.path.join(d, f))).hexdigest() for d, _, fs in os.walk(self.w) for f in fs if "lernen" not in d and not f.endswith(".lock")}
        vid = self.erzeuge("thema:")["neu"][0]
        self.cli(lr, "vorschlag", "vorlegen", vid)
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "wird geprüft", "--ja")[0], 0)
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "umgesetzt", "--grund", "Stellenprüfung angepasst", "--ja")[1]["status"], "umgesetzt")
        nach = {d + f: hashlib.sha256(inhalt(os.path.join(d, f))).hexdigest() for d, _, fs in os.walk(self.w) for f in fs if "lernen" not in d and not f.endswith(".lock")}
        self.assertEqual(nach, vor)
        daten = json.loads(self.lies("lernen", "vorschlaege.json"))
        self.assertFalse(any(v["aendert_stammdaten"] for v in daten["vorschlaege"].values()))

    def test_a_rejected_proposal_cannot_be_carried_out_and_is_not_proposed_again(self):
        self.zwei_absagen()
        vid = self.erzeuge("thema:")["neu"][0]
        self.cli(lr, "vorschlag", "vorlegen", vid)
        self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "abgelehnt", "--grund", "nicht sinnvoll", "--ja")
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "umgesetzt", "--grund", "doch", "--ja")[1]["code"], "uebergang_nicht_erlaubt")
        self.assertEqual(self.cli(lr, "vorschlag", "vorlegen", vid)[1]["code"], "uebergang_nicht_erlaubt")
        self.assertEqual(self.erzeuge("thema:")["neu"], [])
        self.assertEqual(self.cli(lr, "vorschlag", "zeige", vid)[1]["vorschlag"]["status"], "abgelehnt")

    def test_a_deferred_proposal_comes_back_and_a_proposal_cannot_skip_the_review(self):
        self.zwei_absagen()
        vid = self.erzeuge("thema:")["neu"][0]
        self.cli(lr, "vorschlag", "vorlegen", vid)
        self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "zurueckgestellt", "--grund", "später", "--ja")
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "jetzt", "--ja")[1]["code"], "uebergang_nicht_erlaubt")
        self.assertEqual(self.cli(lr, "vorschlag", "vorlegen", vid)[1]["vorschlag"]["status"], "zur_pruefung")

    def test_a_proposal_goes_stale_when_a_source_changes_or_is_due_for_deletion(self):
        self.zwei_absagen()
        vid = self.erzeuge("thema:")["neu"][0]
        self.cli(lr, "vorschlag", "vorlegen", vid)
        self.vorgang("a", "A", "absage", ereignisse=[ereignis("e-001", "absage", status="verworfen", interpretation=grund("beruf_erfahrung", "Kubernetes Operations"))])
        antwort = self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "ok", "--ja")[1]
        self.assertEqual(antwort["code"], "uebergang_nicht_erlaubt")
        self.assertEqual(self.cli(lr, "vorschlag", "zeige", vid)[1]["vorschlag"]["status"], "veraltet")
        self.zwei_absagen("Terraform")
        neu = self.erzeuge("thema:")["neu"][0]
        self.vorgang("b", "B", "absage", extra="loeschen_ab: 2026-10-01\n", ereignisse=[ereignis("e-001", "absage", interpretation=grund("beruf_erfahrung", "Terraform"))])
        self.assertIn(neu, self.erzeuge()["veraltet"])

    def test_the_rules_need_no_made_up_deadline(self):
        self.vorgang("a", "A", "versendet", versendet="2026-01-01")
        self.assertEqual(self.erzeuge("nachfassen:")["neu"], [])  # without nachfass_tage there is no "too long without reply"
        self.schreibe_konfig("nachfass_tage: 30\n")
        neu = self.erzeuge("nachfassen:")["neu"]
        self.assertEqual(len(neu), 1)
        v = self.cli(lr, "vorschlag", "zeige", neu[0])[1]["vorschlag"]
        self.assertIn("nachfass_tage", v["beschreibung"])
        self.assertIn("Freigabe", v["risiken"])

    def test_the_workflow_asks_for_the_decision_and_closes_the_task_with_it(self):
        self.zwei_absagen()
        ids = self.erzeuge()["neu"]
        neu = self.cli(wf, "laufen")[1]["neu"]
        self.assertIn("lernvorschlag_pruefen:lernen:n1", neu)
        self.assertEqual(self.cli(wf, "laufen")[1]["neu"].count("lernvorschlag_pruefen:lernen:n1"), 0)
        for vid in ids:
            self.cli(lr, "vorschlag", "vorlegen", vid)
        self.cli(wf, "abgleichen")
        self.assertEqual(self.cli(wf, "zeige", "lernvorschlag_pruefen:lernen:n1")[1]["aufgabe"]["status"], "bereit")  # open until every proposal is decided
        for vid in ids:
            self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "abgelehnt", "--grund", "nein", "--ja")
        self.cli(wf, "abgleichen")
        self.assertEqual(self.cli(wf, "zeige", "lernvorschlag_pruefen:lernen:n1")[1]["aufgabe"]["status"], "erledigt")


class SafetyTests(unittest.TestCase):
    def test_the_evaluation_sends_nothing_calls_no_tool_and_reads_no_profile(self):
        quelle = inhalt(os.path.join(ROOT, "scripts", "lernen.py")).decode("utf-8")
        imports = set(re.findall(r"^(?:import|from) (\w+)", quelle, re.M))
        self.assertFalse(imports & {"socket", "smtplib", "urllib", "http", "requests", "ssl", "ftplib", "imaplib", "subprocess", "webbrowser", "workflow"}, imports)
        self.assertNotIn("grundlage_laden", quelle)
        self.assertNotIn("profil.md", quelle.replace("`profil.md`", ""))


if __name__ == "__main__":
    unittest.main()
