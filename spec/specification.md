# Feature Specification: Jira/Confluence Automation

**Status:** Clarified prototype specification
**Owner:** Delivery Manager
**Constitution:** [constitution.md](./constitution.md)
**Source specification:** [project_spec.md](../project_spec.md)
**Dashboard reference:** [jira-dashboard-requirements.md](../jira-dashboard-requirements.md)

## 1. Overview

Build a local-first Jira/Confluence automation web application for the Cloud Project. The system retrieves Jira delivery data, prepares an aggregate-only weekly stakeholder status report, supports human review, and records operational status for scheduled and manual runs.

The implemented prototype will use:

- React 18 and Vite for the frontend
- Node.js and Express for the backend
- PostgreSQL 15 in Docker for persistence
- Jira Cloud REST APIs for read-only delivery data
- A scheduler-independent worker entry point for scheduled execution; `launchd` integration is deferred

The first implementation priority is the weekly status workflow. Confluence publishing is not in the initial scope and must not be implemented or enabled without separate requirements and authorization.

## 2. Problem Statement

The Delivery Manager manually gathers Jira project, sprint, status, estimate, and blocker information for leadership and client reporting. The process must be repeatable, fail safely, preserve prior reports, and avoid exposing issue-level or personal information.

The application must make source data gaps explicit rather than guessing or treating missing estimates as zero.

## 3. Goals

- Generate a concise, reviewed stakeholder status report every Friday at 3:00 PM Asia/Kolkata.
- Support a manual report-generation path and the same underlying logic for scheduled runs.
- Read approved Jira Cloud project and sprint data using least-privilege OAuth.
- Preserve aggregate-only reporting and human review before sharing.
- Leave the previous report unchanged after a failed generation.
- Surface missing data, authentication problems, API errors, and operational status clearly.
- Persist operational metadata and review state in PostgreSQL 15.

## 4. Non-Goals

- Creating or modifying a Jira project, Scrum board, project permissions, or project configuration.
- A 15-minute sprint dashboard or assignee-level reporting.
- Granting Jira project access or changing Jira permissions.
- Providing issue-level detail or per-person comparisons in stakeholder reports.
- Automatically emailing, publishing, or otherwise distributing reports.
- Automatically updating or publishing Confluence pages.
- Selecting a manual reporting period other than the current rolling seven-day period.
- Automated missed-run catch-up, external report distribution, and Jira failure notifications.
- A multi-user application authentication system; the prototype is local and single-operator.
- Inferring blocker status from comments or issue text.
- Inventing missing metrics or substituting values for unavailable Jira fields.

## 5. Personas

### Delivery Manager

Creates and reviews reports, diagnoses failed runs, and decides whether a report is ready to share.

### Internal Leadership

Reviews the final aggregate report and intervenes when a commitment or sprint is at risk.

### Client Stakeholder

Receives only a reviewed aggregate report. The stakeholder does not receive Jira access under this specification.

### System Operator

Starts or stops the application, checks local logs, manages credentials, and verifies scheduled runs.

## 6. User Scenarios

### US-01: Configure Jira integration

**As** a Delivery Manager,
**I want** to provide approved Jira configuration and establish read-only OAuth,
**so that** the app can retrieve project and sprint data securely.

**Acceptance criteria**

- The system does not require or accept Jira credentials in source files or browser storage.
- OAuth configuration and secure credential storage are validated before report access.
- The UI shows whether required configuration is missing or invalid.
- Jira requests use the project key and read-only scopes approved for the workflow.

### US-02: Generate a report manually

**As** a Delivery Manager,
**I want** to generate a report for the current rolling reporting period,
**so that** I can prepare a stakeholder update on demand.

**Acceptance criteria**

- The manual action uses the same generation pipeline as scheduled runs.
- The reporting period is seven rolling days ending at the generation time.
- Generation times and report dates use Asia/Kolkata.
- A new report is written only after required data and validation checks pass.
- The UI reports success, failure, and the resulting report path without exposing issue-level data.

### US-03: Review a generated report

**As** a Delivery Manager,
**I want** to inspect a generated Markdown report before sharing it,
**so that** I can verify its facts and remove or resolve any reporting issue.

**Acceptance criteria**

- The report uses the required aggregate sections.
- The UI presents overall status, completed work, in-progress work, upcoming work, sprint progress, blockers and risks, decisions/support needed, and data notes as applicable.
- The UI allows the reviewer to mark a report as reviewed or unreviewed.
- Marking a report reviewed does not automatically distribute or publish it.
- No issue keys, assignee names, raw comments, or individual comparisons are included in the stakeholder report.

