"""Structure of the eval suite under evals/ (docs/en/evals.md). Free: no model is called.

Verifies that every skill and the reviewer agent have a trigger case, that every case has a prompt and a grader, that the
scaffold scripts are executable and use no tool from HOME (a scaffold runs with a replaced HOME), that the suite holds only
fictional data, and that the documentation exists in both languages.
"""

import glob
import os
import re
import stat
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVALS = os.path.join(ROOT, "evals")
CASES = sorted(os.path.dirname(p) for p in glob.glob(os.path.join(EVALS, "*", "prompt.md")))


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class EvalSuiteTests(unittest.TestCase):
    def test_every_skill_and_the_reviewer_have_a_trigger_case(self):
        names = {os.path.basename(c) for c in CASES}
        skills = [os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md"))]
        missing = [s for s in skills if "trigger-" + s.replace("job-application-", "") not in names]
        self.assertEqual(missing, [])
        self.assertIn("trigger-reviewer", names)

    def test_every_case_has_a_prompt_a_grader_and_the_plugin(self):
        self.assertGreaterEqual(len(CASES), 21)
        for case in CASES:
            graders = glob.glob(os.path.join(case, "graders", "*.md"))
            self.assertTrue(graders, f"{case}: a case without a grader does not load")
            prompt = read(os.path.join(case, "prompt.md"))
            self.assertRegex(prompt, r'(?m)^plugins: \["\.\./\.\."\]$', case)
            self.assertRegex(prompt, r"(?m)^tags: \[(trigger|behavior|precondition)", case)
            for grader in graders:
                self.assertRegex(read(grader), r"(?m)^type: (regex|tool_used|tool_order|file_exists|llm|baseline)$", grader)

    PROMPT_KEYS = {"name", "description", "tags", "plugins", "runs", "model", "max_turns", "timeout_seconds", "allowed_tools",
                   "append_system_prompt", "env", "expected_outcome"}

    def test_prompt_frontmatter_uses_only_documented_keys_and_enough_turns(self):
        # unknown keys are an error of the tool (docs/en/evals.md); a trigger run needs about five turns
        for case in CASES:
            head = read(os.path.join(case, "prompt.md")).split("---")[1]
            keys = set(re.findall(r"(?m)^([a-z_]+):", head))
            self.assertLessEqual(keys, self.PROMPT_KEYS, case)
            turns = int(re.search(r"(?m)^max_turns: (\d+)$", head).group(1))
            if os.path.basename(case).startswith("trigger-"):
                self.assertGreaterEqual(turns, 6, case)

    def test_regex_flags_are_known_and_every_negative_grader_has_a_positive_guard(self):
        # a "must not" grader passes when the run fails early; a positive grader in the same case proves that the thing happened
        for case in CASES:
            graders = {g: read(g) for g in glob.glob(os.path.join(case, "graders", "*.md"))}
            for path, text in graders.items():
                flags = re.search(r"(?m)^flags: (\w+)$", text)
                if flags:
                    self.assertRegex(flags.group(1), r"^[ism]+$", path)
                    self.assertNotIn("m", flags.group(1), f"{path}: the documentation names only the flags i and s")
            negative = [p for p, t in graders.items() if re.search(r"(?m)^(match: not_contains|exists: false|max: 0)$", t)]
            if negative:
                positive = [p for p, t in graders.items() if p not in negative]
                self.assertTrue(positive, f"{case}: only negative graders; a failed run would pass")

    @staticmethod
    def frontmatter_files():
        return (glob.glob(os.path.join(EVALS, "*", "prompt.md")) + glob.glob(os.path.join(EVALS, "*", "graders", "*.md"))
                + glob.glob(os.path.join(EVALS, "*", "case.yaml")))

    def test_frontmatter_is_valid_yaml_for_plain_scalars(self):
        # found by the first run of the committed suite: `description: ... graded: a gate ...` is invalid YAML (a ": " inside
        # a plain scalar) and the whole case failed to load. The suite is stdlib-only, so this checks the rules that bit;
        # test_frontmatter_parses_with_pyyaml parses for real where PyYAML is installed.
        for path in self.frontmatter_files():
            text = read(path)
            head = text if path.endswith(".yaml") else text.split("---")[1]
            for number, line in enumerate(head.splitlines(), 1):
                match = re.match(r"^([A-Za-z_][\w-]*):[ ]+(.*)$", line)
                if not match:
                    continue
                value = match.group(2).strip()
                where = f"{path}:{number}"
                self.assertNotIn("\t", line, where)
                if value[:1] in ("'", '"'):
                    self.assertEqual(value[-1], value[0], f"{where}: a quoted value must close with the same quote")
                    continue
                if not value or value[0] in "[{|>&*!%@`":
                    continue
                self.assertNotIn(": ", value, f"{where}: a plain YAML scalar must not contain ': ' (quote it)")
                self.assertNotIn(" #", value, f"{where}: a plain YAML scalar must not contain ' #'")
                self.assertFalse(value.endswith(":"), f"{where}: a plain YAML scalar must not end with ':'")

    def test_frontmatter_parses_with_pyyaml(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML is not installed (the repository .venv of the docs build has it)")
        for path in self.frontmatter_files():
            text = read(path)
            head = text if path.endswith(".yaml") else text.split("---")[1]
            self.assertIsInstance(yaml.safe_load(head), dict, path)

    def test_trigger_cases_check_the_skill_they_are_named_after(self):
        for case in CASES:
            name = os.path.basename(case)
            if not name.startswith("trigger-"):
                continue
            target = "reviewer" if name == "trigger-reviewer" else name.replace("trigger-", "")
            text = "\n".join(read(g) for g in glob.glob(os.path.join(case, "graders", "*.md")))
            self.assertIn(f"job-application-{target}", text, name)

    def test_scaffold_scripts_are_executable_and_avoid_the_users_home(self):
        scripts = glob.glob(os.path.join(EVALS, "*", "*.sh")) + glob.glob(os.path.join(EVALS, "_lib", "*.sh")) + [os.path.join(EVALS, "run.sh")]
        self.assertGreaterEqual(len(scripts), 7)
        for script in scripts:
            self.assertTrue(os.stat(script).st_mode & stat.S_IXUSR, f"{script} is not executable (a scaffold exits with 126)")
            if os.path.basename(script) in ("run.sh",):
                continue
            body = "\n".join(line for line in read(script).splitlines() if not line.lstrip().startswith("#"))
            self.assertNotRegex(body, r"(?m)(^\s*|[|;&(`]\s*|\$\(\s*)(python3?|pip|node|npm|ruby|asdf|pyenv)\b", f"{script}: the scaffold runs with a replaced HOME")
            self.assertNotRegex(body, r"/home/|/Users/", script)

    def test_every_scaffold_script_is_named_in_its_case(self):
        for script in glob.glob(os.path.join(EVALS, "*", "fixture.sh")):
            case_yaml = read(os.path.join(os.path.dirname(script), "case.yaml"))
            self.assertIn("scaffold_script: fixture.sh", case_yaml, script)

    def test_runner_never_publishes_and_caps_the_cost(self):
        runner = read(os.path.join(EVALS, "run.sh"))
        self.assertIn("--no-publish", runner)
        self.assertIn("--max-cost-usd", runner)
        self.assertRegex(runner, r'MAX_COST_USD="\$\{MAX_COST_USD:-\d+\}"')

    def test_results_are_ignored_and_the_pages_exist_in_both_languages(self):
        self.assertIn("evals/results/", read(os.path.join(ROOT, ".gitignore")))
        for lang in ("en", "de"):
            page = read(os.path.join(ROOT, "docs", lang, "evals.md"))
            self.assertIn("evals/run.sh", page)
            self.assertIn("--no-publish", page)
        self.assertIn("en/evals.md", read(os.path.join(ROOT, "mkdocs.yml")))
        self.assertIn("Evaluating the plugin: Das Plugin evaluieren", read(os.path.join(ROOT, "mkdocs.yml")))

    def test_the_suite_holds_no_real_looking_personal_data(self):
        for path in glob.glob(os.path.join(EVALS, "**", "*"), recursive=True):
            if not os.path.isfile(path) or "/results/" in path:
                continue
            text = read(path)
            self.assertNotRegex(text, r"[A-Za-z0-9._-]+@(?!example\.test)[A-Za-z0-9-]+\.[a-z]{2,}", path)
            self.assertNotRegex(text, r"\+?\d{3,}[ /-]\d{5,}", path)


if __name__ == "__main__":
    unittest.main()
