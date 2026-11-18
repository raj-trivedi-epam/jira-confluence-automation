# Weekly Status Generator Backlog

This backlog translates the project specification into actionable implementation tasks. It follows the requested phase structure and is tuned to the selected MVP-first delivery approach: prioritize building the generator around a confirmed Jira project while allowing some integration and validation work to overlap early.

## Phase 1: Setup

- [ ] Confirm Jira project key availability and naming rules for `CLOUD` and verify a company-managed Jira Cloud project can be created.
- [ ] Confirm the target Jira group is exactly `Cloud_project` and verify its membership contains the intended 12 team members.
- [ ] Confirm the Jira project roles and permissions needed for delivery-manager read-only access and stakeholder-safe reporting.
- [ ] Confirm the Scrum board setup, sprint cadence, and the association between the new project, sprint schedule, and reporting windows.
- [ ] Verify workflow configuration: `To Do -> In Progress -> Done` and ensure Epic, Story, and Task issue types exist.
- [ ] Validate the team’s Jira access model and ensure client/leadership stakeholders do not need Jira access for report review.
- [ ] Create the repository structure for the Python CLI app, configuration files, and reports output directory.
- [ ] Define the local project layout for source code, tests, credentials handling, logs, and generated report files.
- [ ] Create a baseline Python environment and dependency manifest for the CLI app, HTTP client, secure storage integration, and date/time handling.
- [ ] Decide the local secure credential storage strategy (for example macOS Keychain) and document the exact OAuth configuration flow.
- [ ] Confirm the target computer scheduler (`launchd`) supports the Friday 3:00 PM Asia/Kolkata schedule and one-time catch-up behavior.
- [ ] Define the failure-notification approach for missed runs, including whether a local log and failed-run status is sufficient.
- [ ] Confirm the exact Jira blocker field/flag/label that will be used for risk reporting before implementation depends on it.
- [ ] Confirm the completion logic, sprint reporting rules, missing-estimate handling, and naming convention for generated reports before the app is locked in.

## Phase 2: Core Features

- [ ] Scaffold the CLI entry point for running a manual report and a scheduled run path.
- [ ] Implement configuration loading for local settings, report naming, time zone, and output paths.
- [ ] Implement secure credential retrieval and a credential refresh workflow for Jira OAuth read-only access.
- [ ] Build a Jira API client abstraction for project metadata, sprint data, issue data, status transitions, and changelog retrieval.
- [ ] Implement pagination and request throttling for Jira REST API calls with bounded retries for transient errors.
- [ ] Model Jira data needed by the report: project metadata, active sprint, statuses, story points, resolution state, and issue lifecycle timestamps.
- [ ] Implement logic to fetch the rolling seven-day report range in Asia/Kolkata time and align it with the weekly schedule.
- [ ] Implement aggregation for completed work over the reporting window and ensure reopened issues are excluded from completion totals.
- [ ] Implement aggregation for in-progress and upcoming work using current Jira status and active sprint context.
- [ ] Implement sprint progress calculations including story-point totals and missing-estimate handling without fabricating values.
- [ ] Build the blocker/risk reporting path using only the agreed Jira blocker indicator and clearly show unavailable metrics when data is absent.
- [ ] Implement the report content model for executive summary, completed work, in-progress work, upcoming work, blockers/risks, and sprint progress.
- [ ] Build the Markdown report template with aggregate-only business language and no issue-level details.
- [ ] Implement date and timestamp formatting in `Asia/Kolkata` for the report period and generation time.
- [ ] Implement safe handling for missing or malformed Jira fields, including explicit “unavailable” reporting rather than silent substitution.
- [ ] Ensure the generator only writes a report after all required data has passed validation checks.
- [ ] Add local logging for runtime, success/failure, and actionable errors without exposing sensitive issue details.

## Phase 3: Integration

