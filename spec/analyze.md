# Task Analysis

**Status:** Analysis complete
**Sources reviewed:** `constitution.md`, `specification.md`, `plan.md`, `tasks.md`, `clarify.md`

## 1. Task Complexity and Risk Assessment

| Task | Complexity | Primary risks | Key dependencies |
|---|---|---|---|
| T001 — Confirm Jira connection configuration | Medium | Wrong site/project/board value; stale active sprint | Jira administrator; T004 |
| T002 — Confirm OAuth and Keychain configuration | High | OAuth callback issues; revoked tokens; insecure storage | T001; macOS Keychain |
| T003 — Confirm Jira field configuration | Medium | Wrong custom field ID; blocker marker unavailable | Jira administrator; T001 |
| T004 — Create Jira mock fixtures | Medium | Fixtures omit edge behavior or disagree with real Jira payloads | T001-T003 configuration values |
| T005 — Configure npm workspaces | Low | Workspace resolution or script configuration conflicts | Existing repository |
| T006 — Configure TypeScript/build tooling | Medium | Inconsistent frontend/backend compiler settings | T005 |
| T007 — Add loopback development configuration | Low | Accidental network exposure; wrong frontend API origin | T005-T006 |
| T008 — Add PostgreSQL 15 Docker Compose | Medium | Volume or credential misconfiguration; Docker/Desktop unavailable | T005; Docker |
| T009 — Create database migrations | Medium | Schema drift; wrong report/run lifecycle; migration rollback issues | T008 |
| T010 — Implement configuration repository | Medium | Secret leakage; precedence ambiguity | T009; T002-T003 |
| T011 — Implement run/report repositories | Medium | Inconsistent report/run state; pagination bugs | T009 |
| T012 — Add database health and migration checks | Medium | False startup failures; migration race | T008-T009 |
| T013 — Configure safe rotating logs | Low | Secret leakage; unclear retention interpretation | T005 |
| T014 — Implement Jira OAuth 3LO | High | Callback security; refresh failure; revoked consent | T002; T015; T016 |
| T015 — Implement macOS Keychain provider | High | OS-account mismatch; token rotation failure | macOS; T002 |
| T016 — Implement Jira read-only API client | High | Jira API differences; pagination omissions; stale payload mapping | T001-T004 |
| T017 — Implement retries/request failures | Medium | Retry storms; timeout/backoff mismatch; 429 handling | T016 |
| T018 — Implement Jira configuration validation | Medium | No active/multiple sprints; Jira setup assumptions | T001-T004; T016 |
| T019 — Implement reporting-period calculation | Medium | Boundary/DST bugs; timezone inconsistency | T004 |
| T020 — Implement completion/reopened logic | High | Incorrect resolution/reopen interpretation; missing evidence | T016; T019 |
| T021 — Implement sprint/story-point aggregation | High | Custom-field ambiguity; sprint membership/scope drift | T003; T016; T018 |
| T022 — Implement status/blocker/missing-data classification | High | Status-category mismatches; misleading blocker states | T016; T018; T003 |
| T023 — Implement deterministic report rendering | Medium | Template drift; accidental sensitive data; invalid status prose | T019-T022 |
| T024 — Implement run locking/concurrency | High | Cross-process lock failure; stale lock; split-brain runs | T009; T011 |
| T025 — Implement scheduler-independent worker | Medium | Worker bypasses UI/config initialization; duplicate schedule semantics | T024; T018; T023 |
| T026 — Implement atomic writing/revisions | Medium | Same-day filename collision; partial writes; permissions | T023 |
| T027 — Implement report/run reconciliation | High | Database/file inconsistency; crash recovery ambiguity | T011; T026 |
| T028 — Implement overall-status review metadata | Low | Operator status stored but no audit lock | T011; T031 |
| T029 — Implement Express API routes | Medium | Contract drift; loopback assumptions; payload exposure | T010-T012; T025-T027 |
| T030 — Implement React configuration/run dashboard | Medium | OAuth UX confusion; secret exposure; stale run state | T029; T014 |
| T031 — Implement report preview/review UI | Medium | Report edited incorrectly; reviewed state used as security | T023; T028-T030 |
| T032 — Add frontend usability states | Low | Missing error/focus behavior; inconsistent loading states | T029-T031 |
| T033 — Add startup/migration commands | Medium | Docker/data loss; migration/reset mismatch | T008-T012 |
| T034 — Add operator runbook | Low | Runbook becomes stale or includes excluded features | T033; all implementation tasks |
| T035 — Add domain unit tests | Medium | Fixtures do not cover DST, reopen, and missing estimates | T019-T023 |
| T036 — Add Jira integration tests | High | Mock/reality mismatch; OAuth test fragility | T004; T014-T018 |
| T037 — Add database/repository tests | Medium | Migration test isolation; secret persistence | T009-T012 |
| T038 — Add API/frontend tests | Medium | Contract drift; loopback and browser assumptions | T029-T032 |
| T039 — Add failure-safety/concurrency tests | High | Difficult crash simulation; lock cleanup unreliability | T024-T027 |
| T040 — Run full convergence review | High | Hidden scope drift; external Jira unavailable; acceptance gaps | T001-T039 |

