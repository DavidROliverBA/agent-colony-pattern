# Acknowledgment is not mitigation

**Date first learned:** 2026-04-13
**Evidence grade:** corroborated
**Source:** [Round 2 feedback on security preauthorisation](../feedback/2026-04-13-round-2-scale-and-security.md)
**Status:** graduated to rule

## The lesson

When a specification admits a risk in the Discussion section, that admission does not close the risk. A reviewer will read "we recognise this could be abused" as hand-waving. The risk is only closed when the specification shows a concrete mitigation that fails gracefully under the attack.

## Conditions

Applies to any specification that claims a controversial property (security preauthorisation, autonomy, self-evolution). The pattern here is: a property that sounds dangerous in the abstract must be defended with specific invariants, not with a paragraph of acknowledgment.

The diagnostic question: *could a hostile reviewer quote this Discussion paragraph back at the author as evidence that the author knew the risk and did nothing about it?* If yes, the acknowledgment is doing the work that a mitigation should do.

## Evidence

- **Round 1 feedback (v1.0.0)** flagged security preauthorisation as a risk. The author added an acknowledgment to the Discussion section in v1.1.0.
- **Round 2 feedback (v1.1.0)** rejected the acknowledgment as insufficient: *"acknowledgement without mitigation reads as hand-waving"*. The reviewer proposed three concrete invariants — closed enum, second-party co-sign, append-only log with bounded rollback.
- **v1.1.1** implemented the three invariants in Principle 6 and in the Conformance section's failure mode 3 as a six-layer defence.
- **Round 3 feedback** praised the six-layer treatment and specifically the clause "*an action that cannot be rolled back is not preauthorised; it is escalated*" as *"the load-bearing one — it converts rollback from a nice-to-have into a gating condition."*

Two rounds of reviewer feedback agreeing on the same point = corroborated.

## Disproven if

- A reviewer of a future specification reads a Discussion-section acknowledgment and accepts it as sufficient without further mitigation. (Not yet observed.)
- A case emerges where adding concrete invariants *weakens* a specification by making it look over-engineered for the actual risk. (Theoretically possible but not observed.)

## Related rules

- **Agent Colony v1.1.1, Principle 6 corollary** — the three preauthorisation invariants.
- **Agent Colony v1.1.1, Conformance §7.5 failure mode 3** — the six-layer defence walks the canonical attack through each invariant.
- **General principle for the specification's own evolution** — any risk flagged by a reviewer must graduate from "acknowledged" to "mitigated" before the next version ships. Acknowledgment is the first step, not the last.
