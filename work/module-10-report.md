# Module 10 Completion Report

## Instruction Files
instructions/create-status-report.agent.md
instructions/creating-instructions.agent.md
instructions/main.agent.md
instructions/update-confluence-page.agent.md

## main.agent.md Contents
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

## Sample Instruction
- File: update-confluence-page.agent.md
- Contents:
# Confluence Project Status Page Update Instructions

- Accept input as:
  + A Confluence page URL or page ID.
  + A project status report in Markdown.
  + Optional `title`, `parent page ID`, and `dry-run` values.
- Require page URL or page ID and status report content before processing.
  + Use `dry-run: true` as the default for every update.
  + Treat an explicit, separate publish request as approval to update the live page.
- Read the status report completely before transforming or publishing it.
- Validate required report fields: reporting period, overall status, executive summary, delivery update, blockers and risks, and data notes.
- Preserve aggregate-only stakeholder-safe content.
  + Omit issue keys, issue summaries, comments, individual names, and person-level comparisons.
  + Do not invent missing data, estimates, sprint progress, blockers, or decisions.
  + Mark unavailable or missing information explicitly.
- Convert the Markdown report into Confluence Storage Format.
- Preserve the report structure and order:
  + Page title.
  + Reporting period and generation timestamp.
  + Overall status.
  + Executive summary.
  + Delivery update.
  + Sprint progress.
  + Blockers and risks.
  + Decisions or support needed.
  + Data notes.
- Convert headings, bullets, links, and tables to valid Confluence Storage Format elements.
  + Render status values as text with explicit `Green`, `Amber`, or `Red` labels.
  + Preserve the source report's concise line and section structure.
- Resolve the existing page and fetch its current version before updating.
- Compare transformed content with the existing page body.
  + Skip the update when content is unchanged.
  + Report a version conflict and stop if the page changes during update preparation.
- In `dry-run` mode:
  + Return the target page, proposed title, and transformed Confluence Storage Format preview.
  + Report which content sections changed.
  + Do not call a write API or modify credentials, page permissions, labels, or attachments.
- In publish mode:
  + Use the Confluence REST API with a read-write token or approved OAuth credential.
  + Request the smallest permitted scope.
  + Update only the page body and optional title; do not alter permissions or metadata unless explicitly requested.
  + Increment the page version using the latest current version.
  + Verify the saved page after the update.
- Return a concise result containing:
  + `mode`: `dry-run`, `published`, `unchanged`, or `failed`.
  + `pageId`, `pageTitle`, and `pageUrl`.
  + `previousVersion` and `newVersion` when published.
  + `changedSections` and `warnings`.
  + A short success or failure summary.
- On failure, return:
  + The failed operation.
  + A non-sensitive error reason.
  + Whether the page was changed.
  + The bounded retry count used.
- Use bounded retries only for transient authentication, timeout, and rate-limit failures.
  + Do not retry validation or permission failures.
  + Leave the page unchanged after a pre-update validation failure.
- Never write credentials, tokens, cookies, private issue content, or sensitive headers to source files, logs, reports, or chat output.
- Do not use comments, Jira issue wording, or inferred data to identify blockers.
- Do not publish by default and do not send page notifications or broadcast links unless explicitly requested.
- Do not create or replace a page unless the input explicitly permits page creation or replacement.
