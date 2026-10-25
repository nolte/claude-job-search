"""Fit of an Nachweis to its requirement (audit finding F-03, CG-4.7 to CG-4.9). Synthetic data only.

`cv_checks.py` cannot read the meaning of a requirement and a quote. What it can do, and what these tests run, is to hold the
recorded assessment of `job-application-posting-analysis` against itself: a row that is `erfüllt` while column `Offen` names an
aspect the Nachweis does not show is a contradiction (CV-24), and `teilweise` or `unklar` must say what is open. Whether the
aspects were identified correctly is a model judgement, checked by the reviewer and by the eval case `behavior-evidence-fit`.
The tests therefore show both directions: an overreaching row is caught, and a correct row with other words than the
requirement, or a partial row that stays usable in the Lebenslauf, produces no finding.

| Group | Case | Expected |
|---|---|---|
| A | direct proof of operation | no finding |
| B | technology named, production operation demanded | `erfüllt` + open aspect: CV-24 Blocker (Muss); `teilweise` clean |
| C | several aspects, one covered | `teilweise` with the open aspects named |
| D | ownership demanded, coordination proven | `erfüllt` + open aspect: Blocker; `teilweise` clean |
| E | effect demanded, activity without result | `Wunsch` `erfüllt` + open aspect: Warnung |
| F | indirect evidence | `teilweise`, use `Lebenslauf` stays allowed |
| G | too little context | `unklar` names the missing information; without it a Warnung |
| H | other words, same activity | `erfüllt` + `—`: no finding (no keyword rejection) |
| I | one Nachweis, two requirements | each row judged on its own requirement |
| J | existing analyses | scenario fixtures carry `Offen` and stay clean |
"""

import glob
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cv_checks  # noqa: E402

HEAD = ("| Anforderung | Priorität | Kompetenz | Nachweis | Stärke | Status | Verwendung | Offen |\n"
        "|---|---|---|---|---|---|---|---|\n")
K8S_REQ = "„Erfahrung im produktiven Betrieb einer Kubernetes-Plattform“"
DEV_USE = "[Entwickler](../grundlage/g.md#station): „Kubernetes im Entwicklungsprojekt eingesetzt“"
OPS = "[Plattform](../grundlage/g.md#station): „Verantwortete den laufenden Betrieb eines Kubernetes-Clusters einschließlich Wartung, Monitoring und Störungsbehebung“"


def row(req, prio, proof, strength, status, use, offen):
    return f"| {req} | {prio} | Kompetenz | {proof} | {strength} | {status} | {use} | {offen} |\n"


def check(*rows):
    return cv_checks.check_analysis(HEAD + "".join(rows), "analyse.md")


def rules(findings, severity=None):
    return [f["regel"] for f in findings if severity is None or f["schweregrad"] == severity]


