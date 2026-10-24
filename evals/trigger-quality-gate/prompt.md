---
description: A natural request must lead to the skill job-application-quality-gate.
tags: [trigger]
plugins: ["../.."]
runs: 1
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
---

Ist meine Bewerbung im Ordner job-application/musterfirma versandfertig? Bitte prüfe sie.
