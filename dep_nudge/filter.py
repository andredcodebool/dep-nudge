"""Filtering utilities for CheckResult lists."""

from __future__ import annotations

from typing import List, Optional

from dep_nudge.checker import CheckResult


def filter_results(
    results: List[CheckResult],
    *,
    outdated_only: bool = False,
    vulnerable_only: bool = False,
    package: Optional[str] = None,
) -> List[CheckResult]:
    """Return a filtered subset of *results*.

    Parameters
    ----------
    results:
        The full list of :class:`~dep_nudge.checker.CheckResult` objects to
        filter.
    outdated_only:
        When ``True``, only results where a newer version is available are
        kept.
    vulnerable_only:
        When ``True``, only results that have at least one associated
        vulnerability are kept.
    package:
        Case-insensitive package name substring filter.  Only results whose
        package name contains *package* are kept.
    """
    filtered: List[CheckResult] = list(results)

    if outdated_only:
        filtered = [r for r in filtered if r.latest and r.latest != r.requirement.version]

    if vulnerable_only:
        filtered = [r for r in filtered if r.vulnerabilities]

    if package:
        needle = package.lower()
        filtered = [r for r in filtered if needle in r.requirement.name.lower()]

    return filtered


def partition_results(
    results: List[CheckResult],
) -> tuple[List[CheckResult], List[CheckResult], List[CheckResult]]:
    """Split *results* into three buckets.

    Returns
    -------
    tuple
        ``(ok, outdated, vulnerable)`` where each element is a list of
        :class:`~dep_nudge.checker.CheckResult` objects.

        * **ok** – up-to-date and vulnerability-free.
        * **outdated** – a newer version exists (may also be vulnerable).
        * **vulnerable** – has known vulnerabilities (may also be outdated).

        Note that a single result can appear in both *outdated* and
        *vulnerable*.
    """
    outdated = filter_results(results, outdated_only=True)
    vulnerable = filter_results(results, vulnerable_only=True)
    outdated_set = set(id(r) for r in outdated)
    vulnerable_set = set(id(r) for r in vulnerable)
    ok = [r for r in results if id(r) not in outdated_set and id(r) not in vulnerable_set]
    return ok, outdated, vulnerable
