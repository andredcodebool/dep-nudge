"""Command-line interface for dep-nudge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dep_nudge import cache as _cache
from dep_nudge.checker import check_requirements
from dep_nudge.parser import parse_requirements
from dep_nudge.report import has_outdated, print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dep-nudge",
        description="Scan requirements files and flag outdated or vulnerable packages.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="Bypass the local cache and always fetch fresh data",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        default=False,
        help="Clear the local cache and exit",
    )
    parser.add_argument(
        "--no-colour",
        action="store_true",
        default=False,
        help="Disable coloured output",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if any packages are outdated",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    if args.clear_cache:
        removed = _cache.clear()
        print(f"Cache cleared ({removed} entries removed).")
        return 0

    req_path = Path(args.file)
    if not req_path.exists():
        print(f"Error: file not found: {req_path}", file=sys.stderr)
        return 2

    requirements = parse_requirements(req_path)
    use_cache = not args.no_cache
    results = check_requirements(requirements, use_cache=use_cache)
    print_report(results, colour=not args.no_colour)

    if args.exit_code and has_outdated(results):
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))
