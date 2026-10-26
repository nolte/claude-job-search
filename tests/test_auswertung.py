"""Tests of the statistical evaluation and the controlled improvement of R-03 (spec ergebnisauswertung EA-17 to EA-24; scripts/lernen.py).

Groups: the funnel and its conversions, maturity and small samples, times from stored dates, filters and unknown features, the traceability of a figure,
data quality, the retrospective A to D, proposals with their check of effect, and the safety rules (nothing is changed, nothing is sent). All data is
invented (Musterfirma GmbH, Beispiel AG). The workflow store and the Warteschlange are written as files, as the real tools write them.
"""

import json
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bewerbung as bw  # noqa: E402
import lernen as lr  # noqa: E402
import workflow as wf  # noqa: E402
from test_lernen import NOW, Base, ereignis, grund, inhalt  # noqa: E402


def stelle(sid, bearbeitung="offen", veto=False, tag="2026-09-01T08:00:00Z", vorgang=""):
    return {"id": sid, "bearbeitung": bearbeitung, "vorpruefung": {"geprueft": True, "veto": [{"feld": "ort"}] if veto else [], "unklar": []}, "unvollstaendig": [],
            "signale": [], "erstmals_gesehen": tag, "vorgang": vorgang}


class Funnel(Base):
    def queue(self, *stellen):
        os.makedirs(os.path.join(self.w, "suche"), exist_ok=True)
        with open(os.path.join(self.w, "suche", "warteschlange.json"), "w", encoding="utf-8") as handle:
            json.dump({"version": 1, "stellen": {s["id"]: s for s in stellen}}, handle)

    def workflow(self, *slugs):
        os.makedirs(os.path.join(self.w, "workflow"), exist_ok=True)
        aufgaben = {f"versand_freigabe:{s}": {"id": f"versand_freigabe:{s}", "typ": "versand_freigabe", "status": "erledigt", "entscheidung": {"art": "erteilt", "kontext_hash": "x"}}
                    for s in slugs}
        with open(os.path.join(self.w, "workflow", "aufgaben.json"), "w", encoding="utf-8") as handle:
            json.dump({"version": 1, "aufgaben": aufgaben}, handle)

    def konv(self, antwort, name):
        return next(c for c in antwort["konversionen"] if c["name"] == name)

    def prozess(self):
        """Seven begun: one only recorded, one created, five dispatched with different courses."""
        self.vorgang("g-erfasst", "Firma G", "erfasst", versendet="", extra="erfasst: 2026-08-01\n")
        self.vorgang("h-erstellt", "Firma H", "erstellt", versendet="", extra="erfasst: 2026-10-01\n")
        self.vorgang("a-offen", "Firma A", "versendet", versendet="2026-08-01", extra="erfasst: 2026-07-20\n")
        self.vorgang("b-gespraech", "Firma B", "angebot", versendet="2026-09-01", extra="erfasst: 2026-08-25\n",
                     ereignisse=[ereignis("e-001", "eingangsbestaetigung", "2026-09-02"), ereignis("e-002", "gespraechseinladung", "2026-09-10"),
                                 ereignis("e-003", "gespraech", "2026-09-20"), ereignis("e-004", "angebot", "2026-09-30"), ereignis("e-005", "angebot_angenommen", "2026-10-05")])
        self.vorgang("c-absage", "Firma C", "absage", versendet="2026-09-05", extra="erfasst: 2026-09-01\n", ereignisse=[ereignis("e-001", "absage", "2026-09-25")])
        self.vorgang("d-einladung", "Firma D", "gespräch", versendet="2026-10-20", extra="erfasst: 2026-10-15\n", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-24")])
        self.vorgang("e-jung", "Firma E", "versendet", versendet="2026-10-23", extra="erfasst: 2026-10-20\n")

    def test_empty_data_gives_zeros_and_no_rate_instead_of_an_error(self):
        s = self.stat()
        self.assertEqual((s["ausgewertet"], s["population"]["begonnen"]), (0, 0))
        k = self.konv(s, "eingereicht_zu_rueckmeldung")
        self.assertEqual((k["zaehler"], k["nenner"], k["quote"], k["konfidenz95"]), (0, 0, None, None))
        self.assertTrue(k["eingeschraenkt"])
        self.assertEqual(s["aktivitaet"]["bewerbungen_begonnen"]["n"], 0)

    def test_the_funnel_counts_what_happened_and_keeps_the_stages_apart(self):
        self.prozess()
        a = self.stat()["aktivitaet"]
        self.assertEqual(a["bewerbungen_begonnen"]["n"], 7)
        self.assertEqual(a["unterlagen_fertig"]["n"], 6)  # created or dispatched; a Vorgang that is only recorded is not
        self.assertEqual(a["eingereicht"]["n"], 5)  # a finished application is not a dispatched one
        self.assertEqual((a["eingangsbestaetigung"]["n"], a["arbeitgeberantworten"]["n"], a["absagen"]["n"]), (1, 3, 1))
        self.assertEqual((a["einladungen"]["n"], a["gespraeche_gefuehrt"]["n"]), (2, 1))  # an invitation is not a held interview
        self.assertEqual((a["angebote"]["n"], a["angebote_angenommen"]["n"], a["angebote_abgelehnt"]["n"]), (1, 1, 0))
        self.assertEqual(a["offen_ohne_rueckmeldung"]["n"], 2)  # no reply known is neither a refusal nor a failure
        self.assertEqual(a["absagen"]["n"], 1)

    def test_the_conversions_have_traceable_numerators_and_denominators(self):
        self.prozess()
        s = self.stat()
        for name, zaehler, nenner in (("begonnen_zu_fertig", 6, 7), ("fertig_zu_eingereicht", 5, 6), ("eingereicht_zu_eingangsbestaetigung", 1, 5),
                                      ("eingereicht_zu_rueckmeldung", 3, 5), ("eingereicht_zu_einladung", 2, 5), ("gespraech_zu_angebot", 1, 1), ("angebot_zu_angenommen", 1, 1)):
            k = self.konv(s, name)
            self.assertEqual((k["zaehler"], k["nenner"]), (zaehler, nenner), name)
            self.assertTrue(k["definition"])

    def test_the_queue_and_the_workflow_feed_the_early_stages_when_they_exist(self):
        self.prozess()
        self.queue(stelle("s1", "übernommen", vorgang="b-gespraech"), stelle("s2"), stelle("s3", "abgelehnt"), stelle("s4", veto=True), stelle("s5", "übernommen", vorgang="a-offen"))
        self.workflow("a-offen", "b-gespraech")
        s = self.stat()
        a = s["aktivitaet"]
        self.assertEqual((a["stellen_recherchiert"]["n"], a["stellen_relevant"]["n"], a["stellen_uebernommen"]["n"]), (5, 3, 2))  # refused and vetoed are not relevant
        self.assertEqual(a["freigegeben"]["n"], 2)
        k = self.konv(s, "relevant_zu_begonnen")
        self.assertEqual((k["zaehler"], k["nenner"]), (2, 3))

    def test_without_a_queue_or_workflow_the_early_stages_are_not_recorded_and_not_guessed(self):
        self.prozess()
        a = self.stat()["aktivitaet"]
        self.assertIsNone(a["stellen_recherchiert"]["n"])
        self.assertIsNone(a["freigegeben"]["n"])
        self.assertIn("nicht erfasst", a["stellen_recherchiert"]["hinweis"])

    def test_several_events_of_one_application_count_once_and_a_status_alone_counts_too_but_is_marked(self):
        self.vorgang("m", "Firma M", "gespräch", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-05"), ereignis("e-002", "gespraechseinladung", "2026-10-06"),
                                                             ereignis("e-003", "absage", "2026-10-10")])
        self.vorgang("n", "Firma N", "zusage")
        s = self.stat()
        self.assertEqual((s["zaehler"]["einladung"], s["zaehler"]["absage"]), (2, 1))  # M counted once for the invitation; N by its status
        self.assertEqual(s["datenqualitaet"]["ergebnis_nur_durch_status"], 1)


