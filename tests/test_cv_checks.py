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

## Sprachkenntnisse
- Deutsch (Muttersprache)

## IT- und Fachkenntnisse
- Programmiersprachen: Python, Go, C++
- Zertifikate: 2022: Zertifikat Beispiel, Beispiel-Akademie, Berlin
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
### 01/2014 – 12/2017 | Softwareentwickler | Beispiel AG, Hamburg
- Team Logistik: Schnittstellen für 4 Partnersysteme umgesetzt.

### 03/2010 – 12/2013 | Softwareentwickler | Beispiel AG, Hamburg
- Team Tracking: Sendungsverfolgung mit 2 Kollegen aufgebaut.
"""
        cv = CLEAN_CV.replace("## Sprachkenntnisse", """\
### 01/2014 – 12/2017 | Softwareentwickler | Beispiel AG, Hamburg
- Schnittstellen für 4 Partnersysteme umgesetzt

### 03/2010 – 12/2013 | Softwareentwickler | Beispiel AG, Hamburg
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

    def test_gap_wording_inside_a_job_title_is_a_station(self):
        # `Weiterbildung` or `Elternzeit` inside a title must not turn the station into a gap entry
        # and switch off CV-15 for it
        cv = CLEAN_CV.replace("## Sprachkenntnisse", """\
### 01/2016 – 12/2017 | Referent Weiterbildung | Erfundene GmbH, Köln
- Schulungen für 40 Teilnehmende organisiert

## Sprachkenntnisse""")
        self.assertIn("CV-15", rules(run(cv, GRUNDLAGE), "Blocker"))
        self.assertFalse(cv_checks.is_gap_entry("Referent Weiterbildung"))
        self.assertFalse(cv_checks.is_gap_entry("Beraterin Elternzeit & Familie"))
        self.assertTrue(cv_checks.is_gap_entry("Weiterbildung"))
        self.assertTrue(cv_checks.is_gap_entry("Elternzeit (04/2019 – 08/2019)"))
        self.assertTrue(cv_checks.is_gap_entry("[ERGÄNZEN: Grund der Lücke]"))

    def test_gap_header_without_period_has_no_bullet_finding(self):
        # a gap entry written as `### Elternzeit (…)` is neither a CV-02 header nor a station without bullets
        cv = CLEAN_CV.replace("### 09/2018 – 03/2021", "### Elternzeit (04/2021 – 04/2021)\n\n### 09/2018 – 03/2021")
        findings = run(cv)
        self.assertNotIn("CV-03", rules(findings))
        self.assertNotIn("CV-02", rules(findings))

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


