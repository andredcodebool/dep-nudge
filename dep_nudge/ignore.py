"""Support for .nudgeignore files — packages to skip during checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

DEFAULT_IGNORE_FILE = ".nudgeignore"


def load_ignore_list(path: str | Path = DEFAULT_IGNORE_FILE) -> set[str]:
    """Read a .nudgeignore file and return a set of normalised package names.

    Lines starting with '#' are treated as comments and ignored.
    Blank lines are skipped.
    Package names are lower-cased and hyphens are normalised to underscores.
    """
    ignore: set[str] = set()
    file = Path(path)
    if not file.exists():
        return ignore
    for raw in file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        ignore.add(_normalise(line))
    return ignore


def _normalise(name: str) -> str:
    """Normalise a package name for comparison (PEP 503)."""
    return re.sub(r"[-_.]+", "_", name).lower()


def apply_ignore(
    results: Iterable,
    ignore: set[str],
) -> list:
    """Return *results* with any package whose normalised name is in *ignore* removed."""
    return [
        r for r in results if _normalise(r.requirement.name) not in ignore
    ]
