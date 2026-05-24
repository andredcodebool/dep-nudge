"""Baseline snapshot management for dep-nudge.

Allows saving and loading a baseline of package versions so that
subsequent runs can report only *new* issues since the baseline was set.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_BASELINE_FILE = ".dep-nudge-baseline.json"


def _default_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / DEFAULT_BASELINE_FILE


def save_baseline(
    package_versions: Dict[str, Optional[str]],
    path: Optional[str] = None,
) -> Path:
    """Persist a mapping of package name -> pinned version to disk."""
    target = Path(path) if path else _default_path()
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "packages": package_versions,
    }
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def load_baseline(path: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Load a previously saved baseline.  Returns an empty dict if missing."""
    target = Path(path) if path else _default_path()
    if not target.exists():
        return {}
    data = json.loads(target.read_text(encoding="utf-8"))
    return data.get("packages", {})


def new_since_baseline(
    current: Dict[str, Optional[str]],
    baseline: Dict[str, Optional[str]],
) -> List[str]:
    """Return package names whose version differs from the baseline.

    A package is considered *new* if it was absent from the baseline or
    if its version has changed (e.g. a new outdated version was detected).
    """
    changed: List[str] = []
    for name, version in current.items():
        if name not in baseline or baseline[name] != version:
            changed.append(name)
    return sorted(changed)
