# Equilibrium Playground

A self-contained browser visualisation of the Agent Colony Equilibrium System. No build step, no server required — open `index.html` in any browser.

## How to open

```bash
open examples/equilibrium-playground/index.html
```

Or just double-click `index.html` in your file manager.

## What it shows

An overlap matrix heatmap of the hello-colony agents, showing how capability overlap is distributed across the colony. The colour scale:

- **Blue/green (0–0.15):** Healthy overlap — agents are well-differentiated
- **Amber (0.15–0.40):** Watch zone — overlap is growing, graduation checklist initiated
- **Red (0.40+):** Merger candidate — Equilibrium Agent will recommend consolidation

## The three indices

**Overlap Index** — average overlap score across all flagged agent pairs (those above the watch threshold). High = consolidation pressure.

**Concentration Index** — how concentrated capability is. Computed as 1 minus a normalised diversity score. High = one or a few agents dominate.

**Vitality Index** — ratio of agents added to agents retired in the current period. Above 1.0 = growing colony. Below 0.5 = fragmentation risk (agents retiring faster than joining).

## Controls

**Watch threshold slider** — move left to flag more pairs as watch-zone; move right to be more permissive. Default: 0.15.

**Merger threshold slider** — move left to flag more pairs as merger candidates; move right to be more permissive. Default: 0.40.

**Add agent** — adds a new domain agent with random overlap values. Shows how the indices shift as the colony grows.

**Remove agent** — retire an existing agent. Shows how the matrix shrinks and whether the vitality index drops.

**Inject workload** — simulates capability accretion. Randomly increases a selection of overlap scores by 0.05–0.15, as if agents have been accumulating each other's responsibilities under load. This is the dark code failure mode in motion.

## Equilibrium states

The system is always in one of three states:

| State | Meaning | Signal |
|-------|---------|--------|
| EQUILIBRIUM | Colony is healthy | Overlap Index < Watch threshold, Vitality Index 0.5–2.0 |
| CONSOLIDATION RISK | Too much overlap | Multiple pairs in watch zone or merger candidate |
| FRAGMENTATION RISK | Colony fragmenting | Vitality Index < 0.5, or Concentration Index > 0.7 |
