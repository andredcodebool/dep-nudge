"""Tests for dep_nudge.summary."""

from __future__ import annotations

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from dep_nudge.checker import CheckResult
from dep_nudge.parser import Requirement
from dep_nudge.vulnerability import Vulnerability
from dep_nudge.summary import Summary, build_summary, summary_to_dict


def _make_result(
    name: str,
    specifier: str = "==1.0.0",
    latest: str | None = "1.0.0",
    vulns: int = 0,
) -> CheckResult:
    req = Requirement(name=name, specifier=SpecifierSet(specifier), raw=f"{name}{specifier}")
    vulnerabilities = [
        Vulnerability(id=f"VULN-{i}", details="desc", aliases=[], fixed_in=[])
        for i in range(vulns)
    ]
    return CheckResult(
        requirement=req,
        latest=Version(latest) if latest else None,
        vulnerabilities=vulnerabilities,
    )


class TestBuildSummary:
    def test_empty_results_gives_zero_totals(self):
        summary = build_summary([])
        assert summary.total == 0
        assert summary.up_to_date == 0
        assert summary.outdated == 0
        assert summary.vulnerable == 0
        assert summary.unknown == 0

    def test_total_reflects_number_of_results(self):
        results = [_make_result("pkgA"), _make_result("pkgB"), _make_result("pkgC")]
        assert build_summary(results).total == 3

    def test_up_to_date_counted_correctly(self):
        results = [_make_result("pkgA", "==1.0.0", "1.0.0")]
        summary = build_summary(results)
        assert summary.up_to_date == 1
        assert summary.outdated == 0

    def test_outdated_counted_correctly(self):
        results = [_make_result("pkgA", "==1.0.0", "2.0.0")]
        summary = build_summary(results)
        assert summary.outdated == 1
        assert summary.up_to_date == 0

    def test_unknown_when_latest_is_none(self):
        results = [_make_result("pkgA", "==1.0.0", None)]
        summary = build_summary(results)
        assert summary.unknown == 1
        assert summary.up_to_date == 0
        assert summary.outdated == 0

    def test_vulnerable_counted_correctly(self):
        results = [_make_result("pkgA", "==1.0.0", "1.0.0", vulns=2)]
        summary = build_summary(results)
        assert summary.vulnerable == 1

    def test_vulnerable_and_outdated_can_overlap(self):
        results = [_make_result("pkgA", "==1.0.0", "2.0.0", vulns=1)]
        summary = build_summary(results)
        assert summary.outdated == 1
        assert summary.vulnerable == 1

    def test_packages_list_populated(self):
        results = [_make_result("requests"), _make_result("flask")]
        summary = build_summary(results)
        assert set(summary.packages) == {"requests", "flask"}


class TestSummaryToDict:
    def test_returns_dict_with_expected_keys(self):
        summary = Summary(total=5, up_to_date=3, outdated=1, vulnerable=1, unknown=0)
        d = summary_to_dict(summary)
        assert set(d.keys()) == {"total", "up_to_date", "outdated", "vulnerable", "unknown"}

    def test_values_match_summary_fields(self):
        summary = Summary(total=4, up_to_date=2, outdated=1, vulnerable=1, unknown=0)
        d = summary_to_dict(summary)
        assert d["total"] == 4
        assert d["up_to_date"] == 2
        assert d["outdated"] == 1
        assert d["vulnerable"] == 1
        assert d["unknown"] == 0
