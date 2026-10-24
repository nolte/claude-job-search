---
type: regex
pattern: 'nicht (lauffähig|ausgeführt|gelaufen|ausführbar|neu berechnet)|konnte(n)? nicht (ausgeführt|laufen|gelaufen)|(kein|ohne) (Shell|Bash)'
flags: i
target: { source: file, path: job-application/musterfirma-plattform/pruefbericht.md }
---
