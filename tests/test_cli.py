"""Tests for dep_nudge.cli (including --format / --output flags)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dep_nudge.cli import build_parser, run


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def req_file(tmp_path: Path) -> Path:
    f = tmp_path / "requirements.txt"
    f.write_text("requests==2.28.0\n")
    return f


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.file == "requirements.txt"
    assert args.no_colour is False
    assert args.exit_zero is False
    assert args.format == "text"
    assert args.output is None


def test_build_parser_custom_file():
    args = build_parser().parse_args(["custom.txt"])
    assert args.file == "custom.txt"


def test_build_parser_flags():
    args = build_parser().parse_args(["--no-colour", "--exit-zero"])
    assert args.no_colour is True
    assert args.exit_zero is True


def test_build_parser_format_json():
    args = build_parser().parse_args(["--format", "json"])
    assert args.format == "json"


def test_build_parser_format_csv():
    args = build_parser().parse_args(["--format", "csv"])
    assert args.format == "csv"


def test_build_parser_output_flag():
    args = build_parser().parse_args(["--format", "json", "--output", "out.json"])
    assert args.output == "out.json"


# ---------------------------------------------------------------------------
# run – missing file
# ---------------------------------------------------------------------------

def test_run_missing_file(tmp_path):
    args = build_parser().parse_args([str(tmp_path / "missing.txt")])
    assert run(args) == 2


# ---------------------------------------------------------------------------
# run – json format prints to stdout
# ---------------------------------------------------------------------------

def test_run_json_format_prints_to_stdout(req_file, capsys):
    mock_result = MagicMock()
    mock_result.is_outdated = False
    mock_result.vulnerabilities = []
    mock_result.requirement.name = "requests"
    mock_result.requirement.specifier = "==2.28.0"
    mock_result.latest_version = "2.28.0"

    with patch("dep_nudge.cli.parse_requirements", return_value=[MagicMock()]), \
         patch("dep_nudge.cli.check_requirements", return_value=[mock_result]):
        args = build_parser().parse_args([str(req_file), "--format", "json"])
        code = run(args)

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert isinstance(parsed, list)
    assert code == 0


# ---------------------------------------------------------------------------
# run – json format writes to file
# ---------------------------------------------------------------------------

def test_run_json_format_writes_to_file(req_file, tmp_path):
    out_file = tmp_path / "report.json"
    mock_result = MagicMock()
    mock_result.is_outdated = False
    mock_result.vulnerabilities = []
    mock_result.requirement.name = "requests"
    mock_result.requirement.specifier = "==2.28.0"
    mock_result.latest_version = "2.28.0"

    with patch("dep_nudge.cli.parse_requirements", return_value=[MagicMock()]), \
         patch("dep_nudge.cli.check_requirements", return_value=[mock_result]):
        args = build_parser().parse_args(
            [str(req_file), "--format", "json", "--output", str(out_file)]
        )
        run(args)

    assert out_file.exists()
    parsed = json.loads(out_file.read_text())
    assert isinstance(parsed, list)


# ---------------------------------------------------------------------------
# run – exit-zero overrides outdated exit code
# ---------------------------------------------------------------------------

def test_run_exit_zero_overrides_outdated(req_file):
    mock_result = MagicMock()
    mock_result.is_outdated = True
    mock_result.vulnerabilities = []

    with patch("dep_nudge.cli.parse_requirements", return_value=[MagicMock()]), \
         patch("dep_nudge.cli.check_requirements", return_value=[mock_result]), \
         patch("dep_nudge.cli.print_report"):
        args = build_parser().parse_args([str(req_file), "--exit-zero"])
        assert run(args) == 0
