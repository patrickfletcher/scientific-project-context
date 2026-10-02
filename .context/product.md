# Product Definition

Purpose: define what Scientific Project Context is, the outcomes it should improve, and the boundaries that keep it small.
Read when: changing the starter files, user journey, context rules, or product scope.
Update when: observed use changes the product promise, lifecycle, or boundary.

## Product Promise

Scientific Project Context is a lightweight, project-local system that helps scientists and their agents preserve the reasoning and evidence needed to change, challenge, repeat, and extend computational work.

Its compact promise is:

> Preserve the minimum trustworthy route from scientific question or decision to inputs, method, check, evidence, uncertainty, and supported limits—and let it evolve with the work.

The intended day-to-day interaction is agent-led: a scientist asks an agent to
inspect, use, and maintain project context, then reads and corrects the
project-owned documents. Agent Skills provide procedures at those moments;
the CLI handles bounded setup and checks, not scientific meaning. Agents are
the current way to work with the system, not its scientific purpose. Success
would be scientific continuity with less repeated explanation, not more
documentation; that outcome has not yet been established across projects.

## Scientific Specifications in Context

A **scientific specification** is the maintained, reviewable account of what matters for a piece of scientific work and what would make it trustworthy enough for its intended use. Depending on the project, it may include an intended behavior or claim, assumptions and domain limits, protected inputs and curated decisions, expected checks or failure signals, and the evidence and limitations currently attached to them.

A scientific specification is not necessarily one file, formally complete, machine-verifiable, or already true. It may be narrative, incomplete, and distributed across existing authoritative sources. Hypotheses, unknowns, conflicting observations, review state, and stale evidence must remain visible rather than being promoted to facts by the system.

Supporting project context makes those specifications usable: current reality, current work, unresolved questions, contributor conventions, authoritative routes, and sharing intent. The product maintains the connection between the two without requiring users to learn a document taxonomy or turn every useful fact into a formal specification.

## Design Principles

1. **Inspect before asking.** Recover observable facts from the project before asking a user to restate them.
2. **Keep context and evidence proportional.** Start small and add a focused context document only when recurring detail no longer fits comfortably. Scale the evidence a result owes to what depends on it, not to whether the work is scientifically material. Real use showed the materiality gate alone producing validation machinery for exploratory work, because nothing in the contract could say "not yet".
3. **Bring scientific practice into the work.** Surface relevant provenance, transformations, assumptions, uncertainty, protected inputs, failure risks, checks, evidence, limits, and staleness when the work makes them matter.
4. **Give each durable fact one authoritative home.** Reuse an existing issue tracker, README, data dictionary, test plan, architecture document, or public guide when it already works. Choose the correct surface before choosing the file: see Surface Ownership below.
5. **Keep meaning and permission review-owned.** Scientists and domain reviewers decide scientific meaning and claim scope; project, data, and community authorities decide permitted changes, use, and sharing. Do not infer one role from the other. Generated material remains visibly review-required until confirmed.
6. **Bound automation to inspectable mechanics.** Tools may copy known resources, check structure, and update marked inventories. They do not decide what a project means or which conclusions are valid.
7. **Connect results and claims to evidence.** Make the relevant chain from source inputs and transformations through settings, notebook/code/protocol and method identity, expected signal, observed result and uncertainty, limits, and staleness reconstructable.
8. **Prepare for sharing without front-loading release work.** Confirmed internal context may become the basis for public documentation when a paper, archive, release, or handoff becomes real.
9. **Measure outcomes, not document counts.** Reading burden, avoided errors, useful checks, and successful handoffs matter; file creation alone does not.
10. **Write for the reader, not the repository.** Every file the product ships or generates should read as ordinary scientific and engineering English. Do not introduce private vocabulary into a project that has its own. Real use showed this product's register leaking into a scientific repository until the user banned it by hand.

## Surface Ownership

A project has three durable text surfaces with different readers and different
read frequencies. Real use showed that without an explicit rule, initialization
duplicates environment, dependency, and command detail into all three at once.

