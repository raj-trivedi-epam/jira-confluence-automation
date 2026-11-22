# Implementation Tasks

**Plan:** [plan.md](./plan.md)
**Specification:** [specification.md](./specification.md)
**Constitution:** [constitution.md](./constitution.md)

## Task Status Legend

- **TBD**: Not started
- **Ready**: Prerequisites resolved and implementation can begin
- **Blocked**: External Jira or operator decision is unresolved
- **Done**: Implementation and acceptance evidence exist

## Phase 0: External setup and fixtures

### T001 — Confirm Jira connection configuration

**Status:** Blocked

**Description:** Confirm the Jira site URL, approved project key or approved replacement, board ID, and active-sprint behavior.

**Acceptance criteria**

- [ ] The Jira site URL is configured.
- [ ] The project key is not assumed without authorization.
- [ ] The board ID and active-sprint selection are confirmed.
- [ ] Configuration is available to mocked and live integration tests.

### T002 — Confirm OAuth and Keychain configuration

**Status:** Blocked

**Description:** Confirm Jira Cloud OAuth 2.0 3LO app registration, callback URL, read-only scopes, and macOS Keychain credential storage behavior.

**Acceptance criteria**

- [ ] OAuth authorization and callback work locally.
- [ ] Only read-only Jira scopes are approved.
- [ ] Access and refresh credentials are stored in macOS Keychain.
- [ ] No credential is committed or logged.

### T003 — Confirm Jira field configuration

**Status:** Blocked

**Description:** Record the story-point custom field ID and blocker field ID, field name, or label.

**Acceptance criteria**

- [ ] Story-point field ID is configured.
- [ ] Blocker marker configuration is explicit.
- [ ] Missing field IDs fail validation without fallback substitution.

### T004 — Create Jira mock fixtures

**Status:** Ready

**Description:** Create deterministic mock responses for project, board, sprint, issue, status, estimate, resolution, changelog, pagination, and error behavior.

**Acceptance criteria**

- [ ] Normal and missing-sprint fixtures exist.
- [ ] Resolution/reopen and missing-estimate fixtures exist.
- [ ] 429, 5xx, authentication, partial-data, pagination, duplicate, and stale-sprint cases exist.
- [ ] Fixtures are reusable by unit and integration tests.

## Phase 1: Monorepo foundation

### T005 — Configure npm workspaces

**Status:** Ready

**Description:** Configure `apps/web`, `apps/api`, and `packages/shared` as npm workspaces with common scripts.

**Acceptance criteria**

- [ ] The repository root installs all workspace dependencies.
- [ ] `test`, `build`, and `lint` scripts are available or intentionally omitted only if tooling is not present.
- [ ] Workspace imports resolve from shared packages.

### T006 — Configure TypeScript and build tooling

**Status:** Ready

**Description:** Add shared TypeScript settings and separate frontend/backend build configurations.

**Acceptance criteria**

- [ ] React/Vite and Express build successfully.
- [ ] Shared types compile in both applications.
- [ ] Strict or repository-standard type checking is enabled.

### T007 — Add loopback development configuration

**Status:** Ready

**Description:** Configure Express and Vite to bind only to `127.0.0.1` and add environment examples for non-secret values.

**Acceptance criteria**

- [ ] Neither service listens on a non-loopback interface.
- [ ] `.env.example` contains no credentials or tokens.
- [ ] The frontend and backend use a documented local port pair.

### T008 — Add PostgreSQL 15 Docker Compose

**Status:** Ready

**Description:** Add PostgreSQL 15, loopback networking, persistent named volume, health check, and development credentials.

**Acceptance criteria**

- [ ] `docker compose up` starts PostgreSQL 15.
- [ ] Database data persists across container restarts.
- [ ] The database port is exposed only for local development.
- [ ] Credentials are external configuration, not source or image values.

## Phase 2: Persistence and configuration

### T009 — Create database migrations

**Status:** Ready

**Description:** Add migrations for Jira configuration, reports, run records, and report review state.

**Acceptance criteria**

- [ ] Entities use UUID primary keys.
- [ ] Report/run foreign-key relationships exist.
- [ ] Created and updated timestamps exist.
- [ ] Fresh and repeated migration runs succeed.

