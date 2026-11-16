---
name: spctx-public-writing
description: Write or revise text for readers outside the immediate work, using only facts the project can support. Use when asked to write or update a README, user or contributor documentation, a methods or results section, a figure or table caption, a status report, release notes, an abstract, or manuscript text — for example "update the README", "write up the results", "draft the methods", "explain this for collaborators", "prepare this for the paper". Do not use for internal context documents, code comments, or commit messages.
---

# Public Writing

Purpose: turn confirmed project facts into text a specific reader can use, without overstating evidence or leaking internal detail.
Use when: writing or revising a README, user or contributor guide, methods or results text, figure or table caption, collaborator report, release notes, abstract, or manuscript section.

Before acting, say that you are using `spctx-public-writing` and name the reader
you are writing for. If the reader is not clear, name the one you assume and
continue. The user can correct it.

## 1. Name the Reader and What They Must Do

Public text fails when it is written for the repository instead of a person.
State in one line each:

- **Who reads this**: a new user, an external collaborator, a reviewer, a reader
  of the paper, a future maintainer, or the authors themselves.
- **What they already know**: the field and methods they understand, and the
  project vocabulary they do not.
- **What they must do afterward**: run it, judge a claim's evidence, reuse the
  data, reproduce a figure, or decide whether to read on.

Different readers need different documents. Do not merge a user guide, a methods
description, and a status report into one file because they describe the same
work.

## 2. Establish the Project's Stage

How much a sentence may claim depends on where the work is.
`.context/scientific-practice.md` defines the levels and what each one owes:
exploratory, depended on, and published. Read `.context/project.md` for the
current evidence and limits. Then name the level of the text you are writing.

Public text most often goes wrong by claiming more than the work's level
supports. If nothing depends on a result yet, describe it; do not conclude from
it. "We found" and "these data are consistent with" are different claims.

Publishing is a decision to depend on a result. If a draft would move a result
to a level it has not earned, that is a scientific change, not a wording choice.
Hand it to `spctx-scientific-change`.

## 3. Write Only From Confirmed Facts

Draft from `.context/project.md`, the context documents its index lists, the
code, and existing public documentation. Do not infer a result, a number, or a
mechanism that the project does not state.

- Mark anything unconfirmed. Do not smooth it into the prose.
- Cite only sources checked with `spctx-literature` at the depth the text
  claims. Never cite a reference from memory.
- Do not restate a number the project has not recorded. If a count, tolerance,
  or effect size is needed and absent, ask, or leave it open.
- Link to the source of a fact rather than copying it. Once a public document
  holds a fact, internal context links to it.

## 4. Keep Each Fact in One Place

Public documentation holds purpose in plain language, setup, commands, and
outputs. Agent instructions hold operational rules. Project context holds
scientific purpose, current state, findings, risks, and open decisions. Write
each fact where it belongs, and link to it from the others.

Check for two common leaks:

- **Internal detail in public text**: agent-only rules, internal vocabulary, or
  repository mechanics that a reader does not need.
- **Transient counts in durable text**: test totals, row counts, file counts, or
  verification tallies that change with the next run. Put them in a generated
  run summary, or give the date and input they describe.

## 5. Write in Ordinary Language

A collaborator's text should also be readable by an interested outsider in the
field.

- Lead with the question, what was measured, the result, and the main limit.
  Implementation detail comes after.
- Use ordinary scientific and engineering English. Do not bring in vocabulary
  from a tool, template, or internal discussion.
- Define abbreviations and specialized statistical terms on first use. Explain
  detail in familiar words; do not remove useful scientific or statistical
  precision to shorten a sentence.
- State each limit once, where it belongs.
- Keep exact identifiers, paths, and schema names in code blocks, tables, or
  methods notes. Use plain labels in narrative text and figure captions.
- Give units, biological or experimental replication, and repeated-measure
  structure wherever a number could be misread.

## 6. Keep It True to the Implementation

Public text goes stale faster than internal context, because nothing forces it
to change. Before you finish:

- Check every command, path, filename, and option against the current code.
  `spctx check` reports paths and links in `README.md` and `docs/` that are not
  there.
- Check that the described outputs still exist and are produced the stated way.
- Remove or update anything that describes behavior that has changed.

If a described behavior is wrong rather than stale, that is a scientific or
implementation finding, not a wording problem. Report it.

## 7. Leave These Judgments to the User

Draft, but do not decide. The user confirms:

- claims, their strength, and their domain;
- authorship, credit, acknowledgement, and citation;
- licensing, data availability, embargo, and access;
- ethics, consent, governance, and community permissions;
- support and maintenance commitments.

Say in your reply which of these you drafted for the user to decide. A draft in
progress needs no review marker. A clean repository, a passing pipeline, or a
well-written paragraph does not make a claim true.

## 8. Report

Say which reader you wrote for and which facts you used. Then say what you
marked as unconfirmed, what you found stale or wrong, and which judgments still
need the user's decision.
