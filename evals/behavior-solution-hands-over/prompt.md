---
description: For an application that is already sent, the router generates nothing and points to the follow-up skill.
tags: [behavior, no-bash]
plugins: ["../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, Bash, Write, Edit]
---

Ich habe meine Bewerbung bei der Musterfirma GmbH gestern abgeschickt. Wie geht es mit dieser Bewerbung jetzt weiter?
