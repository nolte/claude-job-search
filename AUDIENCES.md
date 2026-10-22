# Audiences — claude-job-search

<!--
Produced via the `audience-identify` skill, following
spec/project/audience-identification/.
Do not add audiences without first declaring the bounded context below.
-->

## Bounded context

A Claude Code plugin with eleven skills and one read-only agent for German-speaking job applications (Bewerbungsunterlagen): Lebenslauf, Anschreiben, Bewerbungs-E-Mail, requirement match against a Stellenanzeige, and a quality gate before sending. The repository contains the skills, the specs, the templates, the export script, the tests, and the documentation site.

Explicitly outside the bounded context:
- The candidate's personal Datengrundlage. It lives in the user's own working folder or vault, not in this repository.
- The job portals and the employers' own application systems.
- The application itself: the plugin prepares documents, it does not send them.

## Audiences

Each entry: label, relationship category, interaction surface, expectation, documentation `track` (`user-docs` or `developer-docs` per spec/project/docs-audience-tracks/), open questions, `confirmed` or `assumed`, criticality (primary / secondary / peripheral). Mark a whole category as `none — <reason>` when it does not apply.

### Direct consumers

- **Job seekers using the plugin** — _category_: direct-consumer · _surface_: Claude Code slash commands (`/claude-job-search:<skill>`), the Datengrundlage in Markdown · _expects_: a German Lebenslauf and Anschreiben that contain only facts they actually have, clear gap markers, and a quality gate before sending · _track_: `user-docs` · _status_: `assumed` · _criticality_: primary
  - Open questions: which application situations matter most (Berufseinstieg, Quereinstieg, Standard)? Are ATS portals a priority?

### Operators

- **The job seeker running the workflow** — _category_: operator · _surface_: `task export`, `task install`, the Datengrundlage folder, `konfiguration.md` · _expects_: reproducible exports, a clear Blocker list, and the ability to run the checks locally without developer tooling · _track_: `developer-docs` · _rationale_: operator tasks (export, configuration, checks) are documented with the developer-facing commands · _status_: `assumed` · _criticality_: primary
  - Open questions: is this audience the same person as the direct consumer, or a separate operator (for example a career advisor)?

### Contributors / maintainers

- **Developers who extend skills, specs, and tests** — _category_: contributor · _surface_: `skills/`, `spec/`, `scripts/`, `tests/`, `Taskfile.yml`, the CI workflow · _expects_: a clear canonical spec per rule, runnable tests, and a documented release flow · _track_: `developer-docs` · _status_: `assumed` · _criticality_: secondary
  - Open questions: none recorded.

- **The repository maintainer** — _category_: release-manager · _surface_: pull requests, release drafts, branch protection, the release workflows · _expects_: a release process that is repeatable and does not need manual edits to the release notes · _track_: `developer-docs` · _status_: `assumed` · _criticality_: secondary
  - Open questions: none recorded.

### Governing parties

- none — the plugin does not operate under an external regulator. Personal data handling is covered by the repository's own privacy rules (`spec/job-application/konventionen/en.md` R-6) and is not a governing party relationship.

### Indirect audiences

- **Recruiters and HR staff who read the application** — _category_: indirect · _surface_: the documents the plugin produces (Lebenslauf, Anschreiben, E-Mail), never the plugin itself · _expects_: a consistent, factual, one-page-or-two set that matches the posting and holds up to a second read · _track_: `user-docs` · _rationale_: they receive output, they do not use the plugin, so the documentation track is the user-facing one · _status_: `assumed` · _criticality_: primary
  - Open questions: should the documentation describe what a recruiter expects, or stay with the plugin's own rules?

- **Hiring managers and employers reached through recruiters** — _category_: indirect · _surface_: the same documents, received through an agency · _expects_: no disclosure of details the candidate did not approve · _track_: `user-docs` · _status_: `assumed` · _criticality_: secondary
  - Open questions: is the disclosure rule (`spec/job-application/kontaktklassifikation/en.md`) reflected in the user documentation?

## Open questions (cross-cutting)

- Does the Datengrundlage example in the documentation need the same privacy notice as the repository's rules?
- Should `track` be added to the documentation site's front matter, or only to this artefact?

## Revisit triggers

- A new skill or agent changes what a direct consumer can do.
- The plugin gains a second configuration path besides `job-application/konfiguration.md`.
- A new output format (for example PDF without LuaLaTeX) becomes the default.
- A release introduces a breaking change to a skill name or to the Datengrundlage format.
