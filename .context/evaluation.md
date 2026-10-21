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

T2 is a colleague's computational analysis repository, retrofit over substantial
existing instructions with a pre-dev22 build, upgraded to dev22 two weeks later,
and used daily for about three weeks. `spctx` was installed in the project's
environment and run during the trial. No transcripts were kept and the agent host
was not recorded, so skill selection is not observable; the evidence is the Git
history, a written audit of the project's documents, and the colleague's written
feedback on the product. The packaged core and skill bodies were unmodified. Some project rules that contributed below were
added during the trial in the author's own maintenance sessions.

| Trial | Observation | What changed |
| --- | --- | --- |
| T2 | Every setup line was complete: route active, prompts answered, all three triggers tuned at setup, practice notes written, relied-on list named. The upgrade kept the tuning. | First tuning observation outside the author's repositories; whether it was prompted is unknown. |
| T2 | The check, risk, and negative-result prompts produced habits the project chose to keep: simulated positive and negative controls before real data, a concrete failure-mode list, and negative results kept beside common and shuffled comparators. | Confirms those prompts; no change. |
| T2 | Context became a run log. The compact file grew about fivefold in six days after an upgrade-time refresh had cut over a thousand lines; an earlier hand cleanup was also undone within days. Focused sources whose update trigger was an event, such as a run finishing, reached hundreds of lines. | dev23: the route and starter ask for current state rewritten in place, the split test excludes logs, and refresh rewrites a log instead of trimming it. |
| T2 | The prose turned defensive: what did not happen, what stayed unchanged, and who approved each step, about four times as dense per line as at setup. Permission given in conversation was written into documents and code. | dev23: the core's every-level rules are met by acting rather than stating, the exploratory level relaxes recording too, and permission to run a step stays out of the record. |
| T2 | This product's ownership, authority, promotion, and level vocabulary reached the project's prose, this time from the practice core and skills. | dev23: plain-language pass over the core, starter, and skills; a starter test keeps promotion and source-ownership terms out of shipped text. |
| T2 | No writing guidance reached internal documents. `spctx-public-writing` excludes them, and a project-added style section was ignored: agents imitated the documents they read. | dev23: a writing line in the starter's working style, and the compact file framed as the example later sessions copy. |
| T2 | Exploratory work became expensive again by a different route from T1: compute engineering and its documentation rather than validation evidence, each step approved one at a time on the agent's proposal. | dev23: `spctx-scientific-change` asks for the question before a sub-investigation, prefers shrinking a computation to engineering around it, and reports what was learned first. |
| T2 | `check` was run, and its repeated-passage findings were copied into a context document instead of being resolved. It reported nothing about any of the above, as designed. | Size and banned-word checks declined: moving text to another file or substituting a synonym clears either, which fails the report test in `product.md`. |
| T2 | Upgrade to dev23 in a fresh session with the skill named: it announced the skill, mode, and steps; replaced the route, core, and three skill bodies and checked them byte for byte; kept all three trigger phrasings; and stayed within the prompt's scope. It replaced the core without the core being named. | First observed announcement line and first core replacement during an upgrade. The prompt asked for every package-maintained region and the session followed the project's older copy of the procedure, so neither the new numbered step nor the new finding text is tested on its own. dev24: the upgrade's first step restores the skill's own body, and `DH-SKILL-003` on that skill says to restore it before upgrading, so an older copy no longer runs the upgrade. |
| T2 | Asked to list rather than remove, the whole-file duplicate step ran for the first time. It also listed the starter's own deliberate restatements, such as where facts live and the working style, which removal would have deleted. | dev24: the duplicate step no longer counts a statement aimed at another reader or moment, and notes that the packaged instruction file is written that way. |
| T2 | The upgrade surfaced project rules that contradict the new text: a per-run reading rule, per-run update triggers, leftover promotion wording, and a version pinned in prose. It also found that the starter's precedence list ranks the instruction file above the safeguards while the route and core say to ask on conflict. | Project rules go to the project's own pass. dev24: the starter's precedence list leaves the safeguards out of the order and says to stop and ask on a conflict with them. |
| T2 | A refresh with the skill named changed the rules that produced the log, reported three small edits beyond the request, and resynced the index unasked because its generated summaries still carried the old per-run triggers. | Confirms the dev23 refresh step; no change. |
| T2 | The dev23 always-read lines reached the project only by hand, because an upgrade carries managed regions alone. Written from the core and skill, they repeated packaged text, which `check` reported; the project kept them. | dev24: `init` prints the packaged instruction file whenever it keeps a different one, and upgrade and retrofit offer its sections in the packaged wording instead of writing them from the core. First field case of a project keeping a packaged passage in its always-read file. |
| T2 | The author's cleanup prompt removed protective rules along with the narration they produced; the agent flagged a notebook-preservation rule the project may want back. | No product change: the dev23 core keeps a rule and drops narration of compliance with it. The prompt went further than the guidance. |
| T2 | A project pass with the skill named rewrote the compact file to about a fifth of its length, drafted a findings page under the review marker while flagging two numbers it had derived rather than copied, and retired four log documents. | Confirms the review-marker path for a drafted scientific summary. Whether the result holds through normal use is the open measure. |
| T2 | Retiring those documents broke a project verification script that read them by path. The retire procedure covers links and routes, not code that reads a context file; the agent found the references and reported them. | dev24: the retire steps search code, notebooks, scripts, and configuration for the path and fix or report what reads it. |
| T2 | The instruction file located `spctx` by absolute paths containing a user name, one per machine, plus a pinned version that went stale at the next upgrade, in a repository meant to be shared. | dev24: `Project Essentials` and the setup step ask for the environment's name and a repository- or home-relative path, without a user name or version. |
| T2 | About forty analysis scripts hash their own source and stop with an error when it changes. The colleague attributed this to the core's request for file hashes beside outputs, but every guard predates dev23, which added that wording; the guards' error messages echo the older rules to mark changed evidence stale and keep discrepant results, and the project's own plan asked for checksums. The dev23 wording does not separate source from inputs, so it would reinforce the pattern. | dev24: the core asks code to record its version as a Git commit, settings, environment, and checksums only of inputs obtained from outside the project, and never to refuse to run because its source changed; `spctx-scientific-change` calls a failed reproduction a judgment for the moment, not a guard to build into code. |
| T2 | The staleness rules read as an obligation at every level. The core's rerun-or-mark-stale line and the refresh step's matching sentence are ungated, and dev23 dropped the exploratory level's explicit release from staleness. | dev24: rerun-or-mark-stale applies only to what a relied-on result rests on, in the core and both skills, and the exploratory level again owes no staleness marking; keeping discrepant results stays an every-level rule. |
| T2 | Ownership and authority wording outlived the dev23 pass: project and change authority in the context skill, owner and owns in the core and starter, material that must not change without a decision, and the starter's heading for protected material, which invited long lists. The project's shorter heading, naming the inputs themselves, read better. | dev24: a second plain-language pass names the people responsible instead, and the starter test now rejects authority, owner, owns, and the decision-gate phrase. The heading is Protected inputs, the name the instruction file and route already use, limited to inputs the work takes as given. |
| T2 | Gathering every proposal awaiting a decision into one page removed most of the hedging from the adopted pages. The colleague suggested shipping it as a document type. | dev24, as a rule rather than a type, per `product.md`: the starter's unresolved-questions prompt asks to keep proposals in one place apart from adopted text. |
| T2 | A system of numbered codes for questions, decisions, checks, and sources grew to about 1,500 references before the project replaced it with names. Nothing shipped discouraged it. | dev24: one naming line in the starter's writing guidance. `check`'s own numbered identifiers are machine keys in the JSON report and stay. |
| T2 | Two report defects: a `Purpose` line over the 280-character limit was reported as missing, and the plain report counts passages repeated among the project's own documents without naming them, although the context skill tells the reader to open them. The list appears only with `--diff` or `--json`. | dev24: an over-long line is reported as too long, with its length and the limit, and the plain report names each repeated pair and passage. |
| T2 | Index discovery reads only `.context/` and `.context/active/`, so a subfolder of focused documents with its own index was left out without notice, while the other `check` scans read it. The packaged index says where to put documents, but the project had rewritten that paragraph. | dev24: the index lists every Markdown file under `.context/`, in any folder; see the next row. |
| T2 | Preparing the dev24 upgrade found the same documents listed in four places: the compact file's opening lines, a hand-written list in the index, the generated list beneath it, and the subfolder's own index. The generated list had already fallen behind a new document. | dev24: the index is `.context/index.md`, a starter file that `init` writes and `sync-index` regenerates, holding only the packaged heading and a link to each document with its `Purpose` and `Read when` lines. The routing block sends agents to it alongside `project.md`; the starter and skills say to keep no other list; `check` reports text around the list and a `README.md` beside it, and `sync-index` stops rather than discard project text. |
| T2 | The missing-path finding fired on gitignored inputs that exist only on the analysis machine. A backticked input path was later rewritten as prose naming only its directory, the contortion `product.md` warns a false finding invites. Rewording the finding would not help: it would repeat on every run. | dev24: the finding skips paths the project's `.gitignore` files exclude, read without running Git. |

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

