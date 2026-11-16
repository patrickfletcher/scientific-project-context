---
name: spctx-scientific-change
description: Apply the project's scientific safeguards to a change that touches what later work depends on, or to a result about to be published. Use when changing an analysis, filtering or exclusion rule, notebook, model or simulation, statistical or numerical method, acquisition or instrument workflow, calibration, scientific API, figure or table that the project's list of what later work depends on names, or when preparing results for a paper, poster, release, or handoff — for example "exclude these trials from the main analysis", "change the calibration we depend on", "refit the model for the paper", "redo the figure for the paper". Exploratory analysis needs no skill; the project's instructions cover it. Do not use for formatting, packaging, renaming, or routine maintenance.
---

# Scientific Change

Purpose: plan, perform, and check work that later work depends on, without a separate validation bureaucracy.
Use when: creating or changing an analysis, data transformation or exclusion rule, notebook, model or simulation, numerical or statistical method, acquisition or instrument workflow, calibration, scientific API, figure or table, or any output that supports a reported claim.

Before acting, say in one line that you are using `spctx-scientific-change`.
If the change touches nothing later work depends on and will not be published,
say so and stop. The work is exploratory, and the project's instructions cover it.

## 1. State the Question and the Level

Read `.context/scientific-practice.md` and `.context/project.md`. Read only the
other context documents that `.context/index.md` shows are relevant. Read
`AGENTS.md` for project rules; it does not repeat the scientific contract.

State only what is relevant:

- the question, decision, behavior, result, or claim being changed;
- which intended-use level in the practice contract applies, and what already depends on the result;
- the main way it could be wrong even if the workflow completes or the result looks plausible;
- its intended domain and limits;
- the protected inputs, curated decisions, generated outputs, and public behavior it affects.

Do not decide from a filename who may change something or what it means.

Say the level plainly, because the rest of this procedure depends on it. The
project's list of what later work depends on is the default test:

- If the change touches nothing on that list, it is exploratory, however large it is.
- If something already depends on the result but is not listed, it is not exploratory. Propose adding it to the list.

A parameter, a plot, a helper, or a whole method comparison stays exploratory
until someone decides that later work will depend on it.

Before you start a side investigation, name the decision it could change and
when it will stop. If it could change none, list it as a lead in your reply
instead of running it. When it ends, say what it settled: adopt it as the working
default, keep it as an option, or set it aside. A comparison of candidate methods
is a side investigation too.

If a computation does not fit the time or memory available, make it smaller:
use fewer samples, features, or permutations, or ask. Do not build variants,
guards, or retry chains to make it fit. Engineering that answers no scientific
question is the most expensive kind of exploratory work.

When the work is exploratory, do this and then stop here:

1. Say in your reply what it showed, what was done, and that it is provisional.
2. Adopt a working default if one is useful, and say that it is provisional.
3. Change project context only if the current answer to one of its questions changed. Rewrite that answer; do not add an entry for the run.

Continue past this step only in one of these cases:

- the change touches something on the list;
- a result is about to be published;
- the user decides that later work will depend on the result.

That decision belongs to the user. If the work looks like something later work
will depend on, propose it, and add the result to the list in the same turn.

## 2. Propose the Smallest Useful Check

Skip this step while the work is exploratory.

Ask in plain language: "What is the smallest check or observation that could
show a consequential error? What should happen, within what tolerance or
uncertainty, and why?"

- Draft an answer from project evidence when possible.
- Set the expected signal before you inspect the changed result, when practical.
- Let the user correct scientific judgment. Never invent an expected result.
- If the expected value comes from published work, check its source with `spctx-literature`.

Prefer a check of one of these kinds. They are examples, not requirements.

- a positive or negative control, or a reference material or sample;
- a clean-kernel notebook rerun or a held-out case;
- a sensitivity check or a reference acquisition;
- an analytical or manufactured solution, or a convergence or limiting-case check;
- a backend comparison or a targeted failure case.

When practical, show that the check fails for a known bad or earlier behavior.

Choose one check, not a suite. Do not let one check grow into a benchmark
program unless the depended-on result needs one.

## 3. Plan Evidence and Staleness

Scale the record to the level:

- **Depended on inside this project**: one sentence and a date. Say what was observed, what was expected, and when.
- **Published**: the full identity below, and a public version of the work that reproduces the result for any reader who runs it.

When something produced at a lower level starts to be depended on, rebuild its
evidence from what exists. Use the code and configuration in force at the time,
the outputs, and the project's notes. Say what you could rebuild and what you could
not. A gap is a finding to report, not a blank to fill. You cannot supply an
expected signal that nobody held at the time.

For an executed check, keep a compact evidence record:

- the observed result beside the expected signal;
- the script, notebook, procedure, acquisition record, or command, and how to repeat it;
- material input origin, transformation or exclusion path, model, calibration, method, settings, and randomness;
- code revision and environment, backend, or hardware when relevant;
- run date, observed uncertainty or variation, review state, and limits.

Let the code write machine detail, such as the code revision, environment, and
settings, beside its output. Link to it from context; do not copy it.

Name what the evidence establishes: implementation verification, scientific
validation for an intended use, computational reproducibility, independent
replicability, or generalizability. Do not use one label to imply another.

Name the earlier evidence and downstream outputs that must be rerun. If you do
not rerun them, mark them stale, and stop describing the behavior as validated.

## 4. Choose the Smallest Home

Keep one behavior, check, and evidence record in `.context/project.md` while it
stays readable. Use another context document only under the conditions in
`spctx-project-context`, and run `spctx sync-index .` after you add one. If an
existing test plan, data dictionary, benchmark record, method note, or public
specification already holds the fact, use it.

## 5. Perform the Work and Check It

Set the check and expected signal before or alongside the broader work, when
practical. Perform the analysis, acquisition, calculation, or test. Record the
actual result, uncertainty, and limits. A check that exists is not validation.

If a depended-on result fails to reproduce:

1. Keep the discrepant result.
2. Find what changed.
3. Mark the affected evidence or outputs stale.

That is a judgment for the moment, not a guard to build into code. Make a known
correction, record a consequential choice for review, or ask for the missing
scientific judgment.

## 6. Report the Boundary

Lead with what the work showed about the scientific question. Then report:

- the level you worked at, and anything you deliberately did less of because nothing depends on the result yet;
- what was checked, and what remains provisional or stale;
- which outputs are affected;
- what scientific judgment still needs review.

Report the level you worked at in one line. Put logistics such as run time,
memory, and retries last, or leave them to the run record. Do not generalize
beyond the evidence.
