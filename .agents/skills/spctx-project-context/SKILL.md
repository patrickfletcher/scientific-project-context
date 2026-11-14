---
name: spctx-project-context
description: Set up or repair a project's working context so the next contributor or session can pick the work up safely. Use when asked to "initialize" or "set up context" in a repository, retrofit an existing project, install a new version of scientific-project-context (`spctx`) or bring a project up to date after one, refresh context that no longer matches the code or data, decide whether a topic needs its own document, or retire a stale document. Do not use for ordinary implementation, analysis changes, or writing public documentation.
---

# Project Context

Purpose: establish, activate, refresh, separate, retire, upgrade, or share compact and trustworthy project context without making documentation the project.
Use when: initializing an empty project, retrofitting an existing project, repairing stale context, deciding whether recurring detail needs another home, reviewing whether context still serves the work, or retiring context that is no longer current. A routine in-place update of an answer or the current focus needs no skill.

Before acting, say that you are using `spctx-project-context` and which mode
applies. Restate the mode when it changes.

## Modes

- **initialize**: establish the minimum context needed for the next meaningful step.
- **refresh**: reconcile current context with repository reality.
- **separate**: move one recurring topic from the compact context into a focused source.
- **retire**: remove a source from current context after moving any still-current rule, evidence, or route to the place it belongs.
- **localize**: record this project's field conventions, review requirements, and evidence expectations in the practice contract.
- **upgrade**: reconcile the project's packaged files with a newly installed `spctx` version.
- **review**: find contradictions, repetition, and misplaced material across the context, and propose fixes.

Read the steps your mode needs, not all of them:

| Mode | Steps |
| --- | --- |
| initialize | 1, 2, 3, 4, 5, 11, 13 |
| refresh | 1, 2, 4, 8, 13 |
| separate | 1, 6, 7, 13 |
| retire | 8, 13 |
| localize | 1, 10, 13 |
| upgrade | 9, 11, 13 |
| review | 1, 6, 12, 13 |

For writing a README, methods text, a report, or any other material aimed at
readers outside the immediate work, use `spctx-public-writing` instead.

## 1. Inspect Before Asking

Read `AGENTS.md`, `.context/scientific-practice.md`, `.context/project.md`, and `.context/index.md`, the generated index, and from the index select only the sources relevant to the task. Treat the scientific-practice file as the stable cross-project contract and the project file as its current project-specific application.

For an existing project, inspect targeted evidence before asking questions:

- README and current public documentation
- data and sample provenance, notebooks, scripts, source entry points, manifests, environments, tests, examples, and CI
- protocols, controls, transformations, exclusions, models, parameters, schemas, calibration or acquisition records, instrument state, configurations, and output locations
- visible provenance, safety, access, licensing, citation, and governance constraints

Classify findings as observed, proposed interpretation, or unknown. Filenames alone do not establish scientific meaning or who may change something.

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
| `.context/project.md` and the other documents under `.context/` | humans and agents, on demand | Scientific purpose, current state, evidence, risks, and open decisions. |

Each durable fact belongs in exactly one place; the others link to it. When a
fact is both operational and scientifically material, such as a protected input,
put the one-line constraint in the instruction file and the reasoning in project
context.

The list of context documents follows the same rule. `.context/index.md` holds
it, generated from the opening lines of every Markdown file under `.context/`.
Do not keep another list of them in `project.md`, in a folder's own README, or
in the instruction file, and remove one when you find it: a hand-kept list
drifts from the files. Link a document only where a statement points to its
detail.

Fill the `Project Essentials` block in `AGENTS.md` early, because an agent that
cannot activate the right environment or run the tests will guess. Replace every
bracketed prompt with this project's answer or delete the line. If `spctx` is
used at all, say which environment it is installed in, using the interpreter the
`init` report names, as a path relative to the repository or the home directory;
agents otherwise report the command unavailable. Record the command that
upgrades `spctx` there too, with the source it was installed from, which
`pip freeze` or `uv pip freeze` shows. Leave out user names and version numbers:
the file is shared across machines.

Keep transient counts, verification tallies, and internal vocabulary out of
public documentation. Anything a collaborator reads should be readable by an
interested outsider in the field: ordinary scientific and engineering English,
abbreviations defined on first use, each limitation stated once. Do not import
this system's vocabulary into a project that has its own terms.

## 3. Establish Durable Activation

Installing context files is not the same as activating them. Reliable maintenance requires one project-authorized instruction file that agents actually read, routing them to `.context/project.md`, this skill, and `spctx-scientific-change` when relevant.

