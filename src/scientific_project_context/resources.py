"""Load and identify the immutable resources shipped with the package.

The installed catalog is read through :mod:`importlib.resources`.  Callers may
also provide filesystem-backed ``Traversable`` roots explicitly, which keeps
tests and build verification independent of a source checkout fallback.
"""

from __future__ import annotations

import hashlib
import stat
from dataclasses import dataclass
from importlib import resources as importlib_resources
from pathlib import Path
from typing import Iterable

try:  # `importlib.abc.Traversable` was removed in Python 3.14.
    from importlib.resources.abc import Traversable
except ImportError:  # Python 3.10
    from importlib.abc import Traversable  # type: ignore[attr-defined, no-redef]


RESOURCE_PACKAGE = "_scientific_project_context_resources"

# The files `init` places into a project.
STARTER_INVENTORY = tuple(
    sorted(
        (
            "AGENTS.md",
            ".agents/skills/spctx-project-context/SKILL.md",
            ".agents/skills/spctx-public-writing/SKILL.md",
            ".agents/skills/spctx-scientific-change/SKILL.md",
            ".context/project.md",
            ".context/scientific-practice.md",
        )
    )
)

# The context index is packaged but written only by `sync-index`, once a project
# has enough focused documents for a router to be worth having.
CONTEXT_INDEX_PATH = ".context/README.md"

TEMPLATE_INVENTORY = tuple(sorted((*STARTER_INVENTORY, CONTEXT_INDEX_PATH)))

TEMPLATE_RESOURCE_IDS = tuple(f"template/{path}" for path in TEMPLATE_INVENTORY)
CONTEXT_INDEX_RESOURCE_ID = f"template/{CONTEXT_INDEX_PATH}"


class ResourceError(RuntimeError):
    """The installed or injected resource bundle is incomplete or unsafe."""


@dataclass(frozen=True, slots=True)
class ResourceEntry:
    """One byte-exact resource with a stable, bundle-relative identity."""

    resource_id: str
    collection: str
    relative_path: str
    content: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class ResourceCatalog:
    """The exact packaged Markdown inventory for one artifact."""

    template_entries: tuple[ResourceEntry, ...]
    bundle_sha256: str

    def __post_init__(self) -> None:
        _validate_catalog_entries(
            self.template_entries,
            collection="template",
            expected_paths=TEMPLATE_INVENTORY,
        )
        expected_digest = calculate_bundle_sha256(self.entries)
        if self.bundle_sha256 != expected_digest:
            raise ValueError(
                "Resource catalog bundle digest does not match its entries: "
                f"expected {expected_digest}, got {self.bundle_sha256}."
            )

    @property
    def entries(self) -> tuple[ResourceEntry, ...]:
        """Return all entries in stable resource-ID order."""

        return tuple(
            sorted(self.template_entries, key=lambda entry: entry.resource_id)
        )

    @property
    def starter_entries(self) -> tuple[ResourceEntry, ...]:
        """Return only the entries `init` places into a project."""

        return tuple(
            entry
            for entry in self.entries
            if entry.relative_path in STARTER_INVENTORY
        )

    def get(self, resource_id: str) -> ResourceEntry:
        """Return one resource by stable ID, or raise ``KeyError``."""

        for entry in self.entries:
            if entry.resource_id == resource_id:
                return entry
        raise KeyError(resource_id)


def _validate_catalog_entries(
    entries: tuple[ResourceEntry, ...],
    *,
    collection: str,
    expected_paths: tuple[str, ...],
) -> None:
    expected_ids = tuple(f"{collection}/{path}" for path in expected_paths)
    actual_ids = tuple(entry.resource_id for entry in entries)
    if actual_ids != expected_ids:
        raise ValueError(
            f"{collection} catalog IDs must be exact and sorted; "
            f"expected {expected_ids!r}, got {actual_ids!r}."
        )

    for entry, expected_path in zip(entries, expected_paths):
        if entry.collection != collection or entry.relative_path != expected_path:
            raise ValueError(f"Malformed resource entry: {entry.resource_id!r}.")
        if type(entry.content) is not bytes:
            raise TypeError(f"Resource content must be bytes: {entry.resource_id}.")
        expected_sha256 = hashlib.sha256(entry.content).hexdigest()
        if entry.sha256 != expected_sha256:
            raise ValueError(
                f"Resource digest does not match its content: {entry.resource_id}."
            )


