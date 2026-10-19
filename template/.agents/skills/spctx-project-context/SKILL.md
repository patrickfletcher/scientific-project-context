---
name: spctx-project-context
description: Set up or repair a project's working context so the next contributor or session can pick the work up safely. Use when asked to "initialize" or "set up context" in a repository, retrofit an existing project, bring a project up to date after installing a new version of this package, refresh context that no longer matches the code or data, decide whether a topic needs its own document, or retire a stale document. Do not use for ordinary implementation, analysis changes, or writing public documentation.
---

# Project Context

Purpose: establish, activate, refresh, separate, retire, upgrade, or share compact and trustworthy project context without making documentation the project.
Use when: initializing an empty project, retrofitting an existing project, repairing stale context, deciding whether recurring detail needs another home, or retiring context that is no longer current.

Before acting, say that you are using `spctx-project-context` and which mode
applies. Restate the mode when it changes. Without that, nobody can tell whether
this procedure was followed or the work merely resembled it.

## Modes

- **initialize**: establish the minimum context needed for the next meaningful step.
- **refresh**: reconcile current context with repository reality.
- **separate**: move one recurring topic from the compact context into a focused source.
- **retire**: remove a source from current context after moving any still-current rule, evidence, or route to the place it belongs.
- **localize**: record this project's field conventions, review requirements, and evidence expectations in the practice contract.
- **upgrade**: reconcile the project's packaged files with a newly installed `spctx` version.

Read the steps your mode needs, not all of them:

| Mode | Steps |
| --- | --- |
| initialize | 1, 2, 3, 4, 5, 11, 12 |
| refresh | 1, 2, 4, 8, 12 |
| separate | 1, 6, 7, 12 |
| retire | 8, 12 |
| localize | 1, 10, 12 |
| upgrade | 9, 11, 12 |

For writing a README, methods text, a report, or any other material aimed at
readers outside the immediate work, use `spctx-public-writing` instead.

## 1. Inspect Before Asking

Read `AGENTS.md`, `.context/scientific-practice.md`, and `.context/project.md`. If `.context/README.md` exists, use it as the context index and select only sources relevant to the task. Treat the scientific-practice file as the stable cross-project contract and the project file as its current project-specific application.

For an existing project, inspect targeted evidence before asking questions:

- README and current public documentation
- data and sample provenance, notebooks, scripts, source entry points, manifests, environments, tests, examples, and CI
- protocols, controls, transformations, exclusions, models, parameters, schemas, calibration or acquisition records, instrument state, configurations, and output locations
- visible provenance, safety, access, licensing, citation, and governance constraints

Classify findings as observed, proposed interpretation, or unknown. Filenames alone do not establish scientific meaning or change authority.

Also identify which instruction files the agents in use actually read, such as `AGENTS.md` or a project-owned platform-specific instruction or skill path. Presence alone does not establish that an agent reads a file.

If the repository already has a conventions or instructions file, such as `.github/copilot-instructions.md`, `.github/instructions/`, a contributing guide, or lint and formatter configuration, treat it as authoritative and link to it. Do not restate or compete with its rules.

## 2. Put Each Fact in the Right Place

Decide where a fact belongs before writing it. Getting this wrong is the most
common and most expensive initialization error: the same environment,
dependency, and command detail ends up copied into all three places, and none of
them is trustworthy afterward.

| Place | Reader | Holds |
| --- | --- | --- |
| `AGENTS.md` or another instruction file the agents in use actually read | agents, every session | Operational constraints to honor before acting: environment activation and which tools are installed there, run and test commands, protected inputs in one line, conventions, and routes. |
| `README.md` and other public documentation | humans, including outsiders | Purpose in plain language, setup, commands, and outputs. |
| `.context/project.md` and its focused sources | humans and agents, on demand | Scientific purpose, current state, evidence, risks, and open decisions. |

Each durable fact belongs in exactly one place; the others link to it. When a
fact is both operational and scientifically material, such as a protected input,
put the one-line constraint in the instruction file and the reasoning in project
context.

