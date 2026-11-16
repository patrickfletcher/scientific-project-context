---
name: spctx-project-context
description: Set up or repair a project's working context so the next contributor or session can pick the work up safely. Use when asked to "initialize" or "set up context" in a repository, retrofit an existing project, install a new version of scientific-project-context (`spctx`) or bring a project up to date after one, refresh context that no longer matches the code or data, decide whether a topic needs its own document, review whether the context still serves the work, or retire a stale document. Do not use for ordinary implementation, analysis changes, or writing public documentation.
---

# Project Context

Purpose: establish, activate, refresh, separate, review, retire, or upgrade compact and trustworthy project context without making documentation the project.
Use when: initializing or retrofitting a project, repairing stale context, deciding whether recurring detail needs its own document, reviewing the context, retiring a document, or upgrading after a new `spctx` version.

A routine in-place update of an answer or the current focus needs no skill.

Before acting, say that you are using `spctx-project-context` and which mode
applies. Say it again when the mode changes.

## Modes

- **initialize**: establish the minimum context for the next meaningful step.
- **refresh**: reconcile the context with the repository as it is now.
- **separate**: move one recurring topic from the compact context into its own context document.
- **retire**: remove a context document after moving anything still current to where it belongs.
- **localize**: record this project's field conventions, review requirements, and evidence expectations in the practice contract.
- **upgrade**: bring the project's packaged text up to a newly installed `spctx` version.
- **review**: find contradictions, repetition, and misplaced material across the context, and propose fixes.

Read only the steps your mode needs:

| Mode | Steps |
| --- | --- |
| initialize | 1, 2, 3, 4, 5, 11, 13 |
| refresh | 1, 2, 4, 8, 13 |
| separate | 1, 6, 7, 13 |
| retire | 8, 13 |
| localize | 1, 10, 13 |
| upgrade | 9, 11, 13 |
| review | 1, 6, 12, 13 |

For a README, methods text, a report, or other text for readers outside the
work, use `spctx-public-writing` instead.

## 1. Inspect Before Asking

Read `AGENTS.md`, `.context/scientific-practice.md`, `.context/project.md`, and
`.context/index.md`. From the index, open only the context documents the task
needs. The practice file is the stable contract; the project file applies it to
this project.

For an existing project, inspect the evidence before you ask anything:

- the README and current public documentation;
- data and sample provenance, notebooks, scripts, entry points, manifests, environments, tests, examples, and CI;
- protocols, controls, transformations, exclusions, models, parameters, schemas, calibration or acquisition records, instrument state, configurations, and output locations;
- visible provenance, safety, access, licensing, citation, and governance constraints.

Classify what you find as observed, proposed interpretation, or unknown. A
filename does not establish scientific meaning or who may change something.

Find which instruction files the agents in use actually read: `AGENTS.md`, or a
platform-specific instruction or skill path. A file that exists is not proof
that an agent reads it.

If the repository already has a conventions or instructions file, follow it and
link to it. Examples are `.github/copilot-instructions.md`,
`.github/instructions/`, a contributing guide, or lint and formatter
configuration. Do not restate or compete with its rules.

## 2. Put Each Fact in the Right Place

Decide where a fact belongs before you write it. Placing facts badly is the most
common and most expensive setup error. Environment, dependency, and command
detail gets copied into all three places, and then none of them can be trusted.

| Place | Reader | Holds |
| --- | --- | --- |
| `AGENTS.md`, or the instruction file the agents actually read | agents, every session | Rules to follow before acting: environment activation and its tools, run and test commands, protected inputs in one line, conventions, and routes. |
| `README.md` and other public documentation | humans, including outsiders | Purpose in plain language, setup, commands, and outputs. |
| `.context/project.md` and other context documents | humans and agents, on demand | Scientific purpose, current state, evidence, risks, and open decisions. |

Each durable fact gets one home, and the other places link to it. A fact can
be operational and scientifically material, such as a protected input. Put its
one-line rule in the instruction file and its reasons in context.

The index follows the same rule. `.context/index.md` holds
it, generated from the opening lines of every Markdown file under `.context/`.
Do not keep another list of them in `project.md`, a folder README, or the
instruction file. If you find one, remove it; a list kept by hand drifts. Link a
document only where a statement points to its detail.

Fill the `Project Essentials` block in `AGENTS.md` early. An agent that cannot
activate the environment or run the tests will guess. Replace every bracketed
prompt with this project's answer, or delete the line. For `Context tools`, copy
the line that the `spctx init` report prints. It names which environment `spctx`
is installed in and the command that upgrades it from its source. It has no user
names; if it says a path is specific to one machine, say so where you record it.

Keep transient counts, verification tallies, and internal vocabulary out of
public documentation. Anything a collaborator reads should be readable by an
interested outsider in the field. Use ordinary scientific and engineering
English, define abbreviations on first use, and state each limit once. Do not
bring this system's vocabulary into a project that has its own words.

