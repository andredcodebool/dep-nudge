"""Tests for dep_nudge.pin."""

from __future__ import annotations

import os

import pytest

from dep_nudge.checker import CheckResult
from dep_nudge.parser import Requirement
from dep_nudge.pin import generate_pinned, pin_line, write_pinned


def _make_result(
    name: str,
    specifier: str = "",
    latest: str | None = None,
    raw: str | None = None,
) -> CheckResult:
    req = Requirement(
        name=name,
        specifier=specifier,
        raw=raw or (f"{name}{specifier}" if specifier else name),
    )
    return CheckResult(requirement=req, latest_version=latest, vulnerabilities=[])


# ---------------------------------------------------------------------------
# pin_line
# ---------------------------------------------------------------------------

class TestPinLine:
    def test_uses_latest_when_available(self):
        result = _make_result("requests", "==2.28.0", latest="2.31.0")
        assert pin_line(result) == "requests==2.31.0"

    def test_preserves_specifier_when_no_latest(self):
        result = _make_result("flask", ">=2.0", latest=None)
        assert pin_line(result) == "flask>=2.0"

    def test_falls_back_to_raw_when_no_specifier_and_no_latest(self):
        result = _make_result("numpy", specifier="", latest=None, raw="numpy")
        assert pin_line(result) == "numpy"

    def test_already_up_to_date_still_pinned(self):
        result = _make_result("boto3", "==1.26.0", latest="1.26.0")
        assert pin_line(result) == "boto3==1.26.0"


# ---------------------------------------------------------------------------
# generate_pinned
# ---------------------------------------------------------------------------

class TestGeneratePinned:
    def test_empty_input_returns_empty_string(self):
        assert generate_pinned([]) == ""

    def test_single_result(self):
        result = _make_result("requests", "==2.28.0", latest="2.31.0")
        output = generate_pinned([result])
        assert output == "requests==2.31.0\n"

    def test_multiple_results(self):
        results = [
            _make_result("requests", "==2.28.0", latest="2.31.0"),
            _make_result("flask", "==2.2.0", latest="3.0.0"),
        ]
        output = generate_pinned(results)
        assert output == "requests==2.31.0\nflask==3.0.0\n"

    def test_trailing_newline_present(self):
        result = _make_result("django", "==4.2.0", latest="4.2.1")
        assert generate_pinned([result]).endswith("\n")


# ---------------------------------------------------------------------------
# write_pinned
# ---------------------------------------------------------------------------

class TestWritePinned:
    def test_writes_file(self, tmp_path):
        out = tmp_path / "pinned.txt"
        results = [
            _make_result("requests", "==2.28.0", latest="2.31.0"),
            _make_result("flask", "==2.2.0", latest="3.0.0"),
        ]
        count = write_pinned(results, str(out))
        assert count == 2
        assert out.read_text() == "requests==2.31.0\nflask==3.0.0\n"

    def test_returns_zero_for_empty(self, tmp_path):
        out = tmp_path / "empty.txt"
        count = write_pinned([], str(out))
        assert count == 0
        assert out.read_text() == ""
