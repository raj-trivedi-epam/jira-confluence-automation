- Use `tools/skill_status_report.py` when the user asks to format Jira issues into a Markdown weekly status report.
- Supply the reporting period as `start_date` and `end_date` in `YYYY-MM-DD` format.
- Supply Jira issues as positional JSON, `--issues-file`, `--issues-json`, or JSON piped through standard input.
- Invoke the script from the project root with positional arguments:
  `python3 tools/skill_status_report.py <start_date> <end_date> '<issues_json>'`
- Invoke the script with a JSON file:
  `python3 tools/skill_status_report.py <start_date> <end_date> --issues-file <path>`
- Invoke the script with named date and issue options:
  `python3 tools/skill_status_report.py --start-date <start_date> --end-date <end_date> --issues-json '<issues_json>'`
- Accept Jira issue objects containing a `fields.status.name` and `fields.status.statusCategory.key` when status data follows Jira's standard shape.
- Accept a simplified issue object containing a top-level `status` string.
- Classify status categories `done`, `indeterminate`, and `new` into Completed, In Progress, and Upcoming sections.
- Preserve unknown statuses and report them for review rather than guessing their category.
- Present the script's Markdown output unchanged, including reporting period and section headings.
- Do not invent blocker or delivery information that is absent from the supplied Jira issues.
- If dates are missing or reversed, request corrected dates before invoking the script.
- If issue JSON is missing or invalid, report the input error and do not fabricate issues.
