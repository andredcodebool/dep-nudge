"""Tests for dep_nudge.audit_report module."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch
from packaging.specifiers import SpecifierSet

from dep_nudge.parser import Requirement
from dep_nudge.checker import CheckResult
from dep_nudge.vulnerability import Vulnerability
from dep_nudge.audit import AuditResult
from dep_nudge.audit_report import format_audit_result, print_audit_report


def _make_req(name: str) -> Requirement:
    return Requirement(name=name, specifier=SpecifierSet(">=1.0"), raw=f"{name}>=1.0")


def _make_result(
    name: str,
    current: str = "1.0.0",
    latest: str = "1.0.0",
    vulns: list | None = None,
) -> AuditResult:
    req = _make_req(name)
    check = CheckResult(requirement=req, current_version=current, latest_version=latest)
    v_list = vulns or []
    return AuditResult(check=check, vulnerabilities=v_list)


def _make_vuln(name: str, vid: str = "CVE-2024-001") -> Vulnerability:
    req = _make_req(name)
    return Vulnerability(requirement=req, vuln_id=vid, details="Test vuln", aliases=["GHSA-xxxx"])


class TestFormatAuditResult:
    def test_ok_result_contains_ok_label(self):
        result = _make_result("requests", current="2.0", latest="2.0")
        text = format_audit_result(result, colour=False)
        assert "OK" in text
        assert "requests" in text

    def test_outdated_result_contains_outdated_label(self):
        result = _make_result("flask", current="1.0", latest="2.0")
        text = format_audit_result(result, colour=False)
        assert "OUTDATED" in text

    def test_vulnerable_result_contains_vulnerable_label(self):
        vuln = _make_vuln("django")
        result = _make_result("django", current="2.0", latest="2.0", vulns=[vuln])
        text = format_audit_result(result, colour=False)
        assert "VULNERABLE" in text

    def test_vuln_id_appears_in_output(self):
        vuln = _make_vuln("django", "CVE-2024-999")
        result = _make_result("django", vulns=[vuln])
        text = format_audit_result(result, colour=False)
        assert "CVE-2024-999" in text

    def test_aliases_appear_when_present(self):
        vuln = _make_vuln("numpy")
        result = _make_result("numpy", vulns=[vuln])
        text = format_audit_result(result, colour=False)
        assert "GHSA-xxxx" in text

    def test_latest_version_shown(self):
        result = _make_result("boto3", current="1.0", latest="3.5.0")
        text = format_audit_result(result, colour=False)
        assert "3.5.0" in text


class TestPrintAuditReport:
    def test_prints_all_clear_when_no_issues(self, capsys):
        results = [_make_result("requests", current="2.0", latest="2.0")]
        print_audit_report(results, colour=False)
        captured = capsys.readouterr()
        assert "up-to-date" in captured.out

    def test_prints_summary_line(self, capsys):
        results = [
            _make_result("flask", current="1.0", latest="2.0"),
            _make_result("requests", current="2.0", latest="2.0"),
        ]
        print_audit_report(results, colour=False)
        captured = capsys.readouterr()
        assert "2 package(s) scanned" in captured.out

    def test_only_attention_filters_clean_packages(self, capsys):
        results = [
            _make_result("flask", current="1.0", latest="2.0"),
            _make_result("requests", current="2.0", latest="2.0"),
        ]
        print_audit_report(results, colour=False, only_attention=True)
        captured = capsys.readouterr()
        assert "flask" in captured.out
        assert "requests" not in captured.out.split("scanned")[0]

    def test_vulnerable_count_in_summary(self, capsys):
        vuln = _make_vuln("django")
        results = [_make_result("django", vulns=[vuln])]
        print_audit_report(results, colour=False)
        captured = capsys.readouterr()
        assert "1 vulnerable" in captured.out
