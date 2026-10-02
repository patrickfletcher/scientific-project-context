# Project Context

Purpose: provide the smallest current context needed to work safely in this repository.
Read when: starting work, checking repository intent or current reality, or deciding whether another context source is needed.
Update when: product purpose, executable state, current focus, scientific constraints, or sharing intent changes.

Keep this file brief. `.context/README.md` points to focused context only when a task needs it.

`.context/scientific-practice.md` is the stable scientific contract. This file records how that contract applies to this product repository.

## Purpose and Useful Outcome

**What this project does**: Develops Scientific Project Context, a lightweight project-local system for maintaining the consequential facts, expectations, constraints, checks, and working context needed to understand, change, verify, and eventually explain scientific work.

**Who uses the result and what useful outcome they need**: Scientists working with coding agents, and their collaborators, need a project-owned record they can ask agents to consult and maintain, then review and edit themselves. The record should provide enough trustworthy context for the next meaningful step, without an onboarding questionnaire or a permanent documentation program. `.context/product.md` owns the detailed product promise.

## Current Reality

**Main materials and entry points**:

- `template/` contains the packaged Markdown: the six-file starter set placed into a project, plus the `.context/README.md` router that only `sync-index` writes.
- `pyproject.toml` and `src/scientific_project_context/` define the experimental package, immutable resource catalog, bounded project operations, state-reporting check library, versioned reports, and `spctx` CLI.
- root `.context/` is this repository's own current product, planning, and evidence context; its reference layer is limited to one rationale and one evidence ledger.
- root `.agents/skills/` contains the same three self-contained Agent Skills shipped in the starter set.
- `tools/` contains the repository-only artifact verifier; `tests/` contains product contracts for the packaged Markdown resources and CLI.

**How work is performed, checked, and packaged**: `AGENTS.md` owns the environment and the exact command inventory. In summary, the repository installs locally with pip, ships the `spctx` CLI, and is verified by unit tests, a syntax check, a maintainer starter-resource contract, and a built-artifact membership check.

**Conditions and dependencies**: Runtime code uses only the Python standard library and declares Python 3.10 through 3.14. Hatchling is a build-only dependency. Source is `0.1.0.dev22`. The package is local and experimental, with no automatic upgrade or semantic migration.

## Current Work

**Current focus**: Preparing to share with colleagues. On 2026-10-02 the README was rewritten for outside readers, and this repository's own context was pruned, flattened into one folder, and stripped of anything identifying the trial repositories, which are now recorded only as anonymous trial IDs.

**Next meaningful step**: Share with colleagues from a clean starting point, without this repository's history, and add a CI matrix over the declared Python range and platforms. Then observe the state lines on real exploratory work: do the route, prompt, and relied-on lines change what a person or an agent does?

## Scientific Work, Evidence, and Outputs

**What must not be changed silently**: Packaged resources in `template/`, accepted product meaning, and recorded trial observations. Generated project context and public text remain review-required until confirmed.

**What could make the result wrong even if the workflow completes or looks plausible**: The system could be mechanically consistent yet burden users, conceal project-specific scientific risk, prompt invented meaning, overwrite project knowledge, or encourage claims beyond retained evidence. Real use added three observed failure modes: context can land on the wrong surface and be duplicated across all three, this product's private vocabulary can leak into a scientific project, and the CLI can be absent from the agent's `PATH` while the report text still presents it as the normal route. Product tests could also become ceremonial by checking retired internal mechanisms rather than shipped resources and commands.

**Smallest useful check**: New initialization must install the exact starter contract with the complete managed project-context route, the `Project Essentials` prompts including where `spctx` lives, and structurally valid, self-contained Agent Skills, and the report must ask for that block by name and print the interpreter it ran from. Retrofit preview/apply must retain every occupied regular starter file byte-for-byte, install only safe missing files, defer a missing `AGENTS.md` that would activate retained unreviewed practice or skill content, and expose the exact compact route without editing occupied instructions. `--claude` must add one pointer per skill carrying that project's own description, never overwrite an occupied pointer, and never copy a procedure body. Index dry-runs must expose exact planned bytes, preserve prose outside the marker block, and regenerate bounded summaries when source guidance changes. `check` must report the scientific-practice core, Agent Skill structure, pointer agreement, index integrity, routing guidance, and review markers, and report route state and remaining starter prompts as state lines rather than findings; rerunning this root must report no observations.

**Current evidence and limits**: Product tests, syntax and root checks pass, and the package builds and verifies at dev22; `.context/evaluation.md` holds the tested platform range and the anonymized observations from use. Uncontrolled use in the author's own trial repository exposed defects now fixed in source; an explicitly prompted trial there tuned all three descriptions and preserved them across an upgrade. These observations are not agent-behavior trials. Published host documentation describes skill discovery, but no Claude Code session has followed a pointer skill, and no controlled Codex or Copilot Chat session has verified discovery, automatic selection, or adherence to the revised procedures. Unprompted tuning, the effect of tuned triggers, manual migrations, the declared Python floor, other platforms, and real-use namespace clarity remain untested. No hook behavior, security, latency, or compatibility observation exists.

