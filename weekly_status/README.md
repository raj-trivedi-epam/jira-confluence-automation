# Weekly status report core

This package provides a read-only Jira Cloud client and a report-generation
library. It uses only the Python standard library.

## Current capabilities

- Uses Jira Cloud REST GET requests with an OAuth bearer token provided by a
  callback.
- Retries transient network, rate-limit, and server failures a bounded number
  of times; paginates both Agile API results and JQL search results.
- Finds the unique Jira field named `Story Points` (or a caller-supplied field
  name).
- Restricts active-sprint issues to the configured project key.
- Aggregates current active-sprint status and story-point progress, and counts
  only issues resolved within the rolling seven-day period that are still
  resolved at report time.
- Writes a dated Markdown report atomically under `reports/`. A Jira fetch or
  validation failure happens before the existing dated report is replaced.
- Omits issue keys, summaries, and assignee names from the report. Missing
  estimates and the unconfigured blocker marker are disclosed instead of being
  treated as zero or as “no blockers.”

## Integration boundary

The project key `CLOUD` is only a proposed default in the specification; confirm
it before use. The Scrum board ID is required and must be confirmed to represent
the intended project sprint work. The package does not create Jira projects or
boards.

The OAuth flow, app registration, refresh handling, and secure-store integration
are not configured yet. `JiraClient` accepts a callback that must return a
current OAuth access token from the approved secure credential provider. Do not
hard-code a token or put it in a report, source file, or logs. The caller must
implement expiry/refresh behavior; this package never persists credentials.

No blocker marker has been agreed. Until one is defined and wired into data
retrieval, reports state that blocker information is unavailable. Overall status
and decisions/support requests also require human review.

## Library usage

After confirming the project key, board ID, OAuth flow, and credential provider,
use the core as follows:

```python
from datetime import datetime

from weekly_status.generator import generate_weekly_report
from weekly_status.jira_client import JiraClient


def current_oauth_access_token():
    # Read a current token from the approved secure credential provider.
    ...


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

The example's site, project key, board ID, and token provider are placeholders;
the generator is a library, not yet a configured command-line or scheduled
application.

## Tests

Run the standard-library tests from the project root:

```bash
python3 -m unittest discover -s tests -v
```
