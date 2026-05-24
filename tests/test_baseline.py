"""Tests for dep_nudge.baseline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dep_nudge.baseline import (
    DEFAULT_BASELINE_FILE,
    load_baseline,
    new_since_baseline,
    save_baseline,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


# ---------------------------------------------------------------------------
# save_baseline
# ---------------------------------------------------------------------------

def test_save_creates_file(tmp_dir: Path) -> None:
    target = tmp_dir / DEFAULT_BASELINE_FILE
    result = save_baseline({"requests": "2.31.0"}, path=str(target))
    assert result == target
    assert target.exists()


def test_save_writes_valid_json(tmp_dir: Path) -> None:
    target = tmp_dir / "baseline.json"
    save_baseline({"flask": "3.0.0", "click": "8.1.7"}, path=str(target))
    data = json.loads(target.read_text())
    assert data["packages"] == {"flask": "3.0.0", "click": "8.1.7"}


def test_save_includes_created_at(tmp_dir: Path) -> None:
    target = tmp_dir / "baseline.json"
    save_baseline({}, path=str(target))
    data = json.loads(target.read_text())
    assert "created_at" in data


def test_save_returns_path(tmp_dir: Path) -> None:
    target = tmp_dir / "baseline.json"
    returned = save_baseline({"numpy": "1.26.0"}, path=str(target))
    assert returned == target


# ---------------------------------------------------------------------------
# load_baseline
# ---------------------------------------------------------------------------

def test_load_returns_empty_when_file_missing(tmp_dir: Path) -> None:
    missing = tmp_dir / "no_such_file.json"
    result = load_baseline(path=str(missing))
    assert result == {}


def test_load_round_trips_packages(tmp_dir: Path) -> None:
    target = tmp_dir / "baseline.json"
    packages = {"requests": "2.31.0", "boto3": "1.34.0"}
    save_baseline(packages, path=str(target))
    loaded = load_baseline(path=str(target))
    assert loaded == packages


def test_load_handles_none_versions(tmp_dir: Path) -> None:
    target = tmp_dir / "baseline.json"
    save_baseline({"unknown-pkg": None}, path=str(target))
    loaded = load_baseline(path=str(target))
    assert loaded == {"unknown-pkg": None}


# ---------------------------------------------------------------------------
# new_since_baseline
# ---------------------------------------------------------------------------

def test_new_since_baseline_empty_baseline_returns_all() -> None:
    current = {"requests": "2.31.0", "flask": "3.0.0"}
    result = new_since_baseline(current, {})
    assert sorted(result) == ["flask", "requests"]


def test_new_since_baseline_identical_returns_empty() -> None:
    packages = {"requests": "2.31.0", "flask": "3.0.0"}
    result = new_since_baseline(packages, packages)
    assert result == []


def test_new_since_baseline_detects_version_change() -> None:
    baseline = {"requests": "2.28.0"}
    current = {"requests": "2.31.0"}
    result = new_since_baseline(current, baseline)
    assert result == ["requests"]


def test_new_since_baseline_detects_new_package() -> None:
    baseline = {"requests": "2.31.0"}
    current = {"requests": "2.31.0", "flask": "3.0.0"}
    result = new_since_baseline(current, baseline)
    assert result == ["flask"]


def test_new_since_baseline_result_is_sorted() -> None:
    current = {"zebra": "1.0", "alpha": "2.0", "mango": "3.0"}
    result = new_since_baseline(current, {})
    assert result == sorted(result)