class GroundingTests(unittest.TestCase):
    """CV-19 (list entries), CV-20 (unconfirmed station), CV-05 (unit)."""

    def cv_with(self, section):
        return CLEAN_CV.replace("## Sprachkenntnisse (GER-Niveau)\n- Deutsch: Muttersprache\n", section)

    def test_ungrounded_skills_and_certificates_block(self):
        cv = self.cv_with("## IT- und Fachkenntnisse\n- Programmiersprachen: Python, Rust, Terraform\n\n"
                          "## Weiterbildung und Zertifikate\n- 2023: CKA, CNCF\n")
        blocked = [f["befund"] for f in run(cv, GRUNDLAGE) if f["regel"] == "CV-19" and f["schweregrad"] == "Blocker"]
        for term in ("Rust", "Terraform", "CKA", "CNCF"):
            self.assertTrue(any(f"„{term}“" in text for text in blocked), term)
        self.assertFalse(any("„Python“" in text for text in blocked))

    def test_grounded_entries_pass_with_other_spelling_and_punctuation(self):
        cv = self.cv_with("## Sprachkenntnisse (GER-Niveau)\n- Deutsch: Muttersprache\n\n"
                          "## IT- und Fachkenntnisse\n- Programmiersprachen: python, Go, C++\n\n"
                          "## Weiterbildung und Zertifikate\n- 2022: Zertifikat Beispiel, Beispiel-Akademie, Berlin\n")
        self.assertNotIn("CV-19", rules(run(cv, GRUNDLAGE)))

    def test_language_not_in_the_grundlage_blocks(self):
        cv = self.cv_with("## Sprachkenntnisse (GER-Niveau)\n- Deutsch: Muttersprache\n- Französisch: C1\n")
        blocked = [f["befund"] for f in run(cv, GRUNDLAGE) if f["regel"] == "CV-19"]
        self.assertTrue(any("Französisch" in text for text in blocked))
        self.assertTrue(any("C1" in text for text in blocked))

    def test_number_in_a_qualifier_must_be_in_the_grundlage(self):
        cv = self.cv_with("## IT- und Fachkenntnisse\n- Programmiersprachen: Python (9 Jahre)\n")
        self.assertIn("CV-19", rules(run(cv, GRUNDLAGE), "Blocker"))

    def test_list_sections_are_not_checked_without_a_grundlage(self):
        cv = self.cv_with("## IT- und Fachkenntnisse\n- Programmiersprachen: Rust\n")
        self.assertNotIn("CV-19", rules(run(cv)))

    def test_placeholder_entries_are_left_to_cv_01(self):
        cv = self.cv_with("## IT- und Fachkenntnisse\n- Programmiersprachen: [ERGÄNZEN: Sprachen]\n")
        found = rules(run(cv, GRUNDLAGE))
        self.assertIn("CV-01", found)
        self.assertNotIn("CV-19", found)

    def test_number_with_another_unit_is_a_warning(self):
        # `5` stands in the station, but as `fünf`/Entwickler, not as Mio. EUR
        cv = CLEAN_CV.replace("Einführung von Code-Reviews im Team mit fünf Entwicklern.", "Budget von 120 Mio. EUR verantwortet.")
        self.assertIn("CV-05", rules(run(cv, GRUNDLAGE), "Warnung"))
        same = CLEAN_CV.replace("fünf Entwicklern", "5 Entwicklern")
        grundlage = GRUNDLAGE.replace("fünf Entwicklern", "5 Entwickler")
        self.assertNotIn("CV-05", rules(run(same, grundlage)))

    def test_unit_check_ignores_years_and_numbers_without_a_following_word(self):
        cv = CLEAN_CV.replace("Latenz von 800 ms auf 120 ms gesenkt.", "Latenz seit 2021 gesenkt; Ziel 120.")
        self.assertNotIn("CV-05", rules(run(cv, GRUNDLAGE), "Warnung"))

    def test_unconfirmed_station_blocks(self):
        grundlage = GRUNDLAGE.replace(
            "### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg",
            "### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Bestätigt: nein")
        self.assertIn("CV-20", rules(run(CLEAN_CV, grundlage), "Blocker"))
        for answer in ("ja", "ja | nein"):
            confirmed = GRUNDLAGE.replace(
                "### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg",
                f"### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Bestätigt: {answer}")
            self.assertNotIn("CV-20", rules(run(CLEAN_CV, confirmed)), answer)
        self.assertNotIn("CV-20", rules(run(CLEAN_CV, GRUNDLAGE)))

    def test_unconfirmed_station_note_blocks(self):
        note = STATION_NOTE.replace("fuehrung: nein\n", "fuehrung: nein\nbestaetigt: nein\n")
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Mitarbeit an einer Plattform.\n"
        self.assertIn("CV-20", rules(run(cv, {"station.md": note}), "Blocker"))

    def test_language_level_must_stand_with_its_language(self):
        # review of PR 38: `Englisch (C2)` passed because a `2` stood somewhere, `B2` belonged to French
        grundlage = GRUNDLAGE + "\n- Englisch B2, Team 2 Personen\n- Französisch C1\n"
        for entry in ("Englisch (C2)", "Englisch: C1", "Französisch: B2"):
            cv = self.cv_with(f"## Sprachkenntnisse (GER-Niveau)\n- {entry}\n")
            self.assertIn("CV-19", rules(run(cv, grundlage), "Blocker"), entry)
        for entry in ("Englisch: B2", "Englisch (B2)", "Französisch: C1", "Deutsch: Muttersprache"):
            cv = self.cv_with(f"## Sprachkenntnisse (GER-Niveau)\n- {entry}\n")
            self.assertNotIn("CV-19", rules(run(cv, grundlage)), entry)

    def test_number_in_a_qualifier_is_not_part_of_a_word(self):
        grundlage = GRUNDLAGE + "\n- Kenntnisse B2\n"
        cv = self.cv_with("## IT- und Fachkenntnisse\n- Programmiersprachen: Python (2 Jahre)\n")
        self.assertIn("CV-19", rules(run(cv, grundlage), "Blocker"))

    def test_list_entries_in_other_forms_are_not_blocked(self):
        grundlage = GRUNDLAGE + """
## Ausbildung und Studium
- 09/2010 – 06/2014 | B.Sc. Informatik | Uni Beispiel, Hamburg
- Bachelor Informatik 2014
- Java und Python
- Büroorganisation
"""
        for entry in ("09/2010 – 06/2014 | B.Sc. Informatik | Uni Beispiel", "2014 Bachelor Informatik", "Python und Java",
                      "_Java_", "Bueroorganisation", "**Python**", "2010 – 2014: Bachelor Informatik, Uni Beispiel"):
            cv = self.cv_with(f"## Ausbildung und Studium\n- {entry}\n")
            self.assertNotIn("CV-19", rules(run(cv, grundlage)), entry)
        cv = self.cv_with("## Ausbildung und Studium\n- 09/2010 – 06/2014 | B.Sc. Physik | Uni Beispiel\n")
        self.assertIn("CV-19", rules(run(cv, grundlage), "Blocker"))

    def test_colon_inside_a_time_does_not_split_an_entry(self):
        grundlage = GRUNDLAGE + "\n## Weiterbildung und Zertifikate\n- PMP\n"
        cv = self.cv_with("## Weiterbildung und Zertifikate\n- 12:30 PMP\n")
        found = [f["befund"] for f in run(cv, grundlage) if f["regel"] == "CV-19"]
        self.assertTrue(found and found[0].startswith("Eintrag „12:30 PMP“"), found)

    def test_unit_check_is_lenient_where_the_record_gives_no_unit(self):
        grundlage = GRUNDLAGE.replace("Latenz von 800 ms auf 120 ms gesenkt.", "Latenz von 800 ms auf 120 ms gesenkt. ISO 27001. Team: 5, remote. Kosten 30 Prozent.")
        for bullet in ("ISO 27001 eingeführt", "Team mit 5 Entwicklern betreut", "Kosten um 30 % gesenkt"):
            cv = CLEAN_CV.replace("Einführung von Code-Reviews im Team mit fünf Entwicklern.", bullet + ".")
            self.assertNotIn("CV-05", rules(run(cv, grundlage), "Warnung"), bullet)

    def test_confirmation_flag_accepts_false_and_no(self):
        for value in ("nein", "false", "no", "Nein"):
            note = STATION_NOTE.replace("fuehrung: nein\n", f"fuehrung: nein\nbestaetigt: {value}\n")
            cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Mitarbeit an einer Plattform.\n"
            self.assertIn("CV-20", rules(run(cv, {"station.md": note}), "Blocker"), value)

    def test_probe_cv_of_the_audit_is_blocked(self):
        # AUDIT-FF-001: an invented technology, certificate and budget used to pass with no finding
        cv = ("## Berufserfahrung\n\n### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin\n"
              "- Plattform-Strategie verantwortet; Budget von 40 Mio. EUR genutzt\n\n"
              "## IT- und Fachkenntnisse\n- Programmiersprachen: Rust, Go, Terraform\n\n"
              "## Weiterbildung und Zertifikate\n- 2023: CKA, CNCF\n")
        found = run(cv, GRUNDLAGE)
        self.assertGreaterEqual(rules(found, "Blocker").count("CV-19"), 3)
        self.assertIn("CV-05", rules(found, "Blocker"))


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

    def test_leadership_wording_blocks_when_not_recorded(self):
        # fuehrung missing or ungeklärt: leadership is not evidenced, so the claim blocks (CG-13.4.3)
        note = STATION_NOTE.replace("fuehrung: nein\n", "")
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Teamleitung übernommen.\n"
        self.assertIn("CV-16", rules(run(cv, {"station.md": note}), "Blocker"))
        unresolved = STATION_NOTE.replace("fuehrung: nein", "fuehrung: ungeklärt")
        self.assertIn("CV-16", rules(run(cv, {"station.md": unresolved}), "Blocker"))

    def test_leadership_in_a_header_form_grundlage_follows_its_fuehrung_line(self):
        head = "## Berufserfahrung\n\n### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin\n"
        cv = head + "- Teamleitung für fünf Entwickler übernommen.\n"
        # the default Grundlage form records no leadership: blocks
        self.assertIn("CV-16", rules(run(cv, GRUNDLAGE), "Blocker"))
        for answer, blocks in (("ja", False), ("nein", True), ("ungeklärt", True)):
            grundlage = GRUNDLAGE.replace(
                "- Einführung von Code-Reviews im Team mit fünf Entwicklern.",
                f"- Einführung von Code-Reviews im Team mit fünf Entwicklern.\n- Team: 5 Entwickler; Führung: {answer}")
            self.assertEqual("CV-16" in rules(run(cv, grundlage), "Blocker"), blocks, answer)
        # the unfilled template line is no answer and does not unlock the claim
        template = GRUNDLAGE.replace(
            "- Einführung von Code-Reviews im Team mit fünf Entwicklern.",
            "- Team: Größe, Rollen; Führung: ja | nein | ungeklärt")
        self.assertIn("CV-16", rules(run(cv, template), "Blocker"))

    def test_fuehrung_key_is_case_insensitive_and_anchored(self):
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Teamleitung für sieben Entwickler.\n"
        self.assertNotIn("CV-16", rules(run(cv, {"station.md": STATION_NOTE.replace("fuehrung: nein", "fuehrung: Ja")})))
        head = "## Berufserfahrung\n\n### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin\n- Teamleitung für fünf Entwickler.\n"
        anchor = "- Einführung von Code-Reviews im Team mit fünf Entwicklern."
        for line, blocks in (("- Team: 5 Entwickler; Fachliche Führung: ja", True),
                             ("- Team: 5 Entwickler; Disziplinarische Führung: nein; Führung: ja", False),
                             ("- Führung: ja", False)):
            self.assertEqual("CV-16" in rules(run(head, GRUNDLAGE.replace(anchor, anchor + "\n" + line)), "Blocker"), blocks, line)

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
            # CG-7.3 names `führte` and the Führung family; with a people object they are personnel leadership
            "- Team von 8 Mitarbeitern fachlich und personell geführt",
            "- Führung eines Teams von 5 Entwicklern",
            "- Führte die Abteilung Integration mit 3 Mitarbeitern",
        ):
            self.assertIn("CV-16", rules(run(head + bullet + "\n", {"station.md": STATION_NOTE}), "Blocker"), bullet)

    def test_year_only_header_reports_cv02_once(self):
        # the header-form warning of check_cv covers the missing month; check_period must not add a second CV-02
        cv = "## Berufserfahrung\n\n### 2018 – 2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Mitarbeit an einer Plattform.\n"
        findings = run(cv, {"station.md": STATION_NOTE})
        self.assertEqual(rules(findings).count("CV-02"), 1)

    def test_erfolge_numbers_are_traceable_from_note(self):
        # Erfolge and Team sections of the note are part of the source text (CV-05)
        cv = "## Berufserfahrung\n\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Schnittstelle für 3 Partnersysteme umgesetzt.\n- Teil eines Teams von 7 Entwicklern.\n"
        self.assertNotIn("CV-05", rules(run(cv, {"station.md": STATION_NOTE})))

    def test_non_station_note_is_not_a_station(self):
        records = []
        with Grundlage({"index.md": "---\ntyp: index\n---\n# Index\n"}) as g:
            records = g.records
        self.assertEqual(records, [])


