from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context import (  # noqa: E402
    DISTRIBUTION_NAME,
    __version__,
)
from scientific_project_context import cli, health, reporting  # noqa: E402
from scientific_project_context.resources import (  # noqa: E402
    ResourceCatalog,
    load_filesystem_resources,
)


PROJECT_CONTEXT = """# Project Context

Purpose: keep the fixture's current scientific and execution context compact.
Read when: changing or checking the fixture analysis.
Update when: the fixture purpose, method, evidence, or next step changes.

## Purpose and Useful Outcome

**What this project does**: Analyze a fixed three-value dataset and report its arithmetic mean.

**Who uses the result and what useful outcome they need**: A manuscript author needs a checked companion result.

## Current Reality

**Main files or components**: The project contains one fixed input and one analysis routine.

**How to run and check it**: Run the local analysis test.

## Current Work

**Current focus**: Confirm the companion result before review.

**Next meaningful step**: Retain the observed test result with the manuscript materials.

## Scientific and Artifact Context

**What must not be changed silently**: The fixed three-value input is protected scientific input.

**What could make the result wrong even if the code runs**: Parsing or averaging the wrong values would produce a plausible but incorrect mean.

**Smallest useful check**: Analyze values 1, 2, and 3; require an arithmetic mean of exactly 2.

**Current evidence and limits**: The fixed example passes locally; other encodings and datasets remain untested.

**Important assumptions or settings**: Each input value has equal weight.

**What later work relies on**: nothing yet

`.context/scientific-practice.md` is the stable scientific contract for this project.
"""


