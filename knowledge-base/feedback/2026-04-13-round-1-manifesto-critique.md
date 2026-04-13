# Round 1 — Manifesto critique — 2026-04-13

**Reviewer:** anonymous peer review
**Round:** 1
**Scope:** Full repo review at v1.0.0 — manifesto, thesis, specification, diagrams, repo hygiene
**Version reviewed:** v1.0.0

## Summary

The reviewer gave the pattern a full read and returned a structured critique across five dimensions: repo hygiene, diagram rendering, conceptual clarity, novelty framing, and evidence. The verdict was that the pattern is conceptually stronger than most AI-pattern manifestos currently circulating, but has specific practical weaknesses that could be fixed cheaply and would materially strengthen the whole project.

## Key points raised

### Repo hygiene — weak for a standards-aspirant repo
- Only six files total. Missing: `CONTRIBUTING.md`, `GOVERNANCE.md`, `CITATION.cff`, `CHANGELOG.md`, issue templates.
- `LICENSE` at the repo level says CC BY 4.0, but the specification header claims "Personal intellectual property of the author". The two contradict each other. Pick one.
- `README.md` is 69 lines, no quickstart, no "who is this for", no badges.

### Broken diagrams on GitHub
- The thesis embedded diagrams via `https://claude.ai/chat/...excalidraw` URLs — private Claude session artefacts that would never resolve for anyone else. Anyone reading the thesis on github.com would see a document with six broken images.
- Fix recommended: export `.excalidraw` → `.svg`, commit alongside, rewrite to relative `./diagrams/*.svg`. 1–2 hours, major credibility fix.

### Conceptual clarity — mixed
**Strong:**
- The six principles are named and rationalised.
- Section 2.7 openly admits the circular-gap-analysis problem.
- Section 5.1 concedes the 15% / 40% overlap thresholds are borrowed-from-antitrust guesses. That honesty is rare and valuable.

**Weak:**
- No testable claim, no conformance checklist, no anti-pattern list.
- Key terms ("Constitutional Memory", "Equilibrium Agent", "epistemic discipline") remain metaphors, not interfaces.
- **Self-migration is the load-bearing claim of the whole pattern yet is never worked through a single example.**
- Unit of analysis slips between "deployment", "org-wide estate", and "cross-company ecosystem".

### Novelty — narrower than the framing
- The thesis Section 2.8 concedes that the Equilibrium/Immune agents "are MAPE-K loops in everything but name". If true, the contribution shrinks from "new category" to "synthesis + OASF extension fields + Constitutional Memory".
- Engagement with organisational multi-agent systems (MOISE+, Jason, OperA) is a one-liner where it needs a section. These literatures directly prefigure Gaps 3 and 4.
- "Colony" invites stigmergy comparisons the paper dismisses in a single sentence.

### Evidence — essentially absent
- Zero reference implementations.
- Zero case studies.
- Zero worked examples.
- The specification runs 590 lines of prose with not one YAML or JSON fragment showing what an Agent Mirror actually looks like on disk.
- The manifesto admits this limitation but admission does not close the gap.

### Risks worth flagging
1. **"Security upgrades are always preauthorised"** — lovely until a compromised agent classifies its exfiltration channel as a "security upgrade". Needs scope definition, second-party gate, rollback path.
2. **"Autonomy is earned"** has no adjudicator — re-imports the principal-agent model the paper explicitly rejects.
3. **No cost model** — at what colony size do Mirror curation, Equilibrium monitoring, and Trust Ledger governance pay for themselves? Below that, it is microservice-era tax for monolith-era benefit.
4. **No colony-specific threat model** despite Principle 6 being "mutual defence". What happens when the Reflector is poisoned? Constitutional Memory tampered with?

## Top 5 fixes proposed by the reviewer

1. **Ship one worked example** — `examples/hello-colony/` with a filled-in Agent Mirror YAML, a post-evolution version, and a 5-agent colony snapshot with overlap declarations. Converts the repo from essay to pattern. One day's work, enormous impact.
2. **Fix the diagrams** — export `.svg`, rewrite thesis image paths to relative. 1–2 hours.
3. **Commit a schema** — `schemas/agent-mirror-v0.1.yaml` (or JSON Schema). Without it, the "OASF extension profile" claim is rhetoric; with it, it is a concrete artefact you can take to AGNTCY.
4. **Repo hygiene** — `CONTRIBUTING.md`, `CITATION.cff`, `CHANGELOG.md`, resolve the `LICENSE`/spec-header contradiction, add a "Scope and audiences" section routing practitioners, researchers, and implementers differently.
5. **Falsifiability / Conformance section** — add to the spec: (a) "You are not doing Agent Colony if…" — 5 anti-patterns; (b) 5 observable health signals; (c) 3 named failure modes (compromised Reflector, runaway Equilibrium merger, preauthorised-security abuse). Turns the manifesto into something a team can audit against.

## Verdict

> Better than most AI-pattern manifestos — current literature, genuine self-criticism, mature positioning as an OASF extension rather than a competing standard. Core weaknesses are practical, not conceptual: zero artefacts, broken figures, no schema, three audiences tangled in one repo. Fix the top five and it moves from "thoughtful essay with a GitHub repo" to "pattern you can adopt, critique, and implement against". Leave them and it stays what the manifesto itself warns against — a well-argued gap statement whose gaps stay unfilled.

## What changed in response

All five top-priority fixes were implemented in **v1.1.0** (2026-04-13):

- **Worked example:** `examples/hello-colony/` now contains 5 filled Agent Mirror YAMLs, a pre/post-evolution pair, and a colony snapshot with cross-referenced overlap declarations.
- **Diagrams:** Six Excalidraw sources exported to SVG, thesis references updated to relative `.svg` paths. Diagrams now render natively on GitHub.
- **Schema:** `schemas/agent-mirror-v0.1.json` — 657-line JSON Schema (Draft 2020-12) with a fully populated example.
- **Repo hygiene:** `CONTRIBUTING.md`, `CITATION.cff`, `CHANGELOG.md`, issue templates for challenges and refinements. License contradiction resolved — the specification now inherits the repo-level CC BY 4.0 licence.
- **Conformance section:** `specification.md` §7.5 — 5 anti-patterns, 5 health signals, 3 named failure modes with six-layer defences.

The MAPE-K concession and the related-work shortness (MOISE+, Jason, OperA, stigmergy) were heard but not yet addressed — see "What has not changed".

## What has not changed and why

1. **The MAPE-K concession** — the thesis still says "these are MAPE-K loops in everything but name" without a fuller section on what the contribution adds *beyond* MAPE-K. This is a known weakness. The fuller treatment is planned for v2.0 when a reference implementation can show what the extensions actually buy in practice. Adding a section before the implementation exists would be paper-over-reality.
2. **Organisational MAS engagement (MOISE+, Jason, OperA)** — the literature review gives these a one-liner where they arguably need a section. Same reasoning as above: the comparison is most honest when made against a running implementation, and that does not exist yet.
3. **Stigmergy treatment** — dismissed in a single sentence in the thesis. The reviewer is right that "colony" invites the comparison. This one will be addressed in v1.3 as a footnote with concrete criteria for when stigmergy applies and when colony applies.
4. **Cost model** — no action. The cost question is important but can only be answered empirically. A theoretical cost model before implementation would be invented numbers.
