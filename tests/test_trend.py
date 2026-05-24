"""Tests for dep_nudge.trend."""

from __future__ import annotations

import json
import os
from datetime import date
from unittest.mock import MagicMock

import pytest

from dep_nudge.audit import AuditResult
from dep_nudge.trend import (
    TrendEntry,
    load_trend,
    record_snapshot,
    save_trend,
    snapshot_from_results,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_audit(outdated: bool = False, vulnerable: bool = False) -> AuditResult:
    result = MagicMock(spec=AuditResult)
    result.is_outdated = outdated
    result.is_vulnerable = vulnerable
    return result


# ---------------------------------------------------------------------------
# TrendEntry
# ---------------------------------------------------------------------------

def test_trend_entry_to_dict():
    entry = TrendEntry(date="2024-01-15", total=10, outdated=3, vulnerable=1)
    d = entry.to_dict()
    assert d == {"date": "2024-01-15", "total": 10, "outdated": 3, "vulnerable": 1}


def test_trend_entry_from_dict_round_trip():
    original = TrendEntry(date="2024-06-01", total=5, outdated=2, vulnerable=0)
    restored = TrendEntry.from_dict(original.to_dict())
    assert restored.date == original.date
    assert restored.total == original.total
    assert restored.outdated == original.outdated
    assert restored.vulnerable == original.vulnerable


def test_trend_entry_str():
    entry = TrendEntry(date="2024-03-10", total=8, outdated=4, vulnerable=2)
    text = str(entry)
    assert "2024-03-10" in text
    assert "4/8" in text
    assert "2 vulnerable" in text


# ---------------------------------------------------------------------------
# snapshot_from_results
# ---------------------------------------------------------------------------

def test_snapshot_totals():
    results = [
        _make_audit(outdated=True, vulnerable=False),
        _make_audit(outdated=False, vulnerable=True),
        _make_audit(outdated=False, vulnerable=False),
    ]
    entry = snapshot_from_results(results)
    assert entry.total == 3
    assert entry.outdated == 1
    assert entry.vulnerable == 1


def test_snapshot_date_is_today():
    entry = snapshot_from_results([])
    assert entry.date == date.today().isoformat()


def test_snapshot_empty_results():
    entry = snapshot_from_results([])
    assert entry.total == 0
    assert entry.outdated == 0
    assert entry.vulnerable == 0


# ---------------------------------------------------------------------------
# load_trend / save_trend
# ---------------------------------------------------------------------------

def test_load_trend_missing_file(tmp_path):
    entries = load_trend(str(tmp_path / "nonexistent.json"))
    assert entries == []


def test_save_and_load_round_trip(tmp_path):
    path = str(tmp_path / "trend.json")
    entries = [
        TrendEntry(date="2024-01-01", total=4, outdated=1, vulnerable=0),
        TrendEntry(date="2024-02-01", total=4, outdated=2, vulnerable=1),
    ]
    save_trend(entries, path)
    loaded = load_trend(path)
    assert len(loaded) == 2
    assert loaded[0].date == "2024-01-01"
    assert loaded[1].outdated == 2


# ---------------------------------------------------------------------------
# record_snapshot
# ---------------------------------------------------------------------------

def test_record_snapshot_appends_entry(tmp_path):
    path = str(tmp_path / "trend.json")
    results = [_make_audit(outdated=True)]
    record_snapshot(results, path)
    record_snapshot(results, path)
    loaded = load_trend(path)
    assert len(loaded) == 2


def test_record_snapshot_returns_entry(tmp_path):
    path = str(tmp_path / "trend.json")
    results = [_make_audit(outdated=False, vulnerable=True)]
    entry = record_snapshot(results, path)
    assert isinstance(entry, TrendEntry)
    assert entry.vulnerable == 1
