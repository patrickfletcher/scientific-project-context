"""Describe where this `spctx` came from, so a project can record how to upgrade it.

Installed metadata says which source a direct install used (PEP 610
`direct_url.json`) and which tool installed it (`INSTALLER`). From those this
module builds the `Context tools` line for a project's instruction file. Paths
are shown relative to the project or the home directory, so the line carries no
user name; a path outside both is flagged as specific to this machine.
"""

from __future__ import annotations

import json
import os
import sys
from importlib import metadata
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit
from urllib.request import url2pathname

DISTRIBUTION = "scientific-project-context"


def _display_path(path: Path, project: Path) -> tuple[str, bool]:
    """Return a shareable form of a path and whether it is machine-specific."""

    path = Path(os.path.abspath(path))
    project = Path(os.path.abspath(project))
    bases = [(project, "")]
    if project.parent != project.parent.parent:
        bases.append((project.parent, "../"))
    for base, prefix in bases:
        try:
            relative = path.relative_to(base).as_posix()
        except ValueError:
            continue
        if relative == ".":
            return (prefix.rstrip("/") or "."), False
        return prefix + relative, False
    try:
        return "~/" + path.relative_to(Path.home()).as_posix(), False
    except ValueError:
        return path.as_posix(), True


def _without_credentials(url: str) -> str:
    parts = urlsplit(url)
    if parts.username and parts.username != "git":
        host = parts.hostname or ""
        if parts.port:
            host += f":{parts.port}"
        return urlunsplit((parts.scheme, host, parts.path, parts.query, parts.fragment))
    return url


def describe_installation(project: Path) -> dict[str, object] | None:
    """Return the environment, install source, and suggested lines, or None from source."""

    try:
        distribution = metadata.distribution(DISTRIBUTION)
    except metadata.PackageNotFoundError:
        return None

    executable, executable_specific = _display_path(Path(sys.executable), project)
    environment, environment_specific = _display_path(Path(sys.prefix), project)
    installer = (distribution.read_text("INSTALLER") or "").strip().lower() or "unknown"
    try:
        direct = json.loads(distribution.read_text("direct_url.json") or "null")
    except ValueError:
        direct = None

    kind = "unrecorded"
    source: str | None = None
    specifier: str | None = None
    source_specific = False
    if isinstance(direct, dict) and isinstance(direct.get("url"), str):
        url = _without_credentials(direct["url"])
        vcs = direct.get("vcs_info")
        if isinstance(vcs, dict) and vcs.get("vcs") == "git":
            kind = "git"
            source = url
            specifier = f"git+{url}"
        elif url.startswith("file:") and isinstance(direct.get("dir_info"), dict):
            kind = "local_directory"
            local = Path(url2pathname(unquote(urlsplit(url).path)))
            source, source_specific = _display_path(local, project)
            specifier = source
        else:
            kind = "archive"
            source = url

    command: str | None = None
    if specifier is not None:
        if installer == "uv":
            command = f"uv pip install --python {executable} --upgrade"
            if kind == "local_directory":
                command += f" --reinstall-package {DISTRIBUTION}"
            command += f" {specifier}"
        else:
            command = f"{executable} -m pip install --upgrade {specifier}"

    if command is not None:
        line = (
            f"`spctx` is installed in the environment at `{environment}`; upgrade it there with "
            f"`{command}`."
        )
    else:
        line = (
            f"`spctx` is installed in the environment at `{environment}`; its install source "
            "is not recorded, so ask before upgrading it and never install it by name from a "
            "public package index."
        )
    return {
        "environment": environment,
        "interpreter": executable,
        "installer": installer,
        "source_kind": kind,
        "source": source,
        "upgrade_command": command,
        "machine_specific": executable_specific or environment_specific or source_specific,
        "context_tools_line": line,
    }
