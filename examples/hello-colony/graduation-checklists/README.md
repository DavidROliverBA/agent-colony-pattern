# Graduation Checklists

Graduation checklists are the formal record of an agent's path from one version to the next. They are maintained by the Registry Agent and surface the evidence requirements, approval requirements, and external actions that must be completed before a version increment is accepted.

## What they are

A graduation checklist is the Agent Colony's equivalent of a pull request checklist — except the "PR" is an agent's capability evolution, not a code change. Each checklist records:

- **Evidence requirements** — measurable conditions that must be met (sustained SLA compliance, audit disagreement rates, design reviews)
- **Approval requirements** — sign-offs from other agents or human governance bodies
- **External actions** — side-effects of graduation that must be executed (registry updates, notifications, audit records). Each external action carries a pre-classified blast radius and review regime so there are no surprises at execution time.

## Who maintains them

The Registry Agent generates and updates graduation checklists. An agent cannot self-certify graduation — the Registry Agent holds the checklist and validates evidence before accepting a version increment.

## How to read them

Each file is named `{agent-id}-v{from}-to-v{to}.yaml`. The `summary` block at the bottom gives a quick count of complete / in-progress / pending items. The `estimated_completion` date is set when the checklist is generated and updated as evidence accumulates.

## Current checklists

| Agent | From | To | Status | Estimated Completion |
|-------|------|----|--------|---------------------|
| domain-agent-finance | 1.0 | 1.1 | In progress (1/8) | 2026-05-13 |

## Why the finance agent?

The finance agent has an overlap score of 0.24 with the equilibrium-agent (watch zone: 0.15–0.40). v1.1 will suppress the self-monitoring capabilities that caused the overlap, handing them back to the Equilibrium Agent. This is the pattern working correctly: Equilibrium detected the drift, the graduation path resolves it.