def calculate_bundle_sha256(entries: Iterable[ResourceEntry]) -> str:
    """Hash sorted IDs and contents using unsigned 64-bit big-endian framing.

    Each UTF-8 resource ID and each byte payload is preceded by its byte length.
    Framing both values makes the digest unambiguous without a second manually
    maintained resource version.
    """

    ordered = sorted(entries, key=lambda entry: entry.resource_id)
    resource_ids = [entry.resource_id for entry in ordered]
    if len(resource_ids) != len(set(resource_ids)):
        raise ValueError("Resource IDs must be unique when calculating a bundle digest.")

    digest = hashlib.sha256()
    for entry in ordered:
        identifier = entry.resource_id.encode("utf-8")
        for value in (identifier, entry.content):
            digest.update(len(value).to_bytes(8, byteorder="big", signed=False))
            digest.update(value)
    return digest.hexdigest()


def _link_kind(resource: Traversable) -> str | None:
    """Return a filesystem link kind when the Traversable exposes one."""

    is_symlink = getattr(resource, "is_symlink", None)
    if callable(is_symlink) and is_symlink():
        return "symlink"

    is_junction = getattr(resource, "is_junction", None)
    if callable(is_junction) and is_junction():
        return "junction"

    lstat = getattr(resource, "lstat", None)
    if not callable(lstat):
        return None
    try:
        attributes = getattr(lstat(), "st_file_attributes", 0)
    except (FileNotFoundError, NotADirectoryError):
        return None
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    return "reparse point" if attributes & reparse_flag else None


def _walk_files(root: Traversable) -> tuple[tuple[str, Traversable], ...]:
    if _link_kind(root) is not None:
        raise ResourceError("A resource collection root cannot be a link or reparse point.")
    if not root.is_dir():
        raise ResourceError("A resource collection root is missing or is not a directory.")

    found: list[tuple[str, Traversable]] = []

    def visit(directory: Traversable, parent_parts: tuple[str, ...]) -> None:
        children = sorted(directory.iterdir(), key=lambda child: child.name)
        names = [child.name for child in children]
        if len(names) != len(set(names)):
            raise ResourceError("A resource directory contains duplicate child names.")

        for child in children:
            if (
                child.name in {"", ".", ".."}
                or "/" in child.name
                or "\\" in child.name
            ):
                raise ResourceError(f"Invalid resource path component: {child.name!r}.")
            relative_parts = parent_parts + (child.name,)
            relative_path = "/".join(relative_parts)
            link_kind = _link_kind(child)
            if link_kind is not None:
                raise ResourceError(
                    f"Resource collections cannot contain a {link_kind}: {relative_path}."
                )
            if child.is_dir():
                visit(child, relative_parts)
            elif child.is_file():
                found.append((relative_path, child))
            else:
                raise ResourceError(
                    f"Resource path is neither a regular file nor a directory: {relative_path}."
                )

    visit(root, ())
    return tuple(sorted(found, key=lambda item: item[0]))


def _load_collection(
    root: Traversable,
    *,
    collection: str,
    expected_paths: tuple[str, ...],
) -> tuple[ResourceEntry, ...]:
    files = _walk_files(root)
    actual_paths = tuple(path for path, _ in files)
    if actual_paths != expected_paths:
        missing = sorted(set(expected_paths) - set(actual_paths))
        unexpected = sorted(set(actual_paths) - set(expected_paths))
        details: list[str] = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise ResourceError(
            f"{collection} resource inventory is not exact (" + "; ".join(details) + ")."
        )

    entries: list[ResourceEntry] = []
    for relative_path, resource in files:
        with resource.open("rb") as handle:
            content = handle.read()
        if type(content) is not bytes:
            raise ResourceError(f"Resource reader did not return bytes: {relative_path}.")
        entries.append(
            ResourceEntry(
                resource_id=f"{collection}/{relative_path}",
                collection=collection,
                relative_path=relative_path,
                content=content,
                sha256=hashlib.sha256(content).hexdigest(),
            )
        )
    return tuple(entries)


def catalog_from_roots(template_root: Traversable) -> ResourceCatalog:
    """Load the exact catalog from an explicitly supplied Traversable root."""

    template_entries = _load_collection(
        template_root,
        collection="template",
        expected_paths=TEMPLATE_INVENTORY,
    )
    return ResourceCatalog(
        template_entries=template_entries,
        bundle_sha256=calculate_bundle_sha256(template_entries),
    )


def load_filesystem_resources(template_root: str | Path) -> ResourceCatalog:
    """Load an explicitly injected filesystem catalog, primarily for verification."""

    return catalog_from_roots(Path(template_root))


def load_packaged_resources() -> ResourceCatalog:
    """Load resources from the installed private data package.

    There is deliberately no source-checkout fallback.  Raw-source callers
    that need a catalog must inject the filesystem root explicitly.
    """

    try:
        package_root = importlib_resources.files(RESOURCE_PACKAGE)
    except (ModuleNotFoundError, TypeError) as exc:
        raise ResourceError(
            "Installed Scientific Project Context resources are unavailable; "
            "install or reinstall the package before running project operations."
        ) from exc
    return catalog_from_roots(package_root.joinpath("template"))
