# CLAUDE.md

Orientation for Claude Code and contributors working inside this repository.

## What this repo is

`claude-job-search` is a Claude Code plugin that bundles skills and an agent for
German-speaking job applications (*Bewerbungsunterlagen*): tabular Lebenslauf,
DIN-5008-style Anschreiben, Bewerbungs-E-Mail, requirement match against a
Stellenanzeige, and a quality gate before sending. The conventions are in
`spec/job-application/konventionen/en.md`.

## Layout

- `.claude-plugin/plugin.json` — plugin manifest (name, version, author)
- `.claude-plugin/marketplace.json` — marketplace catalog (downstream install source)
- `skills/<name>/SKILL.md` — reusable skills; each folder is one skill
- `agents/<name>.md` — reusable sub-agents
- `spec/` — specifications (EN canonical; DE translation pending)
- `docs/` — MkDocs source (EN and DE)
- `project/` — mission, roadmap
- `tests/` — repo-local test harness (placeholder until first runtime check exists)

Plugin skills are namespaced by plugin name — for example `/claude-job-search:<skill>`.

## Command entry points

- `task lint` — pre-commit checks
- `task test` — test suite (placeholder — no runtime tests yet)
- `task docs` — build the MkDocs site
- `task export -- <datei.md> --format <pdf|docx|html|md> --doc-type <cv|letter|email>` — export a Bewerbungsdokument (skill `job-application-export`)
- `task plugin:reload` — launch Claude Code with this repo loaded as a plugin (dogfooding)

## Dogfooding

```bash
claude --plugin-dir .
```

Use `/reload-plugins` inside the session to pick up changes without restarting.

## Conventions

- Skills are written in English (the instructions), while the documents they produce are German.
- Specs are authored in English first; German translations follow via `/nolte-shared:spec`.
- Generated configuration files (`.github/*.yml`, `Taskfile.yml`, workflow YAML) are in English.

## Authoring rules

- **Application data is personal.** The `job-application/` working folder, PDFs and DOCX files are git-ignored. Never commit a profile, a CV, or a letter, not even as a fixture.
- **No invented facts.** Skills must not generate employer names, dates, grades, skills or certificates that are not in `job-application/profil.md` or stated by the user in the session. Unknown items become `[ERGÄNZEN: …]`.
- Keep `CLAUDE.md`, `spec/`, and the plugin manifest in sync with what the repo actually ships.
- Never copy plugin-owned skills into a consumer's `.claude/skills/` — distribution happens via the plugin marketplace.
