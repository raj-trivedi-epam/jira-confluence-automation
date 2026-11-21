# Jira/Confluence Automation Toolkit

An AI-assisted project for automating Jira-based weekly stakeholder reporting.
The current implementation is a Python library that reads Jira Cloud data and
generates an aggregate-only Markdown status report. It does not currently
connect to Confluence or publish reports.

## Current capabilities

- Read-only Jira Cloud REST client with pagination and bounded retries for
  transient network, rate-limit, and server failures.
- Weekly report generation covering completed work from the rolling seven-day
  period and the current active sprint.
- Aggregate reporting for statuses and story points, with missing estimates
  disclosed instead of treated as zero.
- Atomic dated report output under `reports/`, so a failed fetch does not
  replace an existing report.
- Tests using Python's standard library; the core has no third-party package
  dependencies.

The report omits issue keys, summaries, and assignee names. A human must review
the report before sharing it. Emailing and automatic publishing are not
implemented.

## Requirements

- Python 3.9 or newer.
- Jira Cloud access and an approved read-only OAuth integration to run against
  live Jira data.

## Run the tests

From the repository root:

```bash
python3 -m unittest discover -s tests -v
```

## Use the report library

The report generator is currently a library, not a configured command-line
application. After confirming the Jira site, project key, board ID, OAuth flow,
and secure credential provider, integrate a token provider and call it as
follows:

```python
from datetime import datetime

from weekly_status.generator import generate_weekly_report
from weekly_status.jira_client import JiraClient


def current_oauth_access_token():
    # Return a current token from the approved secure credential provider.
    raise NotImplementedError("Connect the approved credential provider.")


jira = JiraClient(
    "https://your-site.atlassian.net",
    current_oauth_access_token,
)
report_path = generate_weekly_report(
    jira_client=jira,
    project_key="CLOUD",
    board_id=123,
    reports_dir="reports",
    generated_at=datetime.now().astimezone(),
)
print(report_path)
```

The site URL, project key, and board ID above are examples. `CLOUD` is only a
proposed project key; confirm it and the board before use. The token-provider
function is a placeholder and must be implemented before this example can access
Jira.

The generator writes
`reports/weekly-status-report-YYYY-MM-DD.md`, using `Asia/Kolkata` for report
dates and times.

## Current limitations and open integration work

- OAuth app registration, token refresh, and secure credential storage are not
  configured. Never hard-code credentials or write them to reports or logs.
- The project key `CLOUD`, Jira project setup, Scrum board, and board ID require
  confirmation.
- No Jira blocker field, flag, or label has been agreed; blocker data is
  reported as unavailable until one is configured.
- The overall delivery status and support decisions require human review.
- A scheduled CLI workflow, `launchd` setup, and missed-run recovery are not
  implemented.
- Confluence API integration and automatic publishing are not implemented.

See [the project specification](project_spec.md) for requirements and open
decisions, and [the weekly status core guide](weekly_status/README.md) for
additional implementation details.

## Repository layout

- `weekly_status/` — Jira client, aggregation, report rendering, and generation
  library.
- `tests/` — unit and integration-boundary tests.
- `reports/` — report templates and generated report examples.
- `instructions/` — task-specific guidance for report and Confluence workflows.
- `tools/` — supporting scripts and local MCP demonstration servers.
