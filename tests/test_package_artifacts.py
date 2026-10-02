from __future__ import annotations

import base64
import contextlib
import csv
import hashlib
import io
import json
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_package_artifacts as artifact_check  # noqa: E402


VERSION = "1.2.3"
WHEEL_NAME = f"scientific_project_context-{VERSION}-py3-none-any.whl"
SDIST_NAME = f"scientific_project_context-{VERSION}.tar.gz"
DIST_INFO = f"scientific_project_context-{VERSION}.dist-info"


class PackageArtifactVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.source = self.root / "source"
        self.direct_wheel = self.root / "direct" / WHEEL_NAME
        self.sdist = self.root / "sdist" / SDIST_NAME
        self.sdist_wheel = self.root / "rebuilt" / WHEEL_NAME
        self._write_source()

    def _write(self, relative_path: str, content: bytes) -> None:
        path = self.source / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def _write_source(self) -> None:
        self._write(".gitignore", b"dist/\n")
        self._write("LICENSE", b"Fixture license\n")
        self._write("README.md", b"# Fixture\n")
        self._write(
            "pyproject.toml",
            b"[project]\nname = 'scientific-project-context'\n",
        )
        self._write(
            "src/scientific_project_context/__init__.py",
            b'"""Fixture package."""\n',
        )
        self._write(
            "src/scientific_project_context/cli.py",
            b"def main():\n    return 0\n",
        )
        self._write("template/AGENTS.md", b"# Fixture instructions\n")
        self._write("template/.context/project.md", b"# Fixture project\n")
        self._write("template/.context/README.md", b"# Fixture index\n")

    @staticmethod
    def _metadata() -> bytes:
        return (
            "Metadata-Version: 2.4\n"
            "Name: scientific-project-context\n"
            f"Version: {VERSION}\n"
            f"Requires-Python: {artifact_check.EXPECTED_PYTHON}\n"
            "\n"
            "Fixture metadata.\n"
        ).encode("utf-8")

    def _wheel_payload(self, resource_override: bytes | None = None) -> dict[str, bytes]:
        contract = artifact_check.load_source_contract(self.source)
        payload = {**contract.code_files, **contract.resource_files}
        if resource_override is not None:
            resource_path = next(iter(contract.resource_files))
            payload[resource_path] = resource_override
        payload.update(
            {
                f"{DIST_INFO}/METADATA": self._metadata(),
                f"{DIST_INFO}/WHEEL": (
                    "Wheel-Version: 1.0\n"
                    "Generator: fixture\n"
                    "Root-Is-Purelib: true\n"
                    "Tag: py3-none-any\n"
                ).encode("utf-8"),
                f"{DIST_INFO}/entry_points.txt": (
                    "[console_scripts]\n"
                    "spctx = scientific_project_context.cli:main\n"
                ).encode("utf-8"),
                f"{DIST_INFO}/licenses/LICENSE": b"Fixture license\n",
            }
        )
        return payload

    def _write_wheel(
        self,
        path: Path,
        *,
        resource_override: bytes | None = None,
        corrupt_record: bool = False,
    ) -> None:
        payload = self._wheel_payload(resource_override)
        record_path = f"{DIST_INFO}/RECORD"
        rows: list[tuple[str, str, str]] = []
        for index, (name, content) in enumerate(sorted(payload.items())):
            digest = hashlib.sha256(content).digest()
            if corrupt_record and index == 0:
                digest = b"\x00" * len(digest)
            encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
            rows.append((name, f"sha256={encoded}", str(len(content))))
        rows.append((record_path, "", ""))
        record = io.StringIO(newline="")
        writer = csv.writer(record, lineterminator="\n")
        writer.writerows(rows)
        payload[record_path] = record.getvalue().encode("utf-8")

        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in sorted(payload.items()):
                archive.writestr(name, content)

    def _write_sdist(self) -> None:
        contract = artifact_check.load_source_contract(self.source)
        payload = {**contract.sdist_files, "PKG-INFO": self._metadata()}
        archive_root = f"scientific_project_context-{VERSION}"
        self.sdist.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(self.sdist, mode="w:gz") as archive:
            for name, content in sorted(payload.items()):
                info = tarfile.TarInfo(f"{archive_root}/{name}")
                info.size = len(content)
                info.mode = 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(content))

    def _create_valid_artifacts(self) -> None:
        self._write_wheel(self.direct_wheel)
        self._write_sdist()
        self._write_wheel(self.sdist_wheel)

    def _arguments(self) -> list[str]:
        return [
            "--source-root",
            str(self.source),
            "--direct-wheel",
            str(self.direct_wheel),
            "--sdist",
            str(self.sdist),
            "--sdist-wheel",
            str(self.sdist_wheel),
            "--json",
        ]

    def test_valid_artifacts_pass_with_hashes_and_bundle_identity(self) -> None:
        self._create_valid_artifacts()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = artifact_check.main(self._arguments())

        payload = json.loads(output.getvalue())
        expected_digest = artifact_check.load_source_contract(
            self.source
        ).resource_bundle_sha256
        self.assertEqual(0, status)
        self.assertEqual("pass", payload["result"])
        self.assertEqual(expected_digest, payload["resource_bundle_sha256"])
        for artifact in payload["artifacts"].values():
            self.assertEqual(64, len(artifact["sha256"]))

    def test_source_resource_difference_fails_even_with_a_valid_record(self) -> None:
        self._create_valid_artifacts()
        self._write_wheel(self.direct_wheel, resource_override=b"tampered\n")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = artifact_check.main(self._arguments())

        payload = json.loads(output.getvalue())
        self.assertEqual(2, status)
        self.assertEqual("fail", payload["result"])
        self.assertIn("bytes differ from source", payload["errors"][0])

    def test_record_hash_difference_fails(self) -> None:
        self._create_valid_artifacts()
        self._write_wheel(self.direct_wheel, corrupt_record=True)
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            status = artifact_check.main(self._arguments())

        payload = json.loads(output.getvalue())
        self.assertEqual(2, status)
        self.assertEqual("fail", payload["result"])
        self.assertIn("RECORD hash does not match", payload["errors"][0])


if __name__ == "__main__":
    unittest.main()
