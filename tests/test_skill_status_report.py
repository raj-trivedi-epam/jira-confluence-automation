import unittest

from tools.skill_status_report import format_status_report


def issue(status_name, category):
    return {
        "fields": {
            "status": {
                "name": status_name,
                "statusCategory": {"key": category},
            }
        }
    }


class SkillStatusReportTests(unittest.TestCase):
    def test_formats_issues_by_status_section(self):
        report = format_status_report(
            [
                issue("Done", "done"),
                issue("In Progress", "indeterminate"),
                issue("To Do", "new"),
            ],
            "2026-11-11",
            "2026-11-18",
        )

        self.assertIn("**Reporting period:** 2026-11-11–2026-11-18", report)
        self.assertIn("## Completed", report)
        self.assertIn("- 1 issue(s)", report)
        self.assertIn("## In Progress", report)
        self.assertIn("## Upcoming", report)
        self.assertIn("## Blockers", report)
        self.assertIn("## Next Week", report)

    def test_rejects_reversed_date_range(self):
        with self.assertRaisesRegex(ValueError, "end_date"):
            format_status_report([], "2026-11-18", "2026-11-11")


if __name__ == "__main__":
    unittest.main()
