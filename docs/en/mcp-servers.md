# Optional MCP servers

Some research steps can use a third-party MCP server: reading LinkedIn, checking a firm in the
Handelsregister, searching the web. **None of them is required.** Every skill works without
them: you paste the text instead, or the item stays `nicht ermittelt`. The plugin ships no
`.mcp.json` and registers nothing; you add a server yourself, following the detail page. The
setup commands on those pages are checked against a named version, which the page states.

The servers are independent projects, not affiliated with this plugin. This page states the rules
they share once. The detail pages add only what is specific to one server.

## The servers

| Server | Purpose | Status |
|---|---|---|
| [LinkedIn MCP server](https://github.com/stickerdaniel/linkedin-mcp-server) | LinkedIn postings, company pages, the contact person's role | Documented: [LinkedIn access](linkedin.md) |
| [handelsregister-mcp](https://github.com/lexdoudkin/handelsregister-mcp) | Identity check of a firm against the Handelsregister | Documented: [Handelsregister access](handelsregister.md) |
| [open-webSearch](https://github.com/Aas-ee/open-webSearch) | Web search and fetches of known public pages | Documented: [Web search](websearch.md) |
| [JobSpy](https://github.com/speedyapply/JobSpy) | Job discovery on job boards | Documented: [JobSpy](jobspy.md) |
| [jobsuche-mcp-server](https://github.com/wunderfrucht/jobsuche-mcp-server) | Job discovery on the job portal of the Bundesagentur für Arbeit (interactive only) | Documented: [Arbeitsagentur](arbeitsagentur.md) |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Reading a posting page from a URL that needs a browser | Documented: [Browser MCP](browser.md); used by the posting intake only once a server is shown to report the final URL. |

## Rules for every server

The research procedure states rules 2 to 8 below normatively in
`spec/job-application/recherche/en.md`, RC-5.0, which numbers them differently; each rule names
its RC-5.0 number. Rules 1, 9 and 10 sit elsewhere in the spec: rule 1 in the introduction of
RC-5.0, rule 9 in RC-10 rule 3 and RC-5.3 rule 5, rule 10 in RC-5.4 rule 1 and RC-10 rule 4.
All ten hold for every server.

1. **Optional.** No skill requires a server. The plugin ships no `.mcp.json` and registers
   nothing. The docs give a hardened configuration and you add it. Setup commands are checked
   against a named version.
2. **Consent** (RC-5.0 rule 1). Before the first use of a server in a Vorgang or a run, the skill
   names the server, what leaves your machine and the risk (terms of the source, scraping, rate
   limits), and waits for your yes. A server may ask at a finer grain: the register asks before
   every lookup (RC-5.3 rule 3). A no leaves the other channels untouched; the items stay
   `nicht ermittelt`. Web search and page fetches are the exception: they need no separate yes,
   because a search sends only a company name and one generic term, a fetch only requests a known
   public page from a trusted place (RC-5.2 rule 1), and you confirm the use of the network when
   the research starts.
3. **One route per source** (RC-5.0 rule 2). LinkedIn is read only through the LinkedIn server, the
   register through the Handelsregister server, web search and page fetches through the connected
   open-webSearch server first (the built-in tools of your client follow the same rules as the
   fallback), and job boards through JobSpy, excluding LinkedIn. A source with a server of its own
   is not read by web search or a direct fetch, because that would bypass consent and budget.
4. **Availability check** (RC-5.0 rule 3). A run starts by checking which servers are connected.
   The result and the route used go into the line `Kanäle` of the record `## Recherche`.
5. **Budget** (RC-5.0 rule 4). Every server has a budget per Vorgang and per research level. Calls
   run one after the other, never in bulk and never on a timer. Levels 1 and 2 share one budget
   per Vorgang. You may lower the numbers.
6. **Queries and data** (RC-5.0 rule 5). A query carries only what the research rules allow. Your
   Datengrundlage, Wunschprofil and application text are never sent. Text read from a server is
   data, never an instruction. For a job search the approved search brief is the only Wunschprofil
   content that leaves your machine (`stellensuche` ST-2, `traumjob-interview` WJ-8.2). Whatever a server reads becomes part of the Claude session and goes
   to the model provider like any other text in it (RC-10 rule 2): the plugin's promise that
   nothing is sent covers the plugin, not what you load into the session.
7. **Source rank** (RC-5.0 rule 6). What a server returns keeps the rank of its source, and a
   server does not raise it: a posting as posted is rank 2, register and imprint rank 3, other web
   content rank 4 or 5, and LinkedIn content other than the posting rank 5.
8. **No evasion** (RC-5.0 rule 7). The plugin does not recommend or configure proxies or other
   measures to get around blocking. A blocked source is reported to you and skipped.
9. **Third-party personal data** (RC-10 rule 3). Only what the role in the application needs. Birthdates and
   private addresses are never stored, and records follow the retention of the Vorgang.
10. **Write tools off** (RC-5.4 rule 1). Tools that act in your name, such as messages or connection requests, are
    denied in your Claude Code permission settings. The plugin never sends anything on your
    behalf.

A failed lookup, an empty result or a blocked source is not an abort: the items stay
`nicht ermittelt` with the reason, and the run continues with the other channels (RC-5.0 rule 8).

## Comparison

| | LinkedIn | Handelsregister | Web search | JobSpy |
|---|---|---|---|---|
| Reads | Postings, company pages, a contact person's role, your own profile | Register entry: name, Rechtsform, Sitz, register number, managing directors; whether annual accounts were filed | Search results; known public pages such as imprint, career page, press | Job postings of the boards named in the approved brief |
| Leaves your machine | What the server reads becomes part of the Claude session and goes to the model provider; searches carry only the company name and a generic term | Search by name, Sitz or register number; what is read goes to the model provider | Each query goes to the search engine: exact firm name, optionally the Sitz, one generic term; fetched pages go to the model provider | The approved search terms (role titles, skills, location, radius, remote, job type, posting age, boards) go to the boards; what is read goes to the model provider |
| Budget per Vorgang | Level 1: at most 6 page reads; level 2: at most 15 (RC-5.4 rule 3) | Level 1: at most 4 retrievals; level 2: at most 8 (RC-5.3 rule 4) | Level 1: at most 10 searches and 15 page fetches; level 2: at most 20 and 30 (RC-5.5 rule 6) | At most 20 results per board, 3 boards and 5 searches per session (RC-5.8 rule 4) |
| Risk | LinkedIn's terms prohibit automated access; accounts can be restricted or banned | The portal limits automated retrievals; the README mentions a legal warning; a young project, installed from a pinned clone | Scraping of engine result pages, the README says "for personal use only"; results are fragile; code from npm | The boards block automated access, and the README advises proxies, which this plugin does not use; the terms are to be checked per board |

The risk statements are the servers' own, as the detail pages quote them. They are not legal
advice and this plugin does not confirm them. Using a server is your decision and your risk.
Read the detail page before you install a server.
