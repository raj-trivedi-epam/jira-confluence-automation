# Module 17 Completion Report

## Specification Contents
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

## Commit History
0a35ae6 module 17
f1a0723 module 17
f270d6e spec files
9ed7ad5 chore: project skeleton for prototype
4fbc6fe module 15
bc9e2e6 backlog
4abf5f8 add project README
1efc24c all pending changes
f4e3d19 added skill related files
c2a24f9 module 11
fa94428 module 10 commit
661665c module 9
6b82f86 Initial commit

## Commit Count
13

## Project Files
.env.example
.github/copilot-instructions.md
.github/prompts/to-create-instructions.prompt.md
.github/prompts/to-create-status-report.prompt.md
.github/prompts/to-update-confluence-page.prompt.md
.gitignore
.mcp.json
.vscode/mcp.json
.vscode/settings.json
AGENTS.md
README.md
TODO.md
apps/api/package.json
apps/api/src/config/jira.ts
apps/api/src/jobs/generateWeeklyReport.ts
apps/api/src/routes/.gitkeep
apps/api/src/server.ts
apps/api/src/services/credentials/.gitkeep
apps/api/src/services/jira/.gitkeep
apps/api/src/services/reporting/.gitkeep
apps/web/index.html
apps/web/node_modules/.bin/nanoid
apps/web/node_modules/.bin/rolldown
apps/web/node_modules/.bin/tsc
apps/web/node_modules/.bin/vite
apps/web/node_modules/.package-lock.json
apps/web/node_modules/.vite/deps/_metadata.json
apps/web/node_modules/.vite/deps/package.json
apps/web/node_modules/.vite/deps/react-DgVJeC5g.js
apps/web/node_modules/.vite/deps/react-DgVJeC5g.js.map
apps/web/node_modules/.vite/deps/react-dom_client.js
apps/web/node_modules/.vite/deps/react-dom_client.js.map
apps/web/node_modules/.vite/deps/react.js
apps/web/node_modules/.vite/deps/react_jsx-dev-runtime.js
apps/web/node_modules/.vite/deps/react_jsx-dev-runtime.js.map
apps/web/node_modules/@oxc-project/types/LICENSE
apps/web/node_modules/@oxc-project/types/README.md
apps/web/node_modules/@oxc-project/types/package.json
apps/web/node_modules/@oxc-project/types/types.d.ts
apps/web/node_modules/@rolldown/binding-darwin-arm64/README.md
apps/web/node_modules/@rolldown/binding-darwin-arm64/package.json
apps/web/node_modules/@rolldown/binding-darwin-arm64/rolldown-binding.darwin-arm64.node
apps/web/node_modules/@rolldown/pluginutils/LICENSE
apps/web/node_modules/@rolldown/pluginutils/README.md
apps/web/node_modules/@rolldown/pluginutils/dist/filter-DvHMSB82.mjs
apps/web/node_modules/@rolldown/pluginutils/dist/filter/index.d.mts
apps/web/node_modules/@rolldown/pluginutils/dist/filter/index.mjs
apps/web/node_modules/@rolldown/pluginutils/dist/index.d.mts
apps/web/node_modules/@rolldown/pluginutils/dist/index.mjs
apps/web/node_modules/@rolldown/pluginutils/package.json
apps/web/node_modules/@typescript/typescript-darwin-arm64/LICENSE
apps/web/node_modules/@typescript/typescript-darwin-arm64/NOTICE.txt
apps/web/node_modules/@typescript/typescript-darwin-arm64/README.md
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.decorators.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.decorators.legacy.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.dom.asynciterable.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.dom.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.dom.iterable.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.collection.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.core.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.generator.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.iterable.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.promise.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.proxy.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.reflect.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.symbol.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2015.symbol.wellknown.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2016.array.include.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2016.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2016.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2016.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.arraybuffer.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.date.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.object.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.sharedmemory.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.string.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2017.typedarrays.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2018.asyncgenerator.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2018.asynciterable.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2018.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2018.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2018.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2018.promise.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2018.regexp.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2019.array.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2019.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2019.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2019.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2019.object.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2019.string.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2019.symbol.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.bigint.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.date.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.number.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.promise.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.sharedmemory.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.string.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2020.symbol.wellknown.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2021.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2021.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2021.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2021.promise.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2021.string.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2021.weakref.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2022.array.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2022.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2022.error.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2022.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2022.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2022.object.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2022.regexp.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2022.string.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2023.array.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2023.collection.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2023.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2023.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2023.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.arraybuffer.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.collection.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.object.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.promise.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.regexp.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.sharedmemory.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2024.string.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2025.collection.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2025.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2025.float16.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2025.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2025.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2025.iterator.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2025.promise.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es2025.regexp.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es5.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.es6.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.array.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.collection.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.date.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.decorators.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.disposable.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.error.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.full.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.intl.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.sharedmemory.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.temporal.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.esnext.typedarrays.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.scripthost.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.webworker.asynciterable.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.webworker.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.webworker.importscripts.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/lib.webworker.iterable.d.ts
apps/web/node_modules/@typescript/typescript-darwin-arm64/lib/tsc
apps/web/node_modules/@typescript/typescript-darwin-arm64/package.json
apps/web/node_modules/@vitejs/plugin-react/LICENSE
apps/web/node_modules/@vitejs/plugin-react/README.md
apps/web/node_modules/@vitejs/plugin-react/dist/index.d.ts
apps/web/node_modules/@vitejs/plugin-react/dist/index.js
apps/web/node_modules/@vitejs/plugin-react/dist/reactCompilerBabelPreset.d.ts
apps/web/node_modules/@vitejs/plugin-react/dist/reactCompilerBabelPreset.js
apps/web/node_modules/@vitejs/plugin-react/dist/refresh-runtime.js
apps/web/node_modules/@vitejs/plugin-react/package.json
apps/web/node_modules/@vitejs/plugin-react/types/optionalTypes.d.ts
apps/web/node_modules/@vitejs/plugin-react/types/preamble.d.ts
apps/web/node_modules/detect-libc/LICENSE
apps/web/node_modules/detect-libc/README.md
apps/web/node_modules/detect-libc/index.d.ts
apps/web/node_modules/detect-libc/lib/detect-libc.js
apps/web/node_modules/detect-libc/lib/elf.js
apps/web/node_modules/detect-libc/lib/filesystem.js
apps/web/node_modules/detect-libc/lib/process.js
apps/web/node_modules/detect-libc/package.json
apps/web/node_modules/fdir/LICENSE
apps/web/node_modules/fdir/README.md
apps/web/node_modules/fdir/dist/index.cjs
apps/web/node_modules/fdir/dist/index.d.cts
apps/web/node_modules/fdir/dist/index.d.mts
apps/web/node_modules/fdir/dist/index.mjs
apps/web/node_modules/fdir/package.json
apps/web/node_modules/lightningcss-darwin-arm64/LICENSE
apps/web/node_modules/lightningcss-darwin-arm64/README.md
apps/web/node_modules/lightningcss-darwin-arm64/lightningcss.darwin-arm64.node
apps/web/node_modules/lightningcss-darwin-arm64/package.json
apps/web/node_modules/lightningcss/LICENSE
apps/web/node_modules/lightningcss/README.md
apps/web/node_modules/lightningcss/node/ast.d.ts
apps/web/node_modules/lightningcss/node/ast.js.flow
apps/web/node_modules/lightningcss/node/browserslistToTargets.js
apps/web/node_modules/lightningcss/node/composeVisitors.js
apps/web/node_modules/lightningcss/node/flags.js
apps/web/node_modules/lightningcss/node/index.d.ts
apps/web/node_modules/lightningcss/node/index.js
apps/web/node_modules/lightningcss/node/index.js.flow
apps/web/node_modules/lightningcss/node/index.mjs
apps/web/node_modules/lightningcss/node/targets.d.ts
apps/web/node_modules/lightningcss/node/targets.js.flow
apps/web/node_modules/lightningcss/package.json
apps/web/node_modules/nanoid/LICENSE
apps/web/node_modules/nanoid/README.md
apps/web/node_modules/nanoid/async/index.browser.cjs
apps/web/node_modules/nanoid/async/index.browser.js
apps/web/node_modules/nanoid/async/index.cjs
apps/web/node_modules/nanoid/async/index.d.cts
apps/web/node_modules/nanoid/async/index.d.ts
apps/web/node_modules/nanoid/async/index.js
apps/web/node_modules/nanoid/async/index.native.js
apps/web/node_modules/nanoid/async/package.json
apps/web/node_modules/nanoid/bin/nanoid.cjs
apps/web/node_modules/nanoid/index.browser.cjs
apps/web/node_modules/nanoid/index.browser.js
apps/web/node_modules/nanoid/index.cjs
apps/web/node_modules/nanoid/index.d.cts
apps/web/node_modules/nanoid/index.d.ts
apps/web/node_modules/nanoid/index.js
apps/web/node_modules/nanoid/nanoid.js
apps/web/node_modules/nanoid/non-secure/index.cjs
apps/web/node_modules/nanoid/non-secure/index.d.ts
apps/web/node_modules/nanoid/non-secure/index.js
apps/web/node_modules/nanoid/non-secure/package.json
apps/web/node_modules/nanoid/package.json
apps/web/node_modules/nanoid/url-alphabet/index.cjs
apps/web/node_modules/nanoid/url-alphabet/index.js
apps/web/node_modules/nanoid/url-alphabet/package.json
apps/web/node_modules/picocolors/LICENSE
apps/web/node_modules/picocolors/README.md
apps/web/node_modules/picocolors/package.json
apps/web/node_modules/picocolors/picocolors.browser.js
apps/web/node_modules/picocolors/picocolors.d.ts
apps/web/node_modules/picocolors/picocolors.js
apps/web/node_modules/picocolors/types.d.ts
apps/web/node_modules/picomatch/LICENSE
apps/web/node_modules/picomatch/README.md
apps/web/node_modules/picomatch/index.js
apps/web/node_modules/picomatch/lib/constants.js
apps/web/node_modules/picomatch/lib/parse.js
apps/web/node_modules/picomatch/lib/picomatch.js
apps/web/node_modules/picomatch/lib/scan.js
apps/web/node_modules/picomatch/lib/utils.js
apps/web/node_modules/picomatch/package.json
apps/web/node_modules/picomatch/posix.js
apps/web/node_modules/postcss/LICENSE
apps/web/node_modules/postcss/README.md
apps/web/node_modules/postcss/lib/at-rule.d.ts
apps/web/node_modules/postcss/lib/at-rule.js
apps/web/node_modules/postcss/lib/comment.d.ts
apps/web/node_modules/postcss/lib/comment.js
apps/web/node_modules/postcss/lib/container.d.ts
apps/web/node_modules/postcss/lib/container.js
apps/web/node_modules/postcss/lib/css-syntax-error.d.ts
apps/web/node_modules/postcss/lib/css-syntax-error.js
apps/web/node_modules/postcss/lib/declaration.d.ts
apps/web/node_modules/postcss/lib/declaration.js
apps/web/node_modules/postcss/lib/document.d.ts
apps/web/node_modules/postcss/lib/document.js
apps/web/node_modules/postcss/lib/fromJSON.d.ts
apps/web/node_modules/postcss/lib/fromJSON.js
apps/web/node_modules/postcss/lib/input.d.ts
apps/web/node_modules/postcss/lib/input.js
apps/web/node_modules/postcss/lib/lazy-result.d.ts
apps/web/node_modules/postcss/lib/lazy-result.js
apps/web/node_modules/postcss/lib/list.d.ts
apps/web/node_modules/postcss/lib/list.js
apps/web/node_modules/postcss/lib/map-generator.js
apps/web/node_modules/postcss/lib/no-work-result.d.ts
apps/web/node_modules/postcss/lib/no-work-result.js
apps/web/node_modules/postcss/lib/node.d.ts
apps/web/node_modules/postcss/lib/node.js
apps/web/node_modules/postcss/lib/parse.d.ts
apps/web/node_modules/postcss/lib/parse.js
apps/web/node_modules/postcss/lib/parser.js
apps/web/node_modules/postcss/lib/postcss.d.mts
apps/web/node_modules/postcss/lib/postcss.d.ts
apps/web/node_modules/postcss/lib/postcss.js
apps/web/node_modules/postcss/lib/postcss.mjs
apps/web/node_modules/postcss/lib/previous-map.d.ts
apps/web/node_modules/postcss/lib/previous-map.js
apps/web/node_modules/postcss/lib/processor.d.ts
apps/web/node_modules/postcss/lib/processor.js
apps/web/node_modules/postcss/lib/result.d.ts
apps/web/node_modules/postcss/lib/result.js
apps/web/node_modules/postcss/lib/root.d.ts
apps/web/node_modules/postcss/lib/root.js
apps/web/node_modules/postcss/lib/rule.d.ts
apps/web/node_modules/postcss/lib/rule.js
apps/web/node_modules/postcss/lib/stringifier.d.ts
apps/web/node_modules/postcss/lib/stringifier.js
apps/web/node_modules/postcss/lib/stringify.d.ts
apps/web/node_modules/postcss/lib/stringify.js
apps/web/node_modules/postcss/lib/symbols.js
apps/web/node_modules/postcss/lib/terminal-highlight.js
apps/web/node_modules/postcss/lib/tokenize.js
apps/web/node_modules/postcss/lib/warn-once.js
apps/web/node_modules/postcss/lib/warning.d.ts
apps/web/node_modules/postcss/lib/warning.js
apps/web/node_modules/postcss/package.json
apps/web/node_modules/react-dom/LICENSE
apps/web/node_modules/react-dom/README.md
apps/web/node_modules/react-dom/cjs/react-dom-client.development.js
apps/web/node_modules/react-dom/cjs/react-dom-client.production.js
apps/web/node_modules/react-dom/cjs/react-dom-profiling.development.js
apps/web/node_modules/react-dom/cjs/react-dom-profiling.profiling.js
apps/web/node_modules/react-dom/cjs/react-dom-server-legacy.browser.development.js
apps/web/node_modules/react-dom/cjs/react-dom-server-legacy.browser.production.js
apps/web/node_modules/react-dom/cjs/react-dom-server-legacy.node.development.js
apps/web/node_modules/react-dom/cjs/react-dom-server-legacy.node.production.js
apps/web/node_modules/react-dom/cjs/react-dom-server.browser.development.js
apps/web/node_modules/react-dom/cjs/react-dom-server.browser.production.js
apps/web/node_modules/react-dom/cjs/react-dom-server.bun.development.js
apps/web/node_modules/react-dom/cjs/react-dom-server.bun.production.js
apps/web/node_modules/react-dom/cjs/react-dom-server.edge.development.js
apps/web/node_modules/react-dom/cjs/react-dom-server.edge.production.js
apps/web/node_modules/react-dom/cjs/react-dom-server.node.development.js
apps/web/node_modules/react-dom/cjs/react-dom-server.node.production.js
apps/web/node_modules/react-dom/cjs/react-dom-test-utils.development.js
apps/web/node_modules/react-dom/cjs/react-dom-test-utils.production.js
apps/web/node_modules/react-dom/cjs/react-dom.development.js
apps/web/node_modules/react-dom/cjs/react-dom.production.js
apps/web/node_modules/react-dom/cjs/react-dom.react-server.development.js
apps/web/node_modules/react-dom/cjs/react-dom.react-server.production.js
apps/web/node_modules/react-dom/client.js
apps/web/node_modules/react-dom/client.react-server.js
apps/web/node_modules/react-dom/index.js
apps/web/node_modules/react-dom/package.json
apps/web/node_modules/react-dom/profiling.js
apps/web/node_modules/react-dom/profiling.react-server.js
apps/web/node_modules/react-dom/react-dom.react-server.js
apps/web/node_modules/react-dom/server.browser.js
apps/web/node_modules/react-dom/server.bun.js
apps/web/node_modules/react-dom/server.edge.js
apps/web/node_modules/react-dom/server.js
apps/web/node_modules/react-dom/server.node.js
apps/web/node_modules/react-dom/server.react-server.js
apps/web/node_modules/react-dom/static.browser.js
apps/web/node_modules/react-dom/static.edge.js
apps/web/node_modules/react-dom/static.js
apps/web/node_modules/react-dom/static.node.js
apps/web/node_modules/react-dom/static.react-server.js
apps/web/node_modules/react-dom/test-utils.js
apps/web/node_modules/react/LICENSE
apps/web/node_modules/react/README.md
apps/web/node_modules/react/cjs/react-compiler-runtime.development.js
apps/web/node_modules/react/cjs/react-compiler-runtime.production.js
apps/web/node_modules/react/cjs/react-compiler-runtime.profiling.js
apps/web/node_modules/react/cjs/react-jsx-dev-runtime.development.js
apps/web/node_modules/react/cjs/react-jsx-dev-runtime.production.js
apps/web/node_modules/react/cjs/react-jsx-dev-runtime.profiling.js
apps/web/node_modules/react/cjs/react-jsx-dev-runtime.react-server.development.js
apps/web/node_modules/react/cjs/react-jsx-dev-runtime.react-server.production.js
apps/web/node_modules/react/cjs/react-jsx-runtime.development.js
apps/web/node_modules/react/cjs/react-jsx-runtime.production.js
apps/web/node_modules/react/cjs/react-jsx-runtime.profiling.js
apps/web/node_modules/react/cjs/react-jsx-runtime.react-server.development.js
apps/web/node_modules/react/cjs/react-jsx-runtime.react-server.production.js
apps/web/node_modules/react/cjs/react.development.js
apps/web/node_modules/react/cjs/react.production.js
apps/web/node_modules/react/cjs/react.react-server.development.js
apps/web/node_modules/react/cjs/react.react-server.production.js
apps/web/node_modules/react/compiler-runtime.js
apps/web/node_modules/react/index.js
apps/web/node_modules/react/jsx-dev-runtime.js
apps/web/node_modules/react/jsx-dev-runtime.react-server.js
apps/web/node_modules/react/jsx-runtime.js
apps/web/node_modules/react/jsx-runtime.react-server.js
apps/web/node_modules/react/package.json
apps/web/node_modules/react/react.react-server.js
apps/web/node_modules/rolldown/LICENSE
apps/web/node_modules/rolldown/README.md
apps/web/node_modules/rolldown/THIRD-PARTY-LICENSE
apps/web/node_modules/rolldown/bin/cli.mjs
apps/web/node_modules/rolldown/dist/cli.d.mts
apps/web/node_modules/rolldown/dist/cli.mjs
apps/web/node_modules/rolldown/dist/config.d.mts
apps/web/node_modules/rolldown/dist/config.mjs
apps/web/node_modules/rolldown/dist/experimental-index.d.mts
apps/web/node_modules/rolldown/dist/experimental-index.mjs
apps/web/node_modules/rolldown/dist/experimental-runtime-types.d.ts
apps/web/node_modules/rolldown/dist/experimental-runtime.d.ts
apps/web/node_modules/rolldown/dist/experimental-runtime.mjs
apps/web/node_modules/rolldown/dist/filter-index.d.mts
apps/web/node_modules/rolldown/dist/filter-index.mjs
apps/web/node_modules/rolldown/dist/get-log-filter.d.mts
apps/web/node_modules/rolldown/dist/get-log-filter.mjs
apps/web/node_modules/rolldown/dist/index.d.mts
apps/web/node_modules/rolldown/dist/index.mjs
apps/web/node_modules/rolldown/dist/parallel-plugin-worker.d.mts
apps/web/node_modules/rolldown/dist/parallel-plugin-worker.mjs
apps/web/node_modules/rolldown/dist/parallel-plugin.d.mts
apps/web/node_modules/rolldown/dist/parallel-plugin.mjs
apps/web/node_modules/rolldown/dist/parse-ast-index.d.mts
apps/web/node_modules/rolldown/dist/parse-ast-index.mjs
apps/web/node_modules/rolldown/dist/plugins-index.d.mts
apps/web/node_modules/rolldown/dist/plugins-index.mjs
apps/web/node_modules/rolldown/dist/shared/binding-BQxk4mNX.d.mts
apps/web/node_modules/rolldown/dist/shared/binding-DXnWtC_4.mjs
apps/web/node_modules/rolldown/dist/shared/bindingify-input-options-BjFSnI07.mjs
apps/web/node_modules/rolldown/dist/shared/constructors-OHACCTTC.mjs
apps/web/node_modules/rolldown/dist/shared/constructors-viKPej7M.d.mts
apps/web/node_modules/rolldown/dist/shared/create-bundler-option-BJCYFVUH.mjs
apps/web/node_modules/rolldown/dist/shared/define-config-BQBrxnNZ.mjs
apps/web/node_modules/rolldown/dist/shared/define-config-u93KkixF.d.mts
apps/web/node_modules/rolldown/dist/shared/dist-BHJd_fmG.mjs
apps/web/node_modules/rolldown/dist/shared/error-CLo6EJKG.mjs
apps/web/node_modules/rolldown/dist/shared/get-log-filter-DFFBhB1m.d.mts
apps/web/node_modules/rolldown/dist/shared/load-config-69P1TxdT.mjs
apps/web/node_modules/rolldown/dist/shared/logger-LvdykevT.mjs
apps/web/node_modules/rolldown/dist/shared/logging-loixHZcv.d.mts
apps/web/node_modules/rolldown/dist/shared/logs-DyTyzzWG.mjs
apps/web/node_modules/rolldown/dist/shared/misc-BaVlOYH0.mjs
apps/web/node_modules/rolldown/dist/shared/normalize-string-or-regex-Bb-uIrCY.mjs
apps/web/node_modules/rolldown/dist/shared/parse-Bhrl_Rmm.mjs
apps/web/node_modules/rolldown/dist/shared/prompt-DkftHXS7.mjs
apps/web/node_modules/rolldown/dist/shared/resolve-tsconfig-ru_qwUC7.mjs
apps/web/node_modules/rolldown/dist/shared/rolldown-AohEFLrh.mjs
apps/web/node_modules/rolldown/dist/shared/rolldown-runtime-DYf_mQCB.mjs
apps/web/node_modules/rolldown/dist/shared/transform-Chp2CTwF.d.mts
apps/web/node_modules/rolldown/dist/shared/watch-C1G4Q3kq.mjs
apps/web/node_modules/rolldown/dist/utils-index.d.mts
apps/web/node_modules/rolldown/dist/utils-index.mjs
apps/web/node_modules/rolldown/package.json
apps/web/node_modules/scheduler/LICENSE
apps/web/node_modules/scheduler/README.md
apps/web/node_modules/scheduler/cjs/scheduler-unstable_mock.development.js
apps/web/node_modules/scheduler/cjs/scheduler-unstable_mock.production.js
apps/web/node_modules/scheduler/cjs/scheduler-unstable_post_task.development.js
apps/web/node_modules/scheduler/cjs/scheduler-unstable_post_task.production.js
apps/web/node_modules/scheduler/cjs/scheduler.development.js
apps/web/node_modules/scheduler/cjs/scheduler.native.development.js
apps/web/node_modules/scheduler/cjs/scheduler.native.production.js
apps/web/node_modules/scheduler/cjs/scheduler.production.js
apps/web/node_modules/scheduler/index.js
apps/web/node_modules/scheduler/index.native.js
apps/web/node_modules/scheduler/package.json
apps/web/node_modules/scheduler/unstable_mock.js
apps/web/node_modules/scheduler/unstable_post_task.js
apps/web/node_modules/source-map-js/LICENSE
apps/web/node_modules/source-map-js/README.md
apps/web/node_modules/source-map-js/lib/array-set.js
apps/web/node_modules/source-map-js/lib/base64-vlq.js
apps/web/node_modules/source-map-js/lib/base64.js
apps/web/node_modules/source-map-js/lib/binary-search.js
apps/web/node_modules/source-map-js/lib/mapping-list.js
apps/web/node_modules/source-map-js/lib/quick-sort.js
apps/web/node_modules/source-map-js/lib/source-map-consumer.d.ts
apps/web/node_modules/source-map-js/lib/source-map-consumer.js
apps/web/node_modules/source-map-js/lib/source-map-generator.d.ts
apps/web/node_modules/source-map-js/lib/source-map-generator.js
apps/web/node_modules/source-map-js/lib/source-node.d.ts
apps/web/node_modules/source-map-js/lib/source-node.js
apps/web/node_modules/source-map-js/lib/util.js
apps/web/node_modules/source-map-js/package.json
apps/web/node_modules/source-map-js/source-map.d.ts
apps/web/node_modules/source-map-js/source-map.js
apps/web/node_modules/tinyglobby/LICENSE
apps/web/node_modules/tinyglobby/README.md
apps/web/node_modules/tinyglobby/dist/index.cjs
apps/web/node_modules/tinyglobby/dist/index.d.cts
apps/web/node_modules/tinyglobby/dist/index.d.mts
apps/web/node_modules/tinyglobby/dist/index.mjs
apps/web/node_modules/tinyglobby/package.json
apps/web/node_modules/typescript/LICENSE
apps/web/node_modules/typescript/NOTICE.txt
apps/web/node_modules/typescript/README.md
apps/web/node_modules/typescript/bin/tsc
apps/web/node_modules/typescript/dist/api/async/api.d.ts
apps/web/node_modules/typescript/dist/api/async/api.d.ts.map
apps/web/node_modules/typescript/dist/api/async/api.js
apps/web/node_modules/typescript/dist/api/async/api.js.map
apps/web/node_modules/typescript/dist/api/async/client.d.ts
apps/web/node_modules/typescript/dist/api/async/client.d.ts.map
apps/web/node_modules/typescript/dist/api/async/client.js
apps/web/node_modules/typescript/dist/api/async/client.js.map
apps/web/node_modules/typescript/dist/api/async/types.d.ts
apps/web/node_modules/typescript/dist/api/async/types.d.ts.map
apps/web/node_modules/typescript/dist/api/async/types.js
apps/web/node_modules/typescript/dist/api/async/types.js.map
apps/web/node_modules/typescript/dist/api/compilerOptions.d.ts
apps/web/node_modules/typescript/dist/api/compilerOptions.d.ts.map
apps/web/node_modules/typescript/dist/api/compilerOptions.js
apps/web/node_modules/typescript/dist/api/compilerOptions.js.map
apps/web/node_modules/typescript/dist/api/fs.d.ts
apps/web/node_modules/typescript/dist/api/fs.d.ts.map
apps/web/node_modules/typescript/dist/api/fs.js
apps/web/node_modules/typescript/dist/api/fs.js.map
apps/web/node_modules/typescript/dist/api/node/encoder.d.ts
apps/web/node_modules/typescript/dist/api/node/encoder.d.ts.map
apps/web/node_modules/typescript/dist/api/node/encoder.generated.d.ts
apps/web/node_modules/typescript/dist/api/node/encoder.generated.d.ts.map
apps/web/node_modules/typescript/dist/api/node/encoder.generated.js
apps/web/node_modules/typescript/dist/api/node/encoder.generated.js.map
apps/web/node_modules/typescript/dist/api/node/encoder.js
apps/web/node_modules/typescript/dist/api/node/encoder.js.map
apps/web/node_modules/typescript/dist/api/node/msgpack.d.ts
apps/web/node_modules/typescript/dist/api/node/msgpack.d.ts.map
apps/web/node_modules/typescript/dist/api/node/msgpack.js
apps/web/node_modules/typescript/dist/api/node/msgpack.js.map
apps/web/node_modules/typescript/dist/api/node/node.d.ts
apps/web/node_modules/typescript/dist/api/node/node.d.ts.map
apps/web/node_modules/typescript/dist/api/node/node.generated.d.ts
apps/web/node_modules/typescript/dist/api/node/node.generated.d.ts.map
apps/web/node_modules/typescript/dist/api/node/node.generated.js
apps/web/node_modules/typescript/dist/api/node/node.generated.js.map
apps/web/node_modules/typescript/dist/api/node/node.infrastructure.d.ts
apps/web/node_modules/typescript/dist/api/node/node.infrastructure.d.ts.map
apps/web/node_modules/typescript/dist/api/node/node.infrastructure.js
apps/web/node_modules/typescript/dist/api/node/node.infrastructure.js.map
apps/web/node_modules/typescript/dist/api/node/node.js
apps/web/node_modules/typescript/dist/api/node/node.js.map
apps/web/node_modules/typescript/dist/api/node/protocol.d.ts
apps/web/node_modules/typescript/dist/api/node/protocol.d.ts.map
apps/web/node_modules/typescript/dist/api/node/protocol.generated.d.ts
apps/web/node_modules/typescript/dist/api/node/protocol.generated.d.ts.map
apps/web/node_modules/typescript/dist/api/node/protocol.generated.js
apps/web/node_modules/typescript/dist/api/node/protocol.generated.js.map
apps/web/node_modules/typescript/dist/api/node/protocol.js
apps/web/node_modules/typescript/dist/api/node/protocol.js.map
apps/web/node_modules/typescript/dist/api/node/wtf8.d.ts
apps/web/node_modules/typescript/dist/api/node/wtf8.d.ts.map
apps/web/node_modules/typescript/dist/api/node/wtf8.js
apps/web/node_modules/typescript/dist/api/node/wtf8.js.map
apps/web/node_modules/typescript/dist/api/options.d.ts
apps/web/node_modules/typescript/dist/api/options.d.ts.map
apps/web/node_modules/typescript/dist/api/options.js
apps/web/node_modules/typescript/dist/api/options.js.map
apps/web/node_modules/typescript/dist/api/path.d.ts
apps/web/node_modules/typescript/dist/api/path.d.ts.map
apps/web/node_modules/typescript/dist/api/path.js
apps/web/node_modules/typescript/dist/api/path.js.map
apps/web/node_modules/typescript/dist/api/proto.d.ts
apps/web/node_modules/typescript/dist/api/proto.d.ts.map
apps/web/node_modules/typescript/dist/api/proto.js
apps/web/node_modules/typescript/dist/api/proto.js.map
apps/web/node_modules/typescript/dist/api/sourceFileCache.d.ts
apps/web/node_modules/typescript/dist/api/sourceFileCache.d.ts.map
apps/web/node_modules/typescript/dist/api/sourceFileCache.js
apps/web/node_modules/typescript/dist/api/sourceFileCache.js.map
apps/web/node_modules/typescript/dist/api/sync/api.d.ts
apps/web/node_modules/typescript/dist/api/sync/api.d.ts.map
apps/web/node_modules/typescript/dist/api/sync/api.js
apps/web/node_modules/typescript/dist/api/sync/api.js.map
apps/web/node_modules/typescript/dist/api/sync/client.d.ts
apps/web/node_modules/typescript/dist/api/sync/client.d.ts.map
apps/web/node_modules/typescript/dist/api/sync/client.js
apps/web/node_modules/typescript/dist/api/sync/client.js.map
apps/web/node_modules/typescript/dist/api/sync/types.d.ts
apps/web/node_modules/typescript/dist/api/sync/types.d.ts.map
apps/web/node_modules/typescript/dist/api/sync/types.js
apps/web/node_modules/typescript/dist/api/sync/types.js.map
apps/web/node_modules/typescript/dist/api/syncChannel.d.ts
apps/web/node_modules/typescript/dist/api/syncChannel.d.ts.map
apps/web/node_modules/typescript/dist/api/syncChannel.js
apps/web/node_modules/typescript/dist/api/syncChannel.js.map
apps/web/node_modules/typescript/dist/api/timing.d.ts
apps/web/node_modules/typescript/dist/api/timing.d.ts.map
apps/web/node_modules/typescript/dist/api/timing.js
apps/web/node_modules/typescript/dist/api/timing.js.map
apps/web/node_modules/typescript/dist/ast/ast.d.ts
apps/web/node_modules/typescript/dist/ast/ast.d.ts.map
apps/web/node_modules/typescript/dist/ast/ast.generated.d.ts
apps/web/node_modules/typescript/dist/ast/ast.generated.d.ts.map
apps/web/node_modules/typescript/dist/ast/ast.generated.js
apps/web/node_modules/typescript/dist/ast/ast.generated.js.map
apps/web/node_modules/typescript/dist/ast/ast.js
apps/web/node_modules/typescript/dist/ast/ast.js.map
apps/web/node_modules/typescript/dist/ast/astnav.d.ts
apps/web/node_modules/typescript/dist/ast/astnav.d.ts.map
apps/web/node_modules/typescript/dist/ast/astnav.js
apps/web/node_modules/typescript/dist/ast/astnav.js.map
apps/web/node_modules/typescript/dist/ast/clone.d.ts
apps/web/node_modules/typescript/dist/ast/clone.d.ts.map
apps/web/node_modules/typescript/dist/ast/clone.js
apps/web/node_modules/typescript/dist/ast/clone.js.map
apps/web/node_modules/typescript/dist/ast/factory.generated.d.ts
apps/web/node_modules/typescript/dist/ast/factory.generated.d.ts.map
apps/web/node_modules/typescript/dist/ast/factory.generated.js
apps/web/node_modules/typescript/dist/ast/factory.generated.js.map
apps/web/node_modules/typescript/dist/ast/index.d.ts
apps/web/node_modules/typescript/dist/ast/index.d.ts.map
apps/web/node_modules/typescript/dist/ast/index.js
apps/web/node_modules/typescript/dist/ast/index.js.map
apps/web/node_modules/typescript/dist/ast/is.d.ts
apps/web/node_modules/typescript/dist/ast/is.d.ts.map
apps/web/node_modules/typescript/dist/ast/is.generated.d.ts
apps/web/node_modules/typescript/dist/ast/is.generated.d.ts.map
apps/web/node_modules/typescript/dist/ast/is.generated.js
apps/web/node_modules/typescript/dist/ast/is.generated.js.map
apps/web/node_modules/typescript/dist/ast/is.js
apps/web/node_modules/typescript/dist/ast/is.js.map
apps/web/node_modules/typescript/dist/ast/jsdoc.d.ts
apps/web/node_modules/typescript/dist/ast/jsdoc.d.ts.map
apps/web/node_modules/typescript/dist/ast/jsdoc.js
apps/web/node_modules/typescript/dist/ast/jsdoc.js.map
apps/web/node_modules/typescript/dist/ast/scanner.d.ts
apps/web/node_modules/typescript/dist/ast/scanner.d.ts.map
apps/web/node_modules/typescript/dist/ast/scanner.js
apps/web/node_modules/typescript/dist/ast/scanner.js.map
apps/web/node_modules/typescript/dist/ast/utils.d.ts
apps/web/node_modules/typescript/dist/ast/utils.d.ts.map
apps/web/node_modules/typescript/dist/ast/utils.js
apps/web/node_modules/typescript/dist/ast/utils.js.map
apps/web/node_modules/typescript/dist/ast/visitor.d.ts
apps/web/node_modules/typescript/dist/ast/visitor.d.ts.map
apps/web/node_modules/typescript/dist/ast/visitor.generated.d.ts
apps/web/node_modules/typescript/dist/ast/visitor.generated.d.ts.map
apps/web/node_modules/typescript/dist/ast/visitor.generated.js
apps/web/node_modules/typescript/dist/ast/visitor.generated.js.map
apps/web/node_modules/typescript/dist/ast/visitor.js
apps/web/node_modules/typescript/dist/ast/visitor.js.map
apps/web/node_modules/typescript/dist/enums/characterCodes.d.ts
apps/web/node_modules/typescript/dist/enums/characterCodes.d.ts.map
apps/web/node_modules/typescript/dist/enums/characterCodes.enum.d.ts
apps/web/node_modules/typescript/dist/enums/characterCodes.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/characterCodes.enum.js
apps/web/node_modules/typescript/dist/enums/characterCodes.enum.js.map
apps/web/node_modules/typescript/dist/enums/characterCodes.js
apps/web/node_modules/typescript/dist/enums/characterCodes.js.map
apps/web/node_modules/typescript/dist/enums/commentDirectiveType.d.ts
apps/web/node_modules/typescript/dist/enums/commentDirectiveType.d.ts.map
apps/web/node_modules/typescript/dist/enums/commentDirectiveType.enum.d.ts
apps/web/node_modules/typescript/dist/enums/commentDirectiveType.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/commentDirectiveType.enum.js
apps/web/node_modules/typescript/dist/enums/commentDirectiveType.enum.js.map
apps/web/node_modules/typescript/dist/enums/commentDirectiveType.js
apps/web/node_modules/typescript/dist/enums/commentDirectiveType.js.map
apps/web/node_modules/typescript/dist/enums/completionItemKind.d.ts
apps/web/node_modules/typescript/dist/enums/completionItemKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/completionItemKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/completionItemKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/completionItemKind.enum.js
apps/web/node_modules/typescript/dist/enums/completionItemKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/completionItemKind.js
apps/web/node_modules/typescript/dist/enums/completionItemKind.js.map
apps/web/node_modules/typescript/dist/enums/diagnosticCategory.d.ts
apps/web/node_modules/typescript/dist/enums/diagnosticCategory.d.ts.map
apps/web/node_modules/typescript/dist/enums/diagnosticCategory.enum.d.ts
apps/web/node_modules/typescript/dist/enums/diagnosticCategory.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/diagnosticCategory.enum.js
apps/web/node_modules/typescript/dist/enums/diagnosticCategory.enum.js.map
apps/web/node_modules/typescript/dist/enums/diagnosticCategory.js
apps/web/node_modules/typescript/dist/enums/diagnosticCategory.js.map
apps/web/node_modules/typescript/dist/enums/elementFlags.d.ts
apps/web/node_modules/typescript/dist/enums/elementFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/elementFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/elementFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/elementFlags.enum.js
apps/web/node_modules/typescript/dist/enums/elementFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/elementFlags.js
apps/web/node_modules/typescript/dist/enums/elementFlags.js.map
apps/web/node_modules/typescript/dist/enums/internalSymbolName.d.ts
apps/web/node_modules/typescript/dist/enums/internalSymbolName.d.ts.map
apps/web/node_modules/typescript/dist/enums/internalSymbolName.enum.d.ts
apps/web/node_modules/typescript/dist/enums/internalSymbolName.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/internalSymbolName.enum.js
apps/web/node_modules/typescript/dist/enums/internalSymbolName.enum.js.map
apps/web/node_modules/typescript/dist/enums/internalSymbolName.js
apps/web/node_modules/typescript/dist/enums/internalSymbolName.js.map
apps/web/node_modules/typescript/dist/enums/jsxEmit.d.ts
apps/web/node_modules/typescript/dist/enums/jsxEmit.d.ts.map
apps/web/node_modules/typescript/dist/enums/jsxEmit.enum.d.ts
apps/web/node_modules/typescript/dist/enums/jsxEmit.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/jsxEmit.enum.js
apps/web/node_modules/typescript/dist/enums/jsxEmit.enum.js.map
apps/web/node_modules/typescript/dist/enums/jsxEmit.js
apps/web/node_modules/typescript/dist/enums/jsxEmit.js.map
apps/web/node_modules/typescript/dist/enums/languageVariant.d.ts
apps/web/node_modules/typescript/dist/enums/languageVariant.d.ts.map
apps/web/node_modules/typescript/dist/enums/languageVariant.enum.d.ts
apps/web/node_modules/typescript/dist/enums/languageVariant.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/languageVariant.enum.js
apps/web/node_modules/typescript/dist/enums/languageVariant.enum.js.map
apps/web/node_modules/typescript/dist/enums/languageVariant.js
apps/web/node_modules/typescript/dist/enums/languageVariant.js.map
apps/web/node_modules/typescript/dist/enums/modifierFlags.d.ts
apps/web/node_modules/typescript/dist/enums/modifierFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/modifierFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/modifierFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/modifierFlags.enum.js
apps/web/node_modules/typescript/dist/enums/modifierFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/modifierFlags.js
apps/web/node_modules/typescript/dist/enums/modifierFlags.js.map
apps/web/node_modules/typescript/dist/enums/moduleDetectionKind.d.ts
apps/web/node_modules/typescript/dist/enums/moduleDetectionKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/moduleDetectionKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/moduleDetectionKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/moduleDetectionKind.enum.js
apps/web/node_modules/typescript/dist/enums/moduleDetectionKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/moduleDetectionKind.js
apps/web/node_modules/typescript/dist/enums/moduleDetectionKind.js.map
apps/web/node_modules/typescript/dist/enums/moduleKind.d.ts
apps/web/node_modules/typescript/dist/enums/moduleKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/moduleKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/moduleKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/moduleKind.enum.js
apps/web/node_modules/typescript/dist/enums/moduleKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/moduleKind.js
apps/web/node_modules/typescript/dist/enums/moduleKind.js.map
apps/web/node_modules/typescript/dist/enums/moduleResolutionKind.d.ts
apps/web/node_modules/typescript/dist/enums/moduleResolutionKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/moduleResolutionKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/moduleResolutionKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/moduleResolutionKind.enum.js
apps/web/node_modules/typescript/dist/enums/moduleResolutionKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/moduleResolutionKind.js
apps/web/node_modules/typescript/dist/enums/moduleResolutionKind.js.map
apps/web/node_modules/typescript/dist/enums/newLineKind.d.ts
apps/web/node_modules/typescript/dist/enums/newLineKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/newLineKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/newLineKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/newLineKind.enum.js
apps/web/node_modules/typescript/dist/enums/newLineKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/newLineKind.js
apps/web/node_modules/typescript/dist/enums/newLineKind.js.map
apps/web/node_modules/typescript/dist/enums/nodeBuilderFlags.d.ts
apps/web/node_modules/typescript/dist/enums/nodeBuilderFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.js
apps/web/node_modules/typescript/dist/enums/nodeBuilderFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/nodeBuilderFlags.js
apps/web/node_modules/typescript/dist/enums/nodeBuilderFlags.js.map
apps/web/node_modules/typescript/dist/enums/nodeFlags.d.ts
apps/web/node_modules/typescript/dist/enums/nodeFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/nodeFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/nodeFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/nodeFlags.enum.js
apps/web/node_modules/typescript/dist/enums/nodeFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/nodeFlags.js
apps/web/node_modules/typescript/dist/enums/nodeFlags.js.map
apps/web/node_modules/typescript/dist/enums/objectFlags.d.ts
apps/web/node_modules/typescript/dist/enums/objectFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/objectFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/objectFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/objectFlags.enum.js
apps/web/node_modules/typescript/dist/enums/objectFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/objectFlags.js
apps/web/node_modules/typescript/dist/enums/objectFlags.js.map
apps/web/node_modules/typescript/dist/enums/outerExpressionKinds.d.ts
apps/web/node_modules/typescript/dist/enums/outerExpressionKinds.d.ts.map
apps/web/node_modules/typescript/dist/enums/outerExpressionKinds.enum.d.ts
apps/web/node_modules/typescript/dist/enums/outerExpressionKinds.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/outerExpressionKinds.enum.js
apps/web/node_modules/typescript/dist/enums/outerExpressionKinds.enum.js.map
apps/web/node_modules/typescript/dist/enums/outerExpressionKinds.js
apps/web/node_modules/typescript/dist/enums/outerExpressionKinds.js.map
apps/web/node_modules/typescript/dist/enums/regularExpressionFlags.d.ts
apps/web/node_modules/typescript/dist/enums/regularExpressionFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/regularExpressionFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/regularExpressionFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/regularExpressionFlags.enum.js
apps/web/node_modules/typescript/dist/enums/regularExpressionFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/regularExpressionFlags.js
apps/web/node_modules/typescript/dist/enums/regularExpressionFlags.js.map
apps/web/node_modules/typescript/dist/enums/scriptKind.d.ts
apps/web/node_modules/typescript/dist/enums/scriptKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/scriptKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/scriptKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/scriptKind.enum.js
apps/web/node_modules/typescript/dist/enums/scriptKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/scriptKind.js
apps/web/node_modules/typescript/dist/enums/scriptKind.js.map
apps/web/node_modules/typescript/dist/enums/scriptTarget.d.ts
apps/web/node_modules/typescript/dist/enums/scriptTarget.d.ts.map
apps/web/node_modules/typescript/dist/enums/scriptTarget.enum.d.ts
apps/web/node_modules/typescript/dist/enums/scriptTarget.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/scriptTarget.enum.js
apps/web/node_modules/typescript/dist/enums/scriptTarget.enum.js.map
apps/web/node_modules/typescript/dist/enums/scriptTarget.js
apps/web/node_modules/typescript/dist/enums/scriptTarget.js.map
apps/web/node_modules/typescript/dist/enums/signatureFlags.d.ts
apps/web/node_modules/typescript/dist/enums/signatureFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/signatureFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/signatureFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/signatureFlags.enum.js
apps/web/node_modules/typescript/dist/enums/signatureFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/signatureFlags.js
apps/web/node_modules/typescript/dist/enums/signatureFlags.js.map
apps/web/node_modules/typescript/dist/enums/signatureKind.d.ts
apps/web/node_modules/typescript/dist/enums/signatureKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/signatureKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/signatureKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/signatureKind.enum.js
apps/web/node_modules/typescript/dist/enums/signatureKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/signatureKind.js
apps/web/node_modules/typescript/dist/enums/signatureKind.js.map
apps/web/node_modules/typescript/dist/enums/symbolFlags.d.ts
apps/web/node_modules/typescript/dist/enums/symbolFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/symbolFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/symbolFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/symbolFlags.enum.js
apps/web/node_modules/typescript/dist/enums/symbolFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/symbolFlags.js
apps/web/node_modules/typescript/dist/enums/symbolFlags.js.map
apps/web/node_modules/typescript/dist/enums/syntaxKind.d.ts
apps/web/node_modules/typescript/dist/enums/syntaxKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/syntaxKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/syntaxKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/syntaxKind.enum.js
apps/web/node_modules/typescript/dist/enums/syntaxKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/syntaxKind.js
apps/web/node_modules/typescript/dist/enums/syntaxKind.js.map
apps/web/node_modules/typescript/dist/enums/tokenFlags.d.ts
apps/web/node_modules/typescript/dist/enums/tokenFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/tokenFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/tokenFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/tokenFlags.enum.js
apps/web/node_modules/typescript/dist/enums/tokenFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/tokenFlags.js
apps/web/node_modules/typescript/dist/enums/tokenFlags.js.map
apps/web/node_modules/typescript/dist/enums/typeFlags.d.ts
apps/web/node_modules/typescript/dist/enums/typeFlags.d.ts.map
apps/web/node_modules/typescript/dist/enums/typeFlags.enum.d.ts
apps/web/node_modules/typescript/dist/enums/typeFlags.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/typeFlags.enum.js
apps/web/node_modules/typescript/dist/enums/typeFlags.enum.js.map
apps/web/node_modules/typescript/dist/enums/typeFlags.js
apps/web/node_modules/typescript/dist/enums/typeFlags.js.map
apps/web/node_modules/typescript/dist/enums/typePredicateKind.d.ts
apps/web/node_modules/typescript/dist/enums/typePredicateKind.d.ts.map
apps/web/node_modules/typescript/dist/enums/typePredicateKind.enum.d.ts
apps/web/node_modules/typescript/dist/enums/typePredicateKind.enum.d.ts.map
apps/web/node_modules/typescript/dist/enums/typePredicateKind.enum.js
apps/web/node_modules/typescript/dist/enums/typePredicateKind.enum.js.map
apps/web/node_modules/typescript/dist/enums/typePredicateKind.js
apps/web/node_modules/typescript/dist/enums/typePredicateKind.js.map
apps/web/node_modules/typescript/dist/internal/utils.d.ts
apps/web/node_modules/typescript/dist/internal/utils.d.ts.map
apps/web/node_modules/typescript/dist/internal/utils.js
apps/web/node_modules/typescript/dist/internal/utils.js.map
apps/web/node_modules/typescript/lib/getExePath.d.ts
apps/web/node_modules/typescript/lib/getExePath.js
apps/web/node_modules/typescript/lib/tsc.js
apps/web/node_modules/typescript/lib/version.cjs
apps/web/node_modules/typescript/lib/version.d.cts
apps/web/node_modules/typescript/package.json
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/License.txt
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/README.md
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/browser/main.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/browser/main.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/browser/ril.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/browser/ril.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/api.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/api.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/cancellation.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/cancellation.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/connection.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/connection.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/disposable.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/disposable.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/encoding.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/encoding.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/events.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/events.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/is.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/is.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/linkedMap.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/linkedMap.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageBuffer.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageBuffer.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageReader.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageReader.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageWriter.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messageWriter.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messages.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/messages.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/ral.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/ral.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/semaphore.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/semaphore.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/sharedArrayCancellation.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/common/sharedArrayCancellation.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/node/main.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/node/main.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/node/ril.d.ts
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/lib/node/ril.js
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/package.json
apps/web/node_modules/typescript/vendor/vscode-jsonrpc/typings/thenable.d.ts
apps/web/node_modules/vite/LICENSE.md
apps/web/node_modules/vite/README.md
apps/web/node_modules/vite/bin/openChrome.js
apps/web/node_modules/vite/bin/vite.js
apps/web/node_modules/vite/client.d.ts
apps/web/node_modules/vite/dist/client/bundledDevClient.mjs
apps/web/node_modules/vite/dist/client/client.mjs
apps/web/node_modules/vite/dist/client/env.mjs
apps/web/node_modules/vite/dist/node/chunks/build.js
apps/web/node_modules/vite/dist/node/chunks/dist.js
apps/web/node_modules/vite/dist/node/chunks/lib.js
apps/web/node_modules/vite/dist/node/chunks/moduleRunnerTransport.d.ts
apps/web/node_modules/vite/dist/node/chunks/node.js
apps/web/node_modules/vite/dist/node/chunks/postcss-import.js
apps/web/node_modules/vite/dist/node/cli.js
apps/web/node_modules/vite/dist/node/index.d.ts
apps/web/node_modules/vite/dist/node/index.js
apps/web/node_modules/vite/dist/node/internal.d.ts
apps/web/node_modules/vite/dist/node/internal.js
apps/web/node_modules/vite/dist/node/module-runner.d.ts
apps/web/node_modules/vite/dist/node/module-runner.js
apps/web/node_modules/vite/misc/false.js
apps/web/node_modules/vite/misc/true.js
apps/web/node_modules/vite/package.json
apps/web/node_modules/vite/types/customEvent.d.ts
apps/web/node_modules/vite/types/hmrPayload.d.ts
apps/web/node_modules/vite/types/hot.d.ts
apps/web/node_modules/vite/types/import-meta.d.ts
apps/web/node_modules/vite/types/importGlob.d.ts
apps/web/node_modules/vite/types/importMeta.d.ts
apps/web/node_modules/vite/types/internal/cssPreprocessorOptions.d.ts
apps/web/node_modules/vite/types/internal/devtoolsOptions.d.ts
apps/web/node_modules/vite/types/internal/esbuildOptions.d.ts
apps/web/node_modules/vite/types/internal/lightningcssOptions.d.ts
apps/web/node_modules/vite/types/internal/rollupTypeCompat.d.ts
apps/web/node_modules/vite/types/internal/terserOptions.d.ts
apps/web/node_modules/vite/types/metadata.d.ts
apps/web/package-lock.json
apps/web/package.json
apps/web/src/App.tsx
apps/web/src/components/.gitkeep
apps/web/src/main.tsx
apps/web/src/pages/.gitkeep
apps/web/src/services/api.ts
apps/web/vite.config.ts
backlog.md
compose.yaml
instructions/calculate-compound-interest.agent.md
instructions/create-status-report.agent.md
instructions/creating-instructions.agent.md
instructions/main.agent.md
instructions/update-confluence-page.agent.md
instructions/use-status-report-skill.agent.md
jira-dashboard-requirements.md
notes.md
ops/macos/launchd/.gitkeep
packages/shared/src/index.ts
project_spec.md
reports/example.md
reports/instructions.md
reports/template.md
reports/weekly-status-report-2026-11-18.md
reports/weekly-status-report-2026-11-28.md
spec/analyze.md
spec/clarify.md
spec/constitution.md
spec/external-config.md
spec/plan.md
spec/specification.md
spec/tasks.md
tests/integration/.gitkeep
tests/test_jira_client.py
tests/test_jira_connection_config.ts
tests/test_mcp_text_stats_server.py
tests/test_meeting_notes_check.py
tests/test_report.py
tests/test_skill_status_report.py
tests/unit/api/.gitkeep
tests/unit/web/.gitkeep
tools/check_meeting_notes.py
tools/compound_interest.py
tools/mcp_echo_server.py
tools/mcp_text_stats_server.py
tools/skill_status_report.py
weekly_status/README.md
weekly_status/__init__.py
weekly_status/generator.py
weekly_status/jira_client.py
weekly_status/report.py
work/module-03-report.md
work/module-08-report.md
work/module-09-report.md
work/module-10-report.md
work/module-12-report.md
work/module-13-report.md
work/module-14-report.md
work/module-15-report.md
work/module-16-report.md
work/module03-task
