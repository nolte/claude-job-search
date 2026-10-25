"""Semantic fact fidelity (audit finding F-01, spec CG-7.4): the script flags wording that claims more than the station record.

Synthetic Grundlagen only. Each scenario gives the supported lines of one station and one bullet of the Lebenslauf; the
expected result is the set of (rule, severity) pairs. What the script cannot see (a claim without a marker, the meaning of a
paraphrase) is pinned as a known limit and is left to the quality gate review and the reviewer; tests/README.md lists
which component is expected to catch which scenario.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import cv_checks  # noqa: E402
import test_cv_checks as helpers  # noqa: E402

SCRIPT = os.path.join(ROOT, "scripts", "cv_checks.py")
HEAD = "# Lebenslauf\n\n## Berufserfahrung\n\n### 04/2021 – heute | Backend-Entwickler | Musterfirma GmbH, Berlin\n"


def grundlage(lines, fuehrung="nein"):
    body = "\n".join(f"- {line}" for line in lines)
    return ("## Berufserfahrung\n\n### 04/2021 – heute | Backend-Entwickler | Musterfirma GmbH, Berlin\n"
            f"{body}\n- Führung: {fuehrung}\n\n## IT- und Fachkenntnisse\n- Werkzeuge: Kubernetes, Terraform, Python\n")


def check(lines, bullet, fuehrung="nein"):
    found = helpers.run(HEAD + "- " + bullet + "\n", grundlage(lines, fuehrung))
    return sorted({(f["regel"], f["schweregrad"]) for f in found})


NONE = []
CV22 = [("CV-22", "Warnung")]
CV23 = [("CV-23", "Warnung")]
CV16 = [("CV-16", "Blocker")]
CV05 = [("CV-05", "Blocker")]

# (id, group, lines of the station record, bullet, expected, fuehrung)
SCENARIOS = [
    # A responsibility
    ("A1", "responsibility", ["Mitarbeit am Betrieb einer Kubernetes-Plattform."], "Mitarbeit am Betrieb von Kubernetes-Plattformen.", NONE, "nein"),
    ("A2", "responsibility", ["Gemeinsame Verantwortung im Team für den Betrieb der Kubernetes-Plattform."], "Betrieb der Kubernetes-Plattform im Team verantwortet.", NONE, "nein"),
    ("A3", "responsibility", ["Eigenverantwortlich den Betrieb der Kubernetes-Plattform übernommen."], "Betrieb der Kubernetes-Plattform eigenverantwortlich übernommen.", NONE, "nein"),
    ("A4", "responsibility", ["Mitarbeit am Betrieb einer Kubernetes-Plattform."], "Eigenverantwortlich die gesamte Kubernetes-Plattform betrieben.", CV22, "nein"),
    ("A5", "responsibility", ["Betrieb der Kubernetes-Plattform."], "Betrieb der Kubernetes-Plattform verantwortet.", CV22, "nein"),
    # B leadership
    ("B1", "leadership", ["Koordination technischer Aufgaben im Team."], "Technische Arbeit im Team koordiniert.", NONE, "nein"),
    ("B2", "leadership", ["Fachliche Führung technischer Entscheidungen in Architekturfragen."], "Technische Architekturentscheidungen fachlich geführt.", NONE, "nein"),
    ("B3", "leadership", ["Koordination technischer Aufgaben im Team."], "Engineering-Team gemanagt und Mitarbeiter angeleitet.", CV16, "nein"),
    ("B4", "leadership", ["Koordination technischer Aufgaben im Team."], "Teamleitung für fünf Entwickler übernommen.", CV16, "nein"),
    ("B5", "leadership", ["Koordination technischer Aufgaben im Team."], "Technische Entscheidungen verantwortet.", CV22, "nein"),
    ("B6", "leadership", ["Personalverantwortung für 5 Entwickler."], "Team von 5 Entwicklern geleitet.", NONE, "ja"),
    ("B7", "leadership", ["Koordination technischer Aufgaben im Team."], "Technische Aufgaben im Team koordiniert und Kollegen angeleitet.", CV16, "nein"),
    # C expertise
    ("C1", "expertise", ["Terraform in einem Projekt eingesetzt."], "Terraform in einem Projekt eingesetzt.", NONE, "nein"),
    ("C2", "expertise", ["Terraform in Infrastrukturprojekten eingesetzt."], "Terraform für Infrastrukturautomatisierung angewendet.", NONE, "nein"),
    ("C3", "expertise", ["Spezialisierung auf Terraform-Module in 3 Projekten."], "Spezialisierung auf Terraform-Module in 3 Projekten.", NONE, "nein"),
    ("C4", "expertise", ["Terraform in einem Projekt eingesetzt."], "Terraform-Experte mit tiefer Spezialisierung.", CV22, "nein"),
    ("C5", "expertise", ["Terraform in einem Projekt eingesetzt."], "Sehr gute Kenntnisse in Terraform und Kubernetes.", CV22, "nein"),
    # D scope
    ("D1", "scope", ["Beitrag zu einem Abrechnungsservice."], "Zu einem Abrechnungsservice beigetragen.", NONE, "nein"),
    ("D2", "scope", ["Beitrag zu einem Abrechnungsservice."], "Gesamte Abrechnungsplattform entworfen.", CV22, "nein"),
    ("D3", "scope", ["Beitrag zu einem Abrechnungsservice."], "Unternehmensweite Enterprise-Architektur verantwortet.", CV22, "nein"),
    ("D4", "scope", ["Konzeption der gesamten Abrechnungsplattform."], "Gesamte Abrechnungsplattform konzipiert.", NONE, "nein"),
    # E outcomes
    ("E1", "outcome", ["Latenz der Pipeline von 800 ms auf 120 ms gesenkt."], "Latenz der Pipeline von 800 ms auf 120 ms gesenkt.", NONE, "nein"),
    ("E2", "outcome", ["Das Team senkte die Latenz der Pipeline um 40 %."], "Latenz der Pipeline um 40 % gesenkt.", CV23, "nein"),
    ("E3", "outcome", ["Das Team senkte die Latenz der Pipeline um 40 %."], "Im Team die Latenz der Pipeline um 40 % gesenkt.", NONE, "nein"),
    ("E4", "outcome", ["Gemeinsam mit dem Partnerteam die Latenz um 40 % gesenkt."], "Gemeinsam mit dem Partnerteam die Latenz um 40 % gesenkt.", NONE, "nein"),
    ("E5", "outcome", ["Beitrag zu einem Migrationsprojekt."], "Migrationsprojekt eigenständig umgesetzt; Umsatz um 30 % gesteigert.", CV22 + CV05, "nein"),
    ("E6", "outcome", ["Das Team senkte die Latenz um 40 %."], "Teamgröße von 4 Entwicklern; Latenz im Team um 40 % gesenkt.", CV05, "nein"),
    # F valid rephrasing
    ("F1", "rephrasing", ["Mitarbeit am Betrieb einer Kubernetes-Plattform im Team."], "Betrieb von Kubernetes-Plattformen im Team mitgestaltet.", NONE, "nein"),
    ("F2", "rephrasing", ["Terraform in Infrastrukturprojekten eingesetzt."], "Infrastruktur mit Terraform automatisiert.", NONE, "nein"),
    ("F3", "rephrasing", ["Betreuung der Event-Pipeline in Python."], "Event-Pipeline in Python betreut.", NONE, "nein"),
    ("F4", "rephrasing", ["Koordination technischer Aufgaben im Team."], "Technische Arbeit im Team koordiniert.", NONE, "nein"),
    # H target-position tailoring: the posting asks for ownership and expertise, the record does not give it
    ("H1", "tailoring", ["Mitarbeit am Betrieb einer Kubernetes-Plattform."], "Mitarbeit am Betrieb von Kubernetes-Plattformen (Container, Orchestrierung).", NONE, "nein"),
    ("H2", "tailoring", ["Mitarbeit am Betrieb einer Kubernetes-Plattform."], "Eigenverantwortlicher Kubernetes-Experte für Plattformbetrieb.", CV22, "nein"),
]

# Known limits: the script reads wording, not meaning. These statements pass it and go to the gate review and the reviewer.
KNOWN_LIMITS = [
    ("L1", ["Mitarbeit am Betrieb einer Kubernetes-Plattform."], "Betrieb der Kubernetes-Plattform übernommen.", "ownership without a marker word"),
    ("L2", ["Beitrag zu einem Migrationsprojekt."], "Migrationsprojekt abgeschlossen; Umsatz deutlich gesteigert.", "undocumented result without a number"),
    ("L3", ["Beitrag zu einem Abrechnungsservice."], "Abrechnungsplattform entworfen.", "scope widened by a noun"),
]


class ScenarioTable(unittest.TestCase):
    def test_every_scenario(self):
        for ident, group, lines, bullet, expected, fuehrung in SCENARIOS:
            with self.subTest(ident):
                self.assertEqual(check(lines, bullet, fuehrung), sorted(expected), f"{ident} ({group}): {bullet}")

    def test_the_groups_of_the_remediation_are_all_covered(self):
        groups = {s[1] for s in SCENARIOS}
        self.assertEqual(groups, {"responsibility", "leadership", "expertise", "scope", "outcome", "rephrasing", "tailoring"})
        for group in groups:
            positive = [s for s in SCENARIOS if s[1] == group and s[4] == NONE]
            self.assertTrue(positive, f"{group} has no accepted statement, so a false positive would not show")

    def test_known_limits_pass_the_script_and_are_not_a_claim_that_the_statement_is_supported(self):
        # pinned on purpose: when the script learns to see one of them, this test turns and the matrix is updated
        for ident, lines, bullet, why in KNOWN_LIMITS:
            self.assertEqual(check(lines, bullet), [], f"{ident} ({why})")

    def test_a_marker_in_the_record_of_another_station_does_not_count(self):
        source = (grundlage(["Mitarbeit am Betrieb einer Kubernetes-Plattform."])
                  + "\n### 09/2018 – 03/2021 | Softwareentwickler | Beispiel AG, Hamburg\n- Eigenverantwortlich die gesamte Plattform betrieben.\n")
        found = helpers.run(HEAD + "- Eigenverantwortlich die gesamte Plattform betrieben.\n", source)
        self.assertEqual(sorted({(f["regel"], f["schweregrad"]) for f in found}), CV22)

    def test_the_finding_names_the_dimension_the_evidence_and_a_way_out(self):
        found = helpers.run(HEAD + "- Terraform-Experte für Infrastruktur.\n",
                            grundlage(["Terraform in Infrastrukturprojekten eingesetzt."]))
        text = next(f["befund"] for f in found if f["regel"] == "CV-22")
        for part in ("„Experte“ (Expertise)", "Beleg: Terraform in Infrastrukturprojekten eingesetzt.", "Mit dem Nutzer klären"):
            self.assertIn(part, text)

    def test_one_finding_per_bullet_not_one_per_marker(self):
        found = helpers.run(HEAD + "- Unternehmensweite Enterprise-Architektur eigenverantwortlich verantwortet.\n",
                            grundlage(["Beitrag zu einem Abrechnungsservice."]))
        self.assertEqual([f["regel"] for f in found].count("CV-22"), 1)


class ExistingChecksStay(unittest.TestCase):
    """G: the semantic rules sit next to the existing fact checks and replace none of them."""

    def test_the_existing_rules_still_fire_together_with_the_new_one(self):
        cv = ("# Lebenslauf\n\n## Berufserfahrung\n\n### 04/2021 – heute | Backend-Entwickler | Musterfirma GmbH, Berlin\n"
              "- Plattform eigenverantwortlich betrieben; Kosten um 70 % gesenkt. [ERGÄNZEN: Aufgaben]\n"
              "- Teamleitung für fünf Entwickler.\n\n"
              "### 01/2010 – 03/2012 | Architekt | Erfundene AG, Berlin\n- Architektur entworfen.\n\n"
              "## IT- und Fachkenntnisse\n- Werkzeuge: Rust\n")
        found = helpers.run(cv, grundlage(["Mitarbeit am Betrieb einer Kubernetes-Plattform."]))
        rules = {f["regel"] for f in found}
        for rule in ("CV-01", "CV-05", "CV-15", "CV-16", "CV-19", "CV-22"):
            self.assertIn(rule, rules)

    def test_a_clean_document_has_no_semantic_finding(self):
        found = helpers.run(helpers.CLEAN_CV, helpers.GRUNDLAGE)
        self.assertEqual([f["regel"] for f in found if f["regel"] in ("CV-22", "CV-23")], [])

    def test_the_fixture_documents_stay_clean(self):
        # the good Lebenslauf of tests/fixtures/szenarien are checked in test_scenarios; here only the new rules
        base = os.path.join(ROOT, "tests", "fixtures", "szenarien")
        for persona, cv in (("erfahren", "spezialist"), ("erfahren", "leitung"), ("quereinstieg", "quereinstieg"), ("einsteiger", "einsteiger")):
            with open(os.path.join(base, "cv", cv + ".md"), encoding="utf-8") as handle:
                text = handle.read()
            with open(os.path.join(base, "grundlage", persona + ".md"), encoding="utf-8") as handle:
                source = handle.read()
            found = helpers.run(text, {"grundlage.md": source})
            self.assertEqual([f["regel"] for f in found if f["regel"] in ("CV-22", "CV-23")], [], cv)


class ApprovalAndGate(unittest.TestCase):
    """I and J: the script reports and never edits; a Blocker ends with exit code 1, a Warnung with 0."""

    def run_cli(self, cv, source):
        with tempfile.TemporaryDirectory() as tmp:
            cv_path, source_path = os.path.join(tmp, "lebenslauf.md"), os.path.join(tmp, "grundlage.md")
            with open(cv_path, "w", encoding="utf-8") as handle:
                handle.write(cv)
            with open(source_path, "w", encoding="utf-8") as handle:
                handle.write(source)
            before = [hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (cv_path, source_path)]
            result = subprocess.run([sys.executable, SCRIPT, cv_path, "--grundlage", source_path], capture_output=True, text=True)
            after = [hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (cv_path, source_path)]
            return result, before, after, sorted(os.listdir(tmp))

    def test_detected_issues_change_neither_the_profile_source_nor_the_document(self):
        source = grundlage(["Mitarbeit am Betrieb einer Kubernetes-Plattform."])
        for bullet in ("Eigenverantwortlich die gesamte Plattform betrieben.", "Teamleitung für fünf Entwickler."):
            result, before, after, files = self.run_cli(HEAD + "- " + bullet + "\n", source)
            self.assertEqual(before, after, bullet)
            self.assertEqual(files, ["grundlage.md", "lebenslauf.md"], "the script writes no file")
            self.assertTrue(json.loads(result.stdout)["befunde"], bullet)

    def test_a_warning_alone_does_not_block_and_a_blocker_does(self):
        source = grundlage(["Mitarbeit am Betrieb einer Kubernetes-Plattform."])
        warning, *_ = self.run_cli(HEAD + "- Terraform-Experte für Infrastruktur.\n", source)
        self.assertEqual(warning.returncode, 0, warning.stdout)
        self.assertEqual(json.loads(warning.stdout)["zusammenfassung"]["Blocker"], 0)
        blocker, *_ = self.run_cli(HEAD + "- Teamleitung für fünf Entwickler.\n", source)
        self.assertEqual(blocker.returncode, 1, blocker.stdout)

    def test_without_a_record_the_semantic_rules_stay_silent(self):
        found = cv_checks.check_cv(HEAD + "- Eigenverantwortlich die gesamte Plattform betrieben.\n", "lebenslauf.md")
        self.assertEqual([f["regel"] for f in found if f["regel"] in ("CV-22", "CV-23")], [])
        self.assertIn("CV-01 to CV-23", subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, text=True).stdout)


class Documentation(unittest.TestCase):
    def read(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
            return handle.read()

    def test_the_rules_are_documented_where_they_are_applied(self):
        spec = self.read("spec", "job-application", "cv-generierung", "en.md")
        gate = self.read("skills", "job-application-quality-gate", "SKILL.md")
        reviewer = self.read("agents", "job-application-reviewer.md")
        create = self.read("skills", "job-application-cv-create", "SKILL.md")
        for rule in ("CV-22", "CV-23"):
            for name, text in (("spec", spec), ("gate", gate), ("create", create)):
                self.assertIn(rule, text, f"{rule} in {name}")
        self.assertIn("### CG-7.4 Semantic fidelity", spec)
        for dimension in ("Activity", "Responsibility", "Leadership", "Expertise", "Scope", "Outcome"):
            self.assertRegex(spec, rf"\| {dimension} \|", dimension)
        self.assertIn("## Aussagenstärke prüfen", reviewer)
        self.assertIn("the agent writes nothing and changes no\ndata", reviewer)

    def test_the_matrix_lists_every_scenario_once(self):
        matrix = self.read("tests", "README.md")
        for ident in [s[0] for s in SCENARIOS] + [s[0] for s in KNOWN_LIMITS]:
            self.assertEqual(len(re.findall(rf"^\| {ident} \|", matrix, re.M)), 1, ident)


if __name__ == "__main__":
    unittest.main()
