# Web search

Company research needs two simple things from the web: finding a page and reading a page you
already know, such as an imprint, a career page or a press release. The open-source
[open-webSearch](https://github.com/Aas-ee/open-webSearch) MCP server gives Claude both, runs on
your own machine and needs no API key.

!!! note "The preferred route for web search, but not part of this plugin"
    With the server connected, `job-application-posting-analysis` and
    `job-application-fit-check` search the web and fetch public pages through it. Without it, they
    use the built-in tools of your client under the same query rules, and the record names the
    route that was used. This is the working rule of the research procedure
    (`spec/job-application/recherche/en.md`, RC-5.2 rules 8 and 9, RC-5.5 rules 4 to 11). No skill
    requires the server. The plugin installs nothing and ships no `.mcp.json`: you add the
    configuration below yourself. The server is an independent project, not affiliated with this
    plugin.
    The rules all optional servers share are on [Optional MCP servers](mcp-servers.md).

## What the server does

The research uses three of the server's six tools. The other three are switched off in the
configuration below.

| Tool | Use in the research |
|---|---|
| `search` | Find a URL or a lead for a firm: the exact firm name, optionally the Sitz, and one allowed generic term such as `Impressum` or `Pressemitteilung` (RC-5.5) |
| `fetchWebContent` with `renderMode: request` | Read one known public page as Markdown: imprint, career page, press, privacy notice (RC-5.2) |
| `fetchGithubReadme` | Read the README of a firm's public repository |

`fetchWebContent` also knows the modes `auto` (its default) and `browser`. The research always
asks for `request`, so no browser renders a page.

Why this route comes first: its engines are documented and limited to a short list, the budget
and the queries follow the plugin's rules, and this page can say what leaves your machine. With
whatever search tool a session happens to have, that depends on the client, the region and the
account.

## Set it up

You need [Node.js](https://nodejs.org/), because the server starts through `npx`. The server's own
[README](https://github.com/Aas-ee/open-webSearch) is the authority for current options. Add this
entry to the `mcpServers` section of your MCP configuration:

```json
{
  "mcpServers": {
    "websearch": {
      "command": "npx",
      "args": ["open-websearch@2.2.0"],
      "env": {
        "MODE": "stdio",
        "DEFAULT_SEARCH_ENGINE": "duckduckgo",
        "ALLOWED_SEARCH_ENGINES": "duckduckgo,startpage,brave",
        "SEARCH_MODE": "request",
        "USE_PROXY": "false",
        "MCP_TOOL_FETCH_CSDN_NAME": "<disabled>",
        "MCP_TOOL_FETCH_LINUXDO_NAME": "<disabled>",
        "MCP_TOOL_FETCH_JUEJIN_NAME": "<disabled>"
      }
    }
  }
}
```

!!! info "Version checked"
    Version 2.2.0 (last checked in October 2026). The variable names and defaults below were
    checked against the [README of version 2.2.0](https://github.com/Aas-ee/open-webSearch/blob/v2.2.0/README.md). Before you change the pinned version, read the
    new README again and compare the variable names.

| Setting | Why |
|---|---|
| `MODE=stdio` | The default is `both`, which also opens an HTTP server next to stdio. With `stdio`, no port is open. CORS stays off (`ENABLE_CORS` is `false` by default) |
| `DEFAULT_SEARCH_ENGINE=duckduckgo` | The default engine would be `bing` |
| `ALLOWED_SEARCH_ENGINES=duckduckgo,startpage,brave` | The default is empty, which allows every engine, among them several that are irrelevant here or Chinese-language. The research uses only these three |
| `SEARCH_MODE=request` | The default is `auto`. According to the README, the setting currently affects only Bing. It states your intent: no browser |
| `USE_PROXY=false` | This is the default. The plugin does not recommend a proxy to get around blocking |
| `MCP_TOOL_FETCH_…_NAME=<disabled>` | According to the README, `<disabled>` switches a tool off. This disables the CSDN, Linux.do and Juejin fetch tools, so the tool list stays short and unambiguous |

Type the value `<disabled>` literally, with the angle brackets. The README of version 2.2.0 documents this; an older release may not support it, which is one more reason to keep the pinned version. If `/mcp` still lists the three tools, check the spelling and the pinned version before you rely on the setting.

**Engines.** The server supports more engines, among them `bing`, `baidu`, `hackernews` and
`exa`. Add `bing` only when you ask for it, for example because coverage of a German firm is too
thin: append it to `ALLOWED_SEARCH_ENGINES`. The privacy properties of each engine are those of
its operator. This page does not assert them.

**Pinned version instead of `@latest`.** The server's README shows `npx open-websearch@latest`.
That runs new code on every start without your review. The configuration above names a version
instead. Someone, usually you, reads the changes and checks the variable names before the pinned
version moves. There is no automation for this. The `open-websearch` agent skill that the README
offers is not used: the plugin has its own rules for queries and budgets.

To check that the server runs, open `/mcp` in Claude Code. The server `websearch` should be
listed as connected. If it is not, the research uses the built-in tools instead.

## Budget

The research keeps a budget per Vorgang. Calls run one after the other, never in bulk and never
on a timer. You may lower the numbers.

| Research level | Searches | Page fetches |
|---|---|---|
| 1 | at most 10 | at most 15 |
| 2 | at most 20 | at most 30 |

The record in `## Recherche` lists the route used and every search with engine, query and date
(RC-9), so you can check afterwards what left your machine.

## Limits and risks

1. **Queries leave your machine.** Each query goes to the search engine. The query rules of the
   research apply unchanged (UA-3.2, RC-5.5): the exact firm name, optionally the Sitz, and one
   generic term from the allowed list. Never your profile, your Datengrundlage, your Wunschprofil
   or application text. What the engine operator does with a query is its own matter. This page
   makes no claim about it.
2. **Scraping and terms.** The server reads engine result pages. Its README says the tool is "for
   personal use only", that you should comply with the terms of service of the corresponding
   engines, and it advises rate limiting. This is the server's statement, not legal advice, and
   this plugin does not confirm it. Using the server is your decision and your risk. The budget
   above limits how much you trigger.
3. **Results are fragile.** Results depend on each engine's page layout and can break when it
   changes. A failed or blocked search leaves the items it served as `nicht ermittelt`, and the
   research goes on with other channels. A blocked engine is reported to you and skipped. No proxy
   is used to get around the block.
4. **A hit is a lead.** A search result is a hint. A finding needs the page itself, read and
   dated, not the snippet (RC-5.5 rule 1).
5. **No browser.** The research does not use Playwright or `renderMode: browser`. A page that is
   readable only with JavaScript is recorded as `nicht ermittelt` with the reason. You may paste
   the text yourself. The one planned exception is a posting URL that you give yourself; see
   [Browser MCP](browser.md).
6. **Not for LinkedIn and not for registers.** A `linkedin.com` URL is never passed to the fetch
   tools (RC-5.4 rule 6). Use the [LinkedIn server](linkedin.md) or paste the text. Handelsregister,
   Unternehmensregister and the insolvency notices are form portals and cannot be fetched this
   way.
7. **Fetched text is data.** A page can contain instructions. Claude reads it as data and never
   follows it. According to the README, the initial and final URLs of `fetchWebContent` remain
   subject to public-network safety checks. The plugin passes only URLs from trusted places and
   never an internal address. The check of a redirect comes after the request: a redirect to
   `linkedin.com` is noticed only afterwards, and the text is then not used. The request to the
   redirect target has already been sent from your machine at that point. A built-in fetch tool that
   does not report the final URL is not used for pages at all. Most client fetch tools do not say
   so, so in practice only their search is available: the pages wait for the server or for text
   you paste, and the items stay open. Its search stays allowed.
8. **Everything read enters the session.** Fetched pages become part of the Claude session and go
   to the model provider like any other text in it (RC-10).
9. **Supply chain.** `npx` downloads and runs code from the npm registry. A pinned version limits
   this to code of one release, but does not replace a review. The licence is not repeated here;
   see the project's repository.
10. **No shipped configuration.** Starting third-party code without a separate step of yours is not
    acceptable, so the plugin does not register the server. If you remove the entry, the research
    falls back to the built-in tools.
