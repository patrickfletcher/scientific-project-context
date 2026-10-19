"""Bounded project-file operations built on immutable resource bytes."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Sequence

from .resources import (
    CONTEXT_INDEX_PATH,
    CONTEXT_INDEX_RESOURCE_ID,
    ResourceCatalog,
    ResourceEntry,
    STARTER_INVENTORY,
)


INITIALIZATION_MODES = ("new", "retrofit")
_FILE_DISPOSITIONS = ("create", "identical", "retain", "defer")
SCIENTIFIC_PRACTICE_PATH = ".context/scientific-practice.md"
PROJECT_CONTEXT_PATH = ".context/project.md"
SCIENTIFIC_PRACTICE_BEGIN = "<!-- BEGIN SPCTX SCIENTIFIC PRACTICE CORE v1 -->"
SCIENTIFIC_PRACTICE_END = "<!-- END SPCTX SCIENTIFIC PRACTICE CORE v1 -->"
CONTEXT_ROUTE_BEGIN = "<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->"
CONTEXT_ROUTE_END = "<!-- END SPCTX PROJECT CONTEXT ROUTING v1 -->"
CONTEXT_ROUTE_BLOCK = "\n".join(
    (
        CONTEXT_ROUTE_BEGIN,
        "Read `.context/project.md` at the start of work for the smallest current project context. If `.context/README.md` exists, use it to select only the additional source needed by the task.",
        "",
        "When work changes what the project currently knows, its current focus, a protected input, what later work relies on, or a context route, rewrite that part of the context in place before you finish. Run history, what stayed unchanged, and who approved what belong in Git and the conversation, not in context. Use `.agents/skills/spctx-project-context/SKILL.md` to initialize, refresh, separate, retire, or upgrade context.",
        "",
        "For work that could affect scientific meaning, protected inputs, methods, evidence, artifacts, validation, or claims, read `.context/scientific-practice.md` and use `.agents/skills/spctx-scientific-change/SKILL.md`.",
        "",
        "For text written for readers outside this work, such as a README, contributor guide, methods or results section, figure caption, status report, or manuscript, use `.agents/skills/spctx-public-writing/SKILL.md`.",
        "",
        "Keep project facts in `.context/project.md` or a document it links. If another instruction conflicts with the scientific safeguards, stop and ask the user or the responsible scientist to resolve it.",
        CONTEXT_ROUTE_END,
    )
)
CONTEXT_INVENTORY_BEGIN = "<!-- BEGIN GENERATED CONTEXT INVENTORY -->"
CONTEXT_INVENTORY_END = "<!-- END GENERATED CONTEXT INVENTORY -->"
CONTEXT_EMPTY_INVENTORY_LINE = "*No focused context documents currently exist.*"
DRAFT_CONTEXT_MARKER = "DRAFT CONTEXT - REVIEW REQUIRED"
# Instruction locations common enough that silently adding a second one would surprise.
KNOWN_INSTRUCTION_PATHS = (
    ".github/copilot-instructions.md",
    ".github/instructions",
    ".cursor/rules",
    ".cursorrules",
    "CLAUDE.md",
    "GEMINI.md",
    "CONTRIBUTING.md",
)
# Managed starter files under `.context/`; never inventoried as focused sources.
RESERVED_CONTEXT_FILENAMES = frozenset({"project.md", "readme.md", "scientific-practice.md"})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
CONTEXT_GUIDANCE_LABELS = ("Purpose", "Read when", "Update when")
CONTEXT_GUIDANCE_MAX_CHARS = 280


AGENT_SKILLS = (
    "spctx-project-context",
    "spctx-public-writing",
    "spctx-scientific-change",
)

SKILL_TRIGGER_SEPARATOR = "Also use for requests such as:"


@dataclass(frozen=True, slots=True)
class AgentSkillParts:
    """The frontmatter fields and instruction body of one Agent Skill."""

    name: str
    description: str
    body: str


@dataclass(frozen=True, slots=True)
class AgentSkillComparison:
    """How one installed Agent Skill diverges from its packaged counterpart."""

    description: str
    body: str


def agent_skill_path(skill_name: str) -> str:
    return f".agents/skills/{skill_name}/SKILL.md"


AGENT_SKILL_PATHS = tuple(agent_skill_path(name) for name in AGENT_SKILLS)

# Claude Code discovers project skills only under `.claude/skills/` and reads
# nothing under `.agents/`, so a project using it needs a discoverable pointer.
CLAUDE_INSTRUCTION_PATH = "CLAUDE.md"
CLAUDE_IMPORT_LINE = "@AGENTS.md"


def claude_skill_path(skill_name: str) -> str:
    return f".claude/skills/{skill_name}/SKILL.md"


CLAUDE_SKILL_PATHS = tuple(claude_skill_path(name) for name in AGENT_SKILLS)


def build_claude_skill_stub(skill_name: str, description: str) -> bytes:
    """Render the pointer skill that makes one canonical procedure discoverable."""

    canonical = agent_skill_path(skill_name)
    return (
        "\n".join(
            (
                "---",
                f"name: {skill_name}",
                f"description: {description}",
                "---",
                "",
                f"Read `{canonical}` and follow it exactly.",
                "",
                "That file is the procedure. This one exists only so Claude Code can find "
                "it, and holds no guidance of its own. If you tune the trigger phrasings, "
                "change them in both descriptions.",
                "",
            )
        )
    ).encode("utf-8")


class OperationError(RuntimeError):
    """A bounded, user-actionable project operation failure."""


@dataclass(frozen=True, slots=True)
class InitializationFile:
    """One self-contained template-file observation made during preflight."""

    resource_id: str
    relative_path: str
    content: bytes
    sha256: str
    disposition: str
    target_sha256: str | None = None
    target_content: bytes | None = None


@dataclass(frozen=True, slots=True)
class InitializationPlan:
    """An immutable preview of all safe initialization effects."""

    target: Path
    mode: str
    resource_bundle_sha256: str
    files: tuple[InitializationFile, ...]
    conflicts: tuple[str, ...]
    existing_instructions: tuple[str, ...] = ()
    claude_bridge: bool = False

    @property
    def status(self) -> str:
        """Return the user-facing preflight state."""

        if self.conflicts:
            return "blocked"
        if self.copy_files and self.deferred_files:
            return "ready_with_activation_deferred"
        if self.copy_files:
            return "ready"
        if self.deferred_files:
            return "activation_review_required"
        return "starter_files_present"

    @property
    def copy_files(self) -> tuple[str, ...]:
        return tuple(
            file.relative_path for file in self.files if file.disposition == "create"
        )

    @property
    def identical_files(self) -> tuple[str, ...]:
        return tuple(
            file.relative_path for file in self.files if file.disposition == "identical"
        )

    @property
    def retained_files(self) -> tuple[str, ...]:
        return tuple(
            file.relative_path for file in self.files if file.disposition == "retain"
        )

    @property
    def deferred_files(self) -> tuple[str, ...]:
        return tuple(
            file.relative_path for file in self.files if file.disposition == "defer"
        )

    @property
    def planned_files(self) -> tuple[InitializationFile, ...]:
        """Return only entries that an apply would create."""

        return tuple(file for file in self.files if file.disposition == "create")

    @property
    def agent_skill_files(self) -> tuple[InitializationFile, ...]:
        return tuple(
            file for file in self.files if file.relative_path in AGENT_SKILL_PATHS
        )

    @property
    def claude_skill_files(self) -> tuple[InitializationFile, ...]:
        return tuple(
            file for file in self.files if file.relative_path in CLAUDE_SKILL_PATHS
        )


@dataclass(frozen=True, slots=True)
class InitializationResult:
    """The immutable effects of a successfully applied initialization plan."""

    target: Path
    mode: str
    status: str
    resource_bundle_sha256: str
    created_files: tuple[str, ...]
    identical_files: tuple[str, ...]
    retained_files: tuple[str, ...]
    deferred_files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OwnerDiscovery:
    """The safe focused-context paths visible in one project."""

    owners: tuple[str, ...]
    conflicts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ContextGuidance:
    """Bounded routing summaries extracted from one current context source."""

    path: str
    purpose: str | None
    read_when: str | None
    update_when: str | None

    @property
    def complete(self) -> bool:
        return all((self.purpose, self.read_when, self.update_when))


@dataclass(frozen=True, slots=True)
class IndexSyncPlan:
    """An immutable preview of one bounded context-index synchronization."""

    target: Path
    resource_bundle_sha256: str
    resource_id: str
    relative_path: str
    source_content: bytes
    source_sha256: str
    specialized_owners: tuple[str, ...]
    owner_guidance: tuple[ContextGuidance, ...]
    action: str
    original_content: bytes | None
    original_sha256: str | None
    original_identity: tuple[int, int] | None
    planned_content: bytes | None
    planned_sha256: str | None
    conflicts: tuple[str, ...]

    @property
    def status(self) -> str:
        if self.conflicts or self.action == "blocked":
            return "blocked"
        if self.action in {"not_needed", "no_changes"}:
            return self.action
        return "ready"

    @property
    def destination(self) -> Path:
        return _destination(self.target, self.relative_path)


@dataclass(frozen=True, slots=True)
class IndexSyncResult:
    """The immutable effect of a successfully applied index-sync plan."""

    target: Path
    status: str
    action: str
    resource_bundle_sha256: str
    specialized_owners: tuple[str, ...]
    changed_files: tuple[str, ...]


def _link_kind(path: Path) -> str | None:
    if path.is_symlink():
        return "symlink"

    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        return "junction"

    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except (FileNotFoundError, NotADirectoryError):
        return None
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    return "reparse point" if attributes & reparse_flag else None


def discover_specialized_owners(target: str | os.PathLike[str]) -> OwnerDiscovery:
    """Return focused context files without following linked managed paths."""

    root = Path(target)
    # Keep string identity until after case-collision detection. ``WindowsPath``
    # equality is case-insensitive, so a ``set[Path]`` would erase evidence.
    candidates: list[str] = []
    conflicts: list[str] = []
    design_root = root / ".context"
    design_link = _link_kind(design_root)
    if design_link is not None:
        return OwnerDiscovery((), (f".context (context directory is a {design_link})",))
    if design_root.exists() and not design_root.is_dir():
        return OwnerDiscovery((), (".context (context path is not a directory)",))
    if design_root.is_dir():
        try:
            design_entries = tuple(design_root.iterdir())
        except OSError as exc:
            return OwnerDiscovery((), (f".context (cannot inspect: {exc})",))
        for path in design_entries:
            if (
                path.name.casefold().endswith(".md")
                and path.name.casefold() not in RESERVED_CONTEXT_FILENAMES
            ):
                candidates.append(path.relative_to(root).as_posix())

    active_root = design_root / "active"
    active_link = _link_kind(active_root)
    if active_link is not None:
        conflicts.append(
            f".context/active (focused-context directory is a {active_link})"
        )
    elif active_root.exists() and not active_root.is_dir():
        conflicts.append(".context/active (focused-context path is not a directory)")
    elif active_root.is_dir():
        try:
            active_entries = tuple(active_root.iterdir())
        except OSError as exc:
            conflicts.append(f".context/active (cannot inspect: {exc})")
        else:
            for path in active_entries:
                if path.name.casefold().endswith(".md"):
                    candidates.append(path.relative_to(root).as_posix())

    owners: list[str] = []
    seen_casefolded: dict[str, str] = {}
    for relative_text in sorted(
        set(candidates),
        key=lambda item: (item.casefold(), item),
    ):
        folded = relative_text.casefold()
        prior = seen_casefolded.get(folded)
        if prior is not None and prior != relative_text:
            conflicts.append(f"{relative_text} (path differs from {prior} only by case)")
            continue
        seen_casefolded[folded] = relative_text
        path = root / Path(relative_text)
        link_kind = _link_kind(path)
        if link_kind is not None:
            conflicts.append(f"{relative_text} (focused context is a {link_kind})")
        elif path.exists() and not path.is_file():
            conflicts.append(f"{relative_text} (focused context is not a regular file)")
        elif path.is_file():
            owners.append(relative_text)
    return OwnerDiscovery(tuple(owners), tuple(conflicts))


def extract_context_guidance(text: str, path: str) -> ContextGuidance:
    """Extract bounded routing fields without interpreting document meaning."""

    values: dict[str, list[str] | None] = {}
    active: str | None = None
    label_keys = {label.casefold(): label for label in CONTEXT_GUIDANCE_LABELS}
    for raw_line in text.splitlines()[:20]:
        line = raw_line.strip()
        matched: str | None = None
        for folded, label in label_keys.items():
            prefix = folded + ":"
            if line.casefold().startswith(prefix):
                matched = label
                value = line[len(prefix) :].strip()
                if label in values:
                    values[label] = None
                else:
                    values[label] = [value] if value else []
                active = label
                break
        if matched is not None:
            continue
        if not line:
            active = None
            continue
        if active is not None and values.get(active) is not None:
            assert isinstance(values[active], list)
            values[active].append(line)

    normalized: dict[str, str | None] = {}
    for label in CONTEXT_GUIDANCE_LABELS:
        parts = values.get(label)
        if not parts:
            normalized[label] = None
            continue
        value = " ".join(" ".join(parts).split())
        normalized[label] = (
            value if 0 < len(value) <= CONTEXT_GUIDANCE_MAX_CHARS else None
        )
    return ContextGuidance(
        path=path,
        purpose=normalized["Purpose"],
        read_when=normalized["Read when"],
        update_when=normalized["Update when"],
    )


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _first_structural_obstruction(destination: Path, target: Path) -> Path | None:
    """Find a non-directory or link ancestor strictly below ``target``."""

    current = destination.parent
    while current != target and _is_relative_to(current, target):
        if _link_kind(current) is not None:
            return current
        if current.exists() and not current.is_dir():
            return current
        current = current.parent
    return None


def _display_path(path: Path) -> str:
    return path.as_posix()


def _destination(target: Path, relative_path: str) -> Path:
    pure_path = PurePosixPath(relative_path)
    if pure_path.is_absolute() or ".." in pure_path.parts or pure_path.as_posix() in {"", "."}:
        raise OperationError(f"Unsafe resource destination path: {relative_path!r}.")
    return target.joinpath(*pure_path.parts)


def _canonical_target(
    target: str | os.PathLike[str],
    *,
    operation: str = "Initialization",
) -> Path:
    # ``resolve()`` would erase linked ancestors before we could reject them.
    # ``abspath`` normalizes the lexical path without following filesystem links.
    path = Path(os.path.abspath(os.fspath(target)))
    linked_ancestor = _first_link_ancestor(path)
    if linked_ancestor is not None:
        linked_path, link_kind = linked_ancestor
        raise OperationError(
            f"{operation} target path cannot contain a {link_kind}: {linked_path}"
        )
    return path


def _first_link_ancestor(path: Path) -> tuple[Path, str] | None:
    """Inspect the canonical path chain so later ancestor swaps cannot redirect writes."""

    current = path
    while True:
        link_kind = _link_kind(current)
        if link_kind is not None:
            return current, link_kind
        if current.parent == current:
            return None
        current = current.parent


def _validate_target_mode(target: Path, mode: str) -> None:
    linked_ancestor = _first_link_ancestor(target)
    if linked_ancestor is not None:
        linked_path, link_kind = linked_ancestor
        raise OperationError(
            f"Initialization target path cannot contain a {link_kind}: {linked_path}"
        )

    if mode == "new":
        if target.exists() and not target.is_dir():
            raise OperationError(f"New-project target exists and is not a directory: {target}")
        if target.exists() and any(target.iterdir()):
            raise OperationError(
                "New-project initialization requires a missing or empty target. "
                f"Use --mode retrofit for an existing project: {target}"
            )
        if not target.exists():
            current = target.parent
            while not current.exists():
                if current.parent == current:
                    break
                current = current.parent
            if not current.is_dir():
                raise OperationError(
                    f"New-project target has no plain existing directory ancestor: {target}"
                )
        return

    if not target.is_dir():
        raise OperationError(f"Retrofit target must be an existing directory: {target}")


def infer_initialization_mode(target: str | os.PathLike[str]) -> str:
    """Choose ``new`` for a missing/empty target and ``retrofit`` otherwise."""

    canonical_target = _canonical_target(target)
    if not canonical_target.exists():
        return "new"
    if canonical_target.is_dir() and not any(canonical_target.iterdir()):
        return "new"
    return "retrofit"


def _validate_existing_project_target(target: Path, *, operation: str) -> None:
    linked_ancestor = _first_link_ancestor(target)
    if linked_ancestor is not None:
        linked_path, link_kind = linked_ancestor
        raise OperationError(
            f"{operation} target path cannot contain a {link_kind}: {linked_path}"
        )
    if not target.is_dir():
        raise OperationError(f"{operation} target must be an existing directory: {target}")


def _target_file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _planned_file(
    entry: ResourceEntry,
    disposition: str,
    *,
    target_sha256: str | None = None,
    target_content: bytes | None = None,
) -> InitializationFile:
    return InitializationFile(
        resource_id=entry.resource_id,
        relative_path=entry.relative_path,
        content=entry.content,
        sha256=entry.sha256,
        disposition=disposition,
        target_sha256=target_sha256,
        target_content=target_content,
    )


def parse_agent_skill_content(
    content: bytes,
    *,
    expected_name: str | None = None,
) -> AgentSkillParts:
    """Apply a dependency-free structural check and return the skill's parts."""

    try:
        text = content.decode("utf-8")
    except UnicodeError as exc:
        raise OperationError("Agent Skill must be valid UTF-8.") from exc
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise OperationError("Agent Skill must start with YAML frontmatter.")
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise OperationError("Agent Skill frontmatter is not closed.") from exc
    fields: dict[str, str] = {}
    for line in lines[1:closing]:
        if ":" not in line:
            raise OperationError("Agent Skill frontmatter contains a malformed field.")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value or key in fields:
            raise OperationError("Agent Skill frontmatter fields must be unique and non-empty.")
        fields[key] = value
    if set(fields) != {"name", "description"}:
        raise OperationError("Agent Skill frontmatter must contain only name and description.")
    name = fields["name"]
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is None or len(name) > 64:
        raise OperationError("Agent Skill name is not Agent Skills compatible.")
    if len(fields["description"]) > 1024:
        raise OperationError("Agent Skill description exceeds 1024 characters.")
    body = "\n".join(lines[closing + 1 :]).strip()
    if not body:
        raise OperationError("Agent Skill must contain an instruction body.")
    if expected_name is not None and name != expected_name:
        raise OperationError("Agent Skill name does not match its directory identity.")
    return AgentSkillParts(name=name, description=fields["description"], body=body)


