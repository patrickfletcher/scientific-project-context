"""Scientific Project Context library.

The pre-1.0 library is intentionally small and does not yet promise API
compatibility.  The command-line interface is implemented on top of the same
planning and application functions exposed by the package modules.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


DISTRIBUTION_NAME = "scientific-project-context"


def distribution_version() -> str:
    """Return the installed distribution version or an explicit source marker."""

    try:
        return version(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return "0+uninstalled"


__version__ = distribution_version()

