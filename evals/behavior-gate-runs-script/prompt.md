---
description: The quality gate runs scripts/cv_checks.py before it writes the report (skill step "Automated checks").
tags: [behavior]
plugins: ["../.."]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, Bash, Write, Edit]
---

Ist meine Bewerbung im Ordner job-application/musterfirma-plattform versandfertig? Bitte prüfe sie.
