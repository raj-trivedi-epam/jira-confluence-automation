# Specification Clarification Review

**Status:** Reviewed for prototype scope; all gaps have a disposition below
**Sources reviewed:** `spec/constitution.md`, `spec/specification.md`, `project_spec.md`, `jira-dashboard-requirements.md`

## Critical gaps

### 1. Contradiction between repository proposals and the new prototype stack

The original specification proposes a Python command-line generator and macOS `launchd`, while the new specification requires a React 18/Vite frontend and Node.js/Express backend. This changes the deployment model and user interaction, but the specification does not state whether the Python implementation is superseded or may remain as a shared core.

**Decision needed:** Confirm that Node.js/Express is the authoritative implementation and whether existing Python code must be reused, replaced, or retained only for legacy compatibility.

### 2. Scope conflict: stakeholder report versus sprint dashboard

`jira-dashboard-requirements.md` requests sprint metrics refreshed every 15 minutes and displays work by assignee. The constitution and specification require aggregate-only stakeholder reports and explicitly exclude per-person comparisons and issue-level details.

**Decision needed:** Confirm whether the web prototype is limited to the weekly aggregate report or also includes a 15-minute Jira sprint dashboard. If both exist, define separate audiences and data-visibility boundaries.

### 3. Confluence scope is undefined

The project name includes Confluence, and the constitution mentions Confluence, but no target site, space, page, content format, OAuth flow, update behavior, or publication approval is defined.

**Decision needed:** Confirm whether Confluence is deferred entirely or whether a future feature has a concrete MVP. The specification should not combine “no active Confluence integration” with implied automated publication.

### 4. Product deployment model is unclear

The backend is described as local-first and scheduled through `launchd`, but no browser host, local URL, process lifecycle, startup mechanism, reverse proxy, or authentication model is defined.

**Decision needed:** Confirm whether React and Express run on one local machine, in Docker, or in a remote environment. Define who can access the UI and how local scheduler processes reach it.

### 5. Jira project setup is in scope inconsistently

US-01 and FR-01 validate or configure Jira setup, while the non-goals exclude creating a Jira project or changing permissions. The specification does not identify who can create or modify Jira setup.

**Decision needed:** Separate read-only reporting configuration from administrative Jira setup. Define whether setup validation is view-only or can provision project resources.

### 6. Read-only OAuth behavior is incomplete

The specification requires read-only OAuth but does not define:

- Jira Cloud OAuth provider and app-registration process
- Callback URL and browser/desktop authorization flow
- OAuth scopes
- Token storage and refresh ownership
- Consent, revocation, renewal, and reauthorization behavior
- Behavior for multiple Jira sites or users

**Decision needed:** Approve an OAuth architecture and an exact scope set before implementation.

### 7. Secret storage is not selected

The constitution allows environment variables or an operating-system secure credential store, while PostgreSQL is also mentioned. This leaves the implementation with multiple storage options.

**Decision needed:** Select one credential provider, define supported operating systems, and specify fallback behavior. Database records may reference credentials but must not contain reusable secret material unless separately approved.

## Unclear functional requirements

### 8. “Required data” is not measurable

FR-09 requires required data to pass validation, but the specification never defines a required-fields set or failure threshold.

Define explicitly:

- Which project, sprint, issue, status, estimate, resolution, and changelog fields are mandatory
- Whether missing optional fields permit partial report generation
- Whether data coverage below 100% is failure, warning, or usable with data notes
- How many Jira pages or issue records are required for a complete snapshot

### 9. Reporting-period boundaries are undefined

“The rolling seven days ending at generation time” does not define:

- Whether boundaries are inclusive or exclusive
- Whether resolution timestamps in Jira use UTC and are converted before comparison
- How timezone, DST, daylight savings, and clock changes affect the period
- Whether a report regenerated later replaces or creates another dated report

**Decision needed:** Provide exact boundary rules and a stable report-ID or overwrite policy.

### 10. Completion logic needs resolved-status validation

FR-05 requires resolution during the period and still resolved at report time, but Jira status categories and resolution fields can differ.

