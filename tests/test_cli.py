"""Tests for dep_nudge.cli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dep_nudge.cli import build_parser, run


@pytest.fixture()
def req_file(tmp_path: Path) -> Path:
    p = tmp_path / "requirements.txt"
    p.write_text("requests==2.28.0\nflask==2.2.0\n")
    return p


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.file == "requirements.txt"
    assert args.no_cache is False
    assert args.clear_cache is False
    assert args.no_colour is False
    assert args.exit_code is False


def test_build_parser_custom_file():
    parser = build_parser()
    args = parser.parse_args(["custom.txt"])
    assert args.file == "custom.txt"


def test_build_parser_flags():
    parser = build_parser()
    args = parser.parse_args(["--no-cache", "--no-colour", "--exit-code"])
    assert args.no_cache is True
    assert args.no_colour is True
    assert args.exit_code is True


def test_run_missing_file(tmp_path, capsys):
    parser = build_parser()
    args = parser.parse_args([str(tmp_path / "nope.txt")])
    code = run(args)
    assert code == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_run_clear_cache(capsys):
    parser = build_parser()
    args = parser.parse_args(["--clear-cache"])
    with patch("dep_nudge.cli._cache.clear", return_value=5) as mock_clear:
        code = run(args)
    assert code == 0
    mock_clear.assert_called_once()
    captured = capsys.readouterr()
    assert "5" in captured.out


def test_run_success_no_outdated(req_file):
    parser = build_parser()
    args = parser.parse_args([str(req_file), "--no-cache", "--exit-code"])
    mock_results = [MagicMock(is_outdated=False, is_unpinned=False)]
    with patch("dep_nudge.cli.check_requirements", return_value=mock_results), \
         patch("dep_nudge.cli.print_report"):
        code = run(args)
    assert code == 0


def test_run_exit_code_when_outdated(req_file):
    parser = build_parser()
    args = parser.parse_args([str(req_file), "--no-cache", "--exit-code"])
    mock_results = [MagicMock(is_outdated=True, is_unpinned=False)]
    with patch("dep_nudge.cli.check_requirements", return_value=mock_results), \
         patch("dep_nudge.cli.print_report"), \
         patch("dep_nudge.cli.has_outdated", return_value=True):
        code = run(args)
    assert code == 1


def test_run_no_exit_code_flag_ignores_outdated(req_file):
    parser = build_parser()
    args = parser.parse_args([str(req_file), "--no-cache"])
    mock_results = [MagicMock(is_outdated=True, is_unpinned=False)]
    with patch("dep_nudge.cli.check_requirements", return_value=mock_results), \
         patch("dep_nudge.cli.print_report"):
        code = run(args)
    assert code == 0
