"""Edge cases of the CV checks (audit finding F-05). Synthetic data only.

Each group holds cases that must stay accepted (a false positive would block a valid CV) next to cases that must still be found (a false
negative would let a fact error through). The matrix of the groups:

| Group | Subject | Rule |
|---|---|---|
| A | figures: notation, units, number words | CV-05 |
| B | stations at one employer, spelling variants, overlap | CV-15, CV-04 |
| C | leadership and responsibility wording | CV-16, CV-22 |
| D | skills, certificates: spelling, year, status | CV-19 |
| E | gaps, neutral entries, incomplete periods | CV-13, CV-02, CV-01 |
| F | severities of the above | Blocker, Warnung, Hinweis |
| G | existing valid CVs and facts stay as they were | the fixtures of test_scenarios.py |

`cv_checks.py` equates notation (`1,5` and `1.5`), not values (`500 GB` is not `0,5 TB`) and not similar names (`CKA` is not `CKAD`).
"""

import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import cv_checks  # noqa: E402
from test_cv_checks import rules, run  # noqa: E402

STATION = "### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin"


def station_grundlage(*lines, header=STATION, extra=""):
    return "## Berufserfahrung\n\n" + header + "\n" + "".join(f"- {line}\n" for line in lines) + "- Führung: nein\n" + extra


def station_cv(*bullets, header=STATION, extra=""):
    return "## Berufserfahrung\n\n" + header + "\n" + "".join(f"- {b}\n" for b in bullets) + extra


def check_bullet(bullet, record, **kw):
    return run(station_cv(bullet), station_grundlage(record))


def found(findings, rule, severity=None):
    return [f for f in findings if f["regel"] == rule and (severity is None or f["schweregrad"] == severity)]


class FigureTests(unittest.TestCase):
    """Group A. A figure is a fact; its notation is not."""

    ACCEPTED = (
        ("Kosten um 10% gesenkt", "Kosten um 10 % gesenkt"),
        ("Kosten um 10 % gesenkt", "Kosten um 10% gesenkt"),
        ("Kosten um 10 % gesenkt", "Kosten um 10 Prozent gesenkt"),
        ("Latenz um 1,5 Sekunden gesenkt", "Latenz um 1.5 Sekunden gesenkt"),
        ("Latenz um 1.5 Sekunden gesenkt", "Latenz um 1,5 Sekunden gesenkt"),
        ("Latenz um 1,5 Sekunden gesenkt", "Latenz um 1,50 Sekunden gesenkt"),
        ("1.000 Nutzer betreut", "1000 Nutzer betreut"),
        ("1000 Nutzer betreut", "1.000 Nutzer betreut"),
        ("1,000 Nutzer betreut", "1.000 Nutzer betreut"),
        ("1.000.000 Datensätze migriert", "1000000 Datensätze migriert"),
        ("2.5 TB Daten migriert", "2,5 TB Daten migriert"),
        ("Verfügbarkeit von 99,9% erreicht", "Verfügbarkeit von 99.9 % erreicht"),
        ("Budget von 50.000 € verwaltet", "Budget 50000 € verwaltet"),
        ("24/7-Bereitschaft übernommen", "24/7-Bereitschaft"),
        ("Team von 5 Entwicklern koordiniert", "Team von fünf Entwicklern koordiniert"),
        ("Team von fünf Entwicklern koordiniert", "Team von 5 Entwicklern koordiniert"),
        ("Auf Sicherheit acht gegeben", "Sicherheit"),
        ("Vier-Augen-Prinzip eingeführt", "Prinzip eingeführt"),
    )

    def test_a_valid_notation_is_not_a_finding(self):
        for bullet, record in self.ACCEPTED:
            self.assertEqual(found(check_bullet(bullet, record), "CV-05"), [], f"{bullet} | {record}")

    def test_a_changed_value_is_still_a_blocker(self):
        for bullet, record in (
            ("1.000 Nutzer betreut", "1 Nutzer betreut"),
            ("1,5 Sekunden Latenz", "15 Sekunden Latenz"),
            ("1,500 Nutzer betreut", "1,5 Nutzer betreut"),   # a thousands group is not a decimal
            ("0,5 Sekunden Latenz", "5 Sekunden Latenz"),
            ("Team von fünf Entwicklern koordiniert", "Team von 7 Entwicklern koordiniert"),
            ("Team von 5 Entwicklern koordiniert", "Team von sieben Entwicklern koordiniert"),
            ("Drei Standorte betreut", "Standorte betreut"),
            ("Python 3.11 eingesetzt", "Python eingesetzt"),
        ):
            self.assertTrue(found(check_bullet(bullet, record), "CV-05", "Blocker"), f"{bullet} | {record}")

    def test_a_unit_conversion_is_no_spelling_and_a_wrong_unit_is_a_warning(self):
        # `500 GB` for `0,5 TB` is another figure and stays a finding: the value is not recomputed; write the unit as in the record
        self.assertTrue(found(check_bullet("500 GB Daten migriert", "0,5 TB Daten migriert"), "CV-05", "Blocker"))
        self.assertTrue(found(check_bullet("500 TB Daten migriert", "500 GB Daten migriert"), "CV-05", "Warnung"))

    def test_a_figure_that_is_nowhere_gives_one_finding_not_two(self):
        # `24/7` was read as 24 and 7 and reported twice
        self.assertEqual(len(found(check_bullet("24/7-Bereitschaft übernommen", "Bereitschaft"), "CV-05")), 1)

    def test_number_variants_equate_notation_only(self):
        variants = cv_checks.number_variants
        self.assertTrue({"1000", "1.000", "1,000"} <= variants("1.000"))
        self.assertIn("1000", variants("1.000"))
        self.assertIn("1.5", variants("1,5"))
        self.assertNotIn("1", variants("1.000"))
        self.assertNotIn("1.500", variants("1,5"))
        self.assertIn("0.5", variants("0,500"))  # a leading 0 makes it a decimal
        self.assertEqual(variants("24/7"), {"24/7"})
        self.assertEqual(variants("2021"), {"2021"})  # a year stays a year

    def test_a_figure_inside_a_longer_number_is_no_match(self):
        self.assertFalse(re.search(cv_checks.number_pattern("10"), "100 Nutzer"))
        self.assertFalse(re.search(cv_checks.number_pattern("1,5"), "11,5 Nutzer"))
        self.assertFalse(re.search(cv_checks.number_pattern("1,5"), "1,55 Nutzer"))


