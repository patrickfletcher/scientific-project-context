# Scientific Practice Contract

Purpose: define the durable scientific safeguards that human and agent contributors apply to this project's work.
Read when: work could affect scientific meaning, protected inputs, methods, evidence, artifacts, validation, or claims.
Update when: the project deliberately adopts a revised scientific-practice contract; keep project-specific facts elsewhere.

This is a working agreement for researchers and their assistants, not a universal checklist. Most work is exploratory and owes little beyond keeping its results honest; what a result owes grows with what depends on it. Apply only the safeguards relevant to the work at hand.

Read this once when the project starts, and make it yours. The marked core below is a shared starting point, not a rule imposed on the project: add your field's conventions, standards, protocols, or review requirements in the sections outside the markers, and say plainly where this project deliberately does something different. A contract nobody has read or agreed with will not improve the work.

When later work relies on a result, or it is about to be shared or published, keep a traceable route:

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
## Decisions and Protected Material

- The user decides what results mean, how far a claim may go, and what later work relies on. Inspect the evidence before asking, draft from it, and let the user correct the draft. Distinguish observations, derived results, proposed interpretations, and unknowns; a plausible agent-generated explanation is not evidence.
- Name the inputs the work takes as given: raw or accepted data, reference material, calibrations, schemas, curated decisions, and anything later work relies on. Change one when the request clearly means to. When a change would touch one as a side effect, or the request is ambiguous, say what would change and ask once.
- Permission to use, change, or share data or material the project did not produce comes from whoever controls it, including participants and communities; technical access does not establish permission. Record identifiers, provenance, and access terms, and do not copy controlled material into context merely to make it self-contained.
- Treat generated outputs as derived artifacts, not trusted inputs, until someone decides to rely on them.
- When another instruction conflicts with these safeguards about something later work relies on, ask the user rather than choosing.

## What Will Depend on the Result

- What a result owes depends on what will depend on it:
  - **Exploratory**, the default: nothing depends on it yet. Work quickly, keep negative and odd results, and give each consequential choice, and the alternative set aside, one sentence where the work is done. Say in your reply what was done and that it is provisional. No check, evidence record, or staleness marking is owed, and project context changes only when the current answer to one of its questions changes. A working default may be adopted while exploring; say that it is provisional.
  - **Relied on**: the project's list of what later work relies on names it. Record in a sentence what it rests on: the choice, the alternative set aside, what would change it, and one control, comparison, or sensitivity.
  - **Published**: people outside the project will rely on it, in a paper, poster, release, or handoff. The full route above is owed, including uncertainty, limits, and review, and a public version of the work reproduces the published result for any reader who runs it. This is the one strict reproducibility standard.
- Evidence is owed when later work starts to rely on a result, not when the result is produced. Work freely while exploring and pay when something starts to depend on the answer, by rebuilding what is needed from the commit, settings, and outputs the work already left. Propose adding a result to the list when work starts to depend on it; the user decides. A dependency is real whether or not it has been listed yet.
- Five things hold at every level, and each is met by what you do rather than by saying so: protected material stays protected, discrepant and negative results stay where they are, decisions stay with the user, nothing is described as better established than it is, and no outside source is cited without being identified; a reference recalled rather than looked up is marked as recalled. Do not narrate that something stayed unchanged, did not happen, or was approved. Review of a result that later work relies on is evidence and is recorded as such; permission to run a step is not.

## Question, Method, Risk, and Limits

- For a result later work relies on, or one about to be published, state the question, decision, behavior, or claim at issue; the main way it could be wrong even if the workflow completes or the result looks plausible; and its intended domain and limits.
- Make material input lineage, transformations, exclusions, units, conventions, parameters, calibrations, initial or boundary conditions, and randomization explicit as relevant. Record consequential choices made after inspecting results.
- For such a result, when conclusions depend on sampling, randomness, fitting, filtering, subjective choices, or model form, report relevant uncertainty or variation and whether reasonable alternatives change the conclusion.
- Prefer explicit named parameters and recorded settings over hidden scientific assumptions or unexplained constants.
- Do not generalize a result beyond the inputs, methods, environments, populations, backends, or conditions actually supported by evidence.

## Discriminating Checks

- Above the exploratory level, name the smallest check or observation that could expose a consequential error. Include the expected result, tolerance, uncertainty, property, comparison, control, or failure signal.
- Derive the expected signal from accepted evidence or domain judgment before inspecting the changed result when practical. Do not invent an expected result merely to complete a check.
- Prefer a check with some independence from the logic or data path being changed. Controls, reference materials, invariants, held-out cases, alternative implementations, limiting cases, and clean-session reruns are examples, not requirements.
- State what the evidence establishes: implementation verification, scientific validation for an intended use, computational reproducibility with the same inputs and conditions, independent replicability with new data or evidence, or generalizability beyond the tested setting. Do not treat one as proof of another; test existence or successful execution alone is not validation.

## Evidence and Staleness

- For a result something already depends on, keep enough identity to interpret or repeat material evidence: input origin and version; transformation or exclusion path; notebook, script, protocol, acquisition, model, or method identity; material settings; software, instrument, environment, backend, or hardware state; observed result and uncertainty; expected signal; date; and important limits as relevant. Let the code that produces a result write machine detail beside its output: the code version as a Git commit, and the settings. Record where each outside input came from and which version; add a checksum when the source could change under the same name. Identify code by its version rather than by hashing its source, and never make code refuse to run because its source changed. Context needs the observed result, the expected signal, the limits, and a link.
- When something such a result rests on changes, such as an input, method, setting, calibration, dependency, backend, environment, or public behavior, rerun the affected evidence or mark it and the outputs built on it stale.
- Keep discrepant, null, and negative results and material deviations from the planned approach. Keeping a result means not deleting or hiding it, not retelling it in every later summary. Do not silently replace inconvenient evidence or keep describing stale evidence as current validation.

## Outputs and Claims

- Label an agent-drafted interpretation as provisional in your reply. It needs review before later work relies on it or it is published. Agent-drafted decisions about access, safety, licensing, ethics, or governance are proposals until the user confirms them.
- When a result is relied on or published, report what was checked, what remains provisional or stale, and what judgment still needs review.
- Treat clean structure and passing mechanical checks as readiness for review, not as scientific, ethical, legal, release, or publication approval.
<!-- END SPCTX SCIENTIFIC PRACTICE CORE v1 -->

## This Project's Practice

The core above ships to every project and knows nothing about this field. Answer
the lines below from this project and delete any that does not apply. None of it
is required: if the shared core is the whole of what this work owes, say so in
one line and delete the rest.

- **Standards, protocols, or reporting conventions this field expects**: [name them, or link the document that already holds them]
- **Review this work owes before it is published**: [ethics, governance, community, safety, or institutional review, if any, and who gives it]
- **What a reviewer here would count as adequate evidence**: [the controls, replication, sample structure, or reporting practice this field looks for]
- **Where this project deliberately differs from the core**: [say so plainly, with the reason]

## Keeping Application Proportional

Start with the compact fields in `.context/project.md`. Reuse an existing test plan, method note, data dictionary, benchmark record, issue tracker, or public specification when it already holds a fact. Add a focused context source only when the compact fields stop serving the work; the project-context skill named below says when.

For a scientifically material change, use `.agents/skills/spctx-scientific-change/SKILL.md` to turn this contract into an executable check and an evidence boundary. For context maintenance or growth, use `.agents/skills/spctx-project-context/SKILL.md`.
