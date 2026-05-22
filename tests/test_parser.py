"""Tests for dep_nudge.parser module."""

import textwrap
from pathlib import Path

import pytest

from dep_nudge.parser import Requirement, parse_requirements


@pytest.fixture()
def requirements_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        # This is a comment
        requests==2.28.0
        flask>=2.0,<3.0
        numpy
        boto3[crt]==1.26.0
        -r base.txt
        --index-url https://pypi.org/simple

        pytest>=7.0  # dev dependency
    """)
    req_file = tmp_path / "requirements.txt"
    req_file.write_text(content, encoding="utf-8")
    return req_file


def test_parse_returns_list_of_requirements(requirements_file: Path) -> None:
    reqs = parse_requirements(requirements_file)
    assert isinstance(reqs, list)
    assert all(isinstance(r, Requirement) for r in reqs)


def test_parse_correct_count(requirements_file: Path) -> None:
    reqs = parse_requirements(requirements_file)
    # Expects: requests, flask, numpy, boto3, pytest  (5 packages)
    assert len(reqs) == 5


def test_parse_package_names(requirements_file: Path) -> None:
    reqs = parse_requirements(requirements_file)
    names = [r.name for r in reqs]
    assert "requests" in names
    assert "flask" in names
    assert "numpy" in names
    assert "boto3" in names
    assert "pytest" in names


def test_parse_specifiers(requirements_file: Path) -> None:
    reqs = parse_requirements(requirements_file)
    by_name = {r.name: r for r in reqs}
    assert by_name["requests"].specifier == "==2.28.0"
    assert by_name["numpy"].specifier == ""


def test_parse_extras(requirements_file: Path) -> None:
    reqs = parse_requirements(requirements_file)
    by_name = {r.name: r for r in reqs}
    assert by_name["boto3"].extras == "[crt]"
    assert by_name["requests"].extras is None


def test_parse_line_numbers(requirements_file: Path) -> None:
    reqs = parse_requirements(requirements_file)
    by_name = {r.name: r for r in reqs}
    assert by_name["requests"].line_number == 2


def test_parse_file_not_found() -> None:
    with pytest.raises(FileNotFoundError, match="Requirements file not found"):
        parse_requirements("/nonexistent/requirements.txt")


def test_requirement_str() -> None:
    req = Requirement(name="requests", specifier="==2.28.0", line_number=1,
                      raw_line="requests==2.28.0")
    assert str(req) == "requests==2.28.0"


def test_requirement_str_with_extras() -> None:
    req = Requirement(name="boto3", specifier="==1.26.0", line_number=1,
                      raw_line="boto3[crt]==1.26.0", extras="[crt]")
    assert str(req) == "boto3[crt]==1.26.0"
