# Local structure, Markdown and Obsidian (EN canonical)

Normative rules for where the user's application data is persisted on the local disk, how
the files are written, and how an Obsidian vault relates to them. Every `job-application-*`
skill obeys these rules. The conventions in `spec/job-application/konventionen/en.md` (R-1 …
R-10) stay in force; this document defines the *locations*, the *lifecycle* and the
*Markdown form* that those rules refer to.

Requirement basis: `project/requirements/eigene-datengrundlage.md`,
`project/requirements/ausgabeformate.md`, `project/requirements/datengrundlage-pflege-interview.md`.

## LS-1 Terms

| Term | Meaning |
|---|---|
| **Stammdaten** | Facts about the candidate and the companies they apply to, valid across applications. Persisted once, reused for every Vorgang. |
| **Vorgang** | One application for one Stellenanzeige, from intake to closure. Persisted in its own folder. |
| **Metadaten** | Structured facts about one Vorgang or one Firma, kept in frontmatter. Skills read and write them. |
| **Notizen** | Free text the user writes about a Vorgang or a Firma. Skills read them and never change them. |
| **Wurzel** | Root directory of all application data. Default `job-application/` in the working directory. |
| **Ableitung** | A derived file that can be regenerated from its source. Never edited by hand. |
| **Anker** | The one file at a fixed path that tells the skills where everything else is: `job-application/konfiguration.md`. |

## LS-2 Wurzel, Konfiguration and Obsidian

1. **Default Wurzel.** `job-application/` in the working directory of the user. The folder is
   git-ignored by default; tracking it in a private, unpublished repository is the user's decision
   (R-6, `lebenslauf-versionen` LV-4).
2. **Override.** `job-application/konfiguration.md` may set the frontmatter key `wurzel: <Pfad>`.
   The path may point to any directory on the local disk, including a folder inside an Obsidian
   vault. Without the key, the default applies.
3. **Anker.** `job-application/konfiguration.md` is the only file at a fixed location. It is read
   first. Every other path is resolved through the Wurzel or through an explicit key of the
   konfiguration (see LS-2.5). Without an Anker, a skill asks for the path once and writes it there.
4. **Repository boundary.** The rule R-9.9 applies to the whole Wurzel, not only to the
   Grundlage. A Wurzel inside a directory tree containing `.claude-plugin/plugin.json` with
   `"name": "claude-job-search"` is refused. A user who works inside this repository sets
   `wurzel` to a path outside it.
5. **Konfiguration content.** Only these frontmatter keys are allowed:

   | Key | Required | Default | Meaning |
   |---|---|---|---|
   | `wurzel` | no | `job-application/` | Root of all application data (LS-2.2). |
   | `grundlage` | no | `<wurzel>/grundlage/lebenslauf-chronologisch.md` | Path of the Datengrundlage: one Markdown file, or a directory of notes (R-9.1). |
   | `grundlage_index` | only with a directory `grundlage` | none | Index note of the directory Grundlage, with `stand` and the Pflegeverlauf (R-9.1, R-9.10). |

   No other key is written by the plugin. Free notes below the frontmatter are kept.

6. **Path resolution.** A relative value of `wurzel`, `grundlage` or `grundlage_index` is resolved against
   the working directory that contains `job-application/konfiguration.md`, not against the directory the
   shell happens to be in. Absolute paths are allowed. Relative paths are recommended when the Wurzel lives
   in a repository, because they stay valid on every checkout (R-9.10).

## LS-3 Layout

