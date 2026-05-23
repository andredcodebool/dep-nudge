"""Integration tests for ignore file resolution and application."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dep_nudge.ignore_integration import (
    apply_ignore_for_requirements,
    resolve_ignore_file,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(name: str):
    req = MagicMock()
    req.name = name
    result = MagicMock()
    result.requirement = req
    return result


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    """A temp directory that mimics a project root."""
    req = tmp_path / "requirements.txt"
    req.write_text("requests==2.28.0\nflask==2.0.0\n", encoding="utf-8")
    ignore = tmp_path / ".nudgeignore"
    ignore.write_text("requests\n", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# resolve_ignore_file
# ---------------------------------------------------------------------------

def test_resolve_finds_ignore_next_to_requirements(project_dir: Path):
    req_path = project_dir / "requirements.txt"
    resolved = resolve_ignore_file(req_path)
    assert resolved == project_dir / ".nudgeignore"


def test_resolve_falls_back_to_cwd_when_missing(tmp_path: Path):
    req_path = tmp_path / "requirements.txt"
    req_path.write_text("", encoding="utf-8")
    # No .nudgeignore in tmp_path — fallback is cwd
    resolved = resolve_ignore_file(req_path)
    assert resolved == Path.cwd() / ".nudgeignore"


# ---------------------------------------------------------------------------
# apply_ignore_for_requirements
# ---------------------------------------------------------------------------

def test_apply_filters_ignored_package(project_dir: Path):
    req_path = project_dir / "requirements.txt"
    results = [_make_result("requests"), _make_result("flask")]
    filtered = apply_ignore_for_requirements(results, req_path)
    names = [r.requirement.name for r in filtered]
    assert "requests" not in names
    assert "flask" in names


def test_apply_explicit_ignore_file(tmp_path: Path):
    req_path = tmp_path / "requirements.txt"
    req_path.write_text("", encoding="utf-8")
    custom_ignore = tmp_path / "custom.ignore"
    custom_ignore.write_text("flask\n", encoding="utf-8")
    results = [_make_result("requests"), _make_result("flask")]
    filtered = apply_ignore_for_requirements(results, req_path, ignore_file=custom_ignore)
    names = [r.requirement.name for r in filtered]
    assert "flask" not in names
    assert "requests" in names


def test_apply_no_ignore_file_returns_all(tmp_path: Path):
    req_path = tmp_path / "requirements.txt"
    req_path.write_text("", encoding="utf-8")
    results = [_make_result("requests"), _make_result("flask")]
    # No .nudgeignore anywhere relevant — all results kept
    filtered = apply_ignore_for_requirements(results, req_path)
    assert len(filtered) == 2
