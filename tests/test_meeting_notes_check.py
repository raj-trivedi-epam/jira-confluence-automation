import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from tools.check_meeting_notes import main, missing_sections


COMPLETE_NOTE = """# Meeting Notes

## Meeting Date and Time
## Participants
## Agenda
## Decisions Made
## Action Items
## Dependencies
## Risks
## Next Meeting
"""


class MeetingNotesCheckTests(unittest.TestCase):
    def test_accepts_common_heading_aliases_for_required_sections(self):
        self.assertEqual([], missing_sections(COMPLETE_NOTE))

    def test_section_mentions_in_body_do_not_count_as_headings(self):
        self.assertEqual(
            [
                "Date",
                "Attendees",
                "Agenda",
                "Decisions",
                "Action Items",
                "Dependencies",
                "Risks",
                "Next Meeting",
            ],
            missing_sections(
                "This note mentions date, attendees, agenda, decisions, action "
                "items, dependencies, risks, and the next meeting."
            ),
        )

    def test_processes_each_matching_note_and_reports_missing_sections(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "planning-meeting.md").write_text(
                "# Planning Meeting\n## Date\n", encoding="utf-8"
            )
            (root / "archive.md").write_text(
                COMPLETE_NOTE.replace("# Meeting Notes", "# Team Meeting Minutes"),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "# Project\nMeeting notes are stored elsewhere.\n",
                encoding="utf-8",
            )
            ignored = root / ".venv"
            ignored.mkdir()
            (ignored / "vendor-meeting.md").write_text(
                "# Vendor Meeting\n", encoding="utf-8"
            )

            output = StringIO()
            with redirect_stdout(output):
                result = main([str(root)])

        self.assertEqual(1, result)
        self.assertIn("planning-meeting.md:", output.getvalue())
        self.assertIn("archive.md:", output.getvalue())
        self.assertNotIn("README.md:", output.getvalue())
        self.assertNotIn("vendor-meeting.md:", output.getvalue())
        self.assertIn("Missing sections: Attendees, Agenda", output.getvalue())
        self.assertIn("All required sections are present.", output.getvalue())
        self.assertIn("Checked 2 meeting-note file(s).", output.getvalue())


if __name__ == "__main__":
    unittest.main()
