# Jira/Confluence Automation Constitution

## Purpose

This project delivers a web application and supporting services that integrate with Jira Cloud and Confluence. The primary product is an aggregate-only weekly stakeholder status workflow for the Cloud Project: Jira data is collected, validated, summarized, and presented for human review before any external sharing.

Confluence integration is out of the active implementation scope until its requirements and authorization model are defined. No Confluence content may be read or updated automatically without an approved, explicitly scoped integration.

## Technology Principles

1. **Frontend**
   - Use React 18 and Vite.
   - Prefer typed TypeScript components and small, reusable UI modules.
   - Keep secrets, OAuth credentials, Jira credentials, and privileged API access out of browser code.
   - Do not expose issue-level or personally identifying data unless a requirement explicitly authorizes it.

2. **Backend**
   - Use Node.js with Express.
   - Organize HTTP concerns separately from business logic, integration clients, and persistence.
   - Validate and authorize every request at the API boundary.
   - Use read-only Jira OAuth for Jira data access unless write behavior is separately approved.
   - Use bounded pagination and retries for Jira and Confluence API calls.
   - Respect API rate limits and return actionable, non-sensitive errors.

3. **Database**
   - Use PostgreSQL 15.
   - Run PostgreSQL in Docker for local development.
   - Use migrations for every schema change.
   - Store application configuration and non-sensitive metadata in the database.
   - Do not store Jira or Confluence OAuth tokens as plain application configuration or source-code values.
   - Prefer parameterized queries and a migration-supported query or ORM layer.

4. **Containers**
   - Use Docker Compose or equivalent container configuration for local services.
   - Pin application and database images by a supported major or explicit version.
   - Never include credentials or tokens in images or committed Compose files.

## Core Product Rules

1. Jira reporting must remain aggregate-only. Shared reports must not include issue keys, raw comments, assignee names, or individual performance comparisons.
2. Reports must cover the confirmed rolling seven-day period and active sprint where applicable.
3. The report generation time and reporting dates must use Asia/Kolkata.
4. Missing estimates or unavailable metrics must be reported as unavailable, never as zero or a fabricated value.
5. Completion logic must exclude reopened issues and count only work resolved within the reporting period and still resolved at report time.
6. Blocker reporting must use only a confirmed Jira blocker field, flag, or label. Comments or issue wording must not infer blockers.
7. A human must review reports before they are shared.
8. The application must not email, publish, or distribute reports automatically unless the requirement is explicitly changed and approved.

## Scheduling and Failure Safety

1. A weekly Friday 3:00 PM Asia/Kolkata schedule is required only after the target scheduler is validated.
2. Missed-run catch-up behavior must be implemented only when the target scheduler supports it and the behavior is documented.
3. A failed data fetch or validation failure must leave the previous successful report untouched.
4. Report writes must be atomic and validated before replacement.
5. Transient failures may use bounded retries; permanent failures must produce a clear local failure status.
6. Operational logs must identify run time and outcome without recording sensitive Jira or Confluence content.

## Security and Privacy

1. Secrets must come from environment variables or an operating-system secure credential store.
2. Committed files must not contain passwords, access tokens, refresh tokens, private keys, or connection strings with credentials.
3. OAuth scopes must be least-privilege and read-only where the workflow does not require writes.
4. API responses and logs must avoid unnecessary personal, issue-level, or confidential project data.
5. Backend authorization and input validation are mandatory for every privileged operation.
6. Confluence publication or updates require separate approval and a narrowly scoped permission model.

## Data and Integration Conventions

1. Jira pagination must be complete and bounded.
2. Jira data transformations must separate fetching, validation, aggregation, and rendering.
3. Sprint, status, story-point, resolution, and changelog calculations must be traceable and testable.
4. The project key, board, blocker marker, OAuth configuration, and stakeholder rules must be validated before production use.
5. External API failures must be distinguishable from data-validation failures and application defects.
6. Do not silently substitute missing source data.

## Testing Principles

1. Use tests for configuration, date ranges, Asia/Kolkata handling, report naming, aggregation, missing estimates, reopened issues, blocker handling, retries, atomic writes, and failure behavior.
2. Unit-test transformations independently from Jira and Confluence HTTP clients.
3. Use mocked external APIs for deterministic integration tests.
4. Test database migrations and persistence behavior in PostgreSQL 15.
5. Test frontend behavior and API contracts separately.
6. Run the smallest relevant test set during development and the complete suite before convergence.

## Architecture and Change Boundaries

1. Keep a clear boundary between React presentation, Express HTTP behavior, integration logic, aggregation logic, persistence, and scheduled execution.
2. Prefer small modules with explicit interfaces over cross-layer imports.
3. Do not add a framework or library when the standard platform and existing project dependencies are sufficient.
4. Make precise, reversible changes; do not silently expand scope or change confirmed requirements.
5. Generated reports are implementation artifacts and must not contain confidential or unnecessary source data.

## Acceptance and Convergence

No feature is complete until:

1. It satisfies the relevant functional and acceptance criteria.
2. Required external setup and open decisions are explicitly documented.
3. Tests cover normal, missing-data, retry, and failure paths.
4. Reports remain aggregate-only and fail safely.
5. Credentials and sensitive data are absent from source control and logs.
6. The implementation, specification, tests, and operational documentation are consistent.
7. A human can understand and review the result without relying on implementation folklore.

## Governance

This constitution defines project-level guardrails. Confirmed requirements in `project_spec.md` take precedence over proposed technical approaches. Open decisions and unresolved assumptions must remain visible and must not be invented as facts.

Changes to this constitution require a documented rationale and an updated spec or plan when they affect product behavior, security, integrations, reporting rules, or testing requirements.
