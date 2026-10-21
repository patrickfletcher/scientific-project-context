from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context import resources  # noqa: E402


class ResourceCatalogTests(unittest.TestCase):
    def load_repository_catalog(self) -> resources.ResourceCatalog:
        return resources.load_filesystem_resources(ROOT / "template")

    def test_repository_catalog_has_exact_inventory_and_byte_identity(self) -> None:
        catalog = self.load_repository_catalog()

        self.assertEqual(
            len(resources.TEMPLATE_INVENTORY), len(catalog.template_entries)
        )
        self.assertEqual(resources.TEMPLATE_RESOURCE_IDS, tuple(
            entry.resource_id for entry in catalog.template_entries
        ))
        self.assertEqual(
            resources.STARTER_INVENTORY,
            tuple(entry.relative_path for entry in catalog.starter_entries),
        )
        # The index is a starter file: `init` writes it so it is always the one list.
        self.assertIn(
            resources.CONTEXT_INDEX_PATH,
            tuple(entry.relative_path for entry in catalog.starter_entries),
        )
        self.assertTrue(
            all(".design" not in entry.resource_id for entry in catalog.entries)
        )
        self.assertTrue(
            all(
                not path.startswith(".")
                or path.startswith(".context/")
                or path.startswith(".agents/skills/")
                for path in resources.TEMPLATE_INVENTORY
            )
        )

        for skill_path in resources.TEMPLATE_INVENTORY:
            if not skill_path.startswith(".agents/skills/"):
                continue
            self.assertEqual(
                (ROOT / skill_path).read_bytes(),
                (ROOT / "template" / skill_path).read_bytes(),
            )

        for entry in catalog.entries:
            root = ROOT / entry.collection
            self.assertEqual((root / entry.relative_path).read_bytes(), entry.content)
            self.assertEqual(hashlib.sha256(entry.content).hexdigest(), entry.sha256)

    def test_bundle_digest_is_order_independent_and_changes_with_resources(self) -> None:
        catalog = self.load_repository_catalog()
        self.assertEqual(
            catalog.bundle_sha256,
            resources.calculate_bundle_sha256(reversed(catalog.entries)),
        )
        original = catalog.entries[0]
        changed_content = resources.ResourceEntry(
            resource_id=original.resource_id,
            collection=original.collection,
            relative_path=original.relative_path,
            content=original.content + b"changed",
            sha256=hashlib.sha256(original.content + b"changed").hexdigest(),
        )
        changed_id = resources.ResourceEntry(
            resource_id=original.resource_id + "-changed",
            collection=original.collection,
            relative_path=original.relative_path,
            content=original.content,
            sha256=original.sha256,
        )

        self.assertNotEqual(
            catalog.bundle_sha256,
            resources.calculate_bundle_sha256((changed_content, *catalog.entries[1:])),
        )
        self.assertNotEqual(
            catalog.bundle_sha256,
            resources.calculate_bundle_sha256((changed_id, *catalog.entries[1:])),
        )

    def test_missing_and_unexpected_resources_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            template = root / "template"
            shutil.copytree(ROOT / "template", template)

            (template / "AGENTS.md").unlink()
            with self.assertRaisesRegex(resources.ResourceError, "missing: AGENTS.md"):
                resources.load_filesystem_resources(template)

            shutil.copy2(ROOT / "template" / "AGENTS.md", template / "AGENTS.md")
            (template / "unexpected.md").write_text("unexpected\n", encoding="utf-8")
            with self.assertRaisesRegex(resources.ResourceError, "unexpected: unexpected.md"):
                resources.load_filesystem_resources(template)

    def test_non_directory_collection_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            not_a_directory = root / "template.txt"
            not_a_directory.write_text("not a directory\n", encoding="utf-8")

            with self.assertRaisesRegex(resources.ResourceError, "not a directory"):
                resources.load_filesystem_resources(not_a_directory)

    def test_missing_installed_resource_namespace_is_a_bounded_error(self) -> None:
        with mock.patch.object(
            resources.importlib_resources,
            "files",
            side_effect=ModuleNotFoundError("missing resource package"),
        ):
            with self.assertRaisesRegex(resources.ResourceError, "install or reinstall"):
                resources.load_packaged_resources()


if __name__ == "__main__":
    unittest.main()
