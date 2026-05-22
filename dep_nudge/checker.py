"""Check requirements against the latest versions available on PyPI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import requests
from packaging.version import Version

from dep_nudge import cache as _cache
from dep_nudge.parser import Requirement

_PYPI_URL = "https://pypi.org/pypi/{package}/json"
_CACHE_TTL = 3600


@dataclass
class CheckResult:
    requirement: Requirement
    latest_version: Optional[str]
    is_outdated: bool
    is_unpinned: bool

    def __str__(self) -> str:  # pragma: no cover
        if self.is_unpinned:
            return (
                f"{self.requirement.name}: unpinned "
                f"(latest {self.latest_version})"
            )
        if self.is_outdated:
            return (
                f"{self.requirement.name}: "
                f"{self.requirement.specifier} -> {self.latest_version}"
            )
        return f"{self.requirement.name}: up-to-date"


def fetch_latest_version(
    package_name: str,
    use_cache: bool = True,
    cache_dir=None,
) -> Optional[str]:
    """Return the latest stable version string from PyPI, or None on error."""
    cache_key = f"pypi:{package_name.lower()}"
    cache_kwargs = {} if cache_dir is None else {"cache_dir": cache_dir}

    if use_cache:
        cached = _cache.get(cache_key, **cache_kwargs)
        if cached is not None:
            return cached

    url = _PYPI_URL.format(package=package_name)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError):
        return None

    data = response.json()
    version = data.get("info", {}).get("version")

    if version and use_cache:
        _cache.set(cache_key, version, ttl=_CACHE_TTL, **cache_kwargs)

    return version


def check_requirement(
    req: Requirement,
    use_cache: bool = True,
    cache_dir=None,
) -> CheckResult:
    """Return a CheckResult for a single Requirement."""
    latest = fetch_latest_version(req.name, use_cache=use_cache, cache_dir=cache_dir)
    is_unpinned = not req.specifier
    is_outdated = False

    if latest and req.specifier:
        try:
            pinned = Version(req.specifier.lstrip("=<>!"))
            is_outdated = Version(latest) > pinned
        except Exception:  # noqa: BLE001
            pass

    return CheckResult(
        requirement=req,
        latest_version=latest,
        is_outdated=is_outdated,
        is_unpinned=is_unpinned,
    )


def check_requirements(
    requirements: List[Requirement],
    use_cache: bool = True,
    cache_dir=None,
) -> List[CheckResult]:
    """Return CheckResults for all requirements."""
    return [
        check_requirement(req, use_cache=use_cache, cache_dir=cache_dir)
        for req in requirements
    ]
