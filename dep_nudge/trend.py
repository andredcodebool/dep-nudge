"""Trend analysis: track how many packages are outdated over time."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from dep_nudge.audit import AuditResult

_DEFAULT_TREND_FILE = ".dep-nudge-trend.json"


@dataclass
class TrendEntry:
    """A single snapshot of package health on a given date."""

    date: str  # ISO-8601 date string
    total: int
    outdated: int
    vulnerable: int

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "total": self.total,
            "outdated": self.outdated,
            "vulnerable": self.vulnerable,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrendEntry":
        return cls(
            date=data["date"],
            total=data["total"],
            outdated=data["outdated"],
            vulnerable=data["vulnerable"],
        )

    def __str__(self) -> str:
        return (
            f"{self.date}: {self.outdated}/{self.total} outdated, "
            f"{self.vulnerable} vulnerable"
        )


def snapshot_from_results(results: List[AuditResult]) -> TrendEntry:
    """Build a TrendEntry from the current audit results."""
    today = date.today().isoformat()
    total = len(results)
    outdated = sum(1 for r in results if r.is_outdated)
    vulnerable = sum(1 for r in results if r.is_vulnerable)
    return TrendEntry(date=today, total=total, outdated=outdated, vulnerable=vulnerable)


def load_trend(path: str = _DEFAULT_TREND_FILE) -> List[TrendEntry]:
    """Load existing trend entries from *path*; return empty list if absent."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [TrendEntry.from_dict(entry) for entry in raw]


def save_trend(entries: List[TrendEntry], path: str = _DEFAULT_TREND_FILE) -> None:
    """Persist *entries* to *path* as JSON."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def record_snapshot(
    results: List[AuditResult], path: str = _DEFAULT_TREND_FILE
) -> TrendEntry:
    """Append a new snapshot to the trend file and return it."""
    entries = load_trend(path)
    entry = snapshot_from_results(results)
    entries.append(entry)
    save_trend(entries, path)
    return entry
