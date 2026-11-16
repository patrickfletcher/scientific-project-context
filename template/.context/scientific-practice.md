# Scientific Practice Contract

Purpose: define the durable scientific safeguards that human and agent contributors apply to this project's work.
Read when: work could affect scientific meaning, protected inputs, methods, evidence, artifacts, validation, or claims.
Update when: the project deliberately adopts a revised scientific-practice contract; keep project-specific facts elsewhere.

This is a working agreement for researchers and their assistants. It is not a universal checklist. Most work is exploratory and owes little beyond honest results; what a result owes grows with what depends on it. Apply only the safeguards that fit the work at hand.

Read this once when the project starts, and make it yours. The marked core below is a shared starting point. Add your field's conventions, standards, protocols, and review requirements in the sections outside the markers. Say plainly where this project deliberately does something different. A contract that nobody has read or agreed to will not improve the work.

When later work depends on a result, or when it will be published, keep a traceable route:

```text
question, decision, or intended use
-> input sources and provenance
-> method, transformations, and settings
-> expected check
-> observed evidence and uncertainty
-> supported conclusion and limits
```

These parts may stay compact and may live in existing project sources.

<!-- BEGIN SPCTX SCIENTIFIC PRACTICE CORE v1 -->
## Decisions and Protected Inputs

- The user decides what results mean, how far a claim may go, and what later work depends on. Inspect the evidence before you ask, draft from it, and let the user correct the draft.
- Keep observations, derived results, proposed interpretations, and unknowns apart. A plausible agent-generated explanation is not evidence.
- Name the protected inputs the work takes as given: raw or accepted data, reference material, calibrations, schemas, curated decisions, and anything later work depends on.
- Change a protected input only when the request clearly means to. If a change would touch one as a side effect, or the request is ambiguous, say what would change and ask once.
- Permission to use, change, or share material the project did not produce comes from whoever controls it, including participants and communities. Technical access does not establish permission.
- Record identifiers, provenance, and access terms. Do not copy controlled material into context to make it self-contained.
- Treat generated outputs as derived artifacts until someone decides that later work depends on them.
- If another instruction conflicts with these safeguards about what later work depends on, ask the user. Do not choose between them.

## What Will Depend on the Result

What a result owes depends on what depends on it.

- **Exploratory**, the default: nothing depends on it yet.
  - Work quickly, and keep negative and odd results.
  - Give each consequential choice, and the alternative set aside, one sentence where the work is done.
  - Say in your reply what was done and that it is provisional.
  - No check, evidence record, or staleness marking is owed. Change project context only when the current answer to one of its questions changes.
  - You may adopt a working default while exploring. Say that it is provisional.
- **Depended on**: the project's list of what later work depends on names it. Record in one sentence what it rests on: the choice, the alternative set aside, and what would change it. Add one control, comparison, or sensitivity.
- **Published**: people outside the project will use it, in a paper, poster, release, or handoff. The full route above is owed, with uncertainty, limits, and review. A public version of the work must reproduce the published result for any reader who runs it. This is the one strict reproducibility standard.

Evidence is owed when later work starts to depend on a result, not when the result is produced. Work freely while exploring. When something starts to depend on a result, rebuild what is needed from the commit, settings, and outputs the work left. Propose adding a result to the list when work starts to depend on it; the user decides. A dependency is real whether or not it is listed yet.

Five rules hold at every level. Meet them by what you do, not by saying so:

- Protected inputs stay protected.
- Discrepant and negative results stay where they are.
- Decisions stay with the user.
- Nothing is described as better established than it is.
- No outside source is cited without being identified. Mark a reference you recall but have not looked up as recalled.

Do not write that something stayed unchanged, did not happen, or was approved. Review of a result that later work depends on is evidence, so record it. Permission to run a step is not evidence.

## Question, Method, Risk, and Limits

- For a result that later work depends on, or that will be published, state:
  - the question, decision, behavior, or claim at issue;
  - the main way it could be wrong even if the workflow completes or the result looks plausible;
  - its intended domain and limits.
