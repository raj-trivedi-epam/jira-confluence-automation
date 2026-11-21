# Instructions Catalog

Each entry below is an instruction file with a one-line description.

- [`./instructions/creating-instructions.agent.md`](./creating-instructions.agent.md) — Instructions for creating and maintaining the project instruction and skill infrastructure.
  + Keywords: create instruction, update instruction, add instruction, create skill, instruction catalog, Copilot prompts, Cursor rules, Claude commands
  + Target: `instructions/**/*`, `.github/**/*`, `.cursor/**/*`, `.claude/**/*`

- [`./instructions/create-status-report.agent.md`](./create-status-report.agent.md) — Instructions for generating weekly status reports.
  + Keywords: status report, weekly report, stakeholder report, report generation
  + Target: `reports/**/*.md`, `weekly_status/**/*.py`

- [`./instructions/update-confluence-page.agent.md`](./update-confluence-page.agent.md) — Instructions for safely transforming project status reports and updating a Confluence page.
  + Keywords: Confluence, Confluence page, update page, publish status, project status page
  + Target: `reports/**/*.md`, `work/**/*.md`

- [`./instructions/calculate-compound-interest.agent.md`](./calculate-compound-interest.agent.md) — Instructions for invoking the compound interest calculation tool and presenting its results.
  + Keywords: compound interest, calculate interest, investment growth, compounding
  + Target: `tools/compound_interest.py`

- [`./instructions/use-status-report-skill.agent.md`](./use-status-report-skill.agent.md) — Instructions for invoking the Jira issue Markdown status report skill.
  + Keywords: Jira status report, format issues, weekly status, skill status report
  + Target: `tools/skill_status_report.py`
