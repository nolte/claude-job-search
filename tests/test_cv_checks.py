"""Scenario tests for scripts/cv_checks.py (spec CG-13, CG-14).

All candidate data here is synthetic. No real application documents are used.
"""

import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cv_checks  # noqa: E402

GRUNDLAGE = """\
# Datengrundlage

### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin
- Betreuung der Event-Pipeline in Python und Kafka; Latenz von 800 ms auf 120 ms gesenkt.
- Einführung von Code-Reviews im Team mit fünf Entwicklern.

### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg
- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.
"""

STATION_NOTE = """\
---
typ: station
titel: Softwareentwickler
arbeitgeber: Beispiel AG
zeitraum_von: 2018
zeitraum_bis: 2021
fuehrung: nein
---

## Aufgaben
- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.

## Erfolge
- Schnittstelle für 3 Partnersysteme umgesetzt.

## Team
- Teil eines Teams von 7 Entwicklern, ohne Führungsverantwortung.
"""


class Grundlage:
    """Writes Grundlage notes to a temp directory and yields (source_text, records)."""

    def __init__(self, files):
        self.files = files
        self.dir = None

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        records, texts = [], []
        for name, content in self.files.items():
            path = os.path.join(self.dir, name)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
            records += cv_checks.grundlage_records(path)
            texts.append(content)
        self.text = "\n".join(texts)
        self.records = records
        return self

    def __exit__(self, *exc):
        shutil.rmtree(self.dir, ignore_errors=True)


def run(cv, grundlage=None, analyse=None, ats=False):
    """Findings for a Lebenslauf. `grundlage` is a dict of {file name: content}, or None."""
    if grundlage is None:
        findings = cv_checks.check_cv(cv, "lebenslauf.md", ats=ats)
    else:
        files = grundlage if isinstance(grundlage, dict) else {"grundlage.md": grundlage}
        with Grundlage(files) as g:
            findings = cv_checks.check_cv(cv, "lebenslauf.md", g.text, g.records, ats=ats)
    if analyse is not None:
        findings += cv_checks.check_analysis(analyse, "analyse.md")
    return findings


def rules(findings, severity=None):
    return [f["regel"] for f in findings if severity is None or f["schweregrad"] == severity]


CLEAN_CV = """\
# Lebenslauf

## Berufserfahrung

### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin
- Betreuung der Event-Pipeline in Python und Kafka; Latenz von 800 ms auf 120 ms gesenkt.
- Einführung von Code-Reviews im Team mit fünf Entwicklern.

### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg
- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.

## Sprachkenntnisse (GER-Niveau)
- Deutsch: Muttersprache
"""


