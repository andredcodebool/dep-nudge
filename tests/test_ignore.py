"""Tests for dep_nudge.ignore."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dep_nudge.ignore import apply_ignore, load_ignore_list, _normalise


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
def ignore_file(tmp_path: Path) -> Path:
    content = "# comment\nrequests\nFlask\n\nDjango\n"
    p = tmp_path / ".nudgeignore"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _normalise
# ---------------------------------------------------------------------------

def test_normalise_lowercases():
    assert _normalise("Flask") == "flask"


def test_normalise_replaces_hyphens():
    assert _normalise("my-package") == "my_package"


def test_normalise_replaces_dots():
    assert _normalise("my.package") == "my_package"


def test_normalise_collapses_separators():
    assert _normalise("my--pkg") == "my_pkg"


# ---------------------------------------------------------------------------
# load_ignore_list
# ---------------------------------------------------------------------------

def test_load_returns_empty_when_file_missing(tmp_path: Path):
    result = load_ignore_list(tmp_path / ".nudgeignore")
    assert result == set()


def test_load_skips_comments_and_blanks(ignore_file: Path):
    result = load_ignore_list(ignore_file)
    assert "#" not in " ".join(result)


def test_load_correct_packages(ignore_file: Path):
    result = load_ignore_list(ignore_file)
    assert result == {"requests", "flask", "django"}


def test_load_normalises_names(ignore_file: Path):
    result = load_ignore_list(ignore_file)
    # Flask was stored as 'Flask' in the file; should be normalised
    assert "flask" in result
    assert "Flask" not in result


# ---------------------------------------------------------------------------
# apply_ignore
# ---------------------------------------------------------------------------

def test_apply_ignore_removes_matching(ignore_file: Path):
    ignore = load_ignore_list(ignore_file)
    results = [_make_result("requests"), _make_result("numpy")]
    filtered = apply_ignore(results, ignore)
    names = [r.requirement.name for r in filtered]
    assert "requests" not in names
    assert "numpy" in names


def test_apply_ignore_case_insensitive():
    ignore = {"flask"}
    results = [_make_result("Flask"), _make_result("Django")]
    filtered = apply_ignore(results, ignore)
    assert len(filtered) == 1
    assert filtered[0].requirement.name == "Django"


def test_apply_ignore_empty_set_keeps_all():
    results = [_make_result("requests"), _make_result("flask")]
    assert apply_ignore(results, set()) == results


def test_apply_ignore_returns_list():
    results = [_make_result("requests")]
    assert isinstance(apply_ignore(results, set()), list)