class StationTests(unittest.TestCase):
    """Group B. Several stations at one employer, spelling variants, overlap."""

    GRUNDLAGE = (
        "## Berufserfahrung\n\n"
        "### 01/2022 – heute | Technischer Teamkoordinator | Musterfirma GmbH, Berlin\n- Technische Aufgaben im Team koordiniert.\n- Führung: nein\n\n"
        "### 06/2019 – 12/2021 | Senior Administrator | Musterfirma GmbH, Berlin\n- Betrieb von Servern.\n- Führung: nein\n\n"
        "### 03/2017 – 05/2019 | Administrator | Musterfirma GmbH, Berlin\n- Betrieb von Servern an 3 Standorten.\n- Führung: nein\n")

    def cv(self, *stations):
        return "## Berufserfahrung\n\n" + "\n".join(stations)

    S1 = "### 01/2022 – heute | Technischer Teamkoordinator | Musterfirma GmbH, Berlin\n- Technische Aufgaben im Team koordiniert.\n"
    S2 = "### 06/2019 – 12/2021 | Senior Administrator | Musterfirma GmbH, Berlin\n- Server betrieben.\n"
    S3 = "### 03/2017 – 05/2019 | Administrator | Musterfirma GmbH, Berlin\n- Server an 3 Standorten betrieben.\n"

    def test_a_promotion_path_at_one_employer_is_valid(self):
        self.assertEqual(rules(run(self.cv(self.S1, self.S2, self.S3), self.GRUNDLAGE)), [])

    def test_the_same_roles_are_not_duplicates_of_each_other(self):
        # three stations, one employer: no CV-09 and no CV-15 for the repeated employer
        found_ = run(self.cv(self.S1, self.S2, self.S3), self.GRUNDLAGE)
        self.assertNotIn("CV-09", rules(found_))
        self.assertNotIn("CV-15", rules(found_))

    def test_a_spelling_variant_is_a_hint_not_a_blocker(self):
        for old, new in (("Musterfirma GmbH, Berlin", "Musterfirma, Berlin"),          # legal form left out
                         ("Senior Administrator", "Senior-Administrator"),              # hyphen
                         ("Technischer Teamkoordinator", "Technischer Team-Koordinator"),
                         ("Musterfirma GmbH", "Muster-Firma GmbH")):
            variant = self.S2.replace(old, new) if old in self.S2 else self.S1.replace(old, new)
            findings = run(self.cv(variant), self.GRUNDLAGE)
            self.assertEqual(rules(findings, "Blocker"), [], (old, new))
            self.assertIn("CV-15", rules(findings, "Hinweis"), (old, new))

    def test_other_names_stay_a_blocker(self):
        for old, new in (("Musterfirma GmbH", "Musterfirma AG"),           # another legal form is another employer
                         ("Senior Administrator", "Leitender Administrator"),
                         ("Musterfirma GmbH", "Beispiel GmbH")):
            self.assertIn("CV-15", rules(run(self.cv(self.S2.replace(old, new)), self.GRUNDLAGE), "Blocker"), (old, new))

    def test_overlap_at_one_employer_is_a_hint_and_parallel_work_elsewhere_is_not(self):
        grundlage = ("## Berufserfahrung\n\n### 01/2020 – heute | Senior Admin | Alpha GmbH\n- a.\n- Führung: nein\n\n"
                     "### 01/2017 – 06/2020 | Admin | Alpha GmbH\n- b.\n- Führung: nein\n\n"
                     "### 06/2019 – 06/2020 | Berater | Beta GmbH\n- c.\n- Führung: nein\n")
        cv = self.cv("### 01/2020 – heute | Senior Admin | Alpha GmbH\n- a.\n", "### 06/2019 – 06/2020 | Berater | Beta GmbH\n- c.\n",
                     "### 01/2017 – 06/2020 | Admin | Alpha GmbH\n- b.\n")
        hints = found(run(cv, grundlage), "CV-04", "Hinweis")
        self.assertEqual(len(hints), 1)
        self.assertIn("Alpha GmbH", hints[0]["befund"])
        self.assertNotIn("Beta", hints[0]["befund"])

    def test_a_change_of_role_in_one_month_is_no_overlap(self):
        grundlage = ("## Berufserfahrung\n\n### 06/2020 – heute | Senior Admin | Alpha GmbH\n- a.\n- Führung: nein\n\n"
                     "### 01/2017 – 06/2020 | Admin | Alpha GmbH\n- b.\n- Führung: nein\n")
        cv = self.cv("### 06/2020 – heute | Senior Admin | Alpha GmbH\n- a.\n", "### 01/2017 – 06/2020 | Admin | Alpha GmbH\n- b.\n")
        self.assertEqual(found(run(cv, grundlage), "CV-04"), [])

    def test_a_short_parallel_station_inside_a_longer_one_hides_no_end(self):
        # before F-05: A starts 01/2021, B runs 01/2015 – 12/2020, C (03/2016 – 04/2016) sits inside B. The gap was measured
        # from the end of C to the start of A: a Blocker for a CV without any gap
        grundlage = ("## Berufserfahrung\n\n### 01/2021 – heute | A | X\n- a.\n- Führung: nein\n\n### 01/2015 – 12/2020 | B | Y\n- b.\n- Führung: nein\n\n"
                     "### 03/2016 – 04/2016 | C | Z\n- c.\n- Führung: nein\n")
        cv = self.cv("### 01/2021 – heute | A | X\n- a.\n", "### 01/2015 – 12/2020 | B | Y\n- b.\n", "### 03/2016 – 04/2016 | C | Z\n- c.\n")
        self.assertEqual(found(run(cv, grundlage), "CV-13"), [])

    def test_a_real_gap_beside_a_parallel_station_is_still_found(self):
        grundlage = ("## Berufserfahrung\n\n### 01/2021 – heute | A | X\n- a.\n- Führung: nein\n\n### 01/2015 – 06/2019 | B | Y\n- b.\n- Führung: nein\n\n"
                     "### 03/2016 – 04/2016 | C | Z\n- c.\n- Führung: nein\n")
        cv = self.cv("### 01/2021 – heute | A | X\n- a.\n", "### 01/2015 – 06/2019 | B | Y\n- b.\n", "### 03/2016 – 04/2016 | C | Z\n- c.\n")
        self.assertEqual(len(found(run(cv, grundlage), "CV-13", "Blocker")), 1)


