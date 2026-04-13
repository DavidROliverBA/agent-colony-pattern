# Hello-Colony Live Runtime

A deterministic Python simulation demonstrating the Agent Colony pattern working as code. No LLM calls. No external services. All events are scripted from the hello-colony example data.

## What this is

The runtime loads the hello-colony agent YAML files, validates them against the v0.1 Agent Mirror schema, and simulates four colony events: agent registration, equilibrium check, security patch co-sign, and graduation checklist query. Everything is deterministic — the same input always produces the same output.

This is not a full Agent Colony implementation. It is a Level 1 demonstration that shows the data structures working and the event logic running.

## How to run

```bash
cd examples/hello-colony-runtime
pip install -r requirements.txt
python runtime.py
```

## What the four events demonstrate

**EVENT 1 — Bootstrap**
The Registry Agent loads and validates all five agent mirrors against the JSON schema. Agents that fail validation are quarantined. Each registered agent's trust tier, critical path status, and blast radius ceiling are displayed.

**EVENT 2 — Equilibrium Check**
The Equilibrium Agent reads the colony's overlap matrix and flags agent pairs that exceed the watch threshold (0.15) or merger threshold (0.40). The finance-domain-agent ↔ equilibrium-agent pair scores 0.24 — watch zone. The appropriate review regime is determined from the acting agent's trust tier and blast radius.

**EVENT 3 — Security Patch**
The Sentinel Agent co-signs a preauthorised security patch (CVE-2026-0441) for the registry-agent. The patch action class is in the Sentinel's preauthorised enum, so no additional peer review is required. The co-sign is recorded in the append-only audit log.

**EVENT 4 — Graduation Query**
The Registry Agent returns the graduation checklist for finance-domain-agent v1.0 → v1.1. The checklist shows evidence requirements, approval requirements, and external actions with their current status and blast radius classifications.

## Events directory

The `events/` directory contains YAML definitions of each simulated event. These serve as documentation of the colony events the runtime simulates — useful for understanding what each event represents and what its expected output is.

## What this is not

- Not a real-time runtime — all events run once, sequentially, and exit
- Not an LLM integration — no models are called
- Not a complete colony implementation — governance, equilibrium enforcement, and Comprehension Contract artefacts are simulated, not implemented
- Not a production system — use this to understand the pattern, not to run workloads

## Next steps

Level 2 demonstration (future): an LLM-backed agent that actually calls tools, produces comprehension artefacts, and has its blast radius classified by the Structural Classifier at runtime.