class EvidenceFitTests(unittest.TestCase):
    def test_a_direct_proof_has_no_finding(self):
        self.assertEqual(check(row(K8S_REQ, "Muss", OPS, "stark", "erfüllt", "Lebenslauf", "—")), [])

    def test_b_technology_named_but_production_operation_demanded(self):
        # the F-03 reproduction: Stärke mittel (a described task) passed CG-4.1 although the quote says development project
        overreach = check(row(K8S_REQ, "Muss", DEV_USE, "mittel", "erfüllt", "Lebenslauf", "produktiver Betrieb, Plattform"))
        self.assertIn("CV-24", rules(overreach, "Blocker"))
        honest = check(row(K8S_REQ, "Muss", DEV_USE, "mittel", "teilweise", "Lebenslauf", "produktiver Betrieb, Plattform"))
        self.assertEqual(rules(honest, "Blocker"), [])
        self.assertNotIn("CV-24", rules(honest))
        self.assertIn("CV-07", rules(honest, "Warnung"))  # the Muss gap is still reported (CG-4.5)

    def test_b_the_script_cannot_see_an_open_aspect_nobody_recorded(self):
        # known limit: with `Offen` left at `—` the contradiction does not exist for the script; the reviewer reads the meaning
        silent = check(row(K8S_REQ, "Muss", DEV_USE, "mittel", "erfüllt", "Lebenslauf", "—"))
        self.assertNotIn("CV-24", rules(silent))

    def test_c_partial_match_names_what_is_open(self):
        req = "„Eigenständige Konzeption und Verantwortung für Enterprise-Infrastrukturautomatisierung“"
        proof = "[Admin](../grundlage/g.md#station): „Terraform für die Bereitstellung einzelner Infrastrukturkomponenten verwendet“"
        found = check(row(req, "Muss", proof, "mittel", "teilweise", "Lebenslauf", "Konzeption, Gesamtverantwortung, unternehmensweiter Umfang"))
        self.assertEqual(rules(found, "Blocker"), [])
        self.assertNotIn("CV-24", rules(found))
        self.assertIn("CV-24", rules(check(row(req, "Muss", proof, "mittel", "teilweise", "Lebenslauf", "—")), "Warnung"))

    def test_d_coordination_is_not_leadership(self):
        req = "„Fachliche und disziplinarische Führung eines Teams“"
        proof = "[Lead](../grundlage/g.md#station): „Technische Aufgaben innerhalb eines Teams koordiniert“"
        self.assertIn("CV-24", rules(check(row(req, "Muss", proof, "mittel", "erfüllt", "Lebenslauf", "disziplinarische Führung")), "Blocker"))
        self.assertEqual(rules(check(row(req, "Muss", proof, "mittel", "teilweise", "Lebenslauf", "fachliche und disziplinarische Führung")), "Blocker"), [])

    def test_e_activity_without_result_for_a_wunsch_is_a_warning_not_a_blocker(self):
        req = "„Nachweisbare Verbesserung der Stabilität“"
        proof = "[Dev](../grundlage/g.md#station): „Monitoring der Pipeline betreut“"
        found = check(row(req, "Wunsch", proof, "mittel", "erfüllt", "Lebenslauf", "Ergebnis der Verbesserung"))
        self.assertEqual(rules(found, "Blocker"), [])
        self.assertIn("CV-24", rules(found, "Warnung"))

    def test_f_indirect_evidence_stays_usable(self):
        req = "„Einführung einer Plattform verantwortet“"
        proof = "[Dev](../grundlage/g.md#station): „An der Einführung einer Plattform mitgearbeitet“"
        found = check(row(req, "Muss", proof, "mittel", "teilweise", "Lebenslauf", "Gesamtverantwortung, Ergebnis"))
        self.assertEqual(rules(found, "Blocker"), [])
        self.assertNotIn("CV-24", rules(found))

    def test_g_too_little_context_is_unklar_and_says_what_is_missing(self):
        proof = "[Dev](../grundlage/g.md#station): „Kubernetes genutzt“"
        self.assertNotIn("CV-24", rules(check(row(K8S_REQ, "Muss", proof, "schwach", "unklar", "Rückfrage", "Umgebung (Test oder Produktion), Umfang, Rolle"))))
        self.assertIn("CV-24", rules(check(row(K8S_REQ, "Muss", proof, "schwach", "unklar", "Rückfrage", "—")), "Warnung"))

    def test_h_other_words_for_the_same_activity_are_not_rejected(self):
        req = "„Betrieb von Container-Orchestrierung“"
        proof = "[Plattform](../grundlage/g.md#station): „Laufender Clusterbetrieb: Wartung, Monitoring, Störungsbehebung“"
        self.assertEqual(check(row(req, "Muss", proof, "stark", "erfüllt", "Lebenslauf", "—")), [])

    def test_i_one_nachweis_is_judged_per_requirement(self):
        proof = "[Admin](../grundlage/g.md#station): „Terraform für die Bereitstellung einzelner Infrastrukturkomponenten verwendet“"
        suited = row("„Terraform-Erfahrung“", "Muss", proof, "mittel", "erfüllt", "Lebenslauf", "—")
        unsuited = row("„Konzeption der Enterprise-Infrastrukturautomatisierung“", "Muss", proof, "mittel", "teilweise", "Lebenslauf", "Konzeption, Enterprise-Umfang")
        self.assertEqual(rules(check(suited, unsuited), "Blocker"), [])
        self.assertNotIn("CV-24", rules(check(suited, unsuited)))
        # the same proof recorded as `erfüllt` for the second requirement contradicts its own open aspect
        wrong = row("„Konzeption der Enterprise-Infrastrukturautomatisierung“", "Muss", proof, "mittel", "erfüllt", "Lebenslauf", "Konzeption, Enterprise-Umfang")
        self.assertIn("CV-24", rules(check(suited, wrong), "Blocker"))

    def test_nicht_belegt_needs_no_open_aspect_and_an_old_table_gets_one_warning(self):
        self.assertEqual(check(row("„Go“", "Wunsch", "—", "—", "nicht belegt", "Rückfrage", "—")), [])
        old = ("| Anforderung | Priorität | Kompetenz | Nachweis | Stärke | Status | Verwendung |\n|---|---|---|---|---|---|---|\n"
               "| „Go“ | Muss | Go | [A](../g.md#s): „Go“ | mittel | erfüllt | Lebenslauf |\n")
        found = cv_checks.check_analysis(old, "analyse.md")
        self.assertEqual(rules(found, "Blocker"), [])
        self.assertEqual(rules(found).count("CV-24"), 1)

    def test_j_scenario_analyses_carry_the_column_and_stay_clean(self):
        paths = glob.glob(os.path.join(ROOT, "tests", "fixtures", "szenarien", "analysen", "*.md"))
        self.assertEqual(len(paths), 3)
        for path in paths:
            with open(path, encoding="utf-8") as handle:
                found = cv_checks.check_analysis(handle.read(), path)
            self.assertEqual(found, [], path)


if __name__ == "__main__":
    unittest.main()