## 2. Critical Dependency Chain

The shortest safe implementation sequence is:

```text
T001-T004
  -> T005-T008
  -> T009-T013
  -> T014-T018
  -> T019-T023
  -> T024-T028
  -> T029-T032
  -> T033-T034
  -> T035-T040
```

Tasks that block the first runnable integration are T001-T004, T005-T008, T009-T018, and T019-T027. T028-T034 enable the operator workflow. T035-T040 verify convergence.

External blocking tasks:

- T001-T003 and T014 require Jira/Keychain/operator decisions and cannot be completed fully offline.
- T002 is a prerequisite for live OAuth but T004 fixtures can proceed independently.
- T004 should begin before T016-T023 so integration and domain interfaces stabilize.

## 3. Missing Cross-Artifact Artifacts

The following concrete artifacts are not included in the specification, plan, or tasks, so implementation cannot proceed safely without them.

### 3.1 Environment and deployment artifacts

- Root `package.json` with npm workspaces.
- `apps/web/package.json`
- `apps/api/package.json`
- `packages/shared/package.json`
- `docker-compose.yml` or `compose.yaml`
- `.env.example`
- `.gitignore` updates for `.env*`, `node_modules`, logs, and PostgreSQL data
- `apps/api/tsconfig.json`
- `apps/web/tsconfig.json`
- root `tsconfig.base.json`
- Frontend Vite configuration
- Backend process entry point and worker entry point
- Migration CLI and scripts
- Log directory policy

### 3.2 Jira integration artifacts

- OAuth app registration and callback configuration document
- Keychain provider interface
- Jira API client interface
- Jira configuration schema
- Fixed story-point field ID configuration key
- Blocker marker configuration schema
- Mock fixture directory and fixture manifest
- Jira response-to-domain mapper

### 3.3 Data and persistence artifacts

- Migration files
- Database schema diagram or ERD
- Repository interfaces
- Run/report/review lifecycle definitions
- Reconciliation record type or reconciliation table
- Explicit soft-delete policy
- Backup and restore procedure
- Database reset procedure

### 3.4 API artifacts

- OpenAPI or equivalent JSON contract
- Stable JSON success/error envelope schemas
- Request/response DTOs
- HTTP route test matrix
- Loopback binding test
- Run pagination/cursor contract
- OAuth callback behavior contract
- CSRF decision record

### 3.5 Report artifacts

- Canonical report Markdown template
- Report filename and revision algorithm
- Report ID/run ID relationship
- Example successful and failed report outputs
- Missing-estimate and blocker-state examples
- Report reconciliation record format
- Review metadata model

### 3.6 Operations artifacts

- Docker startup and shutdown instructions
- PostgreSQL migration and backup instructions
- OAuth/Keychain setup guide
- Runbook
- Failure category and recovery matrix
- Logging redaction specification
- Known limitations document

### 3.7 Test artifacts

- Unit test configuration
- Mock Jira server or fixture loader
- Database test container setup
- API contract test setup
- Frontend test setup
- Atomic-write fault injection
- Crash/recovery test harness
- Convergence evidence checklist

## 4. Cross-Artifact Gaps and Contradictions

### G1 — API contract remains underspecified

The specification gives route names but no methods, status codes by scenario, payload fields, pagination parameter, or response examples. The task list says to implement routes but cannot produce a stable contract yet.

**Required fix:** Add an OpenAPI or JSON API contract to `spec/specification.md` or a separate `spec/api.md`.

### G2 — JSON envelope and error taxonomy are not defined

“Stable JSON success/error envelopes” are mentioned, but field names and error categories are absent.

**Required fix:** Define `{data, error, meta}` or an equivalent shape and the exact error codes for validation, auth, upstream, internal, conflict, and retryable failures.

### G3 — OAuth callback and Keychain interfaces are not implemented in artifacts

The spec requires OAuth and Keychain but no callback path, callback port, state/PKCE rules, token lease behavior, or provider interface is provided.

**Required fix:** Add OAuth callback route, state validation, PKCE decision, callback timeout, and Keychain provider interface.

### G4 — Required Jira data is not field-complete

The spec lists required concepts but not Jira REST fields/endpoints or custom-field definitions.

