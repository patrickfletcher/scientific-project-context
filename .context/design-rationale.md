# Design Rationale

Purpose: preserve the small set of enduring reasons behind the current Scientific Project Context design without reviving superseded template structures.
Read when: a current product decision needs deeper justification than `.context/product.md` provides.
Update when: evidence changes one of these rationales or a rejected approach becomes viable for a new reason.

This is rationale, not current operating policy or empirical proof. Current behavior lives in active context, product files, code, and tests.

## Why the Default Is Six Files

The starter needs one automatically encountered authority file, one stable scientific-practice contract, one compact current project view, and on-demand procedures for the recurring tasks that carry the most risk: establishing context, changing scientific behavior, and writing for readers outside the work. Empty plans, decision registers, indexes, validation matrices, and release documents create reading and maintenance burden before their benefit exists.

A default file is justified only when it prevents a high-impact early failure or repeatedly improves early work more than it costs. Optional context grows from observed pressure rather than project type or maturity labels.

## Why Context Documents Carry No YAML Frontmatter

Agent Skills need `name` and `description` frontmatter because a defined consumer reads those fields for routing. The files under `.context/` have no such consumer. They keep visible `Purpose`, `Read when`, and `Update when` lines instead, because no reviewed cross-harness standard gives arbitrary project Markdown knowledge-graph semantics, and a schema with no reader is maintenance without benefit.

Add IDs, relationship types, or other machine metadata only when a concrete consumer and query justify a versioned schema. Ordinary Markdown links and the generated context index remain the portable navigation layer.

## Why Context Is Adaptive

Simple analyses and maintained scientific libraries need different amounts of durable context, but they can share the same entry point. Facts remain in `.context/project.md` until they persist across sessions, update independently, and materially harm its scanability. Existing issue trackers, public docs, data dictionaries, test plans, and scientific specifications remain authoritative when they already work.

This avoids both extremes: a universal documentation tree and an unstructured project notebook. Navigation is added only after several focused sources make selection non-obvious.

## Why Activation Is a Route, Not a Rewrite

Installed files cannot maintain themselves unless an agent is reliably directed to them. A new project can adopt the packaged `AGENTS.md`; a retrofit instead needs explicit authority to add one compact project-context route to an instruction surface that its agents actually discover. Replacing an existing instruction file would risk erasing project knowledge, while installing unreferenced files would create false adoption. The honest fallback is manual activation, not a claim that file presence is enough.

The instruction surface is project-specific, but the underlying context and canonical Agent Skills remain authoritative. Bootstrap therefore needs to discover the surfaces the project's agents actually use and integrate only the compact route with project approval, rather than install parallel copies of the guidance.

## Why History Is Not a Context Layer

Current context should answer what is true and useful now. Rationale and evidence receipts remain in `.context/` only while they support a live rule or claim; superseded plans, completed work, and stale records remain recoverable from Git history instead of occupying a routinely discoverable archive. Historical material is consulted only to reconstruct a disputed decision or missing fact, and it never overrides current sources by age or volume.

## Why Scientific Checks Sit Beside Work

Scientific risk is easiest to miss when implementation appears mechanically successful. Material work therefore names the main failure mode and the smallest executable check capable of exposing it, including the expected result, tolerance, property, or failure signal. Evidence records retain enough identity and limits to explain what was actually observed and what becomes stale after a relevant change.

Tests and generated output are not automatically scientific evidence. Protected inputs, curated decisions, model meaning, calibration, validation status, and claims remain review-owned.

## Sources Behind the Practice Contract

The practice core draws on recurring cross-domain guidance. These sources justify the questions it asks; they are not evidence that the product answers them, and they do not replace field-specific methods, institutional policy, or research-integrity review.

- The [National Academies' reproducibility report](https://doi.org/10.17226/25303) separates computational reproducibility, replicability, and generalizability, which is why the contract asks what a check establishes and never treats rerunnability as correctness.
- The [ALLEA European Code of Conduct](https://doi.org/10.26356/ECOC) treats data, protocols, code, and other research materials as research results, which is why authority, chronology, corrections, and limitations are preserved rather than only code quality.
- [FAIR](https://doi.org/10.1038/sdata.2016.18), [FAIR for Research Software](https://doi.org/10.15497/RDA00068), and the [Software Citation Principles](https://doi.org/10.7717/peerj-cs.86) are why identity, provenance, credit, and access surface at a real handoff or release rather than on day one.
- The [CARE principles](https://www.gida-global.org/careprinciples) are why technical access never implies permission, and why FAIR is never flattened into open by default.
- [Good Enough Practices in Scientific Computing](https://doi.org/10.1371/journal.pcbi.1005510) and [Ten Simple Rules for Reproducible Computational Research](https://doi.org/10.1371/journal.pcbi.1003285) are why the contract asks for protected raw data, recorded transformations and manual steps, and a route from claims to results, at the smallest useful cost.

## Why Automation Is Narrow

Deterministic tools are useful for exact resource identity, safe placement, read-only structural reports, and bounded marker updates. They cannot infer project meaning, decide that another document is warranted, confirm scientific content, or turn structural consistency into release readiness.

The package therefore prefers preview, exclusive creation, explicit selection, stable report boundaries, and refusal on ambiguity. Project files become project-owned snapshots; automatic semantic migration would require a separately justified design.

## Why Evidence Claims Are Layered

Static tests can support mechanical claims. Observed use can expose instruction-following behavior. Human ease requires human observation, domain adequacy requires domain review, and transfer claims require external projects. Evidence changes product policy only when its provenance, observation boundary, limitations, and relevance to the decision are explicit.

## Superseded Approaches

The following approaches were deliberately retired:

- a default tree of active files and inactive stubs,
- demand-profile or project-phase classification during onboarding,
- inbox promotion and mandatory task/decision/archive choreography,
- preinstalled platform-specific instruction files,
- global append-only validation narratives,
- structural health as a proxy for scientific or release readiness, and
- retaining historical artifacts after their useful rule or evidence was absorbed elsewhere.

Reintroduce one only from new observed need, not because it appeared in historical reports.
