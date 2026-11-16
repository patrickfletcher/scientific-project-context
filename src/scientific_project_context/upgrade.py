"""Bring a project's packaged text up to the installed version.

`spctx upgrade` does the mechanical part of an upgrade: it replaces the routing
block and the practice core between their markers, restores skill bodies,
replaces the packaged part of each skill description while keeping the
project's phrasings, keeps generated Claude pointers in step, and adds starter
files a newer version ships. It replaces only text it recognizes as an earlier
package version, unless told to replace edited text too. It never inserts a
routing block, never edits anything outside these regions, and never follows a
link. Judgment steps stay with the `spctx-project-context` skill.
"""

from __future__ import annotations

import difflib
import hashlib
import os
import re
import shutil
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .history import earlier_package_version
from .project import (
    AGENT_SKILLS,
    CONTEXT_ROUTE_BEGIN,
    CONTEXT_ROUTE_BLOCK,
    CONTEXT_ROUTE_END,
    SCIENTIFIC_PRACTICE_BEGIN,
    SCIENTIFIC_PRACTICE_END,
    SCIENTIFIC_PRACTICE_PATH,
    SKILL_TRIGGER_SEPARATOR,
    InitializationPlan,
    OperationError,
    _canonical_target,
    _link_kind,
    _regular_file_observation,
    _validate_existing_project_target,
    agent_skill_path,
    apply_initialization,
    build_claude_skill_stub,
    claude_skill_path,
    extract_managed_block,
    parse_agent_skill_content,
    plan_initialization,
)
from .resources import ResourceCatalog

REPLACED = "replaced"
CURRENT = "current"
SKIPPED_EDITED = "skipped_edited"
CREATED = "created"
REGENERATED = "regenerated"
REPORTED = "reported"
BLOCKED = "blocked"

_DESCRIPTION_LINE_RE = re.compile(r"^description:[^\r\n]*", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class UpgradeRegion:
    """What the upgrade does, or declines to do, with one tracked region."""

    path: str
    region: str
    action: str
    from_version: str | None
    note: str
    diff: str


@dataclass(frozen=True, slots=True)
class UpgradeFile:
    """One existing file the upgrade rewrites, with what it observed at planning."""

    relative_path: str
    original: bytes
    identity: tuple[int, int]
    planned: bytes


@dataclass(frozen=True, slots=True)
class UpgradePlan:
    target: Path
    resource_bundle_sha256: str
    replace_edited: bool
    regions: tuple[UpgradeRegion, ...]
    files: tuple[UpgradeFile, ...]
    initialization: InitializationPlan
    blocked: tuple[str, ...]
    pointer_updates: tuple[tuple[str, bytes, bytes], ...] = ()

    @property
    def created_files(self) -> tuple[str, ...]:
        return tuple(
            file.relative_path for file in self.initialization.files if file.disposition == "create"
        )

    @property
    def has_changes(self) -> bool:
        return bool(self.files or self.created_files)


@dataclass(frozen=True, slots=True)
class UpgradeResult:
    target: Path
    changed_files: tuple[str, ...]
    created_files: tuple[str, ...]


def _newline(content: str) -> str:
    return "\r\n" if "\r\n" in content else "\n"


def _with_newlines(text: str, newline: str) -> str:
    normalized = text.replace("\r\n", "\n")
    return normalized if newline == "\n" else normalized.replace("\n", "\r\n")


def _diff(before: str, after: str, label: str) -> str:
    lines = difflib.unified_diff(
        before.replace("\r\n", "\n").splitlines(keepends=True),
        after.replace("\r\n", "\n").splitlines(keepends=True),
        fromfile=f"{label} (now)",
        tofile=f"{label} (after upgrade)",
    )
    return "".join(lines)


def _replace_block(content: str, begin: str, end: str, block: str) -> str:
    """Replace the lines from one marker to the other, keeping everything else exactly."""

    lines = content.splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.rstrip("\r\n") == begin]
    ends = [index for index, line in enumerate(lines) if line.rstrip("\r\n") == end]
    first, last = starts[0], ends[0]
    trailing = lines[last][len(lines[last].rstrip("\r\n")) :]
    replacement = _with_newlines(block, _newline(content)) + trailing
    return "".join(lines[:first]) + replacement + "".join(lines[last + 1 :])


def _observe(root: Path, relative_path: str) -> tuple[bytes, tuple[int, int]] | None:
    path = root / relative_path
    if not os.path.lexists(path):
        return None
    return _regular_file_observation(path, label=relative_path)


