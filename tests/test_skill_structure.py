"""Structural checks of skills, agents and cross-references (tests/README.md, planned checks).

Verifies that every skill folder matches its frontmatter name, that referenced spec and
requirement files and helper scripts exist, and that see_also and dont_use alternatives name
an existing skill or agent.
"""

import glob
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))
AGENTS = sorted(glob.glob(os.path.join(ROOT, "agents", "*.md")))


def frontmatter(path):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return match.group(1) if match else "", text


def names_of_skills_and_agents():
    names = {os.path.basename(os.path.dirname(p)) for p in SKILLS}
    names |= {os.path.splitext(os.path.basename(p))[0] for p in AGENTS}
    return names


class SkillStructureTests(unittest.TestCase):
    def test_skills_exist(self):
        self.assertTrue(SKILLS)

    def test_frontmatter_name_matches_folder(self):
        for path in SKILLS:
            header, _ = frontmatter(path)
            folder = os.path.basename(os.path.dirname(path))
            match = re.search(r"^name: (.+)$", header, re.M)
            self.assertIsNotNone(match, path)
            self.assertEqual(match.group(1).strip(), folder, path)

    def test_description_present(self):
        for path in SKILLS + AGENTS:
            header, _ = frontmatter(path)
            self.assertRegex(header, re.compile(r"^description: .{20,}", re.M), path)

    def test_referenced_spec_and_requirement_files_exist(self):
        pattern = re.compile(r"((?:spec|project)/[A-Za-z0-9_./-]+\.md)")
        missing = []
        for path in SKILLS + AGENTS:
            with open(path, encoding="utf-8") as handle:
                for ref in set(pattern.findall(handle.read())):
                    if not os.path.isfile(os.path.join(ROOT, ref)):
                        missing.append(f"{os.path.relpath(path, ROOT)} -> {ref}")
        self.assertEqual(missing, [])

    def test_referenced_scripts_exist(self):
        pattern = re.compile(r"scripts/([A-Za-z0-9_]+\.py)")
        present = {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True)}
        missing = []
        for path in SKILLS + AGENTS:
            with open(path, encoding="utf-8") as handle:
                for script in set(pattern.findall(handle.read())):
                    if script not in present:
                        missing.append(f"{os.path.relpath(path, ROOT)} -> {script}")
        self.assertEqual(missing, [])

    def test_no_fixed_job_application_paths(self):
        # lokale-struktur LS-2.6: the only fixed path is the Anker job-application/konfiguration.md; every other
        # path is written as <wurzel>/… . The bare default root `job-application/` (followed by a backtick or a
        # space) and spec paths (spec/job-application/…) are allowed.
        pattern = re.compile(r"(?<![\w/-])job-application/(?!konfiguration\.md)(?=[A-Za-z<])")
        offending = []
        for path in SKILLS + AGENTS:
            with open(path, encoding="utf-8") as handle:
                for number, line in enumerate(handle, 1):
                    if pattern.search(line):
                        offending.append(f"{os.path.relpath(path, ROOT)}:{number}: {line.strip()}")
        self.assertEqual(offending, [])

    def test_cv_create_description_is_short(self):
        # audit finding: the cv-create description states purpose, triggers and limits in at most 500 characters
        path = os.path.join(ROOT, "skills", "job-application-cv-create", "SKILL.md")
        header, _ = frontmatter(path)
        description = re.search(r'^description: "(.*)"$', header, re.M).group(1)
        self.assertLessEqual(len(description), 500, len(description))

    def test_cross_references_name_existing_skills(self):
        known = names_of_skills_and_agents()
        unknown = []
        for path in SKILLS + AGENTS:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for ref in set(re.findall(r"job-application-[a-z-]+|job-application-reviewer", text)):
                if ref not in known:
                    unknown.append(f"{os.path.relpath(path, ROOT)} -> {ref}")
        self.assertEqual(unknown, [])

    def test_no_dangling_decision_ids(self):
        # audit finding: short decision IDs (D3, D14, ...) were defined in no spec; skills cite rule IDs instead
        pattern = re.compile(r"\bD[0-9]{1,2}\b")
        offending = []
        for path in SKILLS + AGENTS:
            with open(path, encoding="utf-8") as handle:
                for number, line in enumerate(handle, 1):
                    if pattern.search(line):
                        offending.append(f"{os.path.relpath(path, ROOT)}:{number}")
        self.assertEqual(offending, [])

    def test_cited_rules_exist_in_the_specs(self):
        # every cited rule ID names a section `## <PREFIX>-<n>` of its spec; a cited sub-rule `<PREFIX>-<n>.<m>` needs a
        # heading of that name, a numbered item `m.` in the section, or a table row / literal mention in the spec
        families = {
            "R": "konventionen", "CG": "cv-generierung", "LB": "lebenslauf", "LV": "lebenslauf-versionen",
            "LS": "lokale-struktur", "AS": "anschreiben", "MS": "motivationsschreiben",
            "KK": "kontaktklassifikation", "UA": "unternehmensanalyse", "WJ": "traumjob-interview",
            "RC": "recherche",
        }
        specs = {}
        for prefix, folder in families.items():
            with open(os.path.join(ROOT, "spec", "job-application", folder, "en.md"), encoding="utf-8") as handle:
                specs[prefix] = handle.read()

        def section(prefix, number):
            text = specs[prefix]
            start = re.search(rf"^## {prefix}-{number}\b", text, re.M)
            if not start:
                return None
            end = re.search(r"^## ", text[start.end():], re.M)
            return text[start.start():start.end() + end.start()] if end else text[start.start():]

        def sub_rule_exists(prefix, number, sub):
            body = section(prefix, number)
            full = f"{prefix}-{number}.{sub}"
            if re.search(rf"(?<![\w.-]){re.escape(full)}(?![\w-]|\.\d)", specs[prefix]):
                return True
            items = {int(n) for n in re.findall(r"^\s*(\d+)\. ", body, re.M)}
            items |= {int(n) for n in re.findall(r"^\| ?(\d+) ?\|", body, re.M)}
            items |= {int(n) for n in re.findall(rf"^#{{3,4}} {prefix}-{number}\.(\d+)\b", body, re.M)}
            return int(sub) in items

        pattern = re.compile(r"\b(R|CG|LB|LV|LS|AS|MS|KK|UA|WJ|RC)-(\d+)(?:\.(\d+))?")
        missing = []
        for path in SKILLS + AGENTS:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for prefix, number, sub in set(pattern.findall(text)):
                where = os.path.relpath(path, ROOT)
                if section(prefix, number) is None:
                    missing.append(f"{where} -> {prefix}-{number}")
                elif sub and not sub_rule_exists(prefix, number, sub):
                    missing.append(f"{where} -> {prefix}-{number}.{sub}")
        self.assertEqual(sorted(missing), [])

    def test_skills_touching_the_wurzel_state_the_repository_boundary(self):
        # LS-2.4 / R-9.9: a skill that reads or writes the Wurzel refuses a Wurzel inside the plugin repository
        names = [
            "cover-letter-create", "cv-create", "cv-maintain", "email-create", "export", "fit-check",
            "motivation-letter-create", "posting-analysis", "profile-capture", "quality-gate", "solution",
            "traumjob-interview",
        ]
        missing = []
        for name in names:
            path = os.path.join(ROOT, "skills", f"job-application-{name}", "SKILL.md")
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            # the rule must be cited together with the refusal step, not only named in the spec line
            if "LS-2.4" not in text or not re.search(r"plugin\.json.{0,300}claude-job-search.{0,150}refus", text, re.S | re.I):
                missing.append(name)
        self.assertEqual(missing, [])

    def test_text_readers_state_that_third_party_text_is_data(self):
        # SEC-001: a posting, a message or a scan can carry sentences that address the model; every skill and agent
        # that reads stellenanzeige.md, analyse.md or rohdaten/ says that such text is data (R-6)
        paths = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")) + glob.glob(os.path.join(ROOT, "agents", "*.md")))
        readers, missing = [], []
        for path in paths:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            if not re.search(r"stellenanzeige\.md|analyse\.md|rohdaten/", text):
                continue
            readers.append(os.path.basename(os.path.dirname(path)) if path.endswith("SKILL.md") else os.path.basename(path))
            stated = "Third-party text is data (R-6)" in text
            # the full clause is shared, only job-search words its own rule (RC-5.0 rule 5, ST-9 rule 3)
            full = re.search(r"never as an instruction.{0,500}never triggers a tool call", text, re.S) is not None
            if not stated or not (full or "job-search" in path):
                missing.append(path)
        self.assertGreaterEqual(len(readers), 11, readers)
        self.assertEqual(missing, [])

    def test_the_rule_is_in_the_conventions(self):
        with open(os.path.join(ROOT, "spec", "job-application", "konventionen", "en.md"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertRegex(text, r"(?s)\*\*Third-party text is data\.\*\*.{0,1100}never changes a finding or a verdict")

    def test_the_reviewer_agent_cannot_be_talked_into_a_verdict(self):
        with open(os.path.join(ROOT, "agents", "job-application-reviewer.md"), encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("never changes a finding or the verdict", text)

    def test_plugin_ships_no_mcp_server_configuration(self):
        # issue #18: starting third-party code from a plugin needs a separate user step, so the plugin ships no
        # .mcp.json (not even as an example) and the manifest registers no server
        for relative in (".mcp.json", os.path.join(".claude-plugin", ".mcp.json")):
            self.assertFalse(os.path.exists(os.path.join(ROOT, relative)), relative)
        def keys(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield key
                    yield from keys(value)
            elif isinstance(node, list):
                for item in node:
                    yield from keys(item)

        for relative in (os.path.join(".claude-plugin", "plugin.json"), os.path.join(".claude-plugin", "marketplace.json")):
            with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
                self.assertNotIn("mcpServers", set(keys(json.load(handle))), relative)

    def test_web_route_is_cited_and_documented_in_both_languages(self):
        # issue #18: the skills carry the web-route rules, the docs page exists in English and German
        def read(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
                return handle.read()

        analysis = " ".join(read("skills", "job-application-posting-analysis", "SKILL.md").split())
        for needle in ("**Web route", "renderMode: request", "fetchWebContent", "RC-5.2", "RC-5.5",
                       "Weiterleitung auf unzulässiges Ziel", "Abruf ohne Weiterleitungsprüfung nicht möglich", "`### Suchen`", "Websuche über open-webSearch"):
            self.assertIn(needle, analysis, needle)
        fit_check = read("skills", "job-application-fit-check", "SKILL.md")
        for needle in ("RC-5.2", "RC-5.5", "Stay local"):
            self.assertIn(needle, fit_check, needle)
        gate = read("skills", "job-application-quality-gate", "SKILL.md")
        for needle in ("### Suchen", "allowlist", "RC-5.5 rule 6"):
            self.assertIn(needle, gate, needle)
        reason = "Abruf ohne Weiterleitungsprüfung nicht möglich"
        self.assertIn(reason, " ".join(read("spec", "job-application", "recherche", "en.md").split()))
        self.assertIn(reason, " ".join(read("skills", "job-application-posting-analysis", "SKILL.md").split()))
        self.assertIn("RC-5.2 rules 8 and 9", " ".join(read("spec", "job-application", "recherche", "en.md").split()))
        for lang in ("en", "de"):
            page = read("docs", lang, "websearch.md")
            self.assertIn("open-websearch@", page, lang)
            self.assertNotIn('@latest"', page, lang)

    def test_web_route_budget_is_the_same_in_spec_skill_and_docs(self):
        # the budget numbers (10/15 at level 1, 20/30 at level 2) live in the spec, the skill, the gate and the docs; they
        # must not drift apart. The gate carries them so that it works without the spec loaded.
        def read(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
                return handle.read()

        def flat(*parts):
            return " ".join(read(*parts).split())

        for label, text in (("spec", flat("spec", "job-application", "recherche", "en.md")),
                            ("skill", flat("skills", "job-application-posting-analysis", "SKILL.md")),
                            ("gate", flat("skills", "job-application-quality-gate", "SKILL.md"))):
            self.assertRegex(text, r"10 searches and 15 page fetches", label)
            self.assertRegex(text, r"20 and 30", label)
        for lang, word in (("en", "at most"), ("de", "höchstens")):
            page = read("docs", lang, "websearch.md")
            for level, searches, fetches in ((1, 10, 15), (2, 20, 30)):
                self.assertRegex(page, rf"\| {level} \| {word} {searches} \| {word} {fetches} \|", f"{lang} level {level}")


    def test_register_route_is_cited_and_documented_in_both_languages(self):
        # issue #16: the Handelsregister route lives in the spec, the two skills and the docs page in both languages
        def flat(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
                return " ".join(handle.read().split())

        spec = flat("spec", "job-application", "recherche", "en.md")
        analysis = flat("skills", "job-application-posting-analysis", "SKILL.md")
        gate = flat("skills", "job-application-quality-gate", "SKILL.md")
        for label, text in (("spec", spec), ("skill", analysis)):
            for needle in ("handelsregister-mcp", "RC-5.3", "search_company", "get_company", "rate_limit_status"):
                self.assertIn(needle, text, f"{label}: {needle}")
        for needle in ("RC-5.3 rule 4", "RC-5.3 rule 5", "RC-9 rule 8", "RC-11 rule 4", "RC-11 rule 5", "CV-18", "--firma"):
            self.assertIn(needle, gate, needle)
        # singular form: `1 Abruf`, otherwise `n Abrufe`, in spec, skill, gate and docs
        for label, text in (("spec", spec), ("skill", analysis), ("gate", gate),
                            ("docs en", flat("docs", "en", "handelsregister.md")), ("docs de", flat("docs", "de", "handelsregister.md"))):
            self.assertRegex(text, r"1 Abruf[`)]", label)
        for label, text in (("spec", spec), ("skill", analysis)):
            self.assertIn("handelsregister-mcp (n Abruf|Abrufe)", text, label)
        self.assertIn("handelsregister-mcp (1 Abruf)", gate)
        self.assertIn("falls below the count of an earlier record", spec)
        self.assertIn("falls below the count of an earlier record", gate)
        self.assertNotIn("register lookup with a fee", analysis)
        for rule in ("4. **Birthdate from the register.**", "5. **Register entry in `Kanäle`.**"):
            self.assertIn(rule, spec, rule)
        for lang, rule in (("en", "RC-9 rule 8"), ("de", "RC-9 Regel 8")):
            page = flat("docs", lang, "handelsregister.md")
            for needle in ("lexdoudkin/handelsregister-mcp", rule, "RC-5.3", "handelsregister-mcp (2 Abrufe)"):
                self.assertIn(needle, page, f"{lang}: {needle}")

    def test_register_budget_is_the_same_in_spec_skill_and_docs(self):
        # 4 retrievals at level 1, 8 at level 2, shared by both levels
        def flat(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
                return " ".join(handle.read().split())

        self.assertRegex(flat("spec", "job-application", "recherche", "en.md"), r"At most 4 retrievals \(tool calls except `rate_limit_status`\) per Vorgang at level 1 and at most 8 at level 2")
        self.assertRegex(flat("skills", "job-application-posting-analysis", "SKILL.md"), r"shared by levels 1 and 2: at most 4 retrievals")
        self.assertRegex(flat("skills", "job-application-posting-analysis", "SKILL.md"), r"at most 4 retrievals.{0,80}at level 1, 8 in total at level 2")
        self.assertRegex(flat("skills", "job-application-quality-gate", "SKILL.md"), r"4 at level 1, 8 at level 2, shared by both levels")
        self.assertRegex(flat("docs", "en", "handelsregister.md"), r"At most 4 retrievals per Vorgang at research level 1 and at most 8 at level 2")
        self.assertRegex(flat("docs", "de", "handelsregister.md"), r"Höchstens 4 Abrufe pro Vorgang in Recherchestufe 1 und höchstens 8 in Stufe 2")

    def test_register_server_commit_pin_is_the_same_in_both_docs_languages(self):
        pins = {}
        for lang in ("en", "de"):
            with open(os.path.join(ROOT, "docs", lang, "handelsregister.md"), encoding="utf-8") as handle:
                text = handle.read()
            found = set(re.findall(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", text))
            self.assertEqual(len(found), 1, f"{lang}: {found}")
            pins[lang] = found
        self.assertEqual(pins["en"], pins["de"])

    def test_register_docs_page_is_in_the_mkdocs_nav(self):
        with open(os.path.join(ROOT, "mkdocs.yml"), encoding="utf-8") as handle:
            self.assertRegex(handle.read(), r"-\s*Handelsregister:\s*en/handelsregister\.md")
        for lang in ("en", "de"):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "docs", lang, "handelsregister.md")), lang)

    def test_mcp_overview_is_in_nav_and_every_server_page_links_back(self):
        # issue #19: one overview page for the optional MCP servers, linked from the nav, the indexes and the README;
        # every detail page links back to it
        def read(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
                return handle.read()

        # the overview is the first entry of the section; the server pages are its sub-items
        self.assertRegex(read("mkdocs.yml"), r"-\s*Optional MCP servers:\s*-\s*Overview:\s*en/mcp-servers\.md")
        for page in ("linkedin", "handelsregister", "websearch", "jobspy", "browser"):
            self.assertRegex(read("mkdocs.yml"), rf"\n      - [^\n]+: en/{page}\.md")
        self.assertIn("Optional MCP servers: Optionale MCP-Server", read("mkdocs.yml"))
        for lang in ("en", "de"):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "docs", lang, "mcp-servers.md")), lang)
            self.assertIn("mcp-servers.md", read("docs", lang, "index.md"), f"{lang} index")
            for page in ("linkedin.md", "handelsregister.md", "websearch.md"):
                self.assertIn("mcp-servers.md", read("docs", lang, page), f"{lang} {page}")
        self.assertIn("/mcp-servers/", read("README.md"))
        # the overview carries the same RC-5.0 citations and the same budget numbers in both languages, and the
        # LinkedIn page names its own budget (6 and 15), which the spec states in RC-5.4 rule 3
        cites = {lang: sorted(set(re.findall(r"RC-5\.0 (?:rule|Regel) (\d)", read("docs", lang, "mcp-servers.md"))))
                 for lang in ("en", "de")}
        self.assertEqual(cites["en"], cites["de"])
        self.assertEqual(cites["en"], [str(n) for n in range(1, 9)])
        for lang, word in (("en", "At most 6 page reads"), ("de", "Höchstens 6 Seitenabrufe")):
            self.assertIn(word, read("docs", lang, "linkedin.md"), lang)

    def test_job_search_skill_follows_the_stellensuche_spec(self):
        # issue #17: the skill cites existing ST rules and scenarios, shows the brief first, keeps LinkedIn out of JobSpy,
        # sets no proxy and keeps Ausschluss text out of the brief
        def read(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
                return handle.read()

        spec = read("spec", "job-application", "stellensuche", "en.md")
        skill = read("skills", "job-application-job-search", "SKILL.md")
        flat = " ".join(skill.split())
        rules = set(re.findall(r"^## (ST-\d+) ", spec, re.MULTILINE))
        scenarios = set(re.findall(r"^\| (SS-[A-Z]) \|", spec, re.MULTILINE))
        cited_rules = {f"ST-{n}" for n in re.findall(r"\bST-(\d+)", skill)}
        cited_scenarios = set(re.findall(r"\bSS-[A-Z]\b", skill))
        self.assertTrue(cited_rules and cited_scenarios)
        self.assertEqual(sorted(cited_rules - rules), [])
        self.assertEqual(sorted(cited_scenarios - scenarios), [])
        # the scenarios that need behaviour of their own in the skill are cited by it, not only defined in the spec
        for scenario in ("SS-B", "SS-D", "SS-E", "SS-J", "SS-N", "SS-P", "SS-Q", "SS-R", "SS-S", "SS-U"):
            self.assertIn(scenario, cited_scenarios, scenario)
        for needle in ("No query before the yes", "Never `linkedin` through JobSpy", "Set no proxy", "Ausschluss reason",
                       "RC-5.8", "WJ-8.2", "Never delete"):
            self.assertIn(needle, flat, needle)
        # the scenario that checks the brief names the Ausschluss and states that the brief does not contain it
        self.assertRegex(spec, r"\| SS-A \|[^\n]*Ausschluss[^\n]*neither the Ausschluss")
        # the skill never passes `linkedin` as a board and names no proxy setting
        self.assertNotRegex(skill, r"HTTPS_PROXY|proxies\s*=")

    def test_search_records_have_a_place_and_a_retention_in_the_local_structure(self):
        with open(os.path.join(ROOT, "spec", "job-application", "lokale-struktur", "en.md"), encoding="utf-8") as handle:
            text = " ".join(handle.read().split())
        for needle in ("suche/", "deleted 90 days after its date", "`übernommen`", "`abgelehnt`", "`offen`",
                       "not a Vorgang"):
            self.assertIn(needle, text, needle)

    def test_jobspy_docs_page_is_in_nav_in_both_languages_and_pins_the_same_version(self):
        def read(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
                return handle.read()

        self.assertRegex(read("mkdocs.yml"), r"-\s*JobSpy:\s*en/jobspy\.md")
        versions = {}
        for lang in ("en", "de"):
            page = read("docs", lang, "jobspy.md")
            self.assertIn("claude mcp add jobspy -- uvx mcp-jobspy@latest", page, lang)
            self.assertIn("mcp-servers.md", page, lang)
            self.assertNotRegex(page, r"HTTPS_PROXY", lang)
            versions[lang] = set(re.findall(r"1\.4\.1", page))
            overview = read("docs", lang, "mcp-servers.md")
            self.assertIn("jobspy.md", overview, lang)
            self.assertNotIn("Planned", overview, lang)
        self.assertEqual(versions["en"], versions["de"])
        self.assertTrue(versions["en"])

    def test_common_channel_rules_are_stated_once_in_the_research_spec(self):
        # issue #19: RC-5.0 carries the rules of all optional network channels; RC-5.2 to RC-5.5 refer to them
        with open(os.path.join(ROOT, "spec", "job-application", "recherche", "en.md"), encoding="utf-8") as handle:
            spec = handle.read()
        self.assertIn("### RC-5.0 Rules for optional network channels", spec)
        block = spec.split("### RC-5.0", 1)[1].split("### RC-5.1", 1)[0]
        self.assertEqual(re.findall(r"^(\d+)\. \*\*", block, re.MULTILINE), [str(n) for n in range(1, 9)])
        for number in ("5.2", "5.3", "5.4", "5.5"):
            section = spec.split(f"### RC-{number} ", 1)[1].split("\n### ", 1)[0]
            self.assertIn("RC-5.0 rule", section, f"RC-{number}")

    def test_release_workflow_aligns_the_manifests_and_no_pr_bumps_the_version(self):
        # the tag comes from release-drafter; the manifests are set to it by the `chore(release): <tag>` commit of
        # release-publish.yml (auto-align), never by a feature PR (claude-shared spec release-automation)
        def read(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
                return handle.read()

        self.assertRegex(read(".github", "workflows", "release-publish.yml"), r"(?m)^\s+auto-align:\s*true\s*$")
        guide = " ".join(read("CLAUDE.md").split())
        self.assertIn("No version bumps in PRs", guide)
        self.assertNotIn("Version bump on every user-visible change", guide)


if __name__ == "__main__":
    unittest.main()