| Surface | Reader | Owns | Does not own |
| --- | --- | --- | --- |
| `AGENTS.md` or another discovered instruction file | agents, every session | Operational constraints an agent must honor before acting: which environment to activate, how to invoke tests and tools, protected inputs in one line, repository conventions, and routes to everything else. | Scientific argument, evidence, or anything a human reader needs. |
| `README.md` or other public documentation | humans, including outsiders | Setup, commands, outputs, and the project's purpose in plain language. | Agent-only constraints, internal jargon, transient counts, or anything that goes stale between runs. |
| `.context/project.md` and its focused sources | humans and agents, on demand | Where the science stands, what it rests on, and what is undecided. | Always-read operational constraints, or a second copy of README setup detail. |

Each fact belongs to exactly one surface. The other surfaces link to it. When a
fact is operational *and* scientifically material — a protected input, for
example — the instruction surface carries the one-line constraint and the
project context carries the reasoning.

## Natural Lifecycle

The system supports a recurring pattern rather than mandatory stages:

```text
understand -> work -> check -> update -> add context when needed -> prepare for sharing
```

A one-off analysis may remain in the starter set for its entire life. A maintained scientific library may gradually add validation, architecture, decision, coordination, and release context. Both begin with the same small entry point, and neither must adopt project-type labels.

## Current Product Shape

The starter set contains six files:

```text
AGENTS.md
.context/project.md
.context/scientific-practice.md
.agents/skills/spctx-project-context/SKILL.md
.agents/skills/spctx-public-writing/SKILL.md
.agents/skills/spctx-scientific-change/SKILL.md
```

- `AGENTS.md` carries project authority and collaboration conventions, a compact versioned route to current context and its maintenance workflows, the project essentials an agent needs before acting (environment activation, test and tool invocation, protected inputs in one line, repository coding conventions or a route to an existing convention source, and where `spctx` is installed), and where each kind of fact lives. It is the scarce budget: everything an on-demand skill can own has been moved out of it.
- `.context/scientific-practice.md` carries the stable, relevance-gated scientific contract: researcher/agent authority, what will depend on the result and the evidence each level owes, protected material and permitted use, questions and methods, provenance and uncertainty, discriminating checks, evidence and staleness, and claim boundaries.
- `.context/project.md` is the compact project-specific application: purpose, materials and entry points, current work, protected material, main scientific risk, useful check, evidence and limits, what later work relies on, unresolved questions, and sharing intent. The relied-on list is the one that carries the intended-use levels in practice: the default is exploratory, only the exceptions are named, and a change that touches nothing on the list needs no ceremony.
- `spctx-project-context` activates, initializes, refreshes, separates, and retires context, records the project's own field conventions in the practice contract outside the managed core, and tunes the skill trigger descriptions to the project's own vocabulary.
- `spctx-scientific-change` connects a material change to its main risk, smallest useful check, evidence, and stale dependents, and stops after stating the risk when nothing depends on the result yet.
- `spctx-public-writing` turns confirmed facts into text for a named reader outside the work, matching claim strength to the level the work has reached and keeping public text true to the implementation. It applies the levels the contract defines rather than defining its own, and hands a claim that would be promoted by drafting back to `spctx-scientific-change`.
- `.agents/skills/` is the sole procedure surface. Each `SKILL.md` combines portable discovery frontmatter with its complete canonical procedure, and states which skill it is before acting so a transcript shows whether the procedure ran.

The three skills divide by the kind of work rather than by document type: establish and repair context, change something scientifically material, or write for an outside reader. That split came from real use. Public writing was previously a step inside `spctx-project-context`, where a request such as "write up the results" would almost never route to it, and the one documented recurring field failure was exactly this: internal detail and transient counts leaking into a public README. Reader, stage, and currency are also judgments the other two skills never had to make.

Design \u2014 choosing what observation would discriminate between competing explanations \u2014 is deliberately left to people. It is the highest-leverage scientific moment and the one where a plausible generated answer does the most damage, so the contract asks for a discriminating check and an expected signal rather than offering a procedure for inventing them.

Trigger descriptions ship generic and are project-owned afterward. `spctx` never overwrites them and checks only their structure, so tuning them to the project's real vocabulary is safe; `spctx-project-context` includes that step. Current guidance identifies `description` as the routing contract, which makes project-specific phrasing the cheapest available accuracy improvement.

