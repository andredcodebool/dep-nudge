"""Tests for dep_nudge.filter."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from dep_nudge.checker import CheckResult
from dep_nudge.filter import filter_results, partition_results
from dep_nudge.parser import Requirement


def _make_result(
    name: str,
    version: str = "1.0.0",
    latest: str | None = None,
    vulns: int = 0,
) -> CheckResult:
    req = Requirement(name=name, specifier="==", version=version, raw=f"{name}=={version}")
    vulnerabilities = [MagicMock() for _ in range(vulns)]
    return CheckResult(requirement=req, latest=latest, vulnerabilities=vulnerabilities)


# ---------------------------------------------------------------------------
# filter_results
# ---------------------------------------------------------------------------

class TestFilterResults:
    def test_no_filters_returns_all(self):
        results = [_make_result("flask"), _make_result("requests")]
        assert filter_results(results) == results

    def test_outdated_only_keeps_outdated(self):
        up_to_date = _make_result("flask", version="2.0.0", latest="2.0.0")
        outdated = _make_result("requests", version="2.27.0", latest="2.31.0")
        result = filter_results([up_to_date, outdated], outdated_only=True)
        assert result == [outdated]

    def test_outdated_only_excludes_no_latest(self):
        no_latest = _make_result("flask", version="2.0.0", latest=None)
        result = filter_results([no_latest], outdated_only=True)
        assert result == []

    def test_vulnerable_only_keeps_vulnerable(self):
        safe = _make_result("flask", vulns=0)
        unsafe = _make_result("requests", vulns=2)
        result = filter_results([safe, unsafe], vulnerable_only=True)
        assert result == [unsafe]

    def test_package_filter_case_insensitive(self):
        flask = _make_result("Flask")
        requests = _make_result("requests")
        result = filter_results([flask, requests], package="flask")
        assert result == [flask]

    def test_package_filter_substring_match(self):
        django_rest = _make_result("djangorestframework")
        django = _make_result("django")
        other = _make_result("flask")
        result = filter_results([django_rest, django, other], package="django")
        assert set(r.requirement.name for r in result) == {"djangorestframework", "django"}

    def test_combined_filters(self):
        safe_old = _make_result("flask", version="1.0", latest="2.0", vulns=0)
        unsafe_old = _make_result("requests", version="1.0", latest="2.0", vulns=1)
        safe_current = _make_result("click", version="8.0", latest="8.0", vulns=0)
        result = filter_results(
            [safe_old, unsafe_old, safe_current],
            outdated_only=True,
            vulnerable_only=True,
        )
        assert result == [unsafe_old]


# ---------------------------------------------------------------------------
# partition_results
# ---------------------------------------------------------------------------

class TestPartitionResults:
    def test_partition_all_ok(self):
        results = [_make_result("flask", latest="1.0.0")]
        ok, outdated, vulnerable = partition_results(results)
        assert len(ok) == 1
        assert outdated == []
        assert vulnerable == []

    def test_partition_outdated(self):
        r = _make_result("flask", version="1.0.0", latest="2.0.0")
        ok, outdated, vulnerable = partition_results([r])
        assert ok == []
        assert r in outdated
        assert vulnerable == []

    def test_partition_vulnerable(self):
        r = _make_result("requests", vulns=1)
        ok, outdated, vulnerable = partition_results([r])
        assert ok == []
        assert r in vulnerable

    def test_partition_both_outdated_and_vulnerable(self):
        r = _make_result("requests", version="1.0", latest="2.0", vulns=1)
        ok, outdated, vulnerable = partition_results([r])
        assert ok == []
        assert r in outdated
        assert r in vulnerable
