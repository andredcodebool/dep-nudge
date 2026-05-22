"""Check installed packages against PyPI for newer versions."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import requests

from dep_nudge.parser import Requirement

logger = logging.getLogger(__name__)

PYPI_URL = "https://pypi.org/pypi/{package}/json"


@dataclass
class CheckResult:
    requirement: Requirement
    current_version: Optional[str]
    latest_version: Optional[str]
    is_outdated: bool = False
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"{self.requirement.name}: error — {self.error}"
        if self.is_outdated:
            return (
                f"{self.requirement.name}: {self.current_version} → "
                f"{self.latest_version} (upgrade available)"
            )
        return f"{self.requirement.name}: up to date ({self.current_version})"


def fetch_latest_version(package_name: str, timeout: int = 5) -> Optional[str]:
    """Return the latest version string from PyPI, or None on failure."""
    url = PYPI_URL.format(package=package_name)
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except requests.RequestException as exc:
        logger.warning("Failed to fetch PyPI data for %s: %s", package_name, exc)
        return None


def check_requirement(req: Requirement) -> CheckResult:
    """Compare a single Requirement against the latest PyPI version."""
    latest = fetch_latest_version(req.name)
    if latest is None:
        return CheckResult(
            requirement=req,
            current_version=None,
            latest_version=None,
            error="Could not retrieve version from PyPI",
        )

    current = req.version
    is_outdated = current is not None and current != latest

    return CheckResult(
        requirement=req,
        current_version=current,
        latest_version=latest,
        is_outdated=is_outdated,
    )


def check_requirements(requirements: list[Requirement]) -> list[CheckResult]:
    """Check a list of requirements and return results for each."""
    results = []
    for req in requirements:
        logger.debug("Checking %s", req.name)
        results.append(check_requirement(req))
    return results