def _plan_block(
    root: Path,
    relative_path: str,
    region: str,
    history_key: str,
    begin: str,
    end: str,
    packaged_block: str,
    replace_edited: bool,
    regions: list[UpgradeRegion],
    blocked: list[str],
) -> tuple[str, bytes, tuple[int, int]] | None:
    observed = _observe(root, relative_path)
    if observed is None:
        return None
    content_bytes, identity = observed
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        blocked.append(f"{relative_path} is not UTF-8 text.")
        return None
    state, block = extract_managed_block(content, begin, end)
    if state == "absent":
        if region == "routing block":
            regions.append(
                UpgradeRegion(
                    relative_path, region, REPORTED, None,
                    "No routing block here. Adding one is the project's decision; "
                    "`spctx init . --dry-run` prints it.",
                    "",
                )
            )
        else:
            blocked.append(f"{relative_path} has no marked {region}.")
        return None
    if state != "present" or block is None:
        blocked.append(f"{relative_path} has duplicated, unbalanced, or out-of-order {region} markers.")
        return None
    if block == packaged_block:
        regions.append(UpgradeRegion(relative_path, region, CURRENT, None, "", ""))
        return None
    version = earlier_package_version(history_key, block)
    diff = _diff(block, packaged_block, f"{relative_path}: {region}")
    if version is None and not replace_edited:
        regions.append(
            UpgradeRegion(
                relative_path, region, SKIPPED_EDITED, None,
                "This text matches no packaged version, so it was edited here. Move wording "
                "to keep outside the markers, then rerun with `--replace-edited`.",
                diff,
            )
        )
        return None
    regions.append(
        UpgradeRegion(
            relative_path, region, REPLACED, version,
            "" if version else "Edited text replaced because `--replace-edited` was given.",
            diff,
        )
    )
    return _replace_block(content, begin, end, packaged_block), content_bytes, identity


def _set_description(content: str, description: str) -> str:
    closing = content.index("\n---", 3)
    head, rest = content[:closing], content[closing:]
    head = _DESCRIPTION_LINE_RE.sub(lambda _: f"description: {description}", head, count=1)
    return head + rest


