"""Command-line interface for Scientific Project Context."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence, TextIO

from . import DISTRIBUTION_NAME, __version__
from .health import HealthError, check_project, diff_managed_regions
from .project import (
    INITIALIZATION_MODES,
    OperationError,
    apply_index_sync,
    apply_initialization,
    infer_initialization_mode,
    plan_index_sync,
    plan_initialization,
)
from .reporting import (
    error_report,
    health_error_report,
    health_report,
    index_sync_report,
    initialization_report,
    render_human,
    render_json,
)
from .resources import ResourceCatalog, ResourceError, load_packaged_resources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spctx",
        description="Keep compact, current context in a scientific project.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{DISTRIBUTION_NAME} {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser(
        "init",
        help="Add missing starter files, keeping existing files untouched.",
    )
    init.add_argument("target", help="Project directory to initialize.")
    init.add_argument(
        "--mode",
        choices=INITIALIZATION_MODES,
        help=(
            "Force new or retrofit behavior. By default, a missing/empty target uses new "
            "mode and any populated directory uses retrofit mode."
        ),
    )
    init.add_argument("--dry-run", action="store_true", help="Plan without writing.")
    init.add_argument(
        "--claude",
        action="store_true",
        help=(
            "Also add pointer skills under .claude/skills/, which is where Claude Code "
            "looks for them. Each one routes to the procedure in .agents/skills/."
        ),
    )
    init.add_argument("--json", action="store_true", help="Emit a versioned JSON report.")

    check = subparsers.add_parser(
        "check",
        help="Report what a project's context files currently have set up.",
    )
    check.add_argument("target", help="Project directory to check.")
    check.add_argument(
        "--diff",
        action="store_true",
        help="Show how regions that track the packaged version differ.",
    )
    check.add_argument("--json", action="store_true", help="Emit a versioned JSON report.")

    sync_index = subparsers.add_parser(
        "sync-index",
        help="Update the generated inventory in the context index.",
    )
    sync_index.add_argument("target", help="Initialized project directory to inspect.")
    sync_index.add_argument("--dry-run", action="store_true", help="Plan without writing.")
    sync_index.add_argument(
        "--json",
        action="store_true",
        help="Emit a versioned JSON report.",
    )
    return parser


def _emit(report: dict[str, object], *, as_json: bool, stream: TextIO) -> None:
    stream.write(render_json(report) if as_json else render_human(report))


def _run_init(
    args: argparse.Namespace,
    *,
    catalog: ResourceCatalog | None,
    output: TextIO,
) -> int:
    loaded_catalog = catalog
    selected_mode = args.mode
    try:
        if loaded_catalog is None:
            loaded_catalog = load_packaged_resources()
        if selected_mode is None:
            selected_mode = infer_initialization_mode(args.target)
        plan = plan_initialization(
            loaded_catalog,
            args.target,
            selected_mode,
            claude=args.claude,
        )
        if plan.conflicts:
            report = initialization_report(plan, dry_run=args.dry_run)
            _emit(report, as_json=args.json, stream=output)
            return 2
        if args.dry_run:
            report = initialization_report(plan, dry_run=True)
        else:
            applied = apply_initialization(plan)
            report = initialization_report(plan, dry_run=False, applied=applied)
        _emit(report, as_json=args.json, stream=output)
        return 0
    except (OperationError, ResourceError, OSError, ValueError) as exc:
        report = error_report(
            str(exc),
            target=args.target,
            mode=selected_mode or "auto",
            dry_run=args.dry_run,
            resource_bundle_sha256=(
                loaded_catalog.bundle_sha256 if loaded_catalog is not None else None
            ),
        )
        _emit(report, as_json=args.json, stream=output)
        return 2


def _run_check(
    args: argparse.Namespace,
    *,
    catalog: ResourceCatalog | None,
    output: TextIO,
) -> int:
    """Report project state; the exit code says only whether it could be read."""

    loaded_catalog = catalog
    try:
        if loaded_catalog is None:
            loaded_catalog = load_packaged_resources()
        result = check_project(loaded_catalog, args.target)
        differences = (
            diff_managed_regions(loaded_catalog, args.target) if args.diff else None
        )
        report = health_report(result, differences=differences)
        _emit(report, as_json=args.json, stream=output)
        return 0
    except (HealthError, ResourceError, OSError, ValueError) as exc:
        report = health_error_report(
            str(exc),
            target=args.target,
            resource_bundle_sha256=(
                loaded_catalog.bundle_sha256 if loaded_catalog is not None else None
            ),
        )
        _emit(report, as_json=args.json, stream=output)
        return 2


def _run_sync_index(
    args: argparse.Namespace,
    *,
    catalog: ResourceCatalog | None,
    output: TextIO,
) -> int:
    loaded_catalog = catalog
    try:
        if loaded_catalog is None:
            loaded_catalog = load_packaged_resources()
        plan = plan_index_sync(loaded_catalog, args.target)
        if plan.conflicts:
            report = index_sync_report(plan, dry_run=args.dry_run)
            _emit(report, as_json=args.json, stream=output)
            return 2
        if args.dry_run:
            report = index_sync_report(plan, dry_run=True)
        else:
            applied = apply_index_sync(plan)
            report = index_sync_report(plan, dry_run=False, applied=applied)
        _emit(report, as_json=args.json, stream=output)
        return 0
    except (OperationError, ResourceError, OSError, UnicodeError, ValueError) as exc:
        report = error_report(
            str(exc),
            operation="sync-index",
            target=args.target,
            dry_run=args.dry_run,
            resource_bundle_sha256=(
                loaded_catalog.bundle_sha256 if loaded_catalog is not None else None
            ),
        )
        _emit(report, as_json=args.json, stream=output)
        return 2


def main(
    argv: Sequence[str] | None = None,
    *,
    catalog: ResourceCatalog | None = None,
    stdout: TextIO | None = None,
) -> int:
    """Run the CLI; an injected catalog keeps raw-source tests explicit."""

    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout if stdout is not None else sys.stdout

    if args.command == "init":
        return _run_init(args, catalog=catalog, output=output)
    if args.command == "check":
        return _run_check(args, catalog=catalog, output=output)
    if args.command == "sync-index":
        return _run_sync_index(args, catalog=catalog, output=output)
    parser.error(f"unknown command: {args.command}")  # pragma: no cover
