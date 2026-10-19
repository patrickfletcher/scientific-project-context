"""Deterministic, read-only structural health checks for project context."""

from __future__ import annotations

import os
import re
import stat
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path, PurePosixPath
from typing import Iterable, Iterator, Sequence

from .project import (
    AGENT_SKILLS,
    CONTEXT_EMPTY_INVENTORY_LINE,
    CONTEXT_INVENTORY_BEGIN,
    CONTEXT_INVENTORY_END,
    DRAFT_CONTEXT_MARKER,
    PROJECT_CONTEXT_PATH,
    SCIENTIFIC_PRACTICE_BEGIN,
    SCIENTIFIC_PRACTICE_END,
    SCIENTIFIC_PRACTICE_PATH,
    SKILL_TRIGGER_SEPARATOR,
    CONTEXT_ROUTE_BEGIN,
    CONTEXT_ROUTE_BLOCK,
    CONTEXT_ROUTE_END,
    OperationError,
    agent_skill_path,
    claude_skill_path,
    collect_context_guidance,
    compare_agent_skill,
    discover_specialized_owners,
    extract_context_guidance,
    extract_managed_block,
    managed_block_state,
    parse_agent_skill_content,
    rewrite_context_inventory,
    validate_agent_skill_content,
)
from .resources import ResourceCatalog, STARTER_INVENTORY, TEMPLATE_INVENTORY


# The skill tells agents to write the bare marker, so accept it with or without
# the emphasis and colon a project may add around it.
DRAFT_CONTEXT_MARKER_RE = re.compile(
    rf"^\s*[*_`\s]*{re.escape(DRAFT_CONTEXT_MARKER)}",
    re.IGNORECASE,
)

TEMPLATE_RESOURCE_TARGET = "resource-catalog:template"
CONTEXT_GUIDANCE_LABELS = ("purpose", "read when", "update when")

DUPLICATE_MIN_WORDS = 12
DUPLICATE_MAX_FINDINGS = 8
DUPLICATE_WORD_RE = re.compile(r"[a-z0-9]+")
FENCED_CODE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]\n]*)\]\([^)\n]*\)")

STALE_REFERENCE_MAX_FINDINGS = 8
# A repository-relative path with a directory and a file extension, and nothing else.
STALE_REFERENCE_RE = re.compile(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)+\.[A-Za-z0-9]{1,6}")

PRACTICE_PROJECT_SECTION = "This Project's Practice"
# A bracketed prompt the starter ships, excluding Markdown links.
BRACKETED_PROMPT_RE = re.compile(r"\[[^\]\n]+\](?!\()")

# Files whose shipped prompts a project is meant to replace with its own answers.
PROMPTED_STARTER_PATHS = ("AGENTS.md", PROJECT_CONTEXT_PATH)

# The compact context field that decides how much evidence a change owes.
RELIED_ON_FIELD = "What later work relies on"
RELIED_ON_NOTHING_PHRASES = frozenset(
    {"nothing", "nothing yet", "none", "none yet", "nothing so far", "not yet"}
)

# Observation kinds. These describe what an observation asks of a reader; they
# are deliberately not a severity scale, because a check reports state rather
# than passing or failing a project.
BROKEN = "broken"
UNFINISHED = "unfinished"
NOTED = "noted"


class HealthError(RuntimeError):
    """A target or resource cannot be inspected safely and deterministically."""


@dataclass(frozen=True, slots=True)
class Finding:
    """One deterministic structural observation."""

    check_id: str
    severity: str
    category: str
    path: str
    line: int | None
    message: str
    evidence: str
    owner_doc: str
    next_action: str


@dataclass(frozen=True, slots=True)
class ContextAdoption:
    """The mechanically observable state of project-context activation."""

    status: str
    practice_core: str
    agent_route: str
    project_route: str
    instruction_compatibility: str
    boundary: str


@dataclass(frozen=True, slots=True)
class SkillTuning:
    """Whether one skill's description carries this project's own phrasings."""

    path: str
    state: str


@dataclass(frozen=True, slots=True)
class StarterPrompts:
    """How many shipped prompts in one starter file are still unanswered."""

    path: str
    unanswered: int


@dataclass(frozen=True, slots=True)
class RepeatedPassage:
    """One passage of prose found in two places, with where the other copy is."""

    path: str
    other: str
    words: int
    passage: str
    further: int
    kind: str


@dataclass(frozen=True, slots=True)
class ManagedDifference:
    """One region that tracks the packaged version and no longer matches it."""

    path: str
    region: str
    state: str
    diff: str


@dataclass(frozen=True, slots=True)
class HealthResult:
    """The immutable result of checking one project or resource view."""

    target: Path | str
    resource_bundle_sha256: str
    findings: tuple[Finding, ...]
    context_adoption: ContextAdoption
    skill_tuning: tuple[SkillTuning, ...] = ()
    repeated_passages: tuple[RepeatedPassage, ...] = ()
    practice_localization: str = "not_inspected"
    starter_prompts: tuple[StarterPrompts, ...] = ()
    relied_on: str = "not_inspected"

    @property
    def counts(self) -> dict[str, int]:
        """Return how many observations of each kind were made."""

        return {
            kind: sum(finding.severity == kind for finding in self.findings)
            for kind in (BROKEN, UNFINISHED, NOTED)
        }


def _validated_catalog(catalog: ResourceCatalog) -> ResourceCatalog:
    if not isinstance(catalog, ResourceCatalog):
        raise HealthError("Health checks require a validated ResourceCatalog.")
    try:
        # Reconstructing is inexpensive and reasserts the exact inventory,
        # entry digests, and bundle digest at the library boundary.
        return ResourceCatalog(
            template_entries=catalog.template_entries,
            bundle_sha256=catalog.bundle_sha256,
        )
    except (TypeError, ValueError) as exc:
        raise HealthError(f"Resource catalog is invalid: {exc}") from exc


def _link_kind(path: Path) -> str | None:
    try:
        if path.is_symlink():
            return "symlink"
        is_junction = getattr(path, "is_junction", None)
        if callable(is_junction) and is_junction():
            return "junction"
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except (FileNotFoundError, NotADirectoryError):
        return None
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    return "reparse point" if attributes & reparse_flag else None


def _first_link_ancestor(path: Path) -> tuple[Path, str] | None:
    current = path
    while True:
        link_kind = _link_kind(current)
        if link_kind is not None:
            return current, link_kind
        if current.parent == current:
            return None
        current = current.parent


