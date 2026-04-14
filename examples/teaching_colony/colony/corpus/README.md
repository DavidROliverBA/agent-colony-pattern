# Corpus — v1.7.0 snapshot

These files are **snapshots** of the repository's top-level pattern documents at release v1.7.0. They are COPIES, not symlinks, so this example remains runnable when cloned in isolation and doesn't couple the example's behaviour to unreleased edits of the top-level files.

## Snapshot contents

### `pattern/`

Snapshot of seven files from the repository root, taken on 2026-04-14:

- `manifesto.md`
- `thesis.md`
- `specification.md`
- `it-takes-a-village.md` (the Newcomer article from `knowledge-base/writings/`)
- `dark-code.md` (from `knowledge-base/references/`)
- `prior-art.md` (from `knowledge-base/references/`)
- `indy-dev-dan-six-ideas.md` (from `knowledge-base/references/`)

These are what Librarian reads during the lifecycle's "Learn" phase. The Teacher agent uses the curated summaries to answer the Agent Colony pattern turn of the demo.

### `beekeeping/`

Hand-written primer that does not correspond to any top-level repository file. This is the running pedagogical example the Teacher uses when explaining the more abstract pattern concepts ("worker bees forage for pollen" → "Librarian reads the corpus"). Updated manually if the metaphor needs refreshing.

## How to refresh

If the top-level pattern documents change and you want the example to reflect the new versions, refresh the snapshot from the repo root:

```bash
cd examples/teaching_colony
cp ../../manifesto.md                                         colony/corpus/pattern/manifesto.md
cp ../../thesis.md                                            colony/corpus/pattern/thesis.md
cp ../../specification.md                                     colony/corpus/pattern/specification.md
cp ../../knowledge-base/writings/2026-04-12-it-takes-a-village.md colony/corpus/pattern/it-takes-a-village.md
cp ../../knowledge-base/references/dark-code.md               colony/corpus/pattern/dark-code.md
cp ../../knowledge-base/references/prior-art.md               colony/corpus/pattern/prior-art.md
cp ../../knowledge-base/references/indy-dev-dan-six-ideas.md  colony/corpus/pattern/indy-dev-dan-six-ideas.md
```

Then re-run the example to verify nothing in the lifecycle broke. The snapshot is intentionally manual — automatic sync would couple the example's behaviour to every top-level edit and break the principle that releases should be reproducible.

## Why snapshots and not symlinks

1. **Portability.** Symlinks break when the example is copied into a different location (tarball, Docker image, CI runner clone).
2. **Reproducibility.** A symlink makes `git checkout v1.7.0` unable to reproduce the example the way it shipped — because the symlinked files might have changed since.
3. **Explicit versioning.** The snapshot date in this README tells a reader when the example last agreed with the top-level pattern documents. A symlink hides that.

Current snapshot date: **2026-04-14** (v1.7.0 release).
