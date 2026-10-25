# Getting started

This page takes you from an empty folder to your first checked application. You need Claude
Code and a folder for your application data. No developer tooling is required for the steps
below; the export to PDF is the one optional step that needs extra software, see
[Export](export.md).

## 1. Install the plugin

Pick one of three ways.

**From the marketplace, per project.** Add the marketplace and enable the plugin in the
`.claude/settings.json` of the folder you work in:

```json
{
  "extraKnownMarketplaces": {
    "claude-job-search": {
      "source": {
        "source": "github",
        "repo": "nolte/claude-job-search"
      }
    }
  },
  "enabledPlugins": {
    "claude-job-search@claude-job-search": true
  }
}
```

**Interactively.** Inside Claude Code run `/plugin`, add the marketplace
`nolte/claude-job-search`, and install `claude-job-search` from it.

**From a local checkout.** Clone the repository and start Claude Code with
`claude --plugin-dir <path-to-the-checkout>`.

Afterwards the skills are available as `/claude-job-search:<skill>`, for example
`/claude-job-search:job-application-solution`.

## 2. Create the configuration

The plugin reads exactly one file at a fixed place: `job-application/konfiguration.md` in the
folder where you run Claude Code. Everything else is found through it. The file has a short
frontmatter and may hold free notes below it.

**Minimal, one file as Datengrundlage.** All application data lives in `job-application/`;
the Datengrundlage is one Markdown file:

```markdown
---
grundlage: job-application/grundlage/lebenslauf-chronologisch.md
---

# Konfiguration
```

**Directory mode with an Obsidian vault outside the data root.** The Datengrundlage is a
folder of notes, one per station, plus an index note that carries the maintenance history:

```markdown
---
wurzel: /home/me/bewerbungen
grundlage: /home/me/vault/lebenslauf
grundlage_index: /home/me/vault/metadata/Lebenslauf.md
---

# Konfiguration

Applications in `/home/me/bewerbungen`, the Datengrundlage in my Obsidian vault.
```

The keys:

| Key | Needed | Meaning |
|---|---|---|
| `wurzel` | optional | Root of all application data. Default: `job-application/` next to the configuration. May point anywhere on your disk, including a folder inside an Obsidian vault. |
| `grundlage` | optional | Your Datengrundlage: one Markdown file, or a directory of notes. Default: `<wurzel>/grundlage/lebenslauf-chronologisch.md`. |
| `grundlage_index` | only for a directory | The index note of the directory, with the maintenance history. |

Relative paths are resolved against the folder that contains `job-application/konfiguration.md`.
If you start a skill without this file, it asks for the paths once and writes the file for you.

!!! warning "Not inside the plugin repository"
    The data root must not lie inside a checkout of the plugin itself. If you develop the plugin
    and apply with it, set `wurzel` to a folder outside the checkout.

## 3. Capture your data

Put your raw material into `<wurzel>/rohdaten/`: old CVs, certificates, a LinkedIn export, notes.
If you have connected the optional LinkedIn server, [LinkedIn access](linkedin.md) shows how to
bring in your own profile. Then run

```text
/claude-job-search:job-application-profile-capture
```

The skill reads the raw material, asks where it is unsure, and writes the Datengrundlage (your
stations, education, skills, languages, certificates, each with its source) and the derived
`profil.md`. Anything it cannot verify is marked `[ERGÄNZEN: …]` and stays visible until you
resolve it. Later changes go through `/claude-job-search:job-application-cv-maintain`, which asks
only about findings and records every change in the maintenance history.

## 4. Optional: say what you are looking for

```text
/claude-job-search:job-application-traumjob-interview
```

A seven-phase interview that records your wishes, priorities and vetoes as `wunschprofil.md`.
Nothing is written before you confirm the summary. With a confirmed Wunschprofil,
`/claude-job-search:job-application-fit-check` compares a posting or a company with it before you
spend time on documents, and a veto stops the plan in step 5.

## 5. The first application

```text
/claude-job-search:job-application-solution
```

Paste the posting text or give its link. A link alone is enough: the skill cleans it of tracking
parameters, loads the page through the optional open-webSearch server and shows you the extracted
posting for confirmation before anything is saved. If the page cannot be read (removed, log-in
wall, bot check, needs JavaScript, no server connected), you are asked to paste the text. LinkedIn
links are never loaded. The skill

1. checks that your Datengrundlage and profile are current,
2. creates the application folder and analyses the posting (which requirements you meet, with
   evidence, which you meet partly, which are not covered),
3. classifies the counterpart (employer directly, recruiter, agency, platform, referral), see
   [Counterparts](counterparts.md),
4. shows you a **plan**: which documents in which format, which stations and bullets it will
   use, which gaps remain,
5. waits for your approval,
6. creates the documents in order (Lebenslauf, then Anschreiben, then the e-mail if you apply by
   e-mail), and
7. runs the quality gate.

The plan is a gate, not a formality: no document is written before you say yes. If the plan
is wrong, say what to change, and the skill shows a new plan.

