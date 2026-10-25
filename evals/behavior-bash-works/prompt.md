---
description: Precondition 1 of 2. An external command must run inside the eval sandbox (echo alone is a shell builtin and proves nothing), otherwise every case that runs a command measures the machine, not the plugin.
tags: [precondition]
plugins: ["../.."]
runs: 1
max_turns: 4
timeout_seconds: 120
allowed_tools: [Read, Glob, Grep, Bash]
---

Führe mit Bash genau diesen Befehl aus: `uname -s`. Gib danach die Ausgabe wörtlich wieder.
