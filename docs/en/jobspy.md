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
   searches per session, and a limited posting age (RC-5.8 rule 4). There are no scheduled or
   recurring searches. Full details are fetched only for the entry you pick, never for a list.
5. The shortlist shows vetoes from your Wunschprofil with their reason instead of dropping them,
   merges duplicates across boards and against your existing Vorgänge, and flags postings from
   a Vermittler or without an employer name. A fit check runs only on request, per entry.
6. You pick one entry; the skill hands it to `job-application-solution` with the posting text as
   posted and the URL as `stellenquelle`.
7. The brief, the shortlist and your decision per entry (`übernommen`, `abgelehnt`, `offen`) go
   to `suche/<JJJJ-MM-TT>-<slug>.md` in your Wurzel. The record is kept for 90 days. The skill
   lists records past that date and deletes nothing; you decide.

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
