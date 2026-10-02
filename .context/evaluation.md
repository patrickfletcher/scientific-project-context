# Evaluation

Purpose: define the evidence needed to assess the product and record what real
use has taught without identifying anyone.
Read when: interpreting checks, planning or recording a trial, or making a
product effect, usability, compatibility, or release claim.
Update when: product behavior changes, the tested platform range changes, or a
trial produces an observation that changes a claim or the product.

## Product Questions

The public product is the installable Markdown resource bundle and the `spctx`
CLI. Evaluation should answer four separate questions:

1. Do built artifacts contain the exact intended resources and command surface?
2. Do `init`, `check`, and `sync-index` preserve their documented filesystem and
   reporting contracts?
3. Do scientists and agents find and apply the guidance appropriately on real
   projects without disproportionate burden?
4. Is the package supportable across its claimed Python and operating-system
   range?

The product test suite addresses the first two questions only.

## Evidence Boundary

Passing unit tests and artifact checks establishes structural and mechanical
consistency for the exercised code paths. It does not establish scientific
validity, human ease, product effect, domain adequacy, cross-platform support,
release readiness, or publication readiness.

Real-use evaluation should keep claims separate: installation mechanics,
guidance discovery, scientific decision quality, handoff continuity, and user
burden are different outcomes. Human-ease claims require human observation;
scientific or domain-adequacy claims require appropriate domain review.

## What Has Been Checked

Build and artifact verification are rerunnable commands in `AGENTS.md`; run
them before sharing an artifact rather than keeping their output here. Two
facts outlast any one run:

- Installed wheels have been exercised only on CPython 3.10 and 3.11 on
  Windows. The rest of the declared range and every other platform are untested.
- Upstream documentation establishes that `.agents/skills/` is a supported
  repository path for Codex and for Copilot in VS Code, and that Claude Code
  reads `AGENTS.md` only while no `CLAUDE.md` is present. This is documentation
  evidence, not a local discovery or trigger observation.

## Recording Observations From Use

Trials run in other people's repositories and in the author's own private ones.
None of them may be identifiable from this repository, which may be shared
publicly, but their lessons must still reach the product.

- Give each trial an opaque ID (`T1`, `T2`, ...). The mapping from ID to
  repository or person lives only outside this repository, with the author.
- Record what the product did, not what the project is: the `spctx` version,
  agent host, new or retrofit setup, whether skills were selected or named,
  what went wrong or helped, the burden it imposed, and the product change or
  decision that followed.
- Describe a project only as coarsely as the lesson needs, such as "an analysis
  repository with several focused context documents". Never record a repository,
  person, lab, or institution name, a research question, a result, data or
  sample details, file or function names, commit messages, or quotations from
  the project's own files.
- Paraphrase what a person reported. Record only what they agreed to share.
- When a lesson is absorbed into product policy, the policy carries the rule and
  the table below keeps one line pointing at it. Do not grow a narrative log.

### Observations

T1 is the author's own analysis repository, used daily with Codex and Copilot
Chat from `0.1.0.dev11` through `0.1.0.dev19`, across several upgrades. All of it
is uncontrolled observation by the repository owner, not a scenario trial.

| Trial | Observation | What changed |
| --- | --- | --- |
| T1 | The compact project context became a genuinely scientific document, and focused sources split off under the three-condition rule each had a real update trigger and owner. | Confirmed the compact-context and split rules; no change. |
| T1 | `sync-index` plus the missing-guidance warning was the one CLI loop worth running: it kept routing lines complete across several focused sources. Other `check` findings rarely told a working scientist anything actionable. | Kept the index loop; `check` now reports state lines instead of a verdict (dev21). |
| T1 | Setup copied environment and command detail into all three places, and transient counts leaked into the public README. | Where Facts Live in the starter and Surface Ownership in `product.md`; `spctx-public-writing` (dev17). |
| T1 | This product's vocabulary leaked into collaborator-facing text, and the user had to ban it by hand. | Writing for readers in the skills and instruction file. |
| T1 | Agents reported `spctx` unavailable because it was reachable only from the environment it was installed in. | `Project Essentials` asks where `spctx` lives; `init` prints the interpreter it ran from. |
| T1 | Repository conventions had no prompted home and were added to `AGENTS.md` by hand. | `Conventions` prompt; the skill defers to an existing conventions file. |
| T1 | `sync-index` planned cleanly but failed on apply for root-level focused documents, because discovery and validation used two different rules. | One shared predicate (dev16). The agent correctly stopped rather than restructure context around a tool defect. |
| T1 | An upgrade rewrote all three skill descriptions, dropping packaged trigger categories, and edited a skill body; nothing detected it. | Drift reporting with `check --diff` and an `upgrade` mode (dev18). |
| T1 | An upgrade with that mode restored bodies but skipped deduplication beyond the section it edited, and treated project trigger phrasings as divergence to remove. | Upgrade steps and report wording now present tuning as the intended outcome (dev19 to dev21). |
| T1 | An explicitly requested tuning kept packaged descriptions intact, appended project phrasings, and preserved them across a later upgrade. | First observation of the intended tuning path; whether unprompted tuning happens is untested. |
| T1 | An exploratory method comparison grew into large benchmark and provenance code, because the scientific contract had no way to say "not yet". | Evidence levels in the practice core; `spctx-scientific-change` stops at the exploratory level (2026-09-25). |
| T1 | After months of use the project had written nothing in the practice file's own section, while adding field rules to `AGENTS.md` instead. | `localize` mode and a report line for the project's practice notes. |
| T1 | The new stale-path and practice-notes signals were run before release: both stayed quiet where they should. An earlier draft of each misread the project. | Narrowed both signals before shipping (dev20). Catching real drift is still unobserved. |

