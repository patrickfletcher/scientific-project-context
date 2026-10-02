# Project Context Index

Purpose: route people and agents from the compact project context to the smallest additional source needed for a task.
Read when: `.context/project.md` does not contain enough context for the current work.
Update when: focused current documents or human-authored routes change; synchronize only the generated inventory mechanically.

Read `AGENTS.md` and `.context/project.md` first. Stop as soon as the relevant code and source of truth are clear. This file owns navigation, not project facts or status.

## Generated Context Inventory

<!-- BEGIN GENERATED CONTEXT INVENTORY -->
- `.context/automation.md`
  - Purpose: define the installable product mechanics and the judgments they must not automate.
  - Read when: changing a command, packaged resource, health check, report contract, or distribution boundary.
  - Update when: a public tool effect, safety guarantee, report field, or release boundary changes.
- `.context/design-rationale.md`
  - Purpose: preserve the small set of enduring reasons behind the current Scientific Project Context design without reviving superseded template structures.
  - Read when: a current product decision needs deeper justification than `.context/product.md` provides.
  - Update when: evidence changes one of these rationales or a rejected approach becomes viable for a new reason.
- `.context/evaluation.md`
  - Purpose: define the evidence needed to assess the product and record what real use has taught without identifying anyone.
  - Read when: interpreting checks, planning or recording a trial, or making a product effect, usability, compatibility, or release claim.
  - Update when: product behavior changes, the tested platform range changes, or a trial produces an observation that changes a claim or the product.
- `.context/product.md`
  - Purpose: define what Scientific Project Context is, the outcomes it should improve, and the boundaries that keep it small.
  - Read when: changing the starter files, user journey, context rules, or product scope.
  - Update when: observed use changes the product promise, lifecycle, or boundary.
- `.context/roadmap.md`
  - Purpose: explain the order of the next few product moves.
  - Read when: planning beyond the current task.
  - Update when: trial evidence changes the sequence or a real release effort begins.
<!-- END GENERATED CONTEXT INVENTORY -->

## Routing

| Need | Minimum read set | Stop rule |
| --- | --- | --- |
| Orient to this repository | `.context/project.md` | Stop when the target and proportionate check are clear. |
| Change the product promise, starter set, or context behavior | `.context/product.md`, affected product files | Stop before history unless a rationale or evidence claim is disputed. |
| Change scientific safeguards or examples | `.context/scientific-practice.md`, affected skill or starter file; `.context/design-rationale.md` for the sources behind them | Stop when the stable contract, relevant risk, check, evidence, and review boundary agree. |
| Change deterministic tools or package mechanics | `.context/automation.md`, affected code/tests | Stop when the effect is classified, bounded, and tested. |
| Plan, record, or interpret a trial or empirical test | `.context/evaluation.md` | Stop when evidence level, observable outcome, limits, and disposition are explicit, and nothing identifies the trial. |
| Choose current work | `.context/project.md`; `.context/roadmap.md` only when sequencing matters | Stop when the executable slice and exit condition are clear. |
| Prepare public guidance or distribution | `.context/product.md`, `.context/roadmap.md`, root `README.md` | Stop when the real sharing trigger and required reviewed choices are named. |
| Add, move, or retire current context | `AGENTS.md`, this index, and the affected source | Stop when each durable fact has one authoritative home and navigation matches live files. |

Read `.context/design-rationale.md` only when a current decision needs deeper justification. Retired material remains available through Git history and is not current instruction.

This repository uses the system on itself. Its documents beyond the starter files arose from recurring work and are not day-one requirements for other projects.
