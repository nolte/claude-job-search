# Tests

`task test` runs the standard-library suite (`python3 -m unittest discover -s tests -v`).

- `test_cv_checks.py`: scenario tests for `scripts/cv_checks.py` (spec CG-13, CG-14). Synthetic data only.
- `test_export.py`: export of Markdown, HTML and DOCX through `skills/job-application-export/scripts/export_document.py`
  (requires pandoc, and python-docx for the DOCX check). The PDF test needs LuaLaTeX and is skipped without it.
- `test_posting_url.py`: URL cleaning and refused targets of the posting intake (spec UE-2, scenarios UE-A and UE-F). Synthetic data only.
- `test_skill_structure.py`: frontmatter names, description, and existence of referenced spec, requirement, and script files,
  and of cross-referenced skills and agents.

Scenarios that depend on the generating skill (CG-14 A, C, D, E) are verified by review, not by these tests.
