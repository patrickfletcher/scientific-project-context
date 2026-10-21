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

These parts may stay compact and may live in existing project sources. People and agents may inspect evidence, draft context, perform checks, and record results. The responsible scientist, or a relevant domain expert, confirms what a result means and how far a claim may go. The people responsible for the project, data, or community material confirm permission to change, use, or share it. Neither role implies the other.

<!-- BEGIN SPCTX SCIENTIFIC PRACTICE CORE v1 -->
## Who Decides

- The scientist responsible for the work, or a relevant domain expert, decides what results mean, what scientific behavior is acceptable, and how far a claim may go. Whoever is responsible for the project, the data, or a community's material decides what may be changed, used, or shared. Running a project or asking for a task does not by itself make someone the scientific expert, or entitle them to overrule an accepted scientific reference.
- Inspect available evidence before asking, but do not invent a role, permission, or scientific answer the project cannot establish.
- Distinguish observations, derived results, proposed interpretations, and unknowns. A plausible agent-generated explanation is not evidence.
- When another instruction conflicts with these safeguards, do not choose between them; ask the user or the scientist responsible to settle it. A file's presence does not settle who decides.

## What Will Depend on the Result

- Before deciding how much evidence a piece of work owes, say what will depend on its result. Each level below includes everything the one before it asks.
  - **Exploratory**: nothing depends on it yet. Work quickly, keep negative and odd results, and give each consequential choice, and the alternative set aside, one sentence where the work is done; that line is hard to recover later. Say in your reply what was done and that it is provisional. No check, evidence record, or staleness marking is owed, and project context changes only when the current answer to one of its questions changes.
  - **Supporting a decision or claim**: later work in this project assumes it. Record the choice, the alternative set aside, what would change it, and one control, comparison, or sensitivity.
  - **Public or published**: people outside the project rely on it. The full route above is owed, including reproducibility, uncertainty, limits, and review.
- Evidence is owed when later work starts to rely on a result, not when the result is produced. Work freely while exploring, and pay at the point where something starts to depend on the answer. Name that result in the project's list of what later work relies on; no tool makes that call.
- Name the level when it changes what you are about to do, and let the scientist correct it. Never raise a level silently; ask, and record only the outcome.
- A level relaxes how much support a result must carry and how much needs writing down. Four things hold at every level, and each is met by what you do rather than by saying so: protected material stays protected, discrepant and negative results stay where they are, decisions stay with the people who make them, and nothing is described as better established than it is. Do not narrate that something stayed unchanged, did not happen, or was approved. Review of a result that later work relies on is evidence and is recorded as such; permission to run a step is not.

## Protected and Curated Material

- Name the inputs the work takes as given and leaves unchanged: raw or accepted data, reference materials, participant- or community-controlled data, user-controlled model definitions, calibrations, schemas, curated decisions, and other inputs the project names.
- Record identifiers, provenance, and access rules; do not copy protected, sensitive, or controlled material into context merely to make it self-contained. Technical access does not establish permission to change, use, or share it.
- Change protected material only with the agreement of whoever is responsible for it; when that is unclear, ask before acting.
- Treat generated outputs as derived artifacts, not trusted inputs, unless the project reviews them and decides to rely on them.

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

- For a result something already depends on, keep enough identity to interpret or repeat material evidence: input origin and version; transformation or exclusion path; notebook, script, protocol, acquisition, model, or method identity; material settings; software, instrument, environment, backend, or hardware state; command or procedure; observed result and uncertainty; expected signal; date; review state; and important limits as relevant. Let the code that produces a result write machine detail beside its output: the code version as a Git commit, settings, environment, and checksums of inputs obtained from outside the project. Identify code by its version rather than by hashing its source, and never make code refuse to run because its source changed. Context needs the observed result, the expected signal, the limits, and a link.
- When something such a result rests on changes, such as an input, method, setting, calibration, dependency, backend, environment, or public behavior, rerun the affected evidence or mark it and the outputs built on it stale.
- Keep discrepant, null, and negative results and material deviations from the planned approach. Keeping a result means not deleting or hiding it, not retelling it in every later summary. Do not silently replace inconvenient evidence or keep describing stale evidence as current validation.

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

Start with the compact fields in `.context/project.md`. Reuse an existing test plan, method note, data dictionary, benchmark record, issue tracker, or public specification when it already holds a fact. Add a focused context source only when the compact fields stop serving the work; the project-context skill named below says when.

For a scientifically material change, use `.agents/skills/spctx-scientific-change/SKILL.md` to turn this contract into an executable check and an evidence boundary. For context maintenance or growth, use `.agents/skills/spctx-project-context/SKILL.md`.