- Make material input lineage, transformations, exclusions, units, conventions, parameters, calibrations, initial or boundary conditions, and randomization explicit where they matter. Record choices made after inspecting results.
- For such a result, if conclusions depend on sampling, randomness, fitting, filtering, subjective choices, or model form, report the uncertainty or variation. Say whether reasonable alternatives change the conclusion.
- Prefer explicit named parameters and recorded settings to hidden assumptions or unexplained constants.
- Do not generalize a result beyond the inputs, methods, environments, populations, backends, or conditions that the evidence supports.

## Discriminating Checks

- Above the exploratory level, name the smallest check or observation that could expose a consequential error. Include the expected result, tolerance, uncertainty, property, comparison, control, or failure signal.
- Derive the expected signal from accepted evidence or domain judgment before you inspect the changed result, when practical. Do not invent an expected result to complete a check.
- Prefer a check that is independent of the logic or data path being changed. Controls, reference materials, invariants, held-out cases, alternative implementations, limiting cases, and clean-session reruns are examples, not requirements.
- State what the evidence establishes:
  - implementation verification;
  - scientific validation for an intended use;
  - computational reproducibility with the same inputs and conditions;
  - independent replicability with new data or evidence;
  - generalizability beyond the tested setting.

  Do not treat one as proof of another. A test that exists or runs is not validation.

## Evidence and Staleness

- For a result something already depends on, keep enough identity to interpret or repeat the evidence. As relevant, record:
  - input origin and version, and the transformation or exclusion path;
  - the notebook, script, protocol, acquisition, model, or method, and its material settings;
  - software, instrument, environment, backend, or hardware state;
  - the observed result and uncertainty, the expected signal, the date, and important limits.
- Let the code that produces a result write machine detail beside its output: the code version as a Git commit, and the settings. Record where each outside input came from and which version; add a checksum when the source could change under the same name.
- Identify code by its version. Do not hash its source, and never make code refuse to run because its source changed.
- Context needs the observed result, the expected signal, the limits, and a link.
- When something such a result rests on changes, rerun the affected evidence or mark it and the outputs built on it stale. Inputs, methods, settings, calibrations, dependencies, backends, environments, and public behavior are examples.
- Keep discrepant, null, and negative results and material deviations from the planned approach. Keeping a result means not deleting or hiding it, not retelling it in every later summary. Do not silently replace inconvenient evidence, and do not describe stale evidence as current validation.

## Outputs and Claims

- Label an agent-drafted interpretation as provisional in your reply. It needs review before later work depends on it or it is published.
- Agent-drafted decisions about access, safety, licensing, ethics, or governance are proposals until the user confirms them.
- When a result is depended on or published, report what was checked, what remains provisional or stale, and what judgment still needs review.
- Treat clean structure and passing mechanical checks as ready for review. They are not scientific, ethical, legal, release, or publication approval.
<!-- END SPCTX SCIENTIFIC PRACTICE CORE v1 -->

## This Project's Practice

The core above ships to every project and knows nothing about this field. Answer
the lines below from this project, and delete any line that does not apply. None
is required. If the shared core is all this work owes, say so in one line and
delete the rest.

- **Standards, protocols, or reporting conventions this field expects**: [name them, or link the document that already holds them]
- **Review this work owes before it is published**: [ethics, governance, community, safety, or institutional review, if any, and who gives it]
- **What a reviewer here would count as adequate evidence**: [the controls, replication, sample structure, or reporting practice this field looks for]
- **Terms this field uses with a specific meaning**: [a link to the project's glossary, or `none`]
- **Where this project deliberately differs from the core**: [say so plainly, with the reason]

## Keeping Application Proportional

Start with the compact fields in `.context/project.md`. If an existing test plan, method note, data dictionary, benchmark record, issue tracker, or public specification already holds a fact, use it. Add another context document only when the compact fields stop serving the work; the project-context skill below says when.

For a change to what later work depends on, use `.agents/skills/spctx-scientific-change/SKILL.md` to turn this contract into a check and an evidence boundary. To maintain or grow the context, use `.agents/skills/spctx-project-context/SKILL.md`.
