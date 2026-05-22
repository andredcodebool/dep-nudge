"""Format and print check results as a human-readable report."""

from __future__ import annotations

from typing import TextIO
import sys

from dep_nudge.checker import CheckResult

# ANSI colour codes
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_RESET = "\033[0m"


def _colourise(text: str, colour: str, use_colour: bool) -> str:
    if not use_colour:
        return text
    return f"{colour}{text}{_RESET}"


def format_result(result: CheckResult, use_colour: bool = True) -> str:
    """Return a single formatted line for a CheckResult."""
    if result.error:
        label = _colourise("ERROR", _RED, use_colour)
        return f"  [{label}] {result.requirement.name}: {result.error}"

    if result.is_outdated:
        label = _colourise("OUTDATED", _YELLOW, use_colour)
        return (
            f"  [{label}] {result.requirement.name} "
            f"{result.current_version} → {result.latest_version}"
        )

    label = _colourise("OK", _GREEN, use_colour)
    return f"  [{label}] {result.requirement.name} {result.current_version}"


def print_report(
    results: list[CheckResult],
    out: TextIO = sys.stdout,
    use_colour: bool = True,
) -> None:
    """Print a full report for all check results."""
    total = len(results)
    outdated = sum(1 for r in results if r.is_outdated)
    errors = sum(1 for r in results if r.error)

    print("dep-nudge report", file=out)
    print("=" * 40, file=out)

    for result in results:
        print(format_result(result, use_colour=use_colour), file=out)

    print("=" * 40, file=out)
    summary = (
        f"Checked: {total}  "
        f"Outdated: {outdated}  "
        f"Errors: {errors}"
    )
    print(summary, file=out)


def has_outdated(results: list[CheckResult]) -> bool:
    """Return True if any result indicates an outdated package."""
    return any(r.is_outdated for r in results)
