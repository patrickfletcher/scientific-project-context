# Scientific Practice Contract

Purpose: define the durable scientific safeguards that human and agent contributors apply to this project's work.
Read when: work could affect scientific meaning, protected inputs, methods, evidence, artifacts, validation, or claims.
Update when: the project deliberately adopts a revised scientific-practice contract; keep project-specific facts elsewhere.

This is a working agreement for researchers and their assistants, not a universal checklist. Work is scientifically material when it could change a result, interpretation, decision, safety boundary, reusable scientific behavior, or public claim. Apply only the safeguards relevant to that work.

Read this once when the project starts, and make it yours. The marked core below is a shared starting point, not a rule imposed on the project: add your field's conventions, standards, protocols, or review requirements in the sections outside the markers, and say plainly where this project deliberately does something different. A contract nobody has read or agreed with will not improve the work.

For material work, preserve a traceable route:

```text
question, decision, or intended use
-> input sources and provenance
-> method, transformations, and settings
-> expected check
-> observed evidence and uncertainty
-> supported conclusion and limits
```

These parts may stay compact and may live in existing project sources. People and agents may inspect evidence, draft context, perform checks, and record results. An identified scientist or relevant domain authority confirms consequential scientific meaning and claim scope. The project, data, or community authority confirms permission to change, use, or share material. One role does not silently imply the other.

<!-- BEGIN SPCTX SCIENTIFIC PRACTICE CORE v1 -->
## Authority and Meaning

- An identified scientist or relevant domain authority owns scientific meaning, acceptable scientific behavior, and claim scope. A project, data, or community owner controls operational changes and permitted use or sharing. Project ownership or a task request alone does not establish scientific expertise or authority over an accepted scientific reference.
- Inspect available evidence before asking, but do not invent a role, permission, or scientific answer when the project cannot establish it.
- Distinguish observations, derived results, proposed interpretations, and unknowns. A plausible agent-generated explanation is not evidence.
- If another instruction materially conflicts with these safeguards, stop and ask the user or domain authority to resolve the conflict. File presence alone does not establish scientific authority.

## What Will Depend on the Result

- Before deciding how much evidence a piece of work owes, say what will depend on its result. Each level below inherits the one before it.
  - **Exploratory**: nothing depends on it yet. Say what was done and that it is provisional. No check, evidence record, or staleness obligation is owed. If you expect to promote it later, naming what you chose and what you set aside costs one line now and is hard to recover afterward.
  - **Supporting a decision or claim**: later work in this project assumes it. Record the choice, the alternative set aside, what would change it, and one control, comparison, or sensitivity.
  - **Public or published**: people outside the project rely on it. The full route above is owed, including reproducibility, uncertainty, limits, and review.
- Evidence is owed when a result is promoted, not when it is produced. Work freely at the exploratory level and pay at the boundary where something starts to depend on the result. Record that promotion as a decision; no tool assigns it.
- Name the level when it changes what you are about to do, and let the scientist correct it. Never raise a level silently; ask.
- A level relaxes only how much support a result must carry before work continues. At every level, protected material stays protected, discrepant and negative results are kept, authority stays with its owner, and nothing is described as better established than it is.

## Protected and Curated Material

- Identify material that must not change silently: raw or accepted data, reference materials, participant- or community-controlled data, user-controlled model definitions, calibrations, schemas, curated decisions, and other project-designated inputs.
- Record identifiers, provenance, and access rules; do not copy protected, sensitive, or controlled material into context merely to make it self-contained. Technical access does not establish permission to change, use, or share it.
- Do not modify protected material unless change authority is clear. Record or surface uncertainty before acting.
- Treat generated outputs as derived artifacts, not authoritative inputs, unless the project explicitly reviews and promotes them.

## Question, Method, Risk, and Limits

- For scientifically material work, state the question, decision, behavior, or claim at issue; which level above applies; the main way it could be wrong even if the workflow completes or the result looks plausible; and its intended domain and limits.
- Make material input lineage, transformations, exclusions, units, conventions, parameters, calibrations, initial or boundary conditions, and randomization explicit as relevant. Record consequential choices made after inspecting results.
- When conclusions depend on sampling, randomness, fitting, filtering, subjective choices, or model form, report relevant uncertainty or variation and whether reasonable alternatives change the conclusion.
- Prefer explicit named parameters and recorded settings over hidden scientific assumptions or unexplained constants.
- Do not generalize a result beyond the inputs, methods, environments, populations, backends, or conditions actually supported by evidence.

## Discriminating Checks

- Above the exploratory level, name the smallest check or observation that could expose a consequential error. Include the expected result, tolerance, uncertainty, property, comparison, control, or failure signal.
- Derive the expected signal from accepted evidence or domain judgment before inspecting the changed result when practical. Do not invent an expected result merely to complete a check.
- Prefer a check with some independence from the logic or data path being changed. Controls, reference materials, invariants, held-out cases, alternative implementations, limiting cases, and clean-session reruns are examples, not requirements.
- State what the evidence establishes: implementation verification, scientific validation for an intended use, computational reproducibility with the same inputs and conditions, independent replicability with new data or evidence, or generalizability beyond the tested setting. Do not treat one as proof of another; test existence or successful execution alone is not validation.

## Evidence and Staleness

- For a result something already depends on, keep enough identity to interpret or repeat material evidence: input origin and version; transformation or exclusion path; notebook, script, protocol, acquisition, model, or method identity; material settings; software, instrument, environment, backend, or hardware state; command or procedure; observed result and uncertainty; expected signal; date; review state; and important limits as relevant.
- When a relevant input, method, setting, calibration, dependency, backend, environment, or public behavior changes, rerun affected evidence or mark it and dependent outputs stale.
- Preserve discrepant, null, and negative results and material deviations from the planned approach. Do not silently replace inconvenient evidence or continue to describe stale evidence as current validation.

## Outputs and Claims

- Treat agent-generated interpretations and claims, and agent-drafted decisions about access, safety, licensing, ethics, or governance, as review-required proposals until the relevant facts and judgments are confirmed.
- Report what was checked, what remains provisional or stale, and what scientific judgment still requires review.
- Treat clean structure and passing mechanical checks as readiness for review, not as scientific, ethical, legal, release, or publication approval.
<!-- END SPCTX SCIENTIFIC PRACTICE CORE v1 -->

## This Project's Practice

This repository builds a tool for research software rather than measuring
anything, so the core applies with one translation: a "result" here is product
behavior, and the people who depend on it are adopting projects.

- **Conventions this work follows**: the cross-domain sources listed in `.context/design-rationale.md`, which justify the questions the product asks rather than any method of its own.
- **Review this work owes**: none institutional. The MIT license is confirmed. Trial repositories and the people behind them stay unidentified; `.context/evaluation.md` says how.
- **What counts as adequate evidence**: `.context/evaluation.md` owns the levels. In short, a passing suite settles mechanics for the paths it exercises and settles nothing about whether a scientist is better off.
- **Where this project differs from the core**: nowhere deliberately. It is held to the contract it ships.

## Keeping Application Proportional

Start with the compact fields in `.context/project.md`. Reuse an existing test plan, method note, data dictionary, benchmark record, issue tracker, or public specification when it already owns a fact. Add a focused context source only when the compact fields stop serving the work; the project-context skill named below owns that test.

For a scientifically material change, use `.agents/skills/spctx-scientific-change/SKILL.md` to turn this contract into an executable check and an evidence boundary. For context maintenance or growth, use `.agents/skills/spctx-project-context/SKILL.md`.