### US-04: Schedule a weekly report

**As** a System Operator,
**I want** a scheduler-compatible report worker,
**so that** reports are prepared consistently.

**Acceptance criteria**

- The scheduler-independent worker entry point is available for future `launchd` integration.
- When invoked by a scheduler, the worker uses the same generation service as manual generation.
- Automated missed-run catch-up is out of scope.
- A worker run records timestamp, outcome, and any non-sensitive error details.

### US-05: Handle unavailable or incomplete Jira data

**As** a Delivery Manager,
**I want** a failed or incomplete fetch to be identified clearly,
**so that** I do not mistakenly share a misleading report.

**Acceptance criteria**

- Transient Jira failures use a bounded retry policy.
- Missing estimates are displayed as unavailable or missing rather than zero.
- Required metrics that cannot be calculated include a limitation in data notes.
- Authentication, permission, rate-limit, and source-data failures are distinguishable.
- A failed run does not replace or corrupt an existing report.

### US-06: Inspect run history

**As** a System Operator,
**I want** to view recent generation attempts and their outcomes,
**so that** I can diagnose failed scheduled or manual runs.

**Acceptance criteria**

- PostgreSQL stores run start, end, trigger type, status, and a safe summary of the outcome.
- Sensitive Jira payloads and OAuth tokens are not stored or logged.
- The UI can distinguish successful, skipped, and failed runs.
- A successful run can link to the generated report record and output path.

## 7. Functional Requirements

### FR-01: Jira project setup validation

- The system must validate or display validation status for the Jira site, project key, Scrum board, group, and permissions before live data retrieval.
- The preferred project key is `CLOUD`, but the system must not assume it is available or allowed.
- Project setup must use a company-managed Jira project, Epic/Story/Task issue types, and the `To Do -> In Progress -> Done` workflow.

### FR-02: Jira read-only OAuth

- The system must support approved Jira Cloud OAuth read-only access.
- The system must support token refresh if the selected OAuth flow requires it.
- Credentials and refresh tokens must remain outside browser code and source control.
- The system must clearly report missing consent, expired authorization, and insufficient permissions.

### FR-03: Jira data retrieval

- The system must retrieve project metadata, active sprint data, issue status, story points, resolution state, and lifecycle timestamps needed for reporting.
- It must retrieve changelog data when needed to establish report-period transitions.
- It must paginate all relevant API collections.
- It must respect rate limits and use bounded retries for transient failures.

### FR-04: Reporting period

- The normal reporting period is the rolling seven days ending at generation time.
- The interval is `[generationTime - 7 days, generationTime]`, with the end exclusive.
- Convert Jira timestamps to UTC for comparison and render them in Asia/Kolkata.
- Manual regeneration creates a dated revision; it does not silently overwrite prior content.
- Both the period and generation timestamp must be formatted in Asia/Kolkata.
- The active sprint snapshot must be captured at the same generation time.

### FR-05: Completion logic

- Work is completed only when resolved during the reporting period and remains resolved at report time.
- Reopened issues must be excluded from completed totals.
- Completion requires Jira Done status category plus a resolution timestamp or validated resolution changelog transition.
- Missing resolution evidence fails the issue for completion rather than counting or estimating it.

### FR-06: Sprint aggregation

- Sprint progress must use project story-point values.
- Committed, completed, and remaining story points must be calculated independently.
- The `JIRA_STORY_POINTS_FIELD_ID` configuration value is required; no alternate field fallback is allowed.
- Committed points come from the active-sprint snapshot.
- Completed points include only completed issues that are members of that snapshot.
- Remaining points equal committed points minus completed points after validation.
- Missing estimates must remain visible as unavailable data, not zero.
- If sprint or estimate data is unavailable, the report must say so in `Sprint Progress` or `Data Notes`.

### FR-07: Blocker and risk reporting

- The system must accept an agreed Jira blocker field, flag, or label as configuration.
- Blockers must be derived only from that agreed marker.
- The report must include impact and the available mitigation or next-update information.
- If no blocker marker is confirmed, blocker reporting must state that it is unavailable.
- The UI/report must distinguish confirmed blockers, no confirmed blockers, marker not configured, and blocker data unavailable.

### FR-08: Report structure

