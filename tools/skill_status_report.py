import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Iterable, Mapping, Sequence, Union


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "dates must use YYYY-MM-DD format"
        ) from error


def _text(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _status(issue: Mapping[str, object]) -> tuple[str, str]:
    fields = issue.get("fields")
    if not isinstance(fields, Mapping) and isinstance(issue.get("status"), str):
        name = issue["status"]
        if name.lower() in ("done", "closed", "resolved"):
            return name, "done"
        if name.lower() in ("in progress", "active", "indeterminate"):
            return name, "indeterminate"
        if name.lower() in ("to do", "todo", "new", "open"):
            return name, "new"
        return name, "unknown"
    if not isinstance(fields, Mapping):
        return "Unknown", "unknown"
    status = fields.get("status")
    if not isinstance(status, Mapping):
        return "Unknown", "unknown"
    name = status.get("name")
    category = status.get("statusCategory")
    category_key = (
        category.get("key") if isinstance(category, Mapping) else None
    )
    return (
        _text(name) if isinstance(name, str) else "Unknown",
        category_key if isinstance(category_key, str) else "unknown",
    )


def format_status_report(
    issues: Iterable[Mapping[str, object]],
    start_date: Union[date, str],
    end_date: Union[date, str],
) -> str:
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = date.fromisoformat(end_date)
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")

    issue_list = list(issues)
    completed: list[Mapping[str, object]] = []
    in_progress: list[Mapping[str, object]] = []
    upcoming: list[Mapping[str, object]] = []
    unknown: list[Mapping[str, object]] = []

    for issue in issue_list:
        _, category = _status(issue)
        if category == "done":
            completed.append(issue)
        elif category == "indeterminate":
            in_progress.append(issue)
        elif category == "new":
            upcoming.append(issue)
        else:
            unknown.append(issue)

    executive_summary = (
        f"{len(completed)} issue(s) completed, "
        f"{len(in_progress)} issue(s) in progress, and "
        f"{len(upcoming)} issue(s) upcoming."
    )
    if unknown:
        executive_summary += (
            f" {len(unknown)} issue(s) have an unknown status and require review."
        )

    def count_summary(items: Sequence[Mapping[str, object]], empty: str) -> str:
        if not items:
            return f"- {empty}"
        return f"- {len(items)} issue(s)"

    return """# Weekly Status Report

**Reporting period:** {start}–{end}

## Executive Summary

- {summary}

## Completed

{completed}

## In Progress

{in_progress}

## Upcoming

{upcoming}

## Blockers

- No blocker information is available from the supplied issue data.

## Next Week

- Review delivery progress and resolve any unknown status data.
""".format(
        start=start_date.isoformat(),
        end=end_date.isoformat(),
        summary=executive_summary,
        completed=count_summary(completed, "No issues completed"),
        in_progress=count_summary(in_progress, "No issues in progress"),
        upcoming=count_summary(upcoming, "No upcoming issues"),
    )


def load_issues(args: argparse.Namespace) -> list[Mapping[str, object]]:
    if args.issues:
        candidate = Path(args.issues)
        if candidate.is_file():
            raw = candidate.read_text(encoding="utf-8")
        else:
            raw = args.issues
        return parse_issues_json(raw)
    if args.issues_file:
        raw = Path(args.issues_file).read_text(encoding="utf-8")
        return parse_issues_json(raw)
    elif args.issues_json:
        raw = args.issues_json
        return parse_issues_json(raw)
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
        return parse_issues_json(raw)
    else:
        return []


def parse_issues_json(raw: str) -> list[Mapping[str, object]]:
    if not raw.strip():
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("issues input must be valid JSON") from error
    if not isinstance(value, list):
        raise ValueError("issues JSON must be a list")
    if not all(isinstance(issue, dict) for issue in value):
        raise ValueError("each Jira issue must be a JSON object")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Format Jira issues as a Markdown weekly status report."
    )
    parser.add_argument("start_date", nargs="?", type=parse_date)
    parser.add_argument("end_date", nargs="?", type=parse_date)
    parser.add_argument("issues", nargs="?")
    parser.add_argument("--start-date", dest="start_date_option", type=parse_date)
    parser.add_argument("--end-date", dest="end_date_option", type=parse_date)
    parser.add_argument(
        "--issues",
        dest="issues_option",
        help="A JSON string or path to a JSON file containing Jira issues",
    )
    parser.add_argument(
        "--issues-file",
        help="Path to a JSON file containing a Jira issue list",
    )
    parser.add_argument(
        "--issues-json",
        help="A JSON string containing a Jira issue list",
    )
    args = parser.parse_args()

    start_date = args.start_date_option or args.start_date
    end_date = args.end_date_option or args.end_date
    if start_date is None or end_date is None:
        parser.error("start and end dates are required")
    args.issues = args.issues_option or args.issues

    try:
        issues = load_issues(args)
        report = format_status_report(issues, start_date, end_date)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    sys.stdout.write(report)


if __name__ == "__main__":
    main()
