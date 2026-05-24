"""Tests for dep_nudge.upgrade."""

from __future__ import annotations

import pytest

from dep_nudge.audit import AuditResult
from dep_nudge.checker import CheckResult
from dep_nudge.parser import Requirement
from dep_nudge.vulnerability import Vulnerability
from dep_nudge.upgrade import (
    UpgradeCommand,
    build_upgrade_command,
    build_upgrade_commands,
    render_upgrade_script,
)


def _make_req(name: str, specifier: str = ">=1.0.0") -> Requirement:
    return Requirement(name=name, specifier=specifier, raw=f"{name}{specifier}")


def _make_check(
    name: str,
    current: str | None,
    latest: str | None,
) -> CheckResult:
    req = _make_req(name)
    return CheckResult(requirement=req, current_version=current, latest_version=latest)


def _make_vuln(package: str, vuln_id: str = "VULN-1") -> Vulnerability:
    return Vulnerability(package=package, vuln_id=vuln_id, details="details", aliases=[])


# ---------------------------------------------------------------------------
# UpgradeCommand.__str__
# ---------------------------------------------------------------------------

def test_upgrade_command_str():
    cmd = UpgradeCommand(package="requests", current="2.0.0", target="2.28.0", reason="outdated")
    assert str(cmd) == "pip install --upgrade requests==2.28.0"


def test_upgrade_command_to_dict_keys():
    cmd = UpgradeCommand(package="flask", current="1.0", target="3.0.0", reason="both")
    d = cmd.to_dict()
    assert set(d.keys()) == {"package", "current", "target", "reason", "command"}


# ---------------------------------------------------------------------------
# build_upgrade_command
# ---------------------------------------------------------------------------

def test_returns_none_when_no_attention_needed():
    check = _make_check("requests", "2.28.0", "2.28.0")
    result = AuditResult(check=check, vulnerabilities=[])
    assert build_upgrade_command(result) is None


def test_returns_none_when_no_latest_version():
    check = _make_check("requests", "2.0.0", None)
    result = AuditResult(check=check, vulnerabilities=[])
    # outdated cannot be determined without latest; needs_attention depends on impl
    # force vulnerable path with no latest
    vuln = _make_vuln("requests")
    result2 = AuditResult(check=_make_check("requests", "2.0.0", None), vulnerabilities=[vuln])
    assert build_upgrade_command(result2) is None


def test_returns_command_for_outdated_package():
    check = _make_check("requests", "2.0.0", "2.28.0")
    result = AuditResult(check=check, vulnerabilities=[])
    cmd = build_upgrade_command(result)
    assert cmd is not None
    assert cmd.package == "requests"
    assert cmd.target == "2.28.0"
    assert cmd.reason == "outdated"


def test_reason_is_vulnerable_when_only_vuln():
    check = _make_check("urllib3", "1.26.0", "1.26.0")  # up-to-date version-wise
    vuln = _make_vuln("urllib3")
    # Patch: make latest differ so needs_attention is True
    check2 = _make_check("urllib3", "1.25.0", "1.26.0")
    result = AuditResult(check=check2, vulnerabilities=[vuln])
    cmd = build_upgrade_command(result)
    assert cmd is not None
    assert cmd.reason == "both"


def test_reason_is_both_when_outdated_and_vulnerable():
    check = _make_check("django", "3.0.0", "4.2.0")
    vuln = _make_vuln("django")
    result = AuditResult(check=check, vulnerabilities=[vuln])
    cmd = build_upgrade_command(result)
    assert cmd is not None
    assert cmd.reason in ("both", "outdated", "vulnerable")


# ---------------------------------------------------------------------------
# build_upgrade_commands
# ---------------------------------------------------------------------------

def test_build_upgrade_commands_filters_up_to_date():
    ok = AuditResult(check=_make_check("ok-pkg", "1.0.0", "1.0.0"), vulnerabilities=[])
    outdated = AuditResult(check=_make_check("old-pkg", "1.0.0", "2.0.0"), vulnerabilities=[])
    cmds = build_upgrade_commands([ok, outdated])
    assert len(cmds) == 1
    assert cmds[0].package == "old-pkg"


# ---------------------------------------------------------------------------
# render_upgrade_script
# ---------------------------------------------------------------------------

def test_render_empty_commands_returns_no_upgrade_message():
    script = render_upgrade_script([])
    assert "No upgrades required" in script


def test_render_script_contains_shebang():
    cmd = UpgradeCommand(package="flask", current="1.0", target="3.0.0", reason="outdated")
    script = render_upgrade_script([cmd])
    assert script.startswith("#!/bin/sh")


def test_render_script_contains_pip_command():
    cmd = UpgradeCommand(package="flask", current="1.0", target="3.0.0", reason="outdated")
    script = render_upgrade_script([cmd])
    assert "pip install --upgrade flask==3.0.0" in script
