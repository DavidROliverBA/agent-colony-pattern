# References

External work the pattern engages with. Prior art, related standards, academic papers. The literature review in `thesis.md` is the formal statement; these files are the working notes behind it — useful when you want to trace *why* a specific reference matters or *how* the pattern positions against it.

## Structure

- **[prior-art.md](prior-art.md)** — historical and academic work that the pattern draws on or distinguishes itself from. Includes MAPE-K, FIPA, KQML, MOISE+, OperA, Jason, Constitutional AI, stigmergy, holonics, Agentic Hives.
- **[standards-watch.md](standards-watch.md)** — active standards efforts to track. Includes A2A, MCP, AGNTCY / OASF, NIST Agent Standards Initiative, AGENTS.md under Linux Foundation AAIF governance, IEEE P3119, ISO/IEC 42001 family.
- **[dark-code.md](dark-code.md)** — Nate B Jones's 2026 framing of *dark code* (code nobody at any point in its lifecycle ever understood), its two structural breaks, the Amazon Kiro incident as public preview, and the mapping of Jones's three prescribed layers onto the Agent Colony's Agent Mirror, Colony Memory, and Coexistence Boundary.
- **[indy-dev-dan-six-ideas.md](indy-dev-dan-six-ideas.md)** — IndyDevDan's six actionable ideas for engineers navigating hyper-capable models (Claude Mythos context), mapped against Agent Colony mechanisms. Identifies *deceptive reasoning / micro-misalignment* as the most significant gap in the current pattern — driving the False Comprehension Artefacts failure mode and blind-audit property in the Comprehension Contract.

## Why this exists separately from the thesis literature review

The thesis Section 3 is a formal literature review — it maps each standard to the gaps it does and does not address, ending in a synthesis table. That is the artefact a reviewer or a standards body cites.

These files are the **working notes** behind that review. They capture:

- **Why a reference was included at all** — the original reasoning, which sometimes gets lost when the prose goes through editing passes.
- **What the pattern concedes** — places where the pattern is genuinely derivative of existing work. These concessions are load-bearing. The thesis does not always state them in full because academic prose compresses; this folder states them in full.
- **What is on the watchlist** — emerging standards that do not yet exist in a citable form but are expected to matter in the next 12 months.
- **Disagreements** — places where the pattern explicitly rejects a position held by a referenced work. The thesis says *what* the pattern does; these notes say *why* it does not do what the referenced work does.

Reviewers who want the formal story read the thesis. Reviewers who want to understand the pattern's intellectual heritage in detail read this folder.

## How to add a reference

1. Decide whether it is prior art (historical / academic) or an active standard (current / emerging).
2. Add an entry to the relevant file with:
   - Name and canonical citation
   - One sentence on what the reference contributes
   - One sentence on how the Agent Colony pattern uses or distinguishes itself from it
   - A link to the primary source
3. If the reference should appear in the thesis literature review, open a PR updating both files together — the working notes and the formal review.
