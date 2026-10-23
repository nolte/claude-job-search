"""Export tests for skills/job-application-export/scripts/export_document.py (spec CG-12).

Uses a synthetic Lebenslauf. Requires pandoc for md/html/docx and python-docx for the DOCX
structure check. The PDF export needs LuaLaTeX; without it the PDF test is skipped and the
skip reason is printed, so the result is not reported as passed.
"""

import json
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
        # the layout filter maps the entry shapes of the Lebenslauf spec (LB-4.1, LB-5.1) to the template macros
        flat = " ".join(tex.split())  # pandoc wraps long lines
        self.assertIn("\\cvheader{Lebenslauf}{Max Mustermann}", flat)
        self.assertIn("\\cvstation{04/2021", flat)

    def test_letter_gets_its_own_page_geometry_and_no_cv_filter(self):
        # the Anschreiben uses 25 mm left (AS-3.3) and no Lebenslauf macros
        result = subprocess.run(
            [sys.executable, EXPORTER, self.source, "--format", "tex", "--doc-type", "letter", "--out-dir", self.out, "--name", "Test_Brief"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.out, "Test_Brief.tex"), encoding="utf-8") as handle:
            tex = handle.read()
        self.assertIn("left=25mm", tex)
        self.assertNotIn("\\cvstation{", tex)

    def test_readback_macros_cover_the_three_layout_macros(self):
        sys.path.insert(0, os.path.dirname(EXPORTER))
        import export_document

        self.assertEqual(export_document.READBACK_MACROS.count("newcommand"), 3)

    def test_gap_entry_and_short_row_render_in_the_grid(self):
        # LB-5.1: a two-part station ("Zeitraum | Elternzeit") is a station with an empty employer, not a
        # fallback heading; LB-6.1/LB-11.9: a two-word row keeps the no-break space out of the label split
        with open(self.source, "w", encoding="utf-8") as handle:
            handle.write(SOURCE.replace(
                "## Sprachkenntnisse (GER-Niveau)\n",
                "### 01/2019 – 03/2021 | Elternzeit\n\n## Ausbildung und Studium\n- 2018: Informatik\n\n## Sprachkenntnisse (GER-Niveau)\n",
            ))
        result = self.export("tex")
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.out, "Test_Lebenslauf.tex"), encoding="utf-8") as handle:
            flat = " ".join(handle.read().split())
        self.assertIn("\\cvstation{01/2019 -- 03/2021}{Elternzeit}{}", flat)
        self.assertNotIn("\\textbar", flat)
        self.assertIn("\\cvrow{2018}{Informatik}", flat)
        self.assertIn("\\textbf{Deutsch}: Muttersprache", flat)

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

    def freeze(self):
        with open(self.source, "w", encoding="utf-8") as handle:
            handle.write(SOURCE.replace("format: chronologisch\n", "format: chronologisch\nauspraegung: basis\nversion: 1\nversion_datum: 2026-01-01\n"))

    def test_export_writes_a_manifest_that_pins_source_and_output(self):
        # lebenslauf-versionen LV-6: the manifest names the source hash, the epoch and the output hash
        self.freeze()
        self.assertEqual(self.export("tex").returncode, 0)
        with open(os.path.join(self.out, "Test_Lebenslauf.tex.manifest.json"), encoding="utf-8") as handle:
            manifest = json.load(handle)
        self.assertEqual(manifest["frontmatter"]["version"], "1")
        self.assertEqual(manifest["source_date_epoch"], 1767225600)
        self.assertTrue(manifest["byte_reproduzierbar"])
        self.assertEqual(len(manifest["quelle"]["sha256"]), 64)
        self.assertEqual(len(manifest["ausgabe"]["sha256"]), 64)

    def test_invalid_version_datum_is_an_error_not_a_traceback(self):
        with open(self.source, "w", encoding="utf-8") as handle:
            handle.write(SOURCE.replace("format: chronologisch\n", "format: chronologisch\nversion_datum: 2026-02-30\n"))
        result = self.export("tex")
        self.assertEqual(result.returncode, 1)
        self.assertIn("version_datum", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_version_datum_only_warns_for_formats_without_a_date(self):
        # DOCX, HTML and MD carry no PDF date: like a missing date, a bad one is reported and the export goes on
        with open(self.source, "w", encoding="utf-8") as handle:
            handle.write(SOURCE.replace("format: chronologisch\n", "format: chronologisch\nversion_datum: '2026-02-30'\n"))
        for fmt in ("html", "md"):
            result = self.export(fmt)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("version_datum", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_quoted_version_datum_is_read_like_the_bare_date(self):
        # YAML quotes around the date are not part of the value
        for quoted in ('"2026-01-01"', "'2026-01-01'"):
            with open(self.source, "w", encoding="utf-8") as handle:
                handle.write(SOURCE.replace("format: chronologisch\n", f"format: chronologisch\nversion_datum: {quoted}\n"))
            for fmt in ("html", "md", "tex"):
                result = self.export(fmt)
                self.assertEqual(result.returncode, 0, f"{quoted} {fmt}: {result.stderr}")
            with open(os.path.join(self.out, "Test_Lebenslauf.tex.manifest.json"), encoding="utf-8") as handle:
                manifest = json.load(handle)
            self.assertEqual(manifest["source_date_epoch"], 1767225600)
            self.assertEqual(manifest["frontmatter"]["version_datum"], "2026-01-01")

    def test_reproduce_confirms_an_unchanged_export_and_rejects_a_changed_source(self):
        self.freeze()
        self.export("tex")
        manifest = os.path.join(self.out, "Test_Lebenslauf.tex.manifest.json")
        ok = subprocess.run([sys.executable, EXPORTER, "--reproduce", manifest], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("byte-identisch", ok.stdout)
        with open(self.source, "a", encoding="utf-8") as handle:
            handle.write("\nNachtrag\n")
        changed = subprocess.run([sys.executable, EXPORTER, "--reproduce", manifest], capture_output=True, text=True)
        self.assertEqual(changed.returncode, 3)
        self.assertIn("Quelle verändert", changed.stderr)

    def test_reproduce_accepts_a_manifest_with_a_non_ascii_name(self):
        # a manifest written before 0.2.0 may carry an umlaut in `name` and `ausgabe.datei`; the rebuilt
        # file is found under today's transliteration (LV-6)
        self.freeze()
        self.export("tex")
        manifest = os.path.join(self.out, "Test_Lebenslauf.tex.manifest.json")
        with open(manifest, encoding="utf-8") as handle:
            data = json.load(handle)
        data["name"] = "Test_Lébenslauf"  # transliterates to the same file name as the export above
        data["ausgabe"]["datei"] = "Test_Lébenslauf.tex"
        with open(manifest, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        result = subprocess.run([sys.executable, EXPORTER, "--reproduce", manifest], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("byte-identisch", result.stdout)

    def test_frozen_version_exports_next_to_the_arbeitsstand_by_default(self):
        # lokale-struktur LS-3, lebenslauf-versionen: versionen/vNNN_<datum>.md -> ../export/vNNN_<datum>.<ext>
        folder = os.path.join(self.tmp, "lebenslauf-basis")
        os.makedirs(os.path.join(folder, "versionen"))
        frozen = os.path.join(folder, "versionen", "v001_2026-01-01.md")
        with open(frozen, "w", encoding="utf-8") as handle:
            handle.write(SOURCE.replace("format: chronologisch\n", "format: chronologisch\nauspraegung: lebenslauf-basis\nversion: 1\nversion_datum: 2026-01-01\n"))
        result = subprocess.run([sys.executable, EXPORTER, frozen, "--format", "md", "--doc-type", "cv"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(os.path.isfile(os.path.join(folder, "export", "v001_2026-01-01.md")), result.stdout)
        self.assertFalse(os.path.exists(os.path.join(folder, "versionen", "export")))

    def test_file_names_are_transliterated_to_ascii(self):
        # R-4: ä→ae, ö→oe, ü→ue, ß→ss, spaces to hyphens, hyphen and underscore kept
        sys.path.insert(0, os.path.dirname(EXPORTER))
        import export_document

        self.assertEqual(export_document.ascii_name("Jörg_Müller-Straße Lebenslauf"), "Joerg_Mueller-Strasse-Lebenslauf")
        # accented and non-German letters are transliterated, not dropped
        self.assertEqual(export_document.ascii_name("René_Dupont_Lebenslauf"), "Rene_Dupont_Lebenslauf")
        self.assertEqual(export_document.ascii_name("Zoë_Łukasz_Ørsted"), "Zoe_Lukasz_Orsted")
        self.assertEqual(export_document.ascii_name("François_Çelik"), "Francois_Celik")
        result = subprocess.run(
            [sys.executable, EXPORTER, self.source, "--format", "md", "--doc-type", "cv", "--out-dir", self.out, "--name", "Max_Müller_Lebenslauf"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(os.path.isfile(os.path.join(self.out, "Max_Mueller_Lebenslauf.md")))

    def test_product_names_do_not_break_across_lines(self):
        # cv.lua: heuristic (inner capital or digit) plus the frontmatter list keep_together; a plain pair stays
        with open(self.source, "w", encoding="utf-8") as handle:
            handle.write(SOURCE.replace("format: chronologisch\n", "format: chronologisch\nkeep_together: [Docker Compose]\n").replace(
                "- Einführung von Code-Reviews im Team mit fünf Entwicklern.",
                "- Deployments mit Argo CD, GitLab CI und Docker Compose automatisiert; Python und Kafka eingesetzt",
            ))
        result = self.export("tex")
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(self.out, "Test_Lebenslauf.tex"), encoding="utf-8") as handle:
            flat = " ".join(handle.read().split())
        for joined in ("Argo~CD", "GitLab~CI", "Docker~Compose"):
            self.assertIn(joined, flat)
        self.assertIn("Python und Kafka", flat)

    def test_manifest_does_not_carry_the_dropped_situation_key(self):
        with open(self.source, "w", encoding="utf-8") as handle:
            handle.write(SOURCE.replace("format: chronologisch\n", "format: chronologisch\nsituation: Standard\n"))
        self.assertEqual(self.export("md").returncode, 0)
        with open(os.path.join(self.out, "Test_Lebenslauf.md.manifest.json"), encoding="utf-8") as handle:
            self.assertNotIn("situation", json.load(handle)["frontmatter"])

    @unittest.skipUnless(python_docx_available(), "python-docx is not installed")
    def test_docx_metadata_names_no_author(self):
        # decision D2: no tool or account name in the DOCX author fields
        import docx

        self.assertEqual(self.export("docx").returncode, 0)
        properties = docx.Document(os.path.join(self.out, "Test_Lebenslauf.docx")).core_properties
        self.assertEqual((properties.author, properties.last_modified_by), ("", ""))
        self.assertEqual(properties.title, "Test_Lebenslauf")

    @unittest.skipUnless(have("lualatex"), "LuaLaTeX is not installed: PDF reproducibility not run")
    def test_frozen_pdf_is_byte_identical_on_a_second_export(self):
        self.freeze()
        self.export("pdf")
        first = open(os.path.join(self.out, "Test_Lebenslauf.pdf"), "rb").read()
        self.export("pdf")
        self.assertEqual(first, open(os.path.join(self.out, "Test_Lebenslauf.pdf"), "rb").read())


class PageNumberTests(unittest.TestCase):
    def strip(self, text):
        sys.path.insert(0, os.path.dirname(EXPORTER))
        import export_document

        return export_document.strip_page_numbers(text)

    def test_year_in_the_period_column_is_not_taken_for_a_page_number(self):
        # page 2 ends with a period line "2019": content, not the page number
        self.assertEqual(self.strip("Berufserfahrung\n1\n\fAusbildung\n2019\n"), "Berufserfahrung\nAusbildung\n2019")

    def test_page_number_at_the_end_of_its_page_is_dropped(self):
        self.assertEqual(self.strip("Berufserfahrung\n1\n\fAusbildung\n2\n\n"), "Berufserfahrung\nAusbildung")

    def test_single_page_without_a_number_is_unchanged(self):
        self.assertEqual(self.strip("Berufserfahrung\nAusbildung"), "Berufserfahrung\nAusbildung")


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
