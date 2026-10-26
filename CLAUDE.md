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
- `scripts/` — helper scripts shared by skills, for example `grundlage_hash.py` (Datengrundlage hash and `stand`, spec R-9.5) and `posting_url.py` (URL cleaning and refused targets of the posting intake, spec UE-2), `stellensuche.py` (Suchauftrag, run log, Warteschlange and hand-off of the recurring search, spec ST-13 to ST-20) with the launcher `stellensuche_geplant.sh`, `arbeitsagentur.py` (query mapping, answer check and cross-board merge of the interactive Bundesagentur search, spec ST-21; it runs no search), `workflow.py` (tasks, dependencies, attempts and approvals of the whole application process, spec WF-1 to WF-14), `qualitaet.py` (quality report of one Vorgang: deterministic checks, export read-back, verification of the semantic verdicts of a model, spec QS-1 to QS-13; it sends and approves nothing) with its library `ats_checks.py` (technical ATS checks of the exported PDF, DOCX or HTML and the key terms of the analysis, QS-13), `kommunikation.py` (replies handed over as messages: assignment, mail type, proposals the user approves, Wiedervorlagen, follow-up basis, spec MV-18 to MV-27; it sends nothing and reads no mailbox) `bewerbung.py` (the result of one application: status changes by one table of allowed transitions, phase and outcome apart from the status, event history with the day it happened and the day it was recorded, next steps, data-quality checks, repeatable migration, spec BE-1 to BE-17; it sends nothing and contacts no employer) and `lernen.py` (statistics, retrospective and proposals over confirmed results, spec EA-1 to EA-16; it changes no status, document or personal data)
- `agents/<name>.md` — reusable sub-agents
- `spec/` — specifications (EN canonical; DE translation pending). Nineteen specs under `spec/job-application/`: `konventionen`, `cv-generierung`, `lebenslauf`, `lebenslauf-versionen`, `anschreiben`, `anschreiben-formulierung`, `motivationsschreiben`, `kontaktklassifikation`, `unternehmensanalyse`, `recherche`, `traumjob-interview`, `lokale-struktur`, `stellensuche`, `stellenanzeige-url`, `workflow`, `qualitaetssicherung`, `bewerbungsergebnis`, `ergebnisauswertung`, `mail-verwaltung` (the Gmail operations are specification only, no connector; the local processing of handed-over messages is implemented). Index with one line per spec: `spec/README.md`
- `docs/` — MkDocs source (EN and DE)
- `design/` — logo, icon, mascot and README banner: reproducible image prompts (`prompts/`), chosen results with their prompt sidecars (`assets/`), and `scripts/add_wordmark.py` that sets the title onto the banner (see `design/README.md`)
- `project/` — mission, roadmap, requirements
- `tests/` — stdlib unittest suite: CV checks, export, skill structure, spec index (`task test`)

Plugin skills are namespaced by plugin name — for example `/claude-job-search:<skill>`.

## Command entry points

- `task lint` — pre-commit checks
- `task test` — test suite (stdlib unittest: CV checks, export, skill structure, spec index)
- `task docs` — build the MkDocs site
- `task export -- <datei.md> --format <pdf|docx|html|md|tex> --doc-type <cv|letter|motivation|email>` (`email` only with `md`; exit code 4 = page limit exceeded) — export a Bewerbungsdokument (skill `job-application-export`); `task export -- --reproduce <datei>.manifest.json` rebuilds an export from its manifest and compares it
- `task quality -- <pruefen|status|entscheiden|katalog> <vorgang-ordner>` — quality report of one Vorgang (`scripts/qualitaet.py`, skill `job-application-quality-gate`): writes `qualitaet.json`, which the workflow reads before the send approval; it sends and approves nothing
- `task workflow -- <befehl>` — run the workflow orchestration (`scripts/workflow.py`): `starten`, `laufen` (for a scheduler), `naechste`, `uebersicht`, `freigeben`, …; it executes no skill and sends nothing
- `task search -- <befehl>` — run the deterministic helper of the recurring job search (`scripts/stellensuche.py`); `task search:scheduled -- <konfiguration.md>` starts one headless session per due Suchauftrag (needs `claude` and the JobSpy server)
- `task communication -- <befehl>` — process replies after the dispatch (`scripts/kommunikation.py`, skill `job-application-follow-up`): proposals the user approves, Wiedervorlagen, follow-up basis; it sends nothing
- `task result -- <befehl>` — the result of an application (`scripts/bewerbung.py`): `status`, `historie`, `ereignis erfassen`, `statuswechsel`, `naechste`, `pruefen`, `finde`, `migrieren`; it sends nothing and contacts no employer
- `task learn -- <befehl>` — evaluate confirmed results (`scripts/lernen.py`): `statistik`, `retrospektive`, `vorschlaege`; it changes no status, document or personal data
- `task plugin:reload` — launch Claude Code with this repo loaded as a plugin (dogfooding)

## Dogfooding

```bash
claude --plugin-dir .
```

Use `/reload-plugins` inside the session to pick up changes without restarting.

The skills refuse a Wurzel inside this repository (LS-2.4), so the default `job-application/` folder in the checkout does not work for dogfooding. Point `wurzel` (and `grundlage`) in `job-application/konfiguration.md` at a folder outside the checkout, for example `~/job-application-test/`. The Anker itself stays in the working directory.

## Conventions

- Skills are written in English (the instructions), while the documents they produce are German.
- Specs are authored in English first; German translations follow via `/nolte-shared:spec`.
- Generated configuration files (`.github/*.yml`, `Taskfile.yml`, workflow YAML) are in English.

## Authoring rules

- **Application data is personal.** The `job-application/` working folder (its Wurzel lies outside this checkout, see Dogfooding), PDFs and DOCX files are local and git-ignored by default; tracking them in a private, unpublished repository is the user's decision (R-6, LV-4). This repository is public: never commit a profile, a CV, or a letter here, and never commit fixtures with real data.
- **Fictional examples only.** Examples in specs and skills use fictional names (Musterfirma GmbH, Beispiel AG); never real stations, employers or people.
- **No invented facts.** Skills must not generate employer names, dates, grades, skills or certificates that are not in the Datengrundlage, in `profil.md` derived from it, or stated by the user in the session. Unknown items become `[ERGÄNZEN: …]`.
- **Paths through the Anker.** Every skill resolves paths through `job-application/konfiguration.md` (LS-2: keys `wurzel`, `grundlage`, `grundlage_index`); no hard-coded `job-application/` paths except the Anker itself.
- **No version bumps in PRs.** The tag of a release comes from the release-drafter draft (`v$RESOLVED_VERSION` from the PR labels). The manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, two occurrences there) are set to that tag only by the `chore(release): <tag>` commit that `release-publish.yml` creates (`auto-align`), or by a `chore(release): <tag>` PR as the fallback; a manual bump in a feature PR is forbidden (`spec/project/release-automation/` in claude-shared). Releases are published, not left as drafts.
- Keep `CLAUDE.md`, `spec/`, and the plugin manifest in sync with what the repo actually ships.
- Never copy plugin-owned skills into a consumer's `.claude/skills/` — distribution happens via the plugin marketplace.