class LeadershipTests(unittest.TestCase):
    """Group C. Which wording claims people, which claims a technical or project responsibility."""

    def bullet(self, bullet, record="Technische Aufgaben im Team koordiniert.", fuehrung="nein"):
        return run(station_cv(bullet), station_grundlage(record).replace("Führung: nein", f"Führung: {fuehrung}"))

    def test_technical_coordination_and_taking_part_are_no_leadership(self):
        for bullet, record in (
            ("Technische Aufgaben innerhalb eines Teams koordiniert", "Technische Aufgaben innerhalb eines Teams koordiniert."),
            ("Mitarbeit bei der Einführung einer Plattform", "Mitarbeit bei der Einführung einer Plattform."),
            ("Betrieb einer Plattform verantwortet", "Betrieb einer Plattform verantwortet."),
            ("Projektleitung für die technische Einführung", "Projektleitung für die technische Einführung einer Plattform."),
            ("Fachgespräche mit dem Team geführt", "Fachgespräche."),
            ("Workshops für das Team geleitet", "Workshops."),
            ("Teamsitzungen geleitet", "Teamsitzungen."),
            ("Weiterbildung zur Führung im Team besucht", "Weiterbildung."),
        ):
            self.assertEqual(found(self.bullet(bullet, bullet if "verantwortet" in bullet else record), "CV-16"), [], bullet)

    def test_personnel_leadership_without_a_record_is_a_blocker(self):
        for bullet in ("Entwicklungsteam geleitet", "Plattformteam geführt", "Leitung eines Teams",
                       "Leitung der Abteilung übernommen", "Abteilungsleiter für den Betrieb", "Gruppenleitung Betrieb",
                       "Disziplinarische Führung übernommen"):
            self.assertTrue(found(self.bullet(bullet), "CV-16", "Blocker"), bullet)

    def test_recorded_leadership_may_be_written(self):
        for bullet in ("Entwicklungsteam geleitet", "Leitung der Abteilung übernommen"):
            self.assertEqual(found(self.bullet(bullet, "Teamleitung.", "ja"), "CV-16"), [], bullet)

    def test_a_project_lead_without_a_record_is_a_warning_not_personnel_leadership(self):
        findings = self.bullet("Projektleitung für die technische Einführung", "Technische Einführung einer Plattform.")
        self.assertEqual(found(findings, "CV-16"), [])
        self.assertTrue(found(findings, "CV-22", "Warnung"))

    def test_a_title_of_the_station_is_evidence_for_the_project_role(self):
        header = "### 04/2021 – heute | Projektleiter | Musterfirma GmbH, Berlin"
        findings = run(station_cv("Projektleitung der Einführung", header=header), station_grundlage("Einführung.", header=header))
        self.assertEqual(found(findings, "CV-22"), [])

    def test_overall_responsibility_without_a_record_is_a_warning(self):
        findings = self.bullet("Gesamtverantwortung für die Einführung einer Plattform", "Mitarbeit bei der Einführung einer Plattform.")
        self.assertTrue(found(findings, "CV-22", "Warnung"))


