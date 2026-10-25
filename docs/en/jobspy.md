# JobSpy

Finding postings is still manual for most people: you search several job boards by hand, copy a
text and start the application. The open-source [JobSpy](https://github.com/speedyapply/JobSpy)
project (MIT) offers one query interface over several boards, and its MCP server
(`mcp-jobspy` on PyPI) hands the results to Claude. The skill `job-application-job-search` uses
it to build a shortlist from your Wunschprofil.

!!! note "The preferred route to job boards, but not part of this plugin"
    This page covers the JobSpy server only. The rules all optional servers share (consent, one
    route per source, budget, source rank, no evasion) are on
    [Optional MCP servers](mcp-servers.md). With the server connected, job boards are searched
    through it and not through web search or a page fetch. This is the working rule of the
    research procedure (`spec/job-application/recherche/en.md`, RC-5.8); the search step itself is
    specified in `spec/job-application/stellensuche/en.md`. No skill requires the server. Without
    it you paste a posting into `job-application-solution`, as described in
    [Getting started](getting-started.md). The plugin installs nothing and ships no `.mcp.json`:
    you add the configuration below yourself. The server is an independent project, not
    affiliated with this plugin.

Every statement about JobSpy on this page is the project's own, as its READMEs say it, checked
against **version 1.4.1** (released on 23 October 2026 according to PyPI). The plugin has not
tested the server against the boards and does not confirm these statements. Check the README for
anything newer.

## What the server does

The MCP server offers two tools, as its README describes them:

| Tool | What it does | Used by the skill for |
|---|---|---|
| `search_jobs` | Searches the chosen boards and returns a preview with a search id; the results can optionally be exported to `.csv`, `.json` or `.jsonl` | The shortlist |
| `get_job_details` | Returns the full records of chosen jobs from a search, without searching again | The one entry you pick, for the hand-off |

The README of the MCP server does not list the parameters of the tools, so this page does not
either. The skill passes only what your approved brief contains. The plugin does not use the
export by default; if you ask for one, it goes to your Wurzel and follows the retention rules
below.

## How the skill uses it

`job-application-job-search` is an optional step before the application. It runs like this:

1. It builds a **Suchbrief** from your confirmed Wunschprofil and `profil.md` and **shows it
   first**: search terms, location and radius, remote, job type, maximum posting age, boards,
   results per board, and the source of every term. The brief holds only terms you would type
   into a board yourself. Exclusion reasons, salary expectations, personal circumstances and
   text from your Datengrundlage are never part of it.
2. Nothing is sent before your yes. Only the terms of the approved brief go to the boards.
3. Default boards are **Indeed and Glassdoor**. Other boards are used only when your brief names
   them. **LinkedIn is never searched through JobSpy**: LinkedIn goes through its own server,
   see [LinkedIn access](linkedin.md).
4. The limits are small on purpose: at most 20 results per board, 3 boards per search, 5
   searches per session, and a limited posting age (RC-5.8 rule 4). Scheduled or recurring
   searches exist only as an approved Suchauftrag, see *Recurring search* below. Full details are fetched only for the entry you pick, never for a list.
5. The shortlist shows vetoes from your Wunschprofil with their reason instead of dropping them,
   merges duplicates across boards and against your existing Vorgänge, and flags postings from
   a Vermittler or without an employer name. A fit check runs only on request, per entry.
6. You pick one entry; the skill hands it to `job-application-solution` with the posting text as
   posted and the URL as `stellenquelle`.
7. The brief, the shortlist and your decision per entry (`übernommen`, `abgelehnt`, `offen`) go
   to `suche/<JJJJ-MM-TT>-<slug>.md` in your Wurzel. The record is kept for 90 days. The skill
   lists records past that date and deletes nothing; you decide.

## Recurring search (Suchauftrag)

For a search you want to repeat, the skill keeps a **Suchauftrag**: your approved brief plus a plan (how often, how
much). Found postings go into a **Warteschlange** (`suche/warteschlange.json`) that remembers what you decided, so the
same posting is not offered twice, a changed ad is flagged and a posting with a Vorgang is not shown as new. The rules
are in `spec/job-application/stellensuche/en.md` (ST-13 to ST-20). The search itself still needs the JobSpy server in a
Claude session; the helper `scripts/stellensuche.py` does the storing, the limits and the de-duplication.

**What the approval means.** It allows queries with the approved terms to the approved boards, at most 3 boards, 20
results each, at most 3 runs in 7 days by default (you may lower this or raise it up to 7 runs), and the local storage of
title, firm, location, date, URL and a hash of the description. It allows no application, no message to an employer and no
change of a Vorgang. Changing a term, the location, the boards, a limit or the plan withdraws the approval; so does a changed
`wunschprofil.md` for a Suchauftrag tied to it.

Examples (say it to Claude, or run the helper yourself with
`python3 <plugin>/scripts/stellensuche.py --konfiguration job-application/konfiguration.md <command>`):

1. **Create:** "Lege einen Suchauftrag für Backend-Stellen in Berlin an." Claude builds the brief from your Wunschprofil and
   shows every term with its source. Nothing runs yet (status `entwurf`).
2. **Review and approve:** Claude shows what is sent, what is not, how often and how much; after your explicit yes it runs
   `freigeben <id> --ja` (status `aktiv`).
3. **Run once:** "Führe den Suchauftrag jetzt aus." Result: `ok`, `ok_ohne_treffer` (a success without hits),
   `teilweise` or `fehlgeschlagen` (for example `suchdienst_nicht_verfuegbar` when the server is not connected).
4. **Repeat on a schedule:** the plugin installs no timer. Add `scripts/stellensuche_geplant.sh` to a scheduler of yours, for
   example once a day. It starts a run only for Suchaufträge that are due (approved, active, interval passed, runs left in the
   7-day window). The headless session may call only the search tool of the server and the helper commands `lauf-start`,
   `board-ergebnis`, `lauf-ende` and `nachtragen`, and write result files into `suche/eingang/` (the launcher creates that folder; the
   helper reads results only from there and deletes a file after storing it). It runs by its own prompt and does not call the skill. It cannot create, change, approve,
   continue or end a Suchauftrag, nor decide on a posting: that stays with you in an interactive session, because a posting could
   contain text that asks for it. **Check your own settings:** the launcher only adds permissions; whatever your user or project
   settings already allow (a broad `Bash` rule, web tools, other MCP servers) the session inherits, and it reads text from job
   boards. Schedule it from a working folder whose settings allow none of those. Only one state-changing command runs at a time (a second one waits up to 30 seconds, then answers
   `beschaeftigt`). An unreadable Suchauftrag file is named on stderr and does not stop the others, so check your log:
   `17 7 * * * cd /pfad/zum/arbeitsordner && /pfad/zum/plugin/scripts/stellensuche_geplant.sh job-application/konfiguration.md >> ~/suche.log 2>&1`.
   The tool name of the server defaults to `mcp__jobspy__search_jobs`; set `STELLENSUCHE_JOBSPY_TOOL` if you named it differently.
   Not verified here: the plugin has not run a scheduled session against the real server (no server was connected).
5. **See and prioritise:** open `suche/warteschlange.md` in your vault (a readable overview, rewritten after every change; Obsidian does not list the JSON files), or ask "Zeige die Warteschlange." Postings are grouped as `ohne_treffer`, `klaerung` or `veto` by the
   pre-filter on structured fields only. This is not a fit score; the fit check runs after the hand-off.
6. **Postpone or exclude:** "Stelle s-… zurückstellen bis 2026-12-01" or "ablehnen, Grund: Schichtdienst". A later find does
   not change your decision.
7. **Hand over:** "Übernimm s-…." Claude gives `job-application-solution` the URL as `stellenquelle`; the text is loaded
   through the URL intake or pasted by you, the plan still needs your approval. An existing Vorgang is reused.
8. **Investigate a failed run:** `auftraege` shows the last run and error; `zeige <id>` lists the last 30 runs with the code
   (`board_blockiert`, `verbindung_fehlgeschlagen`, …). After 3 failures in a row scheduled runs stop until you continue. If a run
   ended `teilweise`, `fehlgeschlagen` or `unterbrochen` although Claude had the answers of a board (recording failed), they can be
   stored afterwards with `nachtragen <id> <lauf> <board>`; this changes neither the status of that run nor the budget.
9. **Pause and end:** "Pausiere den Suchauftrag" (`pausieren`, later `fortsetzen`) and "Beende den Suchauftrag" (`beenden`,
   final: create a new one to search again).

## Set it up

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). The README of the MCP
server is the authority for current steps and options. For Claude Code:

