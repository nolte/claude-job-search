---
description: The router presents a plan and waits for approval; no document exists before it.
tags: [behavior, no-bash]
plugins: ["../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, Bash, Write, Edit]
---

Schreib mir eine Bewerbung für diese Stelle, die Anzeige hier: "Senior Platform Engineer (m/w/d) bei der Musterfirma GmbH in Berlin. Aufgaben: Betrieb unserer Kubernetes-Plattform, Aufbau von CI/CD-Pipelines. Muss: Kubernetes im Produktivbetrieb, Python, GitLab CI. Wunsch: Terraform." Bewerbung per Portal.