- After dev25 reaches T2 by upgrade: whether the session restores the context
  skill before following its steps, offers instruction-file sections in the
  packaged wording, and moves the hand-written index list when `check` reports
  the old `README.md` beside the new index; then whether the context stays
  current state for two weeks, measured by compact-file length, index length,
  and the density of defensive words outside the product, from a baseline taken
  at handback.
- The first upgrade from dev25 onward where the user also asks for the install:
  whether the session uses the recorded upgrade command or finds the source,
  and never installs the package by name from a public index.
- A cold-start test before handback, on a scratch clone and only with the
  colleague's agreement to other providers: fresh sessions in two or three
  harnesses, each given the same three prompts (the current state and next
  step; an exploratory analysis change; a status note for a collaborator).
  Record files read and in what order, whether a skill announced itself, and the
  author's score of each answer. This is the fixed-questions outcome measure
  `.context/project.md` lists as a candidate; T2's handback is the one chance to
  get a before.
- Colleague trials and further author trials, recorded under the rules above:
  whether skills are found without being named, whether exploratory work stays
  cheap, whether the report lines prompt anything, and whether context upkeep
  costs less than it returns.
- Whether an untuned project's `0 of 3` line prompts tuning without a request,
  and whether tuned descriptions improve automatic selection.
- The scenario table above in clean Codex and Copilot Chat sessions.
- A CI matrix across the declared Python range and operating systems.
