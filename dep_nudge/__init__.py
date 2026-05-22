"""dep-nudge: scan requirements files and flag outdated or vulnerable packages."""

__version__ = "0.1.0"
__author__ = "dep-nudge contributors"

from dep_nudge.parser import Requirement, parse_requirements

__all__ = ["parse_requirements", "Requirement"]
