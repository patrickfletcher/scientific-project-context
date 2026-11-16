---
name: spctx-scientific-change
description: Apply the project's scientific safeguards to work that could change a result, an interpretation, or a reported claim. Use when changing an analysis, filtering or exclusion rule, notebook, model or simulation, statistical or numerical method, acquisition or instrument workflow, calibration, scientific API, figure or table, or any output that supports a claim — for example "exclude these trials", "change the filter cutoff", "update the calibration", "refit the model", "redo the figure for the paper". Do not use for formatting, packaging, renaming, or routine maintenance with no scientific effect.
---

# Scientific Change

Purpose: plan, perform, and check scientifically material work without forcing a separate validation bureaucracy onto simple projects.
Use when: creating or changing an analysis, data transformation or exclusion rule, notebook, model or simulation, numerical or statistical method, acquisition or instrument workflow, calibration, scientific API, figure or table, or any output that supports a reported claim.

Before acting, say that you are using `spctx-scientific-change` and name the
change at issue. If the work turns out not to be scientifically material, say so
and stop applying this procedure rather than performing it as ceremony.

## 1. State the Scientific Question and Risk

Read `.context/scientific-practice.md`, `.context/project.md`, and only the other context documents the index in `.context/index.md` shows are relevant. Read `AGENTS.md` for project rules and routing, but do not expect it to duplicate the scientific contract.

State only what is relevant:

- the research question, decision, behavior, result, or claim being changed,
- which intended-use level in the practice contract applies, and what already depends on the result,
- the main way it could be scientifically wrong even if the workflow completes or the result looks plausible,
- the intended domain and limits, and
- affected protected inputs, curated decisions, generated outputs, and public behavior.

Do not infer from a filename who may change something or who decides what it means.

Say the level plainly, because the rest of this procedure is gated on it. The
project's compact context says what later work relies on, and that short list is
the test: a change that touches nothing on it is exploratory, whatever it is and
however much work it took. A parameter, a plot, a helper, or a whole method
comparison is exploratory until someone decides to rely on it.

Before starting a sub-investigation, name the scientific question it answers.
When a computation does not fit the time or memory available, make it smaller,
with fewer samples, features, or permutations, or ask; do not build variants,
guards, or retry chains to make it fit. Engineering that answers no scientific
question is the most expensive kind of exploratory work, and real use has seen
it take over a project one approved step at a time.

When the work is exploratory, say in your reply what it showed, what was done,
and that it is provisional, then stop here; the remaining steps belong to
results something already depends on. Running them anyway turns a quick look
into a validation project, which is the way this procedure has been observed to
cost a project more than it returned. Change project context only when the
current answer to one of its questions changes, and then rewrite that answer
rather than adding an entry for the run.

Continue past this step only when the change touches something on that list, or
when the user decides that later work will rely on the result. That decision is
the user's to make; propose it when the work looks load-bearing, and add the
result to the list in the same turn.

## 2. Propose the Smallest Useful Check

Skip this step while the work is exploratory. It begins when later work starts
to rely on the result.

Ask in plain language: "What is the smallest check or observation that could reveal a consequential error? What should happen, within what tolerance or uncertainty, and why?"

Draft an answer from project evidence when possible. Establish the expected signal before inspecting the changed result when practical. Let the responsible scientist correct scientific judgment; never invent an expected result.

Prefer a positive or negative control, reference material or sample, clean-kernel notebook rerun, held-out case, sensitivity check, reference acquisition, analytical or manufactured solution, numerical-convergence or limiting-case check, backend comparison, or targeted failure case. These are examples, not requirements. When practical, demonstrate that the check fails for a known bad or pre-change behavior.

Choose one check, not a suite. Comparing candidate methods against each other is
a separate piece of work with its own level, and it is rarely warranted while
nothing depends on the answer yet. Do not let one check grow into a benchmark
program unless the result now being relied on actually needs one.

## 3. Plan Evidence and Staleness

Scale the record to the level. A result supporting a decision or claim inside
this project needs a sentence and a date: what was observed, what was expected,
and when. A public or published result needs the full identity below.

When something produced at a lower level starts to be relied on,
rebuild its evidence from what already exists: the code and configuration
in force at the time, the outputs, and the project's own notes. Record what
you could rebuild and what you could not.
A gap is a finding to report, not a blank to fill, and an expected signal
nobody held at the time cannot be supplied now.

For an executed check, retain a compact evidence record:

- observed result beside the expected signal,
- script, notebook, procedure, acquisition record, or command and enough instruction to repeat it,
- material input origin, transformation or exclusion path, model, calibration, method, settings, and randomness identity,
- code revision and environment/backend/hardware identity when relevant,
- run date, observed uncertainty or variation, review state, and documented limits.

Machine identity such as code revision, environment, and settings is best
written by the code beside its output; link to it rather than copying it into
context.

Name what the evidence establishes: implementation verification, scientific validation for an intended use, computational reproducibility with the same inputs and conditions, independent replicability with new data or evidence, or generalizability beyond the tested setting. Do not use one label to imply another.

Identify which prior evidence and downstream outputs must be rerun. If they are not rerun, mark them stale and do not continue to describe the behavior as validated.

## 4. Choose the Smallest Home

Keep one behavior, check, and evidence record in `.context/project.md` while it remains readable. Use another source only under the three conditions in `spctx-project-context`: the detail persists across sessions, updates independently, and no longer fits clearly. Run `spctx sync-index .` after adding one.

Several validation states may justify a validation table; non-obvious artifact provenance and rerun rules may justify an artifact specification; recurring scientific assumptions may justify a compact scientific guide. These are examples, not required filenames. Reuse an existing test plan, data dictionary, benchmark record, method note, or public specification when it already holds the fact.

## 5. Perform the Work and Check It

Establish the check and expected signal before or alongside the broader work when practical. Perform the affected analysis, acquisition, calculation, or test and record the actual result, uncertainty, and limits. Check existence alone is not validation.

When a result something depends on fails to reproduce, keep the discrepant result, find what changed, and mark the affected evidence or outputs stale. That is a judgment for the moment it happens, not a guard to build into code. Perform a known correction, record a consequential choice for review, or ask for missing scientific judgment as appropriate.

## 6. Report the Boundary

Lead with what the work showed about the scientific question. Report the level you worked at, what was checked, what remains provisional or stale, which outputs are affected, and what scientific judgment still needs review. Put logistics such as run time, memory, and retries last, or leave them to the run record. Say so when you deliberately did less because nothing depends on the result yet, so the reader can disagree. Do not generalize beyond the documented evidence domain.
