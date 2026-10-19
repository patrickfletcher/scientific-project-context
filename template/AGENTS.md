# AGENTS.md

## Start Here

<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->
Read `.context/project.md` at the start of work for the smallest current project context. If `.context/README.md` exists, use it to select only the additional source needed by the task.

When work changes what the project currently knows, its current focus, a protected input, what later work relies on, or a context route, rewrite that part of the context in place before you finish. Run history, what stayed unchanged, and who approved what belong in Git and the conversation, not in context. Use `.agents/skills/spctx-project-context/SKILL.md` to initialize, refresh, separate, retire, or upgrade context.

For work that could affect scientific meaning, protected inputs, methods, evidence, artifacts, validation, or claims, read `.context/scientific-practice.md` and use `.agents/skills/spctx-scientific-change/SKILL.md`.

For text written for readers outside this work, such as a README, contributor guide, methods or results section, figure caption, status report, or manuscript, use `.agents/skills/spctx-public-writing/SKILL.md`.

Keep project facts in `.context/project.md` or a document it links. If another instruction conflicts with the scientific safeguards, stop and ask the user or the responsible scientist to resolve it.
<!-- END SPCTX PROJECT CONTEXT ROUTING v1 -->

Read only what the current task needs. Do not scan every context or reference file.

## Project Essentials

Answer each line from this project and delete any that does not apply.

- **What this project is**: [one or two plain sentences; `.context/project.md` holds the full framing]
- **Environment**: [how to activate it, and which tools are installed there; say so if system Python or another interpreter must not be substituted]
- **Run and test**: [the exact commands, including the working directory they assume]
- **Protected inputs**: [data, reference material, or curated decisions that must never be modified, renamed, moved, or deleted; the reasoning belongs in `.context/project.md`]
- **Conventions**: [code style, structure, and review rules, or a link to the file that already covers them]
- **Context tools**: [name the environment `spctx` is installed in, or say it is unavailable here]. `spctx check .` reports what this project has set up so far and what it has not; it passes no judgement and fails nothing. `spctx sync-index . --dry-run` previews the generated context index and `spctx sync-index .` applies it.

## Where Facts Live

Each durable fact belongs in one place, and every other place links to it.

- **This file**: what to honor before acting — environment, commands, protected inputs, conventions, routes.
- **`README.md` and other public docs**: what the project is for and how to run it, for readers including outsiders.
- **`.context/project.md` and its focused sources**: where the science stands, what it rests on, and what is undecided.

A fact that is both operational and scientifically material gets its one-line rule here and its reasoning in project context.

## When Guidance Conflicts

Use this order:

1. The user's current instructions.
2. This file.
3. The safeguards in `.context/scientific-practice.md` when the work is scientifically material.
4. Current project facts in `.context/project.md` and any focused source it links.
5. Existing data, methods, code, tests, public docs, and established project conventions.
6. Your judgment, with important uncertainty visible.

## Working Style

1. Inspect this project before asking. Ask directly when a missing answer about scientific meaning, permission to change something, safety, or scope blocks safe work.
2. Take the smallest coherent step, and check it in proportion to what it could get wrong. Most work here is exploratory until something relies on it: move quickly, keep negative results, and give consequential choices a one-line reason.
3. Write in this project's vocabulary, including in your own summaries; tool and template terminology belongs to the tool. Lead with what was found and what it means, put logistics last, state each limit once, and leave out what did not happen, what stayed unchanged, and who approved it.
4. Treat clean structure as ready for review, not as scientific, ethical, legal, release, or publication approval.