### T010 — Implement configuration repository

**Status:** Ready

**Description:** Persist non-secret Jira configuration and implement environment-to-database precedence.

**Acceptance criteria**

- [ ] Environment overrides apply first.
- [ ] PostgreSQL stores non-secret configuration.
- [ ] OAuth secrets are never written to PostgreSQL or source.
- [ ] Missing or conflicting secrets fail validation.

### T011 — Implement run and report repositories

**Status:** Ready

**Description:** Add parameterized repository operations for run records, report metadata, review state, and canonical file paths.

**Acceptance criteria**

- [ ] Runs and reports can be created and queried.
- [ ] Report records reference run IDs.
- [ ] Run-history pagination returns 25 records.
- [ ] Review status and OS-user reviewer identity persist.

### T012 — Add database health and migration checks

**Status:** Ready

**Description:** Fail startup clearly when PostgreSQL is unavailable or migrations are not current.

**Acceptance criteria**

- [ ] Database health is distinguishable from Jira and file health.
- [ ] Migration status is reported before report generation.
- [ ] No automatic production migration is performed at startup.

### T013 — Configure safe rotating logs

**Status:** Ready

**Description:** Write application and run logs to `logs/app.log` and `logs/runs.log` with the prototype retention policy.

**Acceptance criteria**

- [ ] Retention is 30 days or 5 x 10 MB files, whichever is the repository policy result.
- [ ] Run ID and timestamps are included.
- [ ] Jira payloads, credentials, tokens, comments, and assignees are excluded.

## Phase 3: Jira integration

### T014 — Implement Jira OAuth 2.0 3LO

**Status:** Blocked

**Description:** Implement backend OAuth authorization, callback, refresh, and reauthorization.

**Acceptance criteria**

- [ ] Authorization opens through the backend callback flow.
- [ ] Read-only scopes are used.
- [ ] Refresh works for expired access tokens.
- [ ] Revoked consent produces a clear reauthorization state.
- [ ] The browser receives redacted status only.

### T015 — Implement macOS Keychain credential provider

**Status:** Ready

**Description:** Store and retrieve OAuth access/refresh credentials under the local OS account.

**Acceptance criteria**

- [ ] Credentials are retrievable only by the initializing OS account.
- [ ] No credential is exposed over HTTP or written to logs.
- [ ] Token rotation removes or replaces the old refresh credential.

### T016 — Implement Jira read-only API client

**Status:** Ready

**Description:** Add paginated Jira project, board, sprint, issue, status, estimate, resolution, and changelog retrieval.

**Acceptance criteria**

- [ ] All relevant collections paginate completely.
- [ ] Project, board, sprint, issue, and changelog data are isolated behind interfaces.
- [ ] API responses are mapped into typed domain structures.
- [ ] Raw Jira payloads do not cross the reporting or UI boundary.

### T017 — Implement retries and request failures

**Status:** Ready

**Description:** Implement timeouts, bounded retries, backoff, Retry-After handling, and safe error categories.

**Acceptance criteria**

- [ ] Each request has a 10-second timeout.
- [ ] Transient retries are capped at 3 attempts.
- [ ] Backoff is 1/2/4 seconds.
- [ ] HTTP 429 and 5xx are retried.
- [ ] 429 honors Retry-After up to 60 seconds.
- [ ] Authentication and validation failures are not retried.

### T018 — Implement Jira configuration validation

**Status:** Ready

**Description:** Validate site, project, board, active sprint, story-point field, and blocker marker configuration.

**Acceptance criteria**

- [ ] Missing required configuration produces a validation result.
- [ ] No active sprint or multiple active sprints fail validation.
- [ ] Story-point and blocker fields are not silently replaced with fallbacks.
- [ ] Read-only discovery does not provision or mutate Jira resources.

## Phase 4: Reporting domain

### T019 — Implement reporting-period calculation

**Status:** Ready

**Description:** Calculate `[generationTime - 7 days, generationTime]` and render Asia/Kolkata date/time values.

**Acceptance criteria**

- [ ] Jira timestamps are normalized to UTC for comparison.
- [ ] The end boundary is exclusive.
- [ ] Asia/Kolkata rendering is correct across DST fixtures.
- [ ] Filename dates use Asia/Kolkata.

