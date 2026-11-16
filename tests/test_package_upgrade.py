from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context import cli, health, upgrade  # noqa: E402
from scientific_project_context.project import (  # noqa: E402
    AGENT_SKILLS,
    CONTEXT_ROUTE_BEGIN,
    CONTEXT_ROUTE_BLOCK,
    CONTEXT_ROUTE_END,
    OperationError,
    SKILL_TRIGGER_SEPARATOR,
    build_claude_skill_stub,
    parse_agent_skill_content,
)
from scientific_project_context.resources import load_filesystem_resources  # noqa: E402

DEV25 = ROOT / "tests" / "fixtures" / "release-0.1.0.dev25"
PHRASINGS = f'{SKILL_TRIGGER_SEPARATOR} "refit the decay model".'


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class UpgradeTests(unittest.TestCase):
    """Agents dropped packaged trigger categories when they replaced packaged text by hand."""

    def setUp(self) -> None:
        self.catalog = load_filesystem_resources(ROOT / "template")
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "project"
        shutil.copytree(DEV25, self.project, ignore=shutil.ignore_patterns("README.md"))
        skill = self.project / ".agents/skills/spctx-scientific-change/SKILL.md"
        text = skill.read_text(encoding="utf-8")
        description = parse_agent_skill_content(text.encode("utf-8")).description
        skill.write_text(text.replace(description, f"{description} {PHRASINGS}", 1), encoding="utf-8")
        agents = self.project / "AGENTS.md"
        agents.write_text("# Our lab\n\nKeep raw data read-only.\n\n" + agents.read_text(encoding="utf-8"), encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, *args: str) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        code = cli.main(["upgrade", str(self.project), *args, "--json"], catalog=self.catalog, stdout=output)
        return code, json.loads(output.getvalue())

    def actions(self, payload: dict[str, object]) -> dict[tuple[str, str], str]:
        return {(item["path"], item["region"]): item["action"] for item in payload["regions"]}

    def test_a_release_project_upgrades_to_the_current_package_and_keeps_its_own_text(self) -> None:
        before = snapshot(self.project)

        code, payload = self.run_cli()

        self.assertEqual(0, code)
        self.assertEqual("upgraded", payload["result"])
        actions = self.actions(payload)
        self.assertEqual("replaced", actions[("AGENTS.md", "routing block")])
        self.assertEqual("replaced", actions[(".context/scientific-practice.md", "scientific-practice core")])
        self.assertEqual(
            "replaced",
            actions[(".agents/skills/spctx-scientific-change/SKILL.md", "skill description")],
        )
        self.assertIn(".agents/skills/spctx-literature/SKILL.md", payload["created_files"])
        after = snapshot(self.project)
        # Text outside the tracked regions is untouched, byte for byte.
        self.assertEqual(before[".context/project.md"], after[".context/project.md"])
        self.assertTrue(after["AGENTS.md"].startswith(b"# Our lab\n\nKeep raw data read-only.\n\n"))
        self.assertEqual(
            before["AGENTS.md"].split(CONTEXT_ROUTE_END.encode())[1],
            after["AGENTS.md"].split(CONTEXT_ROUTE_END.encode())[1],
        )
        skill = parse_agent_skill_content(after[".agents/skills/spctx-scientific-change/SKILL.md"])
        packaged = parse_agent_skill_content(
            self.catalog.get("template/.agents/skills/spctx-scientific-change/SKILL.md").content
        )
        self.assertEqual(f"{packaged.description} {PHRASINGS}", skill.description)
        self.assertEqual(packaged.body, skill.body)
        result = health.check_project(self.catalog, self.project)
        self.assertEqual({"broken": 0, "unfinished": 0, "noted": 0}, result.counts)
        self.assertEqual("no_changes", self.run_cli()[1]["result"])

    def test_a_dry_run_writes_nothing_and_shows_each_change(self) -> None:
        before = snapshot(self.project)

        code, payload = self.run_cli("--dry-run")

        self.assertEqual(0, code)
        self.assertEqual("planned", payload["result"])
        self.assertEqual(before, snapshot(self.project))
        routing = next(item for item in payload["regions"] if item["region"] == "routing block")
        self.assertIn("+", routing["diff"])
        human = io.StringIO()
        cli.main(["upgrade", str(self.project), "--dry-run"], catalog=self.catalog, stdout=human)
        self.assertIn("```diff", human.getvalue())
        self.assertIn("does not install", cli.build_parser().format_help() + human.getvalue() + str(payload))

    def test_edited_text_is_skipped_until_the_user_asks_for_it_to_be_replaced(self) -> None:
        practice = self.project / ".context/scientific-practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8").replace("## Who Decides", "## Who Decides Here"),
            encoding="utf-8",
        )

        _, payload = self.run_cli()

        core = (".context/scientific-practice.md", "scientific-practice core")
        self.assertEqual("skipped_edited", self.actions(payload)[core])
        self.assertIn("Who Decides Here", practice.read_text(encoding="utf-8"))
        _, payload = self.run_cli("--replace-edited")
        self.assertEqual("replaced", self.actions(payload)[core])
        self.assertNotIn("Who Decides Here", practice.read_text(encoding="utf-8"))

    def test_a_missing_routing_block_is_never_inserted(self) -> None:
        agents = self.project / "AGENTS.md"
        text = agents.read_text(encoding="utf-8")
        start = text.index(CONTEXT_ROUTE_BEGIN)
        end = text.index(CONTEXT_ROUTE_END) + len(CONTEXT_ROUTE_END)
        agents.write_text(text[:start] + text[end:], encoding="utf-8")

        _, payload = self.run_cli()

        self.assertEqual("reported", self.actions(payload)[("AGENTS.md", "routing block")])
        self.assertNotIn(CONTEXT_ROUTE_BEGIN, agents.read_text(encoding="utf-8"))

    def test_duplicated_markers_block_the_whole_run(self) -> None:
        agents = self.project / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8") + "\n" + CONTEXT_ROUTE_BLOCK + "\n", encoding="utf-8")
        before = snapshot(self.project)

        code, payload = self.run_cli()

        self.assertEqual(2, code)
        self.assertEqual("blocked", payload["result"])
        self.assertEqual(before, snapshot(self.project))

    def test_crlf_files_keep_their_line_endings(self) -> None:
        agents = self.project / "AGENTS.md"
        agents.write_bytes(agents.read_bytes().replace(b"\n", b"\r\n"))

        self.run_cli()

        content = agents.read_bytes()
        self.assertNotIn(b"\n", content.replace(b"\r\n", b""))
        self.assertIn(CONTEXT_ROUTE_BLOCK.replace("\n", "\r\n").encode(), content)

    def test_a_file_changed_after_planning_stops_the_run_and_restores_earlier_files(self) -> None:
        plan = upgrade.plan_upgrade(self.catalog, self.project)
        before = snapshot(self.project)
        later = plan.files[-1]
        (self.project / later.relative_path).write_bytes(later.original + b"\nedited\n")
        before[later.relative_path] = (self.project / later.relative_path).read_bytes()

        with self.assertRaises(OperationError):
            upgrade.apply_upgrade(plan)

        self.assertEqual(before, snapshot(self.project))

    def test_a_linked_instruction_file_is_refused(self) -> None:
        agents = self.project / "AGENTS.md"
        outside = Path(self.tmp.name) / "elsewhere.md"
        outside.write_bytes(agents.read_bytes())
        agents.unlink()
        try:
            os.symlink(outside, agents)
        except OSError:
            self.skipTest("symlinks unavailable")

        code, payload = self.run_cli()

        self.assertEqual(2, code)
        self.assertEqual(outside.read_bytes(), (Path(self.tmp.name) / "elsewhere.md").read_bytes())

    def test_generated_pointers_follow_their_skill_and_edited_ones_are_left_alone(self) -> None:
        names = [name for name in AGENT_SKILLS if (self.project / f".agents/skills/{name}/SKILL.md").exists()]
        for name in names:
            description = parse_agent_skill_content(
                (self.project / f".agents/skills/{name}/SKILL.md").read_bytes()
            ).description
            pointer = self.project / f".claude/skills/{name}/SKILL.md"
            pointer.parent.mkdir(parents=True)
            pointer.write_bytes(build_claude_skill_stub(name, description))
        edited = self.project / ".claude/skills/spctx-public-writing/SKILL.md"
        edited.write_bytes(edited.read_bytes() + b"\nOur own note.\n")

        _, payload = self.run_cli()

        actions = self.actions(payload)
        self.assertEqual("regenerated", actions[(".claude/skills/spctx-scientific-change/SKILL.md", "Claude pointer")])
        self.assertEqual("reported", actions[(".claude/skills/spctx-public-writing/SKILL.md", "Claude pointer")])
        self.assertIn(".claude/skills/spctx-literature/SKILL.md", payload["created_files"])
        self.assertIn(b"Our own note.", edited.read_bytes())
        self.assertEqual([], [f for f in health.check_project(self.catalog, self.project).findings
                              if f.check_id == "DH-SKILL-004" and "scientific-change" in f.path])

    def test_a_description_that_would_grow_too_long_blocks_instead_of_truncating(self) -> None:
        skill = self.project / ".agents/skills/spctx-scientific-change/SKILL.md"
        text = skill.read_text(encoding="utf-8")
        description = parse_agent_skill_content(text.encode("utf-8")).description
        packaged_length = len(
            parse_agent_skill_content(
                self.catalog.get("template/.agents/skills/spctx-scientific-change/SKILL.md").content
            ).description
        )
        filler = " " + "x" * max(0, 1023 - len(description))
        skill.write_text(text.replace(description, description + filler, 1), encoding="utf-8")
        if packaged_length + len(PHRASINGS) + len(filler) + 1 <= 1024:
            self.skipTest("the packaged description leaves room for these phrasings")

        code, payload = self.run_cli()

        self.assertEqual(2, code)
        self.assertTrue(any("1024 characters" in message for message in payload["blocked"]))

    def test_an_invalid_skill_blocks_the_run_even_when_pointers_exist(self) -> None:
        for name in AGENT_SKILLS:
            canonical = self.project / f".agents/skills/{name}/SKILL.md"
            if canonical.exists():
                pointer = self.project / f".claude/skills/{name}/SKILL.md"
                pointer.parent.mkdir(parents=True)
                description = parse_agent_skill_content(canonical.read_bytes()).description
                pointer.write_bytes(build_claude_skill_stub(name, description))
        skill = self.project / ".agents/skills/spctx-public-writing/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("---\n", "---\nlicense: MIT\n", 1), encoding="utf-8")
        before = snapshot(self.project)

        code, payload = self.run_cli()

        self.assertEqual(2, code)
        self.assertEqual("blocked", payload["result"])
        self.assertEqual(before, snapshot(self.project))

    def test_a_pointer_added_in_the_run_carries_the_new_description(self) -> None:
        name = "spctx-scientific-change"
        other = "spctx-public-writing"
        description = parse_agent_skill_content(
            (self.project / f".agents/skills/{other}/SKILL.md").read_bytes()
        ).description
        pointer = self.project / f".claude/skills/{other}/SKILL.md"
        pointer.parent.mkdir(parents=True)
        pointer.write_bytes(build_claude_skill_stub(other, description))

        self.run_cli()

        created = parse_agent_skill_content((self.project / f".claude/skills/{name}/SKILL.md").read_bytes())
        canonical = parse_agent_skill_content((self.project / f".agents/skills/{name}/SKILL.md").read_bytes())
        self.assertEqual(canonical.description, created.description)

    def test_undoing_a_failed_run_keeps_file_permissions(self) -> None:
        plan = upgrade.plan_upgrade(self.catalog, self.project)
        first = self.project / plan.files[0].relative_path
        os.chmod(first, 0o644)
        plan = upgrade.plan_upgrade(self.catalog, self.project)
        later = plan.files[-1]
        (self.project / later.relative_path).write_bytes(later.original + b"\nedited\n")

        with self.assertRaises(OperationError):
            upgrade.apply_upgrade(plan)

        self.assertEqual(0o644, first.stat().st_mode & 0o777)



if __name__ == "__main__":
    unittest.main()
