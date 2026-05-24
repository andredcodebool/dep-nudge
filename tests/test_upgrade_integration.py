"""Integration tests: upgrade commands derived from a realistic audit pipeline."""

from __future__ import annotations

from dep_nudge.audit import AuditResult
from dep_nudge.checker import CheckResult
from dep_nudge.parser import Requirement
from dep_nudge.vulnerability import Vulnerability
from dep_nudge.upgrade import (
    build_upgrade_commands,
    render_upgrade_script,
)


def _req(name: str, spec: str = ">=1.0") -> Requirement:
    return Requirement(name=name, specifier=spec, raw=f"{name}{spec}")


def _check(name: str, current: str | None, latest: str | None) -> CheckResult:
    return CheckResult(requirement=_req(name), current_version=current, latest_version=latest)


def _vuln(package: str, vid: str = "VULN-001") -> Vulnerability:
    return Vulnerability(package=package, vuln_id=vid, details="desc", aliases=[])


def _fake_audit_results() -> list[AuditResult]:
    return [
        AuditResult(check=_check("requests", "2.20.0", "2.31.0"), vulnerabilities=[]),
        AuditResult(check=_check("flask", "2.0.0", "3.0.3"), vulnerabilities=[_vuln("flask")]),
        AuditResult(check=_check("click", "8.1.0", "8.1.0"), vulnerabilities=[]),
        AuditResult(check=_check("boto3", "1.26.0", None), vulnerabilities=[]),
        AuditResult(
            check=_check("pillow", "9.0.0", "10.3.0"),
            vulnerabilities=[_vuln("pillow", "CVE-2023-0001")],
        ),
    ]


def test_only_packages_needing_attention_get_commands():
    results = _fake_audit_results()
    cmds = build_upgrade_commands(results)
    names = {c.package for c in cmds}
    # click is up-to-date; boto3 has no latest
    assert "click" not in names
    assert "boto3" not in names


def test_outdated_packages_included():
    results = _fake_audit_results()
    cmds = build_upgrade_commands(results)
    names = {c.package for c in cmds}
    assert "requests" in names


def test_vulnerable_and_outdated_included():
    results = _fake_audit_results()
    cmds = build_upgrade_commands(results)
    names = {c.package for c in cmds}
    assert "flask" in names
    assert "pillow" in names


def test_command_targets_latest_version():
    results = _fake_audit_results()
    cmds = {c.package: c for c in build_upgrade_commands(results)}
    assert cmds["requests"].target == "2.31.0"
    assert cmds["flask"].target == "3.0.3"


def test_script_line_count_matches_commands():
    results = _fake_audit_results()
    cmds = build_upgrade_commands(results)
    script = render_upgrade_script(cmds)
    pip_lines = [l for l in script.splitlines() if l.startswith("pip install")]
    assert len(pip_lines) == len(cmds)


def test_script_for_empty_results_is_safe():
    script = render_upgrade_script([])
    assert "pip install" not in script
    assert len(script) > 0
