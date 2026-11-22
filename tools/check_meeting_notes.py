import argparse
import os
import re
from pathlib import Path
from typing import Optional


REQUIRED_SECTIONS = {
    "Date": (
        "date",
        "dates",
        "meeting date",
        "date and time",
        "date time",
        "meeting date and time",
    ),
    "Attendees": ("attendee", "attendees", "participants", "present"),
    "Agenda": ("agenda",),
    "Decisions": ("decision", "decisions", "decisions made", "outcomes"),
    "Action Items": ("action items", "actions", "action points", "follow ups"),
    "Dependencies": ("dependency", "dependencies"),
    "Risks": ("risk", "risks"),
    "Next Meeting": ("next meeting", "follow up meeting", "followup meeting"),
}

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
}

_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
_MEETING_NOTE_HEADING = re.compile(
    r"\b(?:meeting\s+(?:notes?|minutes?)|minutes(?:\s+of\s+(?:the\s+)?meeting)?|"
    r"notes?\s+(?:from|of)\s+(?:the\s+)?meeting)\b",
    re.IGNORECASE,
)


def _normalize_heading(value: str) -> str:
    value = re.sub(r"[*_`]", "", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _is_meeting_note(path: Path, content: str) -> bool:
    filename = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", path.stem)
    filename_words = re.sub(r"[^a-z0-9]+", " ", filename.casefold())
    if re.search(r"\b(meeting|minutes)\b", filename_words):
        return True

    return any(
        _MEETING_NOTE_HEADING.search(match.group(1))
        for line in content.splitlines()
        if (match := _HEADING.match(line))
    )


def find_meeting_notes(root: Path) -> list[tuple[Path, str]]:
    if not root.is_dir():
        raise ValueError(f"scan root is not a directory: {root}")

    notes = []
    for current, directories, filenames in os.walk(root, onerror=_raise_walk_error):
        directories[:] = sorted(
            name for name in directories if name not in IGNORED_DIRECTORIES
        )
        for filename in sorted(filenames):
            path = Path(current) / filename
            if path.suffix.casefold() not in {".md", ".markdown"}:
                continue
            content = path.read_text(encoding="utf-8")
            if _is_meeting_note(path, content):
                notes.append((path, content))

    return sorted(notes, key=lambda note: note[0].as_posix().casefold())


def _raise_walk_error(error: OSError) -> None:
    raise error


def missing_sections(markdown: str) -> list[str]:
    headings = {
        _normalize_heading(match.group(1))
        for line in markdown.splitlines()
        if (match := _HEADING.match(line))
    }
    missing = []
    for section, aliases in REQUIRED_SECTIONS.items():
        normalized_aliases = {_normalize_heading(alias) for alias in aliases}
        if headings.isdisjoint(normalized_aliases):
            missing.append(section)
    return missing


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check required sections in repository meeting notes."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository or directory to scan (defaults to the repository root)",
    )
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()

    try:
        notes = find_meeting_notes(root)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if not notes:
        print(f"No meeting-note Markdown files found under {root}.")
        return 0

    has_missing_sections = False
    for path, content in notes:
        missing = missing_sections(content)
        print(f"{path.relative_to(root)}:")
        if missing:
            has_missing_sections = True
            print(f"  Missing sections: {', '.join(missing)}")
        else:
            print("  All required sections are present.")

    print(f"Checked {len(notes)} meeting-note file(s).")
    return 1 if has_missing_sections else 0


if __name__ == "__main__":
    raise SystemExit(main())
