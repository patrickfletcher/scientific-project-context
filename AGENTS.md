# AGENTS.md

## Start Here

<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->
Read `.context/project.md` at the start of work for the project's current state, and `.context/index.md` for the list of every other context document and when to read it. Open only what the task needs.

When work changes what the project currently knows, its current focus, a protected input, or what later work relies on, rewrite that part of the context in place before you finish. Run history, what stayed unchanged, and who approved what belong in Git and the conversation, not in context. After adding, renaming, or removing a document under `.context/`, run `spctx sync-index .`; the index is generated, never edited by hand. Use `.agents/skills/spctx-project-context/SKILL.md` to initialize, refresh, separate, retire, or upgrade context.

For work that could affect scientific meaning, protected inputs, methods, evidence, artifacts, validation, or claims, read `.context/scientific-practice.md` and use `.agents/skills/spctx-scientific-change/SKILL.md`.

For text written for readers outside this work, such as a README, contributor guide, methods or results section, figure caption, status report, or manuscript, use `.agents/skills/spctx-public-writing/SKILL.md`.

Keep project facts in `.context/project.md` or another document under `.context/`. If another instruction conflicts with the scientific safeguards, stop and ask the user or the responsible scientist to resolve it.
<!-- END SPCTX PROJECT CONTEXT ROUTING v1 -->

Do not scan every policy, proposal, or reference document. Follow the smallest relevant route and stop when the target and check are clear.

This repository uses Scientific Project Context on itself. Root-specific facts and product decisions belong in `.context/`; on-demand procedures belong in `.agents/skills/`.

## Project Essentials

- **What this project is**: the Scientific Project Context product — a six-file Markdown starter, three Agent Skills, and the `spctx` CLI. See `.context/project.md` for current state and open decisions.
- **Environment**: `.venv/` at the repository root, where `spctx` is installed. Do not substitute system Python.
- **Run and test**: from the repository root — `python -m unittest discover -s tests` and `python -m compileall -q src tools`.
- **Reinstall after changing packaged resources**: `python -m pip install .`, then `spctx --version`. The current `.venv/` has no pip; use `uv pip install . --python .venv\Scripts\python.exe` there.
- **Verify built artifacts**: `python tools\check_package_artifacts.py --source-root . --direct-wheel <wheel> --sdist <sdist> --sdist-wheel <sdist-built-wheel>`.
- **Context tools**: `spctx check .` after changing context files; `spctx sync-index . --dry-run` then `spctx sync-index .` when a context document is added, renamed, or removed, or its opening lines change.
- **Protected inputs**: packaged resources in `template/` and recorded trial observations in `.context/evaluation.md`. Changing them requires explicit review.
- **Conventions**: standard library only in `src/`; no runtime dependencies. Keep `template/` and the root `.agents/skills/` copies identical, and keep every shipped Markdown file LF-terminated.

## Where Facts Live

Each durable fact belongs in one place, and every other place links to it.

- **This file**: environment, commands, protected inputs, conventions, and routes, for every session.
- **`README.md`**: purpose, the user journey, and public behavior, for humans evaluating or using the product.
- **`.context/project.md` and the other documents `.context/index.md` lists**: product purpose, current state, evidence, risks, and open decisions, on demand. The index is generated; no other list of these documents is kept.

## Authority

When guidance conflicts, use this order:

1. The user's current instructions.
2. This file.
3. Current facts in `.context/project.md` and any focused source selected by `.context/index.md`.
4. Existing code, tests, public docs, and established repository conventions.
5. Reference material or Git history when current sources are insufficient.
6. Engineering judgment, with important uncertainty visible.

## Working Style

1. Inspect before asking. Derive current facts from source, tests, configuration, artifacts, and public documentation before asking the user to repeat them.
2. Implement the narrowest coherent change and verify it in proportion to risk.
3. Ask directly when missing scientific meaning, change authority, safety, or scope blocks safe work.
4. Remove completed work and indefinite blocked/deferred inventory from live planning after preserving useful policy or evidence in its real home.
5. Treat clean structure as ready for review, not as scientific, ethical, legal, release, or publication approval.

## Product Repository Constraints

1. Keep the starter minimal. `.context/product.md` owns the rule for when an always-present file, concept, or prompt earns its place; apply it rather than restating it. Keep root project history outside the starter set.
2. Let agents and users decide scientific meaning and whether another context source is useful. Deterministic tools perform only bounded, inspectable mechanics.
3. Keep generated scientific, access, safety, licensing, governance, and claim-bearing content visibly review-required until supported facts and consequential judgments are confirmed.
4. Do not put project facts or product decisions in `.agents/skills/`.
5. Root and template skills intentionally share one contract. Keep root-specific navigation and product policy in `.context/`, not in a forked skill.
6. Use `.venv/` for the Python virtual environment where `spctx` is installed.
7. Never name or identify a trial repository, its owner, or its research anywhere in this repository. Record observations from use only as anonymous trial IDs, following `.context/evaluation.md`.

## Writing for Readers

This product's own prose is a worked example of its advice, and real use showed
it leaking private vocabulary into a scientific repository. Use ordinary
scientific and engineering English in every shipped file: prefer `place` or
`file` over `surface`, say what an output supports rather than calling it
claim-bearing, and state a boundary once where it belongs.

## Verification

Use the commands in Project Essentials above and run checks proportionate to what changed. `spctx check` reports state rather than a verdict; a report with nothing left to do establishes structural consistency only.
