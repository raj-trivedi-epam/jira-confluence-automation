# Implementation Plan: Jira/Confluence Automation Prototype

**Status:** Proposed
**Specification:** [specification.md](./specification.md)
**Constitution:** [constitution.md](./constitution.md)
**Clarifications:** [clarify.md](./clarify.md)

## Objective

Implement a local-first React 18/Vite and Node.js/Express prototype that generates aggregate-only weekly Jira status reports, persists run and review metadata in PostgreSQL 15, and preserves the previous report after failures.

This plan implements the clarified prototype scope only. Confluence integration, Jira project provisioning, the 15-minute sprint dashboard, assignee-level reporting, manual period selection, automatic distribution, `launchd`, and missed-run catch-up are excluded.

## Implementation Constraints

- Node.js/TypeScript supersedes the original Python implementation proposal.
- Existing Python code may be used as domain-reference material only.
- Express and Vite bind to `127.0.0.1`.
- PostgreSQL 15 runs through Docker Compose.
- macOS Keychain stores OAuth secrets and refresh credentials.
- Markdown under `reports/` is the canonical report artifact.
- PostgreSQL stores configuration metadata, report metadata, review state, run history, and report paths.
- Jira access is read-only OAuth 2.0 3LO.
- Jira project setup is read-only discovery and validation.
- Scheduled execution uses a scheduler-independent worker entry point.

## Phase 0: External Configuration and Test Fixture Setup

### Work

1. Confirm the Jira Cloud site URL.
2. Confirm the `CLOUD` project key or approved replacement.
3. Confirm the project board ID and active sprint.
4. Confirm the Jira read-only OAuth app, callback configuration, and scopes.
5. Confirm the Jira story-point custom field ID.
6. Confirm the blocker field ID, field name, or label.
7. Confirm the `Cloud_project` group and read-only project role.
8. Register representative Jira mock fixtures for project, board, sprint, issue, status, estimate, resolution, changelog, pagination, and failure behavior.

### Deliverables

- Approved `.env.example` with non-secret configuration names.
- Jira fixture set covering normal and failure scenarios.
- Confirmed OAuth callback and Keychain setup instructions.
- A documented configuration validation checklist.

### Milestone M0: External dependencies confirmed

**Exit criteria**

- Every live Jira connection prerequisite is identified.
- Story-point and blocker fields are configured or explicitly marked unavailable.
- Mock fixtures cover all required calculation branches.

## Phase 1: Monorepo Foundation

### Work

1. Define npm workspaces for `apps/web`, `apps/api`, and `packages/shared`.
2. Add backend and frontend package scripts.
3. Add TypeScript configuration and workspace-level lint/test settings.
4. Define environment loading and loopback-only development defaults.
5. Add Docker Compose for PostgreSQL 15.
6. Establish common error, API, status, and domain types in `packages/shared`.

### Deliverables

- Runnable workspace root.
- PostgreSQL 15 development container.
- Empty or minimal Express server on loopback.
- React/Vite application shell on loopback.
- Migration and test commands documented.

### Milestone M1: Foundation starts locally

**Exit criteria**

- The frontend and backend start with loopback addresses.
- PostgreSQL 15 accepts connections from the backend.
- Workspace scripts and initial tests execute successfully.

## Phase 2: Persistence and Configuration

### Work

1. Create migrations for Jira configuration, report, run, and review entities.
2. Add UUID primary keys and report/run foreign-key relations.
3. Implement parameterized configuration and run repositories.
4. Implement migration status and database health checks.
5. Add non-secret configuration precedence:
   - environment overrides
   - PostgreSQL configuration
   - secure provider for secrets
6. Implement Docker volume and local credential setup documentation.
7. Add a 30-day/10 MB/5-file logging policy.

### Deliverables

- PostgreSQL schema and migrations.
- Configuration repository.
- Run and report repositories.
- Health and migration status modules.
- Safe operational log setup.