When several focused context documents make navigation non-obvious, `sync-index` adds `.context/README.md` as a slim router. It lists the starter files, the generated inventory, and an invitation to add whatever the project needs; it prescribes no document kinds. A project-specific document should be created directly when it is the clearest authoritative home. Current context sources begin with short `Purpose`, `Read when`, and `Update when` guidance so a person or agent can select and maintain them quickly.

The prescribed layout stops at the six starter files plus that optional router. Everything under `.context/` beyond them is the project's, named as the project likes; asking an agent for a document is enough, and it will place one there. A project declares a settled fact in those documents whenever it wants the fact protected. The package ships no example documents: a collection of them that no command could deliver was removed at dev21.

## Activation and Maintenance Model

| Layer | Authoritative home | Role |
| --- | --- | --- |
| Durable bootstrap | A project-authorized instruction surface, normally `AGENTS.md` | Routes agents to current context, maintenance, and scientific practice. |
| Current application | `.context/project.md` and only necessary focused sources | States what is true, uncertain, protected, active, and next. |
| Stable safeguards | `.context/scientific-practice.md` | Defines the relevance-gated scientific contract without duplicating project facts. |
| Agent Skills | `.agents/skills/` | Exposes concise trigger metadata and the complete procedures for context maintenance and scientifically material work. |
| Bounded mechanics | `spctx check` and `spctx sync-index` | Checks exact structure and synchronizes only generated navigation. |

Files on disk are not adoption. Reliable self-maintenance requires the compact route in an instruction surface that the agents in use actually discover. New projects receive the complete route in the packaged `AGENTS.md`. For retrofits, initialization must preserve existing instructions, identify the actual discovery surface with an agent or user, and ask the project authority to approve the smallest compatible route after conflict review; full-file replacement is neither required nor allowed by the CLI. Project context and the canonical skills remain the single authority. If no durable route is approved, the honest state is `manual_activation_required`.

Maintenance is event-driven. Ordinary work updates only the durable facts, evidence state, current focus, and routes that changed. A focused source is added only after sustained pressure and is retired after its still-current content has moved to an authoritative home. Git history is the default home for superseded planning and narrative; protected, discrepant, negative, stale, or claim-bearing evidence follows its scientific or governance retention rules instead of being discarded by age.

Successful initialization presents the same bounded command inventory through two entry points: the human/machine operation report and installed `AGENTS.md`. Discovery does not imply use. The public CLI consists of `init`, read-only `check`, and preview-first `sync-index`.

Agent Skills discovery is part of the starter contract. Current Codex and VS Code documentation both support `.agents/skills/`, so the three skills are always installed there for the primary Codex-plus-Copilot use case. Their YAML frontmatter contains only the portable required `name` and trigger-oriented `description`; each body is the complete canonical procedure. Host-specific or experimental fields are omitted unless a demonstrated behavior requires and validates them.

Claude Code is the second primary target and reads no path under `.agents/`, so `--claude` adds one generated pointer per skill under `.claude/skills/`: the same description, and a body that routes to the canonical file. Claude Code reads `AGENTS.md` directly while the project has no `CLAUDE.md`, so the instruction file needs no second copy; where a `CLAUDE.md` exists, the report asks for an `@AGENTS.md` import line and never edits it. Two copies of a procedure would drift, so no procedure body is ever duplicated to reach a host, and a pointer that no longer agrees with its skill is reported. Apart from this bounded pointer, the CLI generates and manages no alternate skill root. Occupied canonical skills and occupied pointers remain project-owned and are not overwritten. Context documents are not skills: they retain visible `Purpose`, `Read when`, and `Update when` guidance rather than duplicating it into universal YAML metadata without a defined consumer and versioned schema.

Generated context-index entries contain a path and, when complete, the bounded `Purpose`, `Read when`, and `Update when` values already present near the start of that source. Missing or malformed guidance stays visible as a structural warning and path-only route. The index remains a generated navigation projection; source documents remain authoritative.

