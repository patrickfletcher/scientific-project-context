from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context import DISTRIBUTION_NAME, __version__  # noqa: E402
from scientific_project_context import cli, project, reporting  # noqa: E402
from scientific_project_context.project import (  # noqa: E402
    AGENT_SKILLS,
    OperationError,
    agent_skill_path,
    apply_initialization,
    claude_skill_path,
    plan_index_sync,
    plan_initialization,
    validate_agent_skill_content,
)
from scientific_project_context.resources import (  # noqa: E402
    STARTER_INVENTORY,
    load_filesystem_resources,
)


class InitializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.catalog = load_filesystem_resources(ROOT / "template")

    def template_content(self, relative_path: str) -> bytes:
        return self.catalog.get(f"template/{relative_path}").content

    def assert_starter_bytes(self, target: Path) -> None:
        for entry in self.catalog.starter_entries:
            with self.subTest(relative_path=entry.relative_path):
                self.assertEqual(entry.content, (target / entry.relative_path).read_bytes())

    def test_new_initialization_dry_run_and_apply(self) -> None:
        target = self.root / "new-project"

        plan = plan_initialization(self.catalog, target, "new")

        self.assertEqual(STARTER_INVENTORY, plan.copy_files)
        self.assertEqual("ready", plan.status)
        self.assertFalse(target.exists())

        result = apply_initialization(plan)

        self.assertEqual("initialized", result.status)
        self.assertEqual(STARTER_INVENTORY, result.created_files)
        self.assertEqual(self.catalog.bundle_sha256, result.resource_bundle_sha256)
        self.assert_starter_bytes(target)

        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        for command, _ in reporting.INITIALIZED_TOOL_COMMANDS:
            self.assertIn(f"`{command}`", agents)

    def test_new_initialization_rejects_nonempty_target(self) -> None:
        target = self.root / "occupied"
        target.mkdir()
        (target / "README.md").write_text("existing project\n", encoding="utf-8")

        with self.assertRaisesRegex(OperationError, "missing or empty"):
            plan_initialization(self.catalog, target, "new")

        self.assertFalse((target / "AGENTS.md").exists())

    def test_retrofit_reuses_identical_files_and_copies_missing_files(self) -> None:
        target = self.root / "retrofit"
        target.mkdir()
        (target / "AGENTS.md").write_bytes(self.template_content("AGENTS.md"))
        unrelated = target / "project.py"
        unrelated.write_text("print('keep me')\n", encoding="utf-8")

        plan = plan_initialization(self.catalog, target, "retrofit")

        self.assertEqual(("AGENTS.md",), plan.identical_files)
        self.assertEqual(len(STARTER_INVENTORY) - 1, len(plan.copy_files))
        self.assertFalse(plan.conflicts)

        result = apply_initialization(plan)

        self.assertEqual("initialized", result.status)
        self.assertEqual("print('keep me')\n", unrelated.read_text(encoding="utf-8"))
        self.assert_starter_bytes(target)

    def test_retrofit_writes_an_index_of_the_documents_already_there(self) -> None:
        """The index is complete from the first run, not only once someone syncs it."""

        target = self.root / "retrofit-with-documents"
        document = target / ".context/methods/calibration.md"
        document.parent.mkdir(parents=True)
        document.write_text(
            "# Calibration\n\nPurpose: the current calibration.\n"
            "Read when: changing a calibration.\nUpdate when: a calibration changes.\n",
            encoding="utf-8",
        )

        plan = plan_initialization(self.catalog, target, "retrofit")
        apply_initialization(plan)

        index = (target / ".context/index.md").read_text(encoding="utf-8")
        self.assertIn(
            "- [methods/calibration.md](methods/calibration.md)\n"
            "  - Purpose: the current calibration.\n"
            "  - Read when: changing a calibration.\n",
            index,
        )
        self.assertEqual("no_changes", plan_index_sync(self.catalog, target).action)

    def test_pre_dev13_design_layout_is_not_silently_migrated(self) -> None:
        target = self.root / "legacy-design-layout"
        legacy_project = target / ".design/project.md"
        legacy_project.parent.mkdir(parents=True)
        legacy_bytes = b"# Project Context\n\nLegacy project-owned context.\n"
        legacy_project.write_bytes(legacy_bytes)

        plan = plan_initialization(self.catalog, target, "retrofit")

        self.assertIn(".context/project.md", plan.copy_files)
        self.assertNotIn(".design/project.md", plan.copy_files)
        apply_initialization(plan)

        self.assertEqual(legacy_bytes, legacy_project.read_bytes())
        self.assertEqual(
            self.template_content(".context/project.md"),
            (target / ".context/project.md").read_bytes(),
        )

    def test_agent_skills_are_required_self_contained_and_idempotent(self) -> None:
        target = self.root / "agent-skills-project"

        plan = plan_initialization(self.catalog, target, "new")
        self.assertEqual(len(AGENT_SKILLS), len(plan.agent_skill_files))
        for file in plan.agent_skill_files:
            self.assertEqual("create", file.disposition)
            validate_agent_skill_content(file.content)
            text = file.content.decode("utf-8")
            self.assertNotIn(".agent/workflows/", text)
            self.assertIn("## 1.", text)

        apply_initialization(plan)
        rerun = plan_initialization(self.catalog, target, "retrofit")
        self.assertTrue(rerun.agent_skill_files)
        self.assertTrue(
            all(file.disposition == "identical" for file in rerun.agent_skill_files)
        )
        self.assertEqual("starter_files_present", apply_initialization(rerun).status)

    def test_agent_skill_never_overwrites_an_occupied_file(self) -> None:
        target = self.root / "occupied-agent-skill"
        skill = target / ".agents/skills/spctx-project-context/SKILL.md"
        skill.parent.mkdir(parents=True)
        occupied = b"project-owned skill\n"
        skill.write_bytes(occupied)

        plan = plan_initialization(self.catalog, target, "retrofit")
        skill_files = {file.relative_path: file for file in plan.agent_skill_files}
        self.assertEqual(
            "retain",
            skill_files[
                ".agents/skills/spctx-project-context/SKILL.md"
            ].disposition,
        )
        apply_initialization(plan)
        self.assertEqual(occupied, skill.read_bytes())

    def test_claude_pointers_are_opt_in_and_route_to_the_canonical_skill(self) -> None:
        """Claude Code reads no skills from `.agents/`, so it needs a pointer."""

        target = self.root / "claude-project"

        without = plan_initialization(self.catalog, target, "new")
        self.assertEqual((), without.claude_skill_files)

        plan = plan_initialization(self.catalog, target, "new", claude=True)
        self.assertEqual(len(AGENT_SKILLS), len(plan.claude_skill_files))
        apply_initialization(plan)

        for name in AGENT_SKILLS:
            with self.subTest(skill=name):
                pointer = target / claude_skill_path(name)
                canonical = target / agent_skill_path(name)
                pointer_parts = project.parse_agent_skill_content(
                    pointer.read_bytes(),
                    expected_name=name,
                )
                canonical_parts = project.parse_agent_skill_content(
                    canonical.read_bytes()
                )
                self.assertEqual(canonical_parts.description, pointer_parts.description)
                self.assertIn(agent_skill_path(name), pointer_parts.body)
                self.assertNotIn("## 1.", pointer_parts.body)

    def test_claude_pointer_carries_this_projects_tuned_triggers(self) -> None:
        target = self.root / "claude-tuned"
        canonical = target / agent_skill_path("spctx-project-context")
        canonical.parent.mkdir(parents=True)
        packaged = self.template_content(agent_skill_path("spctx-project-context"))
        tuned = packaged.replace(
            b"Do not use for ordinary implementation, analysis changes, or writing public documentation.",
            b"Do not use for ordinary implementation, analysis changes, or writing public documentation. "
            b'Also use for requests such as: "set up context for this assay".',
            1,
        )
        self.assertNotEqual(packaged, tuned)
        canonical.write_bytes(tuned)

        plan = plan_initialization(self.catalog, target, "retrofit", claude=True)
        apply_initialization(plan)

        pointer = (target / claude_skill_path("spctx-project-context")).read_bytes()
        self.assertIn(b"set up context for this assay", pointer)

    def test_claude_pointer_is_never_overwritten(self) -> None:
        target = self.root / "claude-occupied"
        pointer = target / claude_skill_path("spctx-project-context")
        pointer.parent.mkdir(parents=True)
        occupied = b"project-owned pointer\n"
        pointer.write_bytes(occupied)

        plan = plan_initialization(self.catalog, target, "retrofit", claude=True)
        pointers = {file.relative_path: file for file in plan.claude_skill_files}
        self.assertEqual(
            "retain",
            pointers[claude_skill_path("spctx-project-context")].disposition,
        )
        apply_initialization(plan)
        self.assertEqual(occupied, pointer.read_bytes())

    def test_report_asks_for_project_essentials_and_names_the_interpreter(self) -> None:
        """A step with no report line does not reliably run."""

        target = self.root / "essentials-project"
        plan = plan_initialization(self.catalog, target, "new")
        report = reporting.initialization_report(plan, dry_run=True)

        actions = [step["action"] for step in report["next_steps"]]
        self.assertIn("populate_agent_essentials", actions)
        self.assertEqual(sys.executable, report["tool_discovery"]["interpreter"])
        self.assertIn(sys.executable, reporting.render_human(report))

    def test_report_explains_how_claude_reads_the_instruction_file(self) -> None:
        target = self.root / "claude-md-project"
        target.mkdir()
        (target / "CLAUDE.md").write_text("project instructions\n", encoding="utf-8")

        plan = plan_initialization(self.catalog, target, "retrofit", claude=True)
        report = reporting.initialization_report(plan, dry_run=True)

        self.assertEqual(
            "claude_md_present_import_required",
            report["claude_skills"]["instruction_file"],
        )
        actions = [step["action"] for step in report["next_steps"]]
        self.assertIn("import_agents_file_into_claude_md", actions)
        self.assertIn("@AGENTS.md", reporting.render_human(report))

    def test_retrofit_retains_a_project_owned_agents_file_and_fills_gaps(self) -> None:
        target = self.root / "retrofit-retain"
        target.mkdir()
        agents = target / "AGENTS.md"
        agents.write_text("project-specific agents\n", encoding="utf-8")

        plan = plan_initialization(self.catalog, target, "retrofit")

        self.assertEqual((), plan.conflicts)
        self.assertEqual(("AGENTS.md",), plan.retained_files)
        self.assertEqual("ready", plan.status)
        result = apply_initialization(plan)

        self.assertEqual("initialized", result.status)
        self.assertEqual(("AGENTS.md",), result.retained_files)
        self.assertEqual("project-specific agents\n", agents.read_text(encoding="utf-8"))
        self.assertTrue((target / ".context/project.md").is_file())
        self.assertTrue(
            (target / ".agents/skills/spctx-project-context/SKILL.md").is_file()
        )

    def test_retrofit_retains_every_occupied_regular_starter_path(self) -> None:
        target = self.root / "retrofit-retain-all"
        target.mkdir()
        expected: dict[str, bytes] = {}
        for index, relative_path in enumerate(STARTER_INVENTORY):
            path = target / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            content = f"project-owned {index}\n".encode()
            path.write_bytes(content)
            expected[relative_path] = content

        plan = plan_initialization(self.catalog, target, "retrofit")

        self.assertEqual(STARTER_INVENTORY, plan.retained_files)
        self.assertEqual("starter_files_present", plan.status)
        self.assertFalse(plan.conflicts)
        result = apply_initialization(plan)

        self.assertEqual("starter_files_present", result.status)
        self.assertEqual(STARTER_INVENTORY, result.retained_files)
        for relative_path, content in expected.items():
            self.assertEqual(content, (target / relative_path).read_bytes())

    def test_retrofit_json_reports_retained_agents_and_actionable_handoff(self) -> None:
        target = self.root / "retrofit-cli-retain"
        target.mkdir()
        agents = target / "AGENTS.md"
        agents.write_text("project-specific agents\n", encoding="utf-8")
        output = io.StringIO()

        result = cli.main(
            ["init", str(target), "--mode", "retrofit", "--json"],
            catalog=self.catalog,
            stdout=output,
        )

        payload = json.loads(output.getvalue())
        self.assertEqual(0, result)
        self.assertEqual("initialized", payload["result"])
        self.assertEqual(0, payload["summary"]["conflicts"])
        self.assertEqual(["AGENTS.md"], payload["retained_files"])
        self.assertIn(
            "integrate_project_context_route",
            [step["action"] for step in payload["next_steps"]],
        )
        adoption = payload["context_adoption"]
        self.assertEqual("manual_activation_required", adoption["status"])
        self.assertEqual("absent", adoption["agent_route"])
        suggested_route = adoption["suggested_agents_block"]
        self.assertIn(project.CONTEXT_ROUTE_BEGIN, suggested_route)
        self.assertIn(".context/project.md", suggested_route)
        self.assertIn("spctx-project-context/SKILL.md", suggested_route)
        self.assertIn("spctx-scientific-change/SKILL.md", suggested_route)
        self.assertEqual(
            "review_required",
            payload["tool_discovery"]["persistent_agent_guidance"],
        )
        self.assertEqual("not_performed", payload["semantic_initialization"])
        self.assertFalse((target / ".agent").exists())
        self.assertEqual("project-specific agents\n", agents.read_text(encoding="utf-8"))

    def test_retrofit_recognizes_a_reviewed_route_without_claiming_compatibility(self) -> None:
        target = self.root / "retrofit-routed"
        target.mkdir()
        agents = target / "AGENTS.md"
        agents.write_text(
            "# Project Instructions\n\n" + project.CONTEXT_ROUTE_BLOCK + "\n",
            encoding="utf-8",
        )

        plan = plan_initialization(self.catalog, target, "retrofit")
        payload = reporting.initialization_report(plan, dry_run=True)

        adoption = payload["context_adoption"]
        self.assertEqual("ready_after_apply", adoption["status"])
        self.assertEqual("exact", adoption["agent_route"])
        self.assertEqual("not_machine_checked", adoption["instruction_compatibility"])
        self.assertNotIn("suggested_agents_block", adoption)
        route_step = next(
            step
            for step in payload["next_steps"]
            if step["action"] == "review_instruction_compatibility"
        )
        self.assertIn("No edit needed", route_step["instruction"])
        # Upgrades wrote always-read lines from the core when the packaged file was out of reach.
        self.assertEqual(
            self.template_content("AGENTS.md").decode("utf-8"),
            adoption["packaged_agents_file"],
        )
        self.assertIn(
            "Packaged AGENTS.md, to compare with yours", reporting.render_human(payload)
        )
        self.assertEqual("# Project Instructions\n\n" + project.CONTEXT_ROUTE_BLOCK + "\n", agents.read_text(encoding="utf-8"))

    def test_retrofit_reports_retained_skill_as_review_required(self) -> None:
        target = self.root / "retrofit-retained-skill"
        target.mkdir()
        skill = target / ".agents/skills/spctx-scientific-change/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(
            "# Existing Scientific Skill\n\nFollow project-specific review rules.\n",
            encoding="utf-8",
        )

        plan = plan_initialization(self.catalog, target, "retrofit")
        payload = reporting.initialization_report(plan, dry_run=True)

        self.assertEqual(("AGENTS.md",), plan.deferred_files)
        self.assertNotIn("AGENTS.md", plan.copy_files)
        self.assertEqual("ready_with_activation_deferred", payload["result"])
        self.assertNotIn("AGENTS.md", payload["tool_discovery"]["read_first"])
        adoption = payload["context_adoption"]
        self.assertEqual("skill_review_required", adoption["status"])
        self.assertEqual(
            "project_owned_review_required",
            adoption["skills"][".agents/skills/spctx-scientific-change/SKILL.md"],
        )
        self.assertEqual(
            "available_after_apply",
            adoption["skills"][".agents/skills/spctx-project-context/SKILL.md"],
        )
        self.assertIn(
            "review_agent_skill_variations",
            [step["action"] for step in payload["next_steps"]],
        )
        self.assertEqual(
            self.template_content(".agents/skills/spctx-scientific-change/SKILL.md").decode(
                "utf-8"
            ),
            adoption["suggested_skills"][
                ".agents/skills/spctx-scientific-change/SKILL.md"
            ],
        )
        self.assertEqual(
            self.template_content("AGENTS.md").decode("utf-8"),
            adoption["suggested_agents_file"],
        )
        human = reporting.render_human(payload)
        self.assertIn("Packaged skill for review", human)
        self.assertIn("Packaged AGENTS.md for review", human)
        self.assertIn("## Project Essentials", human)
        result = apply_initialization(plan)
        self.assertEqual("initialized_with_activation_deferred", result.status)
        self.assertEqual(("AGENTS.md",), result.deferred_files)
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertEqual(
            "# Existing Scientific Skill\n\nFollow project-specific review rules.\n",
            skill.read_text(encoding="utf-8"),
        )

    def test_retrofit_reports_retained_practice_as_review_required_with_packaged_core(self) -> None:
        target = self.root / "retrofit-retained-practice"
        target.mkdir()
        practice = target / ".context" / "scientific-practice.md"
        practice.parent.mkdir(parents=True)
        practice.write_text(
            "# Existing Practice\n\nUse the laboratory's established review.\n",
            encoding="utf-8",
        )

        plan = plan_initialization(self.catalog, target, "retrofit")
        payload = reporting.initialization_report(plan, dry_run=True)

        self.assertEqual(("AGENTS.md",), plan.deferred_files)
        self.assertNotIn("AGENTS.md", plan.copy_files)
        self.assertEqual("ready_with_activation_deferred", payload["result"])
        self.assertNotIn("AGENTS.md", payload["tool_discovery"]["read_first"])
        adoption = payload["context_adoption"]
        self.assertEqual("scientific_contract_review_required", adoption["status"])
        self.assertIn(project.SCIENTIFIC_PRACTICE_BEGIN, adoption["suggested_practice_core"])
        self.assertIn(project.SCIENTIFIC_PRACTICE_END, adoption["suggested_practice_core"])
        self.assertIn(
            "review_scientific_practice_contract",
            [step["action"] for step in payload["next_steps"]],
        )
        human = reporting.render_human(payload)
        self.assertIn("Packaged scientific-practice core for review", human)
        self.assertIn("Held back for review", human)
        result = apply_initialization(plan)
        self.assertEqual("initialized_with_activation_deferred", result.status)
        self.assertEqual(("AGENTS.md",), result.deferred_files)
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertEqual(
            "# Existing Practice\n\nUse the laboratory's established review.\n",
            practice.read_text(encoding="utf-8"),
        )

    def test_structural_obstructions_block_without_partial_writes(self) -> None:
        target = self.root / "structural-obstruction"
        target.mkdir()
        (target / ".agents").write_text("not a directory\n", encoding="utf-8")
        (target / "AGENTS.md").mkdir()

        plan = plan_initialization(self.catalog, target, "retrofit")

        self.assertEqual("blocked", plan.status)
        self.assertTrue(any("parent path" in item for item in plan.conflicts))
        self.assertTrue(any("not a file" in item for item in plan.conflicts))
        with self.assertRaises(OperationError):
            apply_initialization(plan)
        self.assertFalse((target / ".context").exists())
        self.assertEqual("not a directory\n", (target / ".agents").read_text(encoding="utf-8"))
        self.assertTrue((target / "AGENTS.md").is_dir())

    def test_apply_revalidates_every_preflight_classification_before_writing(self) -> None:
        # A path classified for creation must still be absent.
        create_target = self.root / "stale-create"
        create_target.mkdir()
        create_plan = plan_initialization(self.catalog, create_target, "retrofit")
        appeared = create_target / ".context" / "project.md"
        appeared.parent.mkdir()
        appeared.write_text("appeared later\n", encoding="utf-8")
        with self.assertRaisesRegex(OperationError, "appeared after preflight"):
            apply_initialization(create_plan)
        self.assertEqual("appeared later\n", appeared.read_text(encoding="utf-8"))
        self.assertFalse((create_target / ".agent").exists())

        # An identical path must retain its observed bytes.
        identical_target = self.root / "stale-identical"
        identical_target.mkdir()
        identical = identical_target / "AGENTS.md"
        identical.write_bytes(self.template_content("AGENTS.md"))
        identical_plan = plan_initialization(self.catalog, identical_target, "retrofit")
        identical.write_text("changed later\n", encoding="utf-8")
        with self.assertRaisesRegex(OperationError, "changed after preflight"):
            apply_initialization(identical_plan)
        self.assertEqual("changed later\n", identical.read_text(encoding="utf-8"))
        self.assertFalse((identical_target / ".agent").exists())

        # A retained path must retain the differing bytes observed during preflight.
        retain_target = self.root / "stale-retain"
        retain_target.mkdir()
        retained = retain_target / "AGENTS.md"
        retained.write_text("reviewed difference\n", encoding="utf-8")
        retain_plan = plan_initialization(self.catalog, retain_target, "retrofit")
        retained.write_text("different unreviewed change\n", encoding="utf-8")
        with self.assertRaisesRegex(OperationError, "changed after preflight"):
            apply_initialization(retain_plan)
        self.assertEqual(
            "different unreviewed change\n",
            retained.read_text(encoding="utf-8"),
        )
        self.assertFalse((retain_target / ".agent").exists())

        # A missing new-project target must not become occupied between plan and apply.
        new_target = self.root / "stale-new-target"
        new_plan = plan_initialization(self.catalog, new_target, "new")
        new_target.mkdir()
        unrelated = new_target / "README.md"
        unrelated.write_text("external occupant\n", encoding="utf-8")
        with self.assertRaisesRegex(OperationError, "missing or empty"):
            apply_initialization(new_plan)
        self.assertEqual("external occupant\n", unrelated.read_text(encoding="utf-8"))
        self.assertFalse((new_target / "AGENTS.md").exists())

    def test_exclusive_create_race_rolls_back_only_operation_owned_effects(self) -> None:
        target = self.root / "exclusive-race"
        target.mkdir()
        unrelated = target / "README.md"
        unrelated.write_text("keep me\n", encoding="utf-8")
        plan = plan_initialization(self.catalog, target, "retrofit")
        original_write = project._write_bytes_exclusively

        def competing_write(content: bytes, destination: Path) -> tuple[int, int]:
            if destination.name == "AGENTS.md":
                destination.write_text("created by another actor\n", encoding="utf-8")
            return original_write(content, destination)

        with mock.patch.object(
            project,
            "_write_bytes_exclusively",
            side_effect=competing_write,
        ):
            with self.assertRaises(FileExistsError):
                apply_initialization(plan)

        self.assertEqual("keep me\n", unrelated.read_text(encoding="utf-8"))
        self.assertEqual(
            "created by another actor\n",
            (target / "AGENTS.md").read_text(encoding="utf-8"),
        )
        self.assertFalse((target / ".agent").exists())
        self.assertFalse((target / ".context").exists())

    def test_linked_target_and_linked_ancestor_are_rejected_when_supported(self) -> None:
        real_parent = self.root / "real-parent"
        real_parent.mkdir()
        linked_parent = self.root / "linked-parent"
        try:
            linked_parent.symlink_to(real_parent, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink creation is unavailable: {exc}")

        with self.assertRaisesRegex(OperationError, "symlink|junction|reparse"):
            plan_initialization(self.catalog, linked_parent, "retrofit")
        with self.assertRaisesRegex(OperationError, "symlink|junction|reparse"):
            plan_initialization(self.catalog, linked_parent / "new-project", "new")
        self.assertEqual([], list(real_parent.iterdir()))

    def test_linked_destination_is_a_conflict_and_is_not_followed_when_supported(self) -> None:
        target = self.root / "linked-destination"
        target.mkdir()
        external = self.root / "external-agents.md"
        external.write_text("external\n", encoding="utf-8")
        linked_destination = target / "AGENTS.md"
        try:
            linked_destination.symlink_to(external)
        except OSError as exc:
            self.skipTest(f"file symlink creation is unavailable: {exc}")

        plan = plan_initialization(self.catalog, target, "retrofit")

        self.assertTrue(any("AGENTS.md (target is a symlink)" == item for item in plan.conflicts))
        with self.assertRaises(OperationError):
            apply_initialization(plan)
        self.assertEqual("external\n", external.read_text(encoding="utf-8"))
        self.assertFalse((target / ".agent").exists())

    def test_plan_carries_immutable_resource_bytes_after_sources_disappear(self) -> None:
        template_copy = self.root / "resource-copy" / "template"
        shutil.copytree(ROOT / "template", template_copy)
        copied_catalog = load_filesystem_resources(template_copy)
        target = self.root / "snapshot-target"
        plan = plan_initialization(copied_catalog, target, "new")
        expected = {
            entry.relative_path: entry.content for entry in copied_catalog.starter_entries
        }

        shutil.rmtree(template_copy.parent)
        result = apply_initialization(plan)

        self.assertEqual("initialized", result.status)
        for relative_path, content in expected.items():
            self.assertEqual(content, (target / relative_path).read_bytes())


class InitializationReportingAndCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.catalog = load_filesystem_resources(ROOT / "template")

    def run_json(self, arguments: list[str]) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        exit_code = cli.main(
            arguments + ["--json"],
            catalog=self.catalog,
            stdout=output,
        )
        return exit_code, json.loads(output.getvalue())

    def assert_report_identity(self, payload: dict[str, object]) -> None:
        self.assertEqual(reporting.REPORT_SCHEMA_VERSION, payload["report_schema_version"])
        producer = payload["producer"]
        self.assertIsInstance(producer, dict)
        assert isinstance(producer, dict)
        self.assertEqual(DISTRIBUTION_NAME, producer["distribution"])
        self.assertEqual(__version__, producer["version"])
        self.assertEqual(self.catalog.bundle_sha256, producer["resource_bundle_sha256"])
        self.assertEqual("init", payload["operation"])
        self.assertEqual("not_performed", payload["semantic_initialization"])

    def test_versioned_json_and_human_renderers_share_one_report_payload(self) -> None:
        target = self.root / "report-target"
        plan = plan_initialization(self.catalog, target, "new")
        payload = reporting.initialization_report(plan, dry_run=True)

        self.assert_report_identity(payload)
        self.assertEqual(payload, json.loads(reporting.render_json(payload)))
        human = reporting.render_human(payload)
        producer = payload["producer"]
        target_payload = payload["target"]
        assert isinstance(producer, dict)
        assert isinstance(target_payload, dict)
        self.assertIn(f"- Result: {payload['result']}", human)
        self.assertIn(f"- Version: {producer['version']}", human)
        self.assertNotIn("- Resource bundle:", human)
        self.assertEqual(64, len(str(producer["resource_bundle_sha256"])))
        self.assertIn(f"- Target: {target_payload['path']}", human)
        self.assertIn(f"- Files to copy: {len(payload['copy_files'])}", human)
        for relative_path in payload["copy_files"]:
            self.assertIn(f"  - {relative_path}", human)

        discovery = payload["tool_discovery"]
        self.assertIsInstance(discovery, dict)
        assert isinstance(discovery, dict)
        self.assertEqual(str(target), discovery["working_directory"])
        self.assertIs(True, discovery["reported_now"])
        self.assertEqual(
            "after_initialization_apply",
            discovery["persistent_agent_guidance"],
        )
        self.assertIn("Where things are", human)
        self.assertEqual(
            ["AGENTS.md", ".context/project.md"],
            discovery["read_first"],
        )
        self.assertEqual(
            [
                ".context/scientific-practice.md",
                ".agents/skills/spctx-scientific-change/SKILL.md",
            ],
            discovery["read_when_scientifically_material"],
        )
        self.assertEqual(
            [".agents/skills/spctx-project-context/SKILL.md"],
            discovery["read_when_maintaining_context"],
        )
        self.assertIn("Read when work is scientifically material", human)
        self.assertIn("Read when maintaining context", human)
        commands = discovery["commands"]
        self.assertIsInstance(commands, list)
        assert isinstance(commands, list)
        self.assertEqual(
            [command for command, _ in reporting.INITIALIZED_TOOL_COMMANDS],
            [item["command"] for item in commands],
        )
        template_agents = (ROOT / "template" / "AGENTS.md").read_text(encoding="utf-8")
        for command, purpose in reporting.INITIALIZED_TOOL_COMMANDS:
            self.assertIn(f"`{command}`", human)
            self.assertIn(purpose, human)
            self.assertIn(f"`{command}`", template_agents)
        self.assertIn("optional bounded mechanics", str(discovery["boundary"]))

    def test_cli_initialized_and_starter_files_present_exit_contracts(self) -> None:
        target = self.root / "initialized"

        initialized_exit, initialized = self.run_json(
            ["init", str(target), "--mode", "new"]
        )
        existing_exit, existing = self.run_json(
            ["init", str(target), "--mode", "retrofit"]
        )

        self.assertEqual(0, initialized_exit)
        self.assertEqual("initialized", initialized["result"])
        self.assert_report_identity(initialized)
        self.assertEqual(0, existing_exit)
        self.assertEqual("starter_files_present", existing["result"])
        self.assertEqual(0, existing["summary"]["files_to_copy"])
        self.assertEqual(len(STARTER_INVENTORY), existing["summary"]["identical_files"])
        self.assertIs(True, existing["tool_discovery"]["reported_now"])
        self.assertEqual(
            "present",
            existing["tool_discovery"]["persistent_agent_guidance"],
        )
        self.assertIn(
            "review_project_context",
            [step["action"] for step in existing["next_steps"]],
        )
        self.assert_report_identity(existing)

    def test_cli_infers_new_and_retrofit_modes(self) -> None:
        new_target = self.root / "automatic-new"
        new_exit, new_payload = self.run_json(
            ["init", str(new_target), "--dry-run"]
        )

        retrofit_target = self.root / "automatic-retrofit"
        retrofit_target.mkdir()
        (retrofit_target / "README.md").write_text("existing\n", encoding="utf-8")
        retrofit_exit, retrofit_payload = self.run_json(
            ["init", str(retrofit_target), "--dry-run"]
        )

        self.assertEqual(0, new_exit)
        self.assertEqual("new", new_payload["mode"])
        self.assertEqual(0, retrofit_exit)
        self.assertEqual("retrofit", retrofit_payload["mode"])
        self.assertFalse((retrofit_target / "AGENTS.md").exists())

    def test_cli_dry_run_reports_ready_without_writing(self) -> None:
        target = self.root / "preview"

        exit_code, payload = self.run_json(
            ["init", str(target), "--mode", "new", "--dry-run"]
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("ready", payload["result"])
        self.assertTrue(payload["dry_run"])
        self.assertFalse(target.exists())
        self.assert_report_identity(payload)

    def test_cli_reports_required_agent_skills_and_targets(self) -> None:
        target = self.root / "agent-skills-preview"

        exit_code, payload = self.run_json(
            [
                "init",
                str(target),
                "--mode",
                "new",
                "--dry-run",
            ]
        )

        self.assertEqual(0, exit_code)
        skills = payload["agent_skills"]
        self.assertEqual(".agents/skills", skills["convention"])
        self.assertEqual("required_starter_files", skills["installation"])
        self.assertEqual(3, len(skills["files"]))
        for item in skills["files"]:
            self.assertEqual("available_after_apply", item["state"])
            self.assertEqual("create", item["disposition"])
            self.assertEqual(64, len(item["sha256"]))
            self.assertTrue(item["path"].startswith(".agents/skills/"))
            self.assertEqual(
                item["path"],
                agent_skill_path(item["name"]),
            )
        human = reporting.render_human(payload)
        self.assertNotIn("Canonical workflow", human)
        # Skill digests and states stay in the JSON report; the human report
        # lists the files it will create and the next steps.
        self.assertNotIn("SHA-256", human)

    def test_cli_blocked_and_error_exit_contracts(self) -> None:
        blocked_target = self.root / "blocked"
        blocked_target.mkdir()
        (blocked_target / "AGENTS.md").mkdir()

        blocked_exit, blocked = self.run_json(
            ["init", str(blocked_target), "--mode", "retrofit"]
        )

        self.assertEqual(2, blocked_exit)
        self.assertEqual("blocked", blocked["result"])
        self.assertEqual(1, blocked["summary"]["conflicts"])
        self.assertNotIn("tool_discovery", blocked)
        self.assertEqual("resolve_structural_conflicts", blocked["next_steps"][0]["action"])
        self.assertFalse((blocked_target / ".agent").exists())
        self.assert_report_identity(blocked)

        error_target = self.root / "error"
        error_target.mkdir()
        (error_target / "README.md").write_text("occupied\n", encoding="utf-8")

        error_exit, error = self.run_json(
            ["init", str(error_target), "--mode", "new"]
        )

        self.assertEqual(2, error_exit)
        self.assertEqual("error", error["result"])
        self.assertIn("missing or empty", error["message"])
        self.assert_report_identity(error)
        self.assertFalse((error_target / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
