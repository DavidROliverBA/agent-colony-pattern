# Worked examples must track the spec

**Date first learned:** 2026-04-13
**Evidence grade:** corroborated
**Source:** [Round 3 feedback](../feedback/2026-04-13-round-3-hello-colony-gap.md)
**Status:** graduated to rule

## The lesson

When a specification is updated, every worked example that demonstrates it must be updated at the same time. Worked examples drift faster than prose, because prose is read top-to-bottom while examples are spot-checked. A spec update that leaves the example arguing for the previous version is not an update — it is a branch.

## Conditions

Applies to any repository that maintains both a specification and worked examples. The condition is structural: examples are the primary artefact a reader uses to verify they understand the spec, so if the example lags the spec, the reader is calibrating against the wrong artefact.

The diagnostic question: *if a reader reads only the example, which version of the spec would they conclude they are reading?* If the answer is "an older version", the example has drifted.

## Evidence

- **v1.1.0** — Specification §7.5 introduced the Conformance section with the six-layer defence for preauthorised security abuse.
- **v1.1.1** — Principle 6 strengthened with the three invariants: closed enum, Immune System co-sign, append-only audit log with bounded rollback.
- **v1.1.1** also shipped the Scales of Application table in §1.
- **Round 3 feedback (v1.1.1)** flagged: *"Neither change is yet reflected in `hello-colony/`. The worked example still shows the pre-v1.1.1 world... Currently the example is arguing for v1.1; the spec has moved to v1.1.1. Closing that gap is cheap."*
- **v1.1.2** updated the hello-colony registry-agent.v1.1.yaml to carry the three preauthorisation invariant fields (`preauthorised_action_class`, `co_signer`, `pre_state_hash`, `rollback_window_minutes`, `append_only_log_id`) and added a `scale: 5-agent-team` declaration to `colony-snapshot.yaml` tying the example to the Scales of Application table.

One round of reviewer feedback, but the pattern is clear and the fix was accepted without pushback = corroborated by consensus.

## Disproven if

- A case emerges where *not* updating the worked example leads to clearer communication. (Not plausible — worked examples are load-bearing for reader calibration.)
- A case emerges where the spec update is genuinely backward-compatible and the old example still demonstrates the new behaviour. (Plausible in theory; in practice, additions like preauthorisation invariants require the example to show the new fields or it reads as outdated.)

## Related rules

- **Rule for repo contributors:** Any PR that changes the specification must also update `examples/hello-colony/` (or flag it as a breaking example change that requires a follow-up PR). This should be enforced by a CI check or a PR template checklist.
- **Rule for version tagging:** A version bump that leaves the worked example on an older spec version is not a valid release. Either update the example or clearly mark the release as "spec-only, example follow-up pending".
- **Meta-rule:** In a repo with both prose and executable examples, the executable examples carry higher truth weight. A reader who finds a mismatch will trust the example over the prose. This is not a bug — it is why executable examples are valuable — but it means the examples must be kept trustworthy.

This lesson also applies to the planned Hello-Colony Live Runtime (see [`../../examples/demonstration-options.md`](../../examples/demonstration-options.md) option 1). When the runtime exists, any change to the specification must be reflected in the runtime's behaviour. The runtime becomes the highest-truth-weight artefact in the repo.
