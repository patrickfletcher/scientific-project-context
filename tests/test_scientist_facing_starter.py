from __future__ import annotations

import itertools
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from scientific_project_context import health  # noqa: E402
import style_metrics  # noqa: E402

INLINE_CODE = re.compile(r"`[^`\n]*`")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


class ScientistFacingStarterContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (TEMPLATE / relative_path).read_text(encoding="utf-8")

    def flat(self, relative_path: str) -> str:
        """The file with whitespace collapsed, so line wrapping cannot break a phrase."""

        return " ".join(self.read(relative_path).split())

    def section(self, text: str, start: str, end: str) -> str:
        return text[text.index(start) : text.index(end)]

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
        self.assertIn("`AGENTS.md` holds environment, commands, and conventions", project)
        self.assertIn("`README.md` holds human setup", project)

    def test_context_is_current_state_rewritten_in_place(self) -> None:
        """Real use turned per-run update rules into run logs that two cleanups did not fix."""

        project = self.read(".context/project.md")
        self.assertIn("about one screen", project)
        self.assertIn("**Current findings and limits**", project)
        self.assertNotIn("input and procedure identity", project)
        skill = self.flat(".agents/skills/spctx-project-context/SKILL.md")
        for phrase in (
            "is a log, not context",
            "It does not name an event such as a run finishing",
            "rewrite it as current state. Do not trim entries",
            "change that rule too, or the log grows back",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_shipped_text_uses_the_glossary_terms(self) -> None:
        """Trials copied this product's role, gate, and level words into their prose.

        The words to avoid live in `.context/glossary.md`, so one list drives both
        the writing and this test. Inline code is ignored, so a skill can still name
        an earlier field title it reads.
        """

        glossary = (ROOT / ".context" / "glossary.md").read_text(encoding="utf-8")
        avoided: list[str] = []
        for line in glossary.splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if line.startswith("|") and len(cells) == 3 and cells[2] != "Avoid":
                avoided.extend(re.findall(r"`([^`]+)`", cells[2]))
        self.assertGreater(len(avoided), 20)
        for path in sorted(TEMPLATE.rglob("*.md")):
            text = INLINE_CODE.sub(" ", COMMENT.sub(" ", path.read_text(encoding="utf-8")))
            for term in avoided:
                with self.subTest(path=path.relative_to(TEMPLATE).as_posix(), term=term):
                    self.assertIsNone(re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE))

    def test_procedural_sentences_stay_short(self) -> None:
        """Long packed sentences were the hardest instructions to follow; lists replace them."""

        procedural = [
            *sorted((TEMPLATE / ".agents/skills").glob("*/SKILL.md")),
            TEMPLATE / "AGENTS.md",
            TEMPLATE / ".context/scientific-practice.md",
        ]
        long: list[str] = []
        for path in procedural:
            for sentence in style_metrics.sentences(path.read_text(encoding="utf-8")):
                if sentence.startswith(("Purpose:", "Use when:", "Read when:", "Update when:")):
                    continue
                if style_metrics.word_count(sentence) > 25:
                    long.append(f"{path.relative_to(TEMPLATE).as_posix()}: {sentence[:90]}")
        self.assertEqual([], long)

    def test_starter_keeps_proposals_codes_and_conflicts_in_their_place(self) -> None:
        """Real use grew numbered codes, hedged adopted text, and ranked the safeguards."""

        agents = self.flat("AGENTS.md")
        self.assertIn("Name things by what they are, not by numbered codes", agents)
        conflicts = self.section(agents, "## When Guidance Conflicts", "## Working Style")
        self.assertIn("rank does not settle it: ask the user", conflicts)
        self.assertIn("For exploratory work, follow the user's current instructions", conflicts)
        self.assertIn("copy the `Context tools` line that `spctx init` prints", agents)
        project = self.read(".context/project.md")
        self.assertIn("**Protected inputs**", project)
        self.assertIn("Keep ideas not yet adopted here", project)
        self.assertIn("**What this builds on**", project)

    def test_agents_file_prompts_for_essentials_and_states_ownership(self) -> None:
        agents = self.flat("AGENTS.md")
        for phrase in (
            "## Project Essentials",
            "**Environment**",
            "**Run and test**",
            "**Protected inputs**",
            "**Conventions**",
            # Real use showed agents reporting the command missing and working around it.
            "**Context tools**",
            "`spctx check .`",
            "`spctx upgrade . --dry-run`",
            "## Where Facts Live",
            "this project's vocabulary",
            "If the project keeps a glossary, use its terms and avoid its listed words",
            # The strict reproducibility standard belongs to publication alone.
            "a public version that reproduces a published result for any reader",
            "Leave out what did not happen, what stayed unchanged, and who approved it",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, agents)

    def test_context_skill_teaches_placement_before_drafting(self) -> None:
        skill = self.flat(".agents/skills/spctx-project-context/SKILL.md")
        placement = skill.index("## 2. Put Each Fact in the Right Place")
        drafting = skill.index("## 4. Draft the Compact Context")
        self.assertLess(placement, drafting)
        for phrase in (
            "gets copied into all three places",
            "copy the line that the `spctx init` report prints",
            "readable by an interested outsider",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_every_skill_announces_itself_before_acting(self) -> None:
        """Real use could not tell whether a procedure ran or was merely echoed."""

        for name in (
            "spctx-literature",
            "spctx-project-context",
            "spctx-public-writing",
            "spctx-scientific-change",
        ):
            with self.subTest(name=name):
                skill = self.read(f".agents/skills/{name}/SKILL.md")
                self.assertIn(f"you are using `{name}`", skill)

    def test_literature_skill_identifies_reads_and_bounds_outside_sources(self) -> None:
        """Three trials invented source-strength labels and citation rules, and unchecked recollections steered design."""

        skill = self.flat(".agents/skills/spctx-literature/SKILL.md")
        for phrase in (
            "Never write an identifier, title, author list, year, or venue from memory",
            "Mark a reference you have not looked up as recalled",
            "Resolve a persistent identifier",
            "Check whether a retraction, correction, or expression of concern exists",
            "Say what you read: full text, abstract, title only",
            "Separate what the authors measured from what they concluded",
            "Cite the primary source for a primary finding",
            "If the project already keeps a list of sources, use it",
            '"No study found" describes that search, not the world',
            "name the assumption that carries a result from one to the other",
            "If you cannot reach the source from here, say so and mark it unchecked",
            "goes through `spctx-scientific-change`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)
        writing = self.flat(".agents/skills/spctx-public-writing/SKILL.md")
        self.assertIn("Cite only sources checked with `spctx-literature`", writing)

    def test_public_writing_skill_owns_audience_stage_and_currency(self) -> None:
        skill = self.flat(".agents/skills/spctx-public-writing/SKILL.md")
        for phrase in (
            "## 1. Name the Reader and What They Must Do",
            "## 2. Establish the Project's Stage",
            "exploratory, depended on, and published",
            "Transient counts in durable text",
            "Check every command, path, filename, and option",
            "authorship, credit, acknowledgement, and citation",
            "If the reader is not clear, name the one you assume and continue",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_context_skill_defers_public_writing_and_supports_trigger_tuning(self) -> None:
        skill = self.read(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("use `spctx-public-writing` instead", skill)
        self.assertIn("## 11. Tune the Skill Triggers to This Project", skill)

    def test_context_skill_localizes_the_practice_contract_from_real_sources(self) -> None:
        """The extension point existed for months and went unused because nothing named it."""

        skill = self.flat(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("| localize | 1, 10, 13 |", skill)
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
            "Review this work owes before it is published",
            "Where this project deliberately differs from the core",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, section)

    def test_scientific_change_uses_the_relied_on_list_as_its_trigger(self) -> None:
        """Anything is exploratory until someone decides that later work depends on it."""

        skill = self.flat(".agents/skills/spctx-scientific-change/SKILL.md")
        self.assertIn("is the default test", skill)
        # Real use found presence in the list too mechanical; a real dependency counts.
        self.assertIn("If something already depends on the result but is not listed, it is not exploratory", skill)
        self.assertIn("stays exploratory until someone decides that later work will depend on it", skill)
        self.assertIn("That decision belongs to the user", skill)
        self.assertIn("**What later work depends on**", self.read(".context/project.md"))

    def test_scientific_change_keeps_exploratory_work_in_the_reply_and_on_the_question(self) -> None:
        """Real use recorded every run and engineered around compute one approved step at a time."""

        skill = self.flat(".agents/skills/spctx-scientific-change/SKILL.md")
        for phrase in (
            # Every exploratory study met "name the question"; the decision and stop rule held.
            "name the decision it could change and when it will stop",
            "list it as a lead in your reply instead of running it",
            "adopt it as the working default, keep it as an option, or set it aside",
            "Do not build variants, guards, or retry chains",
            "Say in your reply what it showed",
            "do not add an entry for the run",
            "Lead with what the work showed about the scientific question",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_scientific_change_skill_can_pay_the_deferred_evidence_cost(self) -> None:
        """Deferring evidence only works if the procedure says how to pay it later."""

        skill = self.flat(".agents/skills/spctx-scientific-change/SKILL.md")
        self.assertIn("rebuild its evidence from what exists", skill)
        self.assertIn("A gap is a finding to report, not a blank to fill", skill)

    def test_context_skill_covers_upgrading_to_a_new_package_version(self) -> None:
        skill = self.read(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("## 9. Upgrade to a New Package Version", skill)
        upgrade = self.section(skill, "## 9. Upgrade", "## 10.")
        # Byte replacement belongs to the command; agents dropped trigger categories doing it by hand.
        self.assertIn("spctx upgrade . --dry-run", upgrade)
        self.assertIn("--replace-edited", upgrade)
        steps = [line.split(".", 1)[0] for line in upgrade.splitlines() if line[:1].isdigit()]
        # An earlier package shipped this list with a step number repeated.
        self.assertEqual([str(n) for n in range(1, len(steps) + 1)], steps)

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

        practice = " ".join(self.read(".context/scientific-practice.md").split())
        core = self.section(
            practice,
            "<!-- BEGIN SPCTX SCIENTIFIC PRACTICE CORE v1 -->",
            "<!-- END SPCTX SCIENTIFIC PRACTICE CORE v1 -->",
        )
        for phrase in (
            "## What Will Depend on the Result",
            "**Exploratory**, the default",
            "**Depended on**",
            "**Published**",
            "must reproduce the published result for any reader who runs it",
            "This is the one strict reproducibility standard",
            "Evidence is owed when later work starts to depend on a result, not when the result is produced",
            # Real use found the list test too mechanical; dependence is what counts.
            "A dependency is real whether or not it is listed yet",
            "Mark a reference you recall but have not looked up as recalled",
            # A level may relax evidence, never protection, honesty, or who decides.
            "Protected inputs stay protected",
            # Real use narrated compliance after every step; the rules are met by acting.
            "Meet them by what you do, not by saying so",
            "Permission to run a step is not evidence",
            "not retelling it in every later summary",
            "Change a protected input only when the request clearly means to",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, core)

    def test_practice_core_gates_checks_and_evidence_on_that_level(self) -> None:
        practice = self.read(".context/scientific-practice.md")
        self.assertIn("Above the exploratory level, name the smallest check", practice)
        self.assertIn("For a result something already depends on, keep enough identity", practice)
        # Real use read an ungated staleness rule as an obligation on exploratory work.
        self.assertIn("No check, evidence record, or staleness marking is owed", practice)
        self.assertIn("When something such a result rests on changes", practice)

    def test_practice_core_identifies_code_by_version_not_by_source_hashes(self) -> None:
        """Real use wrote scripts that hashed their own source and refused to run on a change."""

        practice = self.read(".context/scientific-practice.md")
        self.assertNotIn("file hashes", practice)
        for phrase in (
            "the code version as a Git commit",
            # Every trial converged on commit and settings; checksums only where a source can change.
            "add a checksum when the source could change under the same name",
            "never make code refuse to run because its source changed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, practice)
        skill = self.read(".agents/skills/spctx-scientific-change/SKILL.md")
        self.assertIn("not a guard to build into code", skill)

    def test_context_skill_maintenance_gates_staleness_and_finds_readers_of_retired_files(self) -> None:
        skill = self.flat(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("Exploratory results need neither", skill)
        # Retiring a document once broke a script that read it by path.
        self.assertIn("It lists every file in the repository that names the document", skill)
        self.assertIn("It has no user names", skill)

    def test_install_on_request_uses_the_recorded_source_never_a_public_index(self) -> None:
        # The package name is unpublished, so installing it by name could fetch someone else's package.
        skill = self.flat(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("install a new version of scientific-project-context (`spctx`)", skill)
        self.assertIn("Never install this package by name from a public package index", skill)
        self.assertIn("Use the upgrade command in the instruction file's `Context tools` line", skill)

    def test_upgrade_restores_its_own_procedure_first_and_works_from_packaged_text(self) -> None:
        """An upgrade followed the project's older copy, and wrote always-read lines from the core."""

        upgrade = self.section(
            self.flat(".agents/skills/spctx-project-context/SKILL.md"), "## 9. Upgrade", "## 10."
        )
        self.assertIn("1. If this skill's own body differs from the packaged one, run `spctx upgrade .` first", upgrade)
        self.assertIn("Compare the rest of the instruction file with the packaged one", upgrade)
        self.assertIn("A restatement for a different reader or moment is not a duplicate", upgrade)

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
        self.assertLess(
            agents.index("<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->"),
            agents.index("## Project Essentials"),
        )
        route = " ".join(agents[agents.index("<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->") :].split())
        for phrase in (
            ".context/project.md",
            "Rewrite that part in place",
            "Keep run history, unchanged items, and approvals in Git and the conversation",
            # Every trial project wrote this default by hand before the route carried it.
            "Work is exploratory unless",
            "Write no review marker, review document, or evidence record",
            "Before a side investigation, name the decision it could change",
            "Change a protected input only when the request clearly means to",
            "spctx-project-context/SKILL.md",
            "scientific-practice.md",
            "spctx-scientific-change/SKILL.md",
            "spctx-public-writing/SKILL.md",
            "spctx-literature/SKILL.md",
            "refresh, review, or upgrade context",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, route)

    def test_the_index_is_the_one_list_of_context_documents(self) -> None:
        """Real use kept four separately maintained lists of the same documents."""

        agents = " ".join(self.read("AGENTS.md").split())
        route = agents[agents.index("<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->") :]
        self.assertIn("`.context/index.md` lists every other context document", route)
        self.assertIn("The index is generated; never edit it by hand", route)
        self.assertIn("Keep no other list", agents)
        project = self.read(".context/project.md")
        self.assertIn("keep no list of them here", project)
        skill = self.flat(".agents/skills/spctx-project-context/SKILL.md")
        self.assertIn("Do not keep another list of them", skill)
        upgrade = self.section(skill, "## 9. Upgrade", "## 10.")
        self.assertIn("Resolve what `spctx check .` reports about the index", upgrade)
        self.assertNotIn("README", upgrade)
        index = self.read(".context/index.md")
        self.assertTrue(index.rstrip("\n").endswith("<!-- END GENERATED CONTEXT INVENTORY -->"))
        self.assertIn("Every other Markdown file under `.context/`, in any folder", index)

    def test_context_skill_splits_by_trigger_and_reviews_context(self) -> None:
        """Trials grew context in shapes the log rule did not name and needed audits to find them."""

        skill = self.flat(".agents/skills/spctx-project-context/SKILL.md")
        for phrase in (
            "Split by why a passage changes, not by how long a document is",
            "narration of when and how a number was measured",
            "A plan is finite",
            "Copy a measured number or a decision into context only as a link",
            "Write a procedure, protocol, or test method as numbered steps, one action per step",
            "keep the project's terms in one glossary",
            "| review | 1, 6, 12, 13 |",
            "## 12. Review Context",
            "Run `spctx check . --inventory`",
            "Look for contradictions first",
            "Write the result as a short dated report outside `.context/`",
            # Markers lingered on documents the user had asked for.
            "only if the document holds an interpretation you drafted that nobody has confirmed",
            "If nothing changed, do not ask",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)

    def test_upgrade_reconciles_overrides_and_lists_what_earlier_versions_left(self) -> None:
        """Every trial wrote overrides, and old wording and code outlived the text that caused them."""

        upgrade = self.section(
            self.flat(".agents/skills/spctx-project-context/SKILL.md"), "## 9. Upgrade", "## 10."
        )
        for phrase in (
            "Upgrade on the branch that others merge from",
            "Compare the rest of the practice file with the packaged one",
            "offer to rename it to `What later work depends on`",
            "Keep the lines specific to this project, and delete the restatement",
            "List what earlier versions of this system left in the project's own text and code",
            "code only on an explicit request",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, upgrade)

    def test_route_names_every_shipped_skill(self) -> None:
        """Listing some skills but not others leaves the rest reachable only by luck."""

        agents = self.read("AGENTS.md")
        route = agents[agents.index("<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->") :]
        for skill in sorted(path.name for path in (TEMPLATE / ".agents/skills").iterdir()):
            with self.subTest(skill=skill):
                self.assertIn(f"{skill}/SKILL.md", route)


if __name__ == "__main__":
    unittest.main()
