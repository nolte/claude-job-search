# Use cases

These pages show the plugin at work in the situations people actually face. Each page starts
from a goal, lists what you need beforehand, walks through the steps with the commands and
what you see, and ends with the files that remain in your data root. All names in the examples
are fictional (Musterfirma GmbH, Beispiel AG).

[Getting started](../getting-started.md) explains installation and configuration once; the
use cases assume that this is done and your Datengrundlage exists.

## Which page fits you

| Your situation | Page | Skills involved |
|---|---|---|
| You have a posting and want a complete, checked application | [Apply to a posting](posting-application.md) | `job-application-solution`, `-posting-analysis`, `-cv-create`, `-cover-letter-create`, `-email-create`, `-quality-gate`, `-export` |
| A recruiter or an agency contacts you, or the employer stays hidden | [Via a recruiter or an agency](recruiter.md) | `job-application-solution`, `-posting-analysis` (counterpart), `-cover-letter-create` (variant `vermittler`) |
| You do not know what to apply for, or you are changing fields | [Career change and job search](career-change.md) | `job-application-traumjob-interview`, `-job-search`, `-fit-check`, `-cv-create` (format `kombiniert`) |
| No posting exists, or a programme asks for your reasons | [Initiative application and Motivationsschreiben](initiative-and-motivation.md) | `job-application-cover-letter-create` (variant `initiativ`), `-motivation-letter-create` |
| Your career has moved on and the base data must follow | [Keep your data and CVs current](maintain-and-variants.md) | `job-application-cv-maintain`, `-profile-capture`, `-cv-create` (variants, frozen versions) |

## Rules that hold in every scenario

- **Plan before documents.** No document is written before you approve the plan.
- **No invented facts.** Every statement comes from your Datengrundlage; what is missing stays
  visible as `[ERGÄNZEN: …]` until you resolve it.
- **You send.** The plugin prepares and checks. Sending, replies and the final result are your
  entries in `vorgang.md`.
- **Optional servers stay optional.** Every scenario works by pasting text. LinkedIn,
  Handelsregister, web search and JobSpy only add convenience, see
  [Optional MCP servers](../mcp-servers.md).