def validate_agent_skill_content(
    content: bytes,
    *,
    expected_name: str | None = None,
) -> None:
    """Apply a dependency-free structural check for a canonical Agent Skill."""

    parse_agent_skill_content(content, expected_name=expected_name)


def compare_agent_skill(installed: bytes, packaged: bytes) -> AgentSkillComparison:
    """Report how an installed skill diverges from its packaged counterpart.

    The description is project-owned after the separator so project vocabulary
    survives an upgrade; the packaged prefix must stay intact or packaged
    trigger updates can never reach the project.
    """

    installed_parts = parse_agent_skill_content(installed)
    packaged_parts = parse_agent_skill_content(packaged)

    if installed_parts.description == packaged_parts.description:
        description = "packaged"
    elif not installed_parts.description.startswith(packaged_parts.description):
        description = "replaced"
    else:
        addition = installed_parts.description[len(packaged_parts.description) :]
        description = (
            "extended"
            if addition.lstrip().startswith(SKILL_TRIGGER_SEPARATOR)
            else "extended_without_separator"
        )

    return AgentSkillComparison(
        description=description,
        body="exact" if installed_parts.body == packaged_parts.body else "modified",
    )


def plan_initialization(
    catalog: ResourceCatalog,
    target: str | os.PathLike[str],
    mode: str,
    *,
    claude: bool = False,
) -> InitializationPlan:
    """Preflight a non-overwriting starter installation without changing the target.

    ``new`` requires a missing or empty target.  ``retrofit`` accepts existing
    project files, retains every occupied regular starter path byte-for-byte,
    and fills safe missing starter paths. A missing agent route is deferred when
    it would activate retained unreviewed guidance. Structural conflicts remain
    blockers.  ``claude`` additionally plans pointer skills under
    ``.claude/skills/``, generated from the skills this project will have.
    """

    if mode not in INITIALIZATION_MODES:
        raise OperationError(f"Unknown initialization mode: {mode}")
    canonical_target = _canonical_target(target)
    _validate_target_mode(canonical_target, mode)
    files: list[InitializationFile] = []
    conflicts: list[str] = []

    for entry in catalog.starter_entries:
        relative_text = entry.relative_path
        destination = _destination(canonical_target, relative_text)
        obstruction = _first_structural_obstruction(destination, canonical_target)

        if obstruction is not None:
            obstruction_text = _display_path(obstruction.relative_to(canonical_target))
            conflicts.append(
                f"{relative_text} (parent path is not a plain directory: {obstruction_text})"
            )
            continue

        link_kind = _link_kind(destination)
        if link_kind is not None:
            conflicts.append(f"{relative_text} (target is a {link_kind})")
            continue

        if not destination.exists():
            files.append(_planned_file(entry, "create"))
            continue

        if not destination.is_file():
            conflicts.append(f"{relative_text} (target path is not a file)")
            continue

        target_content = destination.read_bytes()
        target_sha256 = hashlib.sha256(target_content).hexdigest()
        if target_content == entry.content:
            files.append(
                _planned_file(
                    entry,
                    "identical",
                    target_sha256=target_sha256,
                    target_content=target_content,
                )
            )
        elif mode == "retrofit":
            files.append(
                _planned_file(
                    entry,
                    "retain",
                    target_sha256=target_sha256,
                    target_content=target_content,
                )
            )
        else:
            conflicts.append(f"{relative_text} (target file differs)")

    retained_routes = {
        SCIENTIFIC_PRACTICE_PATH,
        *AGENT_SKILL_PATHS,
    }
    if any(
        file.relative_path in retained_routes and file.disposition == "retain"
        for file in files
    ):
        files = [
            replace(file, disposition="defer")
            if file.relative_path == "AGENTS.md" and file.disposition == "create"
            else file
            for file in files
        ]

    if claude:
        planned_skills = {
            file.relative_path: file
            for file in files
            if file.relative_path in AGENT_SKILL_PATHS
        }
        for skill_name in AGENT_SKILLS:
            relative_text = claude_skill_path(skill_name)
            source = planned_skills.get(agent_skill_path(skill_name))
            if source is None:
                conflicts.append(
                    f"{relative_text} (its canonical skill is not part of this plan)"
                )
                continue
            # A retained skill is the project's own, so its tuned triggers win.
            installed = (
                source.target_content
                if source.disposition == "retain" and source.target_content is not None
                else source.content
            )
            try:
                description = parse_agent_skill_content(installed).description
            except OperationError:
                conflicts.append(
                    f"{relative_text} (cannot read the description in "
                    f"{agent_skill_path(skill_name)})"
                )
                continue

            content = build_claude_skill_stub(skill_name, description)
            destination = _destination(canonical_target, relative_text)
            obstruction = _first_structural_obstruction(destination, canonical_target)
            if obstruction is not None:
                obstruction_text = _display_path(obstruction.relative_to(canonical_target))
                conflicts.append(
                    f"{relative_text} (parent path is not a plain directory: {obstruction_text})"
                )
                continue

            link_kind = _link_kind(destination)
            if link_kind is not None:
                conflicts.append(f"{relative_text} (target is a {link_kind})")
                continue

            generated = InitializationFile(
                resource_id=f"generated/{relative_text}",
                relative_path=relative_text,
                content=content,
                sha256=hashlib.sha256(content).hexdigest(),
                disposition="create",
            )
            if not destination.exists():
                files.append(generated)
                continue
            if not destination.is_file():
                conflicts.append(f"{relative_text} (target path is not a file)")
                continue

            target_content = destination.read_bytes()
            files.append(
                replace(
                    generated,
                    disposition="identical" if target_content == content else "retain",
                    target_sha256=hashlib.sha256(target_content).hexdigest(),
                    target_content=target_content,
                )
            )

    return InitializationPlan(
        target=canonical_target,
        mode=mode,
        resource_bundle_sha256=catalog.bundle_sha256,
        files=tuple(files),
        conflicts=tuple(conflicts),
        existing_instructions=_existing_instructions(canonical_target),
        claude_bridge=claude,
    )


