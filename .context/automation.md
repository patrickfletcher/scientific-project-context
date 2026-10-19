# Automation Boundary

Purpose: define the installable product mechanics and the judgments they must
not automate.
Read when: changing a command, packaged resource, health check, report contract,
or distribution boundary.
Update when: a public tool effect, safety guarantee, report field, or release
boundary changes.

## Responsibility Boundary

Automate only repository-observable mechanics: explicit paths and commands,
file bytes, exact markers, bounded Markdown regions, and declared report fields.
People and relevant scientific, domain, project, data, or community authorities
retain decisions about meaning, adequacy, permission, and claims.

A clean report means only that the checked structure is coherent enough for
review. It does not establish scientific validity, reproducibility, legal or
ethical adequacy, licensing or governance adequacy, release readiness, or
publication readiness.

## Product Commands

| Command | Role | Boundary |
| --- | --- | --- |
| `spctx init` | Infer new/retrofit mode, install the exact six-file starter including three canonical Agent Skills, optionally add `.claude/skills/` pointer skills with `--claude`, retain occupied regular files, and report the activation and semantic handoff. | Never overwrites or merges project instructions or occupied skills and never initializes scientific meaning; unsafe structure blocks. |
| `spctx check` | Report starter integrity, scientific-practice core integrity, Agent Skill structure, pointer-skill agreement, context-index integrity, review markers, and compact routing guidance. | Read-only; does not judge project meaning, prose adequacy, or repository organization. |
| `spctx sync-index` | Create or synchronize only the marked generated inventory for discoverable current context, including bounded self-routing summaries. | Derives summaries only from current regular UTF-8 files and does not write routing prose, project meaning, or scientific claims. |

`tools/check_package_artifacts.py` is the only repository-only product tool. It
checks built wheel/sdist membership, metadata, resource identity, and direct
versus sdist-built wheel parity. It is a maintainer verification tool, not part
of the installed CLI.

## Filesystem Safety

Initialization is previewable and never overwrites an occupied regular starter
path. New mode requires a missing or empty target. Retrofit mode fills safe
gaps, retains existing regular files byte-for-byte, and defers a missing
`AGENTS.md` when installing it would activate retained unreviewed practice or
skill content. Plans carry immutable packaged and observed bytes, revalidate
before writing, create exclusively, and roll back only effects owned by the
operation.

The canonical `spctx-project-context` and `spctx-scientific-change` procedures
are required starter files under `.agents/skills/`. Each `SKILL.md` contains
portable `name` and `description` YAML frontmatter followed by its complete
procedure. Initialization and health validate this bounded structure, including
the directory-matching name, but do not interpret the prose. Existing skill
bytes are retained and reported for review.

`--claude` additionally plans one generated pointer per skill under
`.claude/skills/`, because Claude Code reads no path under `.agents/`. A pointer
carries the description of the skill this project will actually have — the
retained project-owned one where it exists, so tuned triggers propagate — and a
body that routes to the canonical file. Pointers follow every rule the starter
files follow: previewable, exclusive creation, never overwritten. No procedure
body is ever duplicated, and `DH-SKILL-004` reports a pointer whose description
or route no longer agrees with its skill. Apart from this bounded pointer, no
alternate skill root or second procedure location is generated or managed.

Index synchronization changes only the exact generated inventory block. It
preserves human-authored bytes and line endings, blocks malformed or ambiguous
markers and unsafe paths, and revalidates observed paths and routing summaries
before replacement. Discovery and apply-time revalidation share one predicate,
`is_discoverable_owner_path`, which accepts any
Markdown file directly under `.context/` other than the managed starter files,
and any Markdown file in `.context/active/`. Keeping one rule is deliberate:
when these were written twice they drifted, and every custom root-level context
document planned cleanly and then failed on apply. A complete entry contains the
source path and normalized, 280-character-bounded `Purpose`, `Read when`, and
`Update when` values from the first 20 lines. Incomplete guidance yields the
existing `DH-GUIDE-001` warning and a path-only entry. Dry-run reports include
the exact planned UTF-8 content and digest.

