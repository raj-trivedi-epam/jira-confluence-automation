# TODO

# Project Tasks

## Phase 1: Setup
– [x] Create project repository
– [x] Configure .gitignore
– [x] Set up development environment (`.venv/` using Python 3.9.6; no application dependencies added yet)

## Phase 2: Implementation
– [x] Create read-only Jira data-fetching module with pagination and bounded retries
– [x] Build report template (`reports/template.md` already exists)
– [x] Add aggregate formatting logic and atomic dated-report writing

## Pending Integration Setup
– [ ] Confirm the Jira project key and intended Scrum board ID
– [ ] Implement the approved OAuth flow and secure token-provider integration
– [ ] Agree on the Jira blocker marker
– [ ] Run an end-to-end report against the confirmed Jira project and board

## Progress Notes
The data-fetching and report-generation core is implemented in `weekly_status/`.
It requires an injected OAuth token provider and a confirmed board ID; it does not
store credentials or invent blocker data. See `weekly_status/README.md` for current
usage and integration boundaries.
