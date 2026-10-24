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
        self.assertGreaterEqual(len(CASES), 19)
        for case in CASES:
            graders = glob.glob(os.path.join(case, "graders", "*.md"))
            self.assertTrue(graders, f"{case}: a case without a grader does not load")
            prompt = read(os.path.join(case, "prompt.md"))
            self.assertRegex(prompt, r'(?m)^plugins: \["\.\./\.\."\]$', case)
            self.assertRegex(prompt, r"(?m)^tags: \[(trigger|behavior)", case)
            for grader in graders:
                self.assertRegex(read(grader), r"(?m)^type: (regex|tool_used|tool_order|file_exists|llm|baseline)$", grader)

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