Fill the `Project Essentials` block in `AGENTS.md` early, because an agent that
cannot activate the right environment or run the tests will guess. Record the
environment, the exact run and test commands, protected inputs, and conventions.
Replace every bracketed prompt with this project's answer or delete the line; a
prompt left in place is not an answer. If `spctx` is used at all, say
which environment it is installed in — the command is only reachable from
that environment, and agents otherwise report it as unavailable and work
around it. The `init` report names the interpreter it ran from, so record that
observed path instead of guessing one.

Keep transient counts, verification tallies, and internal vocabulary out of
public documentation. Anything a collaborator reads should be readable by an
interested outsider in the field: ordinary scientific and engineering English,
abbreviations defined on first use, each limitation stated once. Do not import
this system's vocabulary into a project that has its own terms.

## 3. Establish Durable Activation

Installing context files is not the same as activating them. Reliable maintenance requires one project-authorized instruction file that agents actually read, routing them to `.context/project.md`, this skill, and `spctx-scientific-change` when relevant.

- For a new project using the packaged `AGENTS.md`, the route becomes active after initialization is applied.
- For a retrofit, keep existing instructions authoritative. Compare them with the compact project-context routing block reported by `spctx init`, resolve material conflicts, and ask the project authority to approve adding only that route. Replace any earlier SPCTX routing block instead of duplicating it; do not replace the full instruction file merely to install this system.
- Once the route is active in a retrofit, the project has the skills but none of the packaged instruction guidance. Offer those sections one at a time, rewritten for this project, and let the user refuse any of them. Start with `Project Essentials`: real use showed that an agent without it invents its own setup. Leave out anything a conventions file here already covers, and link to that file instead. Git is the backup; do not save a second copy of the instruction file.
- The complete canonical procedures live in `spctx-project-context` and `spctx-scientific-change` under `.agents/skills/`. Confirm that the agents in use discover this layout; file presence alone is not behavioral evidence.
- Claude Code reads neither `.agents/skills/` nor any other path under `.agents/`, and reads `AGENTS.md` only while the project has no `CLAUDE.md` above the working directory. For a project that uses it, `spctx init . --claude` adds pointer skills under `.claude/skills/` that carry the same descriptions and route to the canonical files. Where a `CLAUDE.md` already exists, ask the project authority to add an `@AGENTS.md` import line to it rather than keeping a second copy of the instructions.
- Beyond that, other skill layouts are outside what this system manages. Never duplicate a procedure body to reach another host.
- If no instruction file the agents read may be changed, report `manual_activation_required`. The files may still be used when explicitly requested, but do not claim that future agents will discover or maintain them automatically.

## 4. Draft the Compact Context

Populate or refresh only applicable sections of `.context/project.md`:

- purpose, user, and useful outcome
- current materials and entry points, how a result or behavior is checked, and operating conditions that affect the science
- current focus and next meaningful step
- protected or curated material that must not change silently
- what later work now relies on, kept short: the default is that nothing is settled, and only the exceptions are named
- main way the current result or behavior could be wrong
- smallest useful check or observation and expected signal
- current findings: the answer to each open question, its uncertainty and main limit, and the assumptions and settings it rests on
- unresolved questions that must persist
- sharing or reuse intent when it is already relevant

Remove resolved prompts. Use explicit unknowns rather than filling sections speculatively. Link to existing sources instead of copying them, and leave environment, dependency, and command detail to `AGENTS.md` and `README.md`.

Write it as current state, rewritten in place and short enough to read on one
screen. It is also the example later sessions imitate: lead with what is known,
state each limit once, and keep out run history, permissions, and lists of what
did not change.

Start every current context source with short `Purpose`, `Read when`, and `Update when` lines, so a reader can pick the right one without opening all of them.

## 5. Ask Only Material User-Owned Questions

Ask a small batch only for facts or decisions the project cannot establish. Prioritize questions that block the next step: scientific meaning, intended outcome, change authority, expected validation behavior, safety, access, scope, or a material source conflict.

Draft a proposed validation check from project evidence when possible; let the user correct its scientific meaning or expected signal. Do not make the user restate observable paths or commands.

## 6. Decide Whether Another Source Is Warranted

Keeping a fact in the compact context is the default. Suggest a focused source only when the information:

1. must remain useful across sessions,
2. has a distinct update trigger or responsible party, and
3. materially harms the compact context's scanability.