class SkillAndCertificateTests(unittest.TestCase):
    """Group D. Spelling variants are accepted, similar names are not equated, a certificate keeps its year and its status."""

    def entry(self, section, entry, record):
        body = station_grundlage("Betrieb.") + f"\n## {section}\n- {record}\n"
        return run(station_cv("Betrieb.") + f"\n## {section}\n- {entry}\n", body)

    def test_spelling_variants_of_one_name_are_accepted(self):
        for entry, record in (("Container: K8s", "Container: Kubernetes"), ("Container: Kubernetes", "Container: K8s"),
                              ("Datenbanken: Postgres", "Datenbanken: PostgreSQL"), ("Sprachen: NodeJS", "Sprachen: Node.js"),
                              ("Automatisierung: IaC", "Automatisierung: Infrastructure as Code"), ("Cloud: AWS", "Cloud: Amazon Web Services"),
                              ("Werkzeuge: terraform", "Werkzeuge: Terraform"), ("CI: GitLab-CI", "CI: GitLab CI")):
            self.assertEqual(found(self.entry("IT- und Fachkenntnisse", entry, record), "CV-19"), [], entry)

    def test_a_name_that_says_more_is_not_equated(self):
        for entry, record in (("Container: Kubernetes Administration", "Container: Kubernetes"),
                              ("Automatisierung: Infrastructure as Code", "Automatisierung: Terraform"),
                              ("Sprachen: C", "Sprachen: C#"), ("Sprachen: Java", "Sprachen: JavaScript"),
                              ("Sprachen: Python 3", "Sprachen: Python"), ("Container: Kube", "Container: Kubernetes")):
            self.assertTrue(found(self.entry("IT- und Fachkenntnisse", entry, record), "CV-19", "Blocker"), entry)

    def test_a_certificate_name_is_never_equated_by_similarity(self):
        for entry, record in (("2022: CKAD", "2022: CKA"), ("2022: Certified Kubernetes Administrator", "2022: CKA"),
                              ("AWS Solutions Architect Professional", "AWS Solutions Architect Associate"),
                              ("ITIL 3 Foundation", "ITIL 4 Foundation")):
            self.assertTrue(found(self.entry("Weiterbildung und Zertifikate", entry, record), "CV-19", "Blocker"), entry)

    def test_a_version_marker_is_a_spelling(self):
        self.assertEqual(found(self.entry("Weiterbildung und Zertifikate", "ITIL 4 Foundation", "ITIL v4 Foundation"), "CV-19"), [])

    def test_a_certificate_with_its_own_year_and_status_is_accepted(self):
        self.assertEqual(found(self.entry("Weiterbildung und Zertifikate", "2022: CKA (gültig)", "2022: CKA (gültig)"), "CV-19"), [])
        self.assertEqual(found(self.entry("Weiterbildung und Zertifikate", "CKA", "2022: CKA"), "CV-19"), [])

    def test_a_wrong_year_is_a_blocker_and_an_unrecorded_year_a_warning(self):
        self.assertTrue(found(self.entry("Weiterbildung und Zertifikate", "2023: CKA", "2022: CKA"), "CV-19", "Blocker"))
        self.assertTrue(found(self.entry("Weiterbildung und Zertifikate", "2023: CKA", "CKA"), "CV-19", "Warnung"))

    def test_an_expired_certificate_is_not_shown_as_current(self):
        findings = self.entry("Weiterbildung und Zertifikate", "CKA (gültig)", "2019: CKA (abgelaufen 2022)")
        self.assertTrue(found(findings, "CV-19", "Blocker"))
        hint = self.entry("Weiterbildung und Zertifikate", "2019: CKA", "2019: CKA (abgelaufen 2022)")
        self.assertEqual(rules(hint, "Blocker"), [])
        self.assertTrue(found(hint, "CV-19", "Hinweis"))

    def test_an_invented_status_is_a_warning(self):
        findings = self.entry("Weiterbildung und Zertifikate", "2024: CKA (in Vorbereitung)", "2024: CKA")
        self.assertTrue(found(findings, "CV-19", "Warnung"))
        self.assertEqual(found(findings, "CV-19", "Blocker"), [])


