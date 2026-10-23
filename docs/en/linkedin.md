# LinkedIn access (optional)

Much of what an application needs sits on LinkedIn: the posting, the company page, the people
behind a recruiter's name, and your own profile. The open-source
[LinkedIn MCP server](https://github.com/stickerdaniel/linkedin-mcp-server) by Daniel Sticker
(Apache-2.0) gives Claude direct access to these pages, so you do not have to copy them by hand.

!!! note "Optional, and not part of this plugin"
    No skill of this plugin requires the server or calls it by itself. Everything works without
    it: you paste the posting text, as described in [Getting started](getting-started.md). With the
    server connected, you can ask Claude in the same session to read the page first and then
    run the skill on the result. The server is an independent project, not affiliated with this
    plugin or with LinkedIn.

## Where it helps

| You need | Server tool | Then use |
|---|---|---|
| The text of a posting you found on LinkedIn | `get_job_details`, `search_jobs`, `get_saved_jobs` | `job-application-solution`, `job-application-posting-analysis`, `job-application-fit-check` |
| How a posting wants applications (Easy Apply or the employer's site) | `get_job_apply_url` | `job-application-solution` (input `bewerbungsweg`) |
| Facts about the company: size, sector, open jobs, recent posts | `get_company_profile`, `get_company_posts`, `search_companies` | `job-application-fit-check` (company analysis, UA-3) |
| Who works there, and who a contact person is | `get_company_employees`, `get_person_profile`, `search_people` | [Counterparts](counterparts.md): checking a recruiter's employer (KK-3.3) |
| Your own profile as raw material | `get_my_profile` | `job-application-profile-capture` (intake into `rohdaten/`) |

The server also offers tools that act in your name: `send_message`, `connect_with_person`. This
plugin never sends anything on your behalf (R-6). Use those two tools only when you ask for them
yourself, and review every text first.

## Set it up

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). The server's own
[README](https://github.com/stickerdaniel/linkedin-mcp-server#installation-methods---linkedin-mcp-server)
is the authority for current steps and options. As a Claude Code plugin:

```bash
claude plugin marketplace add stickerdaniel/linkedin-mcp-server
claude plugin install linkedin-mcp-server@linkedin-mcp-server
```

Or as an entry in the `mcpServers` section of your MCP configuration:

```json
{
  "mcpServers": {
    "mcp-server-linkedin": {
      "command": "uvx",
      "args": ["mcp-server-linkedin@latest"],
      "env": { "UV_HTTP_TIMEOUT": "300" }
    }
  }
}
```

The first tool call that needs a login reuses a LinkedIn session from a signed-in local
browser or opens a login window. To sign in beforehand, run
`uvx mcp-server-linkedin@latest --login`. Early calls may report that setup is still running;
retry once it has finished.

## Rules that stay in force

1. **Terms of use.** LinkedIn's User Agreement prohibits automated access. The server's README
   says plainly that accounts can be restricted or banned, with no guarantee. Using the server is
   your decision and your risk. Read single pages, in small numbers, and do not let an agent
   crawl.
2. **Data flow.** Whatever the server reads becomes part of the Claude session and goes to the
   model provider like any other text in it. The plugin's rule that nothing is sent anywhere
   applies to the plugin; it does not cover what you load into the session. Read only the pages
   you need, and keep personal data of third parties out of the Datengrundlage.
   Searches follow the rule for company research (UA-3): a query carries only the company name
   and a generic term, never your Wunschprofil, Datengrundlage or application text. Network
   access happens when you ask for it.
3. **Facts stay traceable.** A page you read is a source, not proof. Record it: the posting link
   as `stellenquelle` in `vorgang.md`, company facts with source and reading date (UA-3). Your own
   LinkedIn profile is raw material for `profile-capture`; it asks about every uncertain
   entry, and nothing in it is final until you confirm it.
4. **Recruiters.** A profile read does not replace the question to the counterpart. The employer
   is `gesichert` only when the counterpart confirms it (KK-3.3).
5. **Without the server.** The posting text, the company page and your profile export work as
   before. Paste them, or put the export into `rohdaten/`.