Define:

- The exact status category or resolution field used to establish completion
- Whether resolution timestamp must come from a changelog transition
- Whether issues resolved and reopened within the period count as completed
- Whether a reopened issue with no subsequent resolution is excluded
- How missing resolution timestamps are handled

### 11. Sprint date and sprint assignment rules are undefined

The system must use the active sprint, but no rule defines:

- Behavior when no sprint is active
- Behavior when multiple sprints are active
- Which sprint is used for a historical reporting period
- Whether future or closed sprints are included
- Sprint membership changes and moved-issue scope
- Which Scrum board is authoritative

### 12. Story-point aggregation is underspecified

The spec says to calculate committed, completed, and remaining points independently but does not define:

- Jira custom field ID or fallback behavior
- Whether completed means resolved in the reporting period or completed in the active sprint
- Whether remaining includes not-started and in-progress points or only unfinished work
- How issues moved into or out of a sprint affect committed totals
- How missing estimates are counted in issue count and story-point totals
- Whether unestimated work changes sprint-completion percentages

### 13. In-progress and upcoming definitions are missing

The report template and requirements do not define:

- Which Jira status categories are in progress
- Whether upcoming means backlog items, future sprint items, or both
- Whether upcoming includes items with future planned dates
- Limits for how many issues or what time horizon are included
- Whether summary text is generated from issue keys or aggregation only

### 14. Overall status rules are missing

The report template requires Green, Amber, or Red, but no objective rating rule exists.

Define at minimum:

- Sprint goal or commitment thresholds
- Blocker severity and escalation thresholds
- Missed-estimate and missing-data treatment
- Whether status is calculated, operator-selected, or calculated with manual override
- Required audit trail for overrides

### 15. Blocker/risk behavior is unresolved

The agreed Jira marker is unknown. The specification does not define impact, mitigation, owner, next-update date, severity, or whether unavailable marker data produces unavailable or no-blocker status.

It should also distinguish:

- `No confirmed blockers`
- `Blocker marker not configured`
- `Jira blocker data unavailable`

### 16. Report narrative generation is undefined

It is unclear whether executive summary and delivery sections are:

- Templates populated by metrics
- Derived by deterministic rules
- Written by an AI or other model
- Manually entered by the reviewer

The specification has no grammar, model, prompt, data-provenance, or editing requirements.

### 17. Manual report period selection is unresolved

US-02 permits a “selected or current reporting period,” while FR-04 appears to require a rolling seven-day period ending at generation time.

Define whether users may select arbitrary periods and, if not, remove “selected” from US-02.

### 18. Report persistence is undecided

FR-13 says PostgreSQL stores report records and review state, but Open Decision 9 leaves report text versus file path unresolved.

Define:

- Canonical report source
- Database/report consistency behavior
- Duplicate and concurrent generation behavior
- Retention and archival policy
- Restore behavior after moving or losing the local `reports/` directory
- Report export and deletion behavior

### 19. Report filename can collide

The filename is date-based and does not include a unique run or period. Multiple successful manual runs on the same date could overwrite each other.

Define collision handling, overwrite approval, revision suffixes, or unique report IDs.

### 20. Human-review workflow is incomplete

No authentication or reviewer identity model is defined. “Delivery Manager” review may be one-person local operation or a role-based workflow.

Define:

- Who may review
- Whether review is reversible
- Whether a report is locked after review
- Whether reviewed reports can be regenerated or edited
- Whether review requires a signature or confirmation action
- How reviewer identity is established locally

### 21. Report distribution is left ambiguous

The report must not be automatically distributed, but the UI and local report access do not define an approved manual export or copy step.

Confirm whether manual download, clipboard copy, local file opening, or Confluence publication is allowed.

## Scheduling and reliability gaps

### 22. `launchd` behavior is not specified

The specification requires a scheduled job but does not define:

- The launchd plist location and identity
- Working directory and environment
- Node process and log paths
- Start interval versus calendar interval
- Catch-up mechanism
- Behavior if the web server is stopped
- Timeout and overlap prevention
- Installation and removal commands

