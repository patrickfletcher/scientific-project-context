from __future__ import annotations

import itertools
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context import health  # noqa: E402


class ScientistFacingStarterContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (TEMPLATE / relative_path).read_text(encoding="utf-8")

    def test_shipped_markdown_is_byte_consistent(self) -> None:
        """These files are compared byte for byte, so their formatting cannot vary."""

        problems: list[str] = []
        for path in sorted(TEMPLATE.rglob("*.md")):
            name = path.relative_to(TEMPLATE).as_posix()
            raw = path.read_bytes()
            if b"\r" in raw:
                problems.append(f"{name} contains a carriage return")
            if not raw.endswith(b"\n"):
                problems.append(f"{name} does not end with a newline")
            if b"\n\n\n" in raw:
                problems.append(f"{name} contains a blank line run")
            if b"\t" in raw:
                problems.append(f"{name} contains a tab")
            for number, line in enumerate(raw.split(b"\n"), start=1):
                if line.rstrip() != line:
                    problems.append(f"{name}:{number} has trailing whitespace")

        self.assertEqual([], problems)

    def test_the_review_marker_the_skill_teaches_is_the_one_the_check_finds(self) -> None:
        """A formatting contract only works when the guidance and the check agree."""

        skill = self.read(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn(f"`{health.DRAFT_CONTEXT_MARKER}`", skill)
        for written_form in (
            health.DRAFT_CONTEXT_MARKER,
            f"**{health.DRAFT_CONTEXT_MARKER}**",
            f"**{health.DRAFT_CONTEXT_MARKER}**: still being reviewed",
            f"  {health.DRAFT_CONTEXT_MARKER}",
        ):
            with self.subTest(written_form=written_form):
                self.assertIsNotNone(
                    health.DRAFT_CONTEXT_MARKER_RE.search(written_form)
                )

    def test_starter_states_nothing_twice(self) -> None:
        """The product must meet the standard its repeated-passage check applies."""

        words = {
            path.relative_to(TEMPLATE).as_posix(): health._comparable_words(
                path.read_text(encoding="utf-8")
            )
            for path in TEMPLATE.rglob("*.md")
        }
        repeats: list[str] = []
        for left, right in itertools.combinations(sorted(words), 2):
            for start, length in health._shared_runs(words[left], words[right]):
                passage = " ".join(words[left][start : start + length])
                repeats.append(f"{left} and {right} share {length} words: {passage}")

        self.assertEqual([], repeats)

    def test_project_prompts_cover_research_work_beyond_software_packages(self) -> None:
        project = self.read(".context/project.md")
        for phrase in (
            "Main materials and entry points",
            "How a result or behavior is checked",
            "Operating conditions that affect the science",
            "workflow completes or looks plausible",
            "tolerance, uncertainty",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, project)

    def test_project_context_routes_operational_detail_elsewhere(self) -> None:
        """Real use duplicated environment and commands into all three places."""

        project = self.read(".context/project.md")
        self.assertIn("`AGENTS.md` owns environment, commands, and conventions", project)
        self.assertIn("`README.md` owns human setup", project)

    def test_agents_file_prompts_for_essentials_and_states_ownership(self) -> None:
        agents = self.read("AGENTS.md")
        for phrase in (
            "## Project Essentials",
            "**Environment**",
            "**Run and test**",
            "**Protected inputs**",
            "**Conventions**",
            # Real use showed agents reporting the command missing and working around it.
            "**Context tools**",
            "`spctx check .`",
            "## Where Facts Live",
            "this project's vocabulary",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, agents)

    def test_context_skill_teaches_placement_before_drafting(self) -> None:
        skill = self.read(".agents/skills/spctx-project-context/SKILL.md")
        placement = skill.index("## 2. Put Each Fact in the Right Place")
        drafting = skill.index("## 4. Draft the Compact Context")
        self.assertLess(placement, drafting)
        for phrase in (
            "copied into all three places",
            "which environment it is installed in",
            "readable by an\ninterested outsider",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_every_skill_announces_itself_before_acting(self) -> None:
        """Real use could not tell whether a procedure ran or was merely echoed."""

        for name in (
            "spctx-project-context",
            "spctx-public-writing",
            "spctx-scientific-change",
        ):
            with self.subTest(name=name):
                skill = self.read(f".agents/skills/{name}/SKILL.md")
                self.assertIn(f"you are using `{name}`", skill)

    def test_public_writing_skill_owns_audience_stage_and_currency(self) -> None:
        skill = self.read(".agents/skills/spctx-public-writing/SKILL.md")
        for phrase in (
            "## 1. Name the Reader and What They Must Do",
            "## 2. Establish the Project's Stage",
            "exploratory",
            "supporting a decision or claim",
            "Transient counts in durable text",
            "Check every command, path, filename, and option",
            "authorship, credit, acknowledgement, and citation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_context_skill_defers_public_writing_and_supports_trigger_tuning(self) -> None:
        skill = self.read(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("use `spctx-public-writing` instead", skill)
        self.assertIn("## 11. Tune the Skill Triggers to This Project", skill)

    def test_context_skill_localizes_the_practice_contract_from_real_sources(self) -> None:
        """The extension point existed for months and went unused because nothing named it."""

        skill = self.read(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("| localize | 1, 10, 12 |", skill)
        for phrase in (
            "## 10. Make the Practice Contract This Project's",
            "Do not invent a field's conventions",
            "prior papers, methods sections, or protocols",
            # Declining is an answer, so the prompt cannot nag a settled project forever.
            "Deciding that the shared core is enough is a complete answer",
            "A project that adopted an earlier version has no such section",
            "Do not move project conventions inside the markers",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_practice_contract_prompts_for_this_project_outside_the_core(self) -> None:
        practice = self.read(".context/scientific-practice.md")
        section = practice[practice.index("<!-- END SPCTX SCIENTIFIC PRACTICE CORE v1 -->") :]
        for phrase in (
            "## This Project's Practice",
            "Standards, protocols, or reporting conventions this field expects",
            "Review or approval this work owes",
            "Where this project deliberately differs from the core",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, section)

    def test_scientific_change_uses_the_relied_on_list_as_its_trigger(self) -> None:
        """Anything is exploratory until someone decides to rely on it."""

        skill = self.read(".agents/skills/spctx-scientific-change/SKILL.md")
        self.assertIn("that short list is\nthe test", skill)
        self.assertIn("exploratory until someone decides to rely on it", skill)
        self.assertIn("Promotion is the user's decision", skill)
        self.assertIn("**What later work relies on**", self.read(".context/project.md"))

    def test_scientific_change_skill_can_pay_the_deferred_evidence_cost(self) -> None:
        """Deferring evidence to promotion only works if promotion says how to pay it."""

        skill = self.read(".agents/skills/spctx-scientific-change/SKILL.md")
        self.assertIn("rebuild its evidence", skill)
        self.assertIn("A gap is a finding to report, not a blank to fill", skill)

    def test_context_skill_covers_upgrading_to_a_new_package_version(self) -> None:
        skill = self.read(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("## 9. Upgrade to a New Package Version", skill)
        self.assertIn("spctx check . --diff", skill)

    def test_practice_core_covers_traceability_uncertainty_and_evidence_boundaries(self) -> None:
        practice = self.read(".context/scientific-practice.md").casefold()
        for phrase in (
            "researchers and their assistants",
            "input sources and provenance",
            "exploratory",
            "uncertainty or variation",
            "computational reproducibility",
            "independent replicability",
            "generalizability beyond the tested setting",
            "technical access does not establish permission",
            "discrepant, null, and negative results",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, practice)

    def test_practice_core_scales_evidence_to_what_depends_on_the_result(self) -> None:
        """One adopting project hand-wrote this boundary twice because the core lacked it."""

        practice = self.read(".context/scientific-practice.md")
        core = practice[
            practice.index("<!-- BEGIN SPCTX SCIENTIFIC PRACTICE CORE v1 -->") : practice.index(
                "<!-- END SPCTX SCIENTIFIC PRACTICE CORE v1 -->"
            )
        ]
        for phrase in (
            "## What Will Depend on the Result",
            "**Exploratory**",
            "**Supporting a decision or claim**",
            "**Public or published**",
            "owed when a result is promoted, not when it is produced",
            "Never raise a level silently",
            # A level may relax evidence, never protection, honesty, or authority.
            "protected material stays protected",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, core)

    def test_practice_core_gates_checks_and_evidence_on_that_level(self) -> None:
        practice = self.read(".context/scientific-practice.md")
        self.assertIn("Above the exploratory level, name the smallest check", practice)
        self.assertIn("For a result something already depends on, keep enough identity", practice)

    def test_scientific_change_skill_stops_at_the_exploratory_level(self) -> None:
        skill = self.read(".agents/skills/spctx-scientific-change/SKILL.md")
        for phrase in (
            "which intended-use level in the practice contract applies",
            "stop here",
            "Skip this step while the work is exploratory",
            "Choose one check, not a suite",
            "Scale the record to the level",
            "Report the level you worked at",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_public_writing_skill_defers_the_levels_to_the_contract(self) -> None:
        """The ladder has one home; writing applies it rather than redefining it."""

        skill = self.read(".agents/skills/spctx-public-writing/SKILL.md")
        stage = skill[skill.index("## 2. Establish") : skill.index("## 3. Write Only")]
        self.assertIn("`.context/scientific-practice.md` defines the levels", stage)
        self.assertIn("spctx-scientific-change", stage)

    def test_skill_recognizes_notebooks_instruments_and_non_code_checks(self) -> None:
        skill = self.read(".agents/skills/spctx-scientific-change/SKILL.md")
        for phrase in (
            "data transformation or exclusion rule",
            "notebook",
            "acquisition or instrument workflow",
            "check or observation",
            "Perform the Work and Check It",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_primary_context_route_activates_maintenance_and_scientific_practice(self) -> None:
        agents = self.read("AGENTS.md")
        route = agents[agents.index("<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->") :]
        self.assertLess(
            agents.index("<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->"),
            agents.index("## Project Essentials"),
        )
        for phrase in (
            ".context/project.md",
            "authoritative source in the same turn",
            "spctx-project-context/SKILL.md",
            "scientific-practice.md",
            "spctx-scientific-change/SKILL.md",
            "spctx-public-writing/SKILL.md",
            "retire, or upgrade context",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, route)

    def test_route_names_every_shipped_skill(self) -> None:
        """Listing some skills but not others leaves the rest reachable only by luck."""

        agents = self.read("AGENTS.md")
        route = agents[agents.index("<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->") :]
        for skill in sorted(path.name for path in (TEMPLATE / ".agents/skills").iterdir()):
            with self.subTest(skill=skill):
                self.assertIn(f"{skill}/SKILL.md", route)


if __name__ == "__main__":
    unittest.main()