def _existing_instructions(root: Path) -> tuple[str, ...]:
    """Name instruction locations already in the project, excluding `AGENTS.md`."""

    found: list[str] = []
    for relative_path in KNOWN_INSTRUCTION_PATHS:
        try:
            if (root / relative_path).exists():
                found.append(relative_path)
        except OSError:
            continue
    return tuple(found)


def _validate_plan_integrity(plan: InitializationPlan) -> None:
    if plan.mode not in INITIALIZATION_MODES:
        raise OperationError(f"Initialization plan has an unknown mode: {plan.mode}")
    paths: list[str] = []
    generated_paths: list[str] = []
    for file in plan.files:
        if file.disposition not in _FILE_DISPOSITIONS:
            raise OperationError(
                f"Initialization plan has an unknown disposition: {file.disposition}"
            )
        if hashlib.sha256(file.content).hexdigest() != file.sha256:
            raise OperationError(
                f"Initialization plan content digest is invalid: {file.relative_path}"
            )
        if file.resource_id.startswith("template/"):
            if file.resource_id != f"template/{file.relative_path}":
                raise OperationError(
                    f"Initialization plan resource identity is invalid: {file.resource_id}"
                )
        elif file.resource_id.startswith("generated/"):
            if (
                file.resource_id != f"generated/{file.relative_path}"
                or file.relative_path not in CLAUDE_SKILL_PATHS
            ):
                raise OperationError(
                    f"Initialization plan resource identity is invalid: {file.resource_id}"
                )
        else:
            raise OperationError(
                f"Initialization plan resource identity is invalid: {file.resource_id}"
            )
        skill_definition = next(
            (
                name
                for name in AGENT_SKILLS
                if file.relative_path
                in {agent_skill_path(name), claude_skill_path(name)}
            ),
            None,
        )
        if skill_definition is not None:
            validate_agent_skill_content(
                file.content,
                expected_name=skill_definition,
            )
        _destination(plan.target, file.relative_path)
        if file.disposition in {"identical", "retain"} and file.target_sha256 is None:
            raise OperationError(
                f"Initialization plan lacks its target preflight digest: {file.relative_path}"
            )
        if file.disposition in {"identical", "retain"} and file.target_content is None:
            raise OperationError(
                f"Initialization plan lacks its target preflight content: {file.relative_path}"
            )
        if file.target_content is not None and (
            hashlib.sha256(file.target_content).hexdigest() != file.target_sha256
        ):
            raise OperationError(
                f"Initialization plan target content digest is invalid: {file.relative_path}"
            )
        if file.disposition in {"create", "defer"} and (
            file.target_sha256 is not None or file.target_content is not None
        ):
            raise OperationError(
                "Initialization missing-file plan has an unexpected target observation: "
                f"{file.relative_path}"
            )
        if file.disposition == "identical" and file.target_sha256 != file.sha256:
            raise OperationError(
                f"Initialization identical-file observation is invalid: {file.relative_path}"
            )
        if file.disposition == "retain" and file.target_sha256 == file.sha256:
            raise OperationError(
                f"Initialization retained-file observation is not differing: {file.relative_path}"
            )
        if file.relative_path in CLAUDE_SKILL_PATHS:
            generated_paths.append(file.relative_path)
        else:
            paths.append(file.relative_path)

    if tuple(paths) != STARTER_INVENTORY:
        raise OperationError(
            "A ready initialization plan must contain the exact starter inventory."
        )
    expected_generated = CLAUDE_SKILL_PATHS if plan.claude_bridge else ()
    if tuple(generated_paths) != expected_generated:
        raise OperationError(
            "A ready initialization plan must contain the exact generated inventory."
        )


