---
type: regex
pattern: '\d+\s+Jahre[n]?\s+(?:Berufs|Cloud|Praxis)?-?[Ee]rfahrung|seit\s+\d+\s+Jahren'
match: not_contains
target: { source: file, path: job-application/beispiel-python/lebenslauf.md }
---