### Milestone M2: Persisted, inspectable state

**Exit criteria**

- A fresh database can migrate successfully.
- Configuration and run records persist and reload.
- A database failure is distinguishable from Jira and file failures.
- No credential or token is written to database, source, or logs.

## Phase 3: Jira OAuth and Read-Only Integration

### Work

1. Implement Jira Cloud OAuth 2.0 3LO authorization and callback.
2. Store access and refresh credentials in macOS Keychain.
3. Implement token refresh and reauthorization on revoked/expired consent.
4. Add project, board, sprint, issue, status, story-point, resolution, and changelog fetch clients.
5. Implement complete bounded pagination.
6. Implement 10-second request timeout and 3-attempt retry policy.
7. Retry 429 and 5xx responses; honor `Retry-After` up to 60 seconds.
8. Exclude authentication and validation failures from retries.
9. Implement Jira configuration discovery and validation.

### Deliverables

- Backend-only OAuth service.
- Read-only Jira API client.
- Keychain credential provider.
- Jira configuration status module.
- Mocked integration test suite.

### Milestone M3: Read-only Jira integration works

**Exit criteria**

- OAuth authorization, refresh, and revocation behavior pass tests.
- Project, board, active sprint, issue, estimate, resolution, and changelog fixtures pass.
- Pagination and 429/5xx retry behavior pass.
- No Jira secret or payload is exposed to the browser or logs.

## Phase 4: Reporting Domain Logic

### Work

1. Implement the Asia/Kolkata reporting-period calculation.
2. Implement completed, reopened, in-progress, and upcoming classification.
3. Implement resolution/reopen changelog validation.
4. Implement active-sprint and story-point aggregation.
5. Implement missing-estimate and unavailable-metric rules.
6. Implement blocker-marker interpretation and marker state distinctions.
7. Implement deterministic overall report section templates.
8. Leave overall delivery status for human review rather than generation.

### Deliverables

- Pure domain functions for periods and aggregation.
- Report model and validation rules.
- Deterministic Markdown renderer.
- Unit fixture suite with edge cases.

### Milestone M4: Domain calculations are verified

**Exit criteria**

- The `[generationTime - 7 days, generationTime]` boundary passes exact fixtures.
- Reopened issues are excluded.
- Missing estimates are rendered as unavailable.
- Sprint totals, status categories, and blocker states pass fixtures.
- No issue key, comment, assignee, or individual comparison reaches stakeholder output.

## Phase 5: Report Generation and Atomic Persistence

### Work

1. Implement a process-wide run lock.
2. Implement run creation and overlap handling with HTTP `409`.
3. Implement the scheduler-independent generation pipeline.
4. Validate all required Jira data before rendering.
5. Render Markdown from validated aggregates.
6. Write report files atomically.
7. Implement same-day revision names.
8. Create report and run records after successful file write.
9. Add reconciliation states for database/file mismatch and process crashes.
10. Preserve a prior report on any validation or fetch failure.

### Deliverables

- Generation service.
- Worker entry point.
- Atomic file writer.
- Run/report reconciliation behavior.
- Safe run-history error categories.

### Milestone M5: Failure-safe report generation

**Exit criteria**

- Manual and direct-worker runs use the same pipeline.
- Concurrent runs return 409 and cannot overlap.
- Atomic-write failure leaves prior report bytes unchanged.
- Successful reports receive metadata and a canonical path.
- Database/file inconsistency is visible and recoverable.

## Phase 6: React/Vite Review Application

### Work

1. Build a loopback-only React/Vite application.
2. Add configuration status and non-secret Jira configuration screens.
3. Add OAuth initiation and backend callback status.
4. Add manual report-generation action.
5. Add report preview and aggregate sections.
6. Add overall-status selection and review controls.
7. Add run-history table and pagination at 25 records per page.
8. Add loading, validation, authentication, upstream, and internal error states.
9. Add semantic headings, visible focus, and keyboard-operable controls.

