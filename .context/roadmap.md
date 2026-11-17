# Roadmap

Purpose: explain the order of the next few product moves.
Read when: planning beyond the current task.
Update when: trial evidence changes the sequence or a real release effort begins.

## Now - Observe dev27 in Ordinary Work

Bring the author's trial repositories directly to dev27, then continue their
normal work. The [evaluation plan](evaluation.md#next-useful-evidence) defines
the observations and the short trial period. Use what it shows to choose the
next change and whether to extend the trials.

Keep the packaged guidance and CLI stable during this observation period,
apart from fixes for blocking problems. Root planning and context can be
updated separately, without a package version bump.

## Next - The Remaining Trial Questions

Use the trial findings to prioritize the unresolved questions in
[project.md](project.md#unresolved-questions). Investigate a recurring failure
when a focused comparison could change a product decision.

Retain the no-hook baseline. T2's failures were in prose, which a structural
hook cannot see.

## Later - Supported Distribution

Choose the public namespace and package name, test the declared Python and
platform range, and define compatibility, upgrade, support, and security
expectations. Public claims remain limited to the evidence actually retained.

Historical plans remain recoverable from version control; they are not a live
backlog.