def plan_upgrade(
    catalog: ResourceCatalog,
    target: str | os.PathLike[str],
    *,
    replace_edited: bool = False,
) -> UpgradePlan:
    """Inspect a project and plan every replacement, without writing anything."""

    root = _canonical_target(target, operation="Upgrade")
    _validate_existing_project_target(root, operation="Upgrade")
    regions: list[UpgradeRegion] = []
    files: list[UpgradeFile] = []
    blocked: list[str] = []

    # Routing block and practice core.
    planned = _plan_block(
        root, "AGENTS.md", "routing block", "routing", CONTEXT_ROUTE_BEGIN, CONTEXT_ROUTE_END,
        CONTEXT_ROUTE_BLOCK, replace_edited, regions, blocked,
    )
    if planned:
        files.append(UpgradeFile("AGENTS.md", planned[1], planned[2], planned[0].encode("utf-8")))
    packaged_practice = catalog.get(f"template/{SCIENTIFIC_PRACTICE_PATH}").content.decode("utf-8")
    _, packaged_core = extract_managed_block(
        packaged_practice, SCIENTIFIC_PRACTICE_BEGIN, SCIENTIFIC_PRACTICE_END
    )
    assert packaged_core is not None
    planned = _plan_block(
        root, SCIENTIFIC_PRACTICE_PATH, "scientific-practice core", "practice_core",
        SCIENTIFIC_PRACTICE_BEGIN, SCIENTIFIC_PRACTICE_END, packaged_core, replace_edited,
        regions, blocked,
    )
    if planned:
        files.append(
            UpgradeFile(SCIENTIFIC_PRACTICE_PATH, planned[1], planned[2], planned[0].encode("utf-8"))
        )

    # Skills: body and the packaged part of the description.
    final_descriptions: dict[str, str] = {}
    for name in AGENT_SKILLS:
        relative_path = agent_skill_path(name)
        packaged_bytes = catalog.get(f"template/{relative_path}").content
        packaged = parse_agent_skill_content(packaged_bytes)
        observed = _observe(root, relative_path)
        if observed is None:
            final_descriptions[name] = packaged.description
            continue
        content_bytes, identity = observed
        try:
            installed = parse_agent_skill_content(content_bytes, expected_name=name)
            content = content_bytes.decode("utf-8")
        except (OperationError, UnicodeDecodeError) as exc:
            blocked.append(f"{relative_path} is not a valid Agent Skill: {exc}")
            continue

        new_content = content
        if installed.body != packaged.body:
            version = earlier_package_version(f"skill:{name}", installed.body)
            diff = _diff(installed.body + "\n", packaged.body + "\n", f"{relative_path}: body")
            if version is not None or replace_edited:
                regions.append(
                    UpgradeRegion(
                        relative_path, "skill body", REPLACED, version,
                        "" if version else "Edited body replaced because `--replace-edited` was given.",
                        diff,
                    )
                )
                new_content = _with_newlines(packaged_bytes.decode("utf-8"), _newline(content))
            else:
                regions.append(
                    UpgradeRegion(
                        relative_path, "skill body", SKIPPED_EDITED, None,
                        "This body matches no packaged version. Move project facts to the "
                        "instruction file or `.context/`, then rerun with `--replace-edited`.",
                        diff,
                    )
                )
        else:
            regions.append(UpgradeRegion(relative_path, "skill body", CURRENT, None, "", ""))

        prefix, separator, suffix = installed.description.partition(SKILL_TRIGGER_SEPARATOR)
        project_phrasings = (separator + suffix).strip()
        if prefix.strip() == packaged.description:
            description = installed.description
            regions.append(UpgradeRegion(relative_path, "skill description", CURRENT, None, "", ""))
        else:
            version = earlier_package_version(f"description:{name}", prefix.strip())
            proposed = packaged.description + (f" {project_phrasings}" if project_phrasings else "")
            diff = _diff(installed.description + "\n", proposed + "\n", f"{relative_path}: description")
            if version is None and not replace_edited:
                description = installed.description
                regions.append(
                    UpgradeRegion(
                        relative_path, "skill description", SKIPPED_EDITED, None,
                        "The packaged part of this description was rewritten here. Keep project "
                        f'phrasings after "{SKILL_TRIGGER_SEPARATOR}", then rerun with '
                        "`--replace-edited`.",
                        diff,
                    )
                )
            elif len(proposed) > 1024:
                description = installed.description
                blocked.append(
                    f"{relative_path}: the packaged description plus this project's phrasings "
                    "would exceed 1024 characters; shorten the phrasings."
                )
            else:
                description = proposed
                regions.append(
                    UpgradeRegion(
                        relative_path, "skill description", REPLACED, version,
                        "This project's phrasings were kept." if project_phrasings else "",
                        diff,
                    )
                )
        final_descriptions[name] = description
        if description != parse_agent_skill_content(new_content.encode("utf-8")).description:
            new_content = _set_description(new_content, description)
        if new_content != content:
            files.append(UpgradeFile(relative_path, content_bytes, identity, new_content.encode("utf-8")))

    # Claude pointers, only where the project already uses them.
    has_pointers = any(os.path.lexists(root / claude_skill_path(name)) for name in AGENT_SKILLS)
    if has_pointers:
        for name in AGENT_SKILLS:
            relative_path = claude_skill_path(name)
            observed = _observe(root, relative_path)
            if observed is None:
                continue
            if name not in final_descriptions:
                continue  # its skill is invalid, and the run is already blocked
            content_bytes, identity = observed
            expected = build_claude_skill_stub(name, final_descriptions[name])
            if content_bytes.replace(b"\r\n", b"\n") == expected:
                regions.append(UpgradeRegion(relative_path, "Claude pointer", CURRENT, None, "", ""))
                continue
            try:
                own = parse_agent_skill_content(content_bytes).description
            except OperationError:
                own = None
            if own is not None and content_bytes.replace(b"\r\n", b"\n") == build_claude_skill_stub(name, own):
                regions.append(
                    UpgradeRegion(
                        relative_path, "Claude pointer", REGENERATED, None,
                        "Generated pointer given its skill's description.",
                        _diff(own + "\n", final_descriptions[name] + "\n", f"{relative_path}: description"),
                    )
                )
                planned_bytes = expected
                if b"\r\n" in content_bytes:
                    planned_bytes = expected.replace(b"\n", b"\r\n")
                files.append(UpgradeFile(relative_path, content_bytes, identity, planned_bytes))
            else:
                regions.append(
                    UpgradeRegion(
                        relative_path, "Claude pointer", REPORTED, None,
                        "This pointer was edited here, so it was left alone; copy its skill's "
                        "description into it if it should match.",
                        "",
                    )
                )

    initialization = plan_initialization(catalog, root, "retrofit", claude=has_pointers)
    # A pointer added in this run must carry the description this run writes.
    pointer_updates: list[tuple[str, bytes, bytes]] = []
    for file in initialization.files:
        if file.disposition != "create":
            continue
        for name in AGENT_SKILLS:
            if file.relative_path == claude_skill_path(name) and name in final_descriptions:
                expected = build_claude_skill_stub(name, final_descriptions[name])
                if expected != file.content:
                    pointer_updates.append((file.relative_path, file.content, expected))
    for conflict in initialization.conflicts:
        blocked.append(f"Adding missing starter files is blocked: {conflict}")
    for file in initialization.files:
        if file.disposition == "create":
            regions.append(
                UpgradeRegion(
                    file.relative_path,
                    "starter file",
                    CREATED,
                    None,
                    "Shipped by this version and missing here.",
                    "",
                )
            )

    return UpgradePlan(
        target=root,
        resource_bundle_sha256=catalog.bundle_sha256,
        replace_edited=replace_edited,
        regions=tuple(regions),
        files=tuple(files),
        initialization=initialization,
        blocked=tuple(blocked),
        pointer_updates=tuple(pointer_updates),
    )


