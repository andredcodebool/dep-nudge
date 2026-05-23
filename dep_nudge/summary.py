"""Summary statistics for a collection of CheckResults."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from dep_nudge.checker import CheckResult


@dataclass
class Summary:
    """Aggregated statistics derived from a list of CheckResults."""

    total: int = 0
    up_to_date: int = 0
    outdated: int = 0
    vulnerable: int = 0
    unknown: int = 0
    packages: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        lines = [
            f"Packages checked : {self.total}",
            f"  Up-to-date     : {self.up_to_date}",
            f"  Outdated       : {self.outdated}",
            f"  Vulnerable     : {self.vulnerable}",
            f"  Unknown        : {self.unknown}",
        ]
        return "\n".join(lines)


def build_summary(results: List[CheckResult]) -> Summary:
    """Compute a :class:`Summary` from *results*.

    A result is counted as:
    - *up_to_date*  – has a latest version and it matches the pinned version.
    - *outdated*    – has a latest version and it does not match the pinned version.
    - *vulnerable*  – has one or more associated vulnerabilities (may overlap
                      with outdated).
    - *unknown*     – latest version could not be determined.
    """
    summary = Summary(total=len(results))

    for result in results:
        summary.packages.append(result.requirement.name)

        if result.vulnerabilities:
            summary.vulnerable += 1

        if result.latest is None:
            summary.unknown += 1
        elif result.is_outdated:
            summary.outdated += 1
        else:
            summary.up_to_date += 1

    return summary


def summary_to_dict(summary: Summary) -> dict:
    """Return a plain-dict representation suitable for JSON serialisation."""
    return {
        "total": summary.total,
        "up_to_date": summary.up_to_date,
        "outdated": summary.outdated,
        "vulnerable": summary.vulnerable,
        "unknown": summary.unknown,
    }
