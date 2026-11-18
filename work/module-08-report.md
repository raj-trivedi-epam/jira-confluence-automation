# Module 08 Completion Report

## Tracked Files
jira-dashboard-requirements.md
notes.md
project_spec.md
work/module-03-report.md
work/module03-task

## Spec Commit History
6b82f86 Initial commit

## project_spec.md Contents
# Cloud Project Weekly Stakeholder Status Generator

**Status:** Draft technical specification  
**Project root:** Current workspace root  
**Audience:** Delivery Manager, internal leadership, and client stakeholders

## 1. Purpose

Create a weekly generator that reads delivery data from Jira Cloud and produces a concise Markdown status report for the 12-person Cloud Project team. The report is for stakeholder review and must not be shared automatically.

Jira project setup is in scope. No project, board, integration, or generator has been created as part of this specification.

## 2. Confirmed requirements

### Jira project

- Create a **company-managed Jira Cloud project** named **Cloud Project**.
- Preferred project key: **CLOUD**, subject to availability and organizational naming rules.
- Use Scrum with two-week sprints.
- Use story points for estimation.
- Include these issue types: Epic, Story, and Task.
- Use the workflow: **To Do → In Progress → Done**.
- Grant team access through the existing Jira group **Cloud_project**.
- Client and leadership stakeholders receive the reviewed report only; they do not receive Jira project access under this requirement.

### Report generation

- Generate weekly on **Friday at 3:00 PM Asia/Kolkata**.
- Cover a **rolling seven-day** reporting period.
- Run on the Delivery Manager’s local computer.
- If a scheduled run is missed, run it once when the computer is next available, if supported by the scheduler.
- Produce Markdown under `reports/`, keeping a dated file for each run, using the proposed name `weekly-status-report-YYYY-MM-DD.md`.
- A person reviews the report before sharing it. Do not email or publish it automatically.

### Report audience and contents

Produce one report suitable for both internal leadership and client stakeholders. Keep it aggregate-only and business-focused. Include:

- Executive summary.
- Completed work.
- In-progress work.
- Upcoming work.
- Blockers and risks.
- Sprint progress.

Do not include per-person comparisons, raw Jira comments, or issue-level details in the shared report.

### Integration and failure behavior

- Use Jira Cloud OAuth with read-only access.
- If Jira is unavailable or required data is missing, make a bounded retry, report failure, and leave the previous report untouched.
- Failure notification channel is undecided.

## 3. Proposed technical approach

These are implementation proposals, not additional confirmed requirements.

- Implement the generator in Python as a command-line program.
- Use Jira Cloud REST APIs to read project, sprint, issue, status, estimate, and resolution data. Use changelog data where needed to determine when work changed.
- Store OAuth configuration and refresh credentials in the operating system’s secure credential store. Never put credentials in source files, generated reports, or logs.
- Use the macOS scheduler available on the target computer (for example, `launchd`) for the weekly run. Confirm catch-up behavior on that computer before relying on it.
- Paginate Jira API requests, respect rate limits, use bounded retries for transient errors, and avoid logging sensitive issue content.
- Write the dated report atomically only after all required data has been validated.
- Log run time, success/failure, and actionable error details locally. Do not add an external notification integration unless one is approved.

## 4. Proposed report rules

The following rules fill gaps that need confirmation during implementation:

- Count work as completed when its resolution falls within the rolling seven-day period and it is still resolved at report generation time. Reopened issues are not counted as completed.
- Summarize progress for the active sprint at generation time, alongside seven-day delivery activity.
- Aggregate by status and story points. Clearly identify issues with missing estimates rather than treating missing estimates as zero.
- Do not infer blockers from comments or issue wording. Blocker reporting requires an agreed Jira field, flag, or label.
- If a requested metric cannot be calculated from available Jira data, state that it is unavailable; do not fabricate or silently substitute a value.
- Include the report period and generation timestamp in Asia/Kolkata time.

## 5. Proposed report structure

1. Report period and generation timestamp.
2. Executive summary.
3. Completed work in the last seven days.
4. Current in-progress work.
5. Upcoming work.
6. Active sprint progress, including story-point totals where available.
7. Blockers and risks, based only on the agreed Jira blocker marker.

Keep the content concise and suitable for both audiences. Use aggregate counts and estimates; omit issue keys, individual names, and detailed issue summaries.

## 6. Open items and dependencies

1. Confirm that the `CLOUD` project key is available and permitted, and that the requester or Jira administrator can create a company-managed project.
2. Confirm the exact Jira Cloud OAuth flow, app registration, approved read-only scopes, and secure local credential storage.
3. Identify the existing Jira group exactly as `Cloud_project` and confirm it contains the intended 12 team members. Confirm which project roles it should receive.
4. Define the Jira field, flag, or label that marks a blocker. Until then, blocker reporting cannot be reliably populated.
5. Confirm how the Scrum board and sprint will be created or associated with the new project.
6. Confirm the target computer’s scheduler supports the requested Friday schedule and one-time catch-up behavior.
7. Decide whether failures need a notification beyond a local log and failed run status.
8. Confirm the proposed completion, active-sprint, missing-estimate, and report naming rules before implementation.

## 7. Acceptance criteria

- The project is created only after the project key, permissions, group membership, board, and workflow are verified.
- The generator reads Jira data using approved read-only OAuth permissions.
- A successful scheduled or manual run creates a dated Markdown report with the required sections and reporting period.
- The shared report contains aggregates only and is not automatically distributed.
- Missing data and blockers are clearly identified; no progress is invented.
- A failed run leaves existing reports unchanged and exposes a useful failure status.