class ScenarioTests(unittest.TestCase):
    def test_clean_cv_has_no_findings(self):
        self.assertEqual(run(CLEAN_CV, GRUNDLAGE), [])

    def test_placeholder_blocks_final_document(self):
        # Scenario K
        cv = CLEAN_CV.replace("Muttersprache", "[ERGÄNZEN: Niveau]")
        self.assertIn("CV-01", rules(run(cv, GRUNDLAGE), "Blocker"))

    def test_number_not_in_source_blocks(self):
        # Scenario F and B: invented metric or team size
        cv = CLEAN_CV.replace("fünf Entwicklern", "12 Entwicklern").replace("800 ms", "900 ms")
        blockers = [f for f in run(cv, GRUNDLAGE) if f["schweregrad"] == "Blocker" and f["regel"] == "CV-05"]
        self.assertEqual(sorted(f["befund"].split("„")[1].split("“")[0] for f in blockers), ["12", "900"])

    def test_bullet_without_numbers_is_kept(self):
        # Scenario F: a useful bullet without metric is not penalised
        self.assertNotIn("CV-05", rules(run(CLEAN_CV, GRUNDLAGE)))

    def test_conflicting_dates_block(self):
        # Scenario G
        cv = CLEAN_CV.replace("09/2018 – 03/2021", "09/2018 – 06/2021")
        self.assertIn("CV-06", rules(run(cv, GRUNDLAGE), "Blocker"))

    def test_same_title_and_employer_twice_is_matched_by_period(self):
        # two stations with the same title at the same employer (another team): matched by period, no CV-06
        grundlage = GRUNDLAGE + """
### 01/2014 – 12/2017 | Softwareentwickler | Hermes Europe GmbH, Hamburg
- Team Logistik: Schnittstellen für 4 Partnersysteme umgesetzt.

### 03/2010 – 12/2013 | Softwareentwickler | Hermes Europe GmbH, Hamburg
- Team Tracking: Sendungsverfolgung mit 2 Kollegen aufgebaut.
"""
        cv = CLEAN_CV.replace("## Sprachkenntnisse", """\
### 01/2014 – 12/2017 | Softwareentwickler | Hermes Europe GmbH, Hamburg
- Schnittstellen für 4 Partnersysteme umgesetzt

### 03/2010 – 12/2013 | Softwareentwickler | Hermes Europe GmbH, Hamburg
- Sendungsverfolgung mit 2 Kollegen aufgebaut

## Sprachkenntnisse""")
        findings = run(cv, grundlage)
        self.assertNotIn("CV-06", rules(findings))
        self.assertNotIn("CV-05", rules(findings))  # numbers checked against the matching station block
        # years only in the CV: matched by year, CV-02 only
        by_year = cv.replace("### 03/2010 – 12/2013", "### 2010 – 2013")
        self.assertNotIn("CV-06", rules(run(by_year, grundlage)))
        # a period that fits none of the candidates is still reported
        wrong = cv.replace("### 03/2010 – 12/2013", "### 03/2005 – 12/2008")
        self.assertIn("CV-06", rules(run(wrong, grundlage), "Blocker"))

    def test_station_not_in_grundlage_blocks(self):
        cv = CLEAN_CV.replace("Beispiel AG", "Erfundene GmbH")
        self.assertIn("CV-15", rules(run(cv, GRUNDLAGE), "Blocker"))

    def test_grundlage_without_stations_is_only_a_warning(self):
        findings = run(CLEAN_CV, "# Notiz ohne Stationen\n")
        self.assertIn("CV-15", rules(findings, "Warnung"))
        self.assertNotIn("CV-15", rules(findings, "Blocker"))

    def test_muss_without_evidence_cannot_be_fulfilled(self):
        # Scenario H
        analyse = """\
| Anforderung | Priorität | Kompetenz | Nachweis | Stärke | Status | Verwendung |
|---|---|---|---|---|---|---|
| Kubernetes-Betrieb | Muss | Kubernetes | — | — | erfüllt | Lebenslauf |
"""
        self.assertIn("CV-07", rules(run(CLEAN_CV, GRUNDLAGE, analyse=analyse), "Blocker"))

    def test_muss_gap_is_reported_as_warning_not_blocker(self):
        analyse = """\
| Anforderung | Priorität | Kompetenz | Nachweis | Stärke | Status | Verwendung |
|---|---|---|---|---|---|---|
| Kubernetes-Betrieb | Muss | Kubernetes | — | — | nicht belegt | Rückfrage |
"""
        findings = run(CLEAN_CV, GRUNDLAGE, analyse=analyse)
        self.assertIn("CV-07", rules(findings, "Warnung"))
        self.assertNotIn("CV-07", rules(findings, "Blocker"))

    def test_wunsch_without_evidence_is_not_blocked(self):
        analyse = """\
| Anforderung | Priorität | Kompetenz | Nachweis | Stärke | Status | Verwendung |
|---|---|---|---|---|---|---|
| Kubernetes | Wunsch | Kubernetes | — | — | nicht belegt | Rückfrage |
"""
        self.assertEqual(rules(run(CLEAN_CV, GRUNDLAGE, analyse=analyse), "Blocker"), [])

    def test_old_status_fehlt_is_flagged(self):
        analyse = """\
| Anforderung | Priorität | Kompetenz | Nachweis | Stärke | Status | Verwendung |
|---|---|---|---|---|---|---|
| Go | Wunsch | Go | — | — | fehlt | Rückfrage |
"""
        self.assertIn("CV-14", rules(run(CLEAN_CV, GRUNDLAGE, analyse=analyse), "Warnung"))

    def test_gap_over_two_months_needs_entry(self):
        # Scenario L: no invented reason, the gap is shown or marked
        cv = CLEAN_CV.replace("### 09/2018 – 03/2021", "### 01/2019 – 06/2019")
        self.assertIn("CV-13", rules(run(cv), "Blocker"))
        # a neutral line between the two stations closes the gap (CG-9)
        with_line = cv.replace("### 01/2019 – 06/2019", "Elternzeit 07/2019 – 03/2021\n\n### 01/2019 – 06/2019")
        self.assertNotIn("CV-13", rules(run(with_line), "Blocker"))
        # a gap entry in header form between the stations fills the chain and is not a station of the Grundlage
        with_header = cv.replace("### 01/2019 – 06/2019", "### 07/2019 – 03/2021 | Elternzeit | —\n\n### 01/2019 – 06/2019")
        findings = run(with_header, GRUNDLAGE.replace("### 09/2018 – 03/2021", "### 01/2019 – 06/2019"))
        self.assertNotIn("CV-13", rules(findings, "Blocker"))
        self.assertNotIn("CV-15", rules(findings, "Blocker"))
        self.assertNotIn("CV-03", rules(findings))

    def test_gap_entry_only_counts_between_the_two_stations(self):
        # a gap entry elsewhere in the document does not cover a different gap
        cv = CLEAN_CV.replace("### 09/2018 – 03/2021", "### 01/2019 – 06/2019")
        elsewhere = cv.replace("## Sprachkenntnisse", "### 06/2018 – 12/2018 | Auszeit | —\n\n## Sprachkenntnisse")
        self.assertIn("CV-13", rules(run(elsewhere), "Blocker"))

    def test_gap_wording_in_a_bullet_is_not_a_gap_entry(self):
        cv = CLEAN_CV.replace("### 09/2018 – 03/2021", "### 01/2019 – 06/2019").replace(
            "- Einführung von Code-Reviews im Team mit fünf Entwicklern.",
            "- Weiterbildung des Teams zu Kafka begleitet.",
        )
        self.assertIn("CV-13", rules(run(cv), "Blocker"))

    def test_end_before_start_blocks(self):
        cv = CLEAN_CV.replace("09/2018 – 03/2021", "09/2022 – 03/2021")
        self.assertIn("CV-04", rules(run(cv), "Blocker"))

    def test_reverse_chronology_warning(self):
        cv = CLEAN_CV.replace(
            "### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin",
            "### 04/2015 – 06/2016 | Praktikum | Musterfirma GmbH, Berlin",
        )
        self.assertIn("CV-04", rules(run(cv), "Warnung"))

    def test_tables_are_warning_and_blocker_for_ats(self):
        # Scenario I
        cv = CLEAN_CV + "\n| Jahr | Stelle |\n|---|---|\n"
        self.assertIn("CV-08", rules(run(cv), "Warnung"))
        self.assertIn("CV-08", rules(run(cv, ats=True), "Blocker"))

    def test_nonstandard_heading_is_warning(self):
        cv = CLEAN_CV.replace("## Sprachkenntnisse (GER-Niveau)", "## Meine Stärken")
        self.assertIn("CV-10", rules(run(cv), "Warnung"))

    def test_heading_with_suffix_is_not_a_standard_heading(self):
        # CG-11.2a: the exact heading, optionally with a qualifier in parentheses
        cv = CLEAN_CV.replace("## Berufserfahrung", "## Berufserfahrung bei Musterfirma")
        self.assertIn("CV-10", rules(run(cv), "Warnung"))
        short = CLEAN_CV.replace("## Sprachkenntnisse (GER-Niveau)", "## Kenntnisse").replace("## Berufserfahrung", "## Ausbildung")
        self.assertNotIn("CV-10", rules(run(short)))

    def test_sub_bullets_are_a_note(self):
        cv = CLEAN_CV.replace(
            "- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.",
            "- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.\n  - REST-Schnittstellen\n  - Datenbank",
        )
        self.assertEqual(rules(run(cv), "Hinweis").count("CV-17"), 2)

    def test_bullet_limits(self):
        many = "\n".join(f"- Aufgabe {i} ohne Zahl" for i in range(6))
        cv = CLEAN_CV.replace("- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.", many)
        self.assertIn("CV-03", rules(run(cv), "Warnung"))
        empty = CLEAN_CV.replace("- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.\n", "")
        self.assertIn("CV-03", rules(run(empty), "Hinweis"))

    def test_year_only_header_is_warning(self):
        cv = CLEAN_CV.replace("### 09/2018 – 03/2021", "### 2018 – 2021")
        findings = run(cv)
        self.assertIn("CV-02", rules(findings, "Warnung"))
        self.assertEqual(rules(findings, "Blocker"), [])
        self.assertIn("MM/JJJJ – MM/JJJJ | Position | Arbeitgeber, Ort", next(f["befund"] for f in findings if f["regel"] == "CV-02"))

    def test_year_only_header_still_checks_its_bullets(self):
        # a non-conforming header must not switch off CV-05, CV-15 or CV-13 for that station
        cv = CLEAN_CV.replace("### 09/2018 – 03/2021", "### 2018 – 2021").replace(
            "- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.",
            "- Schnittstellen für 42 Partnersysteme umgesetzt",
        )
        findings = run(cv, GRUNDLAGE)
        self.assertIn("CV-02", rules(findings, "Warnung"))
        self.assertIn("CV-05", rules(findings, "Blocker"))
        self.assertNotIn("CV-15", rules(findings, "Blocker"))
        unknown = cv.replace("Beispiel AG", "Erfundene GmbH")
        self.assertIn("CV-15", rules(run(unknown, GRUNDLAGE), "Blocker"))

    def test_number_from_another_station_is_a_note_not_a_blocker(self):
        # CV-05 checks the station record first; a number found elsewhere in the Grundlage is a Hinweis
        cv = CLEAN_CV.replace(
            "- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.",
            "- Integrationsplattform mit 800 ms Antwortzeit betreut",
        )
        findings = [f for f in run(cv, GRUNDLAGE) if f["regel"] == "CV-05"]
        self.assertEqual([f["schweregrad"] for f in findings], ["Hinweis"])

    def test_generic_and_duplicate_bullets_are_notes(self):
        cv = CLEAN_CV.replace(
            "- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.",
            "- Verantwortlich für die Plattform.\n- Verantwortlich für die Plattform.",
        )
        findings = run(cv)
        self.assertIn("CV-11", rules(findings, "Warnung"))
        self.assertIn("CV-09", rules(findings, "Hinweis"))

    def test_output_is_reproducible(self):
        # CG-13.3
        self.assertEqual(run(CLEAN_CV, GRUNDLAGE), run(CLEAN_CV, GRUNDLAGE))

    def test_new_forbidden_phrases_are_warnings(self):
        # CG-8.2.3, CG-7.3: unsourced evaluative wording is a Warnung
        cv = CLEAN_CV.replace(
            "- Mitarbeit an einer Integrationsplattform mit REST-Schnittstellen.",
            "- Erfolgreich fünf Teams unterstützt.",
        )
        self.assertIn("CV-11", rules(run(cv), "Warnung"))