### T020 — Implement completion and reopened-issue logic

**Status:** Ready

**Description:** Determine completion using Done status category and resolution or changelog evidence.

**Acceptance criteria**

- [ ] Resolutions inside the period and still resolved are counted.
- [ ] Reopened issues are excluded.
- [ ] Missing resolution evidence does not become a completion estimate.
- [ ] Resolution/reopen order is covered by fixtures.

### T021 — Implement sprint and story-point aggregation

**Status:** Ready

**Description:** Aggregate active-sprint committed, completed, and remaining story points.

**Acceptance criteria**

- [ ] `JIRA_STORY_POINTS_FIELD_ID` is required.
- [ ] Committed points use the active-sprint snapshot.
- [ ] Completed points require sprint membership and completed status.
- [ ] Remaining points are committed minus completed after validation.
- [ ] Missing estimates are reported as unavailable, not zero.

### T022 — Implement status, blocker, and missing-data classification

**Status:** Ready

**Description:** Classify in-progress and upcoming work, blocker states, and unavailable metrics.

**Acceptance criteria**

- [ ] Indeterminate/status-category started work is in progress.
- [ ] Active-sprint to-do/new work is upcoming.
- [ ] Blocker marker states distinguish confirmed, absent, missing marker, and unavailable data.
- [ ] Missing data appears in Data Notes or the relevant report section.

### T023 — Implement deterministic report rendering

**Status:** Ready

**Description:** Render the required Markdown report sections without AI or issue-level narrative.

**Acceptance criteria**

- [ ] All required report sections are present.
- [ ] Overall status is not invented during generation.
- [ ] No issue key, assignee, raw comment, or individual comparison appears.
- [ ] Verified facts, forecasts, decisions, risks, and data gaps are distinguishable.

## Phase 5: Generation and file safety

### T024 — Implement run locking and concurrency

**Status:** Ready

**Description:** Prevent overlapping manual or worker runs with an in-process lock and PostgreSQL run state.

**Acceptance criteria**

- [ ] A second concurrent run receives 409.
- [ ] A stale lock cannot leave future runs permanently blocked.
- [ ] Manual and worker invocations participate in the same lock.

### T025 — Implement scheduler-independent worker

**Status:** Ready

**Description:** Add a worker entry point that invokes the same report pipeline used by manual generation.

**Acceptance criteria**

- [ ] The worker runs without the React UI or an HTTP request.
- [ ] Trigger type is recorded as manual or scheduled.
- [ ] No `launchd` installation is required.

### T026 — Implement atomic report writing and revisions

**Status:** Ready

**Description:** Write Markdown atomically and select same-day revision filenames.

**Acceptance criteria**

- [ ] Existing report bytes remain unchanged on write failure.
- [ ] The first same-day report uses the base filename.
- [ ] Later revisions use `-r02`, `-r03`, and so on.
- [ ] Canonical file path is returned after success.

### T027 — Implement report/run reconciliation

**Status:** Ready

**Description:** Reconcile file and PostgreSQL outcomes after successful writes and process failures.

**Acceptance criteria**

- [ ] Database success is created only after file success.
- [ ] Database failure exposes an uncommitted reconciliation state.
- [ ] A report-write failure creates no successful report record.
- [ ] Crash reconciliation is manual and recorded safely.

### T028 — Implement overall-status review metadata

**Status:** Ready

**Description:** Preserve operator-selected overall status and optional review note.

**Acceptance criteria**

- [ ] Generation leaves overall status empty or unknown.
- [ ] Green, Amber, and Red choices persist.
- [ ] Reviewer and timestamp persist.
- [ ] Review metadata does not alter report narrative automatically.

## Phase 6: API and React UI

### T029 — Implement Express API routes

**Status:** Ready

**Description:** Implement configuration status/update, run creation/history, report retrieval, and report review routes.

**Acceptance criteria**

- [ ] All routes listed in the specification exist.
- [ ] Stable JSON success/error envelopes are used.
- [ ] Standard 400/401/403/404/409/429/5xx responses are applied.
- [ ] Raw Jira payloads and credentials are never returned.

### T030 — Implement React configuration and run dashboard

**Status:** Ready