## 3. Establish Durable Activation

Installed files do nothing until an agent is directed to them. One instruction
file that the agents actually read must route them to `.context/project.md`,
this skill, and `spctx-scientific-change`.

- **New project with the packaged `AGENTS.md`**: the route is active once initialization is applied.
- **Retrofit**: keep the existing instructions. Compare them with the routing block that `spctx init` reports, and resolve real conflicts. Ask whoever maintains the instructions to approve adding only that block. Replace an earlier SPCTX routing block; do not add a second one.
- **After a retrofit's route is active**: offer the packaged instruction sections one at a time, rewritten for this project. The user may refuse any of them. `spctx init . --dry-run` prints the packaged file. Start with `Project Essentials`. Link to an existing conventions file instead of restating it, and keep no second copy of the instruction file.
- **Skill discovery**: confirm that the agents in use discover `.agents/skills/`. A file that exists is not evidence of behavior.
- **Claude Code**: it reads nothing under `.agents/`, and it reads `AGENTS.md` only when no `CLAUDE.md` exists above the working directory. `spctx init . --claude` adds pointer skills under `.claude/skills/` with the same descriptions. If a `CLAUDE.md` exists, ask whoever maintains it to add an `@AGENTS.md` import line instead of a second copy of the instructions.
- **Other hosts**: other skill layouts are outside what this system manages. Never copy a procedure body to reach another host.

If no instruction file that the agents read may be changed, report
`manual_activation_required`. The files can still be used on request. Do not
claim that future agents will find or maintain them.

## 4. Draft the Compact Context

Fill or refresh only the sections of `.context/project.md` that apply:

- purpose, user, useful outcome, and what the work builds on from its field;
- current materials and entry points, how a result is checked, and operating conditions that affect the science;
- current focus and next meaningful step;
- protected inputs the work takes as given;
- what later work depends on, kept short: by default nothing is settled, and only the exceptions are named;
- the main way the current result could be wrong;
- the smallest useful check and its expected signal;
- current findings: the answer to each open question, its uncertainty, its main limit, and what it rests on;
- unresolved questions that must persist;
- sharing or reuse intent, when it is already relevant.

Remove prompts once they are answered. Write explicit unknowns; do not fill a
section with guesses. Link to existing sources instead of copying them. Leave
environment, dependency, and command detail to `AGENTS.md` and `README.md`.

Write it as current state, rewritten in place, short enough for one screen.
Later sessions imitate it. Lead with what is known, and state each limit once.
Keep out run history, permissions, and lists of what did not change.

Start every context document with short `Purpose`, `Read when`, and
`Update when` lines. The index shows the first two, so a reader can choose
without opening every document. The third tells the next editor when the
document needs to change.

## 5. Ask Only What the Project Cannot Show

Ask a small batch of questions, and only about facts or decisions the project
cannot establish. Start with questions that block the next step:

- scientific meaning or the intended outcome;
- permission to change something;
- expected check behavior;
- safety, access, or scope;
- a real conflict between sources.

Draft a proposed check from project evidence when possible, and let the user
correct its meaning or expected signal. Do not ask the user to restate paths or
commands you can find.

## 6. Decide Whether Another Document Is Warranted

By default, a fact stays in the compact context. Suggest its own context
document only when the information:

1. must stay useful across sessions;
2. changes for its own reasons; and
3. makes the compact context hard to scan.

If an issue tracker, README, data dictionary, architecture document, test plan,
or public specification already holds the fact, use it.

A record that gains an entry each time a run finishes is a log, not context,
even when it meets all three conditions. Leave run records beside the outputs,
written by the code that produced them, and leave history to Git. A context
document's `Update when` line names a change in what it says is true, such as an
answer, a method, or a decision. It does not name an event such as a run
finishing. Logs also take these shapes:

- a section per study;
- forwarding stubs and dated snapshots;
- narration of when and how a number was measured.

A plan is finite: a goal, deliverables with stopping conditions, and what is
outside them. Delete it when the deliverables land.

Split by why a passage changes, not by how long a document is:

- A passage that changes with the project's state stays in context. Examples are a judgment made, a decision taken, a priority moved, or a question answered.
- A passage that changes only when an outside source, firmware, or tool code changes is reference or tool documentation. Put it beside what it describes, or under `docs/`.
- A passage that says how to run a procedure, or how a number was obtained, belongs beside the procedure or in a record.

Context keeps the finding and a link. Copy a measured number or a decision into
context only as a link to where it lives. Rules a contributor must follow before
acting stay in context or the instruction file, even when they are stable.

Write a procedure, protocol, or test method as numbered steps, one action per
step, beside what it describes.