### 23. Scheduler and web-server availability are coupled ambiguously

A `launchd` job cannot reach an Express UI unless the Express process or a direct CLI/API-independent worker is running. The specification does not state whether the scheduler starts the backend or invokes the generation service separately.

### 24. Catch-up semantics are undefined

There is no maximum catch-up delay, missed-run limit, duplicate prevention, or policy for how a computer asleep for several weeks behaves.

### 25. Retry limits and rate limits are undefined

The specification says retries are bounded but gives no retry count, backoff schedule, retryable status codes, timeout, circuit breaker, or rate-limit behavior.

### 26. Concurrency and idempotency are insufficient

Repeated generation and concurrent manual/scheduled runs can overlap. The specification says generation operations should be idempotent or have explicit concurrency behavior but does not define locking.

Define a run-level lock, overlap handling, and transaction consistency across Jira fetches, PostgreSQL, and the filesystem.

### 27. Atomicity across database and filesystem is not addressed

An atomic file write protects the report file, but PostgreSQL run/report records may disagree if a database write or process crash occurs afterward.

Define recovery and reconciliation behavior for:

- Report written before database commit
- Database committed before report write
- Crash during review or status update

## API and data gaps

### 28. API routes and contracts are not specified

The specification names configuration, generation, review, and run-history operations but provides no HTTP methods, paths, request/response schemas, status codes, pagination, or authorization.

### 29. Authentication and authorization for the local web app are missing

The backend validates every request per the constitution, but no application login, local-session model, role model, CSRF strategy, or network exposure rule is provided.

This is a blocking gap for a browser-accessible Express application.

### 30. Data entities lack identity and lifecycle fields

`JiraConfiguration`, `Report`, and `RunRecord` lack primary/foreign keys and lifecycle definitions such as creation, update, deletion, soft-delete, and optimistic locking.

### 31. Configuration validation precedence is unclear

The specification does not define whether environment variables, database settings, or secure store values win when configuration conflicts.

### 32. PostgreSQL migrations and Docker lifecycle are underspecified

Define migration startup behavior, database health checks, volume persistence, backup/restore, port exposure, reset behavior, and local credentials. The constitution allows secret values outside the database but does not explain the complete local setup.

## Security and privacy gaps

### 33. Local network exposure is not constrained

“Local-first” does not define whether Express listens on localhost or all interfaces and whether Vite exposes the app on the network.

### 34. Browser secrets and OAuth are contradictory in detail

The browser must not receive credentials, but US-01 says the user configures integration and establish OAuth. It does not state whether only backend callbacks and non-secret status are shown.

Define the exact browser-visible configuration fields and forbidden fields.

### 35. Audit and access logs are not specified

The system must not log sensitive data, but no minimum audit fields, log location, retention, rotation, or log redaction policy are defined.

### 36. Secure credential storage also lacks threat boundaries

The secure store provider must be selected, but no threat model defines which process, service account, or local user can retrieve or rotate credentials.

## Testing and acceptance gaps

### 37. Acceptance criteria are mostly behavioral rather than measurable

The specification lacks sample thresholds and expected outputs for:

- The 7-day boundary
- Sprint story-point totals
- Missing estimates
- Reopened issues
- Retry counts
- Report status mapping
- File write failure
- Concurrent run behavior

### 38. The test matrix lacks Jira API fixture details

Mocked tests are listed, but the specification does not define required edge fixtures for:

- Empty sprints
- Missing custom fields
- Duplicate issue records
- Status churn
- Resolution and reopen timing
- Pagination truncation
- Partial API failure
- Stale active-sprint data

### 39. Accessibility and frontend quality are unspecified

No accessibility, keyboard, responsive, loading, or error-state requirements are stated for the React UI.

### 40. No performance or capacity targets are defined

The spec needs bounded targets for Jira issue volume, report generation duration, run-history retention, API response time, and concurrent user count.

## Contradictions and internal inconsistencies

### C-01: Dashboard requirements conflict with aggregate-only reporting