## 6. What is in the application folder

Each application gets one folder under the data root, named after company and position, for
example `musterfirma-senior-backend/`:

| File | Content | Written by |
|---|---|---|
| `vorgang.md` | Company, position, reference number, channel, status, dates, the approved plan, the history | the skills for their steps; you for sending and everything after |
| `notizen.md` | Your free notes: impressions, questions for the interview, names from calls | only you; no skill changes it |
| `stellenanzeige.md` | The posting, verbatim | posting analysis |
| `analyse.md` | Requirement match with evidence, the counterpart, the companies involved | posting analysis |
| `passung.md` | Fit against your Wunschprofil, only when you ran the fit check | fit check |
| `lebenslauf.md` | The Lebenslauf for this application | CV skill |
| `anschreiben.md` | The Anschreiben | cover letter skill |
| `motivationsschreiben.md` | Only when asked for | motivation letter skill |
| `email.md` | Only when you apply by e-mail | e-mail skill |
| `pruefbericht.md` | Which stations were selected and why; the result of the quality gate | CV skill, quality gate |
| `export/` | PDF, DOCX, HTML, only when you ask for an export | export skill |

Next to the application folders sit `grundlage/` (if your Datengrundlage lives there),
`profil.md`, `wunschprofil.md`, `rohdaten/`, `firmen/` (one file per company with stable facts
and your notes), and the CV variants. A **variant** is a Lebenslauf with its own focus that you
reuse across applications, for example `lebenslauf-basis/` or `lebenslauf-teamleitung/`. Each
variant folder holds its `lebenslauf.md`, its `pruefbericht.md`, frozen versions in `versionen/`
and their exports in `export/`.

## 7. Status and overview

`vorgang.md` carries a `status` field with a fixed set of values. The skills set the first
values; from sending onwards you set them yourself:

| Set by the skills | Set by you |
|---|---|
| `erfasst` (posting captured), `analysiert`, `geplant` (plan approved), `erstellt` (documents created), `geprüft` (quality gate passed) or `in Arbeit` (blockers open) | `versendet`, `rückmeldung`, `gespräch`, `angebot`, `verhandlung`, `zusage`, `absage`, `abgelehnt` (you declined), `zurückgezogen`, `ohne Antwort` |

Every status change gets one line in the *Verlauf* section of `vorgang.md` with the date, so
the history stays readable. When you send the application, record the date, the channel and
the attachments there too; `wiedervorlage` holds the date of your next follow-up. Free text
goes to `notizen.md`.

**Overview across all applications.** If your data root is an Obsidian vault (or a folder in
one), a Bases file lists every application by status without any extra plugin. Save this as
`bewerbungen.base` in the vault:

```yaml
filters:
  and:
    - 'file.name == "vorgang"'

properties:
  firma:
    displayName: Firma
  stelle:
    displayName: Stelle
  status:
    displayName: Status
  wiedervorlage:
    displayName: Wiedervorlage

views:
  - type: table
    name: Offen
    filters:
      and:
        - 'status != "zusage"'
        - 'status != "absage"'
        - 'status != "abgelehnt"'
        - 'status != "zurückgezogen"'
        - 'status != "ohne Antwort"'
    groupBy:
      property: status
      direction: ASC
    order:
      - firma
      - stelle
      - status
      - wiedervorlage
      - file.folder

  - type: table
    name: Abgeschlossen
    filters:
      or:
        - 'status == "zusage"'
        - 'status == "absage"'
        - 'status == "abgelehnt"'
        - 'status == "zurückgezogen"'
        - 'status == "ohne Antwort"'
    order:
      - firma
      - stelle
      - status
      - loeschen_ab
      - file.folder
```

Open the file in Obsidian: the first view groups the open applications by status, the second
lists the closed ones with their deletion date. Without Obsidian, `grep -r "^status:" */vorgang.md`
in the data root gives the same list on the command line.

## 8. Export on request

Documents stay Markdown until you ask for an export. Run
`/claude-job-search:job-application-export` or `task export` for a PDF, DOCX, HTML or Markdown
copy. A text PDF is the default, also for application portals; produce DOCX only when a portal
explicitly asks for it. Details, requirements and the container that bundles everything are on
the [Export](export.md) page.

## 9. Retention and deletion

A closed application keeps its folder. For every final status other than `zusage`, the data is
meant to be deleted six months after closure: set `loeschen_ab` in `vorgang.md` to that date
when you close the application. No skill deletes anything; the deletion is your act, and the
Bases view above shows you which dates have passed.

!!! info "For developers"
    The rules behind this page: `spec/job-application/lokale-struktur/en.md` (terms, layout,
    configuration keys, lifecycle and status values, retention), `spec/job-application/konventionen/en.md`
    (fact integrity, data protection, output formats), `spec/job-application/lebenslauf-versionen/en.md`
    (variants and frozen versions), `spec/job-application/traumjob-interview/en.md` (Wunschprofil and fit
    check), `spec/job-application/kontaktklassifikation/en.md` (counterparts).