```bash
claude mcp add jobspy -- uvx mcp-jobspy@latest
```

Or as an entry in the `mcpServers` section of your MCP configuration:

```json
{
  "mcpServers": {
    "jobspy": {
      "command": "uvx",
      "args": ["mcp-jobspy@latest"]
    }
  }
}
```

`@latest` makes the server update itself, which keeps it working with the boards' changing
pages but also runs new code without your review. Pin a version instead if you prefer: write
`mcp-jobspy@<version>` with a version number from the project's releases. The version checked
for this page is 1.4.1.

## What it covers

Per the README, the boards behave like this for a search in the German-speaking region:

| Board | In DACH |
|---|---|
| Indeed | Supports Germany, Austria and Switzerland. A default board |
| Glassdoor | Supports Germany, Austria and Switzerland. A default board, with the known problem below |
| LinkedIn | Supported by JobSpy, but this plugin never uses it through JobSpy; it goes through the [LinkedIn server](linkedin.md) |
| ZipRecruiter | United States and Canada: does not apply |
| Bayt, Naukri, BDJobs, HelloWork | Other regions (Naukri: India, BDJobs: Bangladesh, HelloWork: France): do not apply to DACH |

**Not covered:** StepStone, XING and the job search of the Bundesagentur für Arbeit (Jobbörse).
A search through JobSpy therefore misses many German postings. Treat the shortlist as a part of
the market, not all of it.