The sprint dashboard source requests assignee data and 15-minute refresh, while the constitution/specification removes issue-level and individual data from stakeholder reports. The new specification should clarify that this is a separate dashboard feature or remove it.

### C-02: Confluence is named but intentionally excluded

The constitution says the project delivers Jira/Confluence integration, but the specification makes Confluence publishing out of scope and lists future Confluence decisions. The scope statement should be renamed or explicitly mark this as Jira-first delivery.

### C-03: “Project setup validation” implies administrative setup

FR-01 validates project/group/board setup, but the non-goals exclude Jira setup and project creation. Clarify read-only discovery versus provisioning.

### C-04: Manual generation allows arbitrary periods while the format is weekly

US-02 mentions selecting a period, while FR-04 makes the normal reporting period a 7-day rolling period. Clarify or remove manual period selection.

### C-05: PostgreSQL is required but the file remains the report source

The system stores review state and report records in PostgreSQL, but generated Markdown is written to `reports/`. The canonical source and consistency guarantee are unknown.

### C-06: Previous project says Python; the current feature spec says Node.js

The source specification’s Python proposal and the feature specification’s Node/React proposal are not reconciled. Choose a stack and document supersession.

### C-07: Constitution allows secure credential alternatives

The constitution allows environment variables or OS secure storage, but the specification names Jira OAuth and “secure local credential storage” without selecting one. This is a technology decision, not merely an open implementation detail.

### C-08: Human review is required but no auth or role boundary exists

This makes it unclear who can mark a report reviewed and whether a reviewed state is trustworthy.

## Recommended clarification priority

1. Reconcile the implementation stack and determine whether Confluence and dashboard features are in scope.
2. Select the OAuth, credential-storage, local-deployment, and application-authentication models.
3. Define Jira custom fields, blocker marker, board/sprint selection, and status/resolution rules.
4. Define exact completion, sprint, missing-estimate, and overall-status calculations.
5. Define report-period boundaries, filename collision behavior, canonical storage, and atomic consistency.
6. Define scheduler lifecycle, run locking, retry counts, timeouts, and catch-up behavior.
7. Define API contracts and database schema.
8. Define measurable test and acceptance thresholds.

## Prototype Dispositions

The decisions below resolve every numbered gap and contradiction in this review.

