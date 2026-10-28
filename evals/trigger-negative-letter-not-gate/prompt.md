---
description: A request for the cover letter must lead to job-application-cover-letter-create and not to the quality gate or the router (should-not-trigger case for the skill boundary).
tags: [trigger]
plugins: ["../.."]
runs: 1
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
---

Schreib mir bitte nur das Anschreiben für die Stelle als Senior Platform Engineer bei der Musterfirma GmbH; Lebenslauf und Analyse liegen schon vor.
