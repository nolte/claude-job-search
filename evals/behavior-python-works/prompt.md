---
description: Precondition 2 of 2. python3 must run inside the eval sandbox because the skills call python3 scripts. It fails when the sandbox runs no external programs at all.
tags: [precondition]
plugins: ["../.."]
runs: 1
max_turns: 4
timeout_seconds: 120
allowed_tools: [Read, Glob, Grep, Bash]
---

Führe mit Bash genau diesen Befehl aus: `python3 --version`. Gib danach die Ausgabe wörtlich wieder.
