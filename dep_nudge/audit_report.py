"""Render a human-readable audit report from AuditResult objects."""

from __future__ import annotations

from typing import List, Sequence

from dep_nudge.audit import AuditResult
from dep_nudge.report import _colourise

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_BOLD = "\033[1m"


def _status_label(result: AuditResult, colour: bool) -> str:
    if result.is_vulnerable:
        label = "VULNERABLE"
        return _colourise(label, _RED, colour)
    if result.is_outdated:
        label = "OUTDATED"
        return _colourise(label, _YELLOW, colour)
    return _colourise("OK", _GREEN, colour)


def format_audit_result(result: AuditResult, colour: bool = True) -> str:
    """Return a formatted single-package audit line (plus vuln details)."""
    check = result.check
    req = check.requirement
    status = _status_label(result, colour)
    latest = check.latest_version or "unknown"
    current = check.current_version or req.specifier or "unspecified"
    lines = [f"{_BOLD}{req.name}{_RESET if colour else ''} [{current} -> {latest}] {status}"]
    for vuln in result.vulnerabilities:
        lines.append(f"  ⚠  {vuln.vuln_id}: {vuln.details}")
        if vuln.aliases:
            lines.append(f"     aliases: {', '.join(vuln.aliases)}")
    return "\n".join(lines)


def print_audit_report(
    results: Sequence[AuditResult],
    colour: bool = True,
    only_attention: bool = False,
) -> None:
    """Print a full audit report to stdout."""
    filtered = [r for r in results if r.needs_attention] if only_attention else list(results)
    if not filtered:
        print("All packages are up-to-date and vulnerability-free.")
        return
    for result in filtered:
        print(format_audit_result(result, colour=colour))
    total = len(results)
    outdated = sum(1 for r in results if r.is_outdated)
    vulnerable = sum(1 for r in results if r.is_vulnerable)
    print(f"\n{total} package(s) scanned — {outdated} outdated, {vulnerable} vulnerable.")
