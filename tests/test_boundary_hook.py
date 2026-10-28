"""The PreToolUse hook that refuses a write into a Wurzel inside the plugin repository (LS-2.4, R-9.9).

Runs scripts/boundary_hook.py as Claude Code does: hook JSON on stdin, exit 2 blocks. The plugin repository
is a temporary directory with the manifest, never this checkout.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "scripts", "boundary_hook.py")


def run_hook(payload):
    data = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, HOOK], input=data, capture_output=True, text=True)


def write(path, text=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


class BoundaryHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.plugin = os.path.join(self.tmp.name, "plugin")
        write(os.path.join(self.plugin, ".claude-plugin", "plugin.json"), json.dumps({"name": "job-application"}))
        self.outside = os.path.join(self.tmp.name, "daten")
        os.makedirs(self.outside)

    def tearDown(self):
        self.tmp.cleanup()

    def anker(self, cwd, **keys):
        lines = "\n".join(f"{key}: {value}" for key, value in keys.items())
        write(os.path.join(cwd, "job-application", "konfiguration.md"), f"---\n{lines}\n---\n")

    def event(self, cwd, path, tool="Write"):
        return {"cwd": cwd, "tool_name": tool, "tool_input": {"file_path": path}}

    def test_without_anker_every_write_passes(self):
        result = run_hook(self.event(self.plugin, "job-application/acme/lebenslauf.md"))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_wurzel_inside_the_plugin_repository_is_refused(self):
        self.anker(self.plugin, wurzel="job-application")
        result = run_hook(self.event(self.plugin, "job-application/acme/lebenslauf.md"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("LS-2.4", result.stderr)
        self.assertIn("job-application/konfiguration.md", result.stderr)

    def test_wurzel_outside_the_plugin_repository_passes(self):
        self.anker(self.plugin, wurzel=self.outside)
        result = run_hook(self.event(self.plugin, os.path.join(self.outside, "acme", "lebenslauf.md")))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_write_outside_the_wurzel_is_not_the_hooks_business(self):
        # the Wurzel is wrong, but the write goes elsewhere (the model edits a skill of the checkout)
        self.anker(self.plugin, wurzel="job-application")
        result = run_hook(self.event(self.plugin, "skills/x/SKILL.md"))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_grundlage_inside_the_plugin_repository_is_refused_even_with_a_wurzel_outside(self):
        grundlage = os.path.join(self.plugin, "notizen", "lebenslauf-chronologisch.md")
        self.anker(self.plugin, wurzel=self.outside, grundlage=grundlage)
        result = run_hook(self.event(self.plugin, grundlage, tool="Edit"))
        self.assertEqual(result.returncode, 2)
        write(os.path.join(self.outside, "acme", "x.md"))
        result = run_hook(self.event(self.plugin, os.path.join(self.outside, "acme", "x.md")))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_notebook_path_is_checked_too(self):
        self.anker(self.plugin, wurzel="job-application")
        event = {"cwd": self.plugin, "tool_name": "NotebookEdit", "tool_input": {"notebook_path": "job-application/a.ipynb"}}
        self.assertEqual(run_hook(event).returncode, 2)

    def test_unreadable_input_lets_the_call_pass(self):
        self.assertEqual(run_hook("not json").returncode, 0)
        self.assertEqual(run_hook({"cwd": self.plugin, "tool_input": {}}).returncode, 0)

    def test_hooks_json_wires_the_script_for_the_file_tools(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as handle:
            hooks = json.load(handle)
        entries = hooks["hooks"]["PreToolUse"]
        self.assertEqual(len(entries), 1)
        for tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
            self.assertIn(tool, entries[0]["matcher"].split("|"))
        command = entries[0]["hooks"][0]["command"]
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/boundary_hook.py", command)


if __name__ == "__main__":
    unittest.main()