class StationNoteTests(unittest.TestCase):
    """Vault-style station notes: frontmatter periods, years only, Erfolge and Team sections."""

    def test_station_note_matches_by_year(self):
        cv = CLEAN_CV.replace("09/2018 – 03/2021", "09/2018 – 03/2021")
        # the note has years only: the CV is accepted if the years agree, with a Warnung for the missing month
        findings = run(cv, {"ausbildung.md": STATION_NOTE})
        self.assertNotIn("CV-06", rules(findings, "Blocker"))
        self.assertIn("CV-15", rules(findings, "Blocker"))  # the other CV station is not in this note

    def test_year_mismatch_blocks(self):
        cv = CLEAN_CV.replace("09/2018 – 03/2021", "09/2017 – 03/2021").replace(
            "### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin\n", ""
        )
        findings = run(cv, {"station.md": STATION_NOTE})
        self.assertIn("CV-06", rules(findings, "Blocker"))

    def test_year_only_note_is_warning_not_blocker(self):
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Mitarbeit an einer Plattform.\n"
        findings = run(cv, {"station.md": STATION_NOTE})
        self.assertIn("CV-02", rules(findings, "Warnung"))
        self.assertNotIn("CV-06", rules(findings, "Blocker"))

    def test_leadership_wording_blocks_without_leadership_evidence(self):
        # Scenario B: the note says fuehrung: nein, the CV claims leadership
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Teamleitung für sieben Entwickler übernommen.\n"
        findings = run(cv, {"station.md": STATION_NOTE})
        self.assertIn("CV-16", rules(findings, "Blocker"))

    def test_leadership_wording_is_a_warning_when_not_recorded(self):
        # fuehrung missing or ungeklärt: the claim is open, not refuted
        note = STATION_NOTE.replace("fuehrung: nein\n", "")
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Teamleitung übernommen.\n"
        findings = run(cv, {"station.md": note})
        self.assertIn("CV-16", rules(findings, "Warnung"))
        self.assertNotIn("CV-16", rules(findings, "Blocker"))
        unresolved = STATION_NOTE.replace("fuehrung: nein", "fuehrung: ungeklärt")
        self.assertIn("CV-16", rules(run(cv, {"station.md": unresolved}), "Warnung"))

    def test_leadership_wording_allowed_with_recorded_leadership(self):
        note = STATION_NOTE.replace("fuehrung: nein", "fuehrung: ja")
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Teamleitung für sieben Entwickler.\n"
        self.assertNotIn("CV-16", rules(run(cv, {"station.md": note})))

    def test_leadership_regex_targets_personnel_leadership_only(self):
        head = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n"
        for bullet in (
            "- Technische Führung des Themas Observability übernommen",
            "- Gespräche mit Vorgesetzten zur Priorisierung geführt",
            "- Migration des Clusters geleitet",
            "- Workshops zu Kafka durchgeführt",
        ):
            self.assertNotIn("CV-16", rules(run(head + bullet + "\n", {"station.md": STATION_NOTE})), bullet)
        for bullet in (
            "- Team von 7 Entwicklern fachlich geleitet",
            "- Disziplinarische Verantwortung für 3 Mitarbeiter",
            "- Führungsverantwortung für die Abteilung übernommen",
        ):
            self.assertIn("CV-16", rules(run(head + bullet + "\n", {"station.md": STATION_NOTE}), "Blocker"), bullet)

    def test_erfolge_numbers_are_traceable_from_note(self):
        # Erfolge and Team sections of the note are part of the source text (CV-05)
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Schnittstelle für 3 Partnersysteme umgesetzt.\n- Teil eines Teams von 7 Entwicklern.\n"
        self.assertNotIn("CV-05", rules(run(cv, {"station.md": STATION_NOTE})))

    def test_non_station_note_is_not_a_station(self):
        records = []
        with Grundlage({"index.md": "---\ntyp: index\n---\n# Index\n"}) as g:
            records = g.records
        self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
