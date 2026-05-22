"""Tests for dep_nudge.cli."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dep_nudge.cli import build_parser, run
from dep_nudge.checker import CheckResult
from dep_nudge.parser import Requirement


@pytest.fixture()
def req_file(tmp_path: Path) -> Path:
    f = tmp_path / "requirements.txt"
    f.write_text("requests==2.28.0\nflask==2.2.0\n")
    return f


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.requirements == "requirements.txt"
    assert args.no_colour is False
    assert args.exit_code is False


def test_build_parser_custom_file():
    parser = build_parser()
    args = parser.parse_args(["custom_reqs.txt"])
    assert args.requirements == "custom_reqs.txt"


def test_build_parser_flags():
    parser = build_parser()
    args = parser.parse_args(["--no-colour", "--exit-code", "reqs.txt"])
    assert args.no_colour is True
    assert args.exit_code is True


def test_run_missing_file(tmp_path: Path):
    missing = tmp_path / "missing.txt"
    code = run([str(missing)])
    assert code == 2


def test_run_empty_file(tmp_path: Path):
    empty = tmp_path / "requirements.txt"
    empty.write_text("")
    code = run([str(empty)])
    assert code == 0


def test_run_returns_zero_when_all_up_to_date(req_file: Path):
    result = CheckResult(
        requirement=Requirement("requests", "==", "2.28.0"),
        latest_version="2.28.0",
        is_outdated=False,
    )
    with patch("dep_nudge.cli.check_requirements", return_value=[result]):
        code = run([str(req_file)])
    assert code == 0


def test_run_exit_code_one_when_outdated_and_flag_set(req_file: Path):
    result = CheckResult(
        requirement=Requirement("requests", "==", "2.28.0"),
        latest_version="2.31.0",
        is_outdated=True,
    )
    with patch("dep_nudge.cli.check_requirements", return_value=[result]):
        code = run(["--exit-code", str(req_file)])
    assert code == 1


def test_run_no_exit_code_when_outdated_but_flag_not_set(req_file: Path):
    result = CheckResult(
        requirement=Requirement("requests", "==", "2.28.0"),
        latest_version="2.31.0",
        is_outdated=True,
    )
    with patch("dep_nudge.cli.check_requirements", return_value=[result]):
        code = run([str(req_file)])
    assert code == 0