If a term needs a fixed meaning, or readers keep misreading a word, keep the
project's terms in one glossary. Each entry gives the term, its meaning, and
words to avoid. Use an existing glossary if the project has one.

Every Markdown file under `.context/` appears in the index. Add a file there
only when it is current context. Anything else belongs elsewhere in the
repository, or only in Git history.

## 7. Draft, Review, and Integrate

When another context document is justified:

1. Explain in one short paragraph the recurring detail and its proposed home.
2. Draft supported content.
3. Add a line reading `DRAFT CONTEXT - REVIEW REQUIRED` only if the document holds an interpretation you drafted that nobody has confirmed. Content moved from confirmed sources, or a document the user asked for, needs no marker.
4. Write unknowns explicitly; do not invent them.
5. Ask the user to confirm only consequential scientific meaning, permission to change, safety, claims, licensing, ethics, or governance.
6. Remove the marker once those are confirmed.
7. Replace the moved detail in `.context/project.md` with a short link.
8. Run `spctx sync-index .` so the index lists the document.

You may also create the clearest project-specific document directly. The index
lists it by its own opening lines.

Do not repeat a suggestion the user declined unless the detail changes.

## 8. Maintain and Retire Context

Maintenance follows events; it is not a periodic ritual. At the end of work,
update only the facts that changed:

- what runs, the current focus, or the next step;
- protected inputs, scientific risk, or checks;
- current findings or staleness, and unresolved questions;
- the index, when a document was added, renamed, or removed. Remove answered prompts and finished temporary work; do not keep a work
log.

If a document has already become a log, rewrite it as current state. Do not
trim entries: trimming leaves the style for the next session to copy. Keep the
current answers, their limits, and what is still open, and let Git hold the
rest. If an instruction or an `Update when` line asks for an entry per run,
change that rule too, or the log grows back.

The work may have made later work depend on something new, such as a choice, a
parameter, a calibration, or an exclusion. If so, propose adding it to the list
of what later work depends on. The user decides. If nothing changed, do not ask. The list
is empty by default, and nothing else notices when it should stop being empty.

When an input, method, setting, dependency, environment, or public behavior
changes under something on that list, use `spctx-scientific-change`. Identify
the affected evidence and outputs, and rerun them or mark them stale.
Exploratory results need neither. Age alone is no reason to discard discrepant,
negative, or protected evidence, or evidence that supports a reported claim.

When `spctx check` reports passages repeated among the project's own documents,
prune; do not merely clear the list. It matches words only and misses the same
fact reworded. Keep each fact in the document whose update trigger matches it,
usually the most specific one, and link from the other. Repetition is fine when
the two statements serve different readers or moments. An example is a one-line
rule in the instruction file and its reasons in context. Never resolve it by
rewording one copy.

To retire a context document:

1. Find any rule, decision, evidence, uncertainty, or route in it that still matters.
2. Move each still-current item to the context or public document where it belongs, without duplicating it.
3. Run `spctx check . --inventory`. It lists every file in the repository that names the document, including code, notebooks, scripts, and configuration. Fix or report each one. Repoint links and anchors that lead to it.
4. Remove the document from the working tree. Leave superseded plans and narrative to Git, unless project governance requires a separate record.
5. Run `spctx sync-index .` so the index drops it, then `spctx check .`.

## 9. Upgrade to a New Package Version

Use this mode when a newly installed `spctx` may have changed the packaged text.
Upgrade on the branch that others merge from, so every branch receives the same
text.

If you are also asked to install the new version, do that first. Use the upgrade
command in the instruction file's `Context tools` line, then confirm with
`spctx --version`. If no command is recorded, find the source the current version
came from, or ask. Never install this package by name from a public package
index: it is not published there, and whoever registers that name would be
installed instead.