**Description:** Add non-secret configuration status, OAuth initiation state, manual generation, and run history.

**Acceptance criteria**

- [ ] Required configuration status is visible.
- [ ] OAuth initiation has backend-only callback handling.
- [ ] Manual generation starts the generation pipeline.
- [ ] Run history pages contain 25 records.

### T031 — Implement report preview and review UI

**Status:** Ready

**Description:** Render aggregate report sections and allow operator review status selection.

**Acceptance criteria**

- [ ] Required report sections are visible.
- [ ] Missing-data messages are visible.
- [ ] Overall status and optional note can be saved.
- [ ] Marking reviewed does not distribute or publish the report.

### T032 — Add frontend usability states

**Status:** Ready

**Description:** Add loading, validation, upstream, internal-error, and keyboard/focus behavior.

**Acceptance criteria**

- [ ] Loading and failure states are explicit.
- [ ] Controls have visible focus and semantic labels.
- [ ] Desktop layout has no unhandled overflow or broken navigation.
- [ ] Mobile/responsive acceptance is not required for this prototype.

## Phase 7: Operations and documentation

### T033 — Add startup and migration commands

**Status:** Ready

**Description:** Document Docker Compose startup, PostgreSQL migration, reset, backup, restore, and application startup.

**Acceptance criteria**

- [ ] Fresh setup produces a runnable loopback prototype.
- [ ] Migration commands are explicit.
- [ ] Reset and backup commands are documented separately.
- [ ] Database credentials are not committed.

### T034 — Add operator runbook

**Status:** Ready

**Description:** Document manual generation, report review, OAuth setup, log inspection, failure recovery, and report opening.

**Acceptance criteria**

- [ ] Every operator action has a command or UI location.
- [ ] Failure states explain the next action.
- [ ] No external distribution step is documented.
- [ ] Confluence and `launchd` remain marked out of scope.

## Phase 8: Verification

### T035 — Add domain unit tests

**Status:** Ready

**Description:** Test configuration, period, timezone, completion, sprint, missing-estimate, blocker, and rendering logic.

**Acceptance criteria**

- [ ] Reporting boundaries and DST fixtures pass.
- [ ] Reopened issues are excluded.
- [ ] Missing estimates remain unavailable.
- [ ] Required Markdown sections render.

### T036 — Add Jira integration tests

**Status:** Ready

**Description:** Test OAuth, pagination, project/sprint/issue data, retries, authentication, 429, 5xx, and partial failures.

**Acceptance criteria**

- [ ] All T004 fixture families pass.
- [ ] 3-attempt retry behavior passes.
- [ ] Authentication and validation failures are not retried.
- [ ] Raw Jira payloads do not leak to UI or logs.

### T037 — Add database and repository tests

**Status:** Ready

**Description:** Test migrations and PostgreSQL persistence for configuration, run, report, and review entities.

**Acceptance criteria**

- [ ] Fresh migration succeeds.
- [ ] Foreign-key relationships and UUID IDs pass.
- [ ] Pagination and review persistence pass.
- [ ] No secret token is persisted.

### T038 — Add API and frontend tests

**Status:** Ready

**Description:** Test all route contracts and React review/configuration/run-history behavior.

**Acceptance criteria**

- [ ] Route status codes and JSON envelopes pass.
- [ ] Loopback-only behavior is verified.
- [ ] Report preview and review interactions pass.
- [ ] Loading and error states render correctly.

### T039 — Add failure-safety and concurrency tests

**Status:** Ready

**Description:** Test atomic writes, prior-report preservation, run locking, database/file mismatch, and crash recovery.

**Acceptance criteria**

- [ ] Report-write failure leaves prior bytes unchanged.
- [ ] Concurrent runs produce 409.
- [ ] Database/file mismatch is observable.
- [ ] Successful report creation has file and metadata consistency.

### T040 — Run full convergence review

**Status:** Ready

**Description:** Run the complete suite, security-focused diff review, and acceptance checklist.

**Acceptance criteria**

- [ ] All applicable acceptance criteria pass.
- [ ] Excluded features remain absent.
- [ ] No credentials or sensitive payloads enter source or logs.
- [ ] The prototype starts and generates a mocked report successfully.
