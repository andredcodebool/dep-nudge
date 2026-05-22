"""Integration-style tests: formatter round-trips with real-ish data."""

from __future__ import annotations

import csv
import io
import json
from unittest.mock import MagicMock

from dep_nudge.formatter import format_csv, format_json


def _make_result(name, specifier, latest, outdated, vuln_ids=()):
    req = MagicMock(name="req")
    req.name = name
    req.specifier = specifier

    vulns = []
    for vid in vuln_ids:
        v = MagicMock()
        v.vuln_id = vid
        v.aliases = []
        v.details = "some detail"
        v.fixed_in = latest
        vulns.append(v)

    result = MagicMock(name="result")
    result.requirement = req
    result.latest_version = latest
    result.is_outdated = outdated
    result.vulnerabilities = vulns
    return result


RESULTS = [
    _make_result("django", "==4.1.0", "4.2.0", True, ["GHSA-abc1"]),
    _make_result("pillow", "==9.5.0", "10.0.0", True, ["GHSA-abc2", "GHSA-abc3"]),
    _make_result("black", "==23.1.0", "23.1.0", False),
]


def test_json_round_trip_preserves_all_packages():
    parsed = json.loads(format_json(RESULTS))
    names = [r["package"] for r in parsed]
    assert names == ["django", "pillow", "black"]


def test_json_round_trip_vulnerability_counts():
    parsed = json.loads(format_json(RESULTS))
    assert len(parsed[0]["vulnerabilities"]) == 1
    assert len(parsed[1]["vulnerabilities"]) == 2
    assert len(parsed[2]["vulnerabilities"]) == 0


def test_csv_round_trip_row_count():
    reader = csv.DictReader(io.StringIO(format_csv(RESULTS)))
    rows = list(reader)
    assert len(rows) == 3


def test_csv_round_trip_outdated_field():
    reader = csv.DictReader(io.StringIO(format_csv(RESULTS)))
    rows = list(reader)
    # CSV stores booleans as strings
    assert rows[0]["outdated"] == "True"
    assert rows[2]["outdated"] == "False"


def test_csv_round_trip_vulnerability_ids():
    reader = csv.DictReader(io.StringIO(format_csv(RESULTS)))
    rows = list(reader)
    assert rows[1]["vulnerability_ids"] == "GHSA-abc2;GHSA-abc3"
    assert rows[2]["vulnerability_ids"] == ""
