---
type: regex
pattern: 'Ergebnis:\s*BLOCKIERT'
match: not_contains
target: { source: file, path: job-application/musterfirma-plattform/pruefbericht.md }
---
