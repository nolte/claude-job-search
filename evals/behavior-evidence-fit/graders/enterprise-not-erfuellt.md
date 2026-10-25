---
type: regex
pattern: '(?m)^\|[^\n]*Enterprise[^\n]*\|\s*erfüllt\s*\|'
match: not_contains
target: { source: file, path: job-application/beispiel-fit/analyse.md }
---
