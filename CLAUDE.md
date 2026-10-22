# CLAUDE.md

Orientation for Claude Code and contributors working inside this repository.

## What this repo is

`claude-job-search` is a Claude Code plugin that bundles skills and an agent for
German-speaking job applications (*Bewerbungsunterlagen*): Wunschprofil and fit check,
single-column Lebenslauf, DIN-5008-style Anschreiben, Motivationsschreiben,
Bewerbungs-E-Mail, requirement match against a Stellenanzeige, a quality gate before
sending, export, and the Vorgang (one folder per application with status and history).
The conventions are in `spec/job-application/konventionen/en.md`.

## Layout

- `.claude-plugin/plugin.json` — plugin manifest (name, version, author)
- `.claude-plugin/marketplace.json` — marketplace catalog (downstream install source)
- `skills/<name>/SKILL.md` — reusable skills; each folder is one skill
- `scripts/` — helper scripts shared by skills, for example `grundlage_hash.py` (Datengrundlage hash and `stand`, spec R-9.5)
- `agents/<name>.md` — reusable sub-agents
- `spec/` — specifications (EN canonical; DE translation pending). Ten specs under `spec/job-application/`: `konventionen`, `cv-generierung`, `lebenslauf`, `lebenslauf-versionen`, `anschreiben`, `motivationsschreiben`, `kontaktklassifikation`, `unternehmensanalyse`, `traumjob-interview`, `lokale-struktur`. Index with one line per spec: `spec/README.md`
- `docs/` — MkDocs source (EN and DE)
- `project/` — mission, roadmap, requirements
- `tests/` — stdlib unittest suite: CV checks, export, skill structure, spec index (`task test`)

Plugin skills are namespaced by plugin name — for example `/claude-job-search:<skill>`.

## Command entry points

- `task lint` — pre-commit checks
- `task test` — test suite (stdlib unittest: CV checks, export, skill structure, spec index)
- `task docs` — build the MkDocs site
- `task export -- <datei.md> --format <pdf|docx|html|md> --doc-type <cv|letter|motivation|email>` — export a Bewerbungsdokument (skill `job-application-export`)
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

- **Application data is personal.** The `job-application/` working folder, PDFs and DOCX files are local and git-ignored by default; tracking them in a private, unpublished repository is the user's decision (R-6, LV-4). This repository is public: never commit a profile, a CV, or a letter here, and never commit fixtures with real data.
- **Fictional examples only.** Examples in specs and skills use fictional names (Musterfirma GmbH, Beispiel AG); never real stations, employers or people.
- **No invented facts.** Skills must not generate employer names, dates, grades, skills or certificates that are not in the Datengrundlage, in `profil.md` derived from it, or stated by the user in the session. Unknown items become `[ERGÄNZEN: …]`.
- **Paths through the Anker.** Every skill resolves paths through `job-application/konfiguration.md` (LS-2: keys `wurzel`, `grundlage`, `grundlage_index`); no hard-coded `job-application/` paths except the Anker itself.
- **Version bump on every user-visible change.** Bump `version` in both manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, two occurrences there); releases are published, not left as drafts.
- Keep `CLAUDE.md`, `spec/`, and the plugin manifest in sync with what the repo actually ships.
- Never copy plugin-owned skills into a consumer's `.claude/skills/` — distribution happens via the plugin marketplace.