The ordinary user request may be “initialize this project with Scientific Project Context.” The caller first previews `spctx init . --dry-run`. The CLI installs safe missing files and reports the handoff; it defers a missing `AGENTS.md` when adding it would activate retained unreviewed practice or skill content. An agent inspects the workspace and its actual instruction surfaces, compares retained instructions with the project-context and scientific-practice contracts, proposes only the compact missing route for user review, and populates or refreshes `.context/project.md`. A scientist or domain reviewer resolves scientific meaning and claim scope; the relevant project or data authority resolves permitted change, use, and sharing. A human may execute the same mechanics and then hand the semantic steps to an agent.

## Adoption Cases and Failure Boundaries

- **New project**: install the exact starter baseline, then replace project prompts with observed facts, explicit unknowns, and reviewed domain judgment. This is routed after apply, not scientifically validated.
- **Existing project with compatible instructions**: retain every occupied file, install gaps, and add the compact project-context route to an actually discovered instruction surface only after comparison and user review. The CLI currently verifies the `AGENTS.md` route and versioned core, not prose compatibility or platform-specific discovery.
- **Existing project with conflicting instructions**: preserve both sources and ask the user or domain authority to resolve the material conflict. Do not guess precedence from filenames or automatically merge instructions.
- **User declines every discovered instruction change**: retain a useful manually activatable contract, warn that persistent agent discovery is absent, and require explicit prompting for context maintenance and scientific work. Do not report durable adoption.
- **Existing scientific governance**: link to accepted protocols, validation plans, data dictionaries, or public specifications rather than copying their facts. The core supplies process safeguards, not a rival scientific authority.
- **Small or non-scientific task**: apply the relevance gate. Do not turn formatting, packaging, or routine maintenance into a ceremonial validation exercise.
- **Growing project**: keep project application compact and split only when recurring detail persists, updates independently, and harms scanability.

The traps are false adoption from file presence, instruction takeover, universal-checklist bloat, invented expected results, ceremonial tests, duplicated scientific facts, silent evidence staleness, and a clean report being misread as scientific approval. Separate adoption states, reviewed routing, a relevance gate, discriminating expected signals, one authoritative home, explicit staleness, and visible validation boundaries are the corresponding controls.

## Context and Review Rules

For an existing project, inspect public docs, data and sample provenance, notebooks, scripts, protocols, acquisition or calibration records, source, tests, manifests, environments, configuration, outputs, and visible interfaces first. Ask only about material meaning, expected behavior, change authority, safety, access, scope, or source conflicts that cannot be discovered.

Keep low-volume facts in `.context/project.md`. `spctx-project-context` owns the
test for when a separate document is warranted; this repository does not restate
it.

Link to an existing authoritative source instead of copying it. If a new document is generated, include only supported facts, make unknowns explicit, and retain a visible review-required marker until consequential scientific, safety, access, licensing, governance, or claim content is confirmed. A declined split should not be suggested again unless the situation materially changes.

Generated public text follows the same rule. Once a public document becomes authoritative, internal context links to it instead of maintaining a shadow copy.

Current context is not an activity archive. Before retiring a source, move any still-current rule, decision, uncertainty, route, or evidence to its authoritative home, then remove the source from current navigation. Use Git history for superseded planning and narrative unless scientific, legal, governance, or project requirements establish another retention owner.

## Product Boundary

The starter product is project-local and does not require a particular agent platform or hosted service. It does not prescribe scientific conclusions, infer authority from filenames, make structural checks stand in for scientific review, or require a documentation tree on day one. Initialized projects may already rely on `AGENTS.md`, `.github/`, `.claude/`, or other instruction and skill paths; bootstrap must preserve those surfaces and integrate the compact route only with project authority.

`template/` holds the product's Markdown resources. The installed package and
CLI are the public product surface. Root `.context/` is this repository's own
maintainer context.

The experimental installed package provides resource identity, safe gap-filling
project initialization, bounded context-index synchronization, and a read-only
state report. No supported public release, stable Python API, automatic
migration, or compatibility promise exists yet. Projects own every occupied
file; no tool may overwrite or semantically migrate it.

`.context/` is the project-context namespace used by the package, starter template,
and this repository itself. Pre-dev13 `.design/` projects are
not interpreted as current context or migrated automatically: project owners must
rename the directory and update their project-owned routes before checking the
result. This keeps the pre-1.0 namespace change explicit and preserves the rule
that tools do not overwrite or semantically migrate occupied project files.