```text
<wurzel>/                                   default: job-application/
├── konfiguration.md                        Anker: keys wurzel, grundlage
├── grundlage/
│   └── lebenslauf-chronologisch.md         Datengrundlage: Stammdaten of the person (source of truth)
├── profil.md                               Ableitung of the Grundlage (R-9)
├── rohdaten/                               Raw documents and certificate scans, read-only for skills
│   ├── lebenslauf-2025.pdf
│   ├── zeugnis-musterfirma-2024.pdf
│   └── foto.jpg                            optional, referenced from the Grundlage
├── firmen/                                 Stammdaten and Notizen of companies, one file each (LS-4)
│   └── musterfirma-gmbh.md
├── lebenslauf-basis/                       one Ausprägung without a Vorgang (lebenslauf-versionen LV-1, LV-2)
│   ├── lebenslauf.md                       Arbeitsstand
│   ├── pruefbericht.md                     Auswahl Lebenslauf and Prüfung (LS-7.4)
│   ├── versionen/                          frozen Versionen vNNN_<datum>.md (LV-3)
│   └── export/                             exports of frozen Versionen, vNNN_<datum>.<ext> (LV-2.3)
└── musterfirma-senior-backend/             one Vorgang (LS-6)
    ├── vorgang.md                          Metadaten, status, Plan, Verlauf
    ├── notizen.md                          Notizen of the user, never changed by skills (LS-6.3)
    ├── stellenanzeige.md                   posting text, verbatim
    ├── analyse.md                          requirement match (posting-analysis)
    ├── lebenslauf.md                       Lebenslauf (cv-create)
    ├── anschreiben.md                      cover letter (cover-letter-create)
    ├── email.md                            only when bewerbungsweg is email
    ├── pruefbericht.md                     Auswahl sections and Prüfung (LS-7.4)
    ├── versionen/                          frozen Versionen of this Vorgang's Lebenslauf (LV-3), optional
    └── export/                             PDF, DOCX, HTML, only on request (R-10)
```

Vorgänge sit directly in the Wurzel, next to `grundlage/`, `rohdaten/` and `firmen/`. They are
not nested below a `vorgaenge/` folder, so the paths already used by the skills stay valid.

An **Ausprägung** (`lebenslauf-versionen` LV-1) is the second kind of folder in the Wurzel. It
holds a Lebenslauf variant that is not bound to one Stellenanzeige, for example `lebenslauf-basis/`
or `lebenslauf-teamleitung/`. It carries `lebenslauf.md`, `pruefbericht.md`, `versionen/` and
`export/`, and no `vorgang.md`, `analyse.md` or `anschreiben.md`. A skill tells the two kinds
apart by the presence of `vorgang.md`. A Vorgang may also act as an Ausprägung of its own
(LV-2.2); its Lebenslauf then follows the same version rules.

The Grundlage is either the single file `grundlage/lebenslauf-chronologisch.md` or a directory of
notes, one per Station, named by `grundlage` in the konfiguration (R-9.1). Both forms use the same
hash rule (R-9.5). A directory Grundlage may also live outside the Wurzel, for example in an
Obsidian vault, and then needs `grundlage_index` (LS-2.5).

## LS-4 Persistence of Stammdaten, Metadaten and Notizen

Every Stammdatum, Metadatum and Notiz has exactly one home. A copy elsewhere is a Ableitung,
never a second master.

