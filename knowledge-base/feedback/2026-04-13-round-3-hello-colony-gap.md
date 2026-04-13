# Round 3 — Hello-colony gap + Trust Ledger framing — 2026-04-13

**Reviewer:** anonymous peer review
**Round:** 3
**Scope:** Response to v1.1.1 — one remaining gap the reviewer felt v1.1.1 did not close
**Version reviewed:** v1.1.1

## Summary

The reviewer praised the v1.1.1 changes (Scales of Application table, six-layer security defence) as materially stronger than v1.1. But they flagged one remaining issue: the improvements had landed in the specification and the thesis, but the `hello-colony` worked example still showed the pre-v1.1.1 world. The example was arguing for v1.1 while the spec had moved to v1.1.1. A small polish nit on the Trust Ledger framing was included.

## Key points raised

### The hello-colony gap

> One remaining gap worth flagging: neither change is yet reflected in `hello-colony/`. The worked example still shows the pre-v1.1.1 world. A 20-minute addition of (a) one `agent-mirror.yaml` with a populated `security_upgrade_log` entry showing enum-item + co-signer + hash, and (b) one scale annotation in the colony snapshot saying "this example is calibrated to the 5-agent row of §1.2" would make both changes load-bearing in the example, not just in the prose. Currently the example is arguing for v1.1; the spec has moved to v1.1.1. Closing that gap is cheap.

### Trust Ledger framing nit

The Scales of Application table's 5-agent row for Trust Ledger read: *"Informal; spreadsheet or markdown table"*.

> Minor nit: the 5-agent Trust Ledger cell undersells it slightly — at this scale the Ledger arguably *is* human memory plus a retro, and saying so would be more honest than implying every scale needs an artefact.

## Praise for what landed well

The reviewer was explicit about what they liked in v1.1.1, which is worth preserving for future contributors:

- **On the scales table:** *"The anti-maturity-model disclaimer — 'a 5-agent colony running the lightweight version is not immature… over-engineering a small colony with cryptographic federation is as much a pattern violation as under-engineering a large one with shared markdown.' This is the right move. It stops the table being read as a progression ladder and reframes over-application as a violation, which is a stronger claim than a permission."*
- **On the closed enum:** *"The 'deliberately tight — broader invites abuse, narrower cripples defence' line is the right kind of self-aware framing."*
- **On the co-sign:** *"Crisp. Raises attack cost from 'own one agent' to 'own one agent plus the thing watching it'."*
- **On the rollback-as-gating-condition:** *"'An action that cannot be rolled back is not preauthorised; it is escalated.' That last clause is the load-bearing one — it converts rollback from a nice-to-have into a gating condition."*
- **On the Sentinel drift detection:** *"'A genuine security upgrade makes the Mirror more accurate, not less.' This is a lovely invariant and I have not seen it stated elsewhere. It is a positive signature of legitimacy, not just a negative filter."*
- **On the v1.1.1 closing caveat:** *"'None of the six layers has been exercised by a reference implementation; they are the current design and should be treated as provisional until tested against a real attack scenario.' That one sentence is worth more than any number of confident claims — it tells a sceptical reader you know the difference between a design and a proof."*

## Verdict

> Both revisions are materially stronger than v1.1. The scales table converts a structural ambiguity into a declared feature with concrete mechanisms at each tier. The security section moves from "we acknowledge this risk" to a six-layer defence-in-depth where the attacker has to defeat all of enum, co-sign, log, drift-detection, scope-limits, and cross-colony correlation. That is a real increase in what a hostile reviewer has to argue against.

## What changed in response

Implemented in **v1.1.2** (2026-04-13):

- **`examples/hello-colony/agents/registry-agent.v1.1.yaml`** — the security_patch evolution log entry now carries all three preauthorisation invariants:
  - `preauthorised_action_class: patch_application` (closed enum)
  - `co_signer: sentinel-agent` and `co_sign_verified: true`
  - `pre_state_hash`, `rollback_window_minutes: 60`, `rollback_deadline`, `append_only_log_id`
  - The `last_security_upgrade` field in the security section carries the same metadata.

- **`examples/hello-colony/colony-snapshot.yaml`** — new top-level `scale: 5-agent-team` declaration with a `scale_notes` block that ties the example explicitly to the specification's Scales of Application table. Includes the important note that **security mechanisms are the one thing that does not dial down with scale** — the preauthorisation contract is the same at every tier.

- **`examples/hello-colony/README.md`** — opens with a Scale Calibration section, and the self-evolution walkthrough now explains each of the v1.1.1 invariants with a concrete example of how the canonical attack fails at each one.

- **Trust Ledger framing fix** — the 5-agent cell in the Scales of Application table now reads *"Human memory plus a retro; the team itself is the ledger"*. Mirrored in the thesis.

## What has not changed and why

Nothing. Both pieces of feedback were acted on directly. The Trust Ledger framing fix was the exact wording the reviewer suggested.
