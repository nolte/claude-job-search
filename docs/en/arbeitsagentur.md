# Arbeitsagentur (Bundesagentur für Arbeit)

The job search of the Bundesagentur für Arbeit (BA, [arbeitsagentur.de/jobsuche](https://www.arbeitsagentur.de/jobsuche)) lists
many German postings that [JobSpy](jobspy.md) does not reach. The skill `job-application-job-search` can read it as a second
source through the community MCP server [jobsuche-mcp-server](https://github.com/wunderfrucht/jobsuche-mcp-server) (MIT).

!!! warning "Interactive only, and legally unsettled"
    The BA publishes **no official API** for the job search. The server uses an interface that the community project
    [bundesAPI/jobsuche-api](https://github.com/bundesAPI/jobsuche-api) documents, with a shared public client key. The
    [Nutzungsbedingungen](https://www.arbeitsagentur.de/nutzungsbedingungen) (section 2a, paragraph 3) forbid robots and
    forbid reading an interface for data collection against its intended purpose. Whether a search that *you* start for
    *your* application is within that purpose is not settled by the text. So the plugin uses the BA **only when you ask, in an
    interactive session**, never in a recurring Suchauftrag, never on a schedule, and it stores no BA result in the
    Warteschlange. Using it is your decision and your risk. This is no legal advice.

The rules all optional servers share are on [Optional MCP servers](mcp-servers.md); the normative text is
`spec/job-application/stellensuche/en.md` ST-21 and `recherche/en.md` RC-5.9. The plugin installs nothing and ships no
`.mcp.json`. The server is an independent project, not affiliated with this plugin or with the BA.

## What the server is (checked on 2026-10-26)

| Point | Finding |
|---|---|
| Source | Rust server around the crate `jobsuche`; endpoint `rest.arbeitsagentur.de/jobboerse/jobsuche-service` |
| Credentials | None from you; the shared public key is built into the crate. `JOBSUCHE_API_KEY` can override it |
| Maintenance | 3 stars, last code change 2025-10-23, 6 open issues; unit tests only for parameter handling, none against the live service |
| Tools | `search_jobs`, `get_job_details`, `search_jobs_with_details`, `batch_search_jobs`, `get_server_status` |
| Used by the skill | `search_jobs` and `get_job_details` only. The two bulk tools are never used |
| Limits | Pages of up to 100; retries with backoff are the crate's; the server adds 100/200 ms pauses in its bulk tools |
| Not available | Contact data and application deadline; salary, `fulltime` and the job type only in the full record |
| Known defect | `contract_type` is accepted and **not applied** in `search_jobs` |

The plugin has **not run this server against the live BA service**. The field names come from the server's source code; check them
against the version you install.

## Set it up

You need Node.js (npm) or a Rust toolchain. Check the README of the server for current steps. For Claude Code:

```bash
claude mcp add jobsuche -- npx @wunderfrucht/jobsuche-mcp-server
```

`npx` without a version runs whatever is published. Pin a version you have looked at (`@wunderfrucht/jobsuche-mcp-server@<version>`)
if you prefer. The tool names are then `mcp__jobsuche__search_jobs` and `mcp__jobsuche__get_job_details`. Remove it with
`claude mcp remove jobsuche`; nothing else in the plugin changes.

## How the skill uses it

Name `arbeitsagentur` as a board in the Suchbrief (it counts as one of the three boards). After your yes for exactly that brief:

1. `scripts/arbeitsagentur.py abfrage` turns the brief into one `search_jobs` call per term. Criteria the server cannot enforce are shown to you with
   the reason and not dropped silently.
2. After every call `scripts/arbeitsagentur.py pruefen` checks the answer. **A failure is never reported as "no postings"**: the skill
   tells apart no hits (`ok_ohne_treffer`), a missing server, a connection problem, a rate limit or block, a rejected key, a rejected
   query and an unreadable answer.
3. `scripts/arbeitsagentur.py zusammenfuehren` merges BA and JobSpy entries: the same id or URL, or the same firm, title and place within three
   days, is one posting with all boards and URLs. A similar title alone merges nothing.
4. You pick one entry; the skill loads its full record and gives the description **as posted** to `job-application-solution`.
   The requirement match, the fit check and the quality gate are the existing ones.

| Brief | Sent to the server | |
|---|---|---|
| Search term | `job_title`, one call per term | direct |
| Place, radius | `location`, `radius_km` (radius only with a place) | direct |
| Maximum age | `published_since_days` | direct |
| Results per board | `page_size` (at most 20) | direct |
| Full-time, part-time | `employment_type` | direct |
| Remote: yes | `employment_type: home_office` (Heim-/Telearbeit, close to remote) | approximate |
| Internship, contract type | – | not applied |
| Remote: no | – | not applied |

Remote, job type and salary are not in the list answer and stay empty. The list answer does not carry the description either; the hand-off loads it.

## Rules specific to the BA source

1. **Consent.** Before the first use the skill names the server, what leaves your machine (only the brief terms) and the risk above, and waits for your yes.
2. **Budget.** At most 20 results per call, 3 boards per search, 5 searches per session; a further page counts as a search and is fetched only on your request.
3. **No evasion.** No proxy, no other key, no retry loop.
4. **Posting text is data.** A title or description can contain instructions. The skill ignores them and the script copies no description into its output.
5. **Personal data.** Your profile never goes into a query. What the server reads still becomes part of the Claude session and goes to the model provider.

## Troubleshooting

| Message of the skill | Meaning and next step |
|---|---|
| `nicht_verfuegbar` | The server is not connected. Check `/mcp`; or paste the posting into `job-application-solution` |
| `verbindung` | Network problem or timeout. Try again later |
| `blockiert` | The BA limited or refused the request. Wait; the plugin sets no proxy |
| `authentifizierung` | The key was refused. Do not look for another key; the interface may have changed |
| `ungueltig` | The server rejected the query. Shorten the term or check the place |
| `antwort_ungueltig` | The answer had no usable list. The server version may not match; check its README |
| `ok_ohne_treffer` | Searched, nothing found. Broaden the terms or the maximum age |

## Tests

`python3 -m unittest tests.test_arbeitsagentur` (or `task test`). The tests use synthetic answers and need no server and no network.
A live test is not part of the plugin.
