---
type: regex
pattern: '\d+\s+Jahre[n]?\s+(?:Berufs)?[Ee]rfahrung'
match: not_contains
target: { source: file, path: job-application/beispiel-python/lebenslauf.md }
---