Every generated report must include:

1. Reporting period
2. Generation timestamp and time zone
3. Overall status
4. Executive Summary
5. Delivery Update
   - Completed
   - In Progress
   - Upcoming
6. Sprint Progress
7. Blockers and Risks
8. Decisions or Support Needed
9. Data Notes

The report must distinguish verified facts, forecasts, decisions, missing data, and risks.

### FR-09: Report rendering and writing

- Reports must use Markdown and the existing template conventions.
- Report filenames must use `weekly-status-report-YYYY-MM-DD.md`, with the date in Asia/Kolkata.
- A same-day revision uses `weekly-status-report-YYYY-MM-DD-rNN.md`.
- Reports must be written atomically so a failure cannot truncate or replace a prior report.
- A report may be created only after data validation and required report fields pass.

### FR-10: Human review

- Reports must remain local and require a human review state.
- The application must not email or publish generated reports.
- A review action must record reviewer, timestamp, and review status without storing unnecessary source issue data.
- The local OS account is the prototype reviewer identity. No role model or remote application login is required.
- Review remains reversible until external sharing is implemented.

### FR-11: Scheduling

- The prototype must expose a scheduler-independent worker entry point.
- Automated `launchd` configuration and missed-run catch-up are out of scope.
- Scheduled and manual runs must share a single generation pipeline.

### FR-12: Operational logging

- Log run start, completion, trigger, status, duration, and actionable non-sensitive errors.
- Do not log raw Jira comments, personal issue details, credentials, or access tokens.
- A run history API must expose enough information for local troubleshooting.

### FR-13: PostgreSQL persistence

PostgreSQL 15 must persist only data needed for configuration, report records, review state, and run history.

The application must use migrations for schema changes and parameterized database access.
PostgreSQL runs in Docker on loopback; migrations run explicitly, a named volume persists local data, and database credentials do not enter source or image files.

### FR-14: Confluence boundary

- No Confluence content shall be read or updated in the initial scope.
- A future Confluence integration must define target space/page, OAuth scopes, publication approval, and conflict handling before implementation.

## 8. Web Application Requirements

### 8.1 Frontend

- React 18 with Vite
- Dashboard showing integration status and recent run history
- Manual report-generation action
- Report preview and review controls
- Missing-data and failure explanations
- No credential entry or secret display in the browser
- No issue-level stakeholder report content

### 8.2 Backend

- Node.js and Express
- Input validation on all API boundaries
- Explicit routes for configuration status, report generation, report review, and run history
- Jira integration isolated behind a service interface
- Report aggregation, rendering, and persistence separated into distinct modules
- Least-privilege OAuth and secure credential storage

### 8.3 Database

- PostgreSQL 15 via Docker for local development
- Migration-backed schema
- Parameterized queries or an approved migration-compatible ORM
- Secret values stored outside the database unless the selected secure credential provider requires a protected reference

## 9. API and Error Requirements

The application must expose these prototype backend APIs:

- `GET /api/configuration/status`
- `PATCH /api/configuration` for non-secret configuration only
- `GET /api/runs`
- `POST /api/runs`
- `GET /api/reports/:id`
- `POST /api/reports/:id/review`

Every API response must:

- Use stable JSON shapes
- Distinguish success, validation error, authentication error, upstream error, and internal error
- Avoid returning Jira payloads or sensitive issue data
- Preserve safe details needed for operator troubleshooting

Generation and review operations must be idempotent or provide explicit concurrency behavior for repeated submissions.
Express and Vite bind to `127.0.0.1`. The prototype is one trusted local operator and requires no remote login or role model. State-changing API methods are loopback-only; if cookies are introduced, CSRF protection is required.

## 10. Data Entities

### JiraConfiguration

- UUID primary key
- Jira site URL
- Project key
- Board ID
- OAuth provider reference
- Blocker marker field or label
- Time zone
- Validation status
- Updated timestamp
- OAuth secrets are held only in the selected secure credential provider

### Report

- UUID primary key
- Associated run ID
- Reporting period start
- Reporting period end
- Generation timestamp
- Overall status
- Markdown content or storage path
- Data notes
- Review status
- Reviewer
- Review timestamp
- Canonical Markdown file path

### RunRecord

- UUID primary key
- Start and end timestamps
- Trigger type: manual or scheduled
- Start and end timestamps
- Status: success, skipped, or failed
- Safe error category
- Safe error summary
- Associated report ID

