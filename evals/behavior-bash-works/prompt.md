---
description: Precondition. Bash must work inside the eval sandbox, otherwise the cases that run scripts (behavior-gate-runs-script) measure the machine, not the plugin.
tags: [precondition]
plugins: ["../.."]
runs: 1
max_turns: 4
timeout_seconds: 120
allowed_tools: [Read, Glob, Grep, Bash]
---

Führe mit Bash den Befehl `python3 --version` aus. Gib danach die Ausgabe wörtlich wieder.
