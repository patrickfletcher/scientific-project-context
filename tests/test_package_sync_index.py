from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context import DISTRIBUTION_NAME, __version__  # noqa: E402
from scientific_project_context import cli, project, reporting  # noqa: E402
from scientific_project_context.project import (  # noqa: E402
    CONTEXT_EMPTY_INVENTORY_LINE,
    CONTEXT_INDEX_PATH,
    CONTEXT_INDEX_RESOURCE_ID,
    CONTEXT_INVENTORY_BEGIN,
    CONTEXT_INVENTORY_END,
    IndexSyncPlan,
    OperationError,
    apply_index_sync,
    plan_index_sync,
    rewrite_context_inventory,
)
from scientific_project_context.resources import (  # noqa: E402
    ResourceCatalog,
    load_filesystem_resources,
)


# Focused documents a project might add; the CLI prescribes no such names.
EXAMPLE_OWNER_PATHS = (
    ".context/decision-register.md",
    ".context/active/method-validation.md",
    ".context/active/artifact-contract.md",
)


def sorted_owners(*paths: str) -> tuple[str, ...]:
    return tuple(sorted(paths, key=lambda item: (item.casefold(), item)))


class OwnerPathRuleTests(unittest.TestCase):
    """Discovery and apply-time validation must accept exactly the same paths."""

    def test_context_documents_in_any_folder_are_discoverable(self) -> None:
        for relative_path in (
            ".context/curation.md",
            ".context/spectral-analysis.md",
            ".context/active/method.md",
            ".context/methods/deep/nested.md",
            ".context/methods/README.md",
            *EXAMPLE_OWNER_PATHS,
        ):
            with self.subTest(relative_path=relative_path):
                self.assertTrue(project.is_discoverable_owner_path(relative_path))

    def test_managed_and_unsafe_paths_are_rejected(self) -> None:
        for relative_path in (
            ".context/project.md",
            ".context/index.md",
            ".context/README.md",
            ".context/scientific-practice.md",
            ".context/notes.txt",
            ".context/methods/../escape.md",
            ".context\\methods\\owner.md",
            "../escape.md",
            "docs/elsewhere.md",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertFalse(project.is_discoverable_owner_path(relative_path))


class IndexSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.target = self.root / "project"
        self.target.mkdir()
        self.catalog = load_filesystem_resources(ROOT / "template")

    @property
    def index(self) -> Path:
        return self.target / CONTEXT_INDEX_PATH

    def add_owner(self, relative_path: str, *, target: Path | None = None) -> Path:
        root = target or self.target
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Owner: {relative_path}\n", encoding="utf-8")
        return path

    def create_index(self, *, target: Path | None = None) -> Path:
        root = target or self.target
        plan = plan_index_sync(self.catalog, root)
        self.assertEqual("create", plan.action)
        result = apply_index_sync(plan)
        self.assertEqual("created", result.status)
        return root / CONTEXT_INDEX_PATH

    def run_json(
        self,
        arguments: list[str],
        *,
        catalog: ResourceCatalog | None = None,
    ) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        exit_code = cli.main(
            [*arguments, "--json"],
            catalog=catalog or self.catalog,
            stdout=output,
        )
        return exit_code, json.loads(output.getvalue())

    def assert_common_identity(self, payload: dict[str, object]) -> None:
        self.assertEqual(reporting.REPORT_SCHEMA_VERSION, payload["report_schema_version"])
        self.assertEqual("sync-index", payload["operation"])
        producer = payload["producer"]
        self.assertIsInstance(producer, dict)
        assert isinstance(producer, dict)
        self.assertEqual(DISTRIBUTION_NAME, producer["distribution"])
        self.assertEqual(__version__, producer["version"])
        self.assertEqual(self.catalog.bundle_sha256, producer["resource_bundle_sha256"])

    def test_an_absent_index_is_created_for_any_number_of_documents(self) -> None:
        paths = tuple(EXAMPLE_OWNER_PATHS[:2])
        resource = self.catalog.get(CONTEXT_INDEX_RESOURCE_ID)

        for count in range(3):
            with self.subTest(count=count):
                target = self.root / f"owner-count-{count}"
                target.mkdir()
                selected = list(paths[:count])
                for relative_path in selected:
                    self.add_owner(relative_path, target=target)

                plan = plan_index_sync(self.catalog, target)
                expected = sorted_owners(*selected)

                self.assertIsInstance(plan, IndexSyncPlan)
                self.assertEqual(expected, plan.specialized_owners)
                self.assertEqual("create", plan.action)
                self.assertFalse(plan.conflicts)
                self.assertEqual(
                    rewrite_context_inventory(resource.content, expected),
                    plan.planned_content,
                )
                self.assertFalse((target / CONTEXT_INDEX_PATH).exists())

    def test_custom_owner_drives_create_and_dry_run_does_not_write(self) -> None:
        known = EXAMPLE_OWNER_PATHS[0]
        custom = ".context/active/pipeline-overview.md"
        self.add_owner(known)
        self.add_owner(custom)
        expected = sorted_owners(known, custom)

        exit_code, payload = self.run_json(
            ["sync-index", str(self.target), "--dry-run"]
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("ready", payload["result"])
        self.assertEqual("create", payload["action"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(list(expected), payload["specialized_owners"])
        self.assertEqual(len(expected), payload["specialized_owner_count"])
        self.assertEqual("generated_index", payload["generation_boundary"])
        self.assertFalse(self.index.exists())
        self.assert_common_identity(payload)

        plan = plan_index_sync(self.catalog, self.target)
        result = apply_index_sync(plan)

        self.assertEqual("created", result.status)
        self.assertEqual(expected, result.specialized_owners)
        expected_content = rewrite_context_inventory(
            self.catalog.get(CONTEXT_INDEX_RESOURCE_ID).content,
            expected,
        )
        self.assertEqual(expected_content, self.index.read_bytes())

    def test_custom_root_level_owner_survives_apply_and_reapply(self) -> None:
        """Regression: these planned cleanly, then failed apply revalidation."""

        first = ".context/curation.md"
        second = ".context/spectral-analysis.md"
        self.add_owner(first)
        self.add_owner(second)
        expected = sorted_owners(first, second)

        plan = plan_index_sync(self.catalog, self.target)
        self.assertEqual(expected, plan.specialized_owners)

        result = apply_index_sync(plan)
        self.assertEqual("created", result.status)
        self.assertEqual(expected, result.specialized_owners)

        exit_code, payload = self.run_json(["sync-index", str(self.target)])
        self.assertEqual(0, exit_code)
        self.assertEqual("no_changes", payload["result"])
        self.assertEqual(list(expected), payload["specialized_owners"])

    def test_complete_guidance_enriches_routes_and_dry_run_exposes_exact_bytes(self) -> None:
        first = EXAMPLE_OWNER_PATHS[0]
        second = EXAMPLE_OWNER_PATHS[1]
        first_path = self.add_owner(first)
        second_path = self.add_owner(second)
        first_path.write_text(
            "# First\n\n"
            "Purpose: retain the first bounded route.\n"
            "Read when: selecting context for the first topic.\n"
            "Update when: the first topic changes.\n",
            encoding="utf-8",
        )
        second_path.write_text(
            "# Second\n\n"
            "Purpose: retain a wrapped second\n"
            "route summary.\n"
            "Read when: selecting context for the second topic.\n"
            "Update when: the second topic changes.\n",
            encoding="utf-8",
        )

        exit_code, payload = self.run_json(
            ["sync-index", str(self.target), "--dry-run"]
        )

        self.assertEqual(0, exit_code)
        self.assertEqual(2, len(payload["specialized_routes"]))
        self.assertTrue(all(item["complete"] for item in payload["specialized_routes"]))
        planned = payload["planned_content"].encode("utf-8")
        self.assertEqual(payload["planned_sha256"], hashlib.sha256(planned).hexdigest())
        self.assertIn(b"  - Purpose: retain the first bounded route.\n", planned)
        self.assertIn(b"  - Purpose: retain a wrapped second route summary.\n", planned)
        self.assertFalse(self.index.exists())

        plan = plan_index_sync(self.catalog, self.target)
        apply_index_sync(plan)
        self.assertEqual(planned, self.index.read_bytes())
        stable = plan_index_sync(self.catalog, self.target)
        self.assertEqual("no_changes", stable.action)

    def test_guidance_change_after_preview_blocks_apply(self) -> None:
        for relative_path in EXAMPLE_OWNER_PATHS[:2]:
            path = self.add_owner(relative_path)
            path.write_text(
                "# Routed\n\n"
                "Purpose: route one topic.\n"
                "Read when: selecting that topic.\n"
                "Update when: that topic changes.\n",
                encoding="utf-8",
            )
        plan = plan_index_sync(self.catalog, self.target)
        changed = self.target / EXAMPLE_OWNER_PATHS[0]
        changed.write_text(
            changed.read_text(encoding="utf-8").replace(
                "Purpose: route one topic.",
                "Purpose: route a changed topic.",
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(OperationError, "guidance changed after preflight"):
            apply_index_sync(plan)
        self.assertFalse(self.index.exists())

    def test_create_plan_uses_immutable_catalog_bytes(self) -> None:
        resource_copy = self.root / "resource-copy"
        template_copy = resource_copy / "template"
        shutil.copytree(ROOT / "template", template_copy)
        copied_catalog = load_filesystem_resources(template_copy)
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        self.add_owner(EXAMPLE_OWNER_PATHS[1])
        plan = plan_index_sync(copied_catalog, self.target)
        expected = plan.planned_content

        shutil.rmtree(resource_copy)
        result = apply_index_sync(plan)

        self.assertEqual("created", result.status)
        self.assertEqual(expected, self.index.read_bytes())

    def test_update_keeps_crlf_style_of_the_packaged_heading(self) -> None:
        owner = ".context/roadmap.md"
        self.add_owner(owner)
        packaged = self.catalog.get(CONTEXT_INDEX_RESOURCE_ID).content.replace(b"\n", b"\r\n")
        original = rewrite_context_inventory(packaged, (".context/stale.md",))
        self.index.parent.mkdir(parents=True, exist_ok=True)
        self.index.write_bytes(original)

        plan = plan_index_sync(self.catalog, self.target)
        expected = rewrite_context_inventory(packaged, (owner,))

        self.assertEqual("update", plan.action)
        self.assertEqual(expected, plan.planned_content)
        self.assertNotIn(b"\n", expected.replace(b"\r\n", b""))
        result = apply_index_sync(plan)
        self.assertEqual("updated", result.status)
        self.assertEqual(expected, self.index.read_bytes())

    def test_an_index_holding_text_of_its_own_is_never_overwritten(self) -> None:
        """The index is generated, but deleting what someone wrote there is not the tool's call."""

        owner = ".context/roadmap.md"
        self.add_owner(owner)
        packaged = self.catalog.get(CONTEXT_INDEX_RESOURCE_ID).content
        original = packaged + b"\n- [Roadmap](roadmap.md): a second, hand-kept list.\n"
        self.index.parent.mkdir(parents=True, exist_ok=True)
        self.index.write_bytes(original)

        plan = plan_index_sync(self.catalog, self.target)

        self.assertEqual("blocked", plan.action)
        self.assertIn("move anything still needed", plan.conflicts[0])
        with self.assertRaises(OperationError):
            apply_index_sync(plan)
        self.assertEqual(original, self.index.read_bytes())

        self.index.unlink()
        recreated = plan_index_sync(self.catalog, self.target)
        self.assertEqual("create", recreated.action)
        self.assertEqual(rewrite_context_inventory(packaged, (owner,)), recreated.planned_content)

    def test_existing_index_is_retained_through_contraction_and_is_idempotent(self) -> None:
        first = EXAMPLE_OWNER_PATHS[0]
        second = EXAMPLE_OWNER_PATHS[1]
        first_path = self.add_owner(first)
        second_path = self.add_owner(second)
        self.create_index()

        second_path.unlink()
        one_owner_plan = plan_index_sync(self.catalog, self.target)
        self.assertEqual("update", one_owner_plan.action)
        self.assertEqual((first,), one_owner_plan.specialized_owners)
        self.assertEqual("updated", apply_index_sync(one_owner_plan).status)
        self.assertTrue(self.index.is_file())
        target = first.removeprefix(".context/")
        self.assertIn(f"- [{target}]({target})\n".encode(), self.index.read_bytes())

        first_path.unlink()
        zero_owner_plan = plan_index_sync(self.catalog, self.target)
        self.assertEqual("update", zero_owner_plan.action)
        self.assertEqual((), zero_owner_plan.specialized_owners)
        self.assertEqual("updated", apply_index_sync(zero_owner_plan).status)
        self.assertTrue(self.index.is_file())
        self.assertIn(CONTEXT_EMPTY_INVENTORY_LINE.encode(), self.index.read_bytes())

        stable = self.index.read_bytes()
        no_change_plan = plan_index_sync(self.catalog, self.target)
        self.assertEqual("no_changes", no_change_plan.action)
        self.assertEqual("no_changes", apply_index_sync(no_change_plan).status)
        self.assertEqual(stable, self.index.read_bytes())

    def test_malformed_markers_and_invalid_utf8_block_without_changes(self) -> None:
        begin = CONTEXT_INVENTORY_BEGIN.encode()
        end = CONTEXT_INVENTORY_END.encode()
        cases = {
            "unmarked": b"# Project-owned index\n",
            "duplicate": begin + b"\n" + end + b"\n" + begin + b"\n" + end + b"\n",
            "reversed": end + b"\n" + begin + b"\n",
            "unterminated_begin": b"# Index\n" + begin + end + b"\n",
            "invalid_utf8": begin + b"\n\xff\n" + end + b"\n",
        }

        for name, content in cases.items():
            with self.subTest(name=name):
                target = self.root / f"malformed-{name}"
                target.mkdir()
                self.add_owner(EXAMPLE_OWNER_PATHS[0], target=target)
                index = target / CONTEXT_INDEX_PATH
                index.write_bytes(content)

                plan = plan_index_sync(self.catalog, target)

                self.assertEqual("blocked", plan.action)
                self.assertTrue(plan.conflicts)
                with self.assertRaises(OperationError):
                    apply_index_sync(plan)
                self.assertEqual(content, index.read_bytes())

    def test_owner_addition_and_removal_after_plan_block_apply(self) -> None:
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        self.add_owner(EXAMPLE_OWNER_PATHS[1])
        create_plan = plan_index_sync(self.catalog, self.target)
        late_owner = self.add_owner(".context/active/late-owner.md")

        with self.assertRaisesRegex(OperationError, "changed after preflight"):
            apply_index_sync(create_plan)
        self.assertFalse(self.index.exists())

        late_owner.unlink()
        self.create_index()
        update_owner = self.add_owner(".context/active/update-owner.md")
        update_plan = plan_index_sync(self.catalog, self.target)
        original = self.index.read_bytes()
        update_owner.unlink()

        with self.assertRaisesRegex(OperationError, "changed after preflight"):
            apply_index_sync(update_plan)
        self.assertEqual(original, self.index.read_bytes())

    def test_index_content_and_presence_changes_after_plan_block_apply(self) -> None:
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        self.add_owner(EXAMPLE_OWNER_PATHS[1])
        create_plan = plan_index_sync(self.catalog, self.target)
        appeared = b"created by another actor\n"
        self.index.write_bytes(appeared)

        with self.assertRaises(OperationError):
            apply_index_sync(create_plan)
        self.assertEqual(appeared, self.index.read_bytes())

        self.index.write_bytes(
            rewrite_context_inventory(
                self.catalog.get(CONTEXT_INDEX_RESOURCE_ID).content,
                create_plan.specialized_owners,
            )
        )
        custom = self.add_owner(".context/active/custom.md")
        update_plan = plan_index_sync(self.catalog, self.target)
        external_change = b"changed after planning\n"
        self.index.write_bytes(external_change)

        with self.assertRaises(OperationError):
            apply_index_sync(update_plan)
        self.assertEqual(external_change, self.index.read_bytes())
        self.assertTrue(custom.is_file())

    def test_same_byte_index_replacement_after_plan_is_detected_by_identity(self) -> None:
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        self.add_owner(EXAMPLE_OWNER_PATHS[1])
        self.create_index()
        self.add_owner(".context/active/custom.md")
        plan = plan_index_sync(self.catalog, self.target)
        original = self.index.read_bytes()
        before = self.index.stat(follow_symlinks=False)
        replacement = self.index.with_name("replacement-index.md")
        replacement.write_bytes(original)
        os.replace(replacement, self.index)
        after = self.index.stat(follow_symlinks=False)
        if (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino):
            self.skipTest("filesystem reused the same identity for a replacement file")

        with self.assertRaisesRegex(OperationError, "changed after preflight"):
            apply_index_sync(plan)
        self.assertEqual(original, self.index.read_bytes())

    def test_linked_target_and_linked_ancestor_are_rejected_when_supported(self) -> None:
        real_target = self.root / "real-target"
        real_target.mkdir()
        self.add_owner(EXAMPLE_OWNER_PATHS[0], target=real_target)
        self.add_owner(EXAMPLE_OWNER_PATHS[1], target=real_target)
        linked_target = self.root / "linked-target"
        try:
            linked_target.symlink_to(real_target, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink creation is unavailable: {exc}")

        with self.assertRaisesRegex(OperationError, "symlink|junction|reparse"):
            plan_index_sync(self.catalog, linked_target)

        real_parent = self.root / "real-parent"
        nested_target = real_parent / "project"
        nested_target.mkdir(parents=True)
        self.add_owner(EXAMPLE_OWNER_PATHS[0], target=nested_target)
        self.add_owner(EXAMPLE_OWNER_PATHS[1], target=nested_target)
        linked_parent = self.root / "linked-parent"
        linked_parent.symlink_to(real_parent, target_is_directory=True)

        with self.assertRaisesRegex(OperationError, "symlink|junction|reparse"):
            plan_index_sync(self.catalog, linked_parent / "project")
        self.assertFalse((real_target / CONTEXT_INDEX_PATH).exists())
        self.assertFalse((nested_target / CONTEXT_INDEX_PATH).exists())

    def test_linked_index_is_blocked_and_never_followed_when_supported(self) -> None:
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        self.add_owner(EXAMPLE_OWNER_PATHS[1])
        external = self.root / "external-index.md"
        external_content = b"external project knowledge\n"
        external.write_bytes(external_content)
        self.index.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.index.symlink_to(external)
        except OSError as exc:
            self.skipTest(f"file symlink creation is unavailable: {exc}")

        plan = plan_index_sync(self.catalog, self.target)

        self.assertEqual("blocked", plan.action)
        self.assertTrue(plan.conflicts)
        with self.assertRaises(OperationError):
            apply_index_sync(plan)
        self.assertEqual(external_content, external.read_bytes())

    def test_case_only_custom_owner_collision_blocks_when_supported(self) -> None:
        active = self.target / ".context" / "active"
        active.mkdir(parents=True)
        upper = active / "Method.md"
        lower = active / "method.md"
        upper.write_text("# Upper\n", encoding="utf-8")
        lower.write_text("# Lower\n", encoding="utf-8")
        names = {path.name for path in active.iterdir()}
        if len(names) != 2:
            self.skipTest("filesystem does not preserve case-only filename distinctions")

        plan = plan_index_sync(self.catalog, self.target)

        self.assertEqual("blocked", plan.action)
        self.assertTrue(any("only by case" in conflict for conflict in plan.conflicts))
        self.assertFalse(self.index.exists())

    def test_frozen_plan_rejects_tampered_action_content_owners_and_resource_identity(self) -> None:
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        self.add_owner(EXAMPLE_OWNER_PATHS[1])
        plan = plan_index_sync(self.catalog, self.target)

        with self.assertRaises(FrozenInstanceError):
            plan.action = "update"  # type: ignore[misc]

        tampered_plans = [
            replace(plan, action="update"),
            replace(plan, planned_content=b"tampered plan bytes\n"),
            replace(plan, specialized_owners=tuple(reversed(plan.specialized_owners))),
        ]
        resource_id_fields = [
            field.name for field in fields(plan) if field.name.endswith("resource_id")
        ]
        self.assertEqual(
            1,
            len(resource_id_fields),
            "an index-sync plan must carry one immutable resource identity",
        )
        tampered_plans.append(
            replace(plan, **{resource_id_fields[0]: "template/not-the-index.md"})
        )

        for tampered in tampered_plans:
            with self.subTest(tampered=tampered):
                with self.assertRaises(OperationError):
                    apply_index_sync(tampered)
                self.assertFalse(self.index.exists())

    def test_replace_failure_preserves_original_and_cleans_temporary_file(self) -> None:
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        self.add_owner(EXAMPLE_OWNER_PATHS[1])
        self.create_index()
        self.add_owner(".context/active/custom.md")
        plan = plan_index_sync(self.catalog, self.target)
        original = self.index.read_bytes()
        entries_before = {path.name for path in self.index.parent.iterdir()}

        with mock.patch.object(project.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaisesRegex(OSError, "replace failed"):
                apply_index_sync(plan)

        self.assertEqual(original, self.index.read_bytes())
        self.assertEqual(entries_before, {path.name for path in self.index.parent.iterdir()})

    def test_exclusive_create_race_preserves_competing_index(self) -> None:
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        self.add_owner(EXAMPLE_OWNER_PATHS[1])
        plan = plan_index_sync(self.catalog, self.target)
        original_write = project._write_bytes_exclusively
        competing_content = b"created by another actor\n"

        def competing_write(
            content: bytes,
            destination: Path,
            *,
            operation: str,
        ) -> tuple[int, int]:
            destination.write_bytes(competing_content)
            return original_write(content, destination, operation=operation)

        with mock.patch.object(
            project,
            "_write_bytes_exclusively",
            side_effect=competing_write,
        ):
            with self.assertRaises((FileExistsError, OperationError)):
                apply_index_sync(plan)

        self.assertEqual(competing_content, self.index.read_bytes())

    def test_cli_json_and_human_reports_share_identity_and_success_exit_contracts(self) -> None:
        first = EXAMPLE_OWNER_PATHS[0]
        second = EXAMPLE_OWNER_PATHS[1]
        self.add_owner(first)
        self.add_owner(second)

        dry_exit, dry_payload = self.run_json(
            ["sync-index", str(self.target), "--dry-run"]
        )
        human_output = io.StringIO()
        human_exit = cli.main(
            ["sync-index", str(self.target), "--dry-run"],
            catalog=self.catalog,
            stdout=human_output,
        )

        self.assertEqual(0, dry_exit)
        self.assertEqual(0, human_exit)
        self.assertEqual("ready", dry_payload["result"])
        self.assertEqual("create", dry_payload["action"])
        self.assertFalse(self.index.exists())
        self.assert_common_identity(dry_payload)
        human = human_output.getvalue()
        producer = dry_payload["producer"]
        target = dry_payload["target"]
        assert isinstance(producer, dict)
        assert isinstance(target, dict)
        for expected in (
            f"- Result: {dry_payload['result']}",
            "- Operation: sync-index",
            f"- Version: {producer['version']}",
            f"- Target: {target['path']}",
            "- Planned action: create",
            first,
            second,
        ):
            self.assertIn(expected, human)

        created_exit, created = self.run_json(["sync-index", str(self.target)])
        self.assertEqual(0, created_exit)
        self.assertEqual("created", created["result"])
        self.assert_common_identity(created)

        stable = self.index.read_bytes()
        no_change_exit, no_change = self.run_json(["sync-index", str(self.target)])
        self.assertEqual(0, no_change_exit)
        self.assertEqual("no_changes", no_change["result"])
        self.assertEqual(stable, self.index.read_bytes())
        self.assert_common_identity(no_change)

    def test_documents_in_every_folder_are_listed(self) -> None:
        """A subfolder of documents was once left out of the index without notice."""

        for relative_path in (*EXAMPLE_OWNER_PATHS[:2], ".context/methods/calibration.md"):
            self.add_owner(relative_path)
        self.add_owner(".context/archived/old-plan.md")
        self.add_owner(".context/notes/deep/inner.md")
        (self.target / ".context/notes/figure.png").write_bytes(b"not markdown")

        _, payload = self.run_json(["sync-index", str(self.target), "--dry-run"])

        self.assertEqual(
            [
                ".context/active/method-validation.md",
                ".context/archived/old-plan.md",
                ".context/decision-register.md",
                ".context/methods/calibration.md",
                ".context/notes/deep/inner.md",
            ],
            payload["specialized_owners"],
        )

    def test_cli_created_blocked_and_error_exit_contracts(self) -> None:
        self.add_owner(EXAMPLE_OWNER_PATHS[0])
        created_exit, created = self.run_json(
            ["sync-index", str(self.target)]
        )
        self.assertEqual(0, created_exit)
        self.assertEqual("created", created["result"])
        self.assertTrue(self.index.exists())
        self.assert_common_identity(created)

        blocked_content = b"# Unmarked project index\n"
        self.index.write_bytes(blocked_content)
        blocked_exit, blocked = self.run_json(["sync-index", str(self.target)])
        self.assertEqual(2, blocked_exit)
        self.assertEqual("blocked", blocked["result"])
        self.assertEqual("blocked", blocked["action"])
        self.assertEqual(blocked_content, self.index.read_bytes())
        self.assert_common_identity(blocked)

        missing = self.root / "missing"
        error_exit, error = self.run_json(["sync-index", str(missing)])
        self.assertEqual(2, error_exit)
        self.assertEqual("error", error["result"])
        self.assertEqual("sync-index", error["operation"])
        self.assertEqual({"path": str(missing)}, error["target"])
        self.assertIn("message", error)
        self.assert_common_identity(error)


if __name__ == "__main__":
    unittest.main()
