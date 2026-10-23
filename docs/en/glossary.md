# Glossary

The German terms are the ones used in the skills, the file names and the specs. They are kept
in German on purpose, so what you read in the chat matches what you find on disk.

**Datengrundlage (Grundlage)**
: Your personal facts in Markdown: stations, education, skills, languages, certificates, each
  with its source. The single source of truth. One file or a directory of notes; nothing else
  may invent a fact.

**Profil (Ableitung)**
: `profil.md`, derived from the Datengrundlage with a source reference per entry. The
  generators read it. It is regenerated, never edited by hand.

**Wunschprofil**
: Your wishes, priorities and vetoes for the next position, recorded by the preference
  interview in `wunschprofil.md`. A preference, not a fact; it never enters a document.

**Wurzel**
: The root folder of all your application data, by default `job-application/`. Skills write
  nowhere else.

**Anker (konfiguration.md)**
: `job-application/konfiguration.md`, the only file at a fixed place. It names the Wurzel and
  the Datengrundlage; every other path is resolved through it.

**Vorgang**
: One application for one posting, from intake to closure, in its own folder under the Wurzel.
  Holds the posting, the analysis, the documents, the check report and `vorgang.md`.

**Ausprägung**
: A Lebenslauf variant with its own focus, reused across applications, for example
  `lebenslauf-basis/`. A folder next to the Vorgänge with `lebenslauf.md`, `pruefbericht.md`,
  `versionen/` and `export/`.

**Version**
: A frozen copy of a Lebenslauf in `versionen/`, never edited again. Exports are made from a
  Version, so the sent PDF can be rebuilt byte for byte.

**Stammdaten**
: Facts that hold across applications: yours in the Datengrundlage, a company's in
  `firmen/<company>.md`. Recorded once, reused in every Vorgang.

**Metadaten**
: Structured facts about one Vorgang or one company in the frontmatter (`status`, dates,
  reference number). Skills read and write them.

**Notizen**
: Your free text about a Vorgang (`notizen.md`) or a company. Skills read them and never change
  them.

**Hash / stale**
: Every derived file records a hash of the Datengrundlage it came from. When the Datengrundlage
  changes, the hash no longer matches and the file is *stale*: it is regenerated, not patched.

**Plan-Gate**
: The moment the front door shows the plan for an application and waits for your approval. No
  document is written before you say yes.

**Quality Gate**
: The check before sending: blockers, warnings and notes. An application with blockers is not
  ready; its status is `in Arbeit`, otherwise `geprüft`.

**Kontaktart**
: The kind of counterpart you deal with: employer directly (HR, department, management),
  Personalberatung or Headhunter, Personalvermittlung or Zeitarbeit, referral, job platform, or
  unclear. It decides what you disclose and when, see [Counterparts](counterparts.md).
