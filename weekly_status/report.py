"""Aggregate Jira sprint data into a stakeholder-safe Markdown report."""

import os
import tempfile
from datetime import datetime, timedelta, timezone
from math import isfinite
from pathlib import Path
from zoneinfo import ZoneInfo


REPORT_TIMEZONE = ZoneInfo("Asia/Kolkata")


def _issue_status(issue):
    fields = issue.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("Jira issue is missing its fields object.")
    status = fields.get("status")
    if not isinstance(status, dict) or not isinstance(status.get("name"), str):
        raise ValueError("Jira issue is missing its status name.")
    category = status.get("statusCategory")
    category_key = category.get("key") if isinstance(category, dict) else None
    if category_key not in ("new", "indeterminate", "done"):
        raise ValueError("Jira issue has an unknown status category.")
    return status["name"], category_key


def _issue_points(issue, story_points_field):
    fields = issue.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("Jira issue is missing its fields object.")
    points = fields.get(story_points_field)
    if points is None:
        return None
    if (
        isinstance(points, bool)
        or not isinstance(points, (int, float))
        or not isfinite(points)
    ):
        raise ValueError("Jira story points must be numeric or empty.")
    return points


def _format_points(points):
    if points is None:
        return "N/A"
    if int(points) == points:
        return str(int(points))
    return "{:g}".format(points)


def _parse_jira_datetime(value):
    if not isinstance(value, str):
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    if len(normalized) > 5 and normalized[-5] in ("+", "-") and normalized[-3] != ":":
        normalized = normalized[:-2] + ":" + normalized[-2:]
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _markdown_text(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def _format_sprint_date(value):
    parsed = _parse_jira_datetime(value)
    if parsed is None:
        return "Not recorded"
    return parsed.astimezone(REPORT_TIMEZONE).strftime("%B %-d, %Y")


def format_weekly_report(
    generated_at,
    active_sprint,
    sprint_issues,
    completed_issues,
    story_points_field,
    blocker_issues=None,
):
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must be timezone-aware.")
    local_generated = generated_at.astimezone(REPORT_TIMEZONE)
    period_start = local_generated - timedelta(days=7)
    sprint_start = _format_sprint_date(active_sprint.get("startDate"))
    sprint_end = _format_sprint_date(active_sprint.get("endDate"))
    sprint_name = _markdown_text(active_sprint.get("name") or "Active sprint")
    sprint_goal = _markdown_text(active_sprint.get("goal") or "Not recorded")

    completed_count = 0
    completed_points = 0
    completed_unestimated = 0
    for issue in completed_issues:
        _, category = _issue_status(issue)
        fields = issue["fields"]
        resolution = fields.get("resolution")
        resolved_at = _parse_jira_datetime(fields.get("resolutiondate"))
        if (
            category != "done"
            or resolution is None
            or resolved_at is None
            or not (period_start <= resolved_at <= local_generated)
        ):
            continue
        completed_count += 1
        points = _issue_points(issue, story_points_field)
        if points is None:
            completed_unestimated += 1
        else:
            completed_points += points

    status_counts = {}
    committed_points = 0
    completed_sprint_points = 0
    remaining_points = 0
    sprint_unestimated = 0
    todo_count = 0
    in_progress_count = 0
    for issue in sprint_issues:
        status_name, category = _issue_status(issue)
        status_counts[status_name] = status_counts.get(status_name, 0) + 1
        points = _issue_points(issue, story_points_field)
        if points is None:
            sprint_unestimated += 1
        else:
            committed_points += points
            if category == "done":
                completed_sprint_points += points
            else:
                remaining_points += points
        if category == "new":
            todo_count += 1
        elif category == "indeterminate":
            in_progress_count += 1

    if blocker_issues is None:
        blocker_summary = "Blocker data unavailable; no Jira blocker marker is configured."
    elif blocker_issues:
        blocker_summary = "{} issue(s) are marked as blockers.".format(
            len(blocker_issues)
        )
    else:
        blocker_summary = "No blockers identified from the configured Jira marker."

    completed_summary = "{} issue(s), {} story points".format(
        completed_count, _format_points(completed_points)
    )
    if completed_unestimated:
        completed_summary += "; {} completed issue(s) lack estimates".format(
            completed_unestimated
        )

    status_lines = [
        "- {}: {} issue(s)".format(_markdown_text(name), count)
        for name, count in sorted(status_counts.items(), key=lambda item: item[0].lower())
    ]
    if not status_lines:
        status_lines = ["- No active sprint issues were returned."]
    sprint_notes = []
    if sprint_unestimated:
        sprint_notes.append(
            "{} active sprint issue(s) have no story-point estimate".format(
                sprint_unestimated
            )
        )
    if blocker_issues is None:
        sprint_notes.append("blockers are unavailable until a Jira marker is agreed")
    sprint_notes.append(
        "overall status and decisions require manual review; no Jira rules are configured"
    )
    notes = sprint_notes

    return """# Weekly Status Report — Cloud Project

**Reporting period:** {}–{} (rolling seven days)
**Generated:** {}
**Overall status:** Not assessed — manual review required.

## Executive Summary

{} issue(s) were resolved during the reporting period ({}). Active sprint progress is shown below; delivery status and risks require human review.

## Delivery Update

### Completed

- {}

### In Progress

- {} issue(s) are currently in an In Progress status category.

### Upcoming

- {} issue(s) are currently in the To Do status category within the active sprint.

## Sprint Progress

**Sprint:** {}
**Sprint dates:** {}–{}
**Sprint goal:** {}

| Measure | Value |
| --- | ---: |
| Known active-sprint story points | {} |
| Completed story points | {} |
| Remaining story points | {} |

Status breakdown:
{}

## Blockers and Risks

- {}

## Decisions or Support Needed

- Not available from the configured Jira data; review manually.

## Data Notes

{}
""".format(
        period_start.strftime("%B %-d, %Y"),
        local_generated.strftime("%B %-d, %Y"),
        local_generated.strftime("%B %-d, %Y, %-I:%M %p %Z"),
        completed_count,
        _format_points(completed_points),
        completed_summary,
        in_progress_count,
        todo_count,
        sprint_name,
        sprint_start,
        sprint_end,
        sprint_goal,
        _format_points(committed_points),
        _format_points(completed_sprint_points),
        _format_points(remaining_points),
        "\n".join(status_lines),
        blocker_summary,
        "\n".join("- {}".format(_markdown_text(note)) for note in notes),
    )


def write_report(report_text, reports_dir, generated_at):
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must be timezone-aware.")
    report_date = generated_at.astimezone(REPORT_TIMEZONE).date().isoformat()
    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)
    target = reports_path / "weekly-status-report-{}.md".format(report_date)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(reports_path),
            prefix=".weekly-status-report-",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = temporary.name
            temporary.write(report_text)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, target)
    except OSError:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)
        raise
    return target
