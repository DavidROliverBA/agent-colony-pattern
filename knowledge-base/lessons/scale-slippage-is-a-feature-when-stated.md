# Scale slippage is a feature when stated explicitly

**Date first learned:** 2026-04-13
**Evidence grade:** corroborated
**Source:** [Round 1](../feedback/2026-04-13-round-1-manifesto-critique.md) and [Round 2 feedback](../feedback/2026-04-13-round-2-scale-and-security.md)
**Status:** graduated to rule

## The lesson

A pattern that applies at multiple scales — 5 agents, 50 agents, 5,000 agents — will be critiqued for "slipping between units of analysis" unless the multi-scale nature is stated as an explicit design feature with a per-scale table. The fix is not to pin the pattern to a single scale. The fix is to make the scale-dependence visible and to pair it with the anti-maturity-model disclaimer: **a small colony running the lightweight version is not immature relative to a large colony — it is correctly scaled, and over-engineering the small one is a pattern violation**.

## Conditions

Applies to any pattern that claims to work across organisational scales. The pattern's mechanisms (Agent Mirror, Equilibrium System, Colony Memory, Trust Ledger) each have legitimate implementations at different fidelity levels: a YAML file in git, a schema-validated CI-gated repo, a federated cryptographic registry. Different scales choose different mechanisms, and the *same* principle can be realised by mechanisms that look nothing alike.

The diagnostic question: *can a hostile reviewer quote the pattern at two different scales and make it look inconsistent?* If yes, the pattern has a scale-slippage problem and needs an explicit table.

## Evidence

- **Round 1 feedback (v1.0.0)** flagged: *"Unit of analysis slips between 'deployment', 'org-wide estate', and 'cross-company ecosystem'."*
- The author argued this was by design.
- **Round 2 feedback (v1.1.0)** accepted the pushback and proposed the specific fix: *"The fix is not to pin a single scale, it is to make the scale-dependence explicit. One table in §3 or §5 does it."*
- **v1.1.1** added the Scales of Application table to specification §1 with seven rows (one per principle / mechanism) × three columns (5 / 50 / 5,000 agents), plus the anti-maturity-model disclaimer.
- **Round 3 feedback** explicitly praised the disclaimer: *"The anti-maturity-model disclaimer is the right move. It stops the table being read as a progression ladder and reframes over-application as a violation, which is a stronger claim than a permission."*

Two rounds of feedback converging on the same fix = corroborated.

## Disproven if

- A pattern emerges that genuinely works at only one scale and would be weakened by the per-scale table framing. (Not yet observed — the Agent Colony pattern appears to be scale-adaptive by construction.)
- The per-scale table itself introduces more confusion than the ambiguity it resolves. (Not yet observed.)

## Related rules

- **Agent Colony v1.1.1, Specification §1, Scales of Application** — seven-row table with the explicit anti-maturity-model disclaimer.
- **Thesis** — mirrored shorter summary pointing to the specification.
- **Meta-rule for pattern specifications** — when a reviewer flags "unit of analysis slippage", the author should not defend the pattern against the critique. The author should agree, publish the scale-adaptive table, and include the disclaimer that over-applying at small scale is as much a violation as under-applying at large scale.

This lesson has a broader application: *sometimes the right response to "your spec is ambiguous" is "yes, because it covers N cases, and here is the table showing which mechanism belongs to which case"*. Ambiguity across scales, made explicit, becomes adaptability.
