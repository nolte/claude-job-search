# Browser MCP

Some posting pages show their text only after a browser has run their scripts. A plain page fetch
(see [Web search](websearch.md)) then returns an empty shell. A browser MCP server can load such a
page. It is meant for one purpose: when you give only the URL of a posting, the plugin should
still be able to read it.

!!! warning "Browser route switched off until redirects are shown"
    This page covers the intake of a posting from a URL
    (`spec/job-application/stellenanzeige-url/en.md`), implemented in
    `job-application-posting-analysis`. The route through the open-webSearch server works. The
    browser route stays switched off in practice: it needs a server that is shown to report the
    final URL of the loaded page, and none is (see "Limits you should know"). The plugin ships no
    `.mcp.json`. The rules all optional servers share (consent, one
    route per source, budget, no evasion) are on [Optional MCP servers](mcp-servers.md). The
    server is an independent project, not affiliated with this plugin. No skill requires one:
    without a server you paste the posting text, as described in
    [Getting started](getting-started.md).

Every statement about the server is the project's own, as its README says it. The README
was read on 24 October 2026 on its main branch, not at a tagged version. The latest npm
version on that day was `@playwright/mcp` 0.0.83. The plugin has not run
the server and does not confirm these statements. Check the README for anything newer.

## How the plugin uses a URL

1. You give a URL. Tracking parameters such as `utm_source` are removed first.
2. The plugin first fetches the page without a browser through the open-webSearch server.
3. Only if that returns a page that is just a script shell does it offer the browser, name the
   server and the risk, and wait for your yes. A removed posting, a log-in wall or a bot check never
   leads to the browser; you are asked to paste the text. While no server is shown to report the
   final URL, this step does not happen and you are asked to paste the text.
4. The browser opens the one URL, reads the page text and closes. It does not click, type, fill
   forms, upload or download, and it keeps no profile, cookies or logins.
5. You see the extracted posting and its fields before anything is written to your Wurzel. A URL
   that lists several postings is not a posting: you name one entry. `linkedin.com` links and
   internal addresses are refused before any request.

A page behind a log-in or a CAPTCHA is not read, and no workaround is tried. A `linkedin.com` URL
is never loaded this way; see [LinkedIn access](linkedin.md). The research of a firm (levels 1
and 2) never uses a browser.

## The server

| | Playwright MCP |
|---|---|
| Project | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) |
| Package, licence | `@playwright/mcp`, Apache-2.0 |
| Needs | Node.js 18 or newer |
| Browser | Starts its own browser |
| Profile and logins | `--isolated` keeps the profile in memory and saves nothing |
| Headless | `--headless` |

The plugin reads a posting without your logins and without your history. Use only a server that can
run in an isolated, non-persistent browser context; a server that works in your own browser session
does not fit this intake.

## Set up Playwright MCP

The README of the project is the authority for current steps and options. For Claude Code:

```bash
claude mcp add playwright -- npx @playwright/mcp@<version> --isolated --headless --block-service-workers
```

Replace `<version>` with a version number you have checked. The README shows `@latest`, which runs
new code on every start without your review. The version checked for this page is 0.0.83.

| Option | What it does, per the README |
|---|---|
| `--isolated` | Keeps the browser profile in memory and does not save it to disk. Without it, a persistent profile is kept in a cache folder |
| `--headless` | Runs without a visible window. The default is a visible window |
| `--block-service-workers` | Blocks service workers |

### Limit what the server can do

The server offers many more tools than the intake needs. The plugin uses only `browser_navigate`,
`browser_snapshot` and `browser_close`. Deny the other tools that act on a page in your Claude Code
permission settings, for example in `.claude/settings.local.json`:

```json
{
  "permissions": {
    "deny": [
      "mcp__playwright__browser_click",
      "mcp__playwright__browser_drag",
      "mcp__playwright__browser_drop",
      "mcp__playwright__browser_evaluate",
      "mcp__playwright__browser_file_upload",
      "mcp__playwright__browser_fill_form",
      "mcp__playwright__browser_hover",
      "mcp__playwright__browser_press_key",
      "mcp__playwright__browser_run_code_unsafe",
      "mcp__playwright__browser_select_option",
      "mcp__playwright__browser_type"
    ]
  }
}
```

Tool names follow the README. Open `/mcp` after the setup and check the list of tools of your
installed version; a name that is missing from the list above is not denied. The README says that
`browser_run_code_unsafe` is the riskiest one: it runs arbitrary code in the server process.

## Limits you should know

- **Not a security boundary.** The README says so for Playwright MCP as a whole. Its option
  `--allowed-origins` "does not affect redirects", so it cannot stop a page from sending the
  browser somewhere else.
- **Redirects are not confirmed.** The plugin must check where a page ended up, because a posting
  link can redirect to a page it must not read (RC-5.2 rule 9). The README does not say that a tool
  reports the final URL. Until a run of the installed version shows it, the browser route stays
  switched off in practice. This is an open point in the specification (UE-12).
- **Scripts run on your machine.** A browser executes the scripts of whatever site the URL points
  to. That is why the plugin asks for your yes before it opens one.
- **Terms of the site.** Some sites forbid automated reading. You check their terms; the plugin
  does not claim a fetch is allowed. A blocked page is reported and skipped, and no proxy or other
  workaround is used.
- **Posting text is data.** Text on the page that tries to give instructions is ignored.
- **Personal data.** What the browser reads becomes part of the Claude session and goes to the
  model provider. The plugin stores only the posting text and the fields it extracts.

## Without a browser server

Paste the posting text into `job-application-solution`. Every skill works that way.