### Deliverables

- Configuration dashboard.
- Report preview/review workflow.
- Run-history UI.
- Loopback-only API integration.

### Milestone M6: Human review workflow works

**Exit criteria**

- An operator can configure non-secret settings and authorize Jira.
- A report can be generated, previewed, status-selected, and marked reviewed.
- Review state is stored with OS-user identity and timestamp.
- The UI never displays OAuth secrets or raw Jira payloads.

## Phase 7: API, Logging, and Operations

### Work

1. Implement the route contracts in the specification.
2. Return stable JSON success/error envelopes.
3. Apply 400, 401, 403, 404, 409, 429, and 5xx behavior consistently.
4. Add loopback binding checks.
5. Add run-history and report pagination.
6. Add rotating application and run logs.
7. Implement safe startup and migration-health checks.
8. Document Docker Compose start/stop, migration, reset, backup, and restore commands.
9. Document manual report opening and review.

### Deliverables

- Complete Express API.
- API contract tests.
- Operational runbook.
- Docker and migration documentation.

### Milestone M7: Local prototype is operable

**Exit criteria**

- Startup fails clearly for missing database or required configuration.
- API responses and logs are safe and measurable.
- Backups, resets, migrations, and operator commands are documented.
- The report workflow can run without a browser or HTTP call for scheduled-worker use.

## Phase 8: Verification and Convergence

### Work

1. Run unit tests for domain, configuration, timezone, and filename behavior.
2. Run mocked Jira integration tests for success and edge fixtures.
3. Run PostgreSQL migration and repository tests.
4. Run frontend component/API contract tests.
5. Run atomic-write and crash-recovery tests.
6. Run end-to-end manual generation with Jira mocks.
7. Test loopback binding and secret exposure.
8. Run the complete test suite and security-focused diff review.

### Deliverables

- Automated test suite.
- Test fixture inventory.
- Known limitation document.
- Acceptance evidence.

### Milestone M8: Prototype convergence

**Exit criteria**

- All acceptance checklist items are met or explicitly marked out of scope.
- Failure paths preserve prior reports.
- Report content remains aggregate-only.
- Credentials and payloads are absent from source and logs.
- The complete suite passes.

## Test Plan

| Area | Required fixtures or assertions |
|---|---|
| Reporting period | UTC-derived boundary inclusivity, DST, Asia/Kolkata display |
| Completion | Resolution in period, resolution outside period, reopened issue, missing resolution |
| Sprint | No active sprint, multiple active sprints, active-sprint scope changes |
| Estimates | Missing custom field, zero estimate, partial estimates, duplicate issues |
| Changelog | Resolution/reopen status churn, stale sprint snapshot |
| Jira API | Page truncation, 429, 5xx, authentication failure, partial data |
| Retries | 3 attempts, 1/2/4-second backoff, 10-second timeout |
| Concurrency | Duplicate manual and worker runs return 409 |
| Filesystem | Atomic write success/failure and prior-file preservation |
| Database | Migration, relation, run/report/review persistence |
| API | Stable JSON, status codes, loopback-only behavior |
| Frontend | Loading/error states, report preview, review metadata |

## Performance Targets

- At steady state, support up to 1000 Jira issues per report run.
- Complete the Jira fetch and report pipeline within 60 seconds for normal fixtures.
- Return non-generation API calls within 2 seconds.
- Page run history at 25 records.
- Support one local operator and one active generation process.

## Explicitly Excluded from This Plan

- Confluence read, write, OAuth, and publishing
- Jira project/board provisioning
- Jira permission or group mutation
- 15-minute sprint dashboard
- Assignee-level stakeholder reporting
- Manual custom reporting periods
- AI-generated report narrative
- Automatic report distribution
- `launchd` installation and scheduling
- Automated missed-run catch-up
- External notification channels
- Multi-user authentication and role management
- Remote or network-facing deployment
- Mobile/responsive product targets
