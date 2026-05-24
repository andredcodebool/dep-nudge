"""Integration tests: delta interacts with checker.CheckResult."""

from packaging.specifiers import SpecifierSet

from dep_nudge.checker import CheckResult
from dep_nudge.delta import BumpKind, compute_delta
from dep_nudge.parser import Requirement


def _make_req(name: str, specifier: str = "") -> Requirement:
    return Requirement(
        name=name,
        specifier=SpecifierSet(specifier),
        raw=f"{name}{specifier}",
    )


def _make_result(
    name: str,
    installed: str | None,
    latest: str | None,
) -> CheckResult:
    return CheckResult(
        requirement=_make_req(name, f"=={installed}" if installed else ""),
        installed_version=installed,
        latest_version=latest,
        is_outdated=bool(
            installed and latest and installed != latest
        ),
    )


class TestDeltaWithCheckResult:
    def test_up_to_date_package_yields_none_bump(self):
        result = _make_result("requests", "2.31.0", "2.31.0")
        delta = compute_delta(result.installed_version, result.latest_version)
        assert delta.kind is BumpKind.NONE

    def test_outdated_minor_bump(self):
        result = _make_result("flask", "2.2.0", "2.3.0")
        delta = compute_delta(result.installed_version, result.latest_version)
        assert delta.kind is BumpKind.MINOR

    def test_outdated_major_bump(self):
        result = _make_result("django", "3.2.0", "4.0.0")
        delta = compute_delta(result.installed_version, result.latest_version)
        assert delta.kind is BumpKind.MAJOR

    def test_missing_latest_yields_unknown(self):
        result = _make_result("private-pkg", "1.0.0", None)
        delta = compute_delta(result.installed_version, result.latest_version)
        assert delta.kind is BumpKind.UNKNOWN

    def test_delta_current_matches_installed(self):
        result = _make_result("urllib3", "1.26.0", "2.0.0")
        delta = compute_delta(result.installed_version, result.latest_version)
        assert delta.current == result.installed_version

    def test_delta_latest_matches_check_result(self):
        result = _make_result("urllib3", "1.26.0", "2.0.0")
        delta = compute_delta(result.installed_version, result.latest_version)
        assert delta.latest == result.latest_version
