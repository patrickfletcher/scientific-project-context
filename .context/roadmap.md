# Roadmap

Purpose: explain the order of the next few product moves.
Read when: planning beyond the current task.
Update when: trial evidence changes the sequence or a real release effort begins.

## Now - Hold the Surface Still and Run a Colleague Trial

The shipped surface is frozen for the trial: the six starter files, the three
skills, the three commands, the report fields, and the check identifiers. A
colleague's session must measure the product, not a version that moved under
them, and changing any of it mid-trial also invalidates what the trial observed.

Two exceptions, and nothing else: a defect that blocks a colleague from working,
and wording a colleague reports as wrong or misleading. Record both, and the
version they landed in, because they are trial evidence.

Resist improvements during this period. The cheapest way to waste the trial is
to act on the first piece of feedback before the rest arrives.

## Next - Read the Trial Before Deciding Anything

`.context/evaluation.md` owns what to record. The questions that matter
are whether the skills are found and followed without being named, whether
exploratory work stays cheap, whether the summary lines prompt anything, and
whether context maintenance costs less than it returns.

The open product questions wait for that evidence: whether
`spctx-public-writing` earns its permanent place, and which of the remaining
candidates listed under Unresolved Questions in `.context/project.md` is worth
its cost. Each needs a reason from the trial rather than from this repository's
own reasoning.

Retain the no-hook baseline. Pilot the read-only session-start health hook only
if the trial shows structural failures going unnoticed.

## Later - Supported Distribution

Choose the public namespace and package name, test the declared Python and
platform range, and define compatibility, upgrade, support, and security
expectations. Public claims remain limited to the evidence actually retained.

Historical plans remain recoverable from version control; they are not a live
backlog.
