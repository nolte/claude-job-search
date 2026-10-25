---
type: regex
pattern: '(cv_checks|Skript)[^\n]{0,60}(ohne Befund|0 Blocker|keine Befunde|bestanden|erfolgreich)'
flags: i
match: not_contains
target: { source: file, path: job-application/musterfirma-plattform/pruefbericht.md }
---
