---
type: regex
pattern: '(?m)^\|[^\n]*Orchestrier[^\n]*\|\s*nicht belegt\s*\|'
match: not_contains
target: { source: file, path: job-application/beispiel-fit/analyse.md }
---
