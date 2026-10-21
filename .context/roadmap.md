# Roadmap

Purpose: explain the order of the next few product moves.
Read when: planning beyond the current task.
Update when: trial evidence changes the sequence or a real release effort begins.

## Now - Upgrade T2 to dev25 and Watch It

dev23 and dev24 carry the response to the first colleague trial; dev25 adds
safe install guidance to the upgrade.
`.context/evaluation.md` maps each T2 observation to its change, and
`.context/product.md` holds the resulting rule that context records current
state.

T2 has already taken dev23 and overhauled its own context, so the upgrade
tests two things: whether the session restores the context skill before
following its steps and takes instruction-file lines from the packaged file, and
whether the context then stays current state. `.context/evaluation.md` names the
measure. T2's index is still a `README.md` in `.context/` holding a hand-written
list, so the upgrade is also the first real case of `check` reporting that file
beside the new `index.md` and the session moving its text before deleting it.

Before T2 returns to the colleague: install dev25 by hand, because T2's older
skill has no install guidance; run the upgrade in a fresh session that is
told only the skill and the mode, record the baseline the measure needs, and, if
the colleague agrees to other providers seeing the repository, run the cold-start
prompts in `.context/evaluation.md` on a scratch clone in two or three harnesses.

Hold the rest still while that runs: the seven files, three commands, report
fields, and check identifiers. Record which version each trial runs.

## Next - The Remaining Trial Questions

Whether skills are found without being named, whether the summary lines prompt
anything, whether `spctx-public-writing` earns its place, and which candidate
listed under Unresolved Questions in `.context/project.md` earns its cost. Each
needs a reason from a trial rather than from this repository's own reasoning.

Retain the no-hook baseline. T2's failures were in prose, which a structural
hook cannot see.

## Later - Supported Distribution

Choose the public namespace and package name, test the declared Python and
platform range, and define compatibility, upgrade, support, and security
expectations. Public claims remain limited to the evidence actually retained.

Historical plans remain recoverable from version control; they are not a live
backlog.
