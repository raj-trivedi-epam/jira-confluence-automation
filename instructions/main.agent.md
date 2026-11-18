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
