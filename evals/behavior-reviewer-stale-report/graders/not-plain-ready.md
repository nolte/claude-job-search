---
type: regex
pattern: 'Verdict:\s*READY\s*$|Ergebnis:\s*BEREIT\s*$'
flags: im
match: not_contains
target: last_message
---
