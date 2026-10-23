# Handelsregister access

Who is the firm behind a posting, and does it exist in the form it claims? The commercial register
(Handelsregister) answers this: legal name, Rechtsform, Sitz, register number and managing
directors. The open-source
[Handelsregister MCP server](https://github.com/lexdoudkin/handelsregister-mcp) by lexdoudkin
(Apache-2.0) lets Claude look a firm up in the register portal during the research, so you do not
have to search the portal by hand.

!!! note "The preferred route to the register, but optional and not part of this plugin"
    With the server connected and your yes, the register is read through it and through no other
    route; web search and page fetches are not used for `handelsregister.de`, because they bypass
    your consent and the budget below. This is the working rule of the research procedure
    (`spec/job-application/recherche/en.md`, RC-5.3). No skill of this plugin requires the server,
    and the plugin installs nothing. Without it, everything still works: the research says so, and
    you may enter the register data yourself or leave the items as `nicht ermittelt`. The server is
    an independent project, not affiliated with this plugin or with the register portal.

## When the lookup is offered

- Only at research level 1 or 2, never at level 0.
- Automatically for a Vorgang whose counterpart is a Vermittler (Personalberatung,
  Personalvermittlung, Zeitarbeit) and for the recruiter's firm itself.
- For a direct employer only when you ask for it.
- Always with your yes. Before the first lookup of a Vorgang, Claude names the limits and risks
  below and waits. A no leaves the other channels untouched; the register items stay
  `nicht ermittelt`.

## What the research uses

| Need | Server tool |
|---|---|
| Find the firm by name, Sitz or register number | `search_company` |
| Register entry: name, Rechtsform, Sitz, register number, managing directors | `get_company` |
| Current excerpt (document type `AD` only) | `fetch_document` |
| Whether and when annual accounts were filed (existence and date only) | `list_filed_documents` |
| Remaining hourly allowance | `rate_limit_status` |

The research does not use `get_shareholders`, `fetch_filed_document`, `fetch_document` with a type
other than `AD` (`HD`, `CD`, `SI`, `UT`, `VÖ`), or bulk and neighbour queries. They serve
shareholder research and profiling, which an application does not need (RC-5.3 rule 1).

## Limits and rules

1. **Budget.** At most 4 retrievals per Vorgang at research level 1 and at most 8 at level 2
   (`rate_limit_status` does not count). Both levels share one budget per Vorgang, also across
   sessions: the count is read back from the line `Kanäle` in the record. Calls run one after the
   other. Claude never raises the server's variable `HANDELSREGISTER_MAX_PER_HOUR` (default 60);
   you may lower the numbers. When the budget or the hourly allowance is used up, the open items
   stay `nicht ermittelt` with the reason `Abrufgrenze erreicht`.
2. **Data minimisation.** Birthdates and private addresses of managing directors are not copied
   into `analyse.md` or any firm file. Names and functions are recorded only as far as the
   identity check needs them (RC-5.3 rule 5).
3. **A hit alone confirms nothing.** A register hit confirms the identity of the firm only
   together with the imprint. Two firms with the same name are separated by Sitz and register
   number; if the posting or imprint does not settle which one is meant, the status is
   `Identität nicht bestätigt` and you decide (RC-5.3 rules 6 and 8).
4. **Failure is not an abort.** A failed lookup, an empty result or an unresolved ambiguity leaves
   the item `nicht ermittelt` with the reason, and the research continues (rule 8).
5. **Records.** The line `Kanäle` states the route and the count, for example
   `Handelsregister über handelsregister-mcp (2 Abrufe)`, or why no lookup ran (RC-9 rule 8).

## What it does not cover

The server reads the Handelsregister. Published annual accounts (Unternehmensregister,
Bundesanzeiger) and official insolvency notices stay manual: the research names them as
`nicht ermittelt` or you look them up yourself. Licensed commercial data providers are not
covered here either.

## Risks

- **Terms and law.** The server's README states that the portal limits automated retrievals, sets
  a limit of 60 retrievals per hour, and notes that the portal warns that automated mass querying
  can be a criminal offence. These are statements of the README, not settled law and not confirmed
  by this documentation. Using the server is your decision and your risk. Look up single firms in
  small numbers.
- **Personal data.** The register holds personal data of managing directors. Whatever the server
  reads becomes part of the Claude session and goes to the model provider like any other text in
  it. Keep birthdates and private addresses out of your files.
- **A young project.** The repository was created on 2026-06-21 and has few contributors. It was
  not on PyPI when checked on 2026-10-23 (HTTP 404 on pypi.org), so it is installed from a clone.
  Review the code before you run it, and pin a commit. The commit checked for this page is
  `26e616beb808bc653ed0504c0c9cd525235082fc` (2026-06-21). Nothing updates the pin
  automatically; read the diff before you move it.
- **Portal drift.** The server parses a live portal. When the portal changes, lookups can fail or
  return wrong fields. The research then falls back to `nicht ermittelt`.
- **Do not install the `[ocr]` extra.** It pulls in PyMuPDF (AGPL-3.0 or a commercial licence) and
  is not needed for the lookups above.

## Set it up

The server's own [README](https://github.com/lexdoudkin/handelsregister-mcp) is the authority for
current steps and options. In short: clone the repository, check out the commit you reviewed, and
install it from the clone without the `[ocr]` extra:

```bash
git clone https://github.com/lexdoudkin/handelsregister-mcp
cd handelsregister-mcp
git checkout 26e616beb808bc653ed0504c0c9cd525235082fc
pip install -e .
```

Then register it with Claude Code, as the README describes:

```bash
claude mcp add handelsregister -- handelsregister-mcp
```

Check with `/mcp` that the server is connected. Leave `HANDELSREGISTER_MAX_PER_HOUR` at its default.
