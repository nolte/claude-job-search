---
type: regex
pattern: '(?<!\[(?:ERGÄNZEN|KLÄREN)[^\n\]]*)Terraform'
flags: i
match: not_contains
target: { source: file, path: job-application/beispiel-python/lebenslauf.md }
---
