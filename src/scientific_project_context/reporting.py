"""Versioned reports for Scientific Project Context operations."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from typing import Mapping, Sequence

from . import DISTRIBUTION_NAME, __version__
from .health import BROKEN, NOTED, UNFINISHED, HealthResult, ManagedDifference, RELIED_ON_FIELD
from .project import (
    IndexSyncPlan,
    IndexSyncResult,
    InitializationPlan,
    InitializationResult,
    CLAUDE_IMPORT_LINE,
    CLAUDE_INSTRUCTION_PATH,
    SCIENTIFIC_PRACTICE_BEGIN,
    SCIENTIFIC_PRACTICE_END,
    SCIENTIFIC_PRACTICE_PATH,
    CONTEXT_ROUTE_BEGIN,
    CONTEXT_ROUTE_BLOCK,
    CONTEXT_ROUTE_END,
    AGENT_SKILLS,
    agent_skill_path,
    claude_skill_path,
    managed_block_state,
)


REPORT_SCHEMA_VERSION = 14
HEALTH_VALIDATION_BOUNDARY = (
    "structure only; this does not check whether the science is right, whether the "
    "work reproduces elsewhere, or whether anything is ready to publish"
)
PRACTICE_LOCALIZATION_SUMMARY = {
    "none": "none yet, so the shared core is the whole contract",
    "present": "written",
}
# `check` reports state rather than a verdict, so these describe what each
# observed value means for the reader instead of scoring the project.
AGENT_ROUTE_SUMMARY = {
    "exact": "active; agents reading this project's instructions will find its context",
    "modified": "active, but the routing block no longer matches the installed package",
    "invalid": "unreadable; the routing markers in `AGENTS.md` are damaged",
    "absent": "not active; no instruction file here carries the routing block",
    "missing": "not active; this project has no `AGENTS.md`",
}
RELIED_ON_SUMMARY = {
    "named": "named, so a change that touches it owes a check and an evidence note",
    "nothing_named": (
        "nothing named, so every change here stays exploratory until something is added"
    ),
    "unanswered": "not answered yet, so every change here is treated as exploratory",
    "absent": f"`{RELIED_ON_FIELD}` is no longer in `.context/project.md`",
}
INITIALIZED_TOOL_COMMANDS = (
    (
        "spctx sync-index . --dry-run",
        "Preview an update to the generated context index.",
    ),
    ("spctx check .", "Check the context files for structural problems."),
)

# Machine states stay in the JSON report; these are their human equivalents.
# Report text stays ASCII so it renders correctly on any console codepage.
ADOPTION_SUMMARY = {
    "routed": "active; agents reading this project's instructions will find the context",
    "ready_after_apply": "active once you apply this preview",
    "manual_activation_required": (
        "not active yet; add the routing block below to an instruction file your agents read"
    ),
    "project_route_required": (
        "nearly active; `.context/project.md` still needs to mention `.context/scientific-practice.md`"
    ),
    "scientific_contract_review_required": (
        "needs review; the existing scientific-practice file differs from the packaged one"
    ),
    "skill_review_required": (
        "needs review; an existing skill file differs from the packaged one"
    ),
    "blocked": "cannot be determined until the listed conflicts are resolved",
}

STEP_TITLES = {
    "apply_initialization": "Apply the preview",
    "resolve_structural_conflicts": "Resolve the path conflicts",
    "review_agent_skill_variations": "Review your existing skill files",
    "review_scientific_practice_contract": "Review the scientific-practice file",
    "review_and_create_agent_router": "Create an instruction file",
    "review_instruction_compatibility": "Confirm your instructions still fit",
    "integrate_project_context_route": "Add the routing block",
    "populate_agent_essentials": "Fill in Project Essentials",
    "import_agents_file_into_claude_md": "Point CLAUDE.md at AGENTS.md",
    "review_claude_skill_pointers": "Review your existing Claude skill files",
    "populate_project_context": "Fill in the project context",
    "refresh_project_context": "Refresh the project context",
    "review_project_context": "Review the project context",
    "check_context_structure": "Check the result",
}

STEP_OWNERS = {
    "user_or_agent": "you or an agent",
    "agent_with_user_review": "an agent, with your review",
    "agent_with_user_and_domain_review": "an agent, with your and a domain reviewer's approval",
}
CONTEXT_SKILL_PATHS = tuple(agent_skill_path(name) for name in AGENT_SKILLS)


def _initialization_next_steps(
    plan: InitializationPlan,
    *,
    dry_run: bool,
) -> list[dict[str, object]]:
    if plan.conflicts:
        return [
            {
                "action": "resolve_structural_conflicts",
                "owner": "user_or_agent",
                "paths": list(plan.conflicts),
                "instruction": (
                    "Replace only the reported linked or non-file paths with ordinary "
                    "files and directories, then preview initialization again."
                ),
            }
        ]

    steps: list[dict[str, object]] = []
    if dry_run and plan.copy_files:
        steps.append(
            {
                "action": "apply_initialization",
                "owner": "user_or_agent",
                "paths": list(plan.copy_files),
                "instruction": "Review this preview, then rerun the same command without --dry-run.",
            }
        )

    retained_skills = [
        file.relative_path
        for file in plan.agent_skill_files
        if file.disposition == "retain"
    ]
    if retained_skills:
        steps.append(
            {
                "action": "review_agent_skill_variations",
                "owner": "agent_with_user_review",
                "paths": retained_skills,
                "instruction": (
                    "These skill files already existed and were left alone. Check their "
                    "frontmatter, when they trigger, and their steps; spctx did not "
                    "overwrite them."
                ),
            }
        )

    practice_file = next(
        (file for file in plan.files if file.relative_path == SCIENTIFIC_PRACTICE_PATH),
        None,
    )
    if practice_file is not None and practice_file.disposition == "retain":
        steps.append(
            {
                "action": "review_scientific_practice_contract",
                "owner": "agent_with_user_and_domain_review",
                "paths": [SCIENTIFIC_PRACTICE_PATH],
                "instruction": (
                    "Your existing file stays authoritative. Compare it with the packaged "
                    "version shown below and settle any differences about scientific roles, "
                    "protected material, evidence, and what may be claimed before treating "
                    "the setup as done. spctx will not replace the file."
                ),
            }
        )

    agents_file = next(
        (file for file in plan.files if file.relative_path == "AGENTS.md"),
        None,
    )
    if agents_file is not None and agents_file.disposition in {"retain", "defer"}:
        deferred_router = agents_file.disposition == "defer"
        route_state = (
            "absent"
            if deferred_router
            else managed_block_state(
                agents_file.target_content or b"",
                CONTEXT_ROUTE_BLOCK,
                CONTEXT_ROUTE_BEGIN,
                CONTEXT_ROUTE_END,
            )
        )
        if deferred_router:
            route_instruction = (
                "Review the packaged AGENTS.md shown below once the existing practice and "
                "skill files have been checked. Create it, or an equivalent of your own that "
                "keeps its routes to project context, scientific practice, and the skills. "
                "Settle any real conflict with the people responsible first."
            )
        elif route_state == "exact":
            route_instruction = (
                "Your AGENTS.md already contains the routing block and stays authoritative. "
                "Confirm the rest of it still agrees with the context system. No edit needed."
            )
        else:
            route_instruction = (
                "Your AGENTS.md stays authoritative. Compare it with the scientific-practice "
                "file, settle any real conflict with the people responsible, and add only the "
                "routing block shown above. Replace an earlier SPCTX block rather than "
                "duplicating it, and leave the rest of the file alone."
            )
        steps.append(
            {
                "action": (
                    "review_and_create_agent_router"
                    if deferred_router
                    else "review_instruction_compatibility"
                    if route_state == "exact"
                    else "integrate_project_context_route"
                ),
                "owner": "agent_with_user_review",
                "paths": ["AGENTS.md"],
                "instruction": route_instruction,
            }
        )

    if agents_file is not None and agents_file.disposition == "create":
        steps.append(
            {
                "action": "populate_agent_essentials",
                "owner": "agent_with_user_review",
                "paths": ["AGENTS.md"],
                "instruction": (
                    "Replace each bracketed prompt under `Project Essentials` with what "
                    "this project actually does, and delete the ones that do not apply. "
                    "A prompt left in place is not an answer. Name the environment that "
                    f"holds `spctx`; this run used {sys.executable}."
                ),
            }
        )

    if plan.claude_bridge:
        retained_pointers = [
            file.relative_path
            for file in plan.claude_skill_files
            if file.disposition == "retain"
        ]
        if retained_pointers:
            steps.append(
                {
                    "action": "review_claude_skill_pointers",
                    "owner": "agent_with_user_review",
                    "paths": retained_pointers,
                    "instruction": (
                        "These Claude skill files already existed and were left alone. "
                        "Check that each one still points at the canonical procedure "
                        "under `.agents/skills/` and carries the same description."
                    ),
                }
            )
        if CLAUDE_INSTRUCTION_PATH in plan.existing_instructions:
            steps.append(
                {
                    "action": "import_agents_file_into_claude_md",
                    "owner": "user_or_agent",
                    "paths": [CLAUDE_INSTRUCTION_PATH],
                    "instruction": (
                        f"Claude Code reads `AGENTS.md` only when no `{CLAUDE_INSTRUCTION_PATH}` "
                        f"exists above the working directory. Add `{CLAUDE_IMPORT_LINE}` as a "
                        f"line in `{CLAUDE_INSTRUCTION_PATH}` so both files load, or keep the "
                        "routes in whichever file you decide is authoritative. spctx will not "
                        "edit it."
                    ),
                }
            )

    if ".context/project.md" in plan.copy_files:
        project_action = "populate_project_context"
        project_instruction = (
            "Look at the repository first. Write down only what it actually shows, and say "
            "plainly what is unknown. Ask about meaning, authority, scope, safety, or "
            "expected behavior only where the repository cannot answer."
        )
    elif not plan.copy_files:
        project_action = "review_project_context"
        project_instruction = (
            "Confirm .context/project.md still matches the repository. Refresh only what has "
            "gone stale, and keep the project's own wording and stated unknowns."
        )
    else:
        project_action = "refresh_project_context"
        project_instruction = (
            "Look at the repository and refresh whatever has gone stale. Ask about meaning, "
            "authority, scope, safety, or expected behavior only where the repository cannot "
            "answer."
        )
    steps.append(
        {
            "action": project_action,
            "owner": "agent_with_user_review",
            "paths": [".context/project.md"],
            "instruction": project_instruction,
        }
    )
    steps.append(
        {
            "action": "check_context_structure",
            "owner": "user_or_agent",
            "paths": ["."],
            "command": "spctx check .",
            "instruction": (
                "Run the read-only structural check once the project context and any "
                "instruction changes have been reviewed."
            ),
        }
    )
    return steps


def _initialization_agent_skills(
    plan: InitializationPlan,
    *,
    dry_run: bool,
) -> dict[str, object]:
    files = {file.relative_path: file for file in plan.agent_skill_files}
    entries: list[dict[str, object]] = []
    for skill_name in AGENT_SKILLS:
        path = agent_skill_path(skill_name)
        file = files.get(path)
        if file is None:
            state = "blocked"
        elif dry_run and file.disposition == "create":
            state = "available_after_apply"
        elif file.disposition == "identical":
            state = "exact"
        elif file.disposition == "retain":
            state = "project_owned_review_required"
        else:
            state = file.disposition
        entries.append(
            {
                "name": skill_name,
                "path": path,
                "disposition": file.disposition if file is not None else "blocked",
                "sha256": file.sha256 if file is not None else None,
                "state": state,
            }
        )
    return {
        "convention": ".agents/skills",
        "files": entries,
        "installation": "required_starter_files",
        "boundary": (
            "canonical self-contained procedures with portable YAML discovery metadata; "
            "occupied skills are never overwritten"
        ),
    }


def _initialization_claude_bridge(
    plan: InitializationPlan,
    *,
    dry_run: bool,
) -> dict[str, object]:
    files = {file.relative_path: file for file in plan.claude_skill_files}
    entries: list[dict[str, object]] = []
    for skill_name in AGENT_SKILLS:
        path = claude_skill_path(skill_name)
        file = files.get(path)
        if file is None:
            state = "blocked"
        elif dry_run and file.disposition == "create":
            state = "available_after_apply"
        elif file.disposition == "identical":
            state = "exact"
        elif file.disposition == "retain":
            state = "project_owned_review_required"
        else:
            state = file.disposition
        entries.append(
            {
                "name": skill_name,
                "path": path,
                "canonical_path": agent_skill_path(skill_name),
                "disposition": file.disposition if file is not None else "blocked",
                "sha256": file.sha256 if file is not None else None,
                "state": state,
            }
        )
    claude_md_present = CLAUDE_INSTRUCTION_PATH in plan.existing_instructions
    return {
        "convention": ".claude/skills",
        "files": entries,
        "installation": "generated_pointers",
        "instruction_file": (
            "claude_md_present_import_required"
            if claude_md_present
            else "agents_md_read_directly"
        ),
        "boundary": (
            "each pointer carries only discovery metadata and a route to the canonical "
            "procedure; discovery in a given Claude Code version is not verified here"
        ),
    }


def _initialization_context_adoption(
    plan: InitializationPlan,
    *,
    dry_run: bool,
) -> dict[str, object]:
    files = {file.relative_path: file for file in plan.files}

    def observed_content(path: str) -> bytes:
        file = files[path]
        return file.content if file.disposition in {"create", "identical"} else (file.target_content or b"")

    practice_file = files.get(SCIENTIFIC_PRACTICE_PATH)
    agents_file = files.get("AGENTS.md")
    project_file = files.get(".context/project.md")
    skill_states: dict[str, str] = {}
    effective_skill_states: dict[str, str] = {}
    for path in CONTEXT_SKILL_PATHS:
        skill_file = files.get(path)
        if skill_file is None:
            skill_state = "blocked"
            effective_skill_state = "blocked"
        elif skill_file.disposition == "retain":
            skill_state = "project_owned_review_required"
            effective_skill_state = skill_state
        else:
            effective_skill_state = "exact"
            skill_state = (
                "available_after_apply"
                if dry_run and skill_file.disposition == "create"
                else effective_skill_state
            )
        skill_states[path] = skill_state
        effective_skill_states[path] = effective_skill_state

    if practice_file is None:
        practice_state = "blocked"
    else:
        effective = managed_block_state(
            observed_content(SCIENTIFIC_PRACTICE_PATH),
            practice_file.content,
            SCIENTIFIC_PRACTICE_BEGIN,
            SCIENTIFIC_PRACTICE_END,
        )
        practice_state = (
            "available_after_apply"
            if dry_run and practice_file.disposition == "create"
            else effective
        )

    if agents_file is None:
        agent_state = "blocked"
        effective_agent_state = "blocked"
    else:
        effective_agent_state = managed_block_state(
            observed_content("AGENTS.md"),
            CONTEXT_ROUTE_BLOCK,
            CONTEXT_ROUTE_BEGIN,
            CONTEXT_ROUTE_END,
        )
        agent_state = (
            "available_after_apply"
            if dry_run and agents_file.disposition == "create"
            else effective_agent_state
        )

    if project_file is None:
        project_state = "blocked"
        effective_project_state = "blocked"
    else:
        effective_project_state = (
            "present"
            if SCIENTIFIC_PRACTICE_PATH.encode("utf-8")
            in observed_content(".context/project.md")
            else "absent"
        )
        project_state = (
            "available_after_apply"
            if dry_run and project_file.disposition == "create"
            else effective_project_state
        )

    effective_practice_state = (
        "exact"
        if practice_file is not None and practice_file.disposition == "create"
        else practice_state
    )
    if plan.conflicts:
        status = "blocked"
    elif effective_practice_state != "exact":
        status = "scientific_contract_review_required"
    elif any(state != "exact" for state in effective_skill_states.values()):
        status = "skill_review_required"
    elif effective_agent_state != "exact":
        status = "manual_activation_required"
    elif effective_project_state != "present":
        status = "project_route_required"
    elif dry_run and plan.copy_files:
        status = "ready_after_apply"
    else:
        status = "routed"

    compatibility = "not_machine_checked"
    if agents_file is not None and agents_file.disposition in {"create", "identical"}:
        compatibility = "packaged_baseline"

    adoption: dict[str, object] = {
        "status": status,
        "practice_core": practice_state,
        "skills": skill_states,
        "agent_route": agent_state,
        "project_route": project_state,
        "instruction_compatibility": compatibility,
        "boundary": (
            "project-context routing, exact packaged skills, and versioned-core "
            "integrity only; "
            "natural-language instruction compatibility requires project review and "
            "scientific validity requires relevant scientific or domain review"
        ),
    }
    if effective_practice_state != "exact" and practice_file is not None:
        packaged_text = practice_file.content.decode("utf-8")
        begin = packaged_text.find(SCIENTIFIC_PRACTICE_BEGIN)
        end_marker = packaged_text.find(SCIENTIFIC_PRACTICE_END, begin + 1)
        if begin >= 0 and end_marker >= 0:
            end = end_marker + len(SCIENTIFIC_PRACTICE_END)
            adoption["suggested_practice_core"] = packaged_text[begin:end]
    retained_skill_files = {
        file.relative_path: file.content.decode("utf-8")
        for file in plan.files
        if file.relative_path in CONTEXT_SKILL_PATHS and file.disposition == "retain"
    }
    if retained_skill_files:
        adoption["suggested_skills"] = retained_skill_files
    if agents_file is not None and agents_file.disposition == "defer":
        adoption["suggested_agents_file"] = agents_file.content.decode("utf-8")
    elif effective_agent_state != "exact":
        adoption["suggested_agents_block"] = CONTEXT_ROUTE_BLOCK
    return adoption


def initialization_report(
    plan: InitializationPlan,
    *,
    dry_run: bool,
    applied: InitializationResult | None = None,
) -> dict[str, object]:
    """Build the single machine/human report model for initialization."""

    if dry_run and applied is not None:
        raise ValueError("A dry-run report cannot contain an applied result.")
    if applied is not None:
        if applied.target != plan.target or applied.mode != plan.mode:
            raise ValueError("Applied initialization result does not match its plan.")
        if applied.resource_bundle_sha256 != plan.resource_bundle_sha256:
            raise ValueError("Applied initialization result has a different resource bundle.")
    if plan.conflicts:
        result = "blocked"
    elif applied is not None:
        result = applied.status
    elif dry_run:
        result = plan.status
    else:
        raise ValueError("A non-preview successful report requires an applied result.")

    context_adoption = _initialization_context_adoption(
        plan,
        dry_run=dry_run,
    )
    report: dict[str, object] = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "producer": {
            "distribution": DISTRIBUTION_NAME,
            "version": __version__,
            "resource_bundle_sha256": plan.resource_bundle_sha256,
        },
        "operation": "init",
        "result": result,
        "mode": plan.mode,
        "dry_run": dry_run,
        "target": {"path": str(plan.target)},
        "summary": {
            "files_to_copy": len(plan.copy_files),
            "identical_files": len(plan.identical_files),
            "retained_files": len(plan.retained_files),
            "deferred_files": len(plan.deferred_files),
            "conflicts": len(plan.conflicts),
        },
        "copy_files": list(plan.copy_files),
        "identical_files": list(plan.identical_files),
        "retained_files": list(plan.retained_files),
        "deferred_files": list(plan.deferred_files),
        "conflicts": list(plan.conflicts),
        "existing_instructions": list(plan.existing_instructions),
        "semantic_initialization": "not_performed",
        "context_adoption": context_adoption,
        "agent_skills": _initialization_agent_skills(plan, dry_run=dry_run),
        "next_steps": _initialization_next_steps(plan, dry_run=dry_run),
    }
    if plan.claude_bridge:
        report["claude_skills"] = _initialization_claude_bridge(plan, dry_run=dry_run)
    if not plan.conflicts:
        agent_route = context_adoption["agent_route"]
        if agent_route == "available_after_apply":
            persistent_agent_guidance = "after_initialization_apply"
        elif agent_route == "exact":
            persistent_agent_guidance = "present"
        else:
            persistent_agent_guidance = "review_required"
        report["tool_discovery"] = {
            "reported_now": True,
            "persistent_agent_guidance": persistent_agent_guidance,
            "working_directory": str(plan.target),
            "read_first": (
                ["AGENTS.md", ".context/project.md"]
                if agent_route in {"exact", "available_after_apply"}
                else [".context/project.md"]
            ),
            "read_when_scientifically_material": [
                SCIENTIFIC_PRACTICE_PATH,
                ".agents/skills/spctx-scientific-change/SKILL.md",
            ],
            "read_when_maintaining_context": [
                ".agents/skills/spctx-project-context/SKILL.md",
            ],
            "commands": [
                {"command": command, "purpose": purpose}
                for command, purpose in INITIALIZED_TOOL_COMMANDS
            ],
            "interpreter": sys.executable,
            "boundary": (
                "optional bounded mechanics only; people and agents select actions, while "
                "identified scientific/domain and project/data authorities retain their "
                "respective meaning and permission decisions"
            ),
        }
    return report


def index_sync_report(
    plan: IndexSyncPlan,
    *,
    dry_run: bool,
    applied: IndexSyncResult | None = None,
) -> dict[str, object]:
    """Build the machine/human report model for bounded index synchronization."""

    if dry_run and applied is not None:
        raise ValueError("A dry-run report cannot contain an applied result.")
    if applied is not None and (
        applied.target != plan.target
        or applied.action != plan.action
        or applied.resource_bundle_sha256 != plan.resource_bundle_sha256
        or applied.specialized_owners != plan.specialized_owners
    ):
        raise ValueError("Applied context-index result does not match its plan.")

    if plan.conflicts or plan.action == "blocked":
        result = "blocked"
    elif applied is not None:
        result = applied.status
    elif dry_run:
        result = plan.status
    elif plan.action in {"not_needed", "no_changes"}:
        result = plan.action
    else:
        raise ValueError("A non-preview successful report requires an applied result.")

    changed_files = list(applied.changed_files) if applied is not None else []
    report: dict[str, object] = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "producer": {
            "distribution": DISTRIBUTION_NAME,
            "version": __version__,
            "resource_bundle_sha256": plan.resource_bundle_sha256,
        },
        "operation": "sync-index",
        "result": result,
        "dry_run": dry_run,
        "target": {"path": str(plan.target)},
        "index": plan.relative_path,
        "resource_id": plan.resource_id,
        "action": plan.action,
        "specialized_owner_count": len(plan.specialized_owners),
        "specialized_owners": list(plan.specialized_owners),
        "specialized_routes": [
            {
                "path": item.path,
                "purpose": item.purpose,
                "read_when": item.read_when,
                "update_when": item.update_when,
                "complete": item.complete,
            }
            for item in plan.owner_guidance
        ],
        "changed_files": changed_files,
        "conflicts": list(plan.conflicts),
        "generation_boundary": "inventory_block_only",
    }
    if dry_run and plan.planned_content is not None:
        report["original_sha256"] = plan.original_sha256
        report["planned_sha256"] = plan.planned_sha256
        report["planned_content"] = plan.planned_content.decode("utf-8")
    return report


def health_report(
    result: HealthResult,
    *,
    differences: Sequence[ManagedDifference] | None = None,
) -> dict[str, object]:
    """Build the single machine/human report model for a project check.

    There is deliberately no pass or fail here. The report describes what the
    project currently has set up so a reader can decide what to do next;
    treating structure as a verdict was the thing this product set out not to do.
    """

    report: dict[str, object] = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "producer": {
            "distribution": DISTRIBUTION_NAME,
            "version": __version__,
            "resource_bundle_sha256": result.resource_bundle_sha256,
        },
        "operation": "check",
        "target": {"path": str(result.target)},
        "validation_boundary": HEALTH_VALIDATION_BOUNDARY,
        "state": {
            "agent_route": result.context_adoption.agent_route,
            "starter_prompts": [
                asdict(prompts) for prompts in result.starter_prompts
            ],
            "skill_triggers": {
                "tuned": sum(entry.state == "tuned" for entry in result.skill_tuning),
                "total": len(result.skill_tuning),
                "untuned": [
                    entry.path
                    for entry in result.skill_tuning
                    if entry.state == "untuned"
                ],
            },
            "practice_notes": result.practice_localization,
            "relied_on": result.relied_on,
        },
        "observed": result.counts,
        "findings": [asdict(finding) for finding in result.findings],
        "repeated_passages": [asdict(passage) for passage in result.repeated_passages],
    }
    if differences is not None:
        report["differences"] = [asdict(difference) for difference in differences]
    return report


def health_error_report(
    message: str,
    *,
    target: str | None = None,
    resource_bundle_sha256: str | None = None,
) -> dict[str, object]:
    """Build a versioned report when a project health check cannot run safely."""

    return {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "producer": {
            "distribution": DISTRIBUTION_NAME,
            "version": __version__,
            "resource_bundle_sha256": resource_bundle_sha256,
        },
        "operation": "check",
        "result": "error",
        "target": {"path": target},
        "validation_boundary": HEALTH_VALIDATION_BOUNDARY,
        "message": message,
    }


def error_report(
    message: str,
    *,
    operation: str = "init",
    target: str | None = None,
    mode: str | None = None,
    dry_run: bool = False,
    resource_bundle_sha256: str | None = None,
) -> dict[str, object]:
    """Build a versioned report when planning cannot produce a safe plan."""

    report: dict[str, object] = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "producer": {
            "distribution": DISTRIBUTION_NAME,
            "version": __version__,
            "resource_bundle_sha256": resource_bundle_sha256,
        },
        "operation": operation,
        "result": "error",
        "mode": mode,
        "dry_run": dry_run,
        "target": {"path": target},
        "message": message,
    }
    if operation == "init":
        report["semantic_initialization"] = "not_performed"
    return report


def _check_state_lines(report: Mapping[str, object]) -> list[str]:
    """Render what the project currently has set up, without scoring it."""

    state = report.get("state")
    if not isinstance(state, Mapping):
        return []

    lines: list[str] = []
    route = state.get("agent_route")
    if route in AGENT_ROUTE_SUMMARY:
        lines.append(f"- Agent routing: {AGENT_ROUTE_SUMMARY[route]}")

    prompts = state.get("starter_prompts")
    if isinstance(prompts, list) and prompts:
        outstanding = [
            entry
            for entry in prompts
            if isinstance(entry, Mapping) and entry["unanswered"]
        ]
        if outstanding:
            detail = ", ".join(
                f"{entry['path']} {entry['unanswered']}" for entry in outstanding
            )
            lines.append(
                f"- Starter prompts still holding their shipped text: {detail}"
            )
        else:
            lines.append("- Starter prompts: all replaced with this project's answers")

    triggers = state.get("skill_triggers")
    if isinstance(triggers, Mapping) and triggers["total"]:
        tuned = triggers["tuned"]
        total = triggers["total"]
        if tuned == total:
            lines.append(
                f"- Skill triggers: all {total} carry the words people here actually use"
            )
        elif tuned:
            lines.append(
                f"- Skill triggers: {tuned} of {total} carry the words people here "
                "actually use"
            )
        else:
            lines.append(
                f"- Skill triggers: none of the {total} carry this project's own "
                "request phrasings yet, which is the cheapest way to help agents "
                "pick the right procedure"
            )

    practice = state.get("practice_notes")
    if practice in PRACTICE_LOCALIZATION_SUMMARY:
        lines.append(
            f"- This project's own practice notes: {PRACTICE_LOCALIZATION_SUMMARY[practice]}"
        )

    relied_on = state.get("relied_on")
    if relied_on in RELIED_ON_SUMMARY:
        lines.append(f"- {RELIED_ON_FIELD}: {RELIED_ON_SUMMARY[relied_on]}")
    return lines


def render_human(report: Mapping[str, object]) -> str:
    """Render a report without consulting operation state outside the payload."""

    producer = report["producer"]
    target = report["target"]
    assert isinstance(producer, Mapping)
    assert isinstance(target, Mapping)

    lines = ["## Scientific Project Context Report"]
    if "result" in report:
        lines.append(f"- Result: {report['result']}")
    lines.extend(
        [
            f"- Operation: {report['operation']}",
            f"- Version: {producer['version']}",
            f"- Target: {target['path'] or 'unavailable'}",
        ]
    )
    if report["operation"] == "check":
        lines.extend(_check_state_lines(report))
        observed = report.get("observed")
        if isinstance(observed, Mapping):
            lines.append(
                f"- Observations: {observed[BROKEN]} broken, "
                f"{observed[UNFINISHED]} unfinished, {observed[NOTED]} noted"
            )

        repeated = report.get("repeated_passages")
        project_repeats = (
            [
                passage
                for passage in repeated
                if isinstance(passage, Mapping) and passage["kind"] == "project"
            ]
            if isinstance(repeated, list)
            else []
        )
        if project_repeats:
            lines.append(
                f"- Passages repeated among your own documents: {len(project_repeats)} "
                "(word-for-word only; a reworded copy is not detected)"
            )

        findings = report.get("findings")
        finding_values = findings if isinstance(findings, list) else []
        for finding in finding_values:
            if not isinstance(finding, Mapping):
                continue
            location = str(finding["path"])
            if finding.get("line") is not None:
                location += f":{finding['line']}"
            lines.extend(
                [
                    f"- {finding['severity']} `{location}` ({finding['check_id']})",
                    f"  - {finding['message']}",
                    f"  - Found: {finding['evidence']}",
                    f"  - Next: {finding['next_action']}",
                ]
            )

        differences = report.get("differences")
        if isinstance(differences, list):
            diverged = [
                difference
                for difference in differences
                if isinstance(difference, Mapping) and difference["state"] != "extended"
            ]
            tuned = [
                difference
                for difference in differences
                if isinstance(difference, Mapping) and difference["state"] == "extended"
            ]
            lines.append(
                f"- Tuned to this project: {len(tuned)}; otherwise different from the "
                f"packaged version: {len(diverged)}"
            )
            for difference in tuned + diverged:
                label = (
                    "project tuning"
                    if difference["state"] == "extended"
                    else "no longer tracking the package"
                )
                lines.extend(
                    [
                        f"- {difference['path']} ({difference['region']}: {label})",
                        "",
                        "```diff",
                        str(difference["diff"]).rstrip("\n"),
                        "```",
                    ]
                )

            for passage in project_repeats:
                lines.extend(
                    [
                        f"- {passage['path']} repeats {passage['other']}",
                        f"  - {passage['words']} words: \"{passage['passage']}\"",
                    ]
                )

        message = report.get("message")
        if message:
            lines.append(f"- Error: {message}")
        validation_boundary = report.get("validation_boundary")
        if validation_boundary:
            lines.append(f"- Checked: {validation_boundary}.")
        return "\n".join(lines) + "\n"

    if report["operation"] == "sync-index":
        lines.append(f"- Dry run: {'yes' if report.get('dry_run') else 'no'}")
        if report.get("action") is not None:
            lines.extend(
                [
                    f"- Planned action: {report['action']}",
                    f"- Focused context documents: {report['specialized_owner_count']}",
                ]
            )
            owners = report.get("specialized_owners")
            if isinstance(owners, list):
                lines.extend(f"  - {owner}" for owner in owners)
            lines.append(
                "- Only the generated inventory block is rewritten; "
                "any routing notes you write around it stay as they are"
            )
            planned_content = report.get("planned_content")
            if planned_content is not None:
                lines.extend(
                    [
                        f"- Original SHA-256: {report.get('original_sha256') or 'absent'}",
                        f"- Planned SHA-256: {report['planned_sha256']}",
                        "- Exact planned content:",
                    ]
                )
                lines.extend(
                    f"  {line}" for line in str(planned_content).splitlines()
                )
        conflicts = report.get("conflicts")
        if isinstance(conflicts, list) and conflicts:
            lines.append("- Conflicts:")
            lines.extend(f"  - {conflict}" for conflict in conflicts)
        message = report.get("message")
        if message:
            lines.append(f"- Error: {message}")
        return "\n".join(lines) + "\n"

    if report.get("mode") is not None:
        lines.append(f"- Mode: {report['mode']}")
    lines.append(f"- Dry run: {'yes' if report.get('dry_run') else 'no'}")

    summary = report.get("summary")
    if isinstance(summary, Mapping):
        lines.extend(
            [
                f"- Files to copy: {summary['files_to_copy']}",
                f"- Identical files: {summary['identical_files']}",
                f"- Left unchanged: {summary['retained_files']}",
                f"- Held back for review: {summary.get('deferred_files', 0)}",
                f"- Conflicts: {summary['conflicts']}",
            ]
        )
        for label, key in (
            ("Files to copy", "copy_files"),
            ("Identical files", "identical_files"),
            ("Left unchanged", "retained_files"),
            ("Held back for review", "deferred_files"),
            ("Conflicts", "conflicts"),
        ):
            values = report.get(key)
            if isinstance(values, list) and values:
                lines.append(f"- {label}:")
                lines.extend(f"  - {value}" for value in values)

    message = report.get("message")
    if message:
        lines.append(f"- Error: {message}")
    existing_instructions = report.get("existing_instructions")
    if isinstance(existing_instructions, list):
        copy_files = report.get("copy_files")
        adding_agents = isinstance(copy_files, list) and "AGENTS.md" in copy_files
        if existing_instructions:
            lines.append("- Instructions this project already has:")
            lines.extend(f"  - {value}" for value in existing_instructions)
            if adding_agents:
                lines.append(
                    "  - `AGENTS.md` will be added alongside these. Decide which file "
                    "your agents actually read, and link rather than repeat."
                )
        elif adding_agents:
            lines.append(
                "- No other instruction file found, so `AGENTS.md` will be the one "
                "your agents read. Fill in its `Project Essentials`, including the "
                "environment where `spctx` is installed."
            )
    adoption = report.get("context_adoption")
    if isinstance(adoption, Mapping):
        status = str(adoption["status"])
        lines.append(f"- Agent routing: {ADOPTION_SUMMARY.get(status, status)}")
        suggested = adoption.get("suggested_agents_block")
        suggested_agents_file = adoption.get("suggested_agents_file")
        suggested_practice = adoption.get("suggested_practice_core")
        suggested_skills = adoption.get("suggested_skills")
        if suggested_practice:
            lines.append("  - Packaged scientific-practice core for review:")
            lines.extend(f"    {line}" for line in str(suggested_practice).splitlines())
        if isinstance(suggested_skills, Mapping):
            for path, content in suggested_skills.items():
                lines.append(f"  - Packaged skill for review: `{path}`")
                lines.extend(f"    {line}" for line in str(content).splitlines())
        if suggested_agents_file:
            lines.append("  - Packaged AGENTS.md for review:")
            lines.extend(f"    {line}" for line in str(suggested_agents_file).splitlines())
        if suggested:
            lines.append("  - Routing block to add, with your review:")
            lines.extend(f"    {line}" for line in str(suggested).splitlines())
    claude_skills = report.get("claude_skills")
    if isinstance(claude_skills, Mapping):
        lines.append(
            "- Claude Code: pointer skills under `.claude/skills/`, each routing to the "
            "procedure in `.agents/skills/`. Claude Code reads no skills from `.agents/`."
        )
        entries = claude_skills.get("files")
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, Mapping):
                    lines.append(f"  - `{entry['path']}`: {entry['state']}")
        if claude_skills.get("instruction_file") == "claude_md_present_import_required":
            lines.append(
                f"  - This project has a `{CLAUDE_INSTRUCTION_PATH}`, so Claude Code reads "
                f"that instead of `AGENTS.md`. Add `{CLAUDE_IMPORT_LINE}` to it, or move "
                "the routes there yourself."
            )
        else:
            lines.append(
                "  - No `CLAUDE.md` here, so recent Claude Code versions read `AGENTS.md` "
                "directly. Adding one later stops that unless it imports `AGENTS.md`."
            )
    next_steps = report.get("next_steps")
    if isinstance(next_steps, list) and next_steps:
        lines.append("- Next steps:")
        for item in next_steps:
            if not isinstance(item, Mapping):
                continue
            action = str(item.get("action", ""))
            title = STEP_TITLES.get(action, action.replace("_", " "))
            owner_key = str(item.get("owner", "user_or_agent"))
            owner = STEP_OWNERS.get(owner_key, owner_key.replace("_", " "))
            lines.append(f"  - {title} ({owner}): {item['instruction']}")
            if item.get("command"):
                lines.append(f"    - Command: `{item['command']}`")
    tool_discovery = report.get("tool_discovery")
    if isinstance(tool_discovery, Mapping):
        lines.append("- Where things are:")
        lines.append(f"  - Working directory: {tool_discovery['working_directory']}")
        read_first = tool_discovery.get("read_first")
        if isinstance(read_first, list):
            lines.append("  - Read first:")
            lines.extend(f"    - `{path}`" for path in read_first)
        scientific_read = tool_discovery.get("read_when_scientifically_material")
        if isinstance(scientific_read, list):
            lines.append("  - Read when work is scientifically material:")
            lines.extend(f"    - `{path}`" for path in scientific_read)
        maintenance_read = tool_discovery.get("read_when_maintaining_context")
        if isinstance(maintenance_read, list):
            lines.append("  - Read when maintaining context:")
            lines.extend(f"    - `{path}`" for path in maintenance_read)
        commands = tool_discovery.get("commands")
        if isinstance(commands, list):
            lines.append("  - Commands, if `spctx` is installed in the project environment:")
            for item in commands:
                if isinstance(item, Mapping):
                    lines.append(f"    - `{item['command']}`: {item['purpose']}")
        interpreter = tool_discovery.get("interpreter")
        if interpreter:
            lines.append(
                f"    - This run used {interpreter}. `spctx` is reachable only from that "
                "environment, so record it in `Project Essentials`."
            )
    return "\n".join(lines) + "\n"


def render_json(report: Mapping[str, object]) -> str:
    """Render stable, readable JSON from the same payload as human output."""

    return json.dumps(report, indent=2, sort_keys=True) + "\n"
