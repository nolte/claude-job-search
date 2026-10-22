"""Export tests for skills/job-application-export/scripts/export_document.py (spec CG-12).

Uses a synthetic Lebenslauf. Requires pandoc for md/html/docx and python-docx for the DOCX
structure check. The PDF export needs LuaLaTeX; without it the PDF test is skipped and the
skip reason is printed, so the result is not reported as passed.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTER = os.path.join(ROOT, "skills", "job-application-export", "scripts", "export_document.py")

SOURCE = """\
---
grundlage_hash: 0000000000000000000000000000000000000000000000000000000000000000
format: chronologisch
---

# Lebenslauf

## Persönliche Daten
Max Mustermann · Musterstraße 1 · 00000 Musterstadt

## Berufserfahrung

### 04/2021 – heute | Senior Backend-Entwickler | Musterfirma GmbH, Berlin
- Betreuung der Event-Pipeline in Python und Kafka; Latenz von 800 ms auf 120 ms gesenkt.
- Einführung von Code-Reviews im Team mit fünf Entwicklern.

## Sprachkenntnisse (GER-Niveau)
- Deutsch: Muttersprache

Ort, Datum
"""

HEADINGS = ["Persönliche Daten", "Berufserfahrung", "Sprachkenntnisse (GER-Niveau)"]


def have(tool):
    return shutil.which(tool) is not None


def python_docx_available():
    try:
        import docx  # noqa: F401
    except ImportError:
        return False
    return True


@unittest.skipUnless(have("pandoc"), "pandoc is not installed")
class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.source = os.path.join(self.tmp, "lebenslauf.md")
        with open(self.source, "w", encoding="utf-8") as handle:
            handle.write(SOURCE)
        self.out = os.path.join(self.tmp, "out")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def export(self, fmt):
        result = subprocess.run(
            [sys.executable, EXPORTER, self.source, "--format", fmt, "--doc-type", "cv", "--out-dir", self.out, "--name", "Test_Lebenslauf"],
            capture_output=True,
            text=True,
        )
        return result

    def test_markdown_export_keeps_content(self):
        # Scenario J: export is a copy of the approved content
        result = self.export("md")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = os.path.join(self.out, "Test_Lebenslauf.md")
        with open(output, encoding="utf-8") as handle:
            text = handle.read()
        for line in SOURCE.splitlines():
            if line.startswith("- "):
                self.assertIn(line[2:], text)

    def test_html_export_passes_content_check(self):
        result = self.export("html")
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.out, "Test_Lebenslauf.html"), encoding="utf-8") as handle:
            self.assertIn("Latenz von 800 ms", handle.read())

    def test_motivation_doc_type_is_accepted_with_a_two_page_limit(self):
        # MS-7: the Motivationsschreiben has its own document type; pandoc only, no LuaLaTeX
        sys.path.insert(0, os.path.dirname(EXPORTER))
        import export_document

        self.assertEqual(export_document.PAGE_LIMITS["motivation"], 2)
        result = subprocess.run(
            [sys.executable, EXPORTER, self.source, "--format", "tex", "--doc-type", "motivation", "--out-dir", self.out, "--name", "Test_Motivation"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_tex_export_writes_source_without_lualatex(self):
        # tex is the LaTeX source of the PDF; it needs pandoc only and passes the content check
        result = self.export("tex")
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.out, "Test_Lebenslauf.tex"), encoding="utf-8") as handle:
            tex = handle.read()
        self.assertIn("\\begin{document}", tex)
        self.assertIn("Latenz von 800 ms", tex)

    @unittest.skipUnless(python_docx_available(), "python-docx is not installed")
    def test_docx_export_keeps_headings_in_order_and_bullets(self):
        # Scenario I/J: standard headings in source order, no bullet lost, no table
        import docx

        result = self.export("docx")
        self.assertEqual(result.returncode, 0, result.stderr)
        document = docx.Document(os.path.join(self.out, "Test_Lebenslauf.docx"))
        texts = [p.text for p in document.paragraphs]
        positions = [next(i for i, t in enumerate(texts) if t.startswith(h)) for h in HEADINGS]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(len(document.tables), 0)
        self.assertTrue(any("Einführung von Code-Reviews" in t for t in texts))

    @unittest.skipUnless(have("lualatex"), "LuaLaTeX is not installed: PDF export and page check not run")
    def test_pdf_export_has_extractable_text(self):
        # CG-12.4
        result = self.export("pdf")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(have("pdftotext"))
        text = subprocess.run(["pdftotext", os.path.join(self.out, "Test_Lebenslauf.pdf"), "-"], capture_output=True, text=True).stdout
        self.assertIn("Berufserfahrung", text)


class CompareContentTests(unittest.TestCase):
    def test_hyphen_at_line_break_is_not_a_difference(self):
        # A PDF breaks "E-Mail" or "Kubernetes-Cluster" at the hyphen; the words are the same
        sys.path.insert(0, os.path.dirname(EXPORTER))
        import export_document

        missing, extra = export_document.compare_content("E-Mail und Kubernetes-Cluster", "E-\nMail und Kubernetes-\nCluster")
        self.assertEqual((dict(missing), dict(extra)), ({}, {}))

    def test_missing_word_is_still_reported(self):
        sys.path.insert(0, os.path.dirname(EXPORTER))
        import export_document

        missing, _ = export_document.compare_content("Python und Kafka", "Python")
        self.assertEqual(sorted(missing), ["kafka", "und"])


if __name__ == "__main__":
    unittest.main()
