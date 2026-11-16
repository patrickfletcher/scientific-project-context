# Project Context

Purpose: compact, current context for safe work by human and agent contributors.
Read when: starting work, checking project intent or current reality, or deciding whether more documentation is justified.
Update when: the purpose, a current answer, the focus, protected material, what later work relies on, or sharing intent changes; rewrite the affected part in place.

Keep this file to about one screen, and describe what is known now rather than how the project got here; Git keeps the history. Agents imitate this file, so write it the way you want the project's other documents written. This is not a form that must be completed: delete prompts that do not apply, and use explicit unknowns instead of invented facts. A person or agent may draft it from available evidence; the responsible scientist reviews scientific meaning, and whoever is responsible for the project or data reviews intent and permissions. Add a focused source only when recurring detail persists, updates independently, and materially harms this file's scanability. `.context/index.md` lists every context document, so keep no list of them here; link one only where a statement points to its detail.

This file holds scientific purpose, current state, findings, risks, and open decisions. `AGENTS.md` holds environment, commands, and conventions; `README.md` holds human setup and command documentation. Link to them rather than repeating them here.

`.context/scientific-practice.md` is the stable scientific contract. This file records how that contract applies to the current project.

## Purpose and Useful Outcome

**What this project does**: [one or two sentences]

**Who uses the result and what useful outcome they need**: [who, and what they need out of it]

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

**Smallest useful check**: [a check or observation you could actually perform, plus the expected value, tolerance, uncertainty, property, comparison, control, or failure signal; say why it is premature if no scientific question or behavior is chosen yet]

**Current findings and limits**: [the current answer to each question the work is asking, with its uncertainty and main limit, or `no findings yet`; say which level these results sit at. Rewrite an answer when it changes, and link to where run details live rather than copying them]

**What later work relies on**: [the settled choices later work now assumes — units, conventions, exclusions, parameter ranges, calibration, initial or boundary conditions, randomization — or `nothing yet`. Name only what a change would now break; anything not named here can still change freely]

That last line decides how much evidence a change here owes. While it names
nothing, work stays exploratory and owes nothing beyond saying it is
provisional. Add an entry at the moment you decide to rely on something, and say
so; no tool can make that call for you.

## Unresolved Questions

[only questions that must persist across sessions; ask blocking questions directly instead of parking them here. Keep proposals awaiting a decision here or in one page this links, so adopted text can state what was adopted without hedging]

## Sharing and Reuse

[current paper-companion, archive, internal handoff, library, or service intent when known; `not relevant yet` is fine]
