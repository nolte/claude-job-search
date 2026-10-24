---
description: A natural request must lead to the skill job-application-export.
tags: [trigger]
plugins: ["../.."]
runs: 1
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
---

Exportiere meinen fertigen Lebenslauf als PDF.
