"""Parser for requirements.txt files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


REQUIREMENT_LINE_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_\-\.]+)"
    r"(?P<extras>\[[^\]]+\])?"
    r"(?P<specifier>[^;#\s]*)?"
    r"(?P<marker>[^#]*)?"
    r"(?P<comment>#.*)?$"
)


@dataclass
class Requirement:
    """Represents a single parsed requirement."""

    name: str
    specifier: str
    line_number: int
    raw_line: str
    extras: Optional[str] = None

    def __str__(self) -> str:
        extras = self.extras or ""
        return f"{self.name}{extras}{self.specifier}"


def parse_requirements(filepath: str | Path) -> List[Requirement]:
    """Parse a requirements file and return a list of Requirement objects.

    Args:
        filepath: Path to the requirements file.

    Returns:
        List of parsed Requirement instances.

    Raises:
        FileNotFoundError: If the requirements file does not exist.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Requirements file not found: {filepath}")

    requirements: List[Requirement] = []

    with path.open(encoding="utf-8") as fh:
        for line_number, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()

            # Skip blank lines, comments, and options (e.g. -r, --index-url)
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            match = REQUIREMENT_LINE_RE.match(line)
            if not match:
                continue

            name = match.group("name")
            specifier = (match.group("specifier") or "").strip()
            extras = match.group("extras")

            requirements.append(
                Requirement(
                    name=name,
                    specifier=specifier,
                    line_number=line_number,
                    raw_line=raw_line.rstrip("\n"),
                    extras=extras,
                )
            )

    return requirements
