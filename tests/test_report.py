import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from weekly_status.generator import generate_weekly_report
from weekly_status.report import format_weekly_report, write_report


class FakeJiraClient:
    def __init__(self, fail_on=None):
        self.fail_on = fail_on
        self.calls = []

    def find_field_id(self, field_name):
        self.calls.append(("find_field_id", field_name))
        if self.fail_on == "find_field_id":
            raise RuntimeError("field lookup failed")
        return "customfield_10016"

    def active_sprint(self, board_id):
        self.calls.append(("active_sprint", board_id))
        if self.fail_on == "active_sprint":
            raise RuntimeError("sprint lookup failed")
        return {
            "id": 42,
            "name": "Sprint 4",
            "goal": "Finish the reporting foundation",
            "startDate": "2026-11-09T09:00:00.000Z",
            "endDate": "2026-11-20T09:00:00.000Z",
        }

    def sprint_issues(self, sprint_id, fields, project_key=None):
        self.calls.append(("sprint_issues", sprint_id, fields, project_key))
        if self.fail_on == "sprint_issues":
            raise RuntimeError("sprint issues failed")
        return [
            issue("Done", "done", 5),
            issue("In Progress", "indeterminate", 3),
            issue("To Do", "new", None),
        ]

    def resolved_issues(self, project_key, start_date, end_date, fields):
        self.calls.append(
            ("resolved_issues", project_key, start_date, end_date, fields)
        )
        if self.fail_on == "resolved_issues":
            raise RuntimeError("resolved issue search failed")
        return [
            issue(
                "Done",
                "done",
                3,
                resolution={"name": "Fixed"},
                resolutiondate="2026-11-17T10:00:00.000+0000",
                key="CLOUD-1",
            ),
            issue(
                "Reopened",
                "indeterminate",
                8,
                resolution=None,
                resolutiondate="2026-11-17T10:00:00.000+0000",
                key="CLOUD-2",
            ),
            issue(
                "Done",
                "done",
                13,
                resolution={"name": "Fixed"},
                resolutiondate="2026-11-10T10:00:00.000+0000",
                key="CLOUD-3",
            ),
        ]


def issue(
    status_name,
    category,
    points,
    resolution="sentinel",
    resolutiondate=None,
    key="CLOUD-9",
):
    if resolution == "sentinel":
        resolution = {"name": "Fixed"} if category == "done" else None
    fields = {
        "status": {
            "name": status_name,
            "statusCategory": {"key": category},
        },
        "customfield_10016": points,
        "resolution": resolution,
        "resolutiondate": resolutiondate,
    }
    return {"key": key, "fields": fields}


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.generated_at = datetime(
            2026, 11, 18, 15, 0, tzinfo=ZoneInfo("Asia/Kolkata")
        )

    def test_report_aggregates_data_and_excludes_reopened_or_out_of_period_issues(self):
        jira = FakeJiraClient()
        with tempfile.TemporaryDirectory() as reports_dir:
            report_path = generate_weekly_report(
                jira,
                "CLOUD",
                7,
                reports_dir,
                self.generated_at,
            )
            report = Path(report_path).read_text(encoding="utf-8")

        self.assertIn("1 issue(s), 3 story points", report)
        self.assertIn("Known active-sprint story points | 8", report)
        self.assertIn("Completed story points | 5", report)
        self.assertIn("Remaining story points | 3", report)
        self.assertIn("1 active sprint issue(s) have no story-point estimate", report)
        self.assertIn("Blocker data unavailable", report)
        self.assertNotIn("CLOUD-1", report)
        self.assertNotIn("CLOUD-2", report)
        self.assertEqual("find_field_id", jira.calls[0][0])
        self.assertEqual("active_sprint", jira.calls[1][0])
        self.assertEqual("sprint_issues", jira.calls[2][0])
        self.assertEqual("CLOUD", jira.calls[2][3])
        self.assertEqual("resolved_issues", jira.calls[3][0])

    def test_failed_fetch_does_not_replace_previous_report(self):
        with tempfile.TemporaryDirectory() as reports_dir:
            target = Path(reports_dir) / "weekly-status-report-2026-11-18.md"
            target.write_text("previous report", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "resolved issue search failed"):
                generate_weekly_report(
                    FakeJiraClient(fail_on="resolved_issues"),
                    "CLOUD",
                    7,
                    reports_dir,
                    self.generated_at,
                )

            self.assertEqual("previous report", target.read_text(encoding="utf-8"))

    def test_formatter_requires_timezone_aware_generation_time(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            format_weekly_report(
                datetime(2026, 11, 18, 15),
                {"id": 1},
                [],
                [],
                "customfield_10016",
            )

    def test_report_write_uses_kolkata_date_and_replaces_atomically(self):
        with tempfile.TemporaryDirectory() as reports_dir:
            generated_at = datetime(2026, 11, 17, 19, 0, tzinfo=timezone.utc)

            target = write_report("updated", reports_dir, generated_at)

            self.assertEqual(
                "weekly-status-report-2026-11-18.md", Path(target).name
            )
            self.assertEqual("updated", Path(target).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
