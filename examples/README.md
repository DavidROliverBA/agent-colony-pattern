# Examples

This directory contains example implementations and demonstrations of the Agent Colony pattern. Each example is pitched at a specific audience lens (see Principle 7 in the specification — *Accessibility through abstraction*).

## Lens map

Which example should you start with? It depends on which lens you are currently at. Lenses are sequential — most people traverse Newcomer → Observer → Operator → Beekeeper → Architect — but you can drop in at whichever depth you need.

| Your lens | Where to start | What you'll see |
|-----------|----------------|------------------|
| **Newcomer** | [*It takes a village*](../knowledge-base/writings/2026-04-12-it-takes-a-village.md) | The metaphor. No jargon, no mechanisms. |
| **Observer** | (no repo artefact — invisibility is the point) | If you're an Observer, you don't need the examples at all. |
| **Operator** | [`equilibrium-playground/`](equilibrium-playground/) | A dashboard view of colony health. Open in a browser, no setup. |
| **Beekeeper** | [`hello-colony/`](hello-colony/), [`hello-colony-runtime/`](hello-colony-runtime/), then [`teaching_colony/`](teaching_colony/) | The mechanisms on disk (YAML Mirrors, graduation checklists), the runtime that operates on them, and the first substrate-portable colony that teaches the pattern. |
| **Architect** | [`../specification.md`](../specification.md) | The substrate. Return here once you've seen the mechanisms run. |

The canonical artefacts mapped to each lens are defined in `specification.md` §1 (Audience Lenses). This repository's conformance claim against Principle 7 is exactly this mapping.

## hello-colony

**Audience lens:** Beekeeper

**[hello-colony/](hello-colony/)** — The canonical worked example. Five agents defined with full Agent Mirror YAML files: registry-agent, equilibrium-agent, sentinel-agent, chronicler-agent, and domain-agent-finance. Includes a pre/post-evolution pair (registry-agent v1.0 and v1.1) and a colony snapshot.

In v1.3.0, all six agent definitions were extended with Comprehension Contract fields (trust tier, NFRs, valuation, critical path position) and a graduation checklist for the finance agent's v1.0→v1.1 path.

## hello-colony-runtime

**Audience lens:** Beekeeper

**[hello-colony-runtime/](hello-colony-runtime/)** — A deterministic Python simulation demonstrating the Agent Colony pattern working as code. Loads the hello-colony agent YAML files, validates them against the v0.2.0 schema, and simulates four colony events: bootstrap, equilibrium check, security patch, and graduation query. No LLM calls.

```bash
cd hello-colony-runtime
pip install -r requirements.txt
python runtime.py
```

## teaching-colony

**Audience lens:** Beekeeper

**[teaching_colony/](teaching_colony/)** — A substrate-portable six-agent Agent Colony that teaches the Agent Colony pattern, using beekeeping as the running pedagogical example. Ships with two substrates — Claude Code (Anthropic Python SDK) and the Managed Agents API — demonstrating Principle 2 (*Identity over implementation*) and Principle 4 (*Longevity by design*) in running code for the first time. The first exercise of the Comprehension Contract (§7): Librarian detects KB coverage crossing a threshold, proposes Teacher acquire a new capability, the structural classifier fires, Sentinel co-signs, and Teacher's Mirror is updated with an append-only audit trail. Added in v1.6.0.

```bash
cd teaching_colony
python run.py --substrate=claude-code --mock
```

Known gap: live-mode Managed Agents operations are deferred to v1.7+. See [substrates/managed_agents/gaps.md](teaching_colony/substrates/managed_agents/gaps.md).

## equilibrium-playground

**Audience lens:** Operator

**[equilibrium-playground/](equilibrium-playground/)** — A self-contained browser visualisation of the Equilibrium System. An overlap matrix heatmap with threshold sliders, add/remove agent controls, and an inject-workload button that simulates capability accretion. No build step — just open `index.html`.

```bash
open equilibrium-playground/index.html
```

## demonstration-options

**Audience lens:** Architect

**[demonstration-options.md](demonstration-options.md)** — Design memo of ten options for building visual demonstrations of the pattern, with purpose-fit matrix and three recommended combinations at different ambition levels.