def _revalidate_plan_observations(plan: InitializationPlan) -> None:
    """Repeat the complete read-only target preflight immediately before writes."""

    _validate_target_mode(plan.target, plan.mode)
    for file in plan.files:
        destination = _destination(plan.target, file.relative_path)
        obstruction = _first_structural_obstruction(destination, plan.target)
        if obstruction is not None:
            raise OperationError(
                "Initialization target structure changed after preflight: "
                f"{file.relative_path}"
            )
        if _link_kind(destination) is not None:
            raise OperationError(
                f"Initialization target changed after preflight: {file.relative_path}"
            )

        if file.disposition in {"create", "defer"}:
            if destination.exists():
                raise OperationError(
                    f"Initialization target appeared after preflight: {file.relative_path}"
                )
            continue

        if not destination.is_file():
            raise OperationError(
                f"Initialization target is no longer a regular file: {file.relative_path}"
            )
        if _target_file_sha256(destination) != file.target_sha256:
            raise OperationError(
                f"Initialization target changed after preflight: {file.relative_path}"
            )


def _create_directory_chain(path: Path, created: list[Path]) -> None:
    missing: list[Path] = []
    current = path
    while not current.exists():
        if _link_kind(current) is not None:
            raise OperationError(
                f"Cannot create a directory through a link or reparse point: {current}"
            )
        missing.append(current)
        if current.parent == current:
            raise OperationError(f"No existing parent directory is available for: {path}")
        current = current.parent

    link_kind = _link_kind(current)
    if link_kind is not None or not current.is_dir():
        description = link_kind or "non-directory path"
        raise OperationError(f"Cannot create a directory below {description}: {current}")

    for directory in reversed(missing):
        directory.mkdir()
        created.append(directory)


