"""Tests for dep_nudge.delta."""

import pytest

from dep_nudge.delta import BumpKind, VersionDelta, classify_bump, compute_delta


# ---------------------------------------------------------------------------
# classify_bump
# ---------------------------------------------------------------------------


class TestClassifyBump:
    def test_none_current_returns_unknown(self):
        assert classify_bump(None, "2.0.0") is BumpKind.UNKNOWN

    def test_none_latest_returns_unknown(self):
        assert classify_bump("1.0.0", None) is BumpKind.UNKNOWN

    def test_both_none_returns_unknown(self):
        assert classify_bump(None, None) is BumpKind.UNKNOWN

    def test_invalid_version_string_returns_unknown(self):
        assert classify_bump("not-a-version", "2.0.0") is BumpKind.UNKNOWN

    def test_same_version_returns_none(self):
        assert classify_bump("1.2.3", "1.2.3") is BumpKind.NONE

    def test_latest_older_returns_none(self):
        assert classify_bump("2.0.0", "1.9.9") is BumpKind.NONE

    def test_major_bump(self):
        assert classify_bump("1.9.9", "2.0.0") is BumpKind.MAJOR

    def test_minor_bump(self):
        assert classify_bump("1.2.0", "1.3.0") is BumpKind.MINOR

    def test_patch_bump(self):
        assert classify_bump("1.2.3", "1.2.4") is BumpKind.PATCH

    def test_major_takes_priority_over_minor(self):
        assert classify_bump("0.9.0", "1.0.0") is BumpKind.MAJOR


# ---------------------------------------------------------------------------
# compute_delta
# ---------------------------------------------------------------------------


class TestComputeDelta:
    def test_returns_version_delta_instance(self):
        result = compute_delta("1.0.0", "2.0.0")
        assert isinstance(result, VersionDelta)

    def test_preserves_current(self):
        delta = compute_delta("1.0.0", "1.0.1")
        assert delta.current == "1.0.0"

    def test_preserves_latest(self):
        delta = compute_delta("1.0.0", "1.0.1")
        assert delta.latest == "1.0.1"

    def test_kind_set_correctly_for_patch(self):
        delta = compute_delta("1.0.0", "1.0.1")
        assert delta.kind is BumpKind.PATCH

    def test_kind_set_correctly_for_major(self):
        delta = compute_delta("1.0.0", "3.0.0")
        assert delta.kind is BumpKind.MAJOR

    def test_kind_unknown_when_current_is_none(self):
        delta = compute_delta(None, "1.0.0")
        assert delta.kind is BumpKind.UNKNOWN

    def test_kind_none_when_up_to_date(self):
        delta = compute_delta("4.5.6", "4.5.6")
        assert delta.kind is BumpKind.NONE