Common signals include several independently moving tasks, consequential choices whose rationale must be revisited, multiple validation/evidence states, non-obvious artifact transformations or change boundaries, recurring scientific conventions, or multi-stage sequencing.

These signals are examples, not a required document taxonomy. Prefer an established issue tracker, README, data dictionary, architecture document, test plan, or public specification when it already holds the fact. A project-specific source may be clearer than any packaged starter.

A record that gains an entry each time a run finishes or a step completes meets
all three conditions and is still not context: it is a log. Leave run records
beside the outputs, written by the code that produced them, and leave narrative
history to Git. A focused source's `Update when` line should name a change in
what it says is true, such as an answer, a method, or a decision, not an event
such as a run finishing.

A context index becomes useful only when several focused sources make selection non-obvious.

## 7. Draft, Review, and Integrate

When another source is justified:

1. Explain the recurring detail and proposed home in one short paragraph.
2. Draft supported content and mark it with a line reading `DRAFT CONTEXT - REVIEW REQUIRED`.
3. Make unknowns explicit instead of inventing them.
4. Ask the user to confirm only consequential scientific meaning, change authority, safety, claims, licensing, ethics, or governance.
5. Remove the marker after supported facts and material judgments are confirmed.
6. Replace moved detail in `.context/project.md` with a short link.
7. Synchronize the context index if navigation is no longer obvious.

Synchronize the index only after context routes change. Creating the clearest project-specific source directly remains valid; the tool does not prescribe its kind or scientific content and never makes generated content authoritative.

Do not repeat a declined suggestion unless the recurring detail materially changes.

## 8. Maintain and Retire Context

Maintenance is event-driven, not a periodic documentation ritual. At the end of work, update only facts that actually changed: executable reality, current focus or next step, protected inputs, scientific risk, checks, current findings or staleness, unresolved questions, and context routes. Remove resolved prompts and completed transient work rather than accumulating a work log.

When a document has already become a log, rewrite it as current state instead of
trimming entries: keep the current answers, their limits, and what is still
open, and let Git hold the rest. Trimming leaves the style in place for the next
session to copy. If an instruction or a source's `Update when` line asks for an
entry per run, change that rule as well, or the log grows back; real use saw two
cleanups undone within days this way.

Ask once, at that point, whether anything became load-bearing during the work: a
choice, a parameter, a calibration, an exclusion that the next piece of work will
now assume. If so, propose adding it to the relied-on list in `.context/project.md`
and let the user decide. That list is empty by default, and nothing else in the
system will notice when it should stop being empty.

When an input, method, setting, dependency, environment, or public behavior changes, use `scientific-change` to identify affected evidence and outputs. Rerun them or mark them stale; age alone is not a reason to discard evidence that is discrepant, negative, protected, or supports a reported claim.

When `spctx check` reports passages repeated among the project's own documents,
treat that as a prompt to prune, not as a list to clear. It matches words only,
so it sees a copied passage and misses the same fact reworded. Read the
affected documents and look for the reworded case too.

For each fact stated twice, decide which document keeps it: the one whose update
trigger and responsible party match the fact, usually the most specific one.
Leave a short link from the other. Repetition is fine when the two statements
serve different readers or moments, such as a one-line operational constraint in
the instruction file and its reasoning in project context. It is not fine when
both claim to be current and can drift apart. Never resolve this by rewording
one copy: that hides the repetition from the next check without giving the fact
a single home.

When a context source is no longer current or useful:

1. Identify any rule, decision, evidence, uncertainty, or route that still matters.
2. Move each still-current item to the project or public document where it belongs, without duplicating it.
3. With the project's normal permission to change files, remove the retired source from current navigation and from the working tree. Use Git history for superseded planning and narrative unless project governance requires a separate record.
4. If focused routes changed, preview and apply `spctx sync-index`; then run `spctx check .`.

## 9. Upgrade to a New Package Version

Use this mode when a newly installed `spctx` may have changed the packaged
files. The trigger is the new version, not a change in the repository.

1. Run `spctx check . --diff`. It names every region that tracks the package,
   and prints the exact text that differs. A region carrying this project's own
   trigger phrasings is reported as tuning, not as something to undo.
2. Where the routing block differs, replace the text between its markers with
   the current packaged block. It is the only part of the instruction file the
   package maintains, and a stale one can point at skills or files that have moved.
   Everything outside the markers is the project's.