def _create_parent_directories(path: Path, stop: Path, created: list[Path]) -> None:
    try:
        relative = path.relative_to(stop)
    except ValueError as exc:
        raise OperationError(f"Destination parent escapes initialization target: {path}") from exc

    current = stop
    for component in relative.parts:
        current = current / component
        link_kind = _link_kind(current)
        if link_kind is not None:
            raise OperationError(
                f"Cannot create a directory through a {link_kind}: {current}"
            )
        if current.exists():
            if not current.is_dir():
                raise OperationError(
                    f"Cannot create a directory below a non-directory path: {current}"
                )
            continue
        current.mkdir()
        created.append(current)


def _write_bytes_exclusively(
    content: bytes,
    destination: Path,
    *,
    operation: str = "Initialization",
) -> tuple[int, int]:
    created_identity: tuple[int, int] | None = None
    try:
        with destination.open("xb") as destination_handle:
            created = os.fstat(destination_handle.fileno())
            created_identity = (created.st_dev, created.st_ino)
            destination_handle.write(content)
            destination_handle.flush()
            os.fsync(destination_handle.fileno())
        if _link_kind(destination) is not None or not destination.is_file():
            raise OperationError(
                f"Exclusively created path changed during {operation.lower()}: {destination}"
            )
        current = destination.stat(follow_symlinks=False)
        current_identity = (current.st_dev, current.st_ino)
        if current_identity != created_identity or _target_file_sha256(destination) != hashlib.sha256(content).hexdigest():
            raise OperationError(
                f"Exclusively created file changed during {operation.lower()}: {destination}"
            )
        return created_identity
    except Exception as exc:
        if created_identity is not None:
            try:
                current = destination.stat(follow_symlinks=False)
                if (
                    _link_kind(destination) is None
                    and destination.is_file()
                    and (current.st_dev, current.st_ino) == created_identity
                ):
                    destination.unlink()
                elif destination.exists() or _link_kind(destination) is not None:
                    raise OperationError(
                        f"{operation} write failed and the created path changed before "
                        f"safe cleanup: {destination}"
                    ) from exc
            except FileNotFoundError:
                pass
        raise


def _rollback_created_file(
    path: Path,
    identity: tuple[int, int],
    expected_sha256: str,
) -> str | None:
    try:
        link_kind = _link_kind(path)
        if link_kind is not None or not path.is_file():
            return f"{path} is no longer the regular file created by this operation"
        current = path.stat(follow_symlinks=False)
        if (current.st_dev, current.st_ino) != identity:
            return f"{path} no longer has the identity created by this operation"
        if _target_file_sha256(path) != expected_sha256:
            return f"{path} changed before rollback"
        path.unlink()
        return None
    except OSError as exc:
        return f"{path}: {exc}"


def apply_initialization(plan: InitializationPlan) -> InitializationResult:
    """Apply a ready plan with exclusive writes and owned-effect rollback."""

    if plan.conflicts:
        raise OperationError(
            "Initialization is blocked by target conflicts; no files were created."
        )
    _validate_plan_integrity(plan)

    # Revalidate every classification before creating even the first directory.
    _revalidate_plan_observations(plan)

    created_directories: list[Path] = []
    created_files: list[tuple[Path, tuple[int, int], str]] = []
    try:
        if not plan.target.exists():
            _create_directory_chain(plan.target, created_directories)

        for file in plan.planned_files:
            destination = _destination(plan.target, file.relative_path)
            _create_parent_directories(
                destination.parent,
                plan.target,
                created_directories,
            )
            identity = _write_bytes_exclusively(file.content, destination)
            created_files.append((destination, identity, file.sha256))
    except Exception as exc:
        rollback_failures: list[str] = []
        for path, identity, expected_sha256 in reversed(created_files):
            failure = _rollback_created_file(path, identity, expected_sha256)
            if failure is not None:
                rollback_failures.append(failure)
        for directory in reversed(created_directories):
            try:
                directory.rmdir()
            except FileNotFoundError:
                pass
            except OSError as rollback_exc:
                rollback_failures.append(f"{directory}: {rollback_exc}")
        if rollback_failures:
            raise OperationError(
                f"Initialization failed ({exc}); rollback was incomplete: "
                + "; ".join(rollback_failures)
            ) from exc
        raise

    created_paths = tuple(file.relative_path for file in plan.planned_files)
    return InitializationResult(
        target=plan.target,
        mode=plan.mode,
        status=(
            "initialized_with_activation_deferred"
            if created_paths and plan.deferred_files
            else "initialized"
            if created_paths
            else "activation_review_required"
            if plan.deferred_files
            else "starter_files_present"
        ),
        resource_bundle_sha256=plan.resource_bundle_sha256,
        created_files=created_paths,
        identical_files=plan.identical_files,
        retained_files=plan.retained_files,
        deferred_files=plan.deferred_files,
    )


