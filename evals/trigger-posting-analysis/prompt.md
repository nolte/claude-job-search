---
description: A natural request must lead to the skill job-application-posting-analysis.
tags: [trigger]
plugins: ["../.."]
runs: 1
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
---

Kannst du diese Stellenanzeige für mich analysieren? "Senior Platform Engineer (m/w/d) bei der Musterfirma GmbH in Berlin. Muss: Kubernetes im Produktivbetrieb, Python, GitLab CI. Wunsch: Terraform."
