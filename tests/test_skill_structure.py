"""Structural checks of skills, agents and cross-references (tests/README.md, planned checks).

Verifies that every skill folder matches its frontmatter name, that referenced spec and
requirement files and helper scripts exist, and that see_also and dont_use alternatives name
an existing skill or agent.
"""

import glob
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

    def test_cited_rule_families_exist_in_the_specs(self):
        # every cited rule ID (AS-7, CG-13.2, ...) names a top-level section `## <PREFIX>-<n>` of its spec
        families = {
            "R": "konventionen", "CG": "cv-generierung", "LB": "lebenslauf", "LV": "lebenslauf-versionen",
            "LS": "lokale-struktur", "AS": "anschreiben", "MS": "motivationsschreiben",
            "KK": "kontaktklassifikation", "UA": "unternehmensanalyse", "WJ": "traumjob-interview",
            "RC": "recherche",
        }
        sections = {}
        for prefix, folder in families.items():
            spec = os.path.join(ROOT, "spec", "job-application", folder, "en.md")
            with open(spec, encoding="utf-8") as handle:
                sections[prefix] = set(re.findall(rf"^#{{2,3}} {prefix}-(\d+)\b", handle.read(), re.M))
        pattern = re.compile(r"\b(R|CG|LB|LV|LS|AS|MS|KK|UA|WJ|RC)-(\d+)(?:\.\d+)*")
        missing = []
        for path in SKILLS + AGENTS:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for prefix, number in set(pattern.findall(text)):
                if number not in sections[prefix]:
                    missing.append(f"{os.path.relpath(path, ROOT)} -> {prefix}-{number}")
        self.assertEqual(missing, [])

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
            if "LS-2.4" not in text:
                missing.append(name)
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
