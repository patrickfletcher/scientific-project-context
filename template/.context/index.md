# Context Index

Purpose: list every context document in this project and when to read it.
Read when: at the start of work, alongside `.context/project.md`, to choose what else a task needs.
Update when: never by hand; `spctx sync-index` regenerates this file when a document under `.context/` is added, renamed, or removed, or its opening lines change.

`.context/project.md` holds the project's current state and `.context/scientific-practice.md` its scientific safeguards. Every other Markdown file under `.context/`, in any folder, is linked below with the `Purpose` and `Read when` lines from its top; a file missing either is listed by its link alone.

To add a document, create it under `.context/` with `Purpose`, `Read when`, and `Update when` lines at the top, then run `spctx sync-index .`. Context describes the project as it is now: a file that is not current context belongs elsewhere in the repository, and history belongs in Git.

<!-- BEGIN GENERATED CONTEXT INVENTORY -->
*No other context documents yet.*
<!-- END GENERATED CONTEXT INVENTORY -->