## Routing Block Version

The managed `AGENTS.md` routing block stays at v1 even though dev17 added a
third skill. The block routes to the two context files and the procedures that
maintain them; `spctx-public-writing` has no context file of its own and is
discovered natively from `.agents/skills/` by both supported harnesses. Bumping
the marker would make every existing project's route read as absent and invite
duplicate blocks, which is a real migration cost for no behavioral gain.

dev23 rewrote the block's update rule after T2 and kept v1 for the same reason.
An adopting project's older block reads as modified, which `check --diff` shows
and the `upgrade` mode replaces; its practice core reads the same way until
restored.

## Report Scope

Setup state appears in `check` as summary lines, not findings: whether the route
is present, how many starter prompts remain, and the other state lines below.
`check` keeps the `DH-PRACTICE-001` observation, because silent modification of
the versioned scientific-practice core is an ongoing risk rather than a setup
step. Every package version that changes the core also produces it in each
adopting project, so since dev23 its text names a package update as one cause
and points to the core `init --dry-run` prints, instead of asking the project to
review changes it never made. Its kind stays `broken` while the report fields
are held still for the trials.

The context-adoption block appears only in the `init` report, where activation
is the subject. Human `check` output carries the state lines, observations, and
the validation boundary; resource and skill digests stay in `--json`.
Arbitrary context-document YAML is outside this interface. No current harness
source establishes frontmatter on ordinary project Markdown as a portable
knowledge-graph contract, so adding it would create a second metadata surface
without a defined consumer, schema, or validation boundary.
Portable standard-library replacement cannot promise an absolute adversarial
compare-and-swap boundary across the final filesystem call.

Health checks do not follow linked targets or treat prose heuristics as proof of
semantic adequacy. They verify only the required starter structure, exact
scientific-core and project-context routing blocks, Agent Skill structure,
pointer-skill agreement, bounded index integrity, review markers, compact
routing guidance, and context that names a repository path which is not there.
They do not score prose, repository size, document counts, decision lifecycle,
or alternate platform instruction and skill paths. File placement, persistent
agent routing, and natural-language compatibility remain distinct report states.

## Drift and State Signals

`DH-STALE-001` warns when a `.context/` document backticks a repository-relative
path that is not present. It is the only drift signal available to a read-only
structural tool, so it is deliberately narrow: the string must look like a path
with a directory and a file extension, and its top-level directory must exist,
because a reference into a tree the project does not have is describing a
possibility rather than pointing at something. The generated index is exempt;
its routes are conditional by design and its inventory is already checked. A
first pass without those two rules produced three findings on this repository
and its fixtures, all false, which is why both exist.

The report gained `practice_localization`, observing whether the project wrote
its own practice notes outside the managed core. Diffing the file against the
packaged one was tried first and read the one real adopting project as localized
when it had only adopted an earlier version, so the check looks for project
content instead: a section the package does not ship, or the packaged prompts
answered. It is a summary line and never a finding, because a project that has
settled its contract must not be told about it on every run.

`relied_on` reads one field of the compact context, `What later work relies on`,
and reports whether it names anything. That field is what decides how much
evidence a change owes, and its default is empty, so every project starts
exploratory and stays there until someone decides otherwise. An earlier
`stated_levels` grepped the whole file for the three level names instead; it
read a project that merely discussed the levels as having stated one, and said
nothing about the field the skills actually gate on. Reporting the field is what
gives promotion a moment a person can act on. It is a state line, never a
finding: an empty list is the correct state for most projects most of the time.

`starter_prompts` counts bracketed prompts still present in `AGENTS.md` and
`.context/project.md`. The starter says a prompt left in place is not an answer,
so the count is the cheapest signal that setup is unfinished. It says nothing
about the quality of the answers already written.

For new projects, the exact packaged `AGENTS.md` activates the route after
initialization. For retrofits, the report supplies the exact compact routing
block for an agent and project authority to compare and integrate; the CLI does
not edit an occupied instruction file. `check` reports the resulting route state
on every run: an absent route was previously left to `init`, which meant a
retrofit that never had the block added was told nothing was wrong.