**Required fix:** Define endpoint families and required fields for project, board, sprint, issue, status, resolution, changelog, and story points.

### G5 — Active-sprint logic is underdefined

The spec says no or multiple active sprints fail, but not how sprint state is fetched or which board endpoint is authoritative.

**Required fix:** Define the board-to-sprint API order and exact active-sprint filter.

### G6 — Completion logic has an unresolved resolution timestamp rule

The spec allows either resolution timestamp or resolution changelog transition, but an issue may contain both and disagree.

**Required fix:** Define precedence: resolution timestamp, changelog transition, or reject conflicting evidence.

### G7 — Reopened issue definition is incomplete

The spec excludes reopened issues but does not define reopened-state evidence or a resolution/reopen sequence occurring entirely within the period.

**Required fix:** Define whether current reopened state or resolution/reopen history controls the total.

### G8 — Remaining story points clamping was not fully resolved

`clarify.md` says remaining is committed minus completed and clamped to zero only after validation, but no clamp rule is given for negative values.

**Required fix:** Define whether negative remaining is an inconsistency failure or a clamp with data note.

### G9 — Overall status is operator-selected, but no final-status artifact exists

The plan says status is review metadata, while the report structure requires Overall Status. The tasks do not define whether generation creates a placeholder or review status is merged into the Markdown file.

**Required fix:** Specify generation placeholder text and whether review status modifies a canonical copy or only database metadata.

### G10 — Report canonical storage and revision model disagree

The file is canonical, while database review metadata may become stale if the operator manually edits or moves the Markdown.

**Required fix:** Define manual edit detection, file hash, revision creation after manual edits, and canonical path validation.

### G11 — Same-day revision naming may not be atomic

Filename selection and file creation are not protected by the run lock against a second process or stale lock, and revision numbering is not transactionally reserved.

**Required fix:** Use the run UUID or reserve revision number under a database transaction before opening the file.

### G12 — Database-file reconciliation has no user workflow

The spec requires manual reconciliation but no reconciliation status, API, UI, or runbook procedure is defined.

**Required fix:** Add reconciliation states and API/runbook tasks for orphaned, missing, mismatched, and uncommitted reports.

### G13 — Log retention rule has two interpretations

T013 says 30 days or 5 x 10 MB, but those are not the same retention semantics and could implement two contradictory policies.

**Required fix:** Choose one primary policy and an optional secondary cap.

### G14 — Log directory is not in missing-artifact or startup tasks

T013 adds log files but T033 does not mention creating or securing `logs/`, and `.gitignore` is only part of a broad task.

**Required fix:** Add a log-directory startup and `.gitignore` acceptance requirement.

### G15 — Locking is not clearly process-wide or database-backed

T024 says process-wide and PostgreSQL state, but no lock row lease, owner, expiry, or stale-lock cleanup is defined.

**Required fix:** Define run-state transition and stale-run timeout/cleanup.

### G16 — Worker trigger type may claim scheduled execution despite no scheduler

T025 accepts a “scheduled” trigger but the prototype has no scheduler integration.

**Required fix:** Define CLI worker invocation and accept `manual` and `worker` as trigger types, or define scheduled trigger as future-only.

### G17 — Express API lacks HTTP authentication/callback security details

Loopback binding makes remote access unlikely, but the constitution also says state-changing backend operations require validation. The tasks do not specify loopback verification or OAuth state/PKCE verification.

**Required fix:** Implement loopback source check and OAuth state; document that loopback is not a security boundary against local processes.

### G18 — API status 401/403 are incompatible with no login model

The spec defines 401/403 in its global error requirements while the clarified prototype has no remote login model.

**Required fix:** Restrict 401/403 to OAuth/Jira authorization and document local-loopback authorization, or remove unused codes.

### G19 — CSRF is unresolved

The spec says CSRF is required if cookies are used and no cookies are required, so the tasks need no CSRF implementation if there is no session cookie.

**Disposition:** This is resolved by stateless loopback operations, but a browser callback or future cookie introduction should require a security review.

### G20 — Data entity details remain incomplete

The specification now has UUIDs and timestamps but no migrations, columns, constraints, indexes, soft-delete, or optimistic-lock fields.

**Required fix:** Add ERD or data dictionary and migration index requirements.

### G21 — API pagination contract is missing

T011/T030 specify 25-record run history but no URL parameters, sort order, or returned page metadata.

**Required fix:** Define `limit`, `cursor/offset`, ordering, and next-page fields.

### G22 — Frontend test tooling is not selected

No test runner, component library, or browser test tool is named.

**Required fix:** Select Vitest/React Testing Library or explicitly mark frontend test tooling as an implementation choice. Browser E2E is not currently required.