- For a new project using the packaged `AGENTS.md`, the route becomes active after initialization is applied.
- For a retrofit, keep existing instructions authoritative. Compare them with the compact project-context routing block reported by `spctx init`, resolve material conflicts, and ask whoever maintains the project's instructions to approve adding only that route. Replace any earlier SPCTX routing block instead of duplicating it; do not replace the full instruction file merely to install this system.
- Once the route is active in a retrofit, offer the packaged instruction sections one at a time, rewritten for this project, and let the user refuse any; `spctx init . --dry-run` prints the packaged file. Start with `Project Essentials`. Link to an existing conventions file instead of restating it, and keep no second copy of the instruction file.
- Confirm that the agents in use discover `.agents/skills/`; file presence alone is not behavioral evidence.
- Claude Code reads neither `.agents/skills/` nor any other path under `.agents/`, and reads `AGENTS.md` only while the project has no `CLAUDE.md` above the working directory. For a project that uses it, `spctx init . --claude` adds pointer skills under `.claude/skills/` that carry the same descriptions and route to the canonical files. Where a `CLAUDE.md` already exists, ask whoever maintains it to add an `@AGENTS.md` import line to it rather than keeping a second copy of the instructions.
- Beyond that, other skill layouts are outside what this system manages. Never duplicate a procedure body to reach another host.
- If no instruction file the agents read may be changed, report `manual_activation_required`. The files may still be used when explicitly requested, but do not claim that future agents will discover or maintain them automatically.

## 4. Draft the Compact Context

Populate or refresh only applicable sections of `.context/project.md`:

- purpose, user, useful outcome, and what the work builds on from its field
- current materials and entry points, how a result or behavior is checked, and operating conditions that affect the science
- current focus and next meaningful step
- protected inputs the work takes as given
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

Start every current context source with short `Purpose`, `Read when`, and `Update when` lines, so a reader can pick the right one without opening all of them. The index shows the first two; the third tells the next editor when the document needs changing.

## 5. Ask Only Material User-Owned Questions

Ask a small batch only for facts or decisions the project cannot establish. Prioritize questions that block the next step: scientific meaning, intended outcome, permission to change something, expected validation behavior, safety, access, scope, or a material source conflict.

Draft a proposed validation check from project evidence when possible; let the user correct its scientific meaning or expected signal. Do not make the user restate observable paths or commands.

## 6. Decide Whether Another Source Is Warranted

Keeping a fact in the compact context is the default. Suggest a focused source only when the information:

1. must remain useful across sessions,
2. has a distinct update trigger or responsible party, and
3. materially harms the compact context's scanability.

Prefer an established issue tracker, README, data dictionary, architecture document, test plan, or public specification when it already holds the fact.

A record that gains an entry each time a run finishes or a step completes meets
all three conditions and is still not context: it is a log. Leave run records
beside the outputs, written by the code that produced them, and leave narrative
history to Git. A focused source's `Update when` line should name a change in
what it says is true, such as an answer, a method, or a decision, not an event
such as a run finishing.

Records gain entries in other shapes too: a section per study, forwarding
stubs, dated snapshots, and narration of when and how a number was measured are
logs as well. A plan is finite: its goal, deliverables with stopping conditions,
and what is outside them. Delete it when the deliverables land.

Split by why a passage changes, not by how long a document is. A passage that
changes when the project's state changes, such as a judgment made, a decision
taken, a priority moved, or a question answered, stays in context. A passage
that changes only when an outside source, firmware, or tool code changes is
reference or tool documentation, and belongs beside what it describes or under
`docs/`. A passage that says how to run a procedure or how a number was obtained
belongs beside the procedure or in a record. Context keeps the finding and a
link, and copies a measured number or a decision only as a link to where it
lives. Rules a contributor must honor before acting stay in context or the
instruction file even when they are stable.

Every file under `.context/` appears in the index, so add one there only when it
is current context. Anything that is not should live elsewhere in the
repository, or only in Git history.

## 7. Draft, Review, and Integrate

When another source is justified:

1. Explain the recurring detail and proposed home in one short paragraph.
2. Draft supported content. Mark the document with a line reading `DRAFT CONTEXT - REVIEW REQUIRED` only when it holds an interpretation you drafted that nobody has confirmed; content moved from confirmed sources, or a document the user asked for, needs none.
3. Make unknowns explicit instead of inventing them.
4. Ask the user to confirm only consequential scientific meaning, permission to change, safety, claims, licensing, ethics, or governance.
5. Remove the marker after supported facts and material judgments are confirmed.
6. Replace moved detail in `.context/project.md` with a short link.
7. Run `spctx sync-index .` so the index lists it.

