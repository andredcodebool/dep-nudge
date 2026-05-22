"""Command-line interface for dep-nudge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dep_nudge.checker import check_requirements
from dep_nudge.parser import parse_requirements
from dep_nudge.report import print_report, has_outdated
from dep_nudge.formatter import render, SUPPORTED_FORMATS


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for dep-nudge."""
    parser = argparse.ArgumentParser(
        prog="dep-nudge",
        description="Scan requirements files for outdated or vulnerable packages.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)",
    )
    parser.add_argument(
        "--no-colour",
        action="store_true",
        default=False,
        help="Disable coloured output",
    )
    parser.add_argument(
        "--exit-zero",
        action="store_true",
        default=False,
        help="Always exit with code 0 even when issues are found",
    )
    parser.add_argument(
        "--format",
        choices=SUPPORTED_FORMATS,
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout (only for json/csv formats)",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    """Execute the main logic; return the process exit code."""
    req_path = Path(args.file)
    if not req_path.exists():
        print(f"dep-nudge: file not found: {req_path}", file=sys.stderr)
        return 2

    requirements = parse_requirements(req_path)
    results = check_requirements(requirements)

    if args.format in ("json", "csv"):
        rendered = render(results, args.format)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered)
    else:
        print_report(results, colour=not args.no_colour)

    if args.exit_zero:
        return 0
    return 1 if has_outdated(results) else 0


def main() -> None:  # pragma: no cover
    """Entry point registered in pyproject.toml."""
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))