## 11. Dependencies and Assumptions

### Dependencies

- Jira Cloud project, board, and read-only OAuth must be approved.
- The target macOS computer must support the desired `launchd` schedule.
- PostgreSQL 15 must run locally through Docker.
- React 18 and Vite must provide the frontend build.
- Node.js and Express must provide the backend.
- Secure local credential storage must be selected and validated.

### Assumptions

- The project key, if available, is proposed as `CLOUD`.
- The team has 12 intended members.
- The Jira group is named `Cloud_project`.
- Reports use an aggregate-only stakeholder format.
- The blocker marker and notification behavior remain open until confirmed.

## 12. Open Decisions

External setup decisions still need confirmation before live Jira use:

1. The Jira site and project key are available and permitted.
2. The Jira administrator approves OAuth 2.0 3LO and read-only scopes.
3. The project has the intended 12-member `Cloud_project` group and the required read-only project role.
4. The Jira Scrum board ID and active-sprint behavior are confirmed.
5. The Jira story-point custom field ID is confirmed.
6. The blocker field, field ID, or label is confirmed.

The following items are deliberately resolved as prototype constraints:

- Node.js/Express supersedes the original Python CLI proposal.
- Confluence integration and sprint-dashboard features are out of scope.
- macOS Keychain stores OAuth credentials.
- The app is loopback-only and has one local operator.
- Markdown files are canonical report artifacts; PostgreSQL stores metadata and paths.
- Manual and scheduled workers use a rolling seven-day period only.
- Automated catch-up and external distribution are out of scope.

## 13. Security and Privacy Requirements

- Keep secrets outside source control and browser code.
- Use least-privilege OAuth scopes.
- Validate server-side authorization and input.
- Use parameterized database access.
- Do not log issue keys, issue summaries, raw comments, assignee names, tokens, or credentials.
- Exclude per-person and issue-level detail from stakeholder reports.
- Require separate approval before any Confluence read or write integration.

## 14. Reliability and Failure Requirements

- Retry only transient failures and cap the retry count.
- Check required data before producing or replacing a report.
- Write reports atomically.
- Preserve the prior successful report after any failed run.
- Use Asia/Kolkata consistently for scheduling and report filenames.
- Return a useful local status while avoiding sensitive upstream payloads.

## 15. Test Requirements

The implementation must include:

- Unit tests for configuration parsing and validation
- Unit tests for date range, Asia/Kolkata conversion, report naming, and sprint progress
- Unit tests for completion logic and reopened issues
- Unit tests for missing estimates and unavailable metrics
- Unit tests for blocker-marker handling
- Mocked Jira API tests for pagination, project metadata, active sprint data, status transitions, resolution data, and rate limits
- Retry and authentication failure tests
- PostgreSQL migration and persistence tests
- Frontend behavior tests for configuration, run status, report preview, and review state
- API contract tests for generation and run-history endpoints
- Atomic-write tests proving that failed generation leaves prior reports unchanged

## 16. Success Criteria

The feature is successful when:

- A successful manual or scheduled run creates a dated Markdown report with every required section.
- Report content remains aggregate-only and contains no issue keys, raw comments, assignee names, or individual comparisons.
- The 7-day and active-sprint calculations agree with approved Jira data.
- Missing estimates and unavailable metrics are explicitly marked instead of invented or set to zero.
- Failure paths leave the prior report untouched.
- The run history identifies success, skip, and failure outcomes.
- A human can review the report before sharing.
- The system does not email or publish reports automatically.
- PostgreSQL 15 persists configuration metadata, report records, review state, and run history in local Docker.
- The React/Vite frontend and Express backend operate without exposing credentials or privileged Jira operations to the browser.

## 17. Acceptance Checklist

- [ ] Jira project key and board dependencies are confirmed.
- [ ] Jira OAuth and secure credential storage are configured and tested.
- [ ] Blocker marker is confirmed.
- [ ] Report period and active sprint rules are implemented and tested.
- [ ] Missing estimates are surfaced as unavailable.
- [ ] Reopened issues are excluded from completion totals.
- [ ] Report writing is atomic and failure-safe.
- [ ] Human review is required before sharing.
- [ ] Manual and scheduled generation use the same pipeline.
- [ ] Scheduler behavior is validated.
- [ ] Run history and safe operational logs are available.
- [ ] Confluence publishing remains disabled.
- [ ] Complete test and acceptance review passes.
