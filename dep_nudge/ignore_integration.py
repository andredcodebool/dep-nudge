"""Integration helpers: locate and load the ignore file relative to a
requirements file, then apply it to a list of CheckResults.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from dep_nudge.ignore import apply_ignore, load_ignore_list

DEFAULT_IGNORE_FILENAME = ".nudgeignore"


def resolve_ignore_file(requirements_path: str | Path) -> Path:
    """Return the .nudgeignore path that sits alongside *requirements_path*.

    The ignore file is looked for in the same directory as the requirements
    file.  If that directory has no .nudgeignore the current working directory
    is tried as a fallback.
    """
    req_dir = Path(requirements_path).resolve().parent
    candidate = req_dir / DEFAULT_IGNORE_FILENAME
    if candidate.exists():
        return candidate
    return Path.cwd() / DEFAULT_IGNORE_FILENAME


def apply_ignore_for_requirements(
    results: Iterable,
    requirements_path: str | Path,
    ignore_file: str | Path | None = None,
) -> list:
    """Load the appropriate ignore list and filter *results*.

    Parameters
    ----------
    results:
        Iterable of ``CheckResult`` objects.
    requirements_path:
        Path to the requirements file being processed (used to locate the
        default .nudgeignore when *ignore_file* is *None*).
    ignore_file:
        Explicit path to an ignore file.  When supplied this takes precedence
        over the auto-resolved path.
    """
    path = Path(ignore_file) if ignore_file is not None else resolve_ignore_file(requirements_path)
    ignore = load_ignore_list(path)
    return apply_ignore(list(results), ignore)
