# Examples

This directory contains example implementations and demonstrations of the Agent Colony pattern.

## hello-colony

**[hello-colony/](hello-colony/)** — The canonical worked example. Five agents defined with full Agent Mirror YAML files: registry-agent, equilibrium-agent, sentinel-agent, chronicler-agent, and domain-agent-finance. Includes a pre/post-evolution pair (registry-agent v1.0 and v1.1) and a colony snapshot.

In v1.3.0, all six agent definitions were extended with Comprehension Contract fields (trust tier, NFRs, valuation, critical path position) and a graduation checklist for the finance agent's v1.0→v1.1 path.

## hello-colony-runtime

**[hello-colony-runtime/](hello-colony-runtime/)** — A deterministic Python simulation demonstrating the Agent Colony pattern working as code. Loads the hello-colony agent YAML files, validates them against the v0.2.0 schema, and simulates four colony events: bootstrap, equilibrium check, security patch, and graduation query. No LLM calls.

```bash
cd hello-colony-runtime
pip install -r requirements.txt
python runtime.py
```

## equilibrium-playground

**[equilibrium-playground/](equilibrium-playground/)** — A self-contained browser visualisation of the Equilibrium System. An overlap matrix heatmap with threshold sliders, add/remove agent controls, and an inject-workload button that simulates capability accretion. No build step — just open `index.html`.

```bash
open equilibrium-playground/index.html
```

## demonstration-options

**[demonstration-options.md](demonstration-options.md)** — Design memo of ten options for building visual demonstrations of the pattern, with purpose-fit matrix and three recommended combinations at different ambition levels.
