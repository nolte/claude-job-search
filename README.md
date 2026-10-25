# claude-job-search

[![CI](https://github.com/nolte/claude-job-search/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/nolte/claude-job-search/actions/workflows/ci.yml)

A Claude Code plugin that helps you write job applications for German-speaking countries
(*Bewerbungsunterlagen*): a clear CV, a cover letter, a motivation letter, the application e-mail,
and a check before you send. It writes in German and follows the usual conventions of Germany,
Austria and Switzerland.

## Purpose

Every application repeats the same facts, and each posting asks for something a little different.
This plugin keeps your facts in one place, on your own computer, and builds every document from
them. The result is consistent, fits the posting, and never invents experience.

- You give it a **job posting**. It reads the posting, compares it with your profile, shows you a
  plan, and writes nothing until you approve.
- **Every statement comes from your own material.** If something is missing, the plugin leaves a
  visible gap marked `[ERGÄNZEN: …]` and asks you. A requirement counts as met only when there is
  proof for it.
- **Your data stays with you.** Everything lives in one local folder (the *Wurzel*). Nothing is
  uploaded or sent by the plugin.

## What you can do with it

- **Apply for one posting, end to end.** `job-application-solution` leads you through all steps.
- **Find out what you want.** `job-application-traumjob-interview` records your wishes and
  deal-breakers; `job-application-fit-check` then tells you whether a posting or company fits.
- **Build your profile.** `job-application-profile-capture` turns old CVs, certificates and notes
  into one profile; `job-application-cv-maintain` keeps it up to date.
- **Understand a posting.** `job-application-posting-analysis` lists the requirements and shows
  which ones you meet, with proof.
- **Write the documents.** CV, cover letter, motivation letter and e-mail each have their own skill
  (`job-application-cv-create`, `-cover-letter-create`, `-motivation-letter-create`,
  `-email-create`).
- **Check and export.** `job-application-quality-gate` checks a set before you send it, and
  `job-application-reviewer` reads it like a recruiter would. `job-application-export` produces
  PDF, Word, HTML or Markdown.
- **Look for postings** (optional). `job-application-job-search` searches job boards with a search
  brief that you approve first.

Each application gets its own folder with a status and a short history. The plugin does not track
what happens after you send; you note replies and interviews there yourself, or in Obsidian.

## Getting started

1. Install the plugin from its marketplace.
2. Create `job-application/konfiguration.md` and point it at your material (one file or a folder of
   notes).
3. Put your old CVs and certificates into `rohdaten/` and run
   `/claude-job-search:job-application-profile-capture`.
4. Run `/claude-job-search:job-application-solution` and paste the text of a posting.

The step-by-step guide with examples is on the docs page *Getting started*:
<https://nolte.github.io/claude-job-search/getting-started/> (German: *Erste Schritte*,
<https://nolte.github.io/claude-job-search/de/getting-started/>).

## Optional helpers

Some steps can reach the internet through add-on programs from other authors (MCP servers):
LinkedIn, the Handelsregister, web search, job boards and, for pages that need a browser, a
browser server. **None is required.** Without them you paste the text yourself, and the plugin
installs none of them. The same ground rules apply to all of them, among them: they only start
with your approval, they stay small, and they never receive your personal data. The overview and
the risks are on the docs page *Optional MCP servers*:
<https://nolte.github.io/claude-job-search/mcp-servers/>.

## Usage

Start a skill with `/claude-job-search:<skill>`, for example
`/claude-job-search:job-application-solution`. Your data lives in the *Wurzel*, by default the
`job-application/` folder of your working directory. It is local and ignored by git. If you want
to track it, use a private repository.

The full documentation, in English and German, is at
<https://nolte.github.io/claude-job-search>.

## Structure

The repository holds the skills, one agent, the rules they follow (`spec/`), the documentation and
the tests. If you want to work on the plugin itself, start with [CLAUDE.md](CLAUDE.md): it
explains the layout, the commands and the conventions.

## Related repositories

This plugin is built on [Claude Code](https://claude.com/claude-code) and shares its tooling with
other projects of the same portfolio:

- [claude-shared](https://github.com/nolte/claude-shared): the shared plugin and specifications
  that this repository follows for specs, pull requests and releases.
- [gh-plumbing](https://github.com/nolte/gh-plumbing): the shared GitHub workflows and settings
  behind the checks and releases.
- [taskfiles](https://github.com/nolte/taskfiles): the shared task modules that run the local
  commands, such as the documentation build.

## Status

Ready to use: all thirteen skills and the agent, the application folder with status and history,
and export to PDF, Word, HTML and Markdown. PDF is the default for application portals, because
parsers read it reliably.

Planned (`project/roadmap.md`): follow-up after sending, interview preparation, analysis of
employment references (*Zeugnisse*), and German versions of the rules.

The plugin is tested, but it cannot promise that every application portal reads a document
correctly. PDF export needs pandoc and LuaLaTeX on your computer.

## License

[MIT](LICENSE) — Copyright © 2026 nolte
