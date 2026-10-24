"""Scenario tests A to H of the critical findings audit (AUDIT-TEST-001).

Each scenario runs the deterministic part of the pipeline on the fictional fixtures in
tests/fixtures/szenarien/ (a Grundlage, a posting, its analysis, a good Lebenslauf and letters) and on
variants with one planted defect. What a model decides while writing (selection, wording, tone) cannot be
tested here; tests/fixtures/szenarien/README.md lists per scenario what is automated and what stays review.
All data is synthetic.
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cv_checks  # noqa: E402

FIXTURES = os.path.join(ROOT, "tests", "fixtures", "szenarien")
HASH_SCRIPT = os.path.join(ROOT, "scripts", "grundlage_hash.py")
EXPORTER = os.path.join(ROOT, "skills", "job-application-export", "scripts", "export_document.py")


def read(*parts):
    with open(os.path.join(FIXTURES, *parts), encoding="utf-8") as handle:
        return handle.read()


def cv_findings(cv, persona, analysis=None):
    """Findings of cv_checks for a Lebenslauf text against the Grundlage fixture `persona`."""
    path = os.path.join(FIXTURES, "grundlage", persona + ".md")
    findings = cv_checks.check_cv(cv, "lebenslauf.md", cv_checks.read_sources([path]), cv_checks.load_records([path]))
    if analysis is not None:
        findings += cv_checks.check_analysis(analysis, "analyse.md")
    return findings


def letter_findings(text, persona, posting=None, analysis=None):
    path = os.path.join(FIXTURES, "grundlage", persona + ".md")
    context = "\n".join(part for part in (posting, analysis) if part)
    return cv_checks.check_letter(text, "anschreiben.md", "letter", cv_checks.read_sources([path]),
                                  cv_checks.load_records([path]), context)


def rules(findings, severity=None):
    return sorted(f["regel"] for f in findings if severity is None or f["schweregrad"] == severity)


def replace(text, old, new):
    assert old in text, old
    return text.replace(old, new, 1)


class FixtureTests(unittest.TestCase):
    """The good documents must stay clean: every scenario below plants a defect in one of them."""

    def test_good_documents_have_no_finding(self):
        for persona, cv, analysis in (("erfahren", "spezialist", "spezialist"), ("erfahren", "leitung", "leitung"),
                                      ("quereinstieg", "quereinstieg", "quereinstieg"), ("einsteiger", "einsteiger", None)):
            found = cv_findings(read("cv", cv + ".md"), persona, read("analysen", analysis + ".md") if analysis else None)
            self.assertEqual(found, [], cv)

    def test_good_letters_have_no_blocker(self):
        for name, persona in (("leitung", "erfahren"), ("quereinstieg", "quereinstieg")):
            found = letter_findings(read("briefe", name + ".md"), persona, read("anzeigen", name + ".md"))
            self.assertEqual(rules(found, "Blocker"), [], name)
            self.assertEqual(rules(found, "Warnung"), [], name)

    def test_personal_data_in_fixtures_is_fictional(self):
        for folder in ("grundlage", "anzeigen", "analysen", "cv", "briefe"):
            for name in os.listdir(os.path.join(FIXTURES, folder)):
                text = read(folder, name)
                self.assertNotRegex(text, r"@[a-z0-9-]+\.[a-z]{2,}", name)
                self.assertNotRegex(text, r"\+?\d{3,}[ /-]\d{5,}", name)


class DocumentationTests(unittest.TestCase):
    def test_readme_lists_every_scenario_once(self):
        readme = read("README.md")
        for letter in "ABCDEFGH":
            self.assertEqual(len(re.findall(rf"^\| {letter} ", readme, re.M)), 1, letter)
        names = {name for name in globals() if re.fullmatch(r"Scenario[A-H]_\w+", name)}
        self.assertEqual(sorted(name[8] for name in names), list("ABCDEFGH"))


class ScenarioA_TechnicalSpecialist(unittest.TestCase):
    """A: technical evidence is represented accurately, leadership is not exaggerated, no unsupported skill appears."""

    def test_unsupported_skill_certificate_and_tool_are_blocked(self):
        cv = replace(read("cv", "spezialist.md"), "- Programmiersprachen: Python, Go", "- Programmiersprachen: Python, Go, Rust")
        cv = replace(cv, "- 2023: Zertifikat Beispiel-Cloud, Beispiel-Akademie, Berlin", "- 2024: CKA, CNCF")
        found = cv_findings(cv, "erfahren", read("analysen", "spezialist.md"))
        self.assertEqual(rules(found, "Blocker").count("CV-19"), 3)  # Rust, CKA, CNCF

    def test_leadership_wording_on_a_station_without_leadership_is_blocked(self):
        cv = replace(read("cv", "spezialist.md"), "- Docker-Container im Betrieb mitbetreut", "- Teamleitung für 7 Entwickler übernommen")
        self.assertIn("CV-16", rules(cv_findings(cv, "erfahren", read("analysen", "spezialist.md")), "Blocker"))

    def test_muss_requirement_without_evidence_cannot_be_fulfilled(self):
        analysis = replace(read("analysen", "spezialist.md"), "| „Python“ | Muss | Python | [Softwareentwicklerin](../grundlage/erfahren.md#station): „REST-Schnittstellen in Python“ | stark |", "| „Python“ | Muss | Python | — | — |")
        self.assertIn("CV-07", rules(cv_findings(read("cv", "spezialist.md"), "erfahren", analysis), "Blocker"))

    def test_a_wunsch_with_weak_evidence_stays_a_partial_match(self):
        # Terraform stands in the tool list only: the analysis says `teilweise`, and that is allowed
        self.assertEqual(cv_findings(read("cv", "spezialist.md"), "erfahren", read("analysen", "spezialist.md")), [])


class ScenarioB_TechnicalLeadership(unittest.TestCase):
    """B: actual leadership is represented, team size and management claims are not invented."""

    def test_recorded_leadership_may_be_written(self):
        self.assertNotIn("CV-16", rules(cv_findings(read("cv", "leitung.md"), "erfahren")))

    def test_invented_team_size_is_blocked(self):
        cv = replace(read("cv", "leitung.md"), "für 4 Entwickler", "für 12 Mitarbeiter")
        self.assertIn("CV-05", rules(cv_findings(cv, "erfahren"), "Blocker"))

    def test_leadership_moved_to_the_station_without_it_is_blocked(self):
        cv = replace(read("cv", "leitung.md"), "- REST-Schnittstellen in Python entwickelt; Schnittstelle für 3 Partnersysteme umgesetzt",
                     "- Disziplinarische und fachliche Leitung für 4 Entwickler übernommen")
        self.assertIn("CV-16", rules(cv_findings(cv, "erfahren"), "Blocker"))

    def test_the_posting_number_is_not_taken_over_as_experience(self):
        # the posting asks for 8 years of experience; the periods reach 13 years, so the claim is fine,
        # but 20 years is the posting's number copied and the periods do not reach it
        letter = replace(read("briefe", "leitung.md"), "seit 2022 betreibe ich", "mit 20 Jahren Berufserfahrung betreibe ich")
        found = letter_findings(letter, "erfahren", read("anzeigen", "leitung.md"))
        self.assertIn("BR-03", rules(found, "Blocker"))

    def test_leadership_in_the_letter_is_left_to_the_review_with_a_note(self):
        found = letter_findings(read("briefe", "leitung.md"), "erfahren", read("anzeigen", "leitung.md"))
        self.assertEqual(rules(found, "Hinweis"), ["BR-04"])

    def test_leadership_in_the_letter_without_any_recorded_leadership_is_blocked(self):
        found = letter_findings(read("briefe", "leitung.md"), "einsteiger", read("anzeigen", "leitung.md"))
        self.assertIn("BR-04", rules(found, "Blocker"))


class ScenarioC_CareerChanger(unittest.TestCase):
    """C: transferable evidence is shown, domain experience is not invented, gaps in the posting stay visible."""

    def test_invented_domain_station_is_blocked(self):
        cv = replace(read("cv", "quereinstieg.md"), "### 07/2024 – heute | Junior Entwicklerin | Musterfirma GmbH, Berlin",
                     "### 07/2020 – heute | Softwareentwicklerin | Musterfirma GmbH, Berlin")
        self.assertIn("CV-15", rules(cv_findings(cv, "quereinstieg"), "Blocker"))

    def test_unproven_wunsch_is_reported_for_a_query_not_claimed(self):
        analysis = read("analysen", "quereinstieg.md")
        self.assertEqual(rules(cv_findings(read("cv", "quereinstieg.md"), "quereinstieg", analysis), "Blocker"), [])
        claimed = replace(analysis, "| „Python“ | Muss | Python | [Junior Entwicklerin](../grundlage/quereinstieg.md#station): „Python-Skripten“ | mittel | erfüllt |", "| „Python“ | Muss | Python | — | — | erfüllt |")
        self.assertIn("CV-07", rules(cv_findings(read("cv", "quereinstieg.md"), "quereinstieg", claimed), "Blocker"))

    def test_docker_claimed_without_proof_is_blocked(self):
        cv = replace(read("cv", "quereinstieg.md"), "- Programmiersprachen: Python", "- Programmiersprachen: Python\n- Werkzeuge: Docker")
        self.assertIn("CV-19", rules(cv_findings(cv, "quereinstieg"), "Blocker"))

    def test_retraining_period_is_a_station_and_closes_the_gap(self):
        without = read("cv", "quereinstieg.md")
        start = without.index("### 07/2022")
        end = without.index("### 08/2009")
        self.assertIn("CV-13", rules(cv_findings(without[:start] + without[end:], "quereinstieg"), "Blocker"))
        self.assertNotIn("CV-13", rules(cv_findings(without, "quereinstieg")))

    def test_retraining_does_not_count_as_work_experience(self):
        # Measured at the letter date 24.10.2026: the work stations reach 183 months (15 years), 207 months (17 years)
        # with the retraining counted. 16 years is reached only if the retraining wrongly counts as work.
        text = read("briefe", "quereinstieg.md")
        text = replace(text, "arbeite seit 2024 als Junior Entwicklerin mit Python.", "arbeite seit 2024 als Junior Entwicklerin mit Python. Ich bringe 16 Jahre Berufserfahrung mit.")
        found = letter_findings(text, "quereinstieg", read("anzeigen", "quereinstieg.md"))
        self.assertIn("BR-03", rules(found, "Blocker"))

    def test_known_limit_years_of_experience_are_not_tied_to_a_domain(self):
        # 13 years as a carpenter reach `10 Jahre Berufserfahrung`; that they are not software experience is a review
        # judgement (CG-13.6 known limit). If the check ever learns the domain, this test is to be turned around.
        text = replace(read("briefe", "quereinstieg.md"), "arbeite seit 2024 als Junior Entwicklerin mit Python.", "arbeite seit 2024 als Junior Entwicklerin mit Python und bringe 10 Jahre Berufserfahrung in der Softwareentwicklung mit.")
        found = letter_findings(text, "quereinstieg", read("anzeigen", "quereinstieg.md"))
        self.assertNotIn("BR-03", rules(found))


class ScenarioD_LimitedExperience(unittest.TestCase):
    """D: no invented metrics, unconfirmed stations are flagged, bullets without a result stay."""

    def test_a_cv_without_metrics_is_clean(self):
        self.assertEqual(cv_findings(read("cv", "einsteiger.md"), "einsteiger"), [])

    def test_an_invented_metric_is_blocked(self):
        cv = replace(read("cv", "einsteiger.md"), "- Code-Reviews begleitet", "- Code-Reviews begleitet; Fehlerquote um 30 % gesenkt")
        self.assertIn("CV-05", rules(cv_findings(cv, "einsteiger"), "Blocker"))

    def test_an_unconfirmed_station_cannot_be_used(self):
        cv = replace(read("cv", "einsteiger.md"), "## Ausbildung und Studium",
                     "### 06/2024 – 08/2024 | Aushilfe Support | Beispiel Markt, Kiel\n- Kundenanfragen am Telefon bearbeitet\n\n## Ausbildung und Studium")
        self.assertIn("CV-20", rules(cv_findings(cv, "einsteiger"), "Blocker"))

    def test_an_invented_language_level_is_blocked(self):
        cv = replace(read("cv", "einsteiger.md"), "- Englisch: B2", "- Englisch: C1")
        self.assertIn("CV-19", rules(cv_findings(cv, "einsteiger"), "Blocker"))


class ScenarioE_MissingInformation(unittest.TestCase):
    """E: what the posting requires and the profile lacks is detected and never silently assumed."""

    def test_unproven_must_requirement_is_reported(self):
        analysis = replace(read("analysen", "leitung.md"), "| „Führungserfahrung“ | Muss | Personalführung | [Teamleiterin Plattform](../grundlage/erfahren.md#station): „Führung: ja“ | stark | erfüllt |", "| „Führungserfahrung“ | Muss | Personalführung | — | — | nicht belegt |")
        found = cv_findings(read("cv", "leitung.md"), "erfahren", analysis)
        self.assertEqual(rules(found, "Warnung"), ["CV-07"])
        self.assertEqual(rules(found, "Blocker"), [])

    def test_the_word_fehlt_is_replaced_by_nicht_belegt(self):
        analysis = replace(read("analysen", "leitung.md"), "nicht belegt", "fehlt")
        self.assertIn("CV-14", rules(cv_findings(read("cv", "leitung.md"), "erfahren", analysis), "Warnung"))

    def test_placeholder_in_any_document_blocks(self):
        cv = replace(read("cv", "leitung.md"), "- 40 Linux-Server betrieben", "- [ERGÄNZEN: Aufgaben]")
        self.assertIn("CV-01", rules(cv_findings(cv, "erfahren"), "Blocker"))
        letter = replace(read("briefe", "leitung.md"), "Die Bereitstellungszeit habe ich von 45 min auf 8 min gesenkt.", "[ERGÄNZEN: Beweggrund]")
        self.assertIn("BR-01", rules(letter_findings(letter, "erfahren"), "Blocker"))

    def test_a_posting_number_in_the_letter_is_a_warning_not_proof(self):
        letter = replace(read("briefe", "leitung.md"), "leite dort ein Team von 4 Entwicklern", "leite dort ein Team von 4 Entwicklern in einem Unternehmen mit 500 Mitarbeitenden")
        found = letter_findings(letter, "erfahren", read("anzeigen", "spezialist.md"))
        self.assertEqual(rules(found, "Warnung"), ["BR-02"])


class ScenarioF_ConflictingInformation(unittest.TestCase):
    """F: a conflict between a document and the Grundlage is detected and not resolved in favour of the document."""

    def test_period_that_differs_from_the_grundlage_is_blocked(self):
        cv = replace(read("cv", "spezialist.md"), "### 03/2022 – heute", "### 01/2021 – heute")
        self.assertIn("CV-06", rules(cv_findings(cv, "erfahren"), "Blocker"))

    def test_title_that_differs_from_the_grundlage_is_blocked(self):
        cv = replace(read("cv", "spezialist.md"), "Teamleiterin Plattform", "Leiterin Plattform")
        self.assertIn("CV-15", rules(cv_findings(cv, "erfahren"), "Blocker"))

    def test_two_grundlage_entries_for_one_station_are_matched_by_period(self):
        path = tempfile.mkdtemp()
        try:
            with open(os.path.join(path, "g.md"), "w", encoding="utf-8") as handle:
                handle.write(read("grundlage", "erfahren.md") + "\n### 01/2020 – 02/2022 | Teamleiterin Plattform | Musterfirma GmbH, Berlin\n- Bestätigt: ja\n")
            sources = [os.path.join(path, "g.md")]
            cv = read("cv", "spezialist.md")
            found = cv_checks.check_cv(cv, "lebenslauf.md", cv_checks.read_sources(sources), cv_checks.load_records(sources))
            self.assertNotIn("CV-06", rules(found))
            cv = replace(cv, "### 03/2022 – heute", "### 05/2022 – heute")
            found = cv_checks.check_cv(cv, "lebenslauf.md", cv_checks.read_sources(sources), cv_checks.load_records(sources))
            self.assertIn("CV-06", rules(found, "Blocker"))
        finally:
            shutil.rmtree(path, ignore_errors=True)

    def test_a_year_that_differs_in_the_letter_is_a_number_the_grundlage_must_hold(self):
        letter = replace(read("briefe", "leitung.md"), "seit 2022 betreibe ich", "seit 2019 betreibe ich")
        self.assertIn("BR-02", rules(letter_findings(letter, "erfahren"), "Blocker"))


class ScenarioG_ProfileMaintenance(unittest.TestCase):
    """G: a change of the Grundlage makes derived documents stale; an unchanged one does not."""

    def hash_of(self, folder):
        konfiguration = os.path.join(folder, "konfiguration.md")
        result = subprocess.run([sys.executable, HASH_SCRIPT, konfiguration], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        import json
        return json.loads(result.stdout)["hash"]

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.grundlage = os.path.join(self.folder, "grundlage.md")
        shutil.copy(os.path.join(FIXTURES, "grundlage", "erfahren.md"), self.grundlage)
        with open(os.path.join(self.folder, "konfiguration.md"), "w", encoding="utf-8") as handle:
            handle.write(f"---\nwurzel: {self.folder}\ngrundlage: {self.grundlage}\n---\n")

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def test_hash_is_stable_and_follows_the_content(self):
        before = self.hash_of(self.folder)
        self.assertEqual(before, self.hash_of(self.folder))
        with open(self.grundlage, "a", encoding="utf-8") as handle:
            handle.write("\n- 2025: Zertifikat Beispiel, Beispiel-Akademie, Berlin\n")
        self.assertNotEqual(before, self.hash_of(self.folder))

    def test_a_cv_made_before_the_change_carries_the_old_hash(self):
        old = self.hash_of(self.folder)
        document = f"---\ngrundlage_hash: {old}\n---\n" + read("cv", "spezialist.md")
        with open(self.grundlage, "a", encoding="utf-8") as handle:
            handle.write("\n- Weiterbildung 2025\n")
        recorded = re.search(r"grundlage_hash: (\w+)", document).group(1)
        self.assertNotEqual(recorded, self.hash_of(self.folder))

    def test_a_correction_in_the_grundlage_reaches_the_check(self):
        # the user corrects the title in the Grundlage; the CV with the old title is then blocked, the new one passes
        with open(self.grundlage, encoding="utf-8") as handle:
            text = handle.read()
        with open(self.grundlage, "w", encoding="utf-8") as handle:
            handle.write(replace(text, "Teamleiterin Plattform", "Leiterin Plattform"))
        cv = read("cv", "spezialist.md")
        sources = [self.grundlage]
        old = cv_checks.check_cv(cv, "lebenslauf.md", cv_checks.read_sources(sources), cv_checks.load_records(sources))
        new = cv_checks.check_cv(replace(cv, "Teamleiterin Plattform", "Leiterin Plattform"), "lebenslauf.md",
                                 cv_checks.read_sources(sources), cv_checks.load_records(sources))
        self.assertIn("CV-15", rules(old, "Blocker"))
        self.assertEqual(rules(new, "Blocker"), [])

    def test_unchanged_stations_keep_their_checks(self):
        self.assertEqual(rules(cv_findings(read("cv", "spezialist.md"), "erfahren"), "Blocker"), [])


@unittest.skipUnless(shutil.which("pandoc"), "pandoc is not installed")
class ScenarioH_Export(unittest.TestCase):
    """H: the exported document equals the approved Markdown, German characters survive, a change is detected."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.source = os.path.join(self.folder, "lebenslauf.md")
        text = read("cv", "spezialist.md")
        text = replace(text, "- Docker-Container im Betrieb mitbetreut", "- Docker-Container im Betrieb mitbetreut; Größe, Maßnahmen und Übergabe für Äpfel")
        with open(self.source, "w", encoding="utf-8") as handle:
            handle.write("---\ngrundlage_hash: " + "0" * 64 + "\nformat: chronologisch\n---\n\n" + text)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def export(self, fmt, *extra):
        return subprocess.run([sys.executable, EXPORTER, self.source, "--format", fmt, "--doc-type", "cv", *extra],
                              capture_output=True, text=True)

    def test_html_export_matches_the_source_and_keeps_german_characters(self):
        result = self.export("html")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Inhaltsprüfung: ok", result.stdout)
        with open(os.path.join(self.folder, "export", "lebenslauf.html"), encoding="utf-8") as handle:
            html = handle.read()
        for word in ("Größe", "Maßnahmen", "Übergabe", "Äpfel", "Universität"):
            self.assertIn(word, html)

    def test_markdown_export_is_a_copy(self):
        self.assertEqual(self.export("md").returncode, 0)
        with open(os.path.join(self.folder, "export", "lebenslauf.md"), encoding="utf-8") as one, open(self.source, encoding="utf-8") as two:
            self.assertEqual(one.read(), two.read())

    def test_manifest_pins_the_source_and_a_changed_source_is_detected(self):
        self.assertEqual(self.export("html").returncode, 0)
        manifest = os.path.join(self.folder, "export", "lebenslauf.html.manifest.json")
        import json
        with open(manifest, encoding="utf-8") as handle:
            pinned = json.load(handle)["quelle"]["sha256"]
        with open(self.source, "rb") as handle:
            self.assertEqual(pinned, hashlib.sha256(handle.read()).hexdigest())
        with open(self.source, "a", encoding="utf-8") as handle:
            handle.write("\n- nachträglich ergänzt\n")
        result = subprocess.run([sys.executable, EXPORTER, "--reproduce", manifest], capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)

    def test_an_export_that_loses_or_adds_words_is_reported(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("export_document", EXPORTER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = read("cv", "spezialist.md")
        self.assertEqual(module.compare_content(source, source), (module.Counter(), module.Counter()))
        missing, extra = module.compare_content(source, source.replace("Kubernetes-Plattform betrieben", "Plattform betrieben") + "\nSenior Architektin")
        self.assertIn("kubernetesplattform", missing)
        self.assertIn("architektin", extra)

    def test_open_placeholders_stay_visible_in_the_export(self):
        # the export does not block on them (the quality gate does, CV-01); it must not hide them either
        with open(self.source, "a", encoding="utf-8") as handle:
            handle.write("\n- [ERGÄNZEN: Aufgaben]\n")
        self.assertEqual(self.export("html").returncode, 0)
        with open(os.path.join(self.folder, "export", "lebenslauf.html"), encoding="utf-8") as handle:
            self.assertIn("ERGÄNZEN", handle.read())


if __name__ == "__main__":
    unittest.main()