def create_initialized_project(root: Path, catalog: ResourceCatalog) -> None:
    """Create the starter project with reviewed scientific context."""

    for entry in catalog.starter_entries:
        destination = root.joinpath(*entry.relative_path.split("/"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(entry.content)
    (root / ".context" / "project.md").write_text(
        PROJECT_CONTEXT,
        encoding="utf-8",
    )


def tree_snapshot(root: Path) -> tuple[tuple[str, str, bytes | None], ...]:
    snapshot: list[tuple[str, str, bytes | None]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot.append((relative, "directory", None))
        elif path.is_file():
            snapshot.append((relative, "file", path.read_bytes()))
        else:
            snapshot.append((relative, "other", None))
    return tuple(snapshot)


class PackageHealthCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.project = self.root / "project"
        self.catalog = load_filesystem_resources(ROOT / "template")
        create_initialized_project(self.project, self.catalog)

    def run_json(self, target: Path | None = None) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        exit_code = cli.main(
            ["check", str(target or self.project), "--json"],
            catalog=self.catalog,
            stdout=output,
        )
        return exit_code, json.loads(output.getvalue())

    def test_clean_project_with_platform_paths_passes_with_common_identity(self) -> None:
        github_instructions = self.project / ".github" / "instructions.md"
        github_instructions.parent.mkdir()
        github_instructions.write_text("Project-owned agent instructions.\n", encoding="utf-8")
        claude_skill = self.project / ".claude" / "skills" / "example" / "SKILL.md"
        claude_skill.parent.mkdir(parents=True)
        claude_skill.write_text("# Project-owned skill\n", encoding="utf-8")

        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        self.assertNotIn("result", payload)
        self.assertEqual("check", payload["operation"])
        self.assertEqual(reporting.REPORT_SCHEMA_VERSION, payload["report_schema_version"])
        self.assertEqual(
            {health.BROKEN: 0, health.UNFINISHED: 0, health.NOTED: 0},
            payload["observed"],
        )
        self.assertEqual([], payload["findings"])
        self.assertIn("structure only", payload["validation_boundary"])
        target = payload["target"]
        self.assertIsInstance(target, dict)
        assert isinstance(target, dict)
        self.assertTrue(Path(str(target["path"])).samefile(self.project))

        producer = payload["producer"]
        self.assertIsInstance(producer, dict)
        assert isinstance(producer, dict)
        self.assertEqual(DISTRIBUTION_NAME, producer["distribution"])
        self.assertEqual(__version__, producer["version"])
        self.assertEqual(self.catalog.bundle_sha256, producer["resource_bundle_sha256"])
        for init_only_field in (
            "mode",
            "dry_run",
            "semantic_initialization",
            "context_adoption",
        ):
            self.assertNotIn(init_only_field, payload)

    def test_a_project_with_no_routing_block_is_told_it_is_not_active(self) -> None:
        agents = self.project / "AGENTS.md"
        text = agents.read_text(encoding="utf-8")
        begin = text.index("<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->")
        end_marker = "<!-- END SPCTX PROJECT CONTEXT ROUTING v1 -->"
        end = text.index(end_marker) + len(end_marker)
        agents.write_text(text[:begin] + text[end:], encoding="utf-8")

        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        self.assertEqual(
            ["DH-ROUTE-005"], [item["check_id"] for item in payload["findings"]]
        )
        self.assertEqual("absent", payload["state"]["agent_route"])

        output = io.StringIO()
        cli.main(["check", str(self.project)], catalog=self.catalog, stdout=output)
        self.assertIn("Agent routing: not active", output.getvalue())

    def test_project_additions_outside_the_scientific_core_are_allowed(self) -> None:
        practice = self.project / ".context/scientific-practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8")
            + "\n## Project Convention\n\nUse the accepted local reference dataset.\n",
            encoding="utf-8",
        )

        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        self.assertEqual([], payload["findings"])

    def test_untouched_practice_contract_is_reported_without_being_a_finding(self) -> None:
        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        self.assertEqual([], payload["findings"])
        self.assertEqual("none", payload["state"]["practice_notes"])

        output = io.StringIO()
        cli.main(["check", str(self.project)], catalog=self.catalog, stdout=output)
        self.assertIn("This project's own practice notes: none yet", output.getvalue())

    def test_answering_the_practice_prompts_settles_the_contract(self) -> None:
        """Saying the shared core is enough counts; leaving the prompts as shipped does not."""

        practice = self.project / ".context/scientific-practice.md"
        text = practice.read_text(encoding="utf-8")
        head, _, tail = text.partition("## This Project's Practice")
        _, _, rest = tail.partition("## Keeping Application Proportional")
        practice.write_text(
            head
            + "## This Project's Practice\n\nThe shared core is the whole of what this work owes.\n\n"
            + "## Keeping Application Proportional"
            + rest,
            encoding="utf-8",
        )

        _, payload = self.run_json()

        self.assertEqual("present", payload["state"]["practice_notes"])

    def test_a_section_the_package_does_not_ship_also_counts(self) -> None:
        practice = self.project / ".context/scientific-practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8")
            + "\n## Reporting Convention\n\nReport replication at the animal level.\n",
            encoding="utf-8",
        )

        _, payload = self.run_json()

        self.assertEqual("present", payload["state"]["practice_notes"])

    def test_an_empty_relied_on_list_is_reported_as_exploratory(self) -> None:
        """The default is exploratory; the report says so instead of leaving it implicit."""

        _, payload = self.run_json()

        self.assertEqual("nothing_named", payload["state"]["relied_on"])

        output = io.StringIO()
        cli.main(["check", str(self.project)], catalog=self.catalog, stdout=output)
        self.assertIn("stays exploratory until something is added", output.getvalue())

    def test_a_named_relied_on_item_is_reported_back(self) -> None:
        project_context = self.project / ".context/project.md"
        project_context.write_text(
            PROJECT_CONTEXT.replace(
                "**What later work relies on**: nothing yet",
                "**What later work relies on**: the exclusion rule for saturated traces",
            ),
            encoding="utf-8",
        )

        _, payload = self.run_json()

        self.assertEqual("named", payload["state"]["relied_on"])

    def test_an_unanswered_starter_prompt_is_counted_not_mistaken_for_an_answer(self) -> None:
        project_context = self.project / ".context/project.md"
        project_context.write_text(
            PROJECT_CONTEXT.replace(
                "**What later work relies on**: nothing yet",
                "**What later work relies on**: [the settled choices later work assumes]",
            ),
            encoding="utf-8",
        )

        _, payload = self.run_json()

        self.assertEqual("unanswered", payload["state"]["relied_on"])
        self.assertEqual(
            [{"path": "AGENTS.md", "unanswered": 6}, {"path": ".context/project.md", "unanswered": 1}],
            payload["state"]["starter_prompts"],
        )

        output = io.StringIO()
        cli.main(["check", str(self.project)], catalog=self.catalog, stdout=output)
        self.assertIn("Starter prompts still holding their shipped text", output.getvalue())
    def test_context_pointing_at_a_vanished_file_is_reported(self) -> None:
        project_context = self.project / ".context/project.md"
        project_context.write_text(
            project_context.read_text(encoding="utf-8")
            + "\nThe analysis lives in `.context/gone.md`.\n",
            encoding="utf-8",
        )

        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        stale = [item for item in payload["findings"] if item["check_id"] == "DH-STALE-001"]
        self.assertEqual(1, len(stale))
        self.assertEqual(".context/gone.md", stale[0]["evidence"])
        self.assertEqual(health.UNFINISHED, stale[0]["severity"])

    def test_paths_that_are_not_pointers_are_left_alone(self) -> None:
        """Ratios, globs, absolute paths, and trees the project lacks are not drift."""

        project_context = self.project / ".context/project.md"
        project_context.write_text(
            project_context.read_text(encoding="utf-8")
            + "\nSee `F340/F380`, `data/*.xls`, `/etc/hosts.conf`, and `.github/workflows/ci.yml`.\n",
            encoding="utf-8",
        )

        _, payload = self.run_json()

        self.assertEqual([], [i for i in payload["findings"] if i["check_id"] == "DH-STALE-001"])

    def test_modified_scientific_core_is_reported_as_broken_without_failing_the_run(self) -> None:
        practice = self.project / ".context/scientific-practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8").replace(
                "A plausible agent-generated explanation is not evidence.",
                "A plausible agent-generated explanation might be evidence.",
            ),
            encoding="utf-8",
        )

        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        self.assertEqual(1, payload["observed"][health.BROKEN])
        self.assertIn("DH-PRACTICE-001", [item["check_id"] for item in payload["findings"]])

    def test_missing_project_route_is_left_to_init_not_reported_every_run(self) -> None:
        project_context = self.project / ".context/project.md"
        project_context.write_text(
            PROJECT_CONTEXT.replace(
                "`.context/scientific-practice.md` is the stable scientific contract for this project.\n",
                "",
            ),
            encoding="utf-8",
        )

        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        self.assertEqual([], payload["findings"])

    def test_unfinished_human_and_json_outputs_are_equivalent_and_do_not_write(self) -> None:
        owner = self.project / ".context" / "active" / "method.md"
        owner.parent.mkdir()
        owner.write_text(
            "DRAFT CONTEXT - REVIEW REQUIRED\n\n"
            "Purpose: record the current method.\n"
            "Read when: changing the method.\n"
            "Update when: the method changes.\n",
            encoding="utf-8",
        )
        before = tree_snapshot(self.project)

        json_exit, payload = self.run_json()
        human_output = io.StringIO()
        human_exit = cli.main(
            ["check", str(self.project)],
            catalog=self.catalog,
            stdout=human_output,
        )

        self.assertEqual(0, json_exit)
        self.assertEqual(0, human_exit)
        self.assertEqual(
            {health.BROKEN: 0, health.UNFINISHED: 1, health.NOTED: 0},
            payload["observed"],
        )
        self.assertEqual(1, len(payload["findings"]))
        finding = payload["findings"][0]
        self.assertIsInstance(finding, dict)
        assert isinstance(finding, dict)
        self.assertEqual(health.UNFINISHED, finding["severity"])

        human = human_output.getvalue()
        self.assertNotIn("- Result:", human)
        self.assertIn(str(payload["validation_boundary"]), human)
        for key in (
            "check_id",
            "severity",
            "category",
            "path",
            "message",
            "evidence",
            "owner_doc",
            "next_action",
        ):
            self.assertIn(str(finding[key]), human)
        self.assertNotIn("- Dry run:", human)
        self.assertNotIn("Semantic initialization", human)
        self.assertEqual(before, tree_snapshot(self.project))

    def test_human_managed_index_is_warning_only_at_the_cli_boundary(self) -> None:
        (self.project / ".context" / "README.md").write_text(
            "# Context Index\n\n"
            "Purpose: route current context.\n"
            "Read when: selecting additional context.\n"
            "Update when: current context sources change.\n\n"
            "- `.context/project.md`\n"
            "- `docs/method-validation.md`\n",
            encoding="utf-8",
        )

        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        self.assertEqual(
            {health.BROKEN: 0, health.UNFINISHED: 1, health.NOTED: 0},
            payload["observed"],
        )
        self.assertEqual("DH-ROUTE-001", payload["findings"][0]["check_id"])
        self.assertEqual(health.UNFINISHED, payload["findings"][0]["severity"])

    def test_a_missing_starter_file_is_reported_as_broken_with_a_zero_exit(self) -> None:
        (self.project / "AGENTS.md").unlink()

        exit_code, payload = self.run_json()

        self.assertEqual(0, exit_code)
        self.assertGreater(payload["observed"][health.BROKEN], 0)
        self.assertEqual(health.BROKEN, payload["findings"][0]["severity"])

    def test_missing_target_returns_two_and_operation_error_report(self) -> None:
        missing = self.root / "missing"

        exit_code, payload = self.run_json(missing)

        self.assertEqual(2, exit_code)
        self.assertEqual("error", payload["result"])
        self.assertEqual("check", payload["operation"])
        self.assertEqual({"path": str(missing)}, payload["target"])
        self.assertIn("message", payload)
        producer = payload["producer"]
        self.assertEqual(self.catalog.bundle_sha256, producer["resource_bundle_sha256"])
        for init_only_field in ("mode", "dry_run", "semantic_initialization"):
            self.assertNotIn(init_only_field, payload)

if __name__ == "__main__":
    unittest.main()