### Managed and Project-Owned Regions

Occupied files are project-owned, but a few regions track the installed package.
Without them a packaged improvement can never reach a project that already
adopted the starter, which was an observed real-use failure: an upgrade dropped
packaged trigger categories from every skill description and nothing detected it.

| File | Tracks the installed package | Project-owned |
| --- | --- | --- |
| `.agents/skills/*/SKILL.md` | the body, and the description up to `Also use for requests such as:` | everything from that separator onward |
| `.claude/skills/*/SKILL.md` | nothing; generated once from the skill it points at | everything, with `DH-SKILL-004` reporting disagreement |
| `.context/scientific-practice.md` | the marked core | everything outside the markers |
| `AGENTS.md` | the marked routing block | everything else |
| `.context/project.md` and focused sources | nothing | everything |

`check` reports divergence in a tracked region as an observation, never as a
verdict, and separates this project's own trigger phrasings from any other
difference: adding them is the outcome the system wants, not drift. A project
may maintain its own copy of a procedure or description; the cost of doing so
stays visible instead of silent. No command rewrites a project-owned region.

This repository is the one project that cannot tune its own trigger
descriptions. Its `.agents/skills/` copies must stay byte-identical to the
packaged ones they ship, so `check` here will keep reporting that none carry
project phrasings. That line is correct and not actionable in this repository
alone.

### What the Report Makes Visible

`check` reports state rather than passing or failing a project, because a
verdict invites the reader to treat structure as approval and hides the
individual signals that are actually actionable. Each line is there to prompt
one decision the project may not have made yet: activate the route, answer the
remaining prompts, tune the triggers, write the field's practice notes, or say
what later work now relies on.

Two upgrade trials showed that an agent does what the numbered steps and the
report's summary lines make visible, and skips what they do not. A step with no
mechanical input and no required report line does not reliably run. The report
is therefore a behavioral lever, not only a record.

Before printing any number, apply this test: **would the cheapest way to improve
it also be the right action?** If not, the number will make the product worse.

The same test governs a finding, and dev20 showed it has a second half: a signal
that fires on the wrong thing is worse than no signal, because the cheapest way
to clear a false finding is to contort the prose that caused it. Both new
signals were narrowed against real files before shipping, and the one real
adopting project is the standing test for whether a check is quiet where it
should be. Prefer a summary line to a finding wherever the project may honestly
have nothing to do, so a settled project is never told about it twice.
Two failures of this test are on record. The difference report counted project
trigger tuning as drift, and the next trial removed the tuning to reach zero.
The repeated-passage report first offered rewording as a resolution, which would
have converted detectable repetition into undetectable paraphrase.

Use the report to name a project-owned choice and show its current state, and
leave the decision to the project. State a measure's blind spot next to the
measure, so a low number is not read as a clean result. Do not add a quality
score, a demand, or a line that repeats itself on every run of an unchanged
project.

### Repeated Passages

Repetition is not one problem, and its cost depends on where it sits.

| Where | Cost | Treatment |
| --- | --- | --- |
| A project file repeats packaged reference text | The package updates on its own schedule and the copy does not, so the copy becomes stale guidance presented as current | A finding; the copy should go |
| A project document repeats another project document | Two statements can drift apart, at a cost proportional to how often the fact changes | A pressure signal for the maintenance pass to judge |
| Different readers or moments, such as a one-line constraint in the instruction file and its reasoning in project context | Intended | Allowed |

`check` reports a passage of twelve or more words that appears in two places
among the instruction file, the project's current context sources, the packaged
skills, and the shared practice core. It compares words only: it does not judge
which place should keep a fact, and it cannot see a paraphrase. Only an agent
reading for meaning can do either, so the tool's role is to say that maintenance
is due and where to start looking.

The starter repeats nothing, and a maintainer test enforces it. No exclusion
list is kept for packaged text: the one that existed hid more repetition than
the exception it was written for.

A project may decide a repetition is worth keeping, such as a packaged passage
it wants in the always-read file. The finding names that choice and its cost
rather than demanding a change, but it will appear on every run until the text
changes. Whether that becomes an irritation, and whether an inline exemption
marker would be worth its ceremony, needs field evidence before anything is
built.