| Gap | Disposition and resolved requirement |
|---|---|
| 1 | **Answer:** Node.js/Express is authoritative. Existing Python reporting code may be reused as reference only; prototype implementation is Node.js/TypeScript. |
| 2 | **Out of scope:** The 15-minute sprint dashboard and assignee-level views are not prototype features. The React UI covers weekly reports and run history only. |
| 3 | **Out of scope:** No Confluence read, write, OAuth, or publishing behavior is implemented in the prototype. |
| 4 | **Answer:** The app is local-only. Express and Vite bind to `127.0.0.1`; scheduled generation may invoke the backend generation module directly rather than HTTP. |
| 5 | **Out of scope:** Jira project provisioning and permission changes are not implemented. The app performs read-only discovery and validates configuration entered by the operator. |
| 6 | **Answer:** Use Jira Cloud OAuth 2.0 3LO with read-only scopes, an Authorization Code callback handled by the local Express server, automatic refresh using a refresh token, and reauthorization on revoked/expired consent. No multi-site/multi-user support is required. |
| 7 | **Answer:** Use the macOS Keychain as the prototype credential provider. Environment variables are allowed only for database/runtime configuration, never OAuth secrets or refresh tokens. |
| 8 | **Answer:** Required fields are Jira site, project key, board ID, active sprint, issue status, resolution state, story-point custom field, and resolution or changelog evidence. Missing project/sprint/status/resolution data fails the run; missing estimates or optional narrative fields generate explicit unavailable data. |
| 9 | **Answer:** The period is `[generationTime - 7 days, generationTime]`, with the end exclusive. Resolution timestamps are normalized to UTC, then compared using Asia/Kolkata for display and report dates. Manual regeneration writes a new run record and creates a timestamped revision rather than silently replacing an existing report. |
| 10 | **Answer:** Completion requires a Jira Done-category status and a resolution timestamp or validated resolution changelog transition in the period. Repeated resolution/reopen cycles count only a resolution that remains unresolved? No; count only if the issue is resolved at report time. Missing resolution evidence fails the issue rather than counting or estimating completion. |
| 11 | **Answer:** The configured board's currently active sprint is authoritative. No active sprint or multiple active sprints is a validation failure. Historical period and sprint snapshots are not prototype features. Issues moved in or out of the active sprint are excluded if the sprint membership snapshot cannot be validated. |
| 12 | **Answer:** The story-point field is configuration value `JIRA_STORY_POINTS_FIELD_ID` with no hard-coded fallback. Committed points are active-sprint snapshot values; completed points are completed issues also in that snapshot; remaining is committed minus completed, clamped to zero only after successful validation. Missing estimates are excluded from totals and listed as unavailable in report data notes. |
| 13 | **Answer:** In-progress means Jira statuses in the indeterminate/started status category. Upcoming means active-sprint issues in new/to-do categories. No backlog-wide upcoming horizon is included. Narrative prose is a deterministic aggregate summary with no issue keys or issue-level details. |
| 14 | **Answer:** Prototype overall status is operator-selected in the review UI. Green is “on track/no material risk,” Amber is “credible risk with mitigation/decision,” and Red is “commitment materially off track.” The choice and optional override note are stored with report review metadata. Generation never invents a status. |
| 15 | **Answer:** The blocker marker is a configurable field name, field ID, or label. The report distinguishes confirmed blockers, no confirmed blockers, marker not configured, and blocker data unavailable. Impact, mitigation/owner role, and next update date are rendered only when source data supplies them. |
| 16 | **Answer:** Executive Summary, Completed, In Progress, Upcoming, and Sprint Progress use deterministic templates from validated aggregates. No AI or external model generates report narrative in the prototype. A reviewer may correct generated narrative only if the report format and aggregate-only data rules remain intact. |
| 17 | **Out of scope:** Manual period selection is not implemented. Manual generation always uses the current rolling seven-day period. |
| 18 | **Answer:** The Markdown file in `reports/` is the canonical report artifact. PostgreSQL stores report metadata, review state, run history, and the absolute or repository-relative report path. Database/file mismatch is marked failed or inconsistent and must be reconciled manually; report retention is indefinite for the prototype. |
| 19 | **Answer:** Filenames use `weekly-status-report-YYYY-MM-DD.md`. A same-day revision is named `weekly-status-report-YYYY-MM-DD-rNN.md`, starting with `r02` for the second revision. `r01` may be omitted for the first report. |
| 20 | **Answer:** The local prototype has one operator identity derived from the local OS user and no role system. Review is reversible until the report is marked exported/shared externally, and exported state is not implemented in the prototype. |
| 21 | **Out of scope:** Automatic external distribution, download API, clipboard API, and Confluence publication are not implemented. The operator may open the local Markdown file manually. |
| 22 | **Answer:** `launchd` is optional and out-of-scope for prototype convergence because one-time scheduler setup and full catch-up behavior cannot be verified in this environment. The prototype must provide a scheduler-agnostic worker entry point, but no launchd plist is required. |
| 23 | **Answer:** Scheduled generation invokes the generation module directly or starts the backend worker; it must not depend on the React UI or an HTTP request to a running server. |
| 24 | **Out of scope:** Automated missed-run catch-up, catch-up limits, and sleep-awake recovery are not implemented. |
| 25 | **Answer:** Jira transient retries use at most 3 attempts, 1/2/4-second exponential backoff, and 10-second per-request timeout. Retry HTTP 429 and 5xx; on 429, honor `Retry-After` up to 60 seconds. Authentication and validation failures are not retried. |
| 26 | **Answer:** A process-wide run lock plus a PostgreSQL run row prevents overlap. A second run returns `409 Run already in progress` and does not start work. |
| 27 | **Answer:** Write the report atomically and then create the database record. On database failure, mark the generated file as unreviewed/uncommitted and expose reconciliation in run history. On report-write failure, do not create a successful database report. Crash reconciliation is manual and recorded as a skipped/failure state. |
| 28 | **Answer:** Prototype routes are `GET /api/configuration/status`, `GET /api/runs`, `POST /api/runs`, `GET /api/reports/:id`, `POST /api/reports/:id/review`, and `PATCH /api/configuration` only for non-secret configuration. JSON success/error envelopes and standard 400/401/403/404/409/429/5xx responses apply. |
| 29 | **Answer:** Bind Express and Vite to loopback only. The prototype has one trusted local operator, no remote authentication session, and no multi-user role model. State-changing API methods require a loopback-only binding check and CSRF protection is required if cookies are used. No cookies are required. |
| 30 | **Answer:** Use UUID primary keys and timestamps; foreign-key report/run relations are mandatory. Add status, soft-delete where relevant, and optimistic locking only if concurrent review/update is implemented. |
| 31 | **Answer:** Precedence is environment variables for process/runtime overrides, then PostgreSQL non-secret configuration, then the secure-store provider for secrets. Missing or conflicting secrets fail validation. |
| 32 | **Answer:** Docker Compose creates PostgreSQL 15 on loopback, migration startup is explicit rather than automatic in production, migration health is checked before runs, and a named volume persists data. Development reset and backup/restore commands must be documented. Database credentials remain in environment/secure configuration, not source or image. |
| 33 | **Answer:** Express and Vite bind to `127.0.0.1` only. PostgreSQL binds to Docker loopback or a Docker network not exposed to the host beyond the mapped development port. |
| 34 | **Answer:** The browser may submit non-secret Jira site/project/board/blocker configuration and initiate the OAuth action. The browser may display redacted authorization status, not tokens or refresh credentials. OAuth callback is backend-only. |
| 35 | **Answer:** Logs go to `logs/app.log` and `logs/runs.log`; 30-day retention, 10 MB per file, and 5 rotating files are the prototype defaults. Logs include run ID and timestamp, never Jira payloads or secrets. |
| 36 | **Answer:** Keychain credentials are retrievable only by the OS account that initialized OAuth. The backend process must run under that account and must not expose credentials over HTTP or log them. Token rotation revokes the old refresh token when successful. |
| 37 | **Answer:** Acceptance thresholds are: exact 7-day UTC-derived boundary, expected fixture totals, missing estimate as `unavailable`, reopened issues excluded, 3 retry attempts, overall status from review metadata, atomic write preserving prior bytes on failure, and duplicate run producing 409. |
| 38 | **Answer:** Required fixtures are no active sprint, multiple active sprints, missing story-point field, duplicate issues, resolved/reopened churn, one resolution in period and one outside, page truncation, 429, 5xx, auth failure, partial 2xx data, and stale sprint snapshot. |
| 39 | **Out of scope:** Formal accessibility audit and responsive mobile design are not prototype gates. The UI must provide semantic headings, keyboard-operable controls, visible focus, loading/error text, and desktop use only. |
| 40 | **Answer:** Target ≤1000 Jira issues per run, ≤60-second Jira/report pipeline at steady state, run-history pages of 25 records, and one local operator. API endpoints target <2-second response for non-generation calls. |
| C-01 | **Out of scope:** The 15-minute assignee sprint dashboard is not a prototype feature. |
| C-02 | **Out of scope:** Confluence integration and publication are deferred entirely. The name remains repository naming only. |
| C-03 | **Answer:** FR-01 means read-only discovery and validation. It does not create or modify Jira resources. |
| C-04 | **Out of scope:** Manual arbitrary periods are not supported; current rolling seven-day period only. |
| C-05 | **Answer:** Markdown file is canonical; PostgreSQL stores metadata and path only. |
| C-06 | **Answer:** Node.js/Express/TypeScript supersedes the Python CLI proposal for this prototype. Existing Python code is retained as reference only. |
| C-07 | **Answer:** macOS Keychain is selected. Environment variables are configuration-only. |
| C-08 | **Answer:** Only the local OS operator may review. Review state is not a security boundary unless application authentication is added later. |
