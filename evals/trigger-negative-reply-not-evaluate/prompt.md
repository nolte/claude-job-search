---
description: A single reply from an employer must lead to job-application-follow-up and not to the evaluation across applications (should-not-trigger case for the split of the two skills).
tags: [trigger]
plugins: ["../.."]
runs: 1
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
---

Die Musterfirma GmbH hat mir gerade eine Einladung zum Gespräch geschickt. Trag das bitte in den Vorgang ein.
