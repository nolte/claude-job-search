# Keep your data and CVs current

**Goal:** keep the Datengrundlage correct as your career moves on, and reuse CVs with a focus
across applications.

**Example:** You changed roles at Beispiel AG, finished a certification and now apply both for
specialist and for lead positions.

## Maintain the Datengrundlage

```text
/claude-job-search:job-application-cv-maintain
```

The skill checks the required core points and inconsistencies in your Datengrundlage (gaps
between stations, missing dates, contradicting statements) and asks **only about the findings**.
Each confirmed answer goes into the file; every change is logged in the Pflegeverlauf. At the
end it reports the hash of the Grundlage. Skills that build on it compare this hash and tell
you when `profil.md` is out of date.

New raw material (a fresh certificate, an updated LinkedIn export) goes into `rohdaten/`;
`job-application-cv-maintain` processes it first (read only, the raw files are never changed).
Afterwards it offers to re-derive `profil.md` and hands over to
`job-application-profile-capture`; you decide whether to accept.

## CV variants

A **variant** is a Lebenslauf with its own focus that you reuse. Ask the CV skill for it:

```text
Lege eine Variante "teamleitung" an: Schwerpunkt Führung und Projektverantwortung.
```

Each variant has a folder (for example `lebenslauf-teamleitung/`) with its `lebenslauf.md`,
its `pruefbericht.md`, the frozen versions in `versionen/` and their exports in `export/`.
A Vorgang that needs a changed Lebenslauf takes a version of a variant as a read-only starting
point and writes the result into its own Vorgang folder; the variant itself stays unchanged. No skill edits a frozen version or deletes one without your
request.

## Freeze a version before you send

When the CV skill finishes, it asks whether this state is the one to send. If you confirm, it
copies the document to `versionen/v<NNN>_<date>.md`. A frozen version is never edited. The
next change raises the version number, so you can always show exactly what a recipient
received. Exports can be rebuilt from their manifest
(`task export -- --reproduce <file>.manifest.json`) and compared with the original.

## What remains

The updated Datengrundlage with its Pflegeverlauf, `profil.md`, and per variant the working
copy, the frozen versions and the exports.

## Rhythm

A short `cv-maintain` run after every significant change, and before a larger series of
applications, keeps the later steps fast: the posting analysis finds no stale profile and the
quality gate has fewer findings.