def _canonical_project_target(target: str | os.PathLike[str]) -> Path:
    try:
        root = Path(os.path.abspath(os.fspath(target)))
        linked_ancestor = _first_link_ancestor(root)
    except (OSError, TypeError, ValueError) as exc:
        raise HealthError(f"Cannot inspect project target: {target!r}: {exc}") from exc
    if linked_ancestor is not None:
        linked_path, link_kind = linked_ancestor
        raise HealthError(
            f"Project target path cannot contain a {link_kind}: {linked_path}"
        )
    try:
        if not root.exists():
            raise HealthError(f"Project target does not exist: {root}")
        if not root.is_dir():
            raise HealthError(f"Project target must be a directory: {root}")
    except OSError as exc:
        raise HealthError(f"Cannot inspect project target {root}: {exc}") from exc
    return root


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise HealthError(f"Cannot read project context file {path}: {exc}") from exc
    except OSError as exc:
        raise HealthError(f"Cannot read project context file {path}: {exc}") from exc


def first_line_matching(path: Path, pattern: re.Pattern[str]) -> int | None:
    try:
        if not path.exists():
            return None
    except OSError as exc:
        raise HealthError(f"Cannot inspect project context path {path}: {exc}") from exc
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        if pattern.search(line):
            return line_number
    return None


