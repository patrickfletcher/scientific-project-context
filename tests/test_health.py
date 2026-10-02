import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context import cli as spctx_cli  # noqa: E402
from scientific_project_context import health  # noqa: E402
from scientific_project_context import project  # noqa: E402
from scientific_project_context.project import (  # noqa: E402
    AGENT_SKILL_PATHS,
    SKILL_TRIGGER_SEPARATOR,
    apply_index_sync,
    plan_index_sync,
    plan_initialization,
)
from scientific_project_context.resources import (  # noqa: E402
    ResourceCatalog,
    ResourceEntry,
    calculate_bundle_sha256,
    load_filesystem_resources,
)


FILESYSTEM_CATALOG = load_filesystem_resources(ROOT / "template")


def write_fixture_file(root: Path, relative: str, content: str = "# Fixture\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def project_findings(root: Path) -> tuple[health.Finding, ...]:
    return health.check_project(FILESYSTEM_CATALOG, root).findings


class CLIContractTests(unittest.TestCase):
    def test_template_resource_contract_passes(self) -> None:
        result = health.check_template_resources(FILESYSTEM_CATALOG)

        self.assertEqual(health.TEMPLATE_RESOURCE_TARGET, result.target)
        self.assertEqual(FILESYSTEM_CATALOG.bundle_sha256, result.resource_bundle_sha256)
        self.assertEqual((), result.findings)

    def test_broken_json_contract_still_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = io.StringIO()

            result = spctx_cli.main(
                ["check", tmp, "--json"],
                catalog=FILESYSTEM_CATALOG,
                stdout=output,
            )

            payload = json.loads(output.getvalue())
            self.assertEqual(0, result)
            self.assertNotIn("result", payload)
            self.assertGreater(len(payload["findings"]), 0)
            self.assertEqual("DH-REQ-001", payload["findings"][0]["check_id"])
            self.assertEqual(health.BROKEN, payload["findings"][0]["severity"])

    def test_actual_repository_uses_the_same_lifecycle_and_index_contract(self) -> None:
        findings = project_findings(ROOT)
        index_plan = plan_index_sync(FILESYSTEM_CATALOG, ROOT)

        self.assertEqual((), findings)
        self.assertEqual("no_changes", index_plan.action)
        self.assertEqual(
            health.discover_specialized_owners(ROOT).owners,
            index_plan.specialized_owners,
        )
        for relative in AGENT_SKILL_PATHS:
            self.assertEqual(
                (ROOT / "template" / relative).read_bytes(),
                (ROOT / relative).read_bytes(),
            )

        retrofit_plan = plan_initialization(
            FILESYSTEM_CATALOG,
            ROOT,
            "retrofit",
        )

        self.assertEqual((), retrofit_plan.copy_files)
        self.assertEqual(
            {"AGENTS.md", ".context/project.md", ".context/scientific-practice.md"},
            set(retrofit_plan.retained_files),
        )
        self.assertEqual(set(AGENT_SKILL_PATHS), set(retrofit_plan.identical_files))
        self.assertEqual((), retrofit_plan.conflicts)


class LifecycleLayoutTests(unittest.TestCase):
    def create_lifecycle_layout(self, root: Path) -> None:
        write_fixture_file(
            root,
            "AGENTS.md",
            (ROOT / "template/AGENTS.md").read_text(encoding="utf-8"),
        )
        write_fixture_file(
            root,
            ".context/scientific-practice.md",
            (ROOT / "template/.context/scientific-practice.md").read_text(
                encoding="utf-8"
            ),
        )
        write_fixture_file(
            root,
            ".context/project.md",
            "# Project Context\n\n"
            "Purpose: keep compact current fixture context.\n"
            "Read when: changing or checking the fixture.\n"
            "Update when: fixture context changes.\n",
        )
        for relative in AGENT_SKILL_PATHS:
            write_fixture_file(
                root,
                relative,
                (ROOT / "template" / relative).read_text(encoding="utf-8"),
            )

    def test_lifecycle_scaffold_does_not_require_a_context_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)

            findings: list[health.Finding] = []
            health.check_context_index_pressure(root, findings)

            self.assertEqual([], findings)

    def test_malformed_required_agent_skill_is_a_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(
                root,
                ".agents/skills/spctx-project-context/SKILL.md",
                "# Missing YAML frontmatter\n",
            )

            findings = project_findings(root)
            skill_findings = [
                finding for finding in findings if finding.check_id == "DH-SKILL-001"
            ]

            self.assertEqual(1, len(skill_findings))
            self.assertEqual(health.BROKEN, skill_findings[0].severity)
            self.assertEqual(
                ".agents/skills/spctx-project-context/SKILL.md",
                skill_findings[0].path,
            )

    SKILL_RELATIVE = ".agents/skills/spctx-project-context/SKILL.md"
    CLAUDE_POINTER_RELATIVE = ".claude/skills/spctx-project-context/SKILL.md"

    def test_claude_pointer_that_matches_its_skill_is_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            description = project.parse_agent_skill_content(
                (root / self.SKILL_RELATIVE).read_bytes()
            ).description
            write_fixture_file(
                root,
                self.CLAUDE_POINTER_RELATIVE,
                project.build_claude_skill_stub(
                    "spctx-project-context", description
                ).decode("utf-8"),
            )

            self.assertEqual(
                [],
                [
                    finding
                    for finding in project_findings(root)
                    if finding.check_id == "DH-SKILL-004"
                ],
            )

    def test_claude_pointer_that_lost_its_skills_triggers_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(
                root,
                self.CLAUDE_POINTER_RELATIVE,
                project.build_claude_skill_stub(
                    "spctx-project-context", "Some other description."
                ).decode("utf-8"),
            )

            pointer_findings = [
                finding
                for finding in project_findings(root)
                if finding.check_id == "DH-SKILL-004"
            ]

            self.assertEqual(1, len(pointer_findings))
            self.assertEqual(health.UNFINISHED, pointer_findings[0].severity)
            self.assertEqual("description", pointer_findings[0].evidence)

    def write_tuned_skill(
        self,
        root: Path,
        *,
        description_suffix: str = "",
        replacement_description: str | None = None,
        body_suffix: str = "",
    ) -> None:
        lines = (
            (ROOT / "template" / self.SKILL_RELATIVE)
            .read_text(encoding="utf-8")
            .splitlines()
        )
        for index, line in enumerate(lines):
            if line.startswith("description: "):
                lines[index] = (
                    f"description: {replacement_description}"
                    if replacement_description is not None
                    else line + description_suffix
                )
                break
        text = "\n".join(lines) + "\n" + body_suffix
        write_fixture_file(root, self.SKILL_RELATIVE, text)

    def skill_drift_findings(self, root: Path, check_id: str) -> list[health.Finding]:
        return [
            finding for finding in project_findings(root) if finding.check_id == check_id
        ]

    def test_project_triggers_after_the_separator_are_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            self.write_tuned_skill(
                root,
                description_suffix=(
                    f' {SKILL_TRIGGER_SEPARATOR} "exclude these samples", '
                    '"refit the decay model".'
                ),
            )

            self.assertEqual([], self.skill_drift_findings(root, "DH-SKILL-002"))

    def test_rewritten_description_is_reported_as_informational(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            self.write_tuned_skill(
                root,
                replacement_description=(
                    'Use for requests such as "refresh the project context".'
                ),
            )

            findings = self.skill_drift_findings(root, "DH-SKILL-002")

            self.assertEqual(1, len(findings))
            self.assertEqual(health.NOTED, findings[0].severity)
            self.assertEqual(self.SKILL_RELATIVE, findings[0].path)

    def test_appending_triggers_without_the_separator_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            self.write_tuned_skill(root, description_suffix=' Say "exclude these samples".')

            findings = self.skill_drift_findings(root, "DH-SKILL-002")

            self.assertEqual(
                ["description: extended_without_separator"],
                [finding.evidence for finding in findings],
            )

    def test_modified_skill_body_is_reported_as_informational(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            self.write_tuned_skill(root, body_suffix="\n## Project Step\n\nRun the pipeline.\n")

            findings = self.skill_drift_findings(root, "DH-SKILL-003")

            self.assertEqual(1, len(findings))
            self.assertEqual(health.NOTED, findings[0].severity)

    def test_untouched_packaged_skills_report_no_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)

            drift = [
                finding
                for finding in project_findings(root)
                if finding.check_id in {"DH-SKILL-002", "DH-SKILL-003"}
            ]

            self.assertEqual([], drift)

    def test_diff_shows_only_regions_that_differ_from_the_packaged_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)

            self.assertEqual((), health.diff_managed_regions(FILESYSTEM_CATALOG, root))

            self.write_tuned_skill(
                root,
                description_suffix=f' {SKILL_TRIGGER_SEPARATOR} "exclude these samples".',
            )
            differences = health.diff_managed_regions(FILESYSTEM_CATALOG, root)

            self.assertEqual(1, len(differences))
            self.assertEqual("description", differences[0].region)
            self.assertEqual("extended", differences[0].state)
            self.assertIn("exclude these samples", differences[0].diff)

    def test_tuning_state_separates_project_phrasings_from_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)

            states = {
                entry.path: entry.state
                for entry in health.inspect_skill_tuning(FILESYSTEM_CATALOG, root)
            }
            self.assertEqual({"untuned"}, set(states.values()))
            self.assertEqual(3, len(states))

            self.write_tuned_skill(
                root,
                description_suffix=f' {SKILL_TRIGGER_SEPARATOR} "exclude these samples".',
            )
            tuned = {
                entry.path: entry.state
                for entry in health.inspect_skill_tuning(FILESYSTEM_CATALOG, root)
            }
            self.assertEqual("tuned", tuned[self.SKILL_RELATIVE])

            self.write_tuned_skill(root, replacement_description="Rewritten.")
            diverged = {
                entry.path: entry.state
                for entry in health.inspect_skill_tuning(FILESYSTEM_CATALOG, root)
            }
            self.assertEqual("diverged", diverged[self.SKILL_RELATIVE])

    def test_repeating_packaged_skill_text_is_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            echoed = (
                "Classify findings as observed, proposed interpretation, or unknown. "
                "Filenames alone do not establish scientific meaning or change authority."
            )
            agents = root / "AGENTS.md"
            agents.write_text(
                agents.read_text(encoding="utf-8") + f"\n## Local Rule\n\n{echoed}\n",
                encoding="utf-8",
            )

            echoes = [
                finding
                for finding in project_findings(root)
                if finding.check_id == "DH-DUP-001"
            ]

            self.assertEqual(1, len(echoes))
            self.assertEqual("AGENTS.md", echoes[0].path)
            self.assertIn("packaged", echoes[0].message)

    def test_duplication_among_project_files_is_pressure_not_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            passage = (
                "Every excluded recording needs a specific recorded reason that a "
                "reviewer can check against the acquisition notes later.\n"
            )
            write_fixture_file(
                root,
                ".context/curation.md",
                "# Curation\n\nPurpose: own curation.\nRead when: curating.\n"
                f"Update when: curation changes.\n\n{passage}",
            )
            write_fixture_file(
                root,
                ".context/task-board.md",
                "# Tasks\n\nPurpose: track work.\nRead when: planning.\n"
                f"Update when: work changes.\n\n{passage}",
            )

            result = health.check_project(FILESYSTEM_CATALOG, root)
            repeated = [
                passage
                for passage in result.repeated_passages
                if passage.kind == "project"
            ]

            self.assertEqual(1, len(repeated))
            self.assertIn("specific recorded reason", repeated[0].passage)
            self.assertEqual(
                [],
                [
                    finding
                    for finding in result.findings
                    if finding.check_id == "DH-DUP-001"
                ],
            )

    def test_generated_inventory_and_code_blocks_do_not_count_as_duplication(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            shared_command = (
                "```\nspctx check . --diff and then rerun the whole pipeline "
                "from the repository root every single time\n```\n"
            )
            write_fixture_file(
                root,
                ".context/curation.md",
                "# Curation\n\nPurpose: own curation.\nRead when: curating.\n"
                f"Update when: curation changes.\n\n{shared_command}",
            )
            write_fixture_file(
                root,
                ".context/task-board.md",
                "# Tasks\n\nPurpose: track work.\nRead when: planning.\n"
                f"Update when: work changes.\n\n{shared_command}",
            )

            duplication = [
                finding
                for finding in project_findings(root)
                if finding.check_id == "DH-DUP-001"
            ]

            self.assertEqual([], duplication)

    def test_two_specialized_owners_without_context_index_get_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(root, ".context/task-board.md")
            write_fixture_file(root, ".context/active/pipeline-overview.md")

            findings: list[health.Finding] = []
            health.check_context_index_pressure(root, findings)

            self.assertEqual(["DH-ROUTE-002"], [finding.check_id for finding in findings])
            self.assertEqual(health.UNFINISHED, findings[0].severity)
            self.assertIn("2 focused documents", findings[0].evidence)

    def test_one_specialized_owner_does_not_require_context_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(root, ".context/task-board.md")

            findings: list[health.Finding] = []
            health.check_context_index_pressure(root, findings)

            self.assertEqual([], findings)

    def test_generated_context_inventory_is_parsed_and_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            owner = ".context/active/method-validation.md"
            write_fixture_file(root, owner)
            write_fixture_file(
                root,
                ".context/README.md",
                "# Context Index\n\n"
                "Purpose: route current fixture context.\n"
                "Read when: selecting additional fixture context.\n"
                "Update when: current fixture sources change.\n\n"
                f"{health.CONTEXT_INVENTORY_BEGIN}\n"
                f"- `{owner}`\n"
                f"{health.CONTEXT_INVENTORY_END}\n",
            )

            findings: list[health.Finding] = []
            active = health.parse_context_index(root, findings)

            self.assertEqual([owner], active)
            self.assertEqual([], findings)

    def test_generated_context_index_requires_exact_marker_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(
                root,
                ".context/README.md",
                f"# Context Index\n\n{health.CONTEXT_INVENTORY_BEGIN}\n",
            )

            findings: list[health.Finding] = []
            health.parse_context_index(root, findings)

            self.assertEqual(["DH-ROUTE-001"], [finding.check_id for finding in findings])
            self.assertEqual(health.BROKEN, findings[0].severity)

    def test_human_authored_context_index_without_generated_markers_is_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(
                root,
                ".context/README.md",
                "# Context Index\n\n"
                "- `.context/project.md`\n"
                "- `.context/method-validation.md`\n",
            )

            findings: list[health.Finding] = []
            active = health.parse_context_index(root, findings)

            self.assertEqual([], active)
            self.assertEqual(["DH-ROUTE-001"], [finding.check_id for finding in findings])
            self.assertEqual(health.UNFINISHED, findings[0].severity)
            self.assertIn("human-authored", findings[0].message.lower())

    def test_generated_context_index_rejects_noncanonical_inventory_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(root, ".context/task-board.md")
            write_fixture_file(
                root,
                ".context/README.md",
                "# Context Index\n\n"
                f"{health.CONTEXT_INVENTORY_BEGIN}\n"
                "- `.context/task-board.md`\n"
                "Hand-written note inside the generated block.\n"
                f"{health.CONTEXT_INVENTORY_END}\n",
            )

            findings: list[health.Finding] = []
            health.parse_context_index(root, findings)

            self.assertEqual(["DH-ROUTE-001"], [finding.check_id for finding in findings])
            self.assertIn("non-canonical", findings[0].message)

    def test_generated_context_index_rejects_unsafe_paths_without_dereferencing_them(self) -> None:
        cases = (
            "../outside.md",
            "/absolute/outside.md",
            "C:/outside.md",
            ".context/active/../task-board.md",
            ".context\\active\\owner.md",
            ".context/active",
        )
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for index, unsafe in enumerate(cases):
                with self.subTest(path=unsafe):
                    root = base / str(index)
                    self.create_lifecycle_layout(root)
                    write_fixture_file(
                        root,
                        ".context/README.md",
                        "# Context Index\n\n"
                        f"{health.CONTEXT_INVENTORY_BEGIN}\n"
                        f"- `{unsafe}`\n"
                        f"{health.CONTEXT_INVENTORY_END}\n",
                    )

                    findings = project_findings(root)

                    self.assertIn("DH-ROUTE-001", [finding.check_id for finding in findings])
                    self.assertTrue(
                        any("unsafe or non-canonical" in finding.message for finding in findings)
                    )

    def test_symlinked_custom_owner_blocks_before_inventory_file_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            owner = root / ".context" / "active" / "linked-owner.md"
            owner.parent.mkdir(parents=True)
            try:
                owner.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")
            write_fixture_file(
                root,
                ".context/README.md",
                "# Context Index\n\n"
                f"{health.CONTEXT_INVENTORY_BEGIN}\n"
                "- `.context/active/linked-owner.md`\n"
                f"{health.CONTEXT_INVENTORY_END}\n",
            )

            findings = project_findings(root)

            self.assertIn("DH-ROUTE-003", [finding.check_id for finding in findings])

    def test_generated_inventory_must_exactly_match_owner_discovery(self) -> None:
        cases = {
            "missing": (
                [".context/task-board.md", ".context/active/data-dictionary.md"],
                [".context/task-board.md"],
                "missing:",
            ),
            "extra": (
                [".context/task-board.md"],
                [".context/task-board.md", ".context/notes.md"],
                "extra:",
            ),
            "duplicate": (
                [".context/task-board.md"],
                [".context/task-board.md", ".context/task-board.md"],
                "duplicates:",
            ),
            "order": (
                [".context/task-board.md", ".context/roadmap.md"],
                [".context/task-board.md", ".context/roadmap.md"],
                "deterministic order",
            ),
        }

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name, (owners, inventory, evidence) in cases.items():
                with self.subTest(name=name):
                    root = base / name
                    self.create_lifecycle_layout(root)
                    for owner in owners:
                        write_fixture_file(root, owner)
                    expected = health.discover_specialized_owners(root).owners
                    if name == "order":
                        inventory = list(reversed(expected))
                    write_fixture_file(
                        root,
                        ".context/README.md",
                        "# Context Index\n\n"
                        f"{health.CONTEXT_INVENTORY_BEGIN}\n"
                        + "".join(f"- `{path}`\n" for path in inventory)
                        + f"{health.CONTEXT_INVENTORY_END}\n",
                    )

                    findings: list[health.Finding] = []
                    health.check_context_index_pressure(root, findings)

                    self.assertEqual(["DH-ROUTE-002"], [finding.check_id for finding in findings])
                    self.assertIn(evidence, findings[0].evidence)

    def test_generated_inventory_matching_discovery_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(root, ".context/task-board.md")
            write_fixture_file(root, ".context/active/data-dictionary.md")
            owners = health.discover_specialized_owners(root).owners
            write_fixture_file(
                root,
                ".context/README.md",
                "# Context Index\n\n"
                f"{health.CONTEXT_INVENTORY_BEGIN}\n"
                + "".join(f"- `{path}`\n" for path in owners)
                + f"{health.CONTEXT_INVENTORY_END}\n",
            )

            findings: list[health.Finding] = []
            health.check_context_index_pressure(root, findings)

            self.assertEqual([], findings)

    def test_project_named_direct_context_is_discovered_without_a_kind_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            custom = ".context/experiment-notes.md"
            write_fixture_file(
                root,
                custom,
                "# Experiment Notes\n\n"
                "Purpose: retain current experiment interpretation.\n"
                "Read when: changing or interpreting the experiment.\n"
                "Update when: inputs, interpretation, or evidence changes.\n",
            )

            discovery = health.discover_specialized_owners(root)

            self.assertFalse(discovery.conflicts)
            self.assertIn(custom, discovery.owners)

    def test_context_guidance_warns_without_rewriting_project_meaning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            custom = ".context/active/custom-method.md"
            write_fixture_file(
                root,
                custom,
                "# Custom Method\n\nPurpose: own the current custom method.\n",
            )
            findings: list[health.Finding] = []

            health.check_context_guidance(root, findings)

            self.assertEqual(["DH-GUIDE-001"], [finding.check_id for finding in findings])
            self.assertEqual(custom, findings[0].path)
            self.assertIn("read when", findings[0].evidence)
            self.assertIn("update when", findings[0].evidence)

    def test_context_index_pressure_for_zero_one_and_two_owners(self) -> None:
        paths = (".context/decision-register.md", ".context/active/method-validation.md")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for count in range(3):
                with self.subTest(count=count):
                    root = base / f"owner-count-{count}"
                    self.create_lifecycle_layout(root)
                    for path in paths[:count]:
                        write_fixture_file(root, path)

                    findings: list[health.Finding] = []
                    health.check_context_index_pressure(root, findings)

                    self.assertEqual(
                        ["DH-ROUTE-002"] if count >= 2 else [],
                        [finding.check_id for finding in findings],
                    )

    def test_unsafe_owner_structure_blocks_health_and_index_consistently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            active = root / ".context" / "active"
            active.write_text("not a directory\n", encoding="utf-8")

            findings: list[health.Finding] = []
            health.check_context_index_pressure(root, findings)
            plan = plan_index_sync(FILESYSTEM_CATALOG, root)

            self.assertEqual(["DH-ROUTE-003"], [finding.check_id for finding in findings])
            self.assertEqual(health.BROKEN, findings[0].severity)
            self.assertEqual("blocked", plan.action)
            self.assertEqual(plan.conflicts, health.discover_specialized_owners(root).conflicts)

    def test_symlinked_context_index_is_a_health_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(root, ".context/task-board.md")
            real_index = root / "index-target.md"
            real_index.write_text(
                "# Context Index\n\n"
                f"{health.CONTEXT_INVENTORY_BEGIN}\n"
                "- `.context/task-board.md`\n"
                f"{health.CONTEXT_INVENTORY_END}\n",
                encoding="utf-8",
            )
            context_index = root / ".context" / "README.md"
            try:
                context_index.symlink_to(real_index)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")

            findings = project_findings(root)

            index_findings = [finding for finding in findings if finding.check_id == "DH-ROUTE-003"]
            self.assertEqual(1, len(index_findings))
            self.assertEqual(health.BROKEN, index_findings[0].severity)
            self.assertEqual(".context/README.md", index_findings[0].path)

    def test_non_owner_design_symlink_blocks_before_recursive_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            linked = root / ".context" / "notes" / "linked.md"
            linked.parent.mkdir()
            try:
                linked.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")

            findings = project_findings(root)

            self.assertEqual(["DH-ROUTE-003"], [finding.check_id for finding in findings])
            self.assertEqual(".context/notes/linked.md", findings[0].path)

    def test_required_file_directory_is_reported_without_reading_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            project = root / ".context" / "project.md"
            project.unlink()
            project.mkdir()

            findings = project_findings(root)

            self.assertEqual(["DH-REQ-001"], [finding.check_id for finding in findings])
            self.assertEqual(".context/project.md", findings[0].path)

    def test_populated_lifecycle_with_specialized_owners_and_generated_index_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_lifecycle_layout(root)
            write_fixture_file(
                root,
                ".context/project.md",
                "# Project Context\n\n"
                "Purpose: keep compact current fixture context.\n"
                "Read when: changing or checking the fixture.\n"
                "Update when: fixture context changes.\n\n"
                "`.context/scientific-practice.md` is the stable scientific contract.\n\n"
                "**What could make the result wrong even if the code runs**: stale routing.\n"
                "**Smallest useful check**: compare discovery with the generated inventory.\n"
                "**Current evidence and limits**: deterministic fixture only.\n",
            )
            owners = (
                (".context/task-board.md", "task", "tasks move"),
                (".context/active/pipeline-overview.md", "pipeline stage", "stages change"),
            )
            for owner, topic, trigger in owners:
                write_fixture_file(
                    root,
                    owner,
                    "# Reviewed Owner\n\n"
                    f"Purpose: own the current fixture {topic}.\n"
                    f"Read when: revisiting a fixture {topic}.\n"
                    f"Update when: {trigger}.\n",
                )
            write_fixture_file(root, "src/example.py", "VALUE = 1\n")
            apply_index_sync(plan_index_sync(FILESYSTEM_CATALOG, root))

            findings = project_findings(root)

            self.assertEqual((), findings)

class HealthBoundaryTests(unittest.TestCase):
    def test_linked_target_and_linked_ancestor_raise_health_error_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "real"
            real.mkdir()
            child = real / "child"
            child.mkdir()
            linked = root / "linked"
            try:
                linked.symlink_to(real, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"directory symlink creation is unavailable: {exc}")

            for target in (linked, linked / "child"):
                with self.subTest(target=target), self.assertRaisesRegex(
                    health.HealthError,
                    "symlink|junction|reparse",
                ):
                    health.check_project(FILESYSTEM_CATALOG, target)

    def test_owner_discovery_reports_case_only_collisions_when_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / ".context" / "active"
            active.mkdir(parents=True)
            (active / "CaseOwner.md").write_text("# One\n", encoding="utf-8")
            (active / "caseowner.md").write_text("# Two\n", encoding="utf-8")
            if len(tuple(active.iterdir())) < 2:
                self.skipTest("filesystem does not support case-distinct sibling names")

            discovery = health.discover_specialized_owners(root)

            self.assertEqual(1, len(discovery.conflicts))
            self.assertIn("differs from", discovery.conflicts[0])

    def test_invalid_utf8_template_resource_raises_health_error(self) -> None:
        original = FILESYSTEM_CATALOG.get("template/AGENTS.md")
        invalid_content = b"\xff"
        invalid_entry = ResourceEntry(
            resource_id=original.resource_id,
            collection=original.collection,
            relative_path=original.relative_path,
            content=invalid_content,
            sha256=hashlib.sha256(invalid_content).hexdigest(),
        )
        template_entries = tuple(
            invalid_entry if entry.resource_id == invalid_entry.resource_id else entry
            for entry in FILESYSTEM_CATALOG.template_entries
        )
        invalid_catalog = ResourceCatalog(
            template_entries=template_entries,
            bundle_sha256=calculate_bundle_sha256(template_entries),
        )

        with self.assertRaisesRegex(
            health.HealthError,
            "not valid UTF-8: AGENTS.md",
        ):
            health.check_template_resources(invalid_catalog)


class DraftOwnerReviewTests(unittest.TestCase):
    def test_current_draft_owner_is_reported_but_reference_copy_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = f"**{health.DRAFT_CONTEXT_MARKER}**: review this context.\n"
            write_fixture_file(root, ".context/active/method-validation.md", marker)
            write_fixture_file(
                root,
                ".context/MAINTENANCE.md",
                f"Remove `{health.DRAFT_CONTEXT_MARKER}` after review.\n",
            )
            write_fixture_file(root, ".context/reference/example.md", marker)

            findings: list[health.Finding] = []
            health.check_draft_owners(root, findings)

            self.assertEqual(["DH-REVIEW-001"], [finding.check_id for finding in findings])
            self.assertEqual(".context/active/method-validation.md", findings[0].path)
            self.assertEqual(health.UNFINISHED, findings[0].severity)


if __name__ == "__main__":
    unittest.main()
