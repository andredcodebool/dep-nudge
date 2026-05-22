"""Tests for dep_nudge.formatter."""

from __future__ import annotations

import json
import csv
import io
from unittest.mock import MagicMock

import pytest

from dep_nudge.formatter import format_json, format_csv, render, SUPPORTED_FORMATS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(name="requests", specifier="==2.28.0", latest="2.31.0",
                 outdated=True, vulns=None):
    req = MagicMock()
    req.name = name
    req.specifier = specifier

    result = MagicMock()
    result.requirement = req
    result.latest_version = latest
    result.is_outdated = outdated
    result.vulnerabilities = vulns or []
    return result


def _make_vuln(vuln_id="GHSA-0000", aliases=None, details="A bug.", fixed_in="2.31.0"):
    v = MagicMock()
    v.vuln_id = vuln_id
    v.aliases = aliases or []
    v.details = details
    v.fixed_in = fixed_in
    return v


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------

def test_format_json_returns_valid_json():
    results = [_make_result()]
    output = format_json(results)
    parsed = json.loads(output)  # must not raise
    assert isinstance(parsed, list)


def test_format_json_contains_package_fields():
    results = [_make_result(name="flask", specifier="==2.0.0", latest="3.0.0")]
    parsed = json.loads(format_json(results))
    assert parsed[0]["package"] == "flask"
    assert parsed[0]["current"] == "==2.0.0"
    assert parsed[0]["latest"] == "3.0.0"
    assert parsed[0]["outdated"] is True


def test_format_json_includes_vulnerabilities():
    vuln = _make_vuln(vuln_id="GHSA-1234", aliases=["CVE-2023-1234"])
    results = [_make_result(vulns=[vuln])]
    parsed = json.loads(format_json(results))
    assert len(parsed[0]["vulnerabilities"]) == 1
    assert parsed[0]["vulnerabilities"][0]["id"] == "GHSA-1234"
    assert "CVE-2023-1234" in parsed[0]["vulnerabilities"][0]["aliases"]


def test_format_json_empty_results():
    assert format_json([]) == "[]"


# ---------------------------------------------------------------------------
# format_csv
# ---------------------------------------------------------------------------

def test_format_csv_has_header():
    output = format_csv([_make_result()])
    reader = csv.DictReader(io.StringIO(output))
    assert "package" in reader.fieldnames
    assert "outdated" in reader.fieldnames


def test_format_csv_row_values():
    results = [_make_result(name="boto3", specifier="==1.26.0", latest="1.34.0")]
    reader = csv.DictReader(io.StringIO(format_csv(results)))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["package"] == "boto3"
    assert rows[0]["latest"] == "1.34.0"


def test_format_csv_vulnerability_ids_semicolon_separated():
    vulns = [_make_vuln("GHSA-AAA"), _make_vuln("GHSA-BBB")]
    results = [_make_result(vulns=vulns)]
    reader = csv.DictReader(io.StringIO(format_csv(results)))
    row = next(reader)
    assert row["vulnerability_ids"] == "GHSA-AAA;GHSA-BBB"


# ---------------------------------------------------------------------------
# render dispatcher
# ---------------------------------------------------------------------------

def test_render_json():
    out = render([_make_result()], "json")
    json.loads(out)  # valid JSON


def test_render_csv():
    out = render([_make_result()], "csv")
    assert "package" in out


def test_render_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        render([], "xml")


def test_supported_formats_constant():
    assert "json" in SUPPORTED_FORMATS
    assert "csv" in SUPPORTED_FORMATS
