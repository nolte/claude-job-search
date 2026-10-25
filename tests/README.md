# Tests

`task test` runs the standard-library suite (`python3 -m unittest discover -s tests -v`).

- `test_cv_checks.py`: scenario tests for `scripts/cv_checks.py` (spec CG-13, CG-14). Synthetic data only.
- `test_export.py`: export of Markdown, HTML and DOCX through `skills/job-application-export/scripts/export_document.py`
  (requires pandoc, and python-docx for the DOCX check). The PDF test needs LuaLaTeX and is skipped without it.
- `test_scenarios.py`: the scenarios A to H of the critical findings audit on the fictional fixtures in `tests/fixtures/szenarien/`
  (`README.md` there lists per scenario what is automated and what stays review).
- `test_semantic_fidelity.py`: wording of ownership, scope and expertise and team results against the station record (CV-22, CV-23, CG-7.4); the matrix at the end lists which component catches which scenario.
- `test_posting_url.py`: URL cleaning and refused targets of the posting intake (spec UE-2, scenarios UE-A and UE-F). Synthetic data only.
- `test_skill_structure.py`: frontmatter names, description, and existence of referenced spec, requirement, and script files,
  and of cross-referenced skills and agents.

In the CI the job installs pandoc, python-docx and PyYAML (`tests/requirements.txt`); `ToolchainTests` in `test_export.py` fails there if one is missing.
What the CI covers and what only the model evals check: `docs/en/evals.md`, "What the CI covers".

Scenarios that depend on the generating skill (CG-14 A, C, D, E) are verified by review, not by these tests.
What is automated of them, and what is not, is in `tests/fixtures/szenarien/README.md`.

## Semantic fidelity (audit finding F-01, CG-7.4)

`test_semantic_fidelity.py` runs synthetic stations and bullets through `cv_checks.py`. The matrix says which component is
expected to catch which scenario. Only the deterministic column is executed by the tests; the gate column follows from its
severities (Blocker gives `BLOCKIERT`, a Warnung gives `BEREIT MIT WARNUNGEN`), and the reviewer column is what the agent
instructions require (model review, not executed here; the eval suite is the place for a model run).

| ID | Group | Statement | Deterministic check | Quality gate | Reviewer (expected) |
|---|---|---|---|---|---|
| A1 | responsibility | Mitarbeit am Betrieb von Kubernetes-Plattformen. | — | no finding | accepts (meaning kept) |
| A2 | responsibility | Betrieb der Kubernetes-Plattform im Team verantwortet. | — | no finding | accepts (meaning kept) |
| A3 | responsibility | Betrieb der Kubernetes-Plattform eigenverantwortlich übernommen. | — | no finding | accepts (meaning kept) |
| A4 | responsibility | Eigenverantwortlich die gesamte Kubernetes-Plattform betrieben. | CV-22 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| A5 | responsibility | Betrieb der Kubernetes-Plattform verantwortet. | CV-22 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| B1 | leadership | Technische Arbeit im Team koordiniert. | — | no finding | accepts (meaning kept) |
| B2 | leadership | Technische Architekturentscheidungen fachlich geführt. | — | no finding | accepts (meaning kept) |
| B3 | leadership | Engineering-Team gemanagt und Mitarbeiter angeleitet. | CV-16 Blocker | BLOCKIERT | Blocker (agrees) |
| B4 | leadership | Teamleitung für fünf Entwickler übernommen. | CV-16 Blocker | BLOCKIERT | Blocker (agrees) |
| B5 | leadership | Technische Entscheidungen verantwortet. | CV-22 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| B6 | leadership | Team von 5 Entwicklern geleitet. | — | no finding | accepts (meaning kept) |
| B7 | leadership | Technische Aufgaben im Team koordiniert und Kollegen angeleitet. | CV-16 Blocker | BLOCKIERT | Blocker (agrees) |
| C1 | expertise | Terraform in einem Projekt eingesetzt. | — | no finding | accepts (meaning kept) |
| C2 | expertise | Terraform für Infrastrukturautomatisierung angewendet. | — | no finding | accepts (meaning kept) |
| C3 | expertise | Spezialisierung auf Terraform-Module in 3 Projekten. | — | no finding | accepts (meaning kept) |
| C4 | expertise | Terraform-Experte mit tiefer Spezialisierung. | CV-22 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| C5 | expertise | Sehr gute Kenntnisse in Terraform und Kubernetes. | CV-22 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| D1 | scope | Zu einem Abrechnungsservice beigetragen. | — | no finding | accepts (meaning kept) |
| D2 | scope | Gesamte Abrechnungsplattform entworfen. | CV-22 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| D3 | scope | Unternehmensweite Enterprise-Architektur verantwortet. | CV-22 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| D4 | scope | Gesamte Abrechnungsplattform konzipiert. | — | no finding | accepts (meaning kept) |
| E1 | outcome | Latenz der Pipeline von 800 ms auf 120 ms gesenkt. | — | no finding | accepts (meaning kept) |
| E2 | outcome | Latenz der Pipeline um 40 % gesenkt. | CV-23 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| E3 | outcome | Im Team die Latenz der Pipeline um 40 % gesenkt. | — | no finding | accepts (meaning kept) |
| E4 | outcome | Gemeinsam mit dem Partnerteam die Latenz um 40 % gesenkt. | — | no finding | accepts (meaning kept) |
| E5 | outcome | Migrationsprojekt eigenständig umgesetzt; Umsatz um 30 % gesteigert. | CV-22 Warnung + CV-05 Blocker | BLOCKIERT | Blocker (agrees) |
| E6 | outcome | Teamgröße von 4 Entwicklern; Latenz im Team um 40 % gesenkt. | CV-05 Blocker | BLOCKIERT | Blocker (agrees) |
| F1 | rephrasing | Betrieb von Kubernetes-Plattformen im Team mitgestaltet. | — | no finding | accepts (meaning kept) |
| F2 | rephrasing | Infrastruktur mit Terraform automatisiert. | — | no finding | accepts (meaning kept) |
| F3 | rephrasing | Event-Pipeline in Python betreut. | — | no finding | accepts (meaning kept) |
| F4 | rephrasing | Technische Arbeit im Team koordiniert. | — | no finding | accepts (meaning kept) |
| H1 | tailoring | Mitarbeit am Betrieb von Kubernetes-Plattformen (Container, Orchestrierung). | — | no finding | accepts (meaning kept) |
| H2 | tailoring | Eigenverantwortlicher Kubernetes-Experte für Plattformbetrieb. | CV-22 Warnung | BEREIT MIT WARNUNGEN; user decides | Warnung with the six questions (adds the reason) |
| L1 | known limit | Betrieb der Kubernetes-Plattform übernommen. | — (ownership without a marker word) | not seen | must catch it as Warnung or Blocker (model review) |
| L2 | known limit | Migrationsprojekt abgeschlossen; Umsatz deutlich gesteigert. | — (undocumented result without a number) | not seen | must catch it as Warnung or Blocker (model review) |
| L3 | known limit | Abrechnungsplattform entworfen. | — (scope widened by a noun) | not seen | must catch it as Warnung or Blocker (model review) |

The components complement each other: the script sees wording and numbers, the review reads the meaning. The reviewer
adds the reason and the factual alternative for a wording finding, and is the only component that can see the known limits.
