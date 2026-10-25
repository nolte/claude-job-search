---
description: A natural request must lead to the skill job-application-quality-gate.
tags: [trigger]
plugins: ["../.."]
runs: 1
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
---

Ist meine Bewerbung bei der Musterfirma GmbH versandfertig? Bitte prüfe die Unterlagen.
