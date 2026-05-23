"""Integration tests: pin module working with real parser output."""

from __future__ import annotations

import textwrap

import pytest

from dep_nudge.checker import CheckResult
from dep_nudge.parser import parse_requirements
from dep_nudge.parser import Requirement
from dep_nudge.pin import generate_pinned, write_pinned


REQUIREMENTS_CONTENT = textwrap.dedent("""\
    requests==2.28.0
    flask>=2.0,<3.0
    numpy
    boto3==1.26.0
""")


@pytest.fixture()
def requirements_file(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text(REQUIREMENTS_CONTENT)
    return str(p)


def _fake_results(reqs: list[Requirement]) -> list[CheckResult]:
    """Simulate checker output: bump all pinned packages by a patch version.

    Packages with a ``==`` specifier get their patch component incremented by
    one to mimic a newer release being available.  Packages without a pinned
    version (e.g. range specifiers or bare names) are left with
    ``latest_version=None`` so that ``generate_pinned`` falls back to the
    original specifier.
    """
    results = []
    for req in reqs:
        latest = None
        if "==" in (req.specifier or ""):
            parts = req.specifier.lstrip("==").split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            latest = ".".join(parts)
        results.append(CheckResult(requirement=req, latest_version=latest, vulnerabilities=[]))
    return results


def test_pinned_output_line_count(requirements_file):
    reqs = parse_requirements(requirements_file)
    results = _fake_results(reqs)
    output = generate_pinned(results)
    lines = [l for l in output.splitlines() if l.strip()]
    assert len(lines) == len(reqs)


def test_pinned_output_contains_bumped_versions(requirements_file):
    reqs = parse_requirements(requirements_file)
    results = _fake_results(reqs)
    output = generate_pinned(results)
    assert "requests==2.28.1" in output
    assert "boto3==1.26.1" in output


def test_unpinned_packages_use_original_specifier(requirements_file):
    reqs = parse_requirements(requirements_file)
    results = _fake_results(reqs)
    output = generate_pinned(results)
    assert "flask>=2.0" in output


def test_bare_package_preserved_in_output(requirements_file):
    """A package with no specifier (e.g. 'numpy') should still appear in output."""
    reqs = parse_requirements(requirements_file)
    results = _fake_results(reqs)
    output = generate_pinned(results)
    assert "numpy" in output


def test_write_pinned_round_trip(requirements_file, tmp_path):
    reqs = parse_requirements(requirements_file)
    results = _fake_results(reqs)
    out_path = str(tmp_path / "pinned.txt")
    count = write_pinned(results, out_path)
    assert count == len(reqs)
    reparsed = parse_requirements(out_path)
    assert len(reparsed) == len(reqs)
    names = {r.name for r in reparsed}
    assert "requests" in names
    assert "flask" in names
