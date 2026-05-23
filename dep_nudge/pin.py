"""Generate pinned requirements output from check results."""

from __future__ import annotations

from typing import Iterable

from dep_nudge.checker import CheckResult


def pin_line(result: CheckResult) -> str:
    """Return a pinned requirement line for a single result.

    If a newer version is available the line is pinned to the latest version.
    If the package is already up-to-date the existing specifier is preserved.
    If no version information is available the original raw string is returned.
    """
    req = result.requirement
    name = req.name

    if result.latest_version:
        return f"{name}=={result.latest_version}"

    if req.specifier:
        return f"{name}{req.specifier}"

    return req.raw


def generate_pinned(results: Iterable[CheckResult]) -> str:
    """Return a full pinned requirements file as a string.

    Each result is rendered as a pinned ``name==version`` line where possible.
    Results are separated by newlines and the output ends with a trailing
    newline so it can be written directly to a file.
    """
    lines = [pin_line(r) for r in results]
    return "\n".join(lines) + "\n" if lines else ""


def write_pinned(results: Iterable[CheckResult], path: str) -> int:
    """Write a pinned requirements file to *path*.

    Returns the number of requirements written.
    """
    result_list = list(results)
    content = generate_pinned(result_list)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return len(result_list)