class BirthdateTests(unittest.TestCase):
    """CV-18 (RC-11 rule 4): a birthdate of a person in analyse.md or a firm file is a Warnung."""

    POSITIVE = (
        "Geschäftsführerin Erika Mustermann, Geburtsdatum: 03.05.1971",
        "Erika Mustermann, geb. 3.5.71",
        "Erika Mustermann, Geb. 1971-05-03",
        "Erika Mustermann, geboren am 03.05.1971",
        "Erika Mustermann (* 03.05.1971)",
        "Erika Mustermann *03.05.1971",
        "Erika Mustermann (* 1971-05-03), Geschäftsführerin",
        "Erika Mustermann, geborene Beispiel, 03.05.1971",
        "Erika Mustermann, Geburtsdatum: 03. Mai 1971",
        "Erika Mustermann, geboren am 3. Mai 1971",
        "Erika Mustermann, geb. 03/05/1971",
        "Erika Mustermann, 03.05.1971 geboren",
        "Erika Mustermann (03.05.1971 geb.)",
        "Erika Mustermann, Geburtsdatum: 1971",
        "Erika Mustermann, geb. 1971",
        "Musterfirma GmbH: Erika Mustermann *03. Mai 1971",
    )
    NEGATIVE = (
        "Stand: 2026-10-23",
        "Bewerbungsfrist: 15.11.2026",
        "Gegründet 03.05.1971 als Musterfirma GmbH",
        "Geburtsdatum nicht erfasst (RC-5.3 Regel 5)",
        "Erika Mustermann, Geschäftsführerin seit 2019",
        "*2026-10-23*",
        "* 2026-10-23 Frist des Postings",
        "*Stand: 2026-10-23*",
        "Zeitraum 03.2019 – 05.2021 bei der Beispiel AG",
        "Frist *31.12.2026 bis*",
        "Stand *2026-10-23 (Impressum)*",
        "**Stand:** *2026-10-23",
        "Beispiel AG, geb. Zeitarbeit 01.01.2020",
        "Gegründet 1971 als Musterfirma GmbH",
        "Musterfirma GmbH, gegründet am 3. Mai 1971",
        "Geburtsdatum nicht erfasst, Gründung 1971",
        "Frist 15/11/2026",
    )

    def test_birthdate_forms_are_warnings(self):
        for line in self.POSITIVE:
            findings = cv_checks.check_analysis("## Unternehmen\n" + line + "\n", "analyse.md")
            self.assertEqual(rules(findings), ["CV-18"], line)
            self.assertEqual(findings[0]["schweregrad"], "Warnung", line)
            self.assertEqual(findings[0]["zeile"], 2, line)

    def test_plain_dates_and_notes_are_not_findings(self):
        for line in self.NEGATIVE:
            self.assertEqual(cv_checks.check_analysis(line + "\n", "analyse.md"), [], line)

    def test_firm_file_option_runs_the_check(self):
        base = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, base, True)
        paths = {}
        for name, content in (("lebenslauf.md", CLEAN_CV), ("musterfirma.md", "# Musterfirma GmbH\nErika Mustermann, geb. 03.05.1971\n"),
                              ("sauber.md", "# Beispiel AG\nStand: 2026-10-23\n")):
            paths[name] = os.path.join(base, name)
            with open(paths[name], "w", encoding="utf-8") as handle:
                handle.write(content)
        import contextlib
        import io
        import json
        for firm, expected in (("musterfirma.md", ["CV-18"]), ("sauber.md", [])):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                cv_checks.main([paths["lebenslauf.md"], "--firma", paths[firm]])
            self.assertEqual(rules(json.loads(out.getvalue())["befunde"]), expected, firm)

    def test_missing_optional_paths_are_findings_not_crashes(self):
        import contextlib
        import io
        import json
        base = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, base, True)
        cv = os.path.join(base, "lebenslauf.md")
        with open(cv, "w", encoding="utf-8") as handle:
            handle.write(CLEAN_CV)
        firm = os.path.join(base, "musterfirma.md")
        with open(firm, "w", encoding="utf-8") as handle:
            handle.write("# Musterfirma GmbH\nErika Mustermann, geb. 03.05.1971\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cv_checks.main([cv, "--firma", os.path.join(base, "fehlt.md"), "--firma", firm, "--analyse", os.path.join(base, "fehlt-analyse.md")])
        report = json.loads(out.getvalue())
        missing = [f for f in report["befunde"] if "nicht lesbar" in f["befund"]]
        self.assertEqual(sorted(f["regel"] for f in missing), ["CV-14", "CV-18"])
        self.assertTrue(all(f["schweregrad"] == "Warnung" for f in missing))
        # the other firm file is still checked
        self.assertEqual(sum(1 for f in report["befunde"] if f["regel"] == "CV-18" and "Geburtsdatum einer Person" in f["befund"]), 1)


if __name__ == "__main__":
    unittest.main()