1. If this skill's own body differs from the packaged one, run `spctx upgrade .` first. Then follow the rest of this section from the restored copy. The steps in an older copy belong to the version it came from.
2. Run `spctx upgrade . --dry-run` and read the plan. It replaces only text it recognizes as an earlier packaged version. That covers the routing block, the practice core, skill bodies, and the packaged part of each description. It keeps the project's trigger phrasings, updates generated Claude pointers, and adds missing starter files. Then run `spctx upgrade .`.
3. For each region it skipped as edited, read its diff. Move any wording the project wants to keep to the project's own section, the instruction file, or `.context/`. Then rerun with `--replace-edited`, or leave the region and say why.
4. Compare the rest of the instruction file with the packaged one, which `spctx init . --dry-run` prints. Offer packaged lines that this project's file lacks, one section at a time, in the packaged wording. The user may refuse any. Skip what the project has replaced with its own rule.
5. Compare the rest of the practice file with the packaged one, which `spctx init . --dry-run` prints when they differ. Offer changed lines as in step 4. Leave the project's own section and answered prompts alone.
6. If `.context/project.md` still uses the field title `What later work relies on`, offer to rename it to `What later work depends on`. `spctx check` reads both.
7. Resolve what `spctx check .` reports about the index. Run `spctx sync-index .` if the list is out of date. If it reports project text in a file the package generates or does not use, move what is still needed into context. Then delete that file.
8. Read the whole instruction file, not only the sections you edited. Remove any rule it states twice, once there and once in a skill or context document. Wording an earlier version left behind is not project policy. A project may have written its own section that restates the routing block, such as an exploratory default or rules on when to ask. Keep the lines specific to this project, and delete the restatement. A restatement for a different reader or moment is not a duplicate.
9. List what earlier versions of this system left in the project's own text and code, with counts and places:
   - role titles used for people instead of names or "the user";
   - approval, sign-off, and gate wording;
   - review markers on documents the user asked for;
   - precedence lists that rank the safeguards by number;
   - code that hashes its own source, stops when its source or inputs change, or writes freshness or review signatures for exploratory outputs.

   Propose changes and let the user choose. Change context text when asked, and code only on an explicit request. For a word used hundreds of times, propose adding it to the project's words to avoid, and rewrite it where documents are next edited.
10. Re-run `spctx check .`. Report each of these on its own line:
    - what `spctx upgrade` replaced and skipped;
    - the lines you offered, and their outcome;
    - the duplicated rules you removed or kept;
    - whether each skill description carries this project's phrasings;
    - what step 9 found, and anything the project must decide.

A clean `spctx check` does not show that the new guidance suits this project.
Say what you applied and what you skipped.

## 10. Make the Practice Contract This Project's

The marked core in `.context/scientific-practice.md` ships to every project and
knows nothing about this field. The section below it belongs to the project.
`spctx check` reports whether anything has been written there.

Do not invent a field's conventions. Draft them from something real, in this
order of preference:

1. a standard, protocol, or reporting guideline the project already names;
2. the lab's own prior papers, methods sections, or protocols, when the user points to them;
3. what the code, configuration, and curated decisions visibly do.

Say which of these each proposed line came from. Then ask the user only what
the project cannot show:

- which standards the work is held to;
- what review it owes before it is published;
- what a reviewer in this field would want to see before believing a result.

Keep it short. Four lines that a reviewer would recognize are worth more than a
page of general good practice. Do not restate what the core covers. Deciding
that the shared core is enough is a complete answer: write that in one line
instead of leaving the shipped prompts.

A project that adopted an earlier version has no such section. Add it below the
end marker.

Do not move project conventions inside the markers. Text there is packaged, and
an upgrade replaces it.

## 11. Tune the Skill Triggers to This Project

The packaged descriptions are generic. The strongest routing signal is the
vocabulary this project's people actually use. Once the domain is clear, add it.

Keep the packaged description exactly as it is. After the separator, append
three to six real example requests from this project:

    description: <packaged text, unchanged> Also use for requests such as: "exclude these samples", "change the smoothing window", "refit the decay model".

Use the words a contributor here would type. Keep the whole description under
1024 characters, and keep the `name` matching its directory. Then run
`spctx upgrade .`: it copies each tuned description into its generated Claude
pointer.

Do not rewrite or shorten the packaged part. It carries the general trigger
categories and later packaged improvements.

Everything from the separator onward is the project's and survives an upgrade.
`spctx check` reports how many descriptions carry project phrasings. Keep project
facts out of the body, which is packaged too. Propose the edit, and let the user
confirm the vocabulary.

## 12. Review Context

Use this mode when the context has grown past what a routine refresh fixes, or
when the user asks whether it still serves the work. Inspect and propose; do not
restructure yet.

1. Run `spctx check . --inventory`. It gives each context document's words, sections, `Update when` line, dated lines, links, and the files that name it.
2. Note which kinds of passage each document holds: current state and decisions, findings, stable reference, tool manuals, plans and protocols, and measurement provenance. Note documents whose passages change for different reasons.
3. Look for contradictions first: two statements of one rule or number that disagree, including reworded copies, which `spctx check` cannot see.
4. Then look for:
   - stale statements and numbers copied from where they live;
   - session dates used to identify evidence;
   - plans kept in several places, and broken links;
   - what step 9 of the upgrade lists.
5. Propose fixes in order of cost. Start with contradictions and stale lines. Then give each repeated fact one home. Last, propose any split or move by the rule in section 6.
6. Write the result as a short dated report outside `.context/`, or in your reply, leading with the contradictions.

Apply routine fixes when the user asks. Restructuring waits for the user's
go-ahead. Delete the report once its proposals are applied or declined.

## 13. Report

Report the activation state, the context established or refreshed, open
questions that matter, and context documents created, retired, or deliberately
not created. End with the next meaningful step. Do not claim scientific or
release readiness from documentation structure alone.
