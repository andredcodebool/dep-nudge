"""Output formatters for dep-nudge reports."""

from __future__ import annotations

import json
import csv
import io
from typing import List

from dep_nudge.checker import CheckResult
from dep_nudge.vulnerability import Vulnerability


SUPPORTED_FORMATS = ("text", "json", "csv")


def _result_to_dict(result: CheckResult) -> dict:
    """Serialise a CheckResult to a plain dictionary."""
    vulns: List[Vulnerability] = getattr(result, "vulnerabilities", []) or []
    return {
        "package": result.requirement.name,
        "current": result.requirement.specifier,
        "latest": result.latest_version,
        "outdated": result.is_outdated,
        "vulnerabilities": [
            {
                "id": v.vuln_id,
                "aliases": v.aliases,
                "details": v.details,
                "fixed_in": v.fixed_in,
            }
            for v in vulns
        ],
    }


def format_json(results: List[CheckResult]) -> str:
    """Return a JSON string representing *results*."""
    return json.dumps([_result_to_dict(r) for r in results], indent=2)


def format_csv(results: List[CheckResult]) -> str:
    """Return a CSV string representing *results* (one row per package)."""
    buf = io.StringIO()
    fieldnames = ["package", "current", "latest", "outdated", "vulnerability_ids"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for result in results:
        d = _result_to_dict(result)
        writer.writerow(
            {
                "package": d["package"],
                "current": d["current"],
                "latest": d["latest"],
                "outdated": d["outdated"],
                "vulnerability_ids": ";".join(
                    v["id"] for v in d["vulnerabilities"]
                ),
            }
        )
    return buf.getvalue()


def render(results: List[CheckResult], fmt: str) -> str:
    """Dispatch to the correct formatter for *fmt*.

    Args:
        results: List of check results to format.
        fmt: One of ``'json'`` or ``'csv'``.  Any other value raises
             ``ValueError``.

    Returns:
        Formatted string.
    """
    if fmt == "json":
        return format_json(results)
    if fmt == "csv":
        return format_csv(results)
    raise ValueError(f"Unsupported format {fmt!r}. Choose from: {SUPPORTED_FORMATS}")
