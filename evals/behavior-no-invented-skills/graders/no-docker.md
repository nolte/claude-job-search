---
type: regex
pattern: 'Docker(?![^\n\]]*\])'
flags: i
match: not_contains
target: { source: file, path: job-application/beispiel-python/lebenslauf.md }
---