Creating the clearest project-specific document directly remains valid; the index lists it by its own opening lines.

Do not repeat a declined suggestion unless the recurring detail materially changes.

## 8. Maintain and Retire Context

Maintenance is event-driven, not a periodic documentation ritual. At the end of work, update only facts that actually changed: executable reality, current focus or next step, protected inputs, scientific risk, checks, current findings or staleness, unresolved questions, and the index when a document was added, renamed, or removed. Remove resolved prompts and completed transient work rather than accumulating a work log.

When a document has already become a log, rewrite it as current state instead of
trimming entries: keep the current answers, their limits, and what is still
open, and let Git hold the rest. Trimming leaves the style in place for the next
session to copy. If an instruction or a source's `Update when` line asks for an
entry per run, change that rule as well, or the log grows back.

If the work made something load-bearing, such as a choice, a parameter, a
calibration, or an exclusion that the next piece of work will now assume,
propose adding it to the relied-on list in `.context/project.md` and let the
user decide. When nothing did, do not ask. That list is empty by default, and
nothing else in the system will notice when it should stop being empty.

When an input, method, setting, dependency, environment, or public behavior changes under something the relied-on list names, use `spctx-scientific-change` to identify affected evidence and outputs, and rerun them or mark them stale. Exploratory results need neither. Age alone is not a reason to discard evidence that is discrepant, negative, protected, or supports a reported claim.

When `spctx check` reports passages repeated among the project's own documents,
prune rather than clear the list; it matches words only and misses the same fact
reworded. Keep each fact in the document whose update trigger matches it,
usually the most specific one, and link from the other. Repetition is fine when
the statements serve different readers or moments, such as a one-line rule in
the instruction file and its reasoning in context. Never resolve it by rewording
one copy.

When a context source is no longer current or useful:

1. Identify any rule, decision, evidence, uncertainty, or route that still matters.
2. Move each still-current item to the project or public document where it belongs, without duplicating it.
3. Search code, notebooks, scripts, and configuration for the source's path, and fix or report anything that reads it. Repoint links and anchors that lead to it; `spctx check` reports a link whose file is gone.
4. With the project's normal permission to change files, remove the retired source from current navigation and from the working tree. Use Git history for superseded planning and narrative unless project governance requires a separate record.
5. Run `spctx sync-index .` so the index drops it, then `spctx check .`.

## 9. Upgrade to a New Package Version

Use this mode when a newly installed `spctx` may have changed the packaged
files. The trigger is the new version, not a change in the repository. Upgrade
on the branch others merge from, so every branch receives the same packaged
text; `spctx check` names the package version each tracked region matches.

If you are also asked to install the new version, do that first, with the
upgrade command the instruction file records, then confirm with
`spctx --version`. If none is recorded, find the source the current version came
from, or ask. Never
install this package by name from a public package index: it is not published
there, and whoever registers that name would be installed instead.

1. If this skill's own body differs from the packaged one, restore it first,
   from the text `spctx init . --dry-run` prints, and follow the rest of this
   section from the restored copy. The steps in an older copy belong to the
   version it came from.
2. Run `spctx init . --dry-run` to see whether the new version ships a file this
   project does not have yet, then apply it with `spctx init .`, adding
   `--claude` when the project has pointer skills under `.claude/skills/`.
   Occupied files are never overwritten, and `spctx check` reports little else
   until every starter file is present.
3. Run `spctx check . --diff`. It names every region that tracks the package,
   and prints the exact text that differs. A region carrying this project's own
   trigger phrasings is reported as tuning, not as something to undo.
4. Where the routing block differs, replace the text between its markers with
   the current packaged block. It is the only part of the instruction file the
   package maintains, and a stale one can point at skills or files that have moved.
   Everything outside the markers is the project's.
5. Compare the rest of the instruction file with the packaged one, which
   `spctx init . --dry-run` also prints. Offer packaged lines whose point this
   project's file lacks, one section at a time and in the packaged wording, and
   let the user refuse any. Skip what the project has replaced with its own
   rule. Do not write always-read lines from the core or a skill instead: they
   would repeat text the package maintains elsewhere.
6. Where the scientific-practice core differs, replace the text between its
   markers with the packaged core that `spctx init . --dry-run` prints. A new
   version usually changes it, so a difference here is expected rather than a
   sign that someone edited it. Keep the project's own section below the
   markers, and move any wording the project added inside them there first.