class PeriodTests(unittest.TestCase):
    """Group E. A gap needs an entry, an unfinished or neutral entry does not block, and the wording follows CG-9."""

    A = "### 07/2021 – heute | Admin | Alpha GmbH"
    B = "### 01/2019 – 03/2021 | Admin | Beta GmbH"
    GRUNDLAGE = f"## Berufserfahrung\n\n{A}\n- a.\n- Führung: nein\n\n{B}\n- b.\n- Führung: nein\n"

    def cv(self, middle="", a=None, b=None):
        return f"## Berufserfahrung\n\n{a or self.A}\n- a.\n\n{middle}{b or self.B}\n- b.\n"

    def test_march_to_april_and_two_months_are_no_gap(self):
        for start in ("04/2021", "05/2021", "06/2021"):
            a = self.A.replace("07/2021", start)
            grundlage = self.GRUNDLAGE.replace("07/2021", start)
            self.assertEqual(found(run(self.cv(a=a), grundlage), "CV-13"), [], start)

    def test_three_months_need_an_entry_and_the_listed_wording_closes_it(self):
        self.assertEqual(len(found(run(self.cv(), self.GRUNDLAGE), "CV-13", "Blocker")), 1)
        for middle in ("Elternzeit (04/2021 – 06/2021)\n\n", "Pflege eines Angehörigen\n\n", "### 04/2021 – 06/2021 | Weiterbildung | —\n\n",
                       "### 04/2021 – 06/2021 | Berufliche Neuorientierung | —\n\n"):
            self.assertEqual(found(run(self.cv(middle), self.GRUNDLAGE), "CV-13"), [], middle)

    def test_wording_outside_the_cg9_list_does_not_close_a_gap(self):
        # the list in CG-9 is part of the spec; a dated line with another word is a station only as a `###` entry
        self.assertTrue(found(run(self.cv("Sabbatical (04/2021 – 06/2021)\n\n"), self.GRUNDLAGE), "CV-13", "Blocker"))
        self.assertEqual(found(run(self.cv("### 04/2021 – 06/2021 | Sabbatical | —\n\n"), self.GRUNDLAGE), "CV-13"), [])

    def test_a_parallel_station_covers_a_gap(self):
        middle = "### 01/2021 – 12/2021 | Freiberufler | Selbst\n- x.\n\n"
        grundlage = self.GRUNDLAGE + "\n### 01/2021 – 12/2021 | Freiberufler | Selbst\n- x.\n- Führung: nein\n"
        self.assertEqual(found(run(self.cv(middle), grundlage), "CV-13"), [])

    def test_year_only_periods_are_a_warning_and_a_certain_year_gap_is_a_blocker(self):
        grundlage = "## Berufserfahrung\n\n### 2020 – heute | Admin | Alpha GmbH\n- a.\n- Führung: nein\n\n### 2015 – 2019 | Admin | Beta GmbH\n- b.\n- Führung: nein\n"
        cv = "## Berufserfahrung\n\n### 2020 – heute | Admin | Alpha GmbH\n- a.\n\n### 2015 – 2019 | Admin | Beta GmbH\n- b.\n"
        findings = run(cv, grundlage)
        self.assertEqual(rules(findings, "Blocker"), [])  # 2019 to 2020 may be seamless: not assessable, so only the header warning
        self.assertEqual(rules(findings).count("CV-02"), 2)
        far = run(cv.replace("2020 – heute", "2022 – heute"), grundlage.replace("2020 – heute", "2022 – heute"))
        self.assertTrue(found(far, "CV-13", "Blocker"))

    def test_an_open_end_is_a_placeholder_blocker_and_does_not_crash(self):
        findings = run("## Berufserfahrung\n\n### 06/2019 – [KLÄREN: Ende] | Admin | Alpha GmbH\n- a.\n")
        self.assertIn("CV-01", rules(findings, "Blocker"))