def extract_managed_block(
    content: bytes | str,
    begin_marker: str,
    end_marker: str,
) -> tuple[str, str | None]:
    """Return ``absent``, ``invalid``, or ``present`` plus normalized block text."""

    if isinstance(content, bytes):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            return "invalid", None
    else:
        text = content
    lines = text.splitlines()
    begins = [index for index, line in enumerate(lines) if line == begin_marker]
    ends = [index for index, line in enumerate(lines) if line == end_marker]
    if not begins and not ends:
        return "absent", None
    if len(begins) != 1 or len(ends) != 1 or begins[0] >= ends[0]:
        return "invalid", None
    return "present", "\n".join(lines[begins[0] : ends[0] + 1])


def managed_block_state(
    content: bytes | str,
    expected_content: bytes | str,
    begin_marker: str,
    end_marker: str,
) -> str:
    """Classify a versioned managed block without judging surrounding prose."""

    state, block = extract_managed_block(content, begin_marker, end_marker)
    expected_state, expected_block = extract_managed_block(
        expected_content,
        begin_marker,
        end_marker,
    )
    if expected_state != "present" or expected_block is None:
        raise OperationError("Packaged scientific contract block is invalid.")
    if state != "present":
        return state
    return "exact" if block == expected_block else "modified"


def _validate_sha256(value: str, *, label: str) -> None:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise OperationError(f"{label} is not a lowercase SHA-256 digest.")


def _validate_canonical_plan_target(target: Path, *, operation: str) -> None:
    if not isinstance(target, Path):
        raise OperationError(f"{operation} plan target must be a pathlib Path.")
    canonical = _canonical_target(target, operation=operation)
    if canonical != target:
        raise OperationError(f"{operation} plan target is not canonical: {target}")


def rewrite_context_inventory(
    content: bytes,
    owners: Sequence[str],
    guidance: Sequence[ContextGuidance] = (),
) -> bytes:
    """Replace only the unique generated inventory block in a context index."""

    try:
        text = content.decode("utf-8")
    except UnicodeError as exc:
        raise OperationError("Context index must be valid UTF-8.") from exc
    lines = text.splitlines(keepends=True)
    begin_indexes = [
        index
        for index, line in enumerate(lines)
        if line.rstrip("\r\n") == CONTEXT_INVENTORY_BEGIN
    ]
    end_indexes = [
        index
        for index, line in enumerate(lines)
        if line.rstrip("\r\n") == CONTEXT_INVENTORY_END
    ]
    if len(begin_indexes) != 1 or len(end_indexes) != 1:
        raise OperationError(
            "Context index must contain exactly one generated context-inventory marker pair."
        )
    begin = begin_indexes[0]
    end = end_indexes[0]
    if begin >= end:
        raise OperationError("Context-index generated inventory markers are out of order.")
    if not lines[begin].endswith("\n"):
        raise OperationError("Context-index begin marker must occupy its own terminated line.")

    newline = "\r\n" if lines[begin].endswith("\r\n") else "\n"
    guidance_by_path = {item.path: item for item in guidance}
    if len(guidance_by_path) != len(guidance):
        raise OperationError("Context guidance paths must be unique.")
    if set(guidance_by_path).difference(owners):
        raise OperationError("Context guidance contains a path outside the owner inventory.")
    if owners:
        inventory: list[str] = []
        for path in owners:
            inventory.append(f"- `{path}`{newline}")
            item = guidance_by_path.get(path)
            if item is not None and item.complete:
                inventory.extend(
                    (
                        f"  - Purpose: {item.purpose}{newline}",
                        f"  - Read when: {item.read_when}{newline}",
                        f"  - Update when: {item.update_when}{newline}",
                    )
                )
    else:
        inventory = [f"{CONTEXT_EMPTY_INVENTORY_LINE}{newline}"]
    return "".join(lines[: begin + 1] + inventory + lines[end:]).encode("utf-8")


def collect_context_guidance(
    target: Path,
    owners: Sequence[str],
) -> tuple[ContextGuidance, ...]:
    items: list[ContextGuidance] = []
    for owner in owners:
        path = _destination(target, owner)
        content, _ = _regular_file_observation(path, label="Focused context document")
        try:
            text = content.decode("utf-8")
        except UnicodeError as exc:
            raise OperationError(
                f"Focused context document must be valid UTF-8: {owner}"
            ) from exc
        items.append(extract_context_guidance(text, owner))
    return tuple(items)


def _index_plan(
    *,
    target: Path,
    catalog: ResourceCatalog,
    entry: ResourceEntry,
    owners: tuple[str, ...],
    owner_guidance: tuple[ContextGuidance, ...],
    action: str,
    original_content: bytes | None = None,
    original_identity: tuple[int, int] | None = None,
    planned_content: bytes | None = None,
    conflicts: tuple[str, ...] = (),
) -> IndexSyncPlan:
    return IndexSyncPlan(
        target=target,
        resource_bundle_sha256=catalog.bundle_sha256,
        resource_id=entry.resource_id,
        relative_path=CONTEXT_INDEX_PATH,
        source_content=entry.content,
        source_sha256=entry.sha256,
        specialized_owners=owners,
        owner_guidance=owner_guidance,
        action=action,
        original_content=original_content,
        original_sha256=(
            hashlib.sha256(original_content).hexdigest()
            if original_content is not None
            else None
        ),
        original_identity=original_identity,
        planned_content=planned_content,
        planned_sha256=(
            hashlib.sha256(planned_content).hexdigest()
            if planned_content is not None
            else None
        ),
        conflicts=conflicts,
    )


def _regular_file_observation(
    path: Path,
    *,
    label: str,
) -> tuple[bytes, tuple[int, int]]:
    link_kind = _link_kind(path)
    if link_kind is not None:
        raise OperationError(f"{label} is a {link_kind}: {path}")
    if not path.is_file():
        raise OperationError(f"{label} is not a regular file: {path}")
    before = path.stat(follow_symlinks=False)
    content = path.read_bytes()
    after = path.stat(follow_symlinks=False)
    before_identity = (before.st_dev, before.st_ino)
    after_identity = (after.st_dev, after.st_ino)
    if (
        before_identity != after_identity
        or before.st_size != after.st_size
        or before.st_mtime_ns != after.st_mtime_ns
    ):
        raise OperationError(f"{label} changed while it was being inspected: {path}")
    return content, after_identity