| Information | Home | Written by | Read by |
|---|---|---|---|
| Kontakt: Name, Anschrift, Telefon, E-Mail, LinkedIn | Grundlage, section *Kontakt* | profile-capture (create), cv-maintain (Pflege) | profile derivation, cv-create, email-create |
| Persönlich: Geburtsdatum, Familienstand, Staatsangehörigkeit, Foto reference | Grundlage, section *Persönlich* | cv-maintain, only with scope `persönlich` (R-9.8) | cv-create, only when the format or the country requires it (R-8.2) |
| Berufliche Stationen with Aufgaben, Ergebnisse, Werkzeuge | Grundlage, section *Berufliche Stationen* | profile-capture, cv-maintain | profile derivation, cv-create (selection, R-9.11) |
| Ausbildung, Schule, Weiterbildung | Grundlage | profile-capture, cv-maintain | profile derivation, cv-create |
| Sprachen (GER level), IT-Kenntnisse, Zielrichtung | Grundlage | profile-capture, cv-maintain | profile derivation, cv-create |
| Zeugnis: file, date, issuer, wording of the closing assessment | Grundlage, section *Zeugnisse* (text); scan in `rohdaten/` | profile-capture, cv-maintain | cv-create (Zeugnis entries), quality-gate (traceability) |
| Rohdokumente: old CVs, notes, LinkedIn export | `rohdaten/` | the user | profile-capture, cv-maintain (intake only) |
| Photo file | `rohdaten/foto.jpg`, linked from the Grundlage | the user | cv-create, only when R-8.2 allows a photo |
| Company Stammdaten: legal name, Rechtsform, Sitz, website, Branche | `firmen/<firma-slug>.md`, frontmatter | posting-analysis (create on first use, update only after user confirmation) | posting-analysis, cover-letter-create, email-create |
| Company Notizen: free text about the company | `firmen/<firma-slug>.md`, body | the user | the user; skills never change it |
| Application Metadaten: firma, stelle, Ref.-Nr., weg, status, dates, grundlage_hash | `vorgang.md`, frontmatter (LS-6.1) | posting-analysis (create), the owning skill per stage, the user for S7 and S8 | every Vorgang skill, quality-gate |
| Application Notizen: free text about one posting, interview, impression | `notizen.md` of the Vorgang (LS-6.3) | the user | the user; skills never change it |
| Contact person of one posting: Anrede, name, function | Vorgang, in `analyse.md` | posting-analysis | cover-letter-create, email-create |
| Profile for the generators | `profil.md`, Ableitung | profile-capture, cv-maintain (re-derive) | posting-analysis, cv-create, cover-letter-create, email-create, quality-gate |
| Wunschprofil: wishes, priorities, Ausschlüsse, Hypothesen (preference, not a fact) | `wunschprofil.md` in the Wurzel, next to the Grundlage; versions kept in `Verlauf` (WJ-5) | traumjob-interview (after confirmation) | fit-check, solution (veto before the plan gate) |
| Passung of one posting against the Wunschprofil | `passung.md`, in the Vorgang folder (WJ-6.4) | fit-check | the user, solution (plan gate) |
| Counterpart and company roles of a Vorgang | `analyse.md`, frontmatter keys (KK-6) and section `## Unternehmen` (UA-5.1); stable firm facts in `firmen/` (UA-5.2) | posting-analysis | cover-letter-create, email-create, solution, quality-gate |
| Ausprägung (Lebenslauf variant without a Vorgang): Arbeitsstand, Versionen, exports | `<wurzel>/<ausprägung>/` (LS-3, `lebenslauf-versionen` LV-2) | cv-create (Arbeitsstand, freeze), export (exports and Manifeste) | cv-create (derive a Vorgang's Lebenslauf from a Version), export, quality-gate |
| Referenzen: name, function, consent of a reference person | Grundlage, section *Referenzen* (optional; an entry exists only with the person's consent) | cv-maintain, on the user's statement | cover-letter-create, only when the posting asks for references (R-5) |

Rules for the table:

1. The Grundlage is the only master for personal facts. `profil.md` is derived from it and carries
   a source reference per entry (R-9.6).
2. The contact person is per posting. It is not stored in `firmen/`, because the person changes
   and a stale name would reach the Anrede (R-3).
3. `firmen/` holds only facts that are stable across postings. Facts from one posting go to that
   Vorgang.
4. Metadaten are structured and machine-read. Notizen are free text and human-read. A fact that
   a skill needs for a document belongs in the Metadaten or the Grundlage, never only in a Notiz.

## LS-5 Invariants

1. **One master per fact.** Person facts live in the Grundlage, company facts in `firmen/`,
   application facts in the Vorgang. Derived files point back to their master.
2. **The Grundlage carries no application state.** It holds no status, no selection, no
   reference to a Vorgang, no Notiz on a posting, and no marks for a posting (R-9.11.6).
3. **A Vorgang never changes the Grundlage.** A Vorgang may change only its own folder.
   The one exception is `firmen/` Stammdaten, which is written as described in LS-4.
4. **Derived files carry the hash of their source.** `profil.md`, `lebenslauf.md`,
   `anschreiben.md` and `vorgang.md` carry `grundlage_hash` (R-9.5). A mismatch makes the file
   stale. It is re-derived, never patched by hand.
5. **Raw material is not modified.** Skills read `rohdaten/` and never write into it.
6. **Notizen are never overwritten.** `notizen.md` and the body of `firmen/<firma-slug>.md` are
   written by the user only. A skill that needs to add something to them asks first and appends
   after confirmation. It never rewrites them.
7. **Only the Wurzel is written.** Skills write nothing outside the Wurzel. The plugin repository
   is never written to.

## LS-6 Vorgang lifecycle (the complete application process)

Every stage of an application is covered. A stage that does not yet have a skill is marked
as manual and still has a fixed place for its data.

| Stage | Trigger | Writes | `status` in `vorgang.md` afterwards |
|---|---|---|---|
| **S0 Vorbereitung** | first use or change of the person's data | `konfiguration.md`, `rohdaten/`, Grundlage, `profil.md` (profile-capture, cv-maintain) | no Vorgang yet |
| **S1 Erfassung** | the user gives a posting | `stellenanzeige.md`, `vorgang.md`, `notizen.md` (created empty) | `erfasst` |
| **S2 Analyse** | posting-analysis | `analyse.md`, `firmen/` (first use), `vorgang.md` | `analysiert` |
| **S3 Plan** | the user approves the plan (solution, plan gate) | `vorgang.md` section *Plan* | `geplant` |
| **S4 Erstellung** | cv-create, cover-letter-create, email-create | `lebenslauf.md`, `anschreiben.md`, `email.md`, `pruefbericht.md` (section *Auswahl*) | `erstellt` |
| **S5 Prüfung** | quality-gate | `pruefbericht.md` (section *Prüfung*) | `geprüft` if zero blockers, otherwise `in Arbeit` |
| **S6 Export** | the user asks for PDF, DOCX or HTML | `export/` | unchanged |
| **S7 Versand** | the user sends the application | `vorgang.md`: `versendet`, `versendet_am`, `weg`, `anhaenge`, `wiedervorlage` (KK-5) | `versendet` |
| **S8 Nachverfolgung** | a reply, an interview, an offer, a negotiation, a decision | `vorgang.md` section *Verlauf*; the user's notes go to `notizen.md` | `rückmeldung`, `gespräch`, `angebot`, `verhandlung`, `zusage`, `absage`, `abgelehnt`, `zurückgezogen` or `ohne Antwort` |
| **S9 Abschluss** | final status reached | `vorgang.md`: `loeschen_ab` for a negative final status (S10) | unchanged; the folder is kept |
| **S10 Aufbewahrung und Löschung** | `loeschen_ab` is reached | the user deletes the Vorgang folder except the files S10 keeps; no skill deletes in Phase 1 | folder removed, or kept with `zusage` |

Rules for the lifecycle:

1. **Status is the current state, Verlauf is the history.** Each change of status adds one line
   to *Verlauf* with the date and a short description. Old lines are never removed.
2. **Status values are fixed.** Only the values in the table are allowed: `erfasst`, `analysiert`,
   `geplant`, `erstellt`, `geprüft`, `in Arbeit`, `versendet`, `rückmeldung`, `gespräch`, `angebot`,
   `verhandlung`, `zusage`, `absage`, `abgelehnt`, `zurückgezogen`, `ohne Antwort`. `absage` is the
   employer's rejection; `abgelehnt` is the candidate's own refusal after an offer or a Zusage.
   Nachfassen (a follow-up message) is a *Verlauf* entry, not a status (KK-5). Free text goes to
   *Verlauf* or `notizen.md`.
3. **Plan before generation.** S3 is written before S4 starts (solution skill, plan gate).
4. **S7 and S8 are user statements.** The skill records what the user reports. It never sends,
   and it never infers a reply.
5. **Folders are never moved after S1.** Links from `firmen/`, the Obsidian graph and the user's
   notes stay valid. Closed Vorgänge are found by status, not by location.
6. **A second Vorgang for the same company and role** gets a numeric suffix:
   `musterfirma-senior-backend-2`.
7. **Phase 1 limit.** No skill updates S7 and S8 in Phase 1. The user maintains `vorgang.md`
   and `notizen.md` by hand or in Obsidian. A tracking skill is an open point (LS-10).
8. **S10 Aufbewahrung und Löschung.** The rule names the place and the period; no skill deletes
   anything in Phase 1.
   - A Vorgang with the final status `absage`, `zurückgezogen`, `ohne Antwort` or `abgelehnt` is
     deleted six months after the date of that status. The user writes the date into
     `loeschen_ab` of `vorgang.md` (LS-6.1) when the final status is set; the field stays empty
     before and for `zusage`.
   - The six months lean on the two-month period of AGG § 15 Abs. 4 for claims plus a reserve for
     service and court delivery. This is a legal reference that the user has to verify; the spec
     does not state it as settled law.
   - A Vorgang with `zusage` is kept without a deletion date.
   - Notes with impressions of third parties (`notizen.md` passages about interviewers, recruiters
     or employees, LS-9.3) are deleted when the Vorgang reaches a final status, whatever the status.
   - The PDFs that were actually sent stay together with their Manifest (`lebenslauf-versionen`
     LV-4), also after the Vorgang folder is deleted; the user moves them to the Ausprägung the
     Lebenslauf came from, or keeps the `export/` folder alone.
   - Firm files in `firmen/` are not covered by S10 (`unternehmensanalyse/en.md` UA-7.2).

### LS-6.1 Metadaten of `vorgang.md`

```yaml
---
firma: Musterfirma GmbH
stelle: Senior Backend-Entwickler
ref_nr: 12345                       # empty when the posting has none
bewerbungsweg: email                # email | portal | post
ausrichtung: ausschreibung          # ausschreibung | initiativ | quereinstieg | berufseinstieg | vermittler
kontaktart: "Direkt: Personalabteilung" # one value of KK-2, set by posting-analysis (KK-6)
stellenquelle: https://…            # or: Text, eingefügt
status: erfasst
erfasst: 2026-10-21
grundlage_hash: <sha256>            # set in S4, see LS-5.4
versendet_am:                       # S7
weg:                                # S7: E-Mail, Portal, Post
anhaenge: []                        # S7: list of file names sent
wiedervorlage:                      # S7: set by the user together with versendet_am, as versendet_am plus the follow-up period of KK-5 (rule 7; empty until sent)
loeschen_ab:                        # S9/S10: date of the final status plus six months; empty for zusage
tags: []                            # free labels, for example for Obsidian search
---
```

Body: `## Plan` (S3), `## Verlauf` (S7 and S8, one line per event).

`kontaktart` duplicates the key of KK-6 in `analyse.md` so that an Obsidian Bases view (LS-8.3)
can show it without reading `analyse.md`; `analyse.md` stays the master and posting-analysis
writes both.

### LS-6.2 Metadaten of `firmen/<firma-slug>.md`

```yaml
---
firma: Musterfirma GmbH
rechtsform: GmbH
sitz: Berlin
website: https://…
aktualisiert: 2026-10-21
tags: []
---
```

Body: `## Notizen`, free Markdown written by the user.

### LS-6.3 Notizen of a Vorgang (`notizen.md`)

1. `notizen.md` is created empty in S1. It has no frontmatter, so it is plain text for the user.
2. The user writes freely: impressions, questions for the interview, contact names from calls,
   reasons for or against the posting, follow-up ideas.
3. Each entry the user adds should start with a date heading `## JJJJ-MM-TT`, so entries stay
   ordered. The spec does not force this form on the user.
4. No skill reads `notizen.md` to produce a document, and no skill writes to it without asking
   first (LS-5.6). A Notiz can be used by the user as a basis for `vorgang.md` Metadaten.

## LS-7 Markdown conventions

1. **Encoding.** UTF-8, LF line endings, one final newline, no byte-order mark.
2. **Frontmatter.** YAML between two `---` lines, at the top of the file. Keys are ASCII
   `snake_case`. Values are text, number, list, or ISO dates `YYYY-MM-DD`. These are the types
   Obsidian Properties shows. No other frontmatter type is used.
3. **Dates.** ISO `YYYY-MM-DD` in frontmatter. `MM/JJJJ` only in the body of a Lebenslauf (R-2).
4. **Pruefbericht sections.** `pruefbericht.md` is written by several skills. Each uses its own
   top-level section: `## Auswahl Lebenslauf` (cv-create, R-9.11.5, CG-2.3),
   `## Auswahl Anschreiben` (cover-letter-create), `## Auswahl Motivationsschreiben`
   (motivation-letter-create) and `## Prüfung` (quality-gate, R-7). A run replaces only its own
   section and keeps the others. No other top-level section is written.
5. **Headings.** One H1 per file as the title. In the Grundlage, each Station is a `###`
   heading in the form of R-2.1, so an anchor link can point to it.
6. **Links.** Standard Markdown links with relative paths, for example
   `[Grundlage](../grundlage/lebenslauf-chronologisch.md)`. Obsidian-only wikilinks (`[[…]]`)
   are not written by skills. Standard links render the same in Obsidian and in any other
   Markdown viewer.
7. **Slugs.** Lowercase ASCII. `ä`→`ae`, `ö`→`oe`, `ü`→`ue`, `ß`→`ss`. Spaces and other
   separators become `-`. A Vorgang folder is `<firma-slug>-<stelle-slug>`, a company file is
   `<firma-slug>.md`.
8. **Original language.** Text in another language stays unchanged and is marked `(EN-Original)`
   (D-1).
9. **Markers.** `[ERGÄNZEN: …]` for missing facts, `[KLÄREN: …]` for contradictions (R-1).
   Markers are plain text, so they stay searchable in Obsidian and in `grep`.

## LS-8 Obsidian

1. **Optional.** The plugin does not need Obsidian. It reads and writes plain Markdown files
   (NFA-3 of `eigene-datengrundlage.md`). Obsidian is one way to read and edit the Wurzel.
2. **Vault as Wurzel.** The Wurzel may be the root of an Obsidian vault, or a subfolder of one.
   Set `wurzel` in the konfiguration to the vault folder. The `.obsidian/` folder is never read
   or written by a skill.
3. **Required plugins.** None. The built-in *Properties* view shows the frontmatter of LS-6.1
   and LS-6.2. Recommended recipe for an overview of all Vorgänge: a built-in *Bases* file
   `bewerbungen.base` in the Wurzel that lists every `vorgang.md` as a table, filtered on
   `status`, with the columns `firma`, `stelle`, `status`, `erfasst`, `versendet_am`,
   `wiedervorlage`, `loeschen_ab`; one view per group of statuses (open, sent, closed). The file
   belongs to the user; no skill reads or writes it, and the spec does not depend on it. The
   optional *Dataview* plugin can do the same.
4. **Attachments.** The vault setting for attachment folder should point to `rohdaten/`, so
   pasted scans and photos land there. This is a recommendation; the spec does not depend on it.
5. **Sync conflicts.** Sync services can create conflict copies, for example
   `lebenslauf-chronologisch (Konflikt).md`. A skill never picks a conflict copy. It reports the
   copy and stops until the user resolves it.
6. **Save formatting.** Obsidian may rewrite frontmatter order or quoting on save. Such a change
   alters the bytes, so the hash changes and the derived files are marked stale. After a
   formatting-only edit, the user re-derives the profile. The stale marker is the intended result.
7. **Backup.** The Wurzel is git-ignored by default; a private repository is allowed (LS-2.1,
   `lebenslauf-versionen` LV-4). The user is the only backup owner for the Grundlage,
   `rohdaten/`, the Vorgänge and their Notizen. The plugin never runs `git add` on the Wurzel.

### LS-8.1 Link map

Links connect the files of the Wurzel. They are written by skills where a file depends on
another file, and the user adds more in `notizen.md` and `firmen/`.

| From | To | Written as | Purpose |
|---|---|---|---|
| `<vorgang>/vorgang.md` | `../firmen/<firma-slug>.md` | `[Musterfirma GmbH](../firmen/musterfirma-gmbh.md)` | company Stammdaten |
| `<vorgang>/vorgang.md` | `../grundlage/lebenslauf-chronologisch.md` | Markdown link | source of the application |
| `<vorgang>/vorgang.md` | own documents in the folder | `[Analyse](analyse.md)`, `[Lebenslauf](lebenslauf.md)`, `[Notizen](notizen.md)` and so on | document flow of the Vorgang |
| `<vorgang>/analyse.md`, `lebenslauf.md` | `../grundlage/…md#<station>` | Markdown link to the `###` heading of a Station (LS-7.5) | traceability of a claim (R-9.6, FA-7) |
| `profil.md` | `grundlage/…md#<station>` | one link per entry | source reference per entry (R-9.6) |
| `grundlage/…md` | `../rohdaten/<datei>` | Markdown link to a scan or certificate | proof of a Zeugnis entry (D-2) |
| `notizen.md`, `firmen/*.md` | any file in the Wurzel | Wikilink (LS-8.3) or Markdown link, free to the user | personal references |

### LS-8.2 Direction of links

1. Links point from a derived or application file **to its master**, never the other way.
   The Grundlage links to no Vorgang and no firm (LS-5.2). `firmen/` links to no Vorgang.
2. The reverse view is not written into files. Obsidian shows it as *Backlinks* and in the
   graph. A Firma therefore lists its Vorgänge in Obsidian without any duplicate maintenance.
3. Result for the graph: the Grundlage and `rohdaten/` are the centre. Each Vorgang hangs off
   the Grundlage and its Firma, and the Firma-Notizen connect several Vorgänge.

### LS-8.3 Link syntax

1. **Skills** write standard Markdown links with relative paths and the `.md` extension
   (LS-7.6). Obsidian resolves them, and they stay correct in any Markdown viewer.
2. **The user** may write Wikilinks in `notizen.md` and in the body of `firmen/`. Wikilinks
   resolve by file name, so they must include the folder. The names `vorgang`, `notizen`,
   `analyse` and `lebenslauf` exist in every Vorgang folder. A bare `[[vorgang]]` is ambiguous.
   Write the path from the Wurzel instead: `[[musterfirma-senior-backend/vorgang]]`.
3. **Obsidian setting.** Set *Files & Links → New link format* to *Relative path to file*, and
   *Use [[Wikilinks]]* to off. Then links created in Obsidian have the same form as the skills'
   links. This is a recommendation; the rules of LS-8.2 hold with any setting.
4. **Uniqueness.** Vorgang folders and Firma files have unique names (LS-6 rule 6, LS-7.7). The
   Vorgang folder name is the key of the Vorgang, so it stays stable after S1 (LS-6 rule 5).

## LS-9 Privacy

1. Zeugnis scans and personal documents stay in `rohdaten/`. The Grundlage holds only the text
   of the closing assessment (D-2).
2. The scans are read during intake and maintenance, and only when the user names them.
   Generators never read `rohdaten/`; they read the Grundlage and the profile.
3. Notizen may contain personal impressions of other people. Skills never quote them in a
   generated document and never send them anywhere.
4. The chat shows section names and findings, not the values of sensitive fields (NFA-P2).
5. Nothing in the Wurzel is published, uploaded or sent to a third party by a skill.
   Export and sending are separate, user-initiated acts (R-6).

## LS-10 Open points and required changes in skills

This specification defines the target state. The skills still implement the earlier state.
The following changes are required before the skills follow the spec:

| Area | Change | Status |
|---|---|---|
| `konfiguration.md` | Accept keys `wurzel`, `grundlage` and `grundlage_index` (LS-2.5); resolve all paths through them against the directory of the Anker (LS-2.6) | done |
| Grundlage hash and `stand` | One hash rule for file and directory Grundlage (R-9.5), computed by `scripts/grundlage_hash.py`; skills call the script instead of `sha256sum` | done |
| Every skill that reads a path | Resolve the Wurzel first, fall back to `job-application/` | done |
| `job-application-posting-analysis` | Save the verbatim posting as `stellenanzeige.md`; create `vorgang.md` (S1) with Metadaten, an empty `notizen.md`, and `firmen/` entries on first use (LS-4) | done |
| `job-application-cv-create`, `job-application-cover-letter-create`, `job-application-motivation-letter-create`, `job-application-quality-gate` | Use the sections of `pruefbericht.md` (LS-7.4) | done |
| `job-application-quality-gate` | Check the status against the existence of the documents; compare `grundlage_hash` in `vorgang.md` | done |
| Nachverfolgung (S7, S8) | No skill in Phase 1. A tracking skill is a later requirement | open, deliberate |
| S10 Löschung | Rule defined (LS-6 rule 8, `loeschen_ab`); no skill deletes. The legal reference (AGG § 15 Abs. 4) is to be verified by the user | rule defined, no skill |
| Ausprägung folders | Second folder kind in LS-3; `cv-create` and `export` tell it apart by the missing `vorgang.md` | done (skill, 0.2.0) |
| `kontaktart` in `vorgang.md` | posting-analysis writes the KK-6 value into `vorgang.md` as well (LS-6.1) | done (skill, 0.2.0) |
| Dogfooding in this repository | Requires `wurzel` outside the repository (LS-2.4) | decision for the user |

## Related rules

- R-6 (Datenschutz) refers to this document for the location of the working folder.
- R-9.10 (Konfiguration) is extended by LS-2.5.
- R-9.1 (Location of the Grundlage) resolves relative to the Wurzel (LS-2).
