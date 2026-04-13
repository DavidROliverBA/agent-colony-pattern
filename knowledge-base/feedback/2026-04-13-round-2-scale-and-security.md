# Round 2 — Scale-adaptive application and security preauthorisation — 2026-04-13

**Reviewer:** anonymous peer review
**Round:** 2
**Scope:** Response to v1.1.0 — two specific gaps the reviewer felt v1.1.0 left open
**Version reviewed:** v1.1.0

## Summary

The reviewer accepted most of v1.1.0's fixes but pushed back on two specific points. First, the "unit-of-analysis slippage" from round 1 was acknowledged in the v1.1.0 commits but not visibly addressed in the content — the reviewer wanted this reframed as a *feature* (scale-adaptive application) rather than a *defect*. Second, the v1.1.0 treatment of the security preauthorisation risk was a Discussion-section acknowledgment, not a mitigation — the reviewer wanted concrete invariants.

## Key points raised

### Scale slippage is a feature, not a defect — make it explicit

> You are right it is by design. The fix is not to pin a single scale, it is to make the scale-dependence explicit. One table in §3 or §5 does it.

The reviewer proposed a table structure showing how each principle / mechanism adapts across three tiers:

| Principle | 5-agent team | 50-agent org estate | 5,000-agent ecosystem |
|---|---|---|---|
| Agent Mirror | Lightweight YAML, manual curation | Schema-validated, CI-gated | Registry + signed attestations |
| Equilibrium | Human review | MAPE-K loop per colony | Cross-colony regime monitoring |
| Trust Ledger | Informal | Per-agent score, human adjudication | Federated, cryptographic |

> That reframes the "slip" as scale-adaptive application rather than conceptual confusion — and it protects you from the reviewer who says "this is overkill for 5 agents" and the one who says "this will not survive 5,000". Cost: half a page.

### Security preauthorisation — accept, strengthen

> Fair — I missed that the Discussion flags it. The issue is not that it is unacknowledged, it is that acknowledgement without mitigation reads as hand-waving. Strengthening needs three concrete things the current text does not have.

1. **Scope definition.** What counts as a "security upgrade"? A closed enum (patch application, credential rotation, certificate renewal, signature update, quarantine-of-self) beats an open category. Anything outside the enum is not preauthorised, full stop.
2. **Second-party gate.** Preauthorisation ≠ unilateral. The Immune Agent (or a sibling) co-signs. A single compromised agent cannot self-authorise; it needs collusion, which raises the attack cost meaningfully.
3. **Rollback + audit invariant.** Every preauthorised action writes to an append-only log the acting agent cannot redact, and is reversible within a bounded window. If you cannot roll it back, it is not preauthorised — it is escalated.

> That turns one paragraph of "we recognise the risk" into a mitigation the reader can critique on its merits. It also gives you a clean line against the strongest version of the objection: "a compromised agent classifying exfiltration as a security upgrade" fails at step 1 (not in the enum), step 2 (no co-sign), and step 3 (logged and reversible). Defence in depth, stated explicitly.

## Verdict

> Both are cheap fixes that materially strengthen the thesis without restructuring it.

## What changed in response

Implemented in **v1.1.1** (2026-04-13):

- **Scales of application** — new subsection added to `specification.md` §1 with a seven-row table (one per principle / mechanism) × three columns (5 / 50 / 5,000 agents). Explicit note that the table is not a maturity model — a 5-agent colony with lightweight YAML is *correctly scaled*, not immature. Thesis mirrors it as a shorter summary pointing to the spec.

- **Security preauthorisation strengthened** — three concrete invariants now embedded in Principle 6 itself:
  1. **Closed enum:** patch application, dependency update, credential rotation, certificate renewal, signature update, self-quarantine. Anything else is not preauthorised.
  2. **Immune System co-sign:** every preauthorised action requires a signature from the Sentinel or Patch Agent.
  3. **Append-only audit log with bounded rollback:** 60-minute default, pre-state hash, non-redactable, reversible. An action that cannot be rolled back is escalated, not preauthorised.

- **Conformance section §7.5 failure mode 3** (preauthorised-security abuse) now walks the canonical attack through a six-layer defence: three structural invariants from Principle 6 plus three behavioural detection layers in the Immune System (Sentinel drift detection, Patch Agent scope limits, Response Coordinator cross-check). Explicit note that for the attack to succeed, the adversary must defeat all six layers — and that none of the layers have been exercised by a reference implementation.

## What has not changed and why

Nothing. Both pieces of feedback were accepted in full and implemented as described. The reviewer's proposed table structure was adopted almost verbatim, and the three invariants became the three bullets in the corollary to Principle 6.
