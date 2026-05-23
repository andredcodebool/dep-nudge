"""Audit module: combines check and vulnerability results into a unified audit report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from dep_nudge.checker import CheckResult, check_requirements
from dep_nudge.vulnerability import Vulnerability, fetch_vulnerabilities
from dep_nudge.parser import Requirement


@dataclass
class AuditResult:
    """Unified result combining version check and vulnerability data for a single package."""

    check: CheckResult
    vulnerabilities: List[Vulnerability] = field(default_factory=list)

    @property
    def package(self) -> str:
        return self.check.requirement.name

    @property
    def is_outdated(self) -> bool:
        return self.check.is_outdated

    @property
    def is_vulnerable(self) -> bool:
        return len(self.vulnerabilities) > 0

    @property
    def needs_attention(self) -> bool:
        return self.is_outdated or self.is_vulnerable

    def __str__(self) -> str:
        parts = [str(self.check)]
        for vuln in self.vulnerabilities:
            parts.append(f"  {vuln}")
        return "\n".join(parts)


def audit_requirements(
    requirements: List[Requirement],
    skip_vulns: bool = False,
) -> List[AuditResult]:
    """Run version checks and (optionally) vulnerability lookups for all requirements."""
    check_results = check_requirements(requirements)
    audit_results: List[AuditResult] = []

    for result in check_results:
        vulns: List[Vulnerability] = []
        if not skip_vulns:
            vulns = fetch_vulnerabilities(result.requirement)
        audit_results.append(AuditResult(check=result, vulnerabilities=vulns))

    return audit_results
