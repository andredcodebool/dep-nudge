"""Tests for dep_nudge.audit module."""

from __future__ import annotations

from unittest.mock import patch, MagicMock
from packaging.specifiers import SpecifierSet

from dep_nudge.parser import Requirement
from dep_nudge.checker import CheckResult
from dep_nudge.vulnerability import Vulnerability
from dep_nudge.audit import AuditResult, audit_requirements


def _make_req(name: str, spec: str = ">=1.0.0") -> Requirement:
    return Requirement(name=name, specifier=SpecifierSet(spec), raw=f"{name}{spec}")


def _make_check(name: str, current: str = "1.0.0", latest: str = "2.0.0") -> CheckResult:
    req = _make_req(name)
    return CheckResult(requirement=req, current_version=current, latest_version=latest)


def _make_vuln(pkg: str, vid: str = "VULN-001") -> Vulnerability:
    req = _make_req(pkg)
    return Vulnerability(requirement=req, vuln_id=vid, details="A vulnerability", aliases=[])


class TestAuditResult:
    def test_package_property_returns_name(self):
        check = _make_check("requests")
        result = AuditResult(check=check)
        assert result.package == "requests"

    def test_is_outdated_delegates_to_check(self):
        check = _make_check("requests", current="1.0.0", latest="2.0.0")
        result = AuditResult(check=check)
        assert result.is_outdated is True

    def test_is_not_outdated_when_up_to_date(self):
        check = _make_check("requests", current="2.0.0", latest="2.0.0")
        result = AuditResult(check=check)
        assert result.is_outdated is False

    def test_is_vulnerable_true_when_vulns_present(self):
        check = _make_check("flask")
        vuln = _make_vuln("flask")
        result = AuditResult(check=check, vulnerabilities=[vuln])
        assert result.is_vulnerable is True

    def test_is_vulnerable_false_when_no_vulns(self):
        check = _make_check("flask")
        result = AuditResult(check=check, vulnerabilities=[])
        assert result.is_vulnerable is False

    def test_needs_attention_true_if_outdated(self):
        check = _make_check("django", current="1.0", latest="2.0")
        result = AuditResult(check=check)
        assert result.needs_attention is True

    def test_needs_attention_true_if_vulnerable(self):
        check = _make_check("django", current="2.0", latest="2.0")
        vuln = _make_vuln("django")
        result = AuditResult(check=check, vulnerabilities=[vuln])
        assert result.needs_attention is True

    def test_needs_attention_false_when_clean(self):
        check = _make_check("django", current="2.0", latest="2.0")
        result = AuditResult(check=check)
        assert result.needs_attention is False

    def test_str_includes_check_and_vulns(self):
        check = _make_check("requests")
        vuln = _make_vuln("requests", "CVE-2023-0001")
        result = AuditResult(check=check, vulnerabilities=[vuln])
        text = str(result)
        assert "requests" in text
        assert "CVE-2023-0001" in text


class TestAuditRequirements:
    def test_returns_list_of_audit_results(self):
        reqs = [_make_req("requests"), _make_req("flask")]
        with patch("dep_nudge.audit.check_requirements") as mock_check, \
             patch("dep_nudge.audit.fetch_vulnerabilities", return_value=[]):
            mock_check.return_value = [_make_check(r.name) for r in reqs]
            results = audit_requirements(reqs)
        assert len(results) == 2
        assert all(isinstance(r, AuditResult) for r in results)

    def test_skip_vulns_does_not_call_fetch(self):
        reqs = [_make_req("requests")]
        with patch("dep_nudge.audit.check_requirements") as mock_check, \
             patch("dep_nudge.audit.fetch_vulnerabilities") as mock_fetch:
            mock_check.return_value = [_make_check("requests")]
            audit_requirements(reqs, skip_vulns=True)
        mock_fetch.assert_not_called()

    def test_vulns_attached_to_results(self):
        reqs = [_make_req("requests")]
        vuln = _make_vuln("requests")
        with patch("dep_nudge.audit.check_requirements") as mock_check, \
             patch("dep_nudge.audit.fetch_vulnerabilities", return_value=[vuln]):
            mock_check.return_value = [_make_check("requests")]
            results = audit_requirements(reqs)
        assert results[0].vulnerabilities == [vuln]