3. Where the scientific-practice core differs, replace the text between its
   markers with the packaged core that `spctx init . --dry-run` prints. A new
   version usually changes it, so a difference here is expected rather than a
   sign that someone edited it. Keep the project's own section below the
   markers, and move any wording the project added inside them there first.
4. Run `spctx init . --dry-run` to see whether the new version ships a file this
   project does not have yet, then apply it with `spctx init .`. Occupied files
   are never overwritten.
5. Where a skill body diverged, restore the packaged body. `spctx init . --dry-run`
   prints the packaged text of every retained skill, and
   `--json` carries the same text under `context_adoption.suggested_skills`, so
   take it from there rather than reconstructing it from a diff. Project facts
   belong in the instruction file or `.context/`, not in a modified procedure.
6. Where a description diverged, restore the packaged text and re-append this
   project's phrasings after the separator, following step 11. Never
   drop packaged trigger categories to make room for project ones.
7. Read the whole always-read instruction file, not only the sections you just
   edited, and remove any rule it states twice, once there and once in a skill
   or a context source. Wording an older packaged version left behind does not
   become project policy by sitting there. Keep the project's own rules and
   delete only the duplicate.
8. Re-run `spctx check .`, then report on separate lines: which packaged changes
   you applied; how many duplicated rules you removed and which duplicates you
   deliberately kept; whether each skill description carries this project's
   phrasings, adding them per step 11 if it does not; and anything the
   project must decide.

`spctx check` reports state rather than a verdict, so a run with nothing left to
do does not show that the new version's guidance suits this project. Say plainly
what you applied and what you skipped.

## 10. Make the Practice Contract This Project's

The marked core in `.context/scientific-practice.md` ships to every project and
knows nothing about this field. The section below it is the project's, and
`spctx check` reports whether anything has been written there yet.

Do not invent a field's conventions. Draft them from something real, in this
order of preference: a standard, protocol, or reporting guideline the project
already names; the lab's own prior papers, methods sections, or protocols when
the user points at them; and what the code, configuration, and curated decisions
visibly already do. Say which of those each proposed line came from.

Then ask the scientist only what the project cannot show: which standards this
work is actually held to, what review or approval it owes and who signs it off,
and what a reviewer in this field would want to see before believing a result.

Keep it short. Four lines a reviewer would recognize are worth more than a page
of general good practice, and anything the core already covers should not be
restated. Deciding that the shared core is enough is a complete answer: write
that one line rather than leaving the section as shipped prompts.

A project that adopted an earlier version has no such section. Add it below the
end marker rather than waiting for a tool to place it.

Do not move project conventions inside the markers. Text there tracks the
package and an upgrade will overwrite it.

## 11. Tune the Skill Triggers to This Project

The packaged skill descriptions are written generically because they ship to
every project. The strongest routing signal is the vocabulary this project's
people actually use, so once the domain is clear, improve them.

Keep the packaged description exactly as it is and append three to six real
example phrasings from this project after the separator:

    description: <packaged text, unchanged> Also use for requests such as: "exclude these samples", "change the smoothing window", "refit the decay model".

Use the words a contributor here would type, not generic ones. Keep the whole
description under 1024 characters and the `name` matching its directory. If the
project has pointer skills under `.claude/skills/`, copy each tuned description
into its pointer in the same turn; `spctx` generates a pointer once and never
rewrites it, so `check` reports the disagreement until someone does.

Do not rewrite or shorten the packaged part. It carries the general trigger
categories, so replacing it both narrows what the skill answers to and stops
later packaged trigger improvements from reaching this project.

Everything from the separator onward is project-owned and survives an upgrade.
Adding it is the intended outcome, and `spctx check` reports how many
descriptions carry project phrasings so an untuned project stays visible without
being told what its vocabulary should be. The body is packaged as well: put
project facts in the instruction file or `.context/`, not in a modified copy of
the procedure. Departing from either rule is allowed, and `check` reports it so
the cost stays visible instead of silent. Propose the edit and let the user
confirm the vocabulary is right.

## 12. Report

Report the activation state, context established or refreshed, material questions that remain, focused sources created, retired, or deliberately avoided, and the next meaningful step. Do not claim scientific or release readiness from documentation structure alone.