Every statement this project makes about product effect is exploratory. Only the mechanical behavior of the code paths the tests exercise is settled enough for anything to rely on, and that establishes nothing about human ease, domain adequacy, scientific reproducibility, publication readiness, or release readiness.

**Important assumptions or settings**: Scientists and relevant domain reviewers decide scientific meaning; project, data, and community authorities decide permitted change, use, and sharing; people and agents decide when another document is useful; tools perform bounded mechanics. Files placed into a project become project-owned snapshots. The experimental package has no runtime dependencies, telemetry, automatic upgrade, or automatic semantic migration.

**What later work relies on**: the six-file starter set and the three-command interface, which are held still for the colleague trial; the division of authority in the line above; the rule that no command rewrites a project-owned region; and the rule that `check` reports state rather than passing or failing a project. Everything else, including the wording of any prompt, report line, or procedure step, can still change.

## Unresolved Questions

- Do controlled use or renewed registry checks expose a material reason to change the provisional `scientific-project-context`, `scientific_project_context`, or `spctx` identity before public upload?
- How should the repository be shared: a wheel, a zip of the current files, or a public repository whose history starts at a single snapshot? The private repository's history holds earlier, identifying versions of the trial records, so it should not become public as it is.
- Should the `init` report's remaining machine vocabulary move out of human output entirely? dev17 translated the visible labels, state names, step names, and finding text into plain language while leaving the JSON field values unchanged. What remains visible is `Result:` and `Mode:`, whose values are still machine tokens such as `ready_with_activation_deferred`. Translating those is possible but would either lose the exact state or need a second vocabulary to maintain.
- Should the public README show a worked example of a populated `.context/project.md`? Shelved on 2026-09-23, with three options recorded for when the public surface is filled out. A short synthetic example from a generic domain is the likely first step: it is brief, needs nobody's permission, and can be labeled illustrative. This repository's own `.context/` is already a real example and is linked from the README, though it is a software product rather than a bench or analysis project and so does not show the scientific fields at their most useful. Linking to adopters' live context documents would be the strongest evidence, but that only becomes possible after adoption and requires their agreement.
- Does real use show that contributors recover consequential state more accurately or efficiently without disproportionate reading or question burden?
- Should an inventory-loading failure diagnose stale editable-install metadata/source combinations and suggest reinstalling? The first root attempt reported dev4 while current source expected the dev6 five-file inventory; the version mismatch was visible, but the remediation was not.
- Do the three canonical `.agents/skills/` procedures trigger accurately in clean Codex-extension and Copilot Chat sessions without disproportionate maintenance burden? The self-announcement line added in dev17 is what should make this observable.
- Does `spctx-public-writing` earn a permanent place in the starter, or does it duplicate judgment the other two skills already carry? It was added because public writing was the one documented recurring field failure, but that is one uncontrolled observation.
- Does an opt-in, read-only session-start `spctx check` hook expose otherwise-missed structural activation failures with low enough latency, noise, trust, and compatibility burden to justify packaging host-specific adapters? Retain the no-hook default and do not treat non-execution or a structural pass as semantic freshness.
- Should the contract gate how much evidence a result owes on its intended use, rather than only on whether the work is scientifically material? Answered in part on 2026-09-25: the practice core now defines exploratory, supporting a decision or claim, and public or published, states that evidence is owed at promotion rather than production, lists what no level relaxes, and tells a promotion how to rebuild evidence it deferred; `spctx-scientific-change` stops at the exploratory level and `spctx-public-writing` defers to that definition. The contract also gained a project-owned section, a `localize` mode, and a summary line reporting whether it has been written. What remains unanswered is whether either lever changes agent or user behavior, and whether the level becomes an excuse to skip warranted checks.
- Which of the remaining candidates, if any, earns its cost? A dated one-line decision log, a documented way to turn the system down or out such as a minimal starter, a durable record of declined suggestions, an outcome measure such as asking an agent three fixed questions from context alone and having the user score the answers, and a diff-guided impact-review mode in `spctx-project-context`. Each needs a reason from trial evidence, not from this repository's own reasoning.

Current package mechanics live in `.context/automation.md`; the open decisions above still require user review.

## Sharing and Reuse

The repository currently exposes a local prototype. Experimental artifacts have been built and checked locally, but they are not published and must not be described as a supported release. The MIT license, added on 2026-09-23 and confirmed by the author on 2026-10-02, grants permission to use, modify, and redistribute the source; it does not make the interface stable or supported. Trial repositories, their owners, and their content must not be identifiable from this repository; `.context/evaluation.md` owns how observations are recorded. When a real paper companion, archive, package release, or external handoff occurs, confirmed facts may seed public documentation; authorship, claims, citation, availability, ethics, governance, support, and stewardship remain reviewed decisions.