Generated inventory blocks, versioned managed blocks, fenced and inline code,
and link targets are excluded because they repeat by design. The packaged
instruction and project files are drafts a project is meant to edit, so they are
not treated as reference text.

### Skill Size

A skill is read on demand, so its cost is paid per invocation, not per session;
the always-read instruction file is the scarce budget. Length therefore matters
less than whether a reader can tell which steps apply right now.

The observed failure is not length. Both skipped steps on record lacked a
mechanical input and a required report line, while longer neighbouring steps ran
correctly. When a skill grows, make the route from mode to steps explicit before
considering any split. Keep each skill one file: the resource contract expects
exactly one `SKILL.md` per directory, and a project that must consult several
files to follow one procedure is worse off than one reading a longer page.

## Onboarding

A new project receives the whole starter. An existing project receives only what
it lacks, and loses nothing. The distance between those two outcomes decides
whether adoption changes behavior or quietly changes nothing.

| Situation | What `init` does | What is absent afterwards | Main risk |
| --- | --- | --- | --- |
| Empty or new directory | Writes all six starter files | Nothing | Placeholders left unfilled still read as adopted |
| Existing repository, no instruction file | Writes the starter, including the instruction file | Nothing structural | As above |
| Existing repository that already has `AGENTS.md` | Keeps it byte-for-byte and reports the routing block for a person to place | Every packaged instruction section except the route | An inert install: files present, day-to-day behavior unchanged |
| Existing repository with `.github/copilot-instructions.md` or a contributing guide, but no `AGENTS.md` | Writes `AGENTS.md` | Nothing structural | A second instruction file competing for authority, which nothing detects |
| Skills or the practice contract present, instruction file missing | Defers the instruction file | The route | Deliberate: retained unreviewed content must not be activated |
| Claude Code, with `--claude` | Adds a pointer per skill under `.claude/skills/` | Nothing, unless a `CLAUDE.md` exists | A `CLAUDE.md` silently displaces `AGENTS.md`, so the report names that case |
| Hosts that read neither skill root | Writes files | Discovery | Reported as `manual_activation_required` |

The first risk in that table is the one with no mechanical input, so the report
asks for `Project Essentials` by name and prints the interpreter it ran from.
Field use showed both halves failing at once: an agent invented its own setup,
and reported `spctx` as unavailable because nothing said where it lives.

### Position

The package owns three things in a project and nothing else: the routing block
between its markers, the scientific-practice core between its markers, and the
skill bodies with the packaged part of each description. `check` reports when
any of them drifts, `check --diff` prints the difference, and upgrade mode
restores them. Anything the package owns must be detectable and repairable, or
it will rot in place while the project believes it is current.

The routing block names every skill that ships. Naming some and not others
leaves the rest reachable only by whatever the host happens to index, and a test
holds the block and the shipped skill list together.

No command edits an occupied instruction file. That guarantee is what makes the
product safe to try at all, and it is worth more than any content a command
could add. Being opinionated belongs in the skill, which can propose, explain
itself, and be refused; a command can do none of those. What a command can do is
say what it observed: `init` names the instruction files a project already has
before adding another, and says so plainly when it finds none, because the
user's next action differs in each case.

So after the route is in place, `spctx-project-context` offers the remaining
packed sections one at a time, adapted to the project, each acceptable or
refusable on its own. Version control is the backup; do not leave a copy of the
file beside it.

Offer in this order, because value and conflict risk differ sharply by section:

1. `Project Essentials`, highest value and lowest conflict risk. The first
   real-use receipt was an agent guessing how to run the project, and the CLI is
   reachable only from the environment this section names.
2. `Where Facts Live`, this product's central claim and the section an existing
   file is least likely to already state.
3. `Authority`, only where the existing file states no precedence of its own.
4. `Working Style`, offered last and dropped readily. A maintained repository
   usually has its own, and this is where a merge tramples most easily.

Skip any section whose subject an existing conventions file already owns, and
link to that file from the instruction file instead.

## Default Addition Rule

Add an always-present file, concept, or prompt only when it prevents a high-impact failure or repeatedly improves early work more than it increases setup and reading burden. Otherwise keep it in an on-demand workflow, optional resource, existing project system, or triggered future change.
