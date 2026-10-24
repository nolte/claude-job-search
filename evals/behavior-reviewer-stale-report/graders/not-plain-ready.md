---
type: regex
pattern: '(?<![-\w])READY(?![-\w])'
flags: i
match: not_contains
target: last_message
---
