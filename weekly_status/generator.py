"""Fetch, format, and atomically save one weekly Jira status report."""

from datetime import timedelta

from .report import REPORT_TIMEZONE, format_weekly_report, write_report


def generate_weekly_report(
    jira_client,
    project_key,
    board_id,
    reports_dir,
    generated_at,
    story_points_field_name="Story Points",
):
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must be timezone-aware.")
    if not project_key:
        raise ValueError("project_key is required.")
    if isinstance(board_id, bool) or not isinstance(board_id, int) or board_id < 1:
        raise ValueError("board_id must be a positive integer.")

    field_id = jira_client.find_field_id(story_points_field_name)
    sprint = jira_client.active_sprint(board_id)
    sprint_id = sprint.get("id")
    if not isinstance(sprint_id, int) or sprint_id < 1:
        raise ValueError("Jira active sprint response has no valid sprint ID.")

    fields = ["status", "resolution", "resolutiondate", field_id]
    sprint_issues = jira_client.sprint_issues(
        sprint_id, fields, project_key=project_key
    )
    local_generated = generated_at.astimezone(REPORT_TIMEZONE)
    start_date = (local_generated - timedelta(days=8)).date()
    end_date = local_generated.date() + timedelta(days=2)
    completed_issues = jira_client.resolved_issues(
        project_key, start_date, end_date, fields
    )
    report_text = format_weekly_report(
        generated_at=generated_at,
        active_sprint=sprint,
        sprint_issues=sprint_issues,
        completed_issues=completed_issues,
        story_points_field=field_id,
    )
    return write_report(report_text, reports_dir, generated_at)
