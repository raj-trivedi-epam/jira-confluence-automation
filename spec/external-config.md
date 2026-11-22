# External Jira Configuration Checklist

**Task:** T001 — Confirm Jira connection configuration
**Status:** Blocked

No live Jira values have been confirmed by a Jira administrator or operator.

## Proposed or supplied values

| Setting | Value | Confirmation status |
|---|---|---|
| Jira Cloud site | `https://company.atlassian.net` | Placeholder; not approved |
| Project key | `CLOUD` | Proposed; availability and authorization not confirmed |
| Board ID | Not provided; response was `Create one` | Missing numeric board ID |
| Active sprint | Not confirmed | Board and active-sprint behavior must be verified |

## Required evidence

- [ ] A Jira administrator confirms the Jira Cloud site URL.
- [ ] A Jira administrator confirms that project key `CLOUD` is available and permitted, or provides an approved replacement.
- [ ] The operator supplies the numeric ID of the confirmed active-sprint Scrum board.
- [ ] The board is confirmed to expose exactly one active sprint for reporting.
- [ ] A read-only configuration test confirms project and board discovery.

## Ready-to-configure names

```text
JIRA_SITE_URL=
JIRA_PROJECT_KEY=
JIRA_BOARD_ID=
JIRA_STORY_POINTS_FIELD_ID=
JIRA_BLOCKER_FIELD_ID=
JIRA_BLOCKER_LABEL=
```

Do not place OAuth access tokens, refresh tokens, passwords, or private keys in this file or in source control.

## Implementation status

Task T001 has a validation module that rejects unconfirmed placeholders and accepts only confirmed HTTPS Jira Cloud values, an approved project key, a positive numeric board ID, and a confirmed active sprint.

Live Jira discovery and mutation-free read-only verification remain blocked until the Jira administrator or operator supplies and confirms the real values.