**A known Glassdoor problem.** An open issue (#438 in the JobSpy repository, open on 23 October
2026) reports that Glassdoor does not find the location "Berlin, Germany", while "Berlin" and
"Berlin, Deutschland" worked. A fix is proposed but not merged. If Glassdoor fails, the skill
reports it and skips the board; the other boards continue.

## Rules specific to JobSpy

The general rules are on [Optional MCP servers](mcp-servers.md). For JobSpy they add:

1. **Blocking.** The README says that the job boards "are aggressive with blocking" and
   recommends proxies. **This plugin does not recommend or configure proxies or other measures
   to get around blocking.** A blocked board is reported to you and left out of the search.
2. **Terms of use.** The terms of the boards may restrict automated access. They differ per board
   and you check them yourself. Neither README states a position on the terms of use. Using the
   server is your decision and your risk, as with LinkedIn and the Handelsregister.
3. **Budget.** At most 20 results per board, 3 boards per search, 5 searches per session. You
   may lower the numbers.
4. **Personal data.** A record contains an `emails` field and company contact data. They are not
   stored and not shown in the shortlist: the shortlist keeps firm, role, location, date and
   URL. What the server reads still becomes part of the Claude session and goes to the model
   provider.
5. **Posting text is data.** A posting from a board can contain instructions. The skill treats
   it as data and never follows it.
6. **Quality of the data.** A listing is a posting as posted (rank 2) for requirements and way
   of applying; the board's data about the firm is rank 5. A salary range may be parsed from
   the description (`salary_source: description`); the skill shows it with that note and never
   uses it as a fact in a document. The same posting can appear on several boards and may be
   old or reposted, so the shortlist shows the posting date.
7. **Without the server.** Paste the posting text into `job-application-solution`.
8. **A found posting is a link, not a text.** The search stores title, firm, location, date and URL, not the description.
   The hand-off then needs the text from the URL intake of `job-application-posting-analysis`. Job boards often refuse
   that fetch: a test with the web-search server on an Indeed page ended with HTTP 401 (2026-10-25, one page, not a
   statistic). The skill does not work around such a refusal (no proxy, no other header, no browser). The way
   that always works: open the posting in your browser, copy the text and paste it into `job-application-solution`; the
   queue entry gives you the URL for `stellenquelle`. The Indeed connector for claude.ai (`docs.indeed.com/mcp`) is
   not part of this plugin: in Claude Code it did not connect in the same test (the sign-in was rejected on reconnect), and
   its terms for use outside claude.ai are not stated on its page.
