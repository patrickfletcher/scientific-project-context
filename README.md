# Scientific Project Context

A coding agent learns most of what it knows about your project from the files
it can read. Scientific Project Context gives it an organized place to look: a
few plain Markdown files in the repository that record what the project is
for, how to run it, which data and decisions must not change, where the work
stands, and what is still undecided.

It has three parts:

- **Instructions and skills for agents.** `AGENTS.md` and three
  [Agent Skills](https://agentskills.io/) (procedures an agent loads when a
  task calls for one) tell agents where the project's context lives, when to
  update it, and how to handle the moments that need more care.
- **A `.context/` folder** for the project's own documents. It starts with a
  one-page project summary and a short agreement on scientific practice, and
  grows only when a topic needs a document of its own.
- **`spctx`**, a small command-line tool that adds the starter files without
  overwriting anything and reports what's set up.

All three are meant mainly for agents to use. The aim is for the project's
facts and rules to build up in a controlled way as the work goes on, each kept
in one place where it's easy to find, with agents doing the upkeep as part of
ordinary work rather than as a separate documentation chore. You keep the final
say on how it all evolves: everything is plain Markdown in your repository, so
you can edit it yourself, though usually you'll just ask your agent.

> **Early prototype, shared for feedback.** See [Status](#status) for what has
> and hasn't been tested.

## Getting started

You need Python 3.10–3.14, Git, and a coding agent such as GitHub Copilot in
VS Code, Codex, or Claude Code.

**1. Install `spctx`.** Any Python environment works; a fresh
[virtual environment](https://docs.python.org/3/tutorial/venv.html) keeps it
out of the way.

```sh
python -m pip install git+https://github.com/patrickfletcher/scientific-project-context.git
```

**2. Add the starter files to your project.** Preview first, then apply:

```sh
spctx init path/to/your-project --dry-run
spctx init path/to/your-project
```

Existing files are never overwritten. If your project already has an
`AGENTS.md`, `init` leaves it alone and prints a short block to add to it;
step 3 covers that, with your approval. If you use Claude Code, add `--claude`
to these commands (see [Which agents it works with](#which-agents-it-works-with)).

When it finishes, the report names the Python interpreter `spctx` ran from.
Copy that path for the next step.

**3. Ask your agent to set things up.** Open the project with your coding agent
and ask:

```text
Use the spctx-project-context skill to set up this project's context.
spctx is in the environment at <the Python path from the init report>.
Tell me what needs my review when you're done.
```

The skill tells the agent to read through the project first, fill in the
starter files from what it finds, and ask you only about what it can't work out
for itself, such as what a result means or which inputs must never change. Read
what it wrote and correct anything that's off.

That's the whole setup.

## After setup

Mostly, you just work. `AGENTS.md` tells each agent to read
`.context/project.md` first, and to rewrite the affected part of the context in
place when the work changes something that matters later, such as a new
protected input, a changed answer, or a result that something now depends on.

The context describes the project as it is now and relies on Git for its
history. Keep logs of runs, changes, and approvals out of it: they bury the
current answer, and Git already records what changed and when.

Three skills cover the moments that need more care:

- **`spctx-project-context`**: setting up the context, refreshing it when it
  falls behind, giving a growing topic its own document, or retiring one that's
  no longer useful.
- **`spctx-scientific-change`**: changes that could alter a result, such as an
  exclusion rule, a filter cutoff, or a model refit. It asks the agent to name
  the main way the change could go wrong and, once something depends on the
  result, the smallest check that would catch it.
- **`spctx-public-writing`**: text for readers outside the work, such as a
  README, a methods section, or a figure caption, drafted only from facts the
  project can support.

Each skill has the agent say which one it's following, so you can tell whether
it was used. If an agent misses one, name it in your request.

The context is yours to curate. Edit it by hand, or just tell your agent what
you want:

- "Record that everything in `data/raw/` is original instrument output and must
  never be modified."
- "We're excluding recordings shorter than ten minutes from now on. Update the
  context."
- "The calibration notes have outgrown the summary. Give them their own
  document."

Exploratory work stays light: the agent tells you in its reply what it did and
that the result is provisional, and the context changes only when an answer
does. Checks and evidence come due once a result starts to support a decision or
a claim, or goes public.

## What gets added

```text
AGENTS.md                                          instructions for agents
.context/index.md                                  the list of context documents
.context/project.md                                the project summary
.context/scientific-practice.md                    the scientific-practice agreement
.agents/skills/spctx-project-context/SKILL.md      set up and maintain the context
.agents/skills/spctx-scientific-change/SKILL.md    changes that could affect a result
.agents/skills/spctx-public-writing/SKILL.md       writing for readers outside the work
```

`project.md` starts as a set of prompts (purpose, current work, protected
inputs, main risks, evidence, open questions) that the agent replaces with
what's true for your project, marking what isn't known.
`scientific-practice.md` is a general agreement on scientific practice: who
decides what results mean, protecting raw and curated data, recording
provenance and uncertainty, and not claiming more than the evidence supports.
Below its shared part is a section for your field's own standards, which your
agent can draft from a protocol or reporting guideline you already follow.

Beyond these, `.context/` is yours to organize, in whatever folders suit the
project. When a topic outgrows the summary, such as a calibration procedure or a
list of analysis decisions, an agent can give it its own document and mark it
for review until you've confirmed it. `.context/index.md` links every document
under `.context/` with a line on when to read it. It is generated: `spctx
sync-index` rewrites it when documents are added, renamed, or removed, so don't
edit it by hand or keep a second list elsewhere.

## Which agents it works with

The skills live in `.agents/skills/`, where
[Codex](https://developers.openai.com/codex/skills/) and
[GitHub Copilot in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
look for them. Claude Code doesn't, so adding `--claude` to `spctx init` places
small pointer files under `.claude/skills/` that lead to the same skills.
Recent versions of Claude Code read `AGENTS.md` unless the project has a
`CLAUDE.md`; if yours does, the init report suggests adding an `@AGENTS.md`
line to it. With other agents, ask them to read `AGENTS.md` at the start of a
session.

## The `spctx` command

After setup, agents run these as they work (`AGENTS.md` tells them how), but
you can run them yourself too.

| Command | What it does |
| --- | --- |
| `spctx init <project>` | Adds any missing starter files and never overwrites existing ones. `--dry-run` previews; `--claude` adds the Claude Code pointers. |
| `spctx check <project>` | Reports what's set up and what isn't yet, without changing anything. It describes the project rather than grading it. `--json` gives the same report in machine-readable form. |
| `spctx sync-index <project>` | Regenerates `.context/index.md`, the list of context documents. `--dry-run` previews. |

Add `--help` to any command for its options.

To update to a newer version, rerun the install with `--upgrade`:

```sh
python -m pip install --upgrade git+https://github.com/patrickfletcher/scientific-project-context.git
```

Then ask your agent to use the spctx-project-context skill to bring the project
up to date. It compares your files with the new version and reports what it
changed.

## Trying it out

We're looking for feedback on usage in real projects. Use it the way you normally
work. Don't tidy anything up for its benefit, and after setup, don't name a
skill unless the agent fails to find one: whether it finds the right one by
itself is part of what's being tested.

The most useful things to hear about, roughly in this order:

- where it got in the way, or asked for more work than the result was worth
- anything it asked you to write that you didn't think was worth writing
- whether the agent picked the right skill without being told, and said which
  one it was using
- wording that's wrong, misleading, or not how people in your field talk
- anything you had to correct more than once
- experience in repos using .claude/skills/ and CLAUDE.md - currently untested

The tool is being held steady during these trials so that everyone sees the
same thing. Small fixes for anything that blocks you or reads wrongly will go
in as they come up; bigger changes wait until the feedback is in.

## Status

This is an experimental prototype. It isn't on PyPI, and its commands and files
may still change.

- It has only been tested with CPython 3.10 and 3.11 on Windows. The rest of
  the declared 3.10–3.14 range, macOS, and Linux are untested.
- The design was shaped by uncontrolled use in one real scientific repository.
  Whether it makes projects easier to pick up, keeps agents on track, or
  improves reproducibility hasn't been established.
- Whether agents choose the right skill without being told hasn't been tested
  in controlled sessions.
- `spctx check` looks at structure only. A clean report doesn't mean the
  science is right, that data may be shared, or that anything is ready to
  publish. Those calls stay with you and the people responsible for the work.

## Learn more

This repository uses the system on itself, so its
[project context](.context/project.md) is a working example, though for a
software tool rather than a lab or analysis project. The
[starter files](template/), [CLI source](src/scientific_project_context/), and
[tests](tests/) show exactly what ships and how it's checked.

Background reading behind the practice agreement:
[Good enough practices in scientific computing](https://doi.org/10.1371/journal.pcbi.1005510),
[The Turing Way's definitions](https://book.the-turing-way.org/reproducible-research/overview/overview-definitions.html)
of reproducibility and replication, and the
[CARE Principles for Indigenous Data Governance](https://www.gida-global.org/careprinciples).

## License

[MIT](LICENSE)
