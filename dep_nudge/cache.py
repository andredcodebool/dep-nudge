"""Simple file-based cache for PyPI and vulnerability API responses."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

_DEFAULT_CACHE_DIR = Path.home() / ".dep_nudge" / "cache"
_DEFAULT_TTL = 3600  # seconds


def _cache_path(key: str, cache_dir: Path) -> Path:
    """Return the file path for a given cache key."""
    safe_key = key.replace("/", "_").replace(":", "_")
    return cache_dir / f"{safe_key}.json"


def get(key: str, cache_dir: Path = _DEFAULT_CACHE_DIR) -> Optional[Any]:
    """Return cached value for *key* if present and not expired, else None."""
    path = _cache_path(key, cache_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - data["timestamp"] > data["ttl"]:
            path.unlink(missing_ok=True)
            return None
        return data["value"]
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def set(
    key: str,
    value: Any,
    ttl: int = _DEFAULT_TTL,
    cache_dir: Path = _DEFAULT_CACHE_DIR,
) -> None:
    """Persist *value* under *key* with the given *ttl* in seconds."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = _cache_path(key, cache_dir)
    payload = {"timestamp": time.time(), "ttl": ttl, "value": value}
    path.write_text(json.dumps(payload), encoding="utf-8")


def invalidate(key: str, cache_dir: Path = _DEFAULT_CACHE_DIR) -> bool:
    """Remove a single cache entry.  Returns True if it existed."""
    path = _cache_path(key, cache_dir)
    if path.exists():
        path.unlink(missing_ok=True)
        return True
    return False


def clear(cache_dir: Path = _DEFAULT_CACHE_DIR) -> int:
    """Delete all cache entries.  Returns the number of files removed."""
    if not cache_dir.exists():
        return 0
    removed = 0
    for entry in cache_dir.glob("*.json"):
        entry.unlink(missing_ok=True)
        removed += 1
    return removed