7. Compare the rest of the practice file with the packaged one, which
   `spctx init . --dry-run` prints when they differ. Offer changed packaged
   lines as in step 5, and leave the project's own section and answered
   prompts alone.
8. Resolve what `spctx check .` reports about the index and the files beside it.
   Run `spctx sync-index .` when the list is out of date. Where it reports text
   the project wrote in a file the package generates or does not use, move
   anything still needed to `.context/project.md` or another context document,
   then delete that file.
9. Where a skill body diverged, restore the packaged body. `spctx init . --dry-run`
   prints the packaged text of every retained skill, and
   `--json` carries the same text under `context_adoption.suggested_skills`, so
   take it from there rather than reconstructing it from a diff. Project facts
   belong in the instruction file or `.context/`, not in a modified procedure.
10. Where a description diverged, restore the packaged text and re-append this
   project's phrasings after the separator, following section 11. Never
   drop packaged trigger categories to make room for project ones.
11. Read the whole always-read instruction file, not only the sections you just
   edited, and remove any rule it states twice, once there and once in a skill
   or a context source. Wording an older packaged version left behind does not
   become project policy by sitting there. Where the project wrote its own
   section restating what the routing block now says, such as an exploratory
   default or rules about when to ask, keep the lines specific to this project
   and delete the restatement. A restatement for a different reader or moment
   is not a duplicate, as Maintain and Retire Context explains; the packaged
   instruction file's own lines are written that way.
12. List what earlier versions of this system left in the project's own text
   and code, with counts and places: role titles used for people instead of
   names or "the user"; approval, sign-off, and gate wording;
   review markers on documents the user asked for; precedence lists that rank
   the safeguards by number; and code that hashes its own source, refuses to
   run when its source or inputs changed, or writes freshness or review
   signatures for exploratory outputs. Propose changes and let the user
   choose. Change context text when asked, and code only on an explicit
   request. For a word used hundreds of times, propose adding it to the
   project's words to avoid and rewriting it where documents are next edited.
13. Re-run `spctx check .`, then report on separate lines: which packaged changes
   you applied; how many duplicated rules you removed and which duplicates you
   deliberately kept; whether each skill description carries this project's
   phrasings, adding them per section 11 if it does not; what step 12 found;
   and anything the project must decide.

A `spctx check` run with nothing left to do does not show that the new
version's guidance suits this project; say what you applied and what you
skipped.

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
work is actually held to, what review it owes before it is published, if any,
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

The packaged descriptions are generic. The strongest routing signal is the
vocabulary this project's people actually use, so once the domain is clear, add
it.

Keep the packaged description exactly as it is and append three to six real
example phrasings from this project after the separator:

    description: <packaged text, unchanged> Also use for requests such as: "exclude these samples", "change the smoothing window", "refit the decay model".

Use the words a contributor here would type. Keep the whole description under
1024 characters and the `name` matching its directory. If the project has
pointer skills under `.claude/skills/`, copy each tuned description into its
pointer in the same turn.

Do not rewrite or shorten the packaged part: it carries the general trigger
categories and later packaged improvements.

Everything from the separator onward is the project's and survives an upgrade;
`spctx check` reports how many descriptions carry project phrasings. Keep
project facts out of the body, which is packaged too. Propose the edit and let
the user confirm the vocabulary.

## 12. Review Context

Use this mode when context has grown past what a routine refresh fixes, or when
the user asks whether it still serves the work. Inspect and propose; do not
restructure yet.

1. List each context document with its length and the kinds of passage it
   holds: current state and decisions, findings, stable reference, tool
   manuals, plans and protocols, and measurement provenance. Note documents
   whose passages change for different reasons.
2. Look for contradictions first: two statements of one rule or number that
   disagree, including reworded copies, which `spctx check` cannot see. Then
   look for stale statements, numbers copied from where they live, session
   dates used to identify evidence, plans kept in several places, broken links,
   and what step 12 of the upgrade lists.
3. Propose fixes in order of cost: contradictions and stale lines, then one
   home for each repeated fact, then any split or move by the rule in section 6.
4. Write the result as a short dated report outside `.context/`, or in your
   reply, leading with the contradictions. Apply routine fixes when the user
   asks; restructuring waits for the user's go-ahead. Delete the report once its
   proposals are applied or declined.

## 13. Report

Report the activation state, context established or refreshed, material questions that remain, focused sources created, retired, or deliberately avoided, and the next meaningful step. Do not claim scientific or release readiness from documentation structure alone.