def parse_backtick_bullets(lines: Iterable[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        match = re.match(r"\s*-\s+`([^`]+)`", line)
        if match:
            paths.append(match.group(1))
    return paths


def is_safe_generated_owner_path(path_text: str) -> bool:
    if "\\" in path_text:
        return False
    path = PurePosixPath(path_text)
    return (
        not path.is_absolute()
        and path.as_posix() == path_text
        and len(path.parts) >= 2
        and path.parts[0] == ".context"
        and all(part not in {"", ".", ".."} for part in path.parts)
        and path.suffix.casefold() == ".md"
    )


def _entry_link_kind(entry: os.DirEntry[str], entry_stat: os.stat_result) -> str | None:
    if entry.is_symlink() or stat.S_ISLNK(entry_stat.st_mode):
        return "symlink"
    attributes = getattr(entry_stat, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    return "reparse point" if attributes & reparse_flag else None


def _sorted_entries(directory: Path) -> tuple[os.DirEntry[str], ...]:
    try:
        entries = tuple(os.scandir(directory))
    except OSError as exc:
        raise HealthError(f"Cannot inspect directory {directory}: {exc}") from exc
    return tuple(sorted(entries, key=lambda entry: (entry.name.casefold(), entry.name)))


def _walk_plain_files(
    root: Path,
    *,
    skip_directory_names: frozenset[str] = frozenset(),
) -> Iterator[Path]:
    """Yield regular files in deterministic order without following links."""

    for entry in _sorted_entries(root):
        try:
            entry_stat = entry.stat(follow_symlinks=False)
        except OSError as exc:
            raise HealthError(f"Cannot inspect project path {entry.path}: {exc}") from exc
        if _entry_link_kind(entry, entry_stat) is not None:
            continue
        path = Path(entry.path)
        if stat.S_ISDIR(entry_stat.st_mode):
            if entry.name in skip_directory_names:
                continue
            yield from _walk_plain_files(
                path,
                skip_directory_names=skip_directory_names,
            )
        elif stat.S_ISREG(entry_stat.st_mode):
            yield path


def check_owned_tree_safety(root: Path, findings: list[Finding]) -> None:
    """Reject links and ambiguous entries before recursively reading managed trees."""

    unsafe: list[str] = []
    for relative_root in (Path(".context"),):
        tree_root = root / relative_root
        try:
            root_link = _link_kind(tree_root)
            root_exists = tree_root.exists()
        except OSError as exc:
            unsafe.append(
                f"{relative_root.as_posix()} (cannot inspect: {type(exc).__name__})"
            )
            continue
        if root_link is not None:
            unsafe.append(f"{relative_root.as_posix()} ({root_link})")
            continue
        if not root_exists:
            continue
        if not tree_root.is_dir():
            unsafe.append(f"{relative_root.as_posix()} (not a directory)")
            continue

        pending = [tree_root]
        while pending:
            directory = pending.pop()
            try:
                entries = _sorted_entries(directory)
            except HealthError as exc:
                unsafe.append(
                    f"{rel(directory, root)} (cannot inspect: {type(exc.__cause__).__name__})"
                )
                continue
            child_directories: list[Path] = []
            for entry in entries:
                path = Path(entry.path)
                try:
                    entry_stat = entry.stat(follow_symlinks=False)
                except OSError as exc:
                    unsafe.append(
                        f"{rel(path, root)} (cannot inspect: {type(exc).__name__})"
                    )
                    continue
                link_kind = _entry_link_kind(entry, entry_stat)
                if link_kind is not None:
                    unsafe.append(f"{rel(path, root)} ({link_kind})")
                elif stat.S_ISDIR(entry_stat.st_mode):
                    child_directories.append(path)
                elif not stat.S_ISREG(entry_stat.st_mode):
                    unsafe.append(f"{rel(path, root)} (not a regular file or directory)")
            pending.extend(reversed(child_directories))

    if unsafe:
        unsafe.sort(key=lambda value: (value.casefold(), value))
        findings.append(
            Finding(
                "DH-ROUTE-003",
                BROKEN,
                "structure",
                unsafe[0].split(" (", 1)[0],
                None,
                "Context and instruction folders must contain ordinary files, not links or unreadable entries.",
                "; ".join(unsafe),
                ".context/README.md",
                "Replace linked or unreadable entries with ordinary files.",
            )
        )


def parse_generated_context_index(
    context_index: Path,
    findings: list[Finding],
) -> list[str]:
    lines = read_text(context_index).splitlines()
    begin_indexes = [i for i, line in enumerate(lines) if line == CONTEXT_INVENTORY_BEGIN]
    end_indexes = [i for i, line in enumerate(lines) if line == CONTEXT_INVENTORY_END]

    if not begin_indexes and not end_indexes:
        findings.append(
            Finding(
                "DH-ROUTE-001",
                UNFINISHED,
                "routing",
                ".context/README.md",
                None,
                "Context index is human-authored; no generated inventory markers were found.",
                "begin markers: 0; end markers: 0; inventory consistency was not checked",
                ".context/README.md",
                "Keep writing the index by hand, or add one marker pair so `spctx sync-index` can maintain the inventory.",
            )
        )
        return []

    if len(begin_indexes) != 1 or len(end_indexes) != 1 or begin_indexes[0] >= end_indexes[0]:
        findings.append(
            Finding(
                "DH-ROUTE-001",
                BROKEN,
                "routing",
                ".context/README.md",
                None,
                "Context index does not contain one valid generated inventory marker pair.",
                f"begin markers: {len(begin_indexes)}; end markers: {len(end_indexes)}",
                ".context/README.md",
                "Restore exactly one ordered generated context-inventory marker pair, then resynchronize the index.",
            )
        )
        return []

    begin = begin_indexes[0]
    end = end_indexes[0]
    region = lines[begin + 1 : end]
    paths: list[str] = []
    canonical = True
    index = 0
    if region == [CONTEXT_EMPTY_INVENTORY_LINE]:
        index = len(region)
    while index < len(region):
        match = re.fullmatch(r"- `([^`]+)`", region[index])
        if match is None:
            canonical = False
            break
        paths.append(match.group(1))
        index += 1
        if index < len(region) and region[index].startswith("  - "):
            expected_labels = ("Purpose", "Read when", "Update when")
            for label in expected_labels:
                if index >= len(region):
                    canonical = False
                    break
                summary = re.fullmatch(rf"  - {re.escape(label)}: (.+)", region[index])
                if summary is None:
                    canonical = False
                    break
                index += 1
            if not canonical:
                break
    if not canonical or index != len(region):
        findings.append(
            Finding(
                "DH-ROUTE-001",
                BROKEN,
                "routing",
                ".context/README.md",
                begin + 2,
                "Generated context inventory contains non-canonical content.",
                "inventory entries must list either all three routing summaries or none",
                ".context/README.md",
                "Run `spctx sync-index`; your own prose outside the markers is left alone.",
            )
        )
        return []
    unsafe_paths = [path for path in paths if not is_safe_generated_owner_path(path)]
    if unsafe_paths:
        findings.append(
            Finding(
                "DH-ROUTE-001",
                BROKEN,
                "routing",
                ".context/README.md",
                begin + 2,
                "Generated context inventory contains an unsafe or non-canonical path.",
                ", ".join(unsafe_paths),
                ".context/README.md",
                "Remove escaping, absolute, non-Markdown, or non-canonical paths, then resync.",
            )
        )
        return []
    return paths


def parse_context_index(root: Path, findings: list[Finding]) -> list[str]:
    design_root = root / ".context"
    design_link = _link_kind(design_root)
    if design_link is not None:
        findings.append(
            Finding(
                "DH-ROUTE-003",
                BROKEN,
                "routing",
                ".context",
                None,
                "The `.context` directory must be an ordinary directory, not a link.",
                f"context directory is a {design_link}",
                ".context/project.md",
                "Replace the link with an ordinary directory before rerunning the check.",
            )
        )
        return []

    context_index = root / ".context/README.md"
    context_index_link = _link_kind(context_index)
    if context_index_link is not None:
        findings.append(
            Finding(
                "DH-ROUTE-003",
                BROKEN,
                "routing",
                ".context/README.md",
                None,
                "The context index must be an ordinary file, not a link.",
                f"context-index path is a {context_index_link}",
                ".context/project.md",
                "Replace the link with a reviewed regular-file context index before synchronization.",
            )
        )
        return []
    if context_index.exists() and not context_index.is_file():
        findings.append(
            Finding(
                "DH-ROUTE-003",
                BROKEN,
                "routing",
                ".context/README.md",
                None,
                "The context index must be a regular file.",
                "context-index path is not a regular file",
                ".context/project.md",
                "Replace the structural conflict with a reviewed regular-file context index.",
            )
        )
        return []
    if not context_index.exists():
        return []
    return parse_generated_context_index(context_index, findings)


def check_required(root: Path, findings: list[Finding]) -> None:
    for required in STARTER_INVENTORY:
        path = root / required
        current = root
        obstruction: str | None = None
        for part in PurePosixPath(required).parts[:-1]:
            current = current / part
            link_kind = _link_kind(current)
            if link_kind is not None:
                obstruction = f"parent path is a {link_kind}: {rel(current, root)}"
                break
            if current.exists() and not current.is_dir():
                obstruction = f"parent path is not a directory: {rel(current, root)}"
                break
        if obstruction is not None:
            findings.append(
                Finding(
                    "DH-REQ-001",
                    BROKEN,
                    "structure",
                    required,
                    None,
                    "Required template path has an unsafe or conflicting parent.",
                    obstruction,
                    required,
                    "Replace the conflicting parent path with an ordinary directory.",
                )
            )
            continue
        link_kind = _link_kind(path)
        if link_kind is not None or (path.exists() and not path.is_file()):
            findings.append(
                Finding(
                    "DH-REQ-001",
                    BROKEN,
                    "structure",
                    required,
                    None,
                    "Required template path is not a plain regular file.",
                    "required path is linked or structurally conflicting",
                    required,
                    "Replace it with an ordinary file.",
                )
            )
        elif not path.exists():
            findings.append(
                Finding(
                    "DH-REQ-001",
                    BROKEN,
                    "structure",
                    required,
                    None,
                    "Required template file is missing.",
                    "file not found",
                    required,
                    "Restore the missing file from the template.",
                )
            )


def check_agent_skills(
    catalog: ResourceCatalog,
    root: Path,
    findings: list[Finding],
) -> None:
    """Check only the managed skills, leaving unrelated project skills alone."""

    for skill_name in AGENT_SKILLS:
        relative_path = agent_skill_path(skill_name)
        path = root / relative_path
        if not path.is_file():
            continue
        try:
            content = path.read_bytes()
            validate_agent_skill_content(
                content,
                expected_name=skill_name,
            )
        except (OSError, OperationError) as exc:
            findings.append(
                Finding(
                    "DH-SKILL-001",
                    BROKEN,
                    "agent-skill",
                    relative_path,
                    None,
                    "Required Agent Skill is not structurally valid.",
                    str(exc),
                    relative_path,
                    "Restore valid name and description YAML frontmatter plus a non-empty procedure body.",
                )
            )
            continue
        check_agent_skill_drift(catalog, relative_path, content, findings)


def check_agent_skill_drift(
    catalog: ResourceCatalog,
    relative_path: str,
    content: bytes,
    findings: list[Finding],
) -> None:
    """Report how far a skill has moved from the packaged one, without judging it.

    Adding this project's own trigger phrasings after the separator is the
    intended outcome and is reported as tuning, not as divergence. Only a
    replaced description or a rewritten body is reported here, and only so the
    project knows packaged updates will no longer reach that part.
    """

    try:
        comparison = compare_agent_skill(content, _catalog_content(catalog, relative_path))
    except (KeyError, OperationError):
        return

    if comparison.description not in {"packaged", "extended"}:
        findings.append(
            Finding(
                "DH-SKILL-002",
                NOTED,
                "agent-skill",
                relative_path,
                None,
                "Agent Skill description no longer starts with the packaged text, so packaged trigger updates cannot reach this project.",
                f"description: {comparison.description}",
                relative_path,
                f'Restore the packaged description and add this project\'s example phrasings after "{SKILL_TRIGGER_SEPARATOR}", which keeps both.',
            )
        )

    if comparison.body == "modified":
        findings.append(
            Finding(
                "DH-SKILL-003",
                NOTED,
                "agent-skill",
                relative_path,
                None,
                "Agent Skill body differs from the packaged procedure, so package updates will not reach it.",
                "body: modified",
                relative_path,
                "Restore the packaged body and keep project facts in the instruction file or `.context/`, or accept that this project now maintains this procedure itself.",
            )
        )


def _catalog_content(catalog: ResourceCatalog, relative_path: str) -> bytes:
    return catalog.get(f"template/{relative_path}").content

def check_claude_skill_pointers(root: Path, findings: list[Finding]) -> None:
    """Check pointer skills only where this project already has them."""

    for skill_name in AGENT_SKILLS:
        relative_path = claude_skill_path(skill_name)
        canonical_relative = agent_skill_path(skill_name)
        path = root / relative_path
        canonical = root / canonical_relative
        try:
            if _link_kind(path) is not None or not path.is_file():
                continue
            content = path.read_bytes()
            validate_agent_skill_content(content, expected_name=skill_name)
        except (OSError, OperationError) as exc:
            findings.append(
                Finding(
                    "DH-SKILL-004",
                    UNFINISHED,
                    "agent-skill",
                    relative_path,
                    None,
                    "Claude pointer skill is not structurally valid, so Claude Code cannot load it.",
                    str(exc),
                    relative_path,
                    "Restore valid name and description YAML frontmatter plus a body that routes to "
                    f"`{canonical_relative}`, or remove the file.",
                )
            )
            continue

        try:
            if _link_kind(canonical) is not None or not canonical.is_file():
                continue
            pointer_parts = parse_agent_skill_content(content)
            canonical_parts = parse_agent_skill_content(canonical.read_bytes())
        except (OSError, OperationError):
            continue

        differences = []
        if pointer_parts.description != canonical_parts.description:
            differences.append("description")
        if canonical_relative not in pointer_parts.body:
            differences.append("route")
        if differences:
            findings.append(
                Finding(
                    "DH-SKILL-004",
                    UNFINISHED,
                    "agent-skill",
                    relative_path,
                    None,
                    "Claude pointer skill no longer matches the skill it stands in for, so Claude "
                    "Code and the other agents can route differently.",
                    ", ".join(differences),
                    relative_path,
                    f"Copy the description from `{canonical_relative}` into this file and keep its "
                    "body pointing there, or remove the file if this project no longer uses Claude Code.",
                )
            )


def inspect_context_adoption(
    catalog: ResourceCatalog,
    root: Path,
) -> ContextAdoption:
    """Inspect routing and core integrity without judging instruction meaning."""

    practice = root / SCIENTIFIC_PRACTICE_PATH
    agents = root / "AGENTS.md"
    project = root / ".context/project.md"

    practice_state = "missing"
    if practice.is_file():
        practice_state = managed_block_state(
            read_text(practice),
            _catalog_content(catalog, SCIENTIFIC_PRACTICE_PATH),
            SCIENTIFIC_PRACTICE_BEGIN,
            SCIENTIFIC_PRACTICE_END,
        )

    agent_state = "missing"
    if agents.is_file():
        agent_state = managed_block_state(
            read_text(agents),
            CONTEXT_ROUTE_BLOCK,
            CONTEXT_ROUTE_BEGIN,
            CONTEXT_ROUTE_END,
        )

    project_state = "missing"
    if project.is_file():
        project_state = (
            "present"
            if SCIENTIFIC_PRACTICE_PATH in read_text(project)
            else "absent"
        )

    if practice_state != "exact":
        status = "scientific_contract_review_required"
    elif agent_state != "exact":
        status = "manual_activation_required"
    elif project_state != "present":
        status = "project_route_required"
    else:
        status = "routed"

    compatibility = "not_machine_checked"
    if agents.is_file() and agents.read_bytes() == _catalog_content(catalog, "AGENTS.md"):
        compatibility = "packaged_baseline"

    return ContextAdoption(
        status=status,
        practice_core=practice_state,
        agent_route=agent_state,
        project_route=project_state,
        instruction_compatibility=compatibility,
        boundary=(
            "project-context routing, Agent Skill structure, and versioned-core integrity only; natural-language "
            "instruction compatibility requires project review and scientific validity "
            "requires relevant scientific or domain review"
        ),
    )


def _uninspected_context_adoption() -> ContextAdoption:
    return ContextAdoption(
        status="blocked",
        practice_core="not_inspected_due_to_structure",
        agent_route="not_inspected_due_to_structure",
        project_route="not_inspected_due_to_structure",
        instruction_compatibility="not_machine_checked",
        boundary=(
            "project-context routing, Agent Skill structure, and versioned-core integrity only; natural-language "
            "instruction compatibility requires project review and scientific validity "
            "requires relevant scientific or domain review"
        ),
    )


def check_practice_core(
    root: Path,
    adoption: ContextAdoption,
    findings: list[Finding],
) -> None:
    """Report the state of the two things that make the system reachable.

    A retrofit only becomes active when someone adds the routing block by hand,
    and `init` asks for that once. Staying quiet afterwards meant a project
    could hold every file, route nothing, and still be told it was fine.
    """

    if adoption.practice_core == "modified":
        findings.append(
            Finding(
                "DH-PRACTICE-001",
                BROKEN,
                "scientific-practice",
                SCIENTIFIC_PRACTICE_PATH,
                None,
                "The scientific-practice core differs from the installed package, either because the package was updated or because the marked section was edited here.",
                f"managed core state: {adoption.practice_core}",
                SCIENTIFIC_PRACTICE_PATH,
                "Replace the marked section with the packaged core that `spctx init . --dry-run` prints; move any wording this project wants to keep below the markers first.",
            )
        )
    elif adoption.practice_core != "exact":
        findings.append(
            Finding(
                "DH-PRACTICE-001",
                BROKEN,
                "scientific-practice",
                SCIENTIFIC_PRACTICE_PATH,
                None,
                "The versioned scientific-practice core is missing or malformed.",
                f"managed core state: {adoption.practice_core}",
                SCIENTIFIC_PRACTICE_PATH,
                "Restore one marked core from the text `spctx init . --dry-run` prints; keep your own additions outside the markers.",
            )
        )

    if adoption.agent_route in {"modified", "invalid"}:
        findings.append(
            Finding(
                "DH-ROUTE-004",
                UNFINISHED,
                "routing",
                "AGENTS.md",
                None,
                "The routing block is present but no longer matches the installed package, so some of what it points to may be wrong.",
                f"managed route state: {adoption.agent_route}",
                "AGENTS.md",
                "Replace the marked block with the current packaged routing block; your own text outside the markers is untouched.",
            )
        )
    elif adoption.agent_route in {"absent", "missing"}:
        findings.append(
            Finding(
                "DH-ROUTE-005",
                UNFINISHED,
                "routing",
                "AGENTS.md",
                None,
                "No instruction file routes agents to this project's context, so the files here will only be read when someone names them.",
                f"managed route state: {adoption.agent_route}",
                "AGENTS.md",
                "Run `spctx init .` to see the routing block, then add it to the instruction file your agents actually read.",
            )
        )


def check_context_index_pressure(
    root: Path,
    findings: list[Finding],
    inventory: Sequence[str] | None = None,
) -> None:
    discovery = discover_specialized_owners(root)
    if discovery.conflicts:
        findings.append(
            Finding(
                "DH-ROUTE-003",
                BROKEN,
                "routing",
                ".context",
                None,
                "Focused-context discovery is unsafe or structurally ambiguous.",
                "; ".join(discovery.conflicts),
                ".context/project.md",
                "Replace links or name collisions with ordinary directories and files.",
            )
        )
        return

    context_index = root / ".context/README.md"
    if not context_index.exists():
        if len(discovery.owners) < 2:
            return
        findings.append(
            Finding(
                "DH-ROUTE-002",
                UNFINISHED,
                "routing",
                ".context/README.md",
                None,
                "Several context documents exist, but nothing indexes them.",
                f"{len(discovery.owners)} focused documents: {', '.join(discovery.owners)}",
                ".context/README.md",
                "Run `spctx sync-index` to create the index and list these documents.",
            )
        )
        return

    if inventory is None:
        parse_findings: list[Finding] = []
        parsed = parse_generated_context_index(context_index, parse_findings)
        findings.extend(parse_findings)
        if parse_findings:
            return
        inventory = parsed
    elif any(
        finding.check_id in {"DH-ROUTE-001", "DH-ROUTE-003"}
        and finding.path == ".context/README.md"
        for finding in findings
    ):
        return

    actual = tuple(inventory)
    expected = discovery.owners
    summaries_match = False
    if actual == expected:
        guidance = tuple(
            extract_context_guidance(read_text(root / path), path) for path in expected
        )
        try:
            original = context_index.read_bytes()
            summaries_match = (
                rewrite_context_inventory(original, expected, guidance) == original
            )
        except (OSError, OperationError, UnicodeError, ValueError):
            summaries_match = False
        if summaries_match:
            return
    actual_set = set(actual)
    expected_set = set(expected)
    duplicates = sorted({path for path in actual if actual.count(path) > 1})
    missing = [path for path in expected if path not in actual_set]
    extra = [path for path in actual if path not in expected_set]
    details: list[str] = []
    if missing:
        details.append("missing: " + ", ".join(missing))
    if extra:
        details.append("extra: " + ", ".join(extra))
    if duplicates:
        details.append("duplicates: " + ", ".join(duplicates))
    if not missing and not extra and not duplicates:
        if actual != expected:
            details.append("context paths are not in deterministic order")
        else:
            details.append("routing summaries are missing, incomplete, or stale")
    findings.append(
        Finding(
            "DH-ROUTE-002",
            UNFINISHED,
            "routing",
            ".context/README.md",
            None,
            "Generated context inventory does not exactly match discoverable focused documents.",
            "; ".join(details),
            ".context/README.md",
            "Run `spctx sync-index`; your own routing notes are left alone.",
        )
    )


def check_context_guidance(root: Path, findings: list[Finding]) -> None:
    """Warn when a context document is missing its short routing lines."""

    discovery = discover_specialized_owners(root)
    if discovery.conflicts:
        return
    paths = [".context/project.md", *discovery.owners]
    if (root / ".context/README.md").is_file():
        paths.insert(1, ".context/README.md")

    for path_text in paths:
        path = root / path_text
        if not path.is_file():
            continue
        guidance = extract_context_guidance(read_text(path), path_text)
        missing = [
            label
            for label, value in zip(
                CONTEXT_GUIDANCE_LABELS,
                (guidance.purpose, guidance.read_when, guidance.update_when),
            )
            if value is None
        ]
        if not missing:
            continue
        findings.append(
            Finding(
                "DH-GUIDE-001",
                UNFINISHED,
                "routing",
                path_text,
                None,
                "Context document is missing its short routing lines.",
                "missing near the start: " + ", ".join(missing),
                path_text,
                (
                    "Add short Purpose, Read when, and Update when lines near the start "
                    "so readers can tell what this document is for."
                ),
            )
        )


def check_draft_owners(root: Path, findings: list[Finding]) -> None:
    design_root = root / ".context"
    if not design_root.exists() or not design_root.is_dir():
        return
    for path in _walk_plain_files(
        design_root,
        skip_directory_names=frozenset({"archived", "examples", "reference"}),
    ):
        if path.suffix.casefold() != ".md":
            continue
        path_text = rel(path, root)
        line = first_line_matching(path, DRAFT_CONTEXT_MARKER_RE)
        if line is not None:
            findings.append(
                Finding(
                    "DH-REVIEW-001", UNFINISHED, "review", path_text, line,
                    "Current context document is still marked as a generated draft requiring review.",
                    DRAFT_CONTEXT_MARKER, path_text,
                    "Review supported facts and consequential judgments, then remove the marker when the document is authoritative.",
                )
            )


def check_stale_references(root: Path, findings: list[Finding]) -> None:
    """Report context that points at a repository path which is no longer there.

    This is the one drift signal a read-only structural tool can see. It is
    deliberately narrow: only backticked strings shaped like a repository-relative
    file path are considered, so ratios, globs, URLs, and prose survive untouched.
    A path is only missing if the directory it sits under exists, because a
    reference into a tree the project does not have is describing a possibility
    rather than pointing at something.
    """

    design_root = root / ".context"
    if not design_root.is_dir():
        return
    reported = 0
    for path in _walk_plain_files(
        design_root,
        skip_directory_names=frozenset({"archived", "examples", "reference"}),
    ):
        if path.suffix.casefold() != ".md":
            continue
        # The index routes to documents that may not exist yet, and its generated
        # half is maintained by sync-index and checked by the routing checks.
        if rel(path, root) == ".context/README.md":
            continue
        try:
            text = FENCED_CODE_RE.sub("", read_text(path))
        except OSError:
            continue
        seen: set[str] = set()
        for number, line in enumerate(text.splitlines(), start=1):
            for span in INLINE_CODE_RE.findall(line):
                candidate = span.strip("`")
                if candidate in seen or not STALE_REFERENCE_RE.fullmatch(candidate):
                    continue
                if ".." in candidate or (root / candidate).exists():
                    continue
                if not (root / PurePosixPath(candidate).parts[0]).is_dir():
                    continue
                seen.add(candidate)
                if reported >= STALE_REFERENCE_MAX_FINDINGS:
                    return
                reported += 1
                findings.append(
                    Finding(
                        "DH-STALE-001",
                        UNFINISHED,
                        "routing",
                        rel(path, root),
                        number,
                        "Context names a repository path that is not there.",
                        candidate,
                        rel(path, root),
                        (
                            "Correct the path, drop the reference, or describe the file as one "
                            "the work produces rather than one the repository holds."
                        ),
                    )
                )


def _project_findings(
    catalog: ResourceCatalog,
    root: Path,
    adoption: ContextAdoption,
) -> tuple[tuple[Finding, ...], tuple[RepeatedPassage, ...]]:
    findings: list[Finding] = []
    check_practice_core(root, adoption, findings)
    check_agent_skills(catalog, root, findings)
    check_claude_skill_pointers(root, findings)
    active = parse_context_index(root, findings)
    check_context_index_pressure(root, findings, active)
    discovery = discover_specialized_owners(root)
    if discovery.conflicts or tuple(active) != discovery.owners:
        active = []
    if any(finding.check_id == "DH-ROUTE-003" for finding in findings):
        return tuple(findings), ()
    check_context_guidance(root, findings)
    check_draft_owners(root, findings)
    check_stale_references(root, findings)
    repeated = check_duplicated_rules(catalog, root, findings)
    return tuple(findings), repeated


def check_project(
    catalog: ResourceCatalog,
    target: str | os.PathLike[str],
) -> HealthResult:
    """Check an initialized project without changing or following links in it."""

    validated_catalog = _validated_catalog(catalog)
    root = _canonical_project_target(target)
    structural_findings: list[Finding] = []
    check_owned_tree_safety(root, structural_findings)
    if not structural_findings:
        check_required(root, structural_findings)
    if structural_findings:
        return HealthResult(
            target=root,
            resource_bundle_sha256=validated_catalog.bundle_sha256,
            findings=tuple(structural_findings),
            context_adoption=_uninspected_context_adoption(),
        )
    adoption = inspect_context_adoption(validated_catalog, root)
    findings, repeated = _project_findings(validated_catalog, root, adoption)
    return HealthResult(
        target=root,
        resource_bundle_sha256=validated_catalog.bundle_sha256,
        findings=findings,
        context_adoption=adoption,
        skill_tuning=inspect_skill_tuning(validated_catalog, root),
        repeated_passages=repeated,
        practice_localization=inspect_practice_localization(validated_catalog, root),
        starter_prompts=inspect_starter_prompts(root),
        relied_on=inspect_relied_on(root),
    )


def inspect_practice_localization(catalog: ResourceCatalog, root: Path) -> str:
    """Observe whether the project has written its own practice notes.

    Diffing against the packaged file was tried first and misread a project
    running an older version as localized. This looks for project content
    instead: a section the package does not ship, or the packaged prompts
    answered. Saying in one line that the shared core is enough counts, because
    deciding that is as much an answer as writing a field's conventions down.
    """

    path = root / SCIENTIFIC_PRACTICE_PATH
    if not path.is_file():
        return "absent"
    try:
        installed = _outside_practice_core(read_text(path))
        packaged = _outside_practice_core(
            _catalog_content(catalog, SCIENTIFIC_PRACTICE_PATH).decode("utf-8")
        )
    except (OSError, KeyError, UnicodeDecodeError):
        return "not_inspected"

    sections = _practice_sections(installed)
    if set(sections) - set(_practice_sections(packaged)):
        return "present"
    answered = sections.get(PRACTICE_PROJECT_SECTION, "")
    if answered.strip() and not BRACKETED_PROMPT_RE.search(answered):
        return "present"
    return "none"


def inspect_relied_on(root: Path) -> str:
    """Observe whether the compact context names anything later work relies on.

    This one field decides how much evidence a change owes. Nothing here counts
    individual results: the default is that a project is exploratory, and the
    field exists so a project can name the exceptions. Reporting the state is
    what gives promotion a moment; deciding to promote stays with the user.
    """

    path = root / PROJECT_CONTEXT_PATH
    if not path.is_file():
        return "absent"
    try:
        text = FENCED_CODE_RE.sub(" ", read_text(path))
    except OSError:
        return "not_inspected"

    marker = f"**{RELIED_ON_FIELD}**"
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(marker):
            continue
        value = stripped[len(marker) :].lstrip(": ").strip()
        if not value or BRACKETED_PROMPT_RE.fullmatch(value):
            return "unanswered"
        plain = INLINE_CODE_RE.sub(
            lambda match: match.group(0).strip("`"), value
        ).strip(" .;`")
        if plain.casefold() in RELIED_ON_NOTHING_PHRASES:
            return "nothing_named"
        return "named"
    return "absent"


def inspect_starter_prompts(root: Path) -> tuple[StarterPrompts, ...]:
    """Count shipped prompts a project has not yet replaced with its own answers.

    The starter says plainly that a prompt left in place is not an answer, so a
    count here is the cheapest signal that setup is unfinished. It says nothing
    about whether the answers already written are any good.
    """

    counts: list[StarterPrompts] = []
    for relative_path in PROMPTED_STARTER_PATHS:
        path = root / relative_path
        if not path.is_file():
            continue
        try:
            text = FENCED_CODE_RE.sub(" ", read_text(path))
        except OSError:
            continue
        counts.append(
            StarterPrompts(
                path=relative_path,
                unanswered=len(BRACKETED_PROMPT_RE.findall(text)),
            )
        )
    return tuple(counts)


def _outside_practice_core(text: str) -> str:
    core = re.escape(SCIENTIFIC_PRACTICE_BEGIN) + ".*?" + re.escape(SCIENTIFIC_PRACTICE_END)
    return re.sub(core, "", text, flags=re.DOTALL)


def _practice_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    heading: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if heading is not None:
                sections[heading] = "\n".join(body)
            heading = line[3:].strip()
            body = []
        elif heading is not None:
            body.append(line)
    if heading is not None:
        sections[heading] = "\n".join(body)
    return sections


def inspect_skill_tuning(
    catalog: ResourceCatalog,
    root: Path,
) -> tuple[SkillTuning, ...]:
    """Observe which skills carry project phrasings, without judging their wording."""

    tuning: list[SkillTuning] = []
    for skill_name in AGENT_SKILLS:
        relative_path = agent_skill_path(skill_name)
        path = root / relative_path
        if not path.is_file():
            continue
        try:
            comparison = compare_agent_skill(
                path.read_bytes(),
                _catalog_content(catalog, relative_path),
            )
        except (OSError, KeyError, OperationError):
            continue
        state = {"packaged": "untuned", "extended": "tuned"}.get(
            comparison.description, "diverged"
        )
        tuning.append(SkillTuning(path=relative_path, state=state))
    return tuple(tuning)


def _region_diff(packaged: str, installed: str, label: str) -> str:
    return "".join(
        unified_diff(
            f"{packaged}\n".splitlines(keepends=True),
            f"{installed}\n".splitlines(keepends=True),
            fromfile=f"packaged/{label}",
            tofile=f"project/{label}",
        )
    )


def diff_managed_regions(
    catalog: ResourceCatalog,
    target: str | os.PathLike[str],
) -> tuple[ManagedDifference, ...]:
    """Show how regions that track the packaged version differ in one project."""

    validated_catalog = _validated_catalog(catalog)
    root = _canonical_project_target(target)
    differences: list[ManagedDifference] = []

    agents = root / "AGENTS.md"
    if agents.is_file():
        state, block = extract_managed_block(
            read_text(agents), CONTEXT_ROUTE_BEGIN, CONTEXT_ROUTE_END
        )
        if state == "present" and block is not None and block != CONTEXT_ROUTE_BLOCK:
            differences.append(
                ManagedDifference(
                    path="AGENTS.md",
                    region="routing block",
                    state="diverged",
                    diff=_region_diff(CONTEXT_ROUTE_BLOCK, block, "AGENTS.md:routing"),
                )
            )

    for skill_name in AGENT_SKILLS:
        relative_path = agent_skill_path(skill_name)
        path = root / relative_path
        if not path.is_file():
            continue
        try:
            content = path.read_bytes()
            packaged_content = _catalog_content(validated_catalog, relative_path)
            installed = parse_agent_skill_content(content)
            packaged = parse_agent_skill_content(packaged_content)
            comparison = compare_agent_skill(content, packaged_content)
        except (OSError, KeyError, OperationError):
            continue

        for region, state, packaged_text, installed_text in (
            ("description", comparison.description, packaged.description, installed.description),
            ("body", comparison.body, packaged.body, installed.body),
        ):
            if packaged_text == installed_text:
                continue
            differences.append(
                ManagedDifference(
                    path=relative_path,
                    region=region,
                    state=state,
                    diff=_region_diff(packaged_text, installed_text, f"{relative_path}:{region}"),
                )
            )

    return tuple(differences)


def _comparable_words(text: str) -> list[str]:
    """Reduce Markdown to comparable words, dropping regions that repeat by design."""

    for begin, end in (
        (CONTEXT_ROUTE_BEGIN, CONTEXT_ROUTE_END),
        (SCIENTIFIC_PRACTICE_BEGIN, SCIENTIFIC_PRACTICE_END),
        (CONTEXT_INVENTORY_BEGIN, CONTEXT_INVENTORY_END),
    ):
        text = re.sub(
            re.escape(begin) + ".*?" + re.escape(end), " ", text, flags=re.DOTALL
        )
    text = FENCED_CODE_RE.sub(" ", text)
    text = MARKDOWN_LINK_RE.sub(r"\1", text)
    text = INLINE_CODE_RE.sub(" ", text)
    return [
        word for word in DUPLICATE_WORD_RE.findall(text.lower()) if not word.isdigit()
    ]


def _shared_runs(left: list[str], right: list[str]) -> list[tuple[int, int]]:
    """Return (start in left, word count) for each maximal shared passage."""

    size = DUPLICATE_MIN_WORDS
    if len(left) < size or len(right) < size:
        return []

    right_index: dict[tuple[str, ...], list[int]] = {}
    for position in range(len(right) - size + 1):
        shingle = tuple(right[position : position + size])
        right_index.setdefault(shingle, []).append(position)

    matches: set[tuple[int, int]] = set()
    for position in range(len(left) - size + 1):
        for other in right_index.get(tuple(left[position : position + size]), ()):
            matches.add((position, other))

    runs: list[tuple[int, int]] = []
    for start, other in sorted(matches):
        if (start - 1, other - 1) in matches:
            continue
        extent = 0
        while (start + extent, other + extent) in matches:
            extent += 1
        runs.append((start, size + extent - 1))
    return runs


def _duplicate_regions(
    catalog: ResourceCatalog,
    root: Path,
) -> list[tuple[str, list[str], bool]]:
    """Collect comparable text as (label, words, is_packaged_reference).

    Only the packaged skills and the scientific-practice core are references: the
    packaged instruction and project files ship as drafts a project is meant to
    edit, so overlap with those is expected rather than duplication.
    """

    regions: list[tuple[str, list[str], bool]] = []

    agents = root / "AGENTS.md"
    if agents.is_file():
        regions.append(("AGENTS.md", _comparable_words(read_text(agents)), False))

    context_root = root / ".context"
    if context_root.is_dir():
        for path in _walk_plain_files(
            context_root,
            skip_directory_names=frozenset({"archived", "examples", "reference"}),
        ):
            if path.suffix.casefold() != ".md":
                continue
            regions.append((rel(path, root), _comparable_words(read_text(path)), False))

    for skill_name in AGENT_SKILLS:
        relative_path = agent_skill_path(skill_name)
        try:
            packaged = _catalog_content(catalog, relative_path).decode("utf-8")
        except (KeyError, UnicodeError):
            continue
        regions.append((f"the packaged {skill_name} skill", _comparable_words(packaged), True))

    try:
        practice = _catalog_content(catalog, SCIENTIFIC_PRACTICE_PATH).decode("utf-8")
    except (KeyError, UnicodeError):
        practice = ""
    core = practice.partition(SCIENTIFIC_PRACTICE_BEGIN)[2].partition(
        SCIENTIFIC_PRACTICE_END
    )[0]
    if core:
        regions.append(
            ("the shared scientific-practice core", _comparable_words(core), True)
        )

    return regions


def check_duplicated_rules(
    catalog: ResourceCatalog,
    root: Path,
    findings: list[Finding],
) -> tuple[RepeatedPassage, ...]:
    """Collect repeated passages, reporting only the unambiguous packaged echoes.

    Repeating packaged reference text is always a defect, because the package
    updates on its own schedule and the copy does not. Repetition among a
    project's own documents may be deliberate, so it is surfaced as maintenance
    pressure rather than as a list of defects to clear.
    """

    regions = _duplicate_regions(catalog, root)
    passages: list[RepeatedPassage] = []
    for first in range(len(regions)):
        left_label, left_words, left_packaged = regions[first]
        for second in range(first + 1, len(regions)):
            right_label, right_words, right_packaged = regions[second]
            if left_packaged and right_packaged:
                continue
            runs = _shared_runs(left_words, right_words)
            if not runs:
                continue
            start, length = max(runs, key=lambda run: run[1])
            passage = " ".join(left_words[start : start + length])
            if len(passage) > 110:
                passage = passage[:107].rstrip() + "..."
            owner = right_label if left_packaged else left_label
            other = left_label if left_packaged else right_label
            passages.append(
                RepeatedPassage(
                    path=owner,
                    other=other,
                    words=length,
                    passage=passage,
                    further=len(runs) - 1,
                    kind="packaged" if (left_packaged or right_packaged) else "project",
                )
            )

    passages.sort(key=lambda item: (-item.words, item.path, item.other))
    echoes = [item for item in passages if item.kind == "packaged"]
    for echo in echoes[:DUPLICATE_MAX_FINDINGS]:
        suffix = f"; {echo.further} further shared passages" if echo.further else ""
        findings.append(
            Finding(
                "DH-DUP-001",
                NOTED,
                "duplication",
                echo.path,
                None,
                f"A passage here repeats {echo.other}, which updates with the package while this copy does not.",
                f'{echo.words} words repeated: "{echo.passage}"{suffix}',
                echo.path,
                "Delete the copy and let the packaged text be the only statement, or keep it and accept that it will not change when the package does.",
            )
        )
    return tuple(passages)


def check_template_resources(catalog: ResourceCatalog) -> HealthResult:
    """Check the catalog's exact in-memory starter-resource view.

    ``ResourceCatalog`` already enforces exact membership, byte digests, and
    bundle identity.  This maintainer check adds the scaffold-specific health
    rules that can be evaluated without materializing a filesystem copy.
    """

    validated_catalog = _validated_catalog(catalog)
    findings: list[Finding] = []
    entries = validated_catalog.template_entries
    entry_paths = tuple(entry.relative_path for entry in entries)
    if entry_paths != TEMPLATE_INVENTORY:
        # Defensive only: ResourceCatalog validation normally rejects this first.
        findings.append(
            Finding(
                "DH-REQ-001", BROKEN, "structure", TEMPLATE_RESOURCE_TARGET, None,
                "Packaged starter resources do not have the exact required inventory.",
                f"expected {TEMPLATE_INVENTORY!r}; found {entry_paths!r}",
                "template/", "Restore the exact packaged starter resource inventory.",
            )
        )
    decoded: dict[str, str] = {}
    for entry in entries:
        try:
            decoded[entry.relative_path] = entry.content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HealthError(
                f"Packaged starter resource is not valid UTF-8: {entry.relative_path}"
            ) from exc
    practice = decoded.get(SCIENTIFIC_PRACTICE_PATH)
    practice_state = "missing"
    if practice is not None:
        practice_state = managed_block_state(
            practice,
            practice,
            SCIENTIFIC_PRACTICE_BEGIN,
            SCIENTIFIC_PRACTICE_END,
        )
    if practice_state != "exact":
        findings.append(
            Finding(
                "DH-PRACTICE-001", BROKEN, "scientific-practice",
                SCIENTIFIC_PRACTICE_PATH, None,
                "Packaged scientific-practice core is malformed.",
                "expected one versioned core marker pair", SCIENTIFIC_PRACTICE_PATH,
                "Restore one valid versioned scientific-practice core.",
            )
        )
    agents_text = decoded.get("AGENTS.md")
    agent_state = "missing"
    if agents_text is not None:
        agent_state = managed_block_state(
            agents_text,
            CONTEXT_ROUTE_BLOCK,
            CONTEXT_ROUTE_BEGIN,
            CONTEXT_ROUTE_END,
        )
    if agent_state != "exact":
        findings.append(
            Finding(
                "DH-ADOPT-001", BROKEN, "context-adoption", "AGENTS.md", None,
                "Packaged AGENTS.md lacks the exact project-context routing block.",
                "expected one exact versioned routing block", "AGENTS.md",
                "Restore the compact packaged project-context route.",
            )
        )
    project_text = decoded.get(".context/project.md", "")
    project_state = (
        "present" if SCIENTIFIC_PRACTICE_PATH in project_text else "absent"
    )
    if project_state != "present":
        findings.append(
            Finding(
                "DH-ADOPT-002", BROKEN, "context-adoption",
                ".context/project.md", None,
                "Packaged project context does not route to the scientific-practice contract.",
                "scientific-practice route not found", ".context/project.md",
                "Restore the compact packaged route to .context/scientific-practice.md.",
            )
        )
    for skill_name in AGENT_SKILLS:
        relative_path = agent_skill_path(skill_name)
        entry = next(
            (item for item in entries if item.relative_path == relative_path),
            None,
        )
        if entry is None:
            continue
        try:
            validate_agent_skill_content(
                entry.content,
                expected_name=skill_name,
            )
        except OperationError as exc:
            findings.append(
                Finding(
                    "DH-SKILL-001",
                    BROKEN,
                    "agent-skill",
                    relative_path,
                    None,
                    "Packaged Agent Skill is malformed.",
                    str(exc),
                    relative_path,
                    "Restore valid name and description YAML frontmatter plus a non-empty procedure body.",
                )
            )
    if practice_state != "exact":
        status = "scientific_contract_review_required"
    elif agent_state != "exact":
        status = "manual_activation_required"
    elif project_state != "present":
        status = "project_route_required"
    else:
        status = "routed"
    adoption = ContextAdoption(
        status=status,
        practice_core=practice_state,
        agent_route=agent_state,
        project_route=project_state,
        instruction_compatibility="packaged_baseline",
        boundary=(
            "project-context routing, Agent Skill structure, and versioned-core integrity only; natural-language "
            "instruction compatibility requires project review and scientific validity "
            "requires relevant scientific or domain review"
        ),
    )
    return HealthResult(
        target=TEMPLATE_RESOURCE_TARGET,
        resource_bundle_sha256=validated_catalog.bundle_sha256,
        findings=tuple(findings),
        context_adoption=adoption,
    )