class Maturity(Base):
    def test_a_fresh_application_does_not_distort_the_rate_unnoticed(self):
        self.vorgang("alt-ohne", "Firma A", "versendet", versendet="2026-08-01")
        self.vorgang("alt-mit", "Firma B", "gespräch", versendet="2026-08-05", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-08-20")])
        self.vorgang("jung-ohne", "Firma C", "versendet", versendet="2026-10-24")
        self.vorgang("jung-mit", "Firma D", "gespräch", versendet="2026-10-22", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-25")])
        k = next(c for c in self.stat()["konversionen"] if c["name"] == "eingereicht_zu_einladung")
        self.assertEqual((k["zaehler"], k["nenner"]), (2, 4))
        r = k["reif"]
        self.assertEqual((r["zaehler"], r["nenner"], r["noch_jung"], r["noch_jung_mit_ereignis"], r["reife_tage"]), (1, 2, 2, 1, 28))

    def test_the_maturity_is_a_stated_convention_and_can_be_changed(self):
        self.vorgang("a", "Firma A", "versendet", versendet="2026-10-10")
        self.assertEqual(self.stat()["konversionen"][2]["reif"]["nenner"], 0)  # 16 days old: younger than 28
        code, antwort = self.cli(lr, "statistik", "--reife-tage", "10")
        self.assertEqual(antwort["reife_tage"], 10)
        self.assertEqual(next(c for c in antwort["konversionen"] if c["name"] == "eingereicht_zu_rueckmeldung")["reif"]["nenner"], 1)
        self.assertEqual(self.cli(lr, "statistik", "--reife-tage", "0")[1]["code"], "reife_ungueltig")

    def test_a_missing_reply_is_not_a_refusal_even_after_a_long_time(self):
        self.vorgang("alt", "Firma A", "versendet", versendet="2026-06-01")
        s = self.stat()
        self.assertEqual((s["zaehler"]["absage"], s["zaehler"]["offen_ohne_rueckmeldung"]), (0, 1))
        self.assertEqual(s["aktivitaet"]["absagen"]["n"], 0)

    def test_small_samples_are_marked_and_carry_an_interval(self):
        self.vorgang("a", "Firma A", "gespräch", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-10")])
        self.vorgang("b", "Firma B", "versendet")
        k = next(c for c in self.stat()["konversionen"] if c["name"] == "eingereicht_zu_einladung")
        self.assertEqual((k["zaehler"], k["nenner"], k["quote"]), (1, 2, 0.5))
        self.assertTrue(k["eingeschraenkt"])
        self.assertEqual(k["aussagekraft"], "gering")
        self.assertEqual(k["konfidenz95"], [0.095, 0.905])
        self.assertIn("Momentaufnahme", k["hinweis"])

    def test_with_enough_cases_the_interval_is_narrower_and_the_label_changes(self):
        for i in range(10):
            self.vorgang(f"v{i}", f"Firma {i}", "gespräch" if i < 5 else "versendet", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-10")] if i < 5 else ())
        k = next(c for c in self.stat()["konversionen"] if c["name"] == "eingereicht_zu_einladung")
        self.assertEqual((k["zaehler"], k["nenner"], k["aussagekraft"], k["eingeschraenkt"]), (5, 10, "beschreibend", False))
        self.assertEqual(k["konfidenz95"], [0.237, 0.763])

    def test_the_period_decides_which_applications_are_in_and_says_which_are_out(self):
        self.vorgang("a", "Firma A", "versendet", versendet="2026-08-01")
        self.vorgang("b", "Firma B", "versendet", versendet="2026-10-10")
        self.vorgang("c", "Firma C", "erfasst", versendet="", extra="erfasst: 2026-07-01\n")
        self.vorgang("d", "Firma D", "erfasst", versendet="")
        s = self.stat("--von", "2026-09-01")
        self.assertEqual(s["ausgewertet"], 1)
        self.assertEqual(s["population"]["ausgeschlossen_begonnen"], {"ausserhalb_zeitraum": 2, "datum_fehlt": 1})  # a Vorgang without a date is not given one
        self.assertEqual(s["datenqualitaet"]["ausgeschlossen"]["ausserhalb_zeitraum"], 1)


class Times(Base):
    def test_times_are_computed_from_stored_dates_only(self):
        self.vorgang("a", "Firma A", "angebot", versendet="2026-09-01", extra="erfasst: 2026-08-20\n", ereignisse=[
            ereignis("e-001", "vorbereitet", "2026-08-28"), ereignis("e-002", "gespraechseinladung", "2026-09-08"), ereignis("e-003", "gespraech", "2026-09-15"),
            ereignis("e-004", "angebot", "2026-09-22")])
        self.vorgang("b", "Firma B", "absage", versendet="2026-09-10", extra="erfasst: 2026-09-05\n", ereignisse=[ereignis("e-001", "absage", "2026-09-30")])
        m = self.stat()["zeiten"]["metriken"]
        self.assertEqual((m["beginn_bis_fertig"]["n"], m["beginn_bis_fertig"]["median_tage"]), (1, 8))
        self.assertEqual(m["fertig_bis_einreichung"]["median_tage"], 4)
        self.assertEqual(m["einreichung_bis_einladung"]["median_tage"], 7)
        self.assertEqual(m["einladung_bis_gespraech"]["median_tage"], 7)
        self.assertEqual(m["gespraech_bis_rueckmeldung"]["median_tage"], 7)
        self.assertEqual((m["einreichung_bis_erste_antwort"]["n"], m["einreichung_bis_erste_antwort"]["median_tage"]), (2, 13.5))
        self.assertEqual(m["einreichung_bis_ergebnis"]["median_tage"], 20.5)

    def test_a_missing_start_is_counted_and_never_replaced(self):
        self.vorgang("a", "Firma A", "gespräch", versendet="", extra="erfasst: 2026-09-01\n", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-09-10")])
        m = self.stat()["zeiten"]["metriken"]["einreichung_bis_einladung"]
        self.assertEqual((m["n"], m["ende_beobachtet"], m["ohne_startdatum"]), (0, 1, 1))
        self.assertNotIn("median_tage", m)

    def test_an_event_before_the_dispatch_is_a_contradiction_and_not_a_negative_time(self):
        self.vorgang("a", "Firma A", "gespräch", versendet="2026-10-10", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-01")])
        s = self.stat()
        self.assertEqual(s["zeiten"]["metriken"]["einreichung_bis_einladung"]["ende_vor_start"], 1)
        self.assertEqual(s["zeiten"]["metriken"]["einreichung_bis_einladung"]["n"], 0)

    def test_when_it_happened_and_when_it_was_recorded_are_two_dates(self):
        e = ereignis("e-001", "absage", "2026-10-01")
        e["erfasst"] = "2026-10-11T09:00:00Z"
        self.vorgang("a", "Firma A", "absage", versendet="2026-09-20", ereignisse=[e])
        m = self.stat()["zeiten"]
        self.assertEqual(m["metriken"]["erfassung_nach_ereignis"]["median_tage"], 10)
        self.assertEqual(m["metriken"]["einreichung_bis_ergebnis"]["median_tage"], 11)  # computed from the date it happened, not from the date it was recorded
        self.assertEqual(m["datenstand"]["neueste_erfassung"], "2026-10-11T09:00:00Z")

    def test_events_without_a_date_count_for_the_rates_but_not_for_the_times(self):
        e = ereignis("e-001", "gespraechseinladung", "")
        self.vorgang("a", "Firma A", "gespräch", ereignisse=[e])
        s = self.stat()
        self.assertEqual(s["zaehler"]["einladung"], 1)
        self.assertEqual(s["datenqualitaet"]["ereignisse_ohne_datum"], 1)
        self.assertEqual(s["zeiten"]["metriken"]["einreichung_bis_einladung"]["ende_beobachtet"], 0)


class Filters(Base):
    def setUp(self):
        super().setUp()
        self.vorgang("a", "Firma A", "versendet", extra="weg: portal\nstellenquelle: https://jobs.example/a\nausrichtung: ausschreibung\n", stelle="Backend-Entwickler")
        self.vorgang("b", "Firma B", "gespräch", extra="weg: email\nstellenquelle: Text\nausrichtung: initiativ\n", stelle="Systemadministrator",
                     ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-10")])
        self.vorgang("c", "Firma C", "absage", extra="weg: portal\nstellenquelle: https://jobs.example/c\n", stelle="Backend-Entwickler",
                     ereignisse=[ereignis("e-001", "absage", "2026-10-20")])

    def test_each_filter_selects_by_stored_data_and_names_what_it_left_out(self):
        for argumente, erwartet, grund_ in ((("--kanal", "portal"), 2, "anderer_kanal"), (("--quelle", "jobs.example"), 2, "andere_quelle"), (("--titel", "backend"), 2, "anderer_titel"),
                                            (("--ergebnis", "einladung"), 1, "anderes_ergebnis"), (("--ergebnis", "offen"), 2, "anderes_ergebnis"),
                                            (("--ausrichtung", "initiativ"), 1, "andere_ausrichtung"), (("--arbeitgeber", "Firma B"), 1, "anderer_arbeitgeber")):
            s = self.stat(*argumente)
            self.assertEqual(s["ausgewertet"], erwartet, argumente)
            self.assertIn(grund_, s["datenqualitaet"]["ausgeschlossen"], argumente)
            self.assertEqual(s["population"]["begonnen"], erwartet, argumente)

    def test_an_unknown_value_is_a_value_of_its_own_and_not_an_invented_one(self):
        s = self.stat("--ausrichtung", "unbekannt")
        self.assertEqual(s["ausgewertet"], 1)  # c has no `ausrichtung`
        gruppen = self.stat("--nach", "ausrichtung")["segmente"]["gruppen"]
        self.assertEqual(sorted(gruppen), ["ausschreibung", "initiativ", "unbekannt"])

    def test_features_that_are_not_stored_cannot_be_filtered_and_are_named_as_not_recorded(self):
        s = self.stat()
        self.assertEqual(s["nicht_erfasst"]["merkmale"], ["senioritaet", "branche", "standort", "arbeitsmodell"])
        with self.assertRaises(SystemExit):
            self.cli(lr, "statistik", "--senioritaet", "senior")

    def test_an_invalid_result_filter_is_refused(self):
        with self.assertRaises(SystemExit):
            self.cli(lr, "statistik", "--ergebnis", "erfolg")

    def test_the_filter_by_document_version_and_verdict_uses_what_the_check_stored(self):
        with open(os.path.join(self.w, "a", "passung.md"), "w", encoding="utf-8") as handle:
            handle.write("Ergebnis: Veto\n")
        self.assertEqual(self.stat("--bewertung", "Veto")["ausgewertet"], 1)
        self.assertEqual(self.stat("--dokumentversion", "nicht_eindeutig")["ausgewertet"], 3)  # no quality report: the version is not unambiguous, and it is said so

    def test_segments_of_document_versions_warn_about_unlike_groups(self):
        for i in range(6):
            self.vorgang(f"x{i}", f"Firma X{i}", "versendet", versendet="2026-06-01", extra="ausrichtung: ausschreibung\n")
        for i in range(6):
            self.vorgang(f"y{i}", f"Firma Y{i}", "versendet", versendet="2026-10-20", extra="ausrichtung: initiativ\n")
        gruppen = self.stat("--nach", "ausrichtung")["segmente"]
        self.assertTrue(any("Ausrichtung" in h for h in gruppen["vergleichbarkeit"]))
        self.assertTrue(any("unterschiedlich lange beobachtet" in h for h in gruppen["vergleichbarkeit"]))
        self.assertEqual(gruppen["gruppen"]["initiativ"]["zusammensetzung"]["mittleres_alter_tage"], 6)


class Traceability(Base):
    def test_a_figure_can_be_traced_to_the_applications_behind_it(self):
        self.vorgang("a", "Firma A", "gespräch", versendet="2026-08-20", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-10")])
        self.vorgang("b", "Firma B", "versendet", versendet="2026-10-24")
        self.vorgang("c", "Firma C", "versendet", versendet="2026-08-01")
        code, antwort = self.cli(lr, "erklaere", "eingereicht_zu_einladung")
        self.assertEqual(code, 0, antwort)
        belege = antwort["kennzahl"]["belege"]
        self.assertEqual((belege["zaehler"], belege["nenner"], belege["noch_jung"]), (["a"], ["a", "b", "c"], ["b"]))
        self.assertTrue(antwort["quellen_hash"])

    def test_belege_only_on_request_and_unknown_figures_are_refused(self):
        self.vorgang("a", "Firma A", "versendet")
        self.assertNotIn("belege", self.stat()["konversionen"][0])
        code, antwort = self.cli(lr, "erklaere", "gibt_es_nicht")
        self.assertEqual((code, antwort["code"]), (3, "kennzahl_unbekannt"))

    def test_the_figures_are_reproducible_from_the_stored_data(self):
        self.vorgang("a", "Firma A", "gespräch", ereignisse=[ereignis("e-001", "gespraechseinladung", "2026-10-10")])
        erste, zweite = self.stat(), self.stat()
        for s in (erste, zweite):
            del s["erstellt"]
        self.assertEqual(erste, zweite)


class DataQuality(Base):
    def test_contradictions_gaps_and_unreadable_files_stay_visible(self):
        self.vorgang("a", "Firma A", "versendet", versendet="2026-10-10", ereignisse=[ereignis("e-001", "absage", "2026-10-01")])
        self.vorgang("b", "Firma B", "versendet")
        with open(os.path.join(self.w, "b", "nachverfolgung.json"), "w", encoding="utf-8") as handle:
            handle.write("{kaputt")
        s = self.stat()
        q = s["datenqualitaet"]
        self.assertTrue(q["widersprueche"])
        self.assertEqual(q["ereignisdatei_defekt"], 1)
        self.assertEqual(s["zaehler"]["rueckmeldung"], 1)  # b's broken file did not invent a result for b

    def test_data_due_for_deletion_is_not_evaluated(self):
        self.vorgang("a", "Firma A", "absage", extra="loeschen_ab: 2026-10-01\n")
        s = self.stat()
        self.assertEqual((s["ausgewertet"], s["population"]["begonnen"]), (0, 0))
        self.assertEqual(s["population"]["ausgeschlossen_begonnen"], {"loeschfrist_erreicht": 1})

    def test_events_recorded_with_the_result_tool_of_r01_feed_the_figures_without_a_second_store(self):
        self.vorgang("a", "Firma A", "versendet", versendet="2026-10-01")
        out = self.cli(bw, "ereignis", "erfassen", "a", "--art", "gespraechseinladung", "--eingetreten-am", "2026-10-12", "--ja")
        self.assertEqual(out[0], 0, out)
        s = self.stat()
        self.assertEqual(s["zaehler"]["einladung"], 1)
        self.assertEqual(s["zeiten"]["metriken"]["einreichung_bis_einladung"]["median_tage"], 11)
        self.assertEqual(sorted(os.listdir(os.path.join(self.w, "a"))), ["nachverfolgung.json", "vorgang.md"])  # the evaluation added nothing next to the R-01 record


class RetrospectiveAndProposals(Base):
    def alt(self):
        """Two begun long ago and not finished, one finished and never dispatched, two vetoed, one refusal with a stated reason."""
        self.vorgang("alt1", "Firma 1", "erfasst", versendet="", extra="erfasst: 2026-08-01\n")
        self.vorgang("alt2", "Firma 2", "analysiert", versendet="", extra="erfasst: 2026-08-10\n")
        self.vorgang("fertig", "Firma 3", "erstellt", versendet="", extra="erfasst: 2026-08-15\n", ereignisse=[ereignis("e-001", "vorbereitet", "2026-09-01")])
        self.vorgang("neu", "Firma 4", "erfasst", versendet="", extra="erfasst: 2026-10-24\n")
        for slug in ("alt1", "alt2"):
            with open(os.path.join(self.w, slug, "passung.md"), "w", encoding="utf-8") as handle:
                handle.write("Ergebnis: Veto\n")

    def proposals(self):
        code, antwort = self.cli(lr, "vorschlaege", "erzeugen")
        self.assertEqual(code, 0, antwort)
        return {v["regel"]: v for v in self.cli(lr, "vorschlaege", "liste")[1]["vorschlaege"]}

    def test_proposals_rest_on_existing_data_and_name_who_is_affected(self):
        self.alt()
        v = self.proposals()
        self.assertEqual(sorted(q["vorgang"] for q in v["prozess:nicht_fertig"]["quellen"]), ["alt1", "alt2"])  # the one begun two days ago is not named
        self.assertEqual([q["vorgang"] for q in v["prozess:nicht_eingereicht"]["quellen"]], ["fertig"])
        self.assertEqual(len(v["passung:veto_begonnen"]["quellen"]), 2)
        for vorschlag in v.values():
            for feld in ("beobachtung", "quellen", "unsicherheit", "empfehlung", "erklaerung", "erwarteter_nutzen", "prioritaet"):
                self.assertTrue(vorschlag[feld], (vorschlag["regel"], feld))
            self.assertFalse(vorschlag["aendert_stammdaten"])
            self.assertEqual(vorschlag["status"], "erstellt")

    def test_nothing_is_proposed_without_data_and_a_young_application_is_not_a_finding(self):
        self.vorgang("neu", "Firma 4", "erfasst", versendet="", extra="erfasst: 2026-10-24\n")
        self.assertEqual(self.proposals(), {})
        code, antwort = self.cli(lr, "retrospektive")
        text = self.lies(antwort["datei"])
        self.assertIn("Keine offenen Vorschläge", text)
        self.assertIn("Fehlende Daten", text)
        self.assertIn("Nur 0 eingereichte Bewerbungen", text)

    def test_proposals_are_created_once_and_a_repeat_adds_nothing(self):
        self.alt()
        erste = self.cli(lr, "vorschlaege", "erzeugen")[1]["neu"]
        zweite = self.cli(lr, "vorschlaege", "erzeugen")[1]["neu"]
        self.assertTrue(erste)
        self.assertEqual(zweite, [])

    def test_each_proposal_has_a_check_of_effect_and_it_waits_for_enough_new_cases(self):
        self.alt()
        v = self.proposals()["prozess:nicht_fertig"]
        self.assertEqual(v["pruefung"]["kennzahl"], "begonnen_zu_fertig")
        self.assertEqual(self.cli(lr, "vorschlag", "pruefe", v["id"])[1]["code"], "nicht_angenommen")  # only after the user accepted it
        self.cli(lr, "vorschlag", "vorlegen", v["id"])
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", v["id"], "--entscheidung", "angenommen", "--grund", "ja, sinnvoll", "--ja")[0], 0)
        code, pruefung = self.cli(lr, "vorschlag", "pruefe", v["id"])
        self.assertEqual(code, 0, pruefung)
        self.assertTrue(pruefung["pruefbar"])
        self.assertEqual(pruefung["neue_faelle"], 0)
        self.assertIn("reichen noch nicht", pruefung["aussage"])
        for i in range(6):  # new data arrives: six more begun applications, all finished and old enough
            self.vorgang(f"z{i}", f"Firma Z{i}", "erstellt", versendet="", extra="erfasst: 2026-08-01\n")
        pruefung = self.cli(lr, "vorschlag", "pruefe", v["id"])[1]
        self.assertGreaterEqual(pruefung["neue_faelle"], 5)
        self.assertNotRegex(pruefung["aussage"], r"verursacht|führte zu|bewirkt, dass")

    def test_a_proposal_can_be_accepted_rejected_or_postponed_and_the_decision_is_kept(self):
        self.alt()
        v = self.proposals()
        for regel, entscheidung in (("prozess:nicht_fertig", "abgelehnt"), ("prozess:nicht_eingereicht", "zurueckgestellt"), ("passung:veto_begonnen", "angenommen")):
            vid = v[regel]["id"]
            self.cli(lr, "vorschlag", "vorlegen", vid)
            self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", entscheidung, "--grund", "weil", "--ja")[1]["status"], entscheidung)
        gespeichert = {x["regel"]: x for x in self.cli(lr, "vorschlaege", "liste")[1]["vorschlaege"]}
        self.assertEqual([gespeichert[r]["status"] for r in ("prozess:nicht_fertig", "prozess:nicht_eingereicht", "passung:veto_begonnen")], ["abgelehnt", "zurueckgestellt", "angenommen"])
        self.assertEqual(gespeichert["passung:veto_begonnen"]["entscheidungen"][-1]["von"], "nutzer")
        self.assertEqual(self.cli(lr, "vorschlag", "entscheiden", v["passung:veto_begonnen"]["id"], "--entscheidung", "angenommen", "--grund", "x")[1]["code"], "freigabe_fehlt")

    def test_the_decision_needs_the_user_and_is_refused_in_an_unattended_session(self):
        self.alt()
        vid = self.proposals()["prozess:nicht_fertig"]["id"]
        self.cli(lr, "vorschlag", "vorlegen", vid)
        code, antwort = self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "x", "--ja", umgebung={"WORKFLOW_UNBEAUFSICHTIGT": "1"})
        self.assertEqual((code, antwort["code"]), (3, "nur_interaktiv"))

    def test_the_retrospective_has_the_four_parts_and_every_proposal_the_asked_fields(self):
        self.alt()
        code, antwort = self.cli(lr, "retrospektive")
        self.assertEqual(code, 0, antwort)
        text = self.lies(antwort["datei"])
        for kopf in ("## A. Zusammenfassung", "## B. Prozessqualität", "## C. Reaktionen des Arbeitsmarkts", "## D. Verbesserungsmöglichkeiten", "## Einschränkungen"):
            self.assertIn(kopf, text)
        for feld in ("- Beobachtung:", "- Betroffen:", "- Mögliche Erklärung:", "- Unsicherheit:", "- Empfehlung:", "- Erwarteter Nutzen:", "- Wirksamkeit prüfen:"):
            self.assertIn(feld, text)
        self.assertIn("Prozess: nach mindestens 28 Tagen nicht fertig: 2 (alt1, alt2)", text)
        self.assertIn("**Prozess**", text)
        self.assertIn("**Datenlücke**", text)
        self.assertNotRegex(text, r"führte zu|verursacht|aufgrund Ihrer|liegt an|wegen der Unterlagen|garantiert")

    def test_the_retrospective_names_missing_data_instead_of_inventing_advice(self):
        self.vorgang("a", "Firma A", "versendet", versendet="2026-10-20")
        text = self.lies(self.cli(lr, "retrospektive")[1]["datei"])
        self.assertIn("Nur 1 eingereichte Bewerbungen", text)
        self.assertIn("Keine Warteschlange", text)
        self.assertIn("Kein Workflow-Speicher", text)
        self.assertIn("Eine fehlende Rückmeldung ist keine Absage", text)

    def test_the_source_of_a_stated_reason_is_kept_apart(self):
        wort = ereignis("e-001", "absage", "2026-10-01", original="Wir suchen mehr Erfahrung im Betrieb von Kubernetes.", interpretation=grund("beruf_erfahrung"))
        wort["quelle"] = {"typ": "nachricht", "nachricht_id": "m1"}
        eigene = ereignis("e-001", "absage", "2026-10-02", original="Telefonisch: Stelle intern besetzt.",
                          interpretation={**grund("organisatorisch"), "sicherheit": "mittel"})
        self.vorgang("a", "Firma A", "absage", ereignisse=[wort])
        self.vorgang("b", "Firma B", "absage", ereignisse=[eigene])
        self.vorgang("c", "Firma C", "absage", ereignisse=[ereignis("e-001", "absage", "2026-10-03", interpretation={"kategorie": "unbekannt", "bezeichnung": "unbekannter Grund",
                                                                                                                      "grund_genannt": False, "sicherheit": "niedrig"})])
        text = self.lies(self.cli(lr, "retrospektive")[1]["datei"])
        self.assertRegex(text, r"a \(2026-10-01\): vom Arbeitgeber genannt \(Wortlaut der Nachricht\); Kategorie „beruf_erfahrung“ ist eine Vermutung des Systems")
        self.assertRegex(text, r"b \(2026-10-02\): .*Kategorie „organisatorisch“ von der Nutzerin oder dem Nutzer erfasst")
        self.assertRegex(text, r"c \(2026-10-03\): kein Grund genannt: Grund unbekannt")

    def test_quality_findings_that_recur_become_an_observation_not_a_cause(self):
        for slug in ("a", "b"):
            self.vorgang(slug, f"Firma {slug}", "versendet")
            with open(os.path.join(self.w, slug, "qualitaet.json"), "w", encoding="utf-8") as handle:
                json.dump({"stand": "x", "checks": [{"id": "CV-07", "status": "FAIL"}, {"id": "CV-01", "status": "PASS"}]}, handle)
        v = self.proposals()
        self.assertIn("qualitaet:CV-07", v)
        self.assertEqual(v["qualitaet:CV-07"]["pruefung"]["kennzahl"], "qualitaet_fehler:CV-07")
        self.assertNotIn("qualitaet:CV-01", v)
        self.assertIn("Prüfung CV-07 schlug in 2 Vorgängen fehl", self.lies(self.cli(lr, "retrospektive")[1]["datei"]))

    def test_the_retrospective_is_the_same_when_run_again(self):
        self.alt()
        datei = self.cli(lr, "retrospektive")[1]["datei"]
        erste = inhalt(os.path.join(self.w, datei))
        self.assertEqual(self.cli(lr, "retrospektive")[1]["datei"], datei)
        self.assertEqual(inhalt(os.path.join(self.w, datei)), erste)
        self.assertEqual(self.cli(lr, "aktualitaet", datei)[1]["aktuell"], True)


class Safety(Base):
    def test_the_evaluation_changes_no_data_of_the_applicant_and_writes_only_below_lernen(self):
        self.vorgang("a", "Firma A", "versendet", ereignisse=[ereignis("e-001", "eingangsbestaetigung", "2026-10-03")])
        for name, text in (("profil.md", "Profil"), ("wunschprofil.md", "---\nbestaetigt: ja\n---\n")):
            with open(os.path.join(self.w, name), "w", encoding="utf-8") as handle:
                handle.write(text)
        vorher = {p: inhalt(os.path.join(self.w, p)) for p in ("a/vorgang.md", "a/nachverfolgung.json", "profil.md", "wunschprofil.md")}
        dateien_vorher = {os.path.relpath(os.path.join(d, f), self.w) for d, _, fs in os.walk(self.w) for f in fs}
        self.stat()
        self.cli(lr, "erklaere", "eingereicht_zu_rueckmeldung")
        self.cli(lr, "retrospektive")
        self.cli(lr, "vorschlaege", "erzeugen")
        self.assertEqual({p: inhalt(os.path.join(self.w, p)) for p in vorher}, vorher)
        neu = {os.path.relpath(os.path.join(d, f), self.w) for d, _, fs in os.walk(self.w) for f in fs} - dateien_vorher
        self.assertTrue(all(p.startswith("lernen" + os.sep) for p in neu), neu)

    def test_a_proposal_changes_nothing_when_accepted(self):
        self.vorgang("alt1", "Firma 1", "erfasst", versendet="", extra="erfasst: 2026-08-01\n")
        vid = self.cli(lr, "vorschlaege", "erzeugen") and self.cli(lr, "vorschlaege", "liste")[1]["vorschlaege"][0]["id"]
        vorher = inhalt(os.path.join(self.w, "alt1", "vorgang.md"))
        self.cli(lr, "vorschlag", "vorlegen", vid)
        self.cli(lr, "vorschlag", "entscheiden", vid, "--entscheidung", "angenommen", "--grund", "ok", "--ja")
        self.assertEqual(inhalt(os.path.join(self.w, "alt1", "vorgang.md")), vorher)
        self.assertTrue(self.cli(lr, "vorschlag", "zeige", vid)[1]["vorschlag"]["auswirkung"].startswith("Die Annahme ändert keine"))

    def test_nothing_is_sent_and_no_approval_is_made_by_the_evaluation(self):
        self.vorgang("a", "Firma A", "versendet", versendet="2026-06-01")
        self.assertEqual(wf.ADAPTER, {})
        self.cli(lr, "retrospektive")
        self.cli(lr, "vorschlaege", "erzeugen")
        self.assertFalse([p for d, _, fs in os.walk(self.w) for p in fs if p.startswith("antwort") or p.endswith(".eml")])
        self.assertFalse(os.path.exists(os.path.join(self.w, "workflow")))  # no task, no approval was created
        with open(os.path.join(ROOT, "scripts", "lernen.py"), encoding="utf-8") as handle:
            imports = set(re.findall(r"^(?:import|from) (\w+)", handle.read(), re.M))
        self.assertFalse(imports & {"socket", "smtplib", "urllib", "http", "requests", "ssl", "imaplib", "subprocess", "webbrowser", "antwort", "mail_import"}, imports)

    def test_an_older_approval_is_no_approval_for_anything_the_evaluation_suggests(self):
        self.vorgang("a", "Firma A", "versendet", versendet="2026-06-01")
        os.makedirs(os.path.join(self.w, "workflow"), exist_ok=True)
        with open(os.path.join(self.w, "workflow", "aufgaben.json"), "w", encoding="utf-8") as handle:
            json.dump({"version": 1, "aufgaben": {"versand_freigabe:a": {"id": "versand_freigabe:a", "typ": "versand_freigabe", "status": "erledigt",
                                                                          "entscheidung": {"art": "erteilt", "kontext_hash": "x"}}}}, handle)
        antwort = self.cli(lr, "vorschlaege", "erzeugen")[1]
        self.assertEqual(antwort["hinweis"], "Ein Vorschlag ändert nichts. Erst vorlegen, dann entscheiden.")
        with open(os.path.join(self.w, "workflow", "aufgaben.json"), encoding="utf-8") as handle:
            daten = json.load(handle)
        self.assertEqual(list(daten["aufgaben"]), ["versand_freigabe:a"])  # read, never written


if __name__ == "__main__":
    unittest.main()
