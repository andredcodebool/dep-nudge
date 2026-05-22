"""Command-line interface for dep-nudge."""

import argparse
import sys
from pathlib import Path

from dep_nudge.checker import check_requirements
from dep_nudge.parser import parse_requirements
from dep_nudge.report import has_outdated, print_report


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="dep-nudge",
        description="Scan requirements files and flag outdated packages.",
    )
    parser.add_argument(
        "requirements",
        nargs="?",
        default="requirements.txt",
        metavar="FILE",
        help="Path to requirements file (default: requirements.txt)",
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
        help="Exit with code 1 if any outdated packages are found",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    """Entry point for the CLI. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    req_path = Path(args.requirements)
    if not req_path.exists():
        print(f"dep-nudge: error: file not found: {req_path}", file=sys.stderr)
        return 2

    requirements = parse_requirements(req_path)
    if not requirements:
        print("No requirements found.")
        return 0

    results = check_requirements(requirements)
    print_report(results, colour=not args.no_colour)

    if args.exit_code and has_outdated(results):
        return 1

    return 0


def main() -> None:
    """Main entry point."""
    sys.exit(run())


if __name__ == "__main__":
    main()