def plan_index_sync(
    catalog: ResourceCatalog,
    target: str | os.PathLike[str],
) -> IndexSyncPlan:
    """Preflight bounded context-index creation or inventory synchronization."""

    canonical_target = _canonical_target(target, operation="Context-index")
    _validate_existing_project_target(canonical_target, operation="Context-index")
    try:
        entry = catalog.get(CONTEXT_INDEX_RESOURCE_ID)
    except KeyError as exc:  # ResourceCatalog normally makes this unreachable.
        raise OperationError(
            f"Context-index resource is unavailable: {CONTEXT_INDEX_RESOURCE_ID}"
        ) from exc

    discovery = discover_specialized_owners(canonical_target)
    owners = discovery.owners
    if discovery.conflicts:
        return _index_plan(
            target=canonical_target,
            catalog=catalog,
            entry=entry,
            owners=owners,
            owner_guidance=(),
            action="blocked",
            conflicts=discovery.conflicts,
        )
    try:
        owner_guidance = collect_context_guidance(canonical_target, owners)
    except OperationError as exc:
        return _index_plan(
            target=canonical_target,
            catalog=catalog,
            entry=entry,
            owners=owners,
            owner_guidance=(),
            action="blocked",
            conflicts=(str(exc),),
        )

    destination = _destination(canonical_target, CONTEXT_INDEX_PATH)
    link_kind = _link_kind(destination)
    if link_kind is not None:
        return _index_plan(
            target=canonical_target,
            catalog=catalog,
            entry=entry,
            owners=owners,
            owner_guidance=owner_guidance,
            action="blocked",
            conflicts=(f"{CONTEXT_INDEX_PATH} (target is a {link_kind})",),
        )

    if destination.exists():
        if not destination.is_file():
            return _index_plan(
                target=canonical_target,
                catalog=catalog,
                entry=entry,
                owners=owners,
                owner_guidance=owner_guidance,
                action="blocked",
                conflicts=(f"{CONTEXT_INDEX_PATH} (target is not a file)",),
            )
        original, identity = _regular_file_observation(
            destination,
            label="Context index",
        )
        try:
            planned = rewrite_context_inventory(original, owners, owner_guidance)
        except (OperationError, UnicodeError) as exc:
            return _index_plan(
                target=canonical_target,
                catalog=catalog,
                entry=entry,
                owners=owners,
                owner_guidance=owner_guidance,
                action="blocked",
                original_content=original,
                original_identity=identity,
                conflicts=(f"{CONTEXT_INDEX_PATH} ({exc})",),
            )
        action = "no_changes" if planned == original else "update"
        return _index_plan(
            target=canonical_target,
            catalog=catalog,
            entry=entry,
            owners=owners,
            owner_guidance=owner_guidance,
            action=action,
            original_content=original,
            original_identity=identity,
            planned_content=planned,
        )

    if len(owners) < 2:
        return _index_plan(
            target=canonical_target,
            catalog=catalog,
            entry=entry,
            owners=owners,
            owner_guidance=owner_guidance,
            action="not_needed",
        )

    planned = rewrite_context_inventory(entry.content, owners, owner_guidance)
    conflicts: list[str] = []
    obstruction = _first_structural_obstruction(destination, canonical_target)
    if obstruction is not None:
        obstruction_text = _display_path(obstruction.relative_to(canonical_target))
        conflicts.append(
            f"{CONTEXT_INDEX_PATH} "
            f"(parent path is not a plain directory: {obstruction_text})"
        )
    return _index_plan(
        target=canonical_target,
        catalog=catalog,
        entry=entry,
        owners=owners,
        owner_guidance=owner_guidance,
        action="blocked" if conflicts else "create",
        planned_content=None if conflicts else planned,
        conflicts=tuple(conflicts),
    )


def is_discoverable_owner_path(relative_path: str) -> bool:
    """Return whether one POSIX path may be inventoried as a focused source.

    Discovery and apply-time validation must share this rule; when they drifted,
    a custom `.context/<name>.md` planned cleanly and then failed on apply.
    """

    pure = PurePosixPath(relative_path)
    if pure.is_absolute() or ".." in pure.parts or pure.suffix.casefold() != ".md":
        return False
    if len(pure.parts) == 2 and pure.parts[0] == ".context":
        return pure.name.casefold() not in RESERVED_CONTEXT_FILENAMES
    return len(pure.parts) == 3 and pure.parts[:2] == (".context", "active")


def _validate_owner_tuple(owners: tuple[str, ...]) -> None:
    if type(owners) is not tuple or any(not isinstance(owner, str) for owner in owners):
        raise OperationError("Context-index owner inventory must be an immutable string tuple.")
    expected_order = tuple(sorted(set(owners), key=lambda item: (item.casefold(), item)))
    if owners != expected_order:
        raise OperationError("Context-index owner inventory is not unique and deterministic.")
    for owner in owners:
        if not is_discoverable_owner_path(owner):
            raise OperationError(f"Context-index owner path is invalid: {owner}")


def _validate_guidance_tuple(
    owners: tuple[str, ...],
    guidance: tuple[ContextGuidance, ...],
    *,
    allow_empty: bool = False,
) -> None:
    if type(guidance) is not tuple or any(
        not isinstance(item, ContextGuidance) for item in guidance
    ):
        raise OperationError("Context-index guidance must be an immutable guidance tuple.")
    if allow_empty and not guidance:
        return
    if tuple(item.path for item in guidance) != owners:
        raise OperationError("Context-index guidance does not match its owner inventory.")
    for item in guidance:
        for value in (item.purpose, item.read_when, item.update_when):
            if value is not None and (
                not isinstance(value, str)
                or not value
                or len(value) > CONTEXT_GUIDANCE_MAX_CHARS
            ):
                raise OperationError("Context-index guidance contains an invalid summary.")


def _validate_optional_bytes(
    content: bytes | None,
    sha256: str | None,
    *,
    label: str,
) -> None:
    if content is None and sha256 is None:
        return
    if type(content) is not bytes or sha256 is None:
        raise OperationError(f"{label} content and digest must appear together.")
    _validate_sha256(sha256, label=f"{label} identity")
    if hashlib.sha256(content).hexdigest() != sha256:
        raise OperationError(f"{label} digest is invalid.")


def _validate_index_sync_plan(plan: IndexSyncPlan) -> None:
    _validate_canonical_plan_target(plan.target, operation="Context-index")
    _validate_sha256(
        plan.resource_bundle_sha256,
        label="Context-index resource bundle identity",
    )
    if (
        plan.relative_path != CONTEXT_INDEX_PATH
        or plan.resource_id != CONTEXT_INDEX_RESOURCE_ID
    ):
        raise OperationError("Context-index plan resource identity is invalid.")
    if type(plan.source_content) is not bytes:
        raise OperationError("Context-index resource content must be immutable bytes.")
    _validate_sha256(plan.source_sha256, label="Context-index resource identity")
    if hashlib.sha256(plan.source_content).hexdigest() != plan.source_sha256:
        raise OperationError("Context-index resource digest is invalid.")
    _destination(plan.target, plan.relative_path)
    _validate_owner_tuple(plan.specialized_owners)
    _validate_guidance_tuple(
        plan.specialized_owners,
        plan.owner_guidance,
        allow_empty=bool(plan.conflicts),
    )
    _validate_optional_bytes(
        plan.original_content,
        plan.original_sha256,
        label="Context-index original",
    )
    _validate_optional_bytes(
        plan.planned_content,
        plan.planned_sha256,
        label="Context-index planned",
    )
    if (plan.original_content is None) != (plan.original_identity is None):
        raise OperationError(
            "Context-index original content and filesystem identity must appear together."
        )
    if plan.original_identity is not None and (
        type(plan.original_identity) is not tuple
        or len(plan.original_identity) != 2
        or any(not isinstance(value, int) for value in plan.original_identity)
    ):
        raise OperationError("Context-index original filesystem identity is invalid.")

    allowed_actions = {"blocked", "create", "update", "no_changes", "not_needed"}
    if plan.action not in allowed_actions:
        raise OperationError(f"Context-index plan has an unknown action: {plan.action}")
    if plan.action == "blocked":
        if not plan.conflicts or plan.planned_content is not None:
            raise OperationError("Blocked context-index plan relationships are invalid.")
        return
    if plan.conflicts:
        raise OperationError("Unblocked context-index plan unexpectedly has conflicts.")

    if plan.action == "not_needed":
        if (
            len(plan.specialized_owners) >= 2
            or plan.original_content is not None
            or plan.planned_content is not None
        ):
            raise OperationError("Context-index not-needed plan relationships are invalid.")
        return
    if plan.action == "create":
        expected = rewrite_context_inventory(
            plan.source_content,
            plan.specialized_owners,
            plan.owner_guidance,
        )
        if (
            len(plan.specialized_owners) < 2
            or plan.original_content is not None
            or plan.planned_content != expected
        ):
            raise OperationError("Context-index create plan relationships are invalid.")
        return

    if plan.original_content is None or plan.planned_content is None:
        raise OperationError("Context-index update observation is incomplete.")
    expected = rewrite_context_inventory(
        plan.original_content,
        plan.specialized_owners,
        plan.owner_guidance,
    )
    if plan.planned_content != expected:
        raise OperationError("Context-index planned inventory transformation is invalid.")
    should_be_no_changes = plan.planned_content == plan.original_content
    if should_be_no_changes != (plan.action == "no_changes"):
        raise OperationError("Context-index action does not match its planned bytes.")


