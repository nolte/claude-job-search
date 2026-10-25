# Scenario fixtures

Fictional data for the scenario tests A to H of the critical findings audit (`tests/test_scenarios.py`). Nobody in
these files exists; names, employers and numbers are invented (CLAUDE.md: fictional examples only, no real data).

| Folder | Content |
|---|---|
| `grundlage/` | Three Datengrundlagen: `erfahren` (platform engineer with one station of leadership), `einsteiger` (student, one unconfirmed station), `quereinstieg` (carpenter, retraining, junior developer) |
| `anzeigen/` | Three postings: specialist, leadership role, career changer |
| `analysen/` | The requirement match (`analyse.md`) for each posting, in the table form of CG-4 |
| `cv/` | A good Lebenslauf per persona. The tests plant one defect at a time in a copy |
| `briefe/` | A good Anschreiben for the leadership and the career-change case |

The good documents must have no finding (`FixtureTests`). A scenario test changes one thing and expects the rule that
should fire. A new check therefore needs a fixture defect, not a new fixture.

## What is automated and what stays review

| Scenario | Automated by `test_scenarios.py` | Stays with the review (model judgement) |
|---|---|---|
| A Technical specialist | Unsupported skill, certificate or leadership wording blocked (CV-19, CV-16); *Muss* without evidence (CV-07) | Which projects and technologies the posting makes relevant; order of emphasis (CG-5) |
| B Technical leadership | Recorded leadership may be written; invented team size, moved leadership, posting number as own experience blocked (CV-05, CV-16, BR-03, BR-04) | Whether a leadership claim is tied to the right station (BR-04 is a note); technical depth kept |
| C Career changer | Invented domain station (CV-15), unproven tool (CV-19), unproven requirement (CV-07), gap closed by the retraining station (CV-13), retraining not counted as work (BR-03) | Which transferable skills to show; credibility of the story. Known limit: years of experience are not tied to a domain (`test_known_limit_years_of_experience_are_not_tied_to_a_domain`) |
| D Limited experience | Invented metric, unconfirmed station, invented language level blocked (CV-05, CV-20, CV-19); a CV without numbers is clean | Choice of projects and education; page limit one page (checked on the exported PDF) |
| E Missing information | *Muss* gap is a Warnung and never *erfüllt* (CV-07, CV-14); placeholders block in CV and letter (CV-01, BR-01); a posting number is a Warnung, not proof (BR-02) | Whether the skill asks the user; whether the gap is addressed honestly in the letter |
| F Conflicting information | Period, title and duplicate entries (CV-06, CV-15); a different year in the letter (BR-02) | Conflicts between `profil.md` and the Grundlage, and between older documents and the Grundlage: the profile is re-derived, no script compares it |
| G Profile maintenance | The hash follows the Grundlage and marks older documents stale; a correction reaches the checks; unchanged stations keep passing | The interview itself (diff, confirmation, no silent overwrite); that a stale document is re-derived by its owning skill |
| H Export | Content check, German characters, markdown copy, manifest pins the source, a changed source is detected (needs pandoc); added or lost words are reported | PDF layout and the page limit (needs LuaLaTeX, covered by `test_export.py` where installed); ATS parsing of the PDF is not tested |

Not tested anywhere: that a model follows the instructions of a skill. What the plan gate asks, whether it stops at a
blocker, and the tone of a letter are checked by reading a generated example, as CG-14 states.
