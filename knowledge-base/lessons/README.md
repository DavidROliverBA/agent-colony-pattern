# Lessons

Insights extracted from [`../feedback/`](../feedback/) and from development work. Each lesson has an evidence grade, a source, and a note on whether it has graduated into a specification rule.

## Convention

Each lesson follows the same structure as a Lesson Memory entry in the specification — which is deliberate. The pattern's own principles applied to the pattern's own development.

```markdown
# [Lesson title]

**Date first learned:** YYYY-MM-DD
**Evidence grade:** empirical | corroborated | theoretical | inherited | anecdotal
**Source:** [which feedback round, commit, or observation]
**Status:** provisional | corroborated | graduated to rule

## The lesson
[one or two sentences stating the lesson]

## Conditions
[when does it apply? Under what conditions is it relevant?]

## Evidence
[what supports it? link to specific feedback, commits, or observations]

## Disproven if
[what would falsify this lesson?]

## Related rules
[if the lesson has graduated, which rule(s) in the specification or in the excalidraw-diagram skill cite it?]
```

## Evidence grades (same as spec §6.2)

| Grade | Meaning |
|-------|---------|
| **Empirical** | Directly observed, reproducible |
| **Corroborated** | Observed multiple times across contexts |
| **Theoretical** | Logically sound, not yet observed in practice |
| **Inherited** | From external sources, not yet validated locally |
| **Anecdotal** | Single observation, unreproduced |

Rules in the specification should require **corroborated** evidence or higher. Lessons that start as anecdotal can graduate as they accumulate corroboration.

## Current lessons

| File | Date | Grade | Status | Source |
|------|------|-------|--------|--------|
| [`acknowledgment-is-not-mitigation.md`](acknowledgment-is-not-mitigation.md) | 2026-04-13 | corroborated | graduated to rule | Round 2 feedback |
| [`diagrams-must-run-rules-not-taste.md`](diagrams-must-run-rules-not-taste.md) | 2026-04-13 | corroborated | graduated to rule | Rounds 4+ and multiple diagram iterations |
| [`scale-slippage-is-a-feature-when-stated.md`](scale-slippage-is-a-feature-when-stated.md) | 2026-04-13 | corroborated | graduated to rule | Round 2 feedback |
| [`worked-examples-must-track-the-spec.md`](worked-examples-must-track-the-spec.md) | 2026-04-13 | corroborated | graduated to rule | Round 3 feedback |
