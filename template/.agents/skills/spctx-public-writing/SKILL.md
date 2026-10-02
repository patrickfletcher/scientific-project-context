---
name: spctx-public-writing
description: Write or revise text for readers outside the immediate work, using only facts the project can support. Use when asked to write or update a README, user or contributor documentation, a methods or results section, a figure or table caption, a status report, release notes, an abstract, or manuscript text — for example "update the README", "write up the results", "draft the methods", "explain this for collaborators", "prepare this for the paper". Do not use for internal context documents, code comments, or commit messages.
---

# Public Writing

Purpose: turn confirmed project facts into text a specific reader can use, without overstating evidence or leaking internal detail.
Use when: writing or revising a README, user or contributor guide, methods or results text, figure or table caption, collaborator report, release notes, abstract, or manuscript section.

Before acting, say that you are using `spctx-public-writing` and name the reader
you are writing for. If you cannot name the reader, ask.

## 1. Name the Reader and What They Must Do

Public text fails when it is written for the repository instead of a person.
State, in one line each:

- **Who reads this** — a new user, an external collaborator, a reviewer, a
  reader of the paper, a future maintainer, or the authors themselves.
- **What they already know** — the field and methods they can be assumed to
  understand, and the project-specific vocabulary they cannot.
- **What they must be able to do afterward** — run it, judge whether the
  evidence supports the claim, reuse the data, reproduce a figure, or decide
  whether to read further.

Different readers need different documents. Do not merge a user guide, a
methods description, and a status report into one file because they describe
the same work.

## 2. Establish the Project's Stage

How much a sentence may claim depends on where the work actually is.
`.context/scientific-practice.md` defines the levels and what each one owes:
exploratory, supporting a decision or claim, and public or published. Read
`.context/project.md` for current evidence and limits, then name the level the
text is being written at.

Writing above the level the work has reached is the common way public text goes
wrong. Something nothing depends on yet may be described, not concluded from.
"We found" and "these data are consistent with" are different claims.

Publishing is itself a promotion. If drafting would move a result to a level it
has not earned, that is a scientific change rather than a wording choice; hand
it to `spctx-scientific-change` instead of settling it in prose.

## 3. Write Only From Confirmed Facts

Draft from `.context/project.md`, its focused sources, the code, and existing
public documentation. Do not infer a result, a number, or a mechanism that the
project does not state.

- Mark anything unconfirmed rather than smoothing it into the prose.
- Do not restate a number the project has not recorded. If a count, tolerance,
  or effect size is needed and absent, ask or leave it explicitly open.
- Prefer linking an authoritative source over copying it. Once a public
  document is authoritative, internal context links to it instead of keeping a
  shadow copy.

## 4. Keep Each Fact in One Place

Public documentation owns purpose in plain language, setup, commands, and
outputs. Agent instructions own operational constraints. Project context owns
scientific purpose, current state, evidence, risks, and open decisions. Write
the fact where it belongs and link from the others.

Two specific leaks are common and worth checking for by name:

- **Internal detail in public text** — agent-only constraints, internal
  vocabulary, or repository mechanics a reader does not need.
- **Transient counts in durable text** — test totals, row counts, file counts,
  or verification tallies that will be wrong after the next run. Put them in a
  generated run summary, or state them with the date and input they describe.

## 5. Write in Ordinary Language

Anything a collaborator reads should also be readable by an interested outsider
in the field.

- Lead with the question, what was measured, the result, and the important
  limitation. Implementation detail comes after.
- Use ordinary scientific and engineering English. Do not import vocabulary from
  a tool, template, or internal discussion into text with its own terms.
- Define abbreviations and specialized statistical terms on first use. Explain
  detail in familiar language rather than removing it; do not strip useful
  scientific or statistical precision to make a sentence shorter.
- State each limitation once, where it belongs, rather than repeating it in
  every section.
- Keep exact identifiers, paths, and schema names in code blocks, tables, or
  methods notes where reproducibility needs them. Use plain labels in narrative
  text and figure captions.
- Give units, biological or experimental replication, and repeated-measure
  structure wherever a number could otherwise be misread.

## 6. Keep It True to the Implementation

Public text goes stale faster than internal context because nothing forces it to
change. Before finishing:

- Check every command, path, filename, and option against the current code.
- Check that described outputs still exist and are still produced the stated way.
- Remove or update anything describing behavior that has since changed.

If a described behavior turns out to be wrong rather than merely stale, that is a
scientific or implementation finding, not a wording problem. Report it.

## 7. Leave Judgment With Its Owner

Draft, but do not decide. The following remain review-required until the
responsible person confirms them:

- claims, their strength, and their domain
- authorship, credit, acknowledgement, and citation
- licensing, data availability, embargo, and access
- ethics, consent, governance, and community permissions
- support and maintenance commitments

Keep generated public text visibly draft until the relevant facts and
consequential judgments are confirmed. A clean repository, a passing pipeline,
or a well-written paragraph does not make a claim true.

## 8. Report

Say which reader you wrote for, which facts you used, what you marked as
unconfirmed or draft, what you found stale or wrong, and which judgments still
need the author's decision.
