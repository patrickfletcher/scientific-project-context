# AGENTS.md

## Start Here

<!-- BEGIN SPCTX PROJECT CONTEXT ROUTING v1 -->
Read `.context/project.md` at the start of work. It gives the project's current state. `.context/index.md` lists every other context document and when to read it. Open only what the task needs.

Work is exploratory unless `.context/project.md` lists it under what later work depends on. For exploratory work:

- Move quickly, and keep negative and odd results.
- Give each consequential choice a one-line reason where you make it.
- Write no review marker, review document, or evidence record. Say in your reply what the work showed and that it is provisional.
- Before a side investigation, name the decision it could change. If it could change none, list it as a lead.

Update context only when work changes an answer, the current focus, a protected input, or what later work depends on. Rewrite that part in place. Keep run history, unchanged items, and approvals in Git and the conversation. After you add, rename, or remove a document under `.context/`, run `spctx sync-index .`. The index is generated; never edit it by hand.

Use these procedures:

- `.agents/skills/spctx-project-context/SKILL.md` to set up, refresh, review, or upgrade context.
- `.agents/skills/spctx-scientific-change/SKILL.md`, with `.context/scientific-practice.md`, to change what later work depends on or to prepare a result for publication.
- `.agents/skills/spctx-literature/SKILL.md` to find, check, and cite outside sources.
- `.agents/skills/spctx-public-writing/SKILL.md` to write for readers outside this work.

Change a protected input only when the request clearly means to. If a change would touch one as a side effect, say what would change and ask once. If an instruction conflicts with the scientific safeguards about what later work depends on, ask the user.
<!-- END SPCTX PROJECT CONTEXT ROUTING v1 -->

Read only what the current task needs. Do not scan every context or reference file.

## Project Essentials

Answer each line from this project. Delete a line that does not apply.

- **What this project is**: [one or two plain sentences; `.context/project.md` gives the full picture]
- **Environment**: [how to activate it and which tools it holds; say if system Python or another interpreter must not be used]
- **Run and test**: [the exact commands and the working directory they need]
- **Protected inputs**: [data, reference material, or curated decisions that must never be changed, renamed, moved, or deleted; give the reasons in `.context/project.md`]
- **Conventions**: [code style, structure, and review rules, or a link to the file that holds them]
- **Context tools**: [copy the `Context tools` line that `spctx init` prints, or say that `spctx` is not available here]. `spctx check .` reports what this project has set up; it passes no judgement. `spctx upgrade . --dry-run` shows what a newer `spctx` would change in packaged text. `spctx sync-index .` regenerates the context index.

## Where Facts Live

Keep each durable fact in one place, and link to it from every other place.

- **This file**: what to follow before acting: environment, commands, protected inputs, conventions, and routes.
- **`README.md` and other public docs**: what the project is for and how to run it, for any reader.
- **`.context/project.md` and other context documents**: where the science stands, what it rests on, and what is undecided.
- **`.context/index.md`**: the index, the one place that lists context documents. `spctx sync-index` generates it. Keep no other list.
- **Reference material, tool manuals, and test protocols**: beside what they describe, or under `docs/`. Context links to them.

If a fact is operational and scientifically material, put its one-line rule here and its reasons in context.

## When Guidance Conflicts

If an instruction conflicts with the safeguards in `.context/scientific-practice.md` about what later work depends on, rank does not settle it: ask the user. For exploratory work, follow the user's current instructions and note the conflict in one line. For other conflicts, use this order:

1. The user's current instructions.
2. This file.
3. Current project facts in `.context/project.md` and the other context documents.
4. Existing data, methods, code, tests, public docs, and established project conventions.
5. Your judgment, with important uncertainty visible.

## Working Style

1. Inspect this project before you ask. Ask directly when a missing answer about scientific meaning, permission, safety, or scope blocks safe work.
2. Take the smallest coherent step, and check it in proportion to what it could get wrong. The strictest standard applies only to publication: a public version that reproduces a published result for any reader.
3. Write in this project's vocabulary, also in your own summaries. If the project keeps a glossary, use its terms and avoid its listed words.
   - Lead with what you found and what it means. Put logistics last, and state each limit once.
   - Leave out what did not happen, what stayed unchanged, and who approved it.
   - Name things by what they are, not by numbered codes. Call people by name or "the user", not by role titles.
   - Avoid chains of "not a …" qualifiers.
4. Treat clean structure as ready for review. It is not scientific, ethical, legal, release, or publication approval.
