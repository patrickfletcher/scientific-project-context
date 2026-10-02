#!/usr/bin/env python3
"""Verify built package artifacts without installing them.

The check compares both wheels and the source distribution with the current
authoritative source trees.  It intentionally uses only the Python standard
library so artifact verification does not add a project runtime dependency.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import configparser
import csv
import hashlib
import hmac
import io
import json
import os
import re
import stat
import tarfile
import zipfile
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence


DISTRIBUTION_NAME = "scientific-project-context"
IMPORT_PACKAGE = "scientific_project_context"
RESOURCE_PACKAGE = "_scientific_project_context_resources"
# The normalized form packaging emits for `>=3.10,<3.15`; changing the supported
# range is a reviewed decision, so this stays a literal rather than a lookup.
EXPECTED_PYTHON = "<3.15,>=3.10"
EXPECTED_SCRIPTS = {"spctx": "scientific_project_context.cli:main"}
PROJECT_ONLY_ROOTS = frozenset({".agent", ".context", "tests", "tools"})
WHEEL_FORBIDDEN_ROOTS = PROJECT_ONLY_ROOTS | frozenset({"template"})
SKIPPED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hatch",
        ".hg",
        ".mypy_cache",
        ".nox",
        ".pixi",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
    }
)
SKIPPED_FILES = frozenset({".DS_Store", ".git"})
EXPECTED_DIST_INFO_FILES = frozenset(
    {"METADATA", "RECORD", "WHEEL", "entry_points.txt", "licenses/LICENSE"}
)


class ArtifactError(RuntimeError):
    """A package artifact violates the declared contract."""


@dataclass(frozen=True)
class SourceContract:
    code_files: Mapping[str, bytes]
    resource_files: Mapping[str, bytes]
    resource_ids: Mapping[str, bytes]
    sdist_files: Mapping[str, bytes]
    resource_bundle_sha256: str


@dataclass(frozen=True)
class WheelInspection:
    path: Path
    artifact_sha256: str
    files: Mapping[str, bytes]
    metadata: Mapping[str, object]
    wheel_metadata: Mapping[str, object]
    scripts: Mapping[str, str]


@dataclass(frozen=True)
class SdistInspection:
    path: Path
    artifact_sha256: str
    files: Mapping[str, bytes]
    metadata: Mapping[str, object]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_link_or_reparse(stat_result: os.stat_result) -> bool:
    if stat.S_ISLNK(stat_result.st_mode):
        return True
    attributes = getattr(stat_result, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    return bool(attributes & reparse_flag)


def _require_plain_file(path: Path, label: str) -> Path:
    try:
        stat_result = path.lstat()
    except OSError as exc:
        raise ArtifactError(f"{label} is unavailable: {path}: {exc}") from exc
    if _is_link_or_reparse(stat_result) or not stat.S_ISREG(stat_result.st_mode):
        raise ArtifactError(f"{label} must be a regular non-link file: {path}")
    return path.resolve()


def _collect_tree(root: Path, *, prefix: str, skip_build_noise: bool) -> dict[str, bytes]:
    try:
        root_stat = root.lstat()
    except OSError as exc:
        raise ArtifactError(f"Required source directory is unavailable: {root}: {exc}") from exc
    if _is_link_or_reparse(root_stat) or not stat.S_ISDIR(root_stat.st_mode):
        raise ArtifactError(f"Required source path is not a plain directory: {root}")

    files: dict[str, bytes] = {}

    def visit(directory: Path, relative_parts: tuple[str, ...]) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            raise ArtifactError(f"Cannot inspect source directory {directory}: {exc}") from exc
        names = [entry.name for entry in entries]
        if len(names) != len(set(names)):
            raise ArtifactError(f"Source directory has duplicate child names: {directory}")

        for entry in entries:
            try:
                entry_stat = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise ArtifactError(f"Cannot inspect source path {entry.path}: {exc}") from exc
            relative = relative_parts + (entry.name,)
            display = "/".join(relative)
            if _is_link_or_reparse(entry_stat):
                raise ArtifactError(f"Source trees cannot contain links: {display}")
            if stat.S_ISDIR(entry_stat.st_mode):
                if skip_build_noise and (
                    entry.name in SKIPPED_DIRECTORIES
                    or entry.name.endswith(".egg-info")
                ):
                    continue
                visit(Path(entry.path), relative)
            elif stat.S_ISREG(entry_stat.st_mode):
                if entry.name in SKIPPED_FILES:
                    continue
                if skip_build_noise and Path(entry.name).suffix in {".pyc", ".pyd", ".pyo"}:
                    continue
                archive_path = "/".join(part for part in (prefix, display) if part)
                files[archive_path] = Path(entry.path).read_bytes()
            else:
                raise ArtifactError(f"Source path is not a regular file or directory: {display}")

    visit(root, ())
    return dict(sorted(files.items()))


def _bundle_sha256(resource_ids: Mapping[str, bytes]) -> str:
    digest = hashlib.sha256()
    for resource_id, content in sorted(resource_ids.items()):
        identifier = resource_id.encode("utf-8")
        for value in (identifier, content):
            digest.update(len(value).to_bytes(8, byteorder="big", signed=False))
            digest.update(value)
    return digest.hexdigest()


def load_source_contract(source_root: Path) -> SourceContract:
    source_root = source_root.resolve()
    code_root = source_root / "src" / IMPORT_PACKAGE
    src_root = source_root / "src"
    template_root = source_root / "template"

    code_files = _collect_tree(
        code_root,
        prefix=IMPORT_PACKAGE,
        skip_build_noise=True,
    )
    all_src_files = _collect_tree(src_root, prefix="src", skip_build_noise=True)
    template_sources = _collect_tree(
        template_root,
        prefix="template",
        skip_build_noise=False,
    )
    if not code_files:
        raise ArtifactError("The import package contains no source files.")
    if not template_sources:
        raise ArtifactError("The template source tree must contain files.")

    resource_ids = dict(template_sources)
    resource_files = {
        f"{RESOURCE_PACKAGE}/{resource_id}": content
        for resource_id, content in resource_ids.items()
    }
    required_root_files: dict[str, bytes] = {}
    for relative_path in (".gitignore", "LICENSE", "README.md", "pyproject.toml"):
        path = _require_plain_file(source_root / relative_path, f"Source {relative_path}")
        required_root_files[relative_path] = path.read_bytes()

    sdist_files = {
        **all_src_files,
        **template_sources,
        **required_root_files,
    }
    return SourceContract(
        code_files=code_files,
        resource_files=dict(sorted(resource_files.items())),
        resource_ids=dict(sorted(resource_ids.items())),
        sdist_files=dict(sorted(sdist_files.items())),
        resource_bundle_sha256=_bundle_sha256(resource_ids),
    )


def _validate_archive_path(name: str, label: str) -> PurePosixPath:
    if not name or name.startswith("/") or "\\" in name:
        raise ArtifactError(f"{label} has a non-canonical member path: {name!r}")
    path = PurePosixPath(name)
    if str(path) != name or any(part in {"", ".", ".."} for part in path.parts):
        raise ArtifactError(f"{label} has a non-canonical member path: {name!r}")
    return path


def _metadata_semantics(data: bytes, label: str) -> dict[str, object]:
    message = BytesParser(policy=policy.default).parsebytes(data)
    if message.defects:
        raise ArtifactError(f"{label} contains malformed metadata: {message.defects!r}")
    name = message.get("Name")
    version = message.get("Version")
    requires_python = message.get("Requires-Python")
    requirements = tuple(sorted(message.get_all("Requires-Dist", [])))
    if name != DISTRIBUTION_NAME:
        raise ArtifactError(f"{label} has unexpected Name: {name!r}")
    if not version:
        raise ArtifactError(f"{label} has no Version field.")
    if requires_python != EXPECTED_PYTHON:
        raise ArtifactError(
            f"{label} has unexpected Requires-Python: {requires_python!r}"
        )
    if requirements:
        raise ArtifactError(f"{label} declares runtime dependencies: {requirements!r}")
    return {
        "name": name,
        "version": version,
        "requires_python": requires_python,
        "requires_dist": requirements,
    }


def _wheel_metadata_semantics(data: bytes, label: str) -> dict[str, object]:
    message = BytesParser(policy=policy.default).parsebytes(data)
    if message.defects:
        raise ArtifactError(f"{label} contains malformed WHEEL metadata.")
    wheel_version = message.get("Wheel-Version")
    pure = message.get("Root-Is-Purelib")
    tags = tuple(sorted(message.get_all("Tag", [])))
    if wheel_version != "1.0" or pure != "true" or tags != ("py3-none-any",):
        raise ArtifactError(
            f"{label} has unexpected wheel semantics: "
            f"Wheel-Version={wheel_version!r}, Root-Is-Purelib={pure!r}, Tags={tags!r}"
        )
    return {"wheel_version": wheel_version, "pure": pure, "tags": tags}


def _script_semantics(data: bytes, label: str) -> dict[str, str]:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    try:
        parser.read_string(data.decode("utf-8"))
    except (UnicodeDecodeError, configparser.Error) as exc:
        raise ArtifactError(f"{label} has malformed entry-point metadata: {exc}") from exc
    if parser.sections() != ["console_scripts"]:
        raise ArtifactError(f"{label} must contain only [console_scripts].")
    scripts = dict(parser.items("console_scripts"))
    if scripts != EXPECTED_SCRIPTS:
        raise ArtifactError(f"{label} has unexpected console scripts: {scripts!r}")
    return scripts


def _normalized_component(value: str) -> str:
    return re.sub(r"[^\w\d.]+", "_", value, flags=re.UNICODE)


def _verify_record(files: Mapping[str, bytes], record_path: str, label: str) -> None:
    try:
        text = files[record_path].decode("utf-8")
        rows = list(csv.reader(io.StringIO(text, newline="")))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ArtifactError(f"{label} has an unreadable RECORD: {exc}") from exc

    records: dict[str, tuple[str, str]] = {}
    for row in rows:
        if len(row) != 3:
            raise ArtifactError(f"{label} RECORD contains a malformed row: {row!r}")
        path, hash_field, size_field = row
        _validate_archive_path(path, f"{label} RECORD")
        if path in records:
            raise ArtifactError(f"{label} RECORD repeats {path!r}.")
        records[path] = (hash_field, size_field)

    if set(records) != set(files):
        missing = sorted(set(files) - set(records))
        unexpected = sorted(set(records) - set(files))
        raise ArtifactError(
            f"{label} RECORD membership differs from the wheel "
            f"(missing={missing!r}, unexpected={unexpected!r})."
        )
    if records[record_path] != ("", ""):
        raise ArtifactError(f"{label} RECORD must leave its own hash and size blank.")

    for path, content in files.items():
        if path == record_path:
            continue
        hash_field, size_field = records[path]
        try:
            algorithm, encoded = hash_field.split("=", 1)
            padding = "=" * (-len(encoded) % 4)
            recorded_digest = base64.urlsafe_b64decode(encoded + padding)
        except (ValueError, binascii.Error) as exc:
            raise ArtifactError(f"{label} RECORD has an invalid hash for {path}.") from exc
        if algorithm != "sha256" or not hmac.compare_digest(
            recorded_digest, hashlib.sha256(content).digest()
        ):
            raise ArtifactError(f"{label} RECORD hash does not match {path}.")
        if not size_field.isdecimal() or int(size_field) != len(content):
            raise ArtifactError(f"{label} RECORD size does not match {path}.")


def _assert_exact_bytes(
    actual: Mapping[str, bytes],
    expected: Mapping[str, bytes],
    label: str,
) -> None:
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    if missing or unexpected:
        raise ArtifactError(
            f"{label} membership is not exact "
            f"(missing={missing!r}, unexpected={unexpected!r})."
        )
    differing = sorted(path for path, content in expected.items() if actual[path] != content)
    if differing:
        raise ArtifactError(f"{label} bytes differ from source: {differing!r}")


def inspect_wheel(path: Path, contract: SourceContract, label: str) -> WheelInspection:
    path = _require_plain_file(path, label)
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise ArtifactError(f"{label} contains duplicate members.")
            files: dict[str, bytes] = {}
            for info in infos:
                if info.is_dir():
                    raise ArtifactError(f"{label} contains an explicit directory member: {info.filename}")
                _validate_archive_path(info.filename, label)
                mode = (info.external_attr >> 16) & 0xFFFF
                if mode and stat.S_ISLNK(mode):
                    raise ArtifactError(f"{label} contains a symbolic link: {info.filename}")
                files[info.filename] = archive.read(info)
    except zipfile.BadZipFile as exc:
        raise ArtifactError(f"{label} is not a readable wheel: {exc}") from exc

    metadata_paths = [
        name
        for name in files
        if name.count("/") == 1 and name.endswith(".dist-info/METADATA")
    ]
    if len(metadata_paths) != 1:
        raise ArtifactError(f"{label} must contain exactly one dist-info/METADATA file.")
    metadata_path = metadata_paths[0]
    metadata = _metadata_semantics(files[metadata_path], f"{label} METADATA")
    dist_info = metadata_path.rsplit("/", 1)[0]
    expected_dist_info = (
        f"{_normalized_component(str(metadata['name']))}-{metadata['version']}.dist-info"
    )
    if dist_info != expected_dist_info:
        raise ArtifactError(
            f"{label} dist-info path is {dist_info!r}; expected {expected_dist_info!r}."
        )
    expected_filename_prefix = expected_dist_info.removesuffix(".dist-info") + "-"
    if not path.name.startswith(expected_filename_prefix) or not path.name.endswith(".whl"):
        raise ArtifactError(f"{label} filename does not match its metadata: {path.name}")

    metadata_members = {f"{dist_info}/{name}" for name in EXPECTED_DIST_INFO_FILES}
    expected_members = set(contract.code_files) | set(contract.resource_files) | metadata_members
    missing = sorted(expected_members - set(files))
    unexpected = sorted(set(files) - expected_members)
    if missing or unexpected:
        raise ArtifactError(
            f"{label} membership is not exact "
            f"(missing={missing!r}, unexpected={unexpected!r})."
        )
    forbidden = sorted(
        name for name in files if PurePosixPath(name).parts[0] in WHEEL_FORBIDDEN_ROOTS
    )
    if forbidden:
        raise ArtifactError(f"{label} includes project-only roots: {forbidden!r}")

    _assert_exact_bytes(
        {name: files[name] for name in contract.code_files},
        contract.code_files,
        f"{label} code",
    )
    _assert_exact_bytes(
        {name: files[name] for name in contract.resource_files},
        contract.resource_files,
        f"{label} resources",
    )
    scripts_path = f"{dist_info}/entry_points.txt"
    wheel_path = f"{dist_info}/WHEEL"
    record_path = f"{dist_info}/RECORD"
    scripts = _script_semantics(files[scripts_path], f"{label} entry_points.txt")
    wheel_metadata = _wheel_metadata_semantics(files[wheel_path], f"{label} WHEEL")
    _verify_record(files, record_path, label)
    return WheelInspection(
        path=path,
        artifact_sha256=_sha256_file(path),
        files=dict(sorted(files.items())),
        metadata=metadata,
        wheel_metadata=wheel_metadata,
        scripts=scripts,
    )


def inspect_sdist(
    path: Path,
    contract: SourceContract,
    expected_metadata: Mapping[str, object],
) -> SdistInspection:
    label = "Source distribution"
    path = _require_plain_file(path, label)
    try:
        with tarfile.open(path, mode="r:gz") as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            if len(names) != len(set(names)):
                raise ArtifactError(f"{label} contains duplicate members.")
            raw_files: dict[str, bytes] = {}
            for member in members:
                _validate_archive_path(member.name, label)
                if not member.isfile():
                    raise ArtifactError(
                        f"{label} contains a non-regular member: {member.name}"
                    )
                handle = archive.extractfile(member)
                if handle is None:
                    raise ArtifactError(f"{label} member cannot be read: {member.name}")
                raw_files[member.name] = handle.read()
    except tarfile.TarError as exc:
        raise ArtifactError(f"{label} is not a readable tar.gz archive: {exc}") from exc

    roots = {PurePosixPath(name).parts[0] for name in raw_files}
    if len(roots) != 1:
        raise ArtifactError(f"{label} must contain one top-level directory: {sorted(roots)!r}")
    root = next(iter(roots))
    expected_root = (
        f"{_normalized_component(str(expected_metadata['name']))}-{expected_metadata['version']}"
    )
    if root != expected_root:
        raise ArtifactError(f"{label} root is {root!r}; expected {expected_root!r}.")
    if path.name != f"{expected_root}.tar.gz":
        raise ArtifactError(f"{label} filename does not match its metadata: {path.name}")

    files = {
        "/".join(PurePosixPath(name).parts[1:]): content
        for name, content in raw_files.items()
    }
    expected_members = set(contract.sdist_files) | {"PKG-INFO"}
    missing = sorted(expected_members - set(files))
    unexpected = sorted(set(files) - expected_members)
    if missing or unexpected:
        raise ArtifactError(
            f"{label} membership is not exact "
            f"(missing={missing!r}, unexpected={unexpected!r})."
        )
    forbidden = sorted(
        name for name in files if PurePosixPath(name).parts[0] in PROJECT_ONLY_ROOTS
    )
    if forbidden:
        raise ArtifactError(f"{label} includes project-only roots: {forbidden!r}")
    _assert_exact_bytes(
        {name: files[name] for name in contract.sdist_files},
        contract.sdist_files,
        label,
    )
    metadata = _metadata_semantics(files["PKG-INFO"], "Source distribution PKG-INFO")
    if metadata != expected_metadata:
        raise ArtifactError(
            "Source distribution metadata differs semantically from the direct wheel."
        )
    return SdistInspection(
        path=path,
        artifact_sha256=_sha256_file(path),
        files=dict(sorted(files.items())),
        metadata=metadata,
    )


def verify_artifacts(
    source_root: Path,
    direct_wheel: Path,
    sdist: Path,
    sdist_wheel: Path,
) -> dict[str, object]:
    contract = load_source_contract(source_root)
    direct = inspect_wheel(direct_wheel, contract, "Direct wheel")
    source_distribution = inspect_sdist(sdist, contract, direct.metadata)
    rebuilt = inspect_wheel(sdist_wheel, contract, "Source-distribution-built wheel")

    if (
        rebuilt.metadata != direct.metadata
        or rebuilt.wheel_metadata != direct.wheel_metadata
        or rebuilt.scripts != direct.scripts
    ):
        raise ArtifactError(
            "Direct and source-distribution-built wheels are not semantically equivalent."
        )
    semantic_members = set(contract.code_files) | set(contract.resource_files)
    differing = sorted(
        name for name in semantic_members if direct.files[name] != rebuilt.files[name]
    )
    if differing:
        raise ArtifactError(
            "Direct and source-distribution-built wheel payloads differ: " + repr(differing)
        )

    return {
        "result": "pass",
        "artifacts": {
            "direct_wheel": {
                "path": str(direct.path),
                "sha256": direct.artifact_sha256,
                "members": len(direct.files),
            },
            "sdist": {
                "path": str(source_distribution.path),
                "sha256": source_distribution.artifact_sha256,
                "members": len(source_distribution.files),
            },
            "sdist_wheel": {
                "path": str(rebuilt.path),
                "sha256": rebuilt.artifact_sha256,
                "members": len(rebuilt.files),
            },
        },
        "distribution": {
            "name": direct.metadata["name"],
            "version": direct.metadata["version"],
        },
        "resource_bundle_sha256": contract.resource_bundle_sha256,
        "summary": {
            "code_files": len(contract.code_files),
            "resource_files": len(contract.resource_files),
            "runtime_dependencies": 0,
        },
    }


def _failure_report(args: argparse.Namespace, message: str) -> dict[str, object]:
    artifacts: dict[str, object] = {}
    for key, raw_path in (
        ("direct_wheel", args.direct_wheel),
        ("sdist", args.sdist),
        ("sdist_wheel", args.sdist_wheel),
    ):
        path = Path(raw_path)
        digest: str | None = None
        try:
            if path.is_file() and not path.is_symlink():
                digest = _sha256_file(path)
        except OSError:
            pass
        artifacts[key] = {"path": str(path), "sha256": digest}

    resource_digest: str | None = None
    try:
        resource_digest = load_source_contract(Path(args.source_root)).resource_bundle_sha256
    except (ArtifactError, OSError):
        pass
    return {
        "result": "fail",
        "artifacts": artifacts,
        "resource_bundle_sha256": resource_digest,
        "errors": [message],
    }


def _print_human(report: Mapping[str, object]) -> None:
    if report["result"] == "fail":
        print("Package artifact check: FAIL")
        for error in report.get("errors", []):
            print(f"- {error}")
        return

    artifacts = report["artifacts"]
    assert isinstance(artifacts, Mapping)
    distribution = report["distribution"]
    assert isinstance(distribution, Mapping)
    print("Package artifact check: PASS")
    print(f"- Distribution: {distribution['name']} {distribution['version']}")
    for key, label in (
        ("direct_wheel", "Direct wheel"),
        ("sdist", "Source distribution"),
        ("sdist_wheel", "Source-distribution-built wheel"),
    ):
        artifact = artifacts[key]
        assert isinstance(artifact, Mapping)
        print(f"- {label}: sha256={artifact['sha256']} ({artifact['members']} files)")
    print(f"- Resource bundle: sha256={report['resource_bundle_sha256']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--direct-wheel", required=True, type=Path)
    parser.add_argument("--sdist", required=True, type=Path)
    parser.add_argument("--sdist-wheel", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = verify_artifacts(
            args.source_root,
            args.direct_wheel,
            args.sdist,
            args.sdist_wheel,
        )
        exit_status = 0
    except Exception as exc:
        report = _failure_report(args, str(exc))
        exit_status = 2

    if args.json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_human(report)
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
