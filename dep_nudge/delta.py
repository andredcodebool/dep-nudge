"""Version delta helpers — classify how far behind a package is."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from packaging.version import Version, InvalidVersion


class BumpKind(str, Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class VersionDelta:
    current: Optional[str]
    latest: Optional[str]
    kind: BumpKind

    def __str__(self) -> str:  # pragma: no cover
        if self.kind is BumpKind.NONE:
            return f"{self.current} is up to date"
        if self.kind is BumpKind.UNKNOWN:
            return f"cannot compare {self.current!r} → {self.latest!r}"
        return f"{self.current} → {self.latest} ({self.kind.value} bump)"


def classify_bump(current: Optional[str], latest: Optional[str]) -> BumpKind:
    """Return the kind of version bump needed to reach *latest* from *current*."""
    if current is None or latest is None:
        return BumpKind.UNKNOWN
    try:
        cur = Version(current)
        lat = Version(latest)
    except InvalidVersion:
        return BumpKind.UNKNOWN

    if lat <= cur:
        return BumpKind.NONE
    if lat.major != cur.major:
        return BumpKind.MAJOR
    if lat.minor != cur.minor:
        return BumpKind.MINOR
    return BumpKind.PATCH


def compute_delta(current: Optional[str], latest: Optional[str]) -> VersionDelta:
    """Build a :class:`VersionDelta` for the given version pair."""
    kind = classify_bump(current, latest)
    return VersionDelta(current=current, latest=latest, kind=kind)