## Check Reports State, Not a Verdict

`check` no longer classifies a project as passing or failing. It reports what
the project has set up — route, unanswered prompts, tuned triggers, practice
notes, relied-on list — and what it observed, under three kinds: `broken` for
structure the tool cannot work with, `unfinished` for a step not taken yet, and
`noted` for a state the project may have chosen deliberately. The exit code says
only whether the target could be read: `0` when it could, `2` when it could not.

The reason is the product's own boundary. A verdict invites a reader to treat
structure as approval, and the aggregate hid the individual signals that are
actually actionable. Tuning trigger phrasings, in particular, is the outcome the
system wants and was previously reported as divergence from the packaged text.

The report is at schema 14. Instruction files other than `AGENTS.md` and
`CLAUDE.md` are preserved but are not yet inspected or certified as discoverable
by the CLI.

## Harness Automation Boundary

The product currently ships no lifecycle-hook configuration or executable hook
handler. Hooks are event adapters, not an additional authority or implementation
of project context. If a project opts into a hook, it should invoke an existing
deterministic command and preserve that command's validation boundary; it must
not duplicate CLI logic or make semantic context edits.

The first candidate is a measured, opt-in `SessionStart` advisory that calls
`spctx check <target> --json`, stays silent when nothing needs attention, and
shows a compact note when the route or the starter prompts do. It
remains a pilot: no hook may be installed or trusted by default, and missing,
disabled, untrusted, timed-out, or incompatible hooks must not make the project
unusable or be reported as successful adoption.

Repository-local hook execution adds a security boundary because the host runs
the configured command with its own permissions. A productized adapter would
require explicit enablement and review, least-privilege and no-write behavior,
bounded validated input/output, short timeouts, versioned host compatibility,
and tests showing that an agent cannot silently edit then execute the handler.
Host-specific configuration remains thin; deterministic evaluation belongs in
the CLI or a directly tested shared handler.

Use ordinary pre-commit or CI integration when a project wants structural
enforcement beyond agent sessions. Because `check` now exits `0` whenever the
target could be read, such an integration must read the JSON report and decide
for itself which observations matter; the CLI deliberately declines to make that
call. Whatever it decides establishes only what the invoked command inspected.
Context freshness, instruction compatibility, scientific adequacy, and authority
remain outside the machine-checked result.

## Resource and Interface Boundary

The installed package contains one Markdown collection: the six starter files
`init` places into a project, plus `.context/README.md`, which only `sync-index`
ever writes. The package ships no example documents; people and agents create or
reuse the clearest project-specific source when recurring detail justifies it.

The managed project-context namespace is `.context/`. The CLI neither discovers
nor migrates the pre-dev13 `.design/` layout; migration requires a project-owned
directory rename and route review before the current structural checks apply.
Projects from the earlier `.agent/workflows/` prototype reinstall the current
package, preview and apply `spctx init .`, confirm the new `.agents/skills/`
files and routes, then delete the obsolete `.agent/` tree themselves. The tool
adds missing canonical files but never removes project-owned legacy files. Both
migrations affect only prototype repositories predating publication, so they are
recorded here rather than in the public README.

The supported command surface is exactly `init`, `check`, and `sync-index`.
Package modules exist to implement those commands, but no stable public Python
API or automatic migration promise is made before 1.0. Runtime code uses only
the Python standard library; Hatchling is build-only.

## Maintainer Checks

- Product tests: `python -m unittest discover -s tests`
- Syntax: `python -m compileall -q src tools`
- Starter contract: `python -m unittest tests.test_health.CLIContractTests.test_template_resource_contract_passes`
- Built artifacts: `python tools\check_package_artifacts.py --source-root . --direct-wheel <wheel> --sdist <sdist> --sdist-wheel <sdist-built-wheel>`

These checks cover shipped resources, CLI mechanics, bounded filesystem
behavior, reports, and artifact composition. They do not measure product value
or user experience.
