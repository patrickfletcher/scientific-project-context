"""Measure the context for a review, and find every file that names a context document.

`spctx check --inventory` runs this. It reports counts and references, never
findings: the numbers inform a review the user asked for, and a size line in
every report would invite trimming for its own sake.
"""

from __future__ import annotations

import os
import posixpath
import re
import stat
from dataclasses import dataclass
from pathlib import Path

from .health import (
    FENCED_CODE_RE,
    HISTORY_POINTER_RE,
    LINK_TARGET_RE,
    _is_gitignored,
    _link_kind,
    _walk_plain_files,
    read_text,
    rel,
)
from .project import CONTEXT_INDEX_PATH, read_context_guidance_lines

# Directories that hold tools or caches rather than project text.
SKIPPED_DIRECTORIES = frozenset(
    {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv", ".tox",
     ".mypy_cache", ".pytest_cache", ".ipynb_checkpoints"}
)
MAX_FILES = 20_000
MAX_FILE_BYTES = 1_000_000
MAX_MISSING = 50
CONTEXT_NAME_RE = re.compile(r"(?<![A-Za-z0-9_./-])\.context/[A-Za-z0-9_./-]*[A-Za-z0-9_-]\.md\b")
ISO_DATE_RE = re.compile(r"\b(?:19|20)\d\d-[01]\d-[0-3]\d\b")


@dataclass(frozen=True, slots=True)
class ContextDocument:
    path: str
    words: int
    sections: int
    update_when: str | None
    dated_lines: int
    links_out: int
    named_by: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MissingContextName:
    path: str
    line: int
    target: str


@dataclass(frozen=True, slots=True)
class ContextInventory:
    documents: tuple[ContextDocument, ...]
    missing: tuple[MissingContextName, ...]
    files_scanned: int
    scan_limited: bool


def _project_text_files(root: Path) -> tuple[list[Path], bool]:
    """Regular, non-ignored, plausibly textual files, without following links."""

    found: list[Path] = []
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError:
            continue
        for entry in entries:
            try:
                entry_stat = entry.stat(follow_symlinks=False)
            except OSError:
                continue
            path = Path(entry.path)
            if stat.S_ISLNK(entry_stat.st_mode) or _link_kind(path) is not None:
                continue
            relative = rel(path, root)
            if stat.S_ISDIR(entry_stat.st_mode):
                if entry.name in SKIPPED_DIRECTORIES or _is_gitignored(root, relative, is_directory=True):
                    continue
                pending.append(path)
            elif stat.S_ISREG(entry_stat.st_mode):
                if entry_stat.st_size > MAX_FILE_BYTES or _is_gitignored(root, relative):
                    continue
                found.append(path)
                if len(found) >= MAX_FILES:
                    return found, True
    return sorted(found), False


def _named_context_paths(path: Path, root: Path, text: str) -> list[tuple[int, str]]:
    """Context documents a file names, by repository path or by Markdown link."""

    names: list[tuple[int, str]] = []
    is_markdown = path.suffix.casefold() == ".md"
    directory = posixpath.dirname(rel(path, root))
    for number, line in enumerate(text.splitlines(), start=1):
        if HISTORY_POINTER_RE.search(line):
            continue
        for match in CONTEXT_NAME_RE.finditer(line):
            names.append((number, posixpath.normpath(match.group(0))))
        if is_markdown:
            for match in LINK_TARGET_RE.finditer(line):
                target = match.group(1).split("#", 1)[0]
                if not target or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("/"):
                    continue
                resolved = posixpath.normpath(posixpath.join(directory, target))
                if resolved.startswith(".context/") and resolved.casefold().endswith(".md"):
                    names.append((number, resolved))
    return names


def inspect_context_inventory(root: Path) -> ContextInventory:
    files, limited = _project_text_files(root)
    named_by: dict[str, set[str]] = {}
    missing: list[MissingContextName] = []
    for path in files:
        source = rel(path, root)
        if source == CONTEXT_INDEX_PATH:
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\0" in raw[:8192]:
            continue
        text = raw.decode("utf-8", errors="replace")
        for number, target in _named_context_paths(path, root, text):
            if target == source:
                continue
            if os.path.lexists(root / target):
                named_by.setdefault(target, set()).add(source)
            elif not _is_gitignored(root, target) and len(missing) < MAX_MISSING:
                missing.append(MissingContextName(source, number, target))

    documents: list[ContextDocument] = []
    design_root = root / ".context"
    if design_root.is_dir() and _link_kind(design_root) is None:
        for path in _walk_plain_files(design_root):
            relative = rel(path, root)
            if path.suffix.casefold() != ".md" or relative == CONTEXT_INDEX_PATH:
                continue
            try:
                text = read_text(path)
            except OSError:
                continue
            prose = FENCED_CODE_RE.sub("", text)
            lines = prose.splitlines()
            documents.append(
                ContextDocument(
                    path=relative,
                    words=len(text.split()),
                    sections=sum(line.startswith("## ") for line in lines),
                    update_when=read_context_guidance_lines(text).get("Update when"),
                    dated_lines=sum(bool(ISO_DATE_RE.search(line)) for line in lines),
                    links_out=sum(len(LINK_TARGET_RE.findall(line)) for line in lines),
                    named_by=tuple(sorted(named_by.get(relative, ()))),
                )
            )
    return ContextInventory(
        documents=tuple(sorted(documents, key=lambda item: item.path)),
        missing=tuple(missing),
        files_scanned=len(files),
        scan_limited=limited,
    )
