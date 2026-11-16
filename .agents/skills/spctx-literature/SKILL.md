---
name: spctx-literature
description: Find, check, interpret, and cite the outside sources a project builds on — papers, preprints, reviews, datasets, software, standards, and documentation. Use when searching the literature, adding or checking a citation or reference list, taking a parameter, method, expected value, or reference dataset from published work, summarizing what is known or comparing studies, identifying a gap, or crediting reused code, data, or figures — for example "find papers on", "check this citation", "what does the literature say about", "is this value published", "summarize prior work on". Do not use for links between the project's own documents.
---

# Literature and Prior Work

Purpose: ground the project in prior work by identifying each outside source exactly, reading it for what it shows, carrying it into the project explicitly, and crediting it.
Use when: searching for, checking, interpreting, synthesizing, or citing outside sources, or taking a value, method, or expected signal from one.

Before acting, say that you are using `spctx-literature` and what the source is for.

## 1. Say What the Source Is For

Name the use: background, a value or parameter, a method, an expected signal
for a check, a comparison, or a sentence for outside readers. The use sets the
depth.

- While exploring, a quick search or a recalled reference is enough. Label it as such.
- If later work will depend on what a source says, identify the source exactly and read the part that supports the use. Do the same if text that cites it will be published.

## 2. Identify It Exactly

- Look a source up before you cite it. Never write an identifier, title, author list, year, or venue from memory as if it had been checked.
- Mark a reference you have not looked up as recalled. Do not let it support what later work depends on, or text for outside readers.
- Resolve a persistent identifier where one exists: a DOI, PubMed or PMC ID, arXiv ID, ISBN, dataset accession, software release and version, or standard number.
- Confirm that the title, authors, year, and venue match what is cited.
- Note whether it is a preprint or the published version, and which edition or software version. Check whether a retraction, correction, or expression of concern exists.
- If you cannot reach the source from here, say so and mark it unchecked. Services such as Crossref, PubMed or Europe PMC, arXiv, and DataCite answer most lookups.

## 3. Read What It Actually Shows

- Say what you read: full text, abstract, title only, or another work's account of it.
- If later work depends on the use, find the passage, table, or figure that supports it, and note where it is.
- Record the conditions that limit transfer, as relevant:
  - organism, strain, cell type, or preparation;
  - in vivo, in vitro, or model;
  - design and sample size;
  - measurement, units, and normalization;
  - method or software version, and the regime the result holds in.
- Separate what the authors measured from what they concluded, speculated, or cited from elsewhere.
- Say what kind of evidence it is: a direct measurement, evidence for a component or correlate, a model result, or a review's synthesis.
- Cite the primary source for a primary finding, and a review for its synthesis.

## 4. Carry It Into This Project Explicitly

- Say what holds here and what does not. A different species, condition, or regime is an assumption to state, not a detail to drop.
- If a published value becomes a parameter, prior, threshold, or expected signal, show any conversion. Record its source beside the setting that uses it.
- If later work depends on that value, put it on the project's list of what later work depends on. Changing it then goes through `spctx-scientific-change`.

## 5. Keep Each Source in One Place

- If the project already keeps a list of sources, use it: a bibliography file that its writing tools read, or a context document.
- Otherwise keep one list. For each source, give its identifier, what the project takes from it, how it was checked, and where it is used.
- Link to that entry; do not restate it.
- Keep quotations short. Do not commit copies of articles, figures, or datasets that the project has no right to redistribute.

## 6. Synthesize and Find Gaps Honestly

- State the scope of the search behind a synthesis: where, which terms, when, and what was included. "No study found" describes that search, not the world.
- Group findings by the conditions they hold under. Keep disagreements beside the differences that might explain them. Do not count studies as votes.
- When you link fields, name the assumption that carries a result from one to the other.
- A gap is a proposal. Give the search behind it, and keep it with the project's unresolved questions until the user adopts it.

## 7. Credit and Permission

- Cite ideas, methods, data, and software, with the version used.
- Check the licence before you reuse code, data, or figures, and keep the attribution with what was reused.
- Authorship, credit, and acknowledgement decisions stay with the user.

## 8. Report

Lead with what the sources show for the question. Then report:

- how each source was checked: full text, abstract, title, or recalled;
- what remains unchecked;
- the scope of any search;
- anything that would change a value later work depends on.
