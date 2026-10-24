---
description: The reviewer does not inherit a BEREIT report when the document holds an open placeholder.
tags: [behavior, no-bash]
plugins: ["../.."]
runs: 3
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent, AskUserQuestion]
---

Mach bitte ein kritisches Gesamtreview meiner Bewerbung im Ordner job-application/musterfirma-plattform vor dem Versand.
