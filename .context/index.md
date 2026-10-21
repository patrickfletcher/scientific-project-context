# Context Index

Purpose: list every context document in this project and when to read it.
Read when: at the start of work, alongside `.context/project.md`, to choose what else a task needs.
Update when: never by hand; `spctx sync-index` regenerates this file when a document under `.context/` is added, renamed, or removed, or its opening lines change.

`.context/project.md` holds the project's current state and `.context/scientific-practice.md` its scientific safeguards. Every other Markdown file under `.context/`, in any folder, is linked below with the `Purpose` and `Read when` lines from its top; a file missing either is listed by its link alone.

To add a document, create it under `.context/` with `Purpose`, `Read when`, and `Update when` lines at the top, then run `spctx sync-index .`. Context describes the project as it is now: a file that is not current context belongs elsewhere in the repository, and history belongs in Git.

<!-- BEGIN GENERATED CONTEXT INVENTORY -->
- [automation.md](automation.md)
  - Purpose: define the installable product mechanics and the judgments they must not automate.
  - Read when: changing a command, packaged resource, health check, report contract, or distribution boundary.
- [design-rationale.md](design-rationale.md)
  - Purpose: preserve the small set of enduring reasons behind the current Scientific Project Context design without reviving superseded template structures.
  - Read when: a current product decision needs deeper justification than `.context/product.md` provides, or a change to the scientific safeguards needs the sources behind them.
- [evaluation.md](evaluation.md)
  - Purpose: define the evidence needed to assess the product and record what real use has taught without identifying anyone.
  - Read when: interpreting checks, planning or recording a trial, or making a product effect, usability, compatibility, or release claim.
- [product.md](product.md)
  - Purpose: define what Scientific Project Context is, the outcomes it should improve, and the boundaries that keep it small.
  - Read when: changing the starter files, user journey, context rules, or product scope.
- [roadmap.md](roadmap.md)
  - Purpose: explain the order of the next few product moves.
  - Read when: planning beyond the current task.
<!-- END GENERATED CONTEXT INVENTORY -->
