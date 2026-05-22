"""Tests for dep_nudge.checker module."""

from unittest.mock import MagicMock, patch

import pytest

from dep_nudge.checker import (
    CheckResult,
    check_requirement,
    check_requirements,
    fetch_latest_version,
)
from dep_nudge.parser import Requirement


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_req(name: str, version: str | None = None) -> Requirement:
    return Requirement(name=name, specifier="==", version=version)


# ---------------------------------------------------------------------------
# fetch_latest_version
# ---------------------------------------------------------------------------

def test_fetch_latest_version_returns_version(requests_mock):
    requests_mock.get(
        "https://pypi.org/pypi/requests/json",
        json={"info": {"version": "2.31.0"}},
    )
    assert fetch_latest_version("requests") == "2.31.0"


def test_fetch_latest_version_returns_none_on_http_error(requests_mock):
    requests_mock.get("https://pypi.org/pypi/nonexistent-pkg/json", status_code=404)
    assert fetch_latest_version("nonexistent-pkg") is None


def test_fetch_latest_version_returns_none_on_connection_error(requests_mock):
    import requests as req_lib
    requests_mock.get(
        "https://pypi.org/pypi/flaky/json",
        exc=req_lib.ConnectionError,
    )
    assert fetch_latest_version("flaky") is None


# ---------------------------------------------------------------------------
# check_requirement
# ---------------------------------------------------------------------------

@patch("dep_nudge.checker.fetch_latest_version", return_value="2.31.0")
def test_check_requirement_up_to_date(mock_fetch):
    req = make_req("requests", "2.31.0")
    result = check_requirement(req)
    assert result.is_outdated is False
    assert result.latest_version == "2.31.0"
    assert result.error is None


@patch("dep_nudge.checker.fetch_latest_version", return_value="2.31.0")
def test_check_requirement_outdated(mock_fetch):
    req = make_req("requests", "2.28.0")
    result = check_requirement(req)
    assert result.is_outdated is True
    assert result.latest_version == "2.31.0"
    assert result.current_version == "2.28.0"


@patch("dep_nudge.checker.fetch_latest_version", return_value=None)
def test_check_requirement_pypi_failure(mock_fetch):
    req = make_req("broken-pkg", "1.0.0")
    result = check_requirement(req)
    assert result.error is not None
    assert result.is_outdated is False


# ---------------------------------------------------------------------------
# check_requirements
# ---------------------------------------------------------------------------

@patch("dep_nudge.checker.fetch_latest_version", return_value="1.0.0")
def test_check_requirements_returns_one_result_per_requirement(mock_fetch):
    reqs = [make_req("pkgA", "1.0.0"), make_req("pkgB", "0.9.0")]
    results = check_requirements(reqs)
    assert len(results) == 2
    assert all(isinstance(r, CheckResult) for r in results)


# ---------------------------------------------------------------------------
# CheckResult.__str__
# ---------------------------------------------------------------------------

def test_check_result_str_outdated():
    req = make_req("flask", "2.0.0")
    result = CheckResult(requirement=req, current_version="2.0.0", latest_version="3.0.0", is_outdated=True)
    assert "→" in str(result)
    assert "upgrade available" in str(result)


def test_check_result_str_up_to_date():
    req = make_req("flask", "3.0.0")
    result = CheckResult(requirement=req, current_version="3.0.0", latest_version="3.0.0", is_outdated=False)
    assert "up to date" in str(result)


def test_check_result_str_error():
    req = make_req("broken", None)
    result = CheckResult(requirement=req, current_version=None, latest_version=None, error="timeout")
    assert "error" in str(result)
