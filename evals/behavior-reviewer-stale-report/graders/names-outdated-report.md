---
type: regex
pattern: '(Bericht|Protokoll|BEREIT)[^\n]{0,160}(veraltet|nicht aktuell|überholt|unzuverlässig|nicht verlässlich)|(veraltet|nicht aktuell|überholt|unzuverlässig|nicht verlässlich)[^\n]{0,160}(Bericht|Protokoll|BEREIT)'
flags: i
target: last_message
---