def _replace_atomically(path: Path, file: UpgradeFile) -> int:
    """Replace one file and return its original permission bits."""

    current, identity = _regular_file_observation(path, label=file.relative_path)
    mode = stat.S_IMODE(path.stat(follow_symlinks=False).st_mode)
    if identity != file.identity or current != file.original:
        raise OperationError(f"{file.relative_path} changed after the upgrade was planned; rerun it.")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(file.planned)
            handle.flush()
            os.fsync(handle.fileno())
        shutil.copystat(path, temporary, follow_symlinks=False)
        current, identity = _regular_file_observation(path, label=file.relative_path)
        if identity != file.identity or current != file.original:
            raise OperationError(f"{file.relative_path} changed during the upgrade; rerun it.")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return mode


def _restore(path: Path, original: bytes, mode: int) -> str | None:
    try:
        if _link_kind(path) is not None:
            return f"{path} became a link"
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            handle.write(original)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
        return None
    except OSError as exc:
        return f"{path}: {exc}"


def _remove_created(path: Path, expected: bytes) -> str | None:
    try:
        if _link_kind(path) is not None or not path.is_file():
            return f"{path} is no longer the file this upgrade added"
        if path.read_bytes() != expected:
            return f"{path} changed after this upgrade added it"
        path.unlink()
        return None
    except OSError as exc:
        return f"{path}: {exc}"


def apply_upgrade(plan: UpgradePlan) -> UpgradeResult:
    """Apply a plan: add missing starter files, then replace files one by one.

    Missing files go first, because adding them checks every starter file
    against what was observed at planning. Every replaced file is checked the
    same way just before it is written. If any step fails, replaced files get
    their original bytes back and added files are removed, and the failure says
    whether that was complete.
    """

    if plan.blocked:
        raise OperationError("The upgrade is blocked; no file was changed.")
    created: tuple[str, ...] = ()
    if plan.created_files:
        created = apply_initialization(plan.initialization).created_files
    planned_creations = {file.relative_path: file.content for file in plan.initialization.files}
    replaced: list[tuple[UpgradeFile, int]] = []
    try:
        for file in plan.files:
            mode = _replace_atomically(plan.target / file.relative_path, file)
            replaced.append((file, mode))
        for relative_path, created_bytes, expected in plan.pointer_updates:
            path = plan.target / relative_path
            if relative_path in created:
                current, identity = _regular_file_observation(path, label=relative_path)
                pointer = UpgradeFile(relative_path, created_bytes, identity, expected)
                if current == created_bytes:
                    _replace_atomically(path, pointer)
    except Exception as exc:
        failures = [
            failure
            for failure in (
                _restore(plan.target / file.relative_path, file.original, mode)
                for file, mode in reversed(replaced)
            )
            if failure is not None
        ]
        failures.extend(
            failure
            for failure in (
                _remove_created(plan.target / path, planned_creations[path]) for path in created
            )
            if failure is not None
        )
        if failures:
            raise OperationError(
                f"Upgrade failed ({exc}); undoing it was incomplete: {'; '.join(failures)}"
            ) from exc
        raise
    return UpgradeResult(
        target=plan.target,
        changed_files=tuple(file.relative_path for file, _ in replaced),
        created_files=tuple(created),
    )


def plan_digest(plan: UpgradePlan) -> str:
    digest = hashlib.sha256()
    for file in plan.files:
        digest.update(file.relative_path.encode("utf-8") + b"\0" + file.planned + b"\0")
    return digest.hexdigest()