class SeverityTests(unittest.TestCase):
    """Group F. The severity follows the weight of the problem; nothing was moved between levels by F-05."""

    def test_the_levels_of_the_new_findings(self):
        self.assertEqual({f["schweregrad"] for f in found(check_bullet("500 TB Daten migriert", "500 GB Daten migriert"), "CV-05")}, {"Warnung"})
        self.assertEqual({f["schweregrad"] for f in found(check_bullet("Team von fünf Entwicklern koordiniert", "Team von 7 Entwicklern"), "CV-05")}, {"Blocker"})
        grundlage = station_grundlage("a.", header=STATION)
        variant = run(station_cv("a.", header=STATION.replace("Musterfirma GmbH", "Musterfirma")), grundlage)
        self.assertEqual({f["schweregrad"] for f in found(variant, "CV-15")}, {"Hinweis"})

    def test_a_valid_edge_case_does_not_block_the_whole_cv(self):
        cv = station_cv("Latenz um 1,5 Sekunden gesenkt; 1.000 Nutzer betreut.", header=STATION.replace("Musterfirma GmbH", "Musterfirma"))
        findings = run(cv, station_grundlage("Latenz um 1.5 Sekunden gesenkt; 1000 Nutzer betreut."))
        self.assertEqual(rules(findings, "Blocker"), [])


class RegressionTests(unittest.TestCase):
    """Group G. The accepted CVs of the scenario fixtures and the facts in them are untouched."""

    def test_the_accepted_cvs_of_the_scenarios_have_no_finding(self):
        import test_scenarios as scenarios

        for persona, cv, analysis in (("erfahren", "spezialist", "spezialist"), ("erfahren", "leitung", "leitung"),
                                      ("quereinstieg", "quereinstieg", "quereinstieg"), ("einsteiger", "einsteiger", None)):
            findings = scenarios.cv_findings(scenarios.read("cv", cv + ".md"), persona, scenarios.read("analysen", analysis + ".md") if analysis else None)
            self.assertEqual(findings, [], cv)

    def test_the_documented_rules_are_still_listed(self):
        for rule in ("CV-05", "CV-13", "CV-15", "CV-16", "CV-19", "CV-22", "CV-24"):
            self.assertIn(rule, cv_checks.__doc__)


if __name__ == "__main__":
    unittest.main()