### G23 — PostgreSQL backup/reset behavior is underspecified

T033 says document backup/reset, but no backup format, restore path, named-volume location, or reset confirmation is specified.

**Required fix:** Add operational commands and destructive-action confirmation rules.

### G24 — Secret precedence creates a data-source contradiction

The spec says environment variables override PostgreSQL and Keychain secrets, but T002/T015 prevent OAuth secrets from environment variables.

**Required fix:** Clarify that secret precedence applies only to database/runtime secrets; OAuth secrets come exclusively from Keychain and environment overrides are not permitted.

### G25 — `T001-T003` external blockers have no completion owner

Tasks are marked Blocked but no owner or required evidence artifact is assigned.

**Required fix:** Add owner, due/dependency evidence, and a “confirmed external configuration” file or operator checklist.

### G26 — No task covers report export or local opening behavior

T034 says document report opening, but no implementation task defines platform command or path.

**Disposition:** Report opening is out of scope for code. T034 should document manual file browsing rather than app-controlled opening.

### G27 — No explicit task covers Docker compose volume backup

T008/T033 split setup and operations but do not add a backup implementation test.

**Required fix:** Add volume backup/restore verification to T033 or T039.

### G28 — No explicit task covers `.gitignore` for report and log artifacts

Report retention and logs may create untracked or committed artifacts accidentally.

**Required fix:** Add `.gitignore` requirements for `logs/`, local database data, `.env*`, `node_modules`, and an explicit policy for committed `reports/`.

### G29 — No task verifies no Jira data enters run/history logs

T013/T036 cover log redaction, but T040 convergence should include an explicit scan for secrets, issue keys, comments, assignee names, and raw payloads.

**Required fix:** Add secret/redaction assertion to T040 and T036.

### G30 — Performance task is missing

The plan names 1000 issues/60 seconds/2-second APIs/25-run pagination, but no task implements or measures these targets.

**Required fix:** Add a performance benchmark task or acceptance assertions to T040.

### G31 — Accessibility task is present but downgraded

T032 gives semantic/focus requirements; T039 formal audit is out of scope. This is internally consistent, but no automated accessibility check is required.

**Disposition:** Keep the basic keyboard/focus acceptance and record formal WCAG audit out of scope.

### G32 — Convergence task may depend on unavailable live Jira

T040 requires mocked and secret scans, but live Jira can remain blocked. The spec should permit mock/live evidence separation.

**Required fix:** Mark external live-Jira acceptance blocked separately from local mock convergence.

## 5. Task Coverage Summary

The task set covers all major implementation phases, but the following plan/spec requirements lack a dedicated task:

- A stable API schema and OpenAPI contract
- OAuth callback/security details and Keychain interface
- Database ERD/migration data dictionary
- Canonical report template and report/revision collision algorithm
- Reconciliation user workflow
- Secret/redaction evidence
- Performance benchmark
- Volume backup/restore verification
- Explicit `.gitignore` and report/log policy
- External live-Jira acceptance separation

The task set also lacks explicit tasks for adding package manifests and test fixtures beyond T004/T005. T008 and T033 imply Docker setup, but T005/T006 should name lockfile/package artifact acceptance.

## 6. Severity Ranking

### Blocking before implementation

- G1-G6
- G8-G12
- G15-G17
- G20-G21
- G24-G25
- G27-G30
- G32

### Blocking before UI/API convergence

- G7
- G9-G12
- G13-G14
- G18-G19
- G22
- G26-G29

### Blocking only before external live validation

- G3-G5
- G24-G25
- G32

## 7. Recommended Artifacts Before Implementation

1. `spec/api-contract.md` or `spec/openapi.yaml`
2. `spec/data-model.md`
3. `spec/jira-integration.md`
4. `spec/report-format.md`
5. `spec/operations.md`
6. `spec/reconciliation.md`
7. `.env.example`
8. `docker-compose.yml`
9. `package.json` workspaces and workspace manifests
10. Mock Jira fixture manifest
11. Database migration directory
12. Test setup and fixture directories
13. Operational runbook
14. Known limitations and acceptance evidence document

## 8. Final Assessment

The task breakdown is comprehensive for feature-level implementation but is not yet executable without several interface and data artifacts. The highest implementation risk is not frontend or database setup; it is the unresolved Jira evidence rules, OAuth/Keychain integration, report canonical/revision semantics, and file/database reconciliation.

Before implementation starts, resolve or artifact G1-G12 and G15-G20, then add the missing operations and verification tasks identified above. Mock-only convergence can begin independently, but live Jira generation should remain blocked until T001-T003 and T014 receive confirmed external configuration.
