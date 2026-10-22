"""Structural checks of the spec corpus: every spec is indexed and every cross-reference resolves."""

import glob
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS = sorted(glob.glob(os.path.join(ROOT, "spec", "job-application", "*", "en.md")))


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class SpecIndexTests(unittest.TestCase):
    def test_specs_exist(self):
        self.assertTrue(SPECS)

    def test_every_spec_is_listed_in_the_index(self):
        index = read(os.path.join(ROOT, "spec", "README.md"))
        missing = [os.path.relpath(p, ROOT) for p in SPECS if os.path.relpath(p, ROOT) not in index]
        self.assertEqual(missing, [])

    def test_cross_references_between_specs_resolve(self):
        broken = []
        for path in SPECS:
            text = read(path)
            for ref in set(re.findall(r"spec/job-application/[a-z-]+/en\.md", text)):
                if not os.path.isfile(os.path.join(ROOT, ref)):
                    broken.append(f"{os.path.relpath(path, ROOT)} -> {ref}")
            for topic in set(re.findall(r"`([a-z-]+)/en\.md`", text)):
                if not os.path.isfile(os.path.join(ROOT, "spec", "job-application", topic, "en.md")):
                    broken.append(f"{os.path.relpath(path, ROOT)} -> {topic}/en.md")
        self.assertEqual(broken, [])

    def test_document_type_specs_have_sources_and_open_points(self):
        for topic in ("lebenslauf", "anschreiben", "motivationsschreiben"):
            text = read(os.path.join(ROOT, "spec", "job-application", topic, "en.md"))
            self.assertRegex(text, r"## [A-Z]{2}-\d+ Sources", topic)
            self.assertRegex(text, r"## [A-Z]{2}-\d+ Open points", topic)
            self.assertRegex(text, r"## [A-Z]{2}-\d+ Acceptance scenarios", topic)


if __name__ == "__main__":
    unittest.main()
