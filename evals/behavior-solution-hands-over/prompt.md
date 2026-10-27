---
description: For an application that is already sent, the router generates nothing and names the follow-up skill.
tags: [behavior, no-bash]
plugins: ["../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, Bash, Write, Edit]
---

Schreib mir bitte die Bewerbung für die Beispielstelle bei der Musterfirma GmbH.
