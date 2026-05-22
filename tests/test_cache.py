"""Tests for dep_nudge.cache."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from dep_nudge import cache as _cache_module
from dep_nudge.cache import clear, get, invalidate, set


@pytest.fixture()
def tmp_cache(tmp_path: Path):
    """Return a temporary cache directory."""
    return tmp_path / "cache"


def test_get_returns_none_for_missing_key(tmp_cache):
    assert get("missing", cache_dir=tmp_cache) is None


def test_set_and_get_round_trip(tmp_cache):
    set("pkg:requests", "2.31.0", cache_dir=tmp_cache)
    assert get("pkg:requests", cache_dir=tmp_cache) == "2.31.0"


def test_get_returns_none_after_ttl_expired(tmp_cache, monkeypatch):
    set("pkg:flask", "3.0.0", ttl=1, cache_dir=tmp_cache)
    # Advance time past TTL
    monkeypatch.setattr(time, "time", lambda: time.time() + 10)
    assert get("pkg:flask", cache_dir=tmp_cache) is None


def test_get_returns_value_within_ttl(tmp_cache):
    set("pkg:flask", "3.0.0", ttl=3600, cache_dir=tmp_cache)
    assert get("pkg:flask", cache_dir=tmp_cache) == "3.0.0"


def test_set_creates_cache_dir(tmp_path):
    cache_dir = tmp_path / "new" / "nested" / "cache"
    assert not cache_dir.exists()
    set("key", "value", cache_dir=cache_dir)
    assert cache_dir.exists()


def test_invalidate_removes_existing_key(tmp_cache):
    set("pkg:numpy", "1.26.0", cache_dir=tmp_cache)
    result = invalidate("pkg:numpy", cache_dir=tmp_cache)
    assert result is True
    assert get("pkg:numpy", cache_dir=tmp_cache) is None


def test_invalidate_returns_false_for_missing_key(tmp_cache):
    assert invalidate("nonexistent", cache_dir=tmp_cache) is False


def test_clear_removes_all_entries(tmp_cache):
    set("pkg:a", "1.0", cache_dir=tmp_cache)
    set("pkg:b", "2.0", cache_dir=tmp_cache)
    removed = clear(cache_dir=tmp_cache)
    assert removed == 2
    assert get("pkg:a", cache_dir=tmp_cache) is None
    assert get("pkg:b", cache_dir=tmp_cache) is None


def test_clear_on_missing_dir_returns_zero(tmp_path):
    missing = tmp_path / "does_not_exist"
    assert clear(cache_dir=missing) == 0


def test_cache_key_with_slashes(tmp_cache):
    """Keys with special characters should not cause path traversal issues."""
    set("some/key:value", [1, 2, 3], cache_dir=tmp_cache)
    assert get("some/key:value", cache_dir=tmp_cache) == [1, 2, 3]