## Agent Skill Behavior Scenarios

Retain these scenarios for comparison on Codex and Copilot Chat. Structural
tests confirm only canonical paths, frontmatter, non-empty procedure bodies,
and non-overwrite behavior; they do not establish that an agent selects or
follows a skill correctly.

Run both harnesses against the same canonical `.agents/skills/` files in clean
sessions, checking explicit invocation and automatic selection separately. Do
not introduce alternate roots or same-named copies into the product trial.

| Request | Expected selection | Consequential observation |
| --- | --- | --- |
| Initialize or retrofit a repository and populate current project context. | `spctx-project-context` | Inspects sources before asking and keeps generated meaning review-required. |
| Reconcile stale `.context/project.md` facts after implementation changed. | `spctx-project-context` | Updates only affected durable facts and routes. |
| Change a filtering rule used in an analysis something relies on. | `spctx-scientific-change` | Names the main scientific failure mode, check, evidence, and stale dependents. |
| Change calibration or a scientific API's numerical behavior. | `spctx-scientific-change` | Preserves authority boundaries and does not equate a passing test with scientific validation. |
| Update the README after the pipeline entry point changed. | `spctx-public-writing` | Names the reader, checks commands against the code, and keeps agent-only detail out. |
| Write up current results for a collaborator or a methods section. | `spctx-public-writing` | Matches claim strength to the project's stage and leaves authorship and claims to review. |
| Reformat Markdown or rename a non-context implementation symbol. | neither | Avoids scientific or context-maintenance ceremony. |
| Fix routine packaging metadata with no scientific or context effect. | neither | Uses ordinary repository instructions only. |
| Bring the project up to date after installing a newer `spctx`. | `spctx-project-context`, upgrade mode | Restores packaged text, preserves project-owned phrasings, and prunes rules an older version left behind. |

Every `SKILL.md` names itself before acting, so selection, misses, and false
positives are readable from the transcript. Record whether that line actually
appears; if a skill's content is applied without it, the announcement is not
reliable evidence. Also record whether a public-writing request that would
change a scientific claim hands off to `spctx-scientific-change`.

No controlled per-scenario receipt exists yet. When the table is run, record
selection or miss, task completion, consequential errors exposed or avoided,
unnecessary questions, context read, and user burden, using the anonymity rules
above.

## Harness Automation Pilot

No lifecycle-hook behavior receipt exists. `automation.md` owns the boundary any
hook must keep. Evaluate an optional, read-only `SessionStart` hook that calls
`spctx check <target> --json` only after retaining a no-hook baseline, and keep
three conditions separate: explicit instruction routing, automatic skill
selection, and skill plus hook.

For each host and operating system, record host and version, hook discovery and
trust state, `spctx` version, report schema, startup duration, model-visible
output, user action, writes, and result. Cover at least: a healthy project, a
missing route, unanswered starter prompts, a missing CLI or timeout, a disabled
or untrusted hook, a session started below the project root, and prose that
became false while structure stayed valid, which the hook must not claim to
detect.

Do not retain prompts, transcripts, protected data, or session summaries for
this evaluation. Package an adapter only if it catches consequential structural
failures otherwise missed, with low latency and warning burden, no writes, and
the structural-only boundary intact.

## Next Useful Evidence

- Colleague trials and further author trials, recorded under the rules above:
  whether skills are found without being named, whether exploratory work stays
  cheap, whether the report lines prompt anything, and whether context upkeep
  costs less than it returns.
- Whether an untuned project's `0 of 3` line prompts tuning without a request,
  and whether tuned descriptions improve automatic selection.
- The scenario table above in clean Codex and Copilot Chat sessions.
- A CI matrix across the declared Python range and operating systems.
