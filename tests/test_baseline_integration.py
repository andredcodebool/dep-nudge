"""Integration tests for the baseline workflow.

Verifies that save -> load -> diff works end-to-end and that the
DEFAULT_BASELINE_FILE constant is respected when no explicit path is given.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from dep_nudge.baseline import (
    DEFAULT_BASELINE_FILE,
    load_baseline,
    new_since_baseline,
    save_baseline,
)


@pytest.fixture()
def project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Temporary directory that acts as the working directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_default_file_written_to_cwd(project_dir: Path) -> None:
    save_baseline({"requests": "2.31.0"})
    expected = project_dir / DEFAULT_BASELINE_FILE
    assert expected.exists()


def test_default_file_loaded_from_cwd(project_dir: Path) -> None:
    packages = {"flask": "3.0.0", "click": "8.1.7"}
    save_baseline(packages)
    loaded = load_baseline()
    assert loaded == packages


def test_full_workflow_no_new_issues(project_dir: Path) -> None:
    """When nothing changes between runs, new_since_baseline returns []."""
    packages = {"requests": "2.31.0", "boto3": "1.34.0"}
    save_baseline(packages)
    baseline = load_baseline()
    result = new_since_baseline(packages, baseline)
    assert result == []


def test_full_workflow_detects_regression(project_dir: Path) -> None:
    """A version bump on a second run is flagged as new."""
    original = {"requests": "2.28.0", "flask": "2.3.0"}
    save_baseline(original)

    # Simulate a later run where requests has a newer available version.
    updated = {"requests": "2.31.0", "flask": "2.3.0"}
    baseline = load_baseline()
    result = new_since_baseline(updated, baseline)
    assert result == ["requests"]


def test_overwriting_baseline_reflects_new_state(project_dir: Path) -> None:
    save_baseline({"requests": "2.28.0"})
    save_baseline({"requests": "2.31.0", "flask": "3.0.0"})
    loaded = load_baseline()
    assert loaded == {"requests": "2.31.0", "flask": "3.0.0"}
