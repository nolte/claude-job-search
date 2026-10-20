# Skills and agents

| Name | Phase | Purpose |
|---|---|---|
| `job-application-solution` | plan | Front door: profile, analysis, plan approval, documents, quality gate |
| `job-application-profile-capture` | intake | Builds the Datengrundlage and derives `job-application/profil.md` from it |
| `job-application-posting-analysis` | analyse | Extracts requirements and matches them to the profile with evidence |
| `job-application-cv-create` | create | Single-column German CV in the format chosen for the situation |
| `job-application-cv-maintain` | intake | Guided maintenance interview for an existing Datengrundlage: checks core points, asks about findings |
| `job-application-cover-letter-create` | create | One-page DIN-style cover letter, four variants |
| `job-application-email-create` | deliver | Cover e-mail, subject, attachment list and file names |
| `job-application-export` | deliver | Exports a finished document to PDF (LaTeX), DOCX, HTML or Markdown via `task export` |
| `job-application-quality-gate` | review | Quality gate: blockers, warnings, notes |
| `job-application-reviewer` (agent) | review | Read-only whole-set review from a recruiter's perspective |