- [ ] Connect the report generator to the confirmed Jira project data sources and validate access using read-only OAuth.
- [ ] Validate the end-to-end data flow from Jira API responses to internal aggregation logic and final Markdown output.
- [ ] Implement the scheduling integration for the target machine using `launchd`, including the weekly Friday 3:00 PM trigger.
- [ ] Implement catch-up behavior for missed scheduled runs if the scheduler supports it, otherwise document the limitation clearly.
- [ ] Implement atomic report output writing to `reports/weekly-status-report-YYYY-MM-DD.md` so a failed run does not corrupt or replace the previous report.
- [ ] Ensure failures leave any prior successful report untouched and expose a useful failure status to the operator.
- [ ] Implement a bounded retry strategy for transient Jira outages and short-lived read failures.
- [ ] Implement graceful failure handling for unavailable Jira data, authentication issues, and incomplete metrics without producing misleading report content.
- [ ] Add a local review gate so the generated Markdown report is inspected by a person before sharing externally.
- [ ] Ensure the app does not email, publish, or share the report automatically.
- [ ] Validate the command-line invocation path for both manual and scheduled runs using the same underlying generator logic.
- [ ] Add operational logging and a local status signal that clearly distinguishes successful, skipped, and failed runs.

## Phase 4: Testing

- [ ] Create unit tests for configuration parsing, timezone conversion, report date range logic, and file naming.
- [ ] Create unit tests for aggregation rules: completed work, in-progress work, upcoming work, sprint progress, and missing estimates.
- [ ] Create unit tests for blocker handling, unavailable metrics, and the “do not fabricate values” requirement.
- [ ] Create unit tests for report rendering and required Markdown sections, ensuring aggregate-only output without issue-level detail.
- [ ] Create mocked Jira API tests covering project metadata, sprint data, issue transitions, resolution data, pagination, and rate-limit handling.
- [ ] Add retry-path tests for transient failures, authentication problems, and partial data loss.
- [ ] Add atomic-write tests to confirm a failed generation does not overwrite an existing report.
- [ ] Add regression tests for reopened issues so they are excluded from completed work totals.
- [ ] Add validation tests for missing estimate fields and blocked metrics to ensure they are surfaced as unavailable rather than zero or guessed.
- [ ] Run a local smoke test that produces a sample weekly report from mocked Jira data and verifies the final file is written under `reports/`.
- [ ] Validate the scheduled-run path on the target machine or equivalent environment and confirm the trigger and catch-up behavior.
- [ ] Perform a failure-mode test where Jira is unavailable and confirm the app exits cleanly without modifying previous reports.

## Phase 5: Documentation

- [ ] Write a project README with overview, setup instructions, and expected run behavior.
- [ ] Document the Jira project setup requirements, including company-managed project creation, key selection, board, sprint, issue types, and workflow validation.
- [ ] Document the local OAuth and secure credential-storage process for Jira read-only access.
- [ ] Document the report generation flow, output folder, naming conventions, and review-before-share process.
- [ ] Document operational behavior for retries, missing data, blocker handling, and failure-safe report writing.
- [ ] Write a runbook for the Delivery Manager covering manual execution, scheduled execution, and recovery from a failed run.
- [ ] Document how to inspect local logs and how to interpret a failed run status.
- [ ] Add a troubleshooting section for common Jira API, authorization, and scheduling issues.
- [ ] Document the exact stakeholder-facing report rules and the limits of the generated output so team members understand what is intentionally omitted.
- [ ] Document the decision record for blocker reporting and any unresolved assumptions that still require confirmation.
- [ ] Finalize a lightweight implementation checklist for release readiness and sign-off.

## Recommended order for execution

1. Setup and Jira verification
2. Core generator and aggregation logic
3. End-to-end integration with Jira and scheduler
4. Testing and failure-mode validation
5. Documentation and release readiness

This backlog is intentionally structured to support the selected MVP-first priority: build the generator around a confirmed Jira setup, then validate and document the operational flow before broader rollout.