def _revalidate_index_sync_plan(plan: IndexSyncPlan) -> None:
    _validate_existing_project_target(plan.target, operation="Context-index")
    discovery = discover_specialized_owners(plan.target)
    if discovery.conflicts or discovery.owners != plan.specialized_owners:
        raise OperationError(
            "Focused context owners changed after preflight; rerun context-index sync."
        )
    try:
        current_guidance = collect_context_guidance(plan.target, discovery.owners)
    except OperationError as exc:
        raise OperationError(
            "Focused context guidance changed after preflight; rerun context-index sync."
        ) from exc
    if current_guidance != plan.owner_guidance:
        raise OperationError(
            "Focused context guidance changed after preflight; rerun context-index sync."
        )

    destination = plan.destination
    if plan.action in {"create", "not_needed"}:
        obstruction = _first_structural_obstruction(destination, plan.target)
        if obstruction is not None:
            raise OperationError("Context-index target structure changed after preflight.")
        if _link_kind(destination) is not None or destination.exists():
            raise OperationError(
                f"Context index appeared after preflight: {plan.relative_path}"
            )
        return

    if plan.action in {"update", "no_changes"}:
        content, identity = _regular_file_observation(
            destination,
            label="Context index",
        )
        if identity != plan.original_identity or content != plan.original_content:
            raise OperationError(
                f"Context index changed after preflight; rerun the plan: {destination}"
            )


def _replace_file_if_unchanged(
    path: Path,
    *,
    original: bytes,
    original_identity: tuple[int, int],
    planned: bytes,
) -> None:
    current, current_identity = _regular_file_observation(path, label="Context index")
    if current_identity != original_identity or current != original:
        raise OperationError(f"Context index changed after preflight; rerun the plan: {path}")

    temporary_path: Path | None = None
    temporary_identity: tuple[int, int] | None = None
    planned_sha256 = hashlib.sha256(planned).hexdigest()
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            created = os.fstat(handle.fileno())
            temporary_identity = (created.st_dev, created.st_ino)
            handle.write(planned)
            handle.flush()
            os.fsync(handle.fileno())
        shutil.copystat(path, temporary_path, follow_symlinks=False)

        staged, staged_identity = _regular_file_observation(
            temporary_path,
            label="Staged context index",
        )
        if staged_identity != temporary_identity or staged != planned:
            raise OperationError("Staged context index changed before replacement.")
        current, current_identity = _regular_file_observation(
            path,
            label="Context index",
        )
        if current_identity != original_identity or current != original:
            raise OperationError(
                f"Context index changed during apply; rerun the plan: {path}"
            )
        os.replace(temporary_path, path)
        temporary_path = None
    except Exception as exc:
        if temporary_path is not None and temporary_identity is not None:
            failure = _rollback_created_file(
                temporary_path,
                temporary_identity,
                planned_sha256,
            )
            if failure is not None:
                raise OperationError(
                    f"Context-index update failed ({exc}); temporary-file cleanup "
                    f"was incomplete: {failure}"
                ) from exc
        raise


def apply_index_sync(plan: IndexSyncPlan) -> IndexSyncResult:
    """Apply a safe index plan while changing only the generated inventory block."""

    _validate_index_sync_plan(plan)
    if plan.conflicts or plan.action == "blocked":
        raise OperationError("Context-index operation is blocked; no file was changed.")
    _revalidate_index_sync_plan(plan)

    if plan.action in {"not_needed", "no_changes"}:
        return IndexSyncResult(
            target=plan.target,
            status=plan.action,
            action=plan.action,
            resource_bundle_sha256=plan.resource_bundle_sha256,
            specialized_owners=plan.specialized_owners,
            changed_files=(),
        )

    if plan.action == "update":
        assert plan.original_content is not None
        assert plan.original_identity is not None
        assert plan.planned_content is not None
        _replace_file_if_unchanged(
            plan.destination,
            original=plan.original_content,
            original_identity=plan.original_identity,
            planned=plan.planned_content,
        )
        return IndexSyncResult(
            target=plan.target,
            status="updated",
            action=plan.action,
            resource_bundle_sha256=plan.resource_bundle_sha256,
            specialized_owners=plan.specialized_owners,
            changed_files=(plan.relative_path,),
        )

    assert plan.planned_content is not None
    created_directories: list[Path] = []
    created_files: list[tuple[Path, tuple[int, int], str]] = []
    try:
        _create_parent_directories(
            plan.destination.parent,
            plan.target,
            created_directories,
        )
        identity = _write_bytes_exclusively(
            plan.planned_content,
            plan.destination,
            operation="Context-index",
        )
        assert plan.planned_sha256 is not None
        created_files.append((plan.destination, identity, plan.planned_sha256))
    except Exception as exc:
        rollback_failures: list[str] = []
        for path, identity, expected_sha256 in reversed(created_files):
            failure = _rollback_created_file(path, identity, expected_sha256)
            if failure is not None:
                rollback_failures.append(failure)
        for directory in reversed(created_directories):
            try:
                directory.rmdir()
            except FileNotFoundError:
                pass
            except OSError as rollback_exc:
                rollback_failures.append(f"{directory}: {rollback_exc}")
        if rollback_failures:
            raise OperationError(
                f"Context-index creation failed ({exc}); rollback was incomplete: "
                + "; ".join(rollback_failures)
            ) from exc
        raise

    return IndexSyncResult(
        target=plan.target,
        status="created",
        action=plan.action,
        resource_bundle_sha256=plan.resource_bundle_sha256,
        specialized_owners=plan.specialized_owners,
        changed_files=(plan.relative_path,),
    )
