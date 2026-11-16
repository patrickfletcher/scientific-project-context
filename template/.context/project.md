# Project Context

Purpose: compact, current context for safe work by human and agent contributors.
Read when: starting work, checking project intent or current reality, or deciding whether more documentation is justified.
Update when: the purpose, a current answer, the focus, a protected input, what later work depends on, or sharing intent changes; rewrite the affected part in place.

Keep this file to about one screen. Describe what is known now, not how the project got here; Git keeps the history. Agents imitate this file, so write it the way you want the project's other documents written.

This is not a form to complete. Delete prompts that do not apply, and write explicit unknowns instead of invented facts. A person or agent may draft it from the evidence; the user corrects what it says the science means. Add another context document only when recurring detail persists, changes for its own reasons, and makes this file hard to scan. `.context/index.md` lists every context document, so keep no list of them here. Link one only where a statement points to its detail.

This file holds scientific purpose, current state, findings, risks, and open decisions. `AGENTS.md` holds environment, commands, and conventions; `README.md` holds human setup and command documentation. Link to them; do not repeat them here.

`.context/scientific-practice.md` is the stable scientific contract. This file records how that contract applies to this project.

## Purpose and Useful Outcome

**What this project does**: [one or two sentences]

**Who uses the result and what useful outcome they need**: [who, and what they need out of it]

**What this builds on**: [the prior work, datasets, methods, or theory this project takes from its field, with identifiers, or a link to where its sources are kept; `not identified yet` is fine]

## Current Reality

**Main materials and entry points**: [the data, notebooks, scripts, protocols, instrument configurations, models, or outputs someone needs to find the work; not how to run it]

**How a result or behavior is checked**: [control, reference measurement, expected property, test, or explicit absence of any check]

**Operating conditions that affect the science**: [instrument or acquisition state, biological or physical conditions, access limits, or explicit unknown; routine software setup belongs in `README.md`]

## Current Work

**Current focus**: [what is being worked on now]

**Next meaningful step**: [the smallest useful next step]

## Scientific Work, Evidence, and Outputs

**Protected inputs**: [the data, reference material, calibrations, or curated decisions the work takes as given, and why each is fixed; or `none identified yet`]

**What could make the result wrong even if the workflow completes or looks plausible**: [the main failure modes]

**Smallest useful check**: [a check or observation you could actually perform, with its expected value, tolerance, uncertainty, property, comparison, control, or failure signal; if no question is chosen yet, say so]

**Current findings and limits**: [the current answer to each question the work asks, with its uncertainty and main limit, or `no findings yet`. Rewrite an answer when it changes. Link to where run details live; do not copy them]

**What later work depends on**: [the settled choices later work now assumes, such as units, conventions, exclusions, parameter ranges, calibration, or randomization, or `nothing yet`. Name only what a change would now break; anything not named can still change freely]

That last line decides what a change here owes. While it names nothing, all work
is exploratory and owes only a statement that it is provisional. Add an entry when
you decide that later work will depend on something, and say so. No tool can make
that decision for you.

## Unresolved Questions

[only questions that must persist across sessions; ask blocking questions directly. Keep ideas not yet adopted here or in one page this links. Exploratory work may try any of them; adopting one means moving its text, so adopted text states what was adopted without hedging]

## Sharing and Reuse

[current paper-companion, archive, internal handoff, library, or service intent when known; `not relevant yet` is fine]
