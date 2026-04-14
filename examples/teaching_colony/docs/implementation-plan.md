# Teaching Colony Implementation Plan

> **This is the implementation plan that produced the Teaching Colony example.** It was written as a working document in the author's private vault alongside the [design spec](design-spec.md) and copied into the public repository at v1.6.1. It describes the five-sub-agent parallel execution strategy used to build v1.6.0. Reading it gives an honest view of how the example was actually built — including the coordination rules, the write-scope boundaries, the research risks, and the rollback plan.
>
> Companion: [design-spec.md](design-spec.md) — the spec this plan executed.

**Date:** 2026-04-14
**Status:** Executed in v1.6.0; exposed in public repo at v1.6.1
**Spec:** [design-spec.md](design-spec.md)
**Repository:** `agent-colony-pattern`

---

## Execution strategy

Five sub-agents across two batches.

**Batch 1 — three parallel sub-agents, no file conflicts between them.** Run simultaneously.

- **Sub-agent A** — substrate contract, colony definition, Mirrors, corpus, classifier, graduation logic. Writes everything under `examples/teaching-colony/` except the `substrates/` directory. Does NOT touch the substrates directory.
- **Sub-agent B** — Claude Code substrate adapter. Writes everything under `examples/teaching-colony/substrates/claude-code/`. Reads the sub-agent A output only through agreed interface files (contract.py, Mirror files). Does NOT touch `substrates/managed-agents/` or anything outside its own directory.
- **Sub-agent C** — Managed Agents API research and scaffolding. Writes `examples/teaching-colony/substrates/managed-agents/api-research.md` and a scaffolding `adapter.py` with stub methods. Does NOT attempt a working adapter in Batch 1 — that is Batch 2's job.

**Batch 2 — two sequential sub-agents, depending on Batch 1 output.**

- **Sub-agent D** — Managed Agents adapter completion. Takes sub-agent C's research output, implements whatever is implementable, documents gaps honestly.
- **Sub-agent E** — portability test + top-level README + CHANGELOG + CITATION + repo-level README updates. Runs after D so it can verify both substrates.

After both batches complete, a final commit with tag `v1.6.0` and a GitHub release.

## Coordination rules for parallel sub-agents

All three Batch 1 sub-agents are told:

- Your working directory is the repo root: `/Users/david.oliver/Documents/GitHub/agent-colony-pattern`
- Your write scope is exactly the paths listed in your task
- You MUST NOT modify any file outside your scope, even to fix a typo you notice
- If you discover a problem that requires cross-cutting changes, STOP and report the problem in your final message — do not try to fix it across scope boundaries
- When reading files from another sub-agent's scope that do not yet exist, use the contract defined in this plan document as your ground truth (do not guess)
- You MAY read any file outside your scope (reading is safe)
- Assume the v0.2.0 Mirror schema at `schemas/agent-mirror-v0.2.0.json` is the ground truth for Mirror structure
- Assume the hello-colony agents at `examples/hello-colony/agents/*.yaml` are the reference style for Mirror formatting

## Sub-agent A — Contract, colony, classifier

**Working directory:** `/Users/david.oliver/Documents/GitHub/agent-colony-pattern`

**Write scope:**

- `examples/teaching-colony/README.md`
- `examples/teaching-colony/requirements.txt`
- `examples/teaching-colony/run.py`
- `examples/teaching-colony/contract.py`
- `examples/teaching-colony/substrate-contract.md`
- `examples/teaching-colony/colony/mirrors/*.yaml` (six files)
- `examples/teaching-colony/colony/corpus/pattern/` (copies of pattern files — see note below)
- `examples/teaching-colony/colony/corpus/beekeeping/primer.md`
- `examples/teaching-colony/colony/overlap.yaml`
- `examples/teaching-colony/colony/logic/classifier.py`
- `examples/teaching-colony/colony/logic/review_regime.py`
- `examples/teaching-colony/colony/logic/graduation.py`
- `examples/teaching-colony/colony/logic/__init__.py`
- `examples/teaching-colony/state/kb/beekeeping.md`
- `examples/teaching-colony/state/.gitignore`

**Specific content requirements:**

### contract.py

Exactly the `SubstrateContract` abstract base class from the spec's "Substrate contract" section. Eight abstract methods with full type hints. Use `abc.ABC` and `@abstractmethod`. Include dataclasses for `Mirror`, `Event`, `Document`, `AuditEntry`, `Signature`, `Classification` with the fields described in the spec.

Include at the top of the file a docstring with the eight operations as a summary table.

### Mirrors

Six YAML files following the v0.2.0 schema. Read `examples/hello-colony/agents/registry-agent.v1.1.yaml` and `examples/hello-colony/agents/sentinel-agent.yaml` as reference style. Each Mirror must include:

- `identity` — name, purpose, version (1.0.0), lineage
- `capabilities` — at least one capability per agent, using the structure hello-colony uses
- `autonomy` — level: `supervised` for L3 agents, `bounded` for L1/L2 agents; evolution_log starting as a fresh list
- `security` — posture, escalation_process with preauthorised_security_upgrades: true
- `lifecycle` — stage: `active`, retirement_conditions
- `relationships` — dependencies, overlap_map (short), critical_path
- `comprehension_contract` — trust_tier per spec table, pre_registered_policies, audit_rate, blast_radius_ceiling, classifier_version: "1.0"
- `nfrs` — inherited colony-event-logging, specific values per spec
- `valuation` — self, peer, audit, human dimensions (most start under-calibrated)

**Per-agent specifics from the spec's agent composition table:**

- registry-agent: Bounded, critical_path.structural true
- chronicler-agent: Bounded, critical_path.structural true
- equilibrium-agent: Bounded, critical_path.structural true
- sentinel-agent: Bounded, blast_radius_ceiling: Boundary-crossing, two pre_registered_policies (graduation_cosign and security_patch_cosign), critical_path.structural true
- librarian-agent: Observing, audit_rate 1.0, capabilities include `read_corpus`, `extract_concepts`, `write_kb`, `propose_capability`, critical_path.structural false
- teacher-agent: Observing, audit_rate 1.0, capabilities include `teach_beekeeping` (initial single capability), critical_path.structural false — this agent is the one whose Mirror will be updated in the graduation event

Each Mirror must validate against `schemas/agent-mirror-v0.2.0.json`.

### corpus/pattern/ — copy strategy

For portability across operating systems, copy (do not symlink) the following files from the repo root into `examples/teaching-colony/colony/corpus/pattern/`:

```
manifesto.md                       → corpus/pattern/manifesto.md
thesis.md                          → corpus/pattern/thesis.md
specification.md                   → corpus/pattern/specification.md
knowledge-base/references/dark-code.md                 → corpus/pattern/dark-code.md
knowledge-base/references/prior-art.md                 → corpus/pattern/prior-art.md
knowledge-base/references/indy-dev-dan-six-ideas.md    → corpus/pattern/indy-dev-dan-six-ideas.md
knowledge-base/writings/2026-04-12-it-takes-a-village.md → corpus/pattern/it-takes-a-village.md
```

Use `shutil.copy2` in a one-off script or do it directly. Do this at plan execution time; the corpus is static after that. Document in `README.md` that the corpus is a snapshot at v1.6.0 and must be refreshed manually if the source files change.

### corpus/beekeeping/primer.md

Hand-write a 2–3 page primer covering:

1. What a beehive is (the physical structure: hive body, frames, supers)
2. The three types of bee (queen, worker, drone) and their roles
3. How the colony makes decisions (swarming, queen signals, waggle dance communication)
4. How a beekeeper inspects and maintains a hive
5. Why the metaphor applies to software colonies (one short paragraph at the end)

Write in plain English, no technical software terminology except in the final paragraph. This primer is the pedagogical example Teacher will use when explaining the Agent Colony pattern later. Target ~800 words.

### overlap.yaml

A small static overlap matrix between the six agents. Set `librarian ↔ teacher` to 0.18 (watch zone) to give Equilibrium something to notice. All other pairs < 0.10.

### classifier.py

Pure function as shown in the spec. Include the REVIEW_TABLE:

```python
REVIEW_TABLE = {
    'Observing':     {'Local': 'Event-line', 'Inter-agent': 'Peer Review',     'Colony-wide': 'Governance Council', 'Boundary-crossing': 'Governance Council'},
    'Sandboxed':     {'Local': 'Event-line', 'Inter-agent': 'Peer Review',     'Colony-wide': 'Governance Council', 'Boundary-crossing': 'Governance Council'},
    'Bounded':       {'Local': 'Event-line', 'Inter-agent': 'Event-line',     'Colony-wide': 'Peer Review',         'Boundary-crossing': 'Governance Council'},
    'Self-Directed': {'Local': 'Event-line', 'Inter-agent': 'Event-line',     'Colony-wide': 'Peer Review',         'Boundary-crossing': 'Peer Review'},
}
```

### review_regime.py

Implements the §7.4 formula as a thin wrapper around classifier.py. Exports `determine_review_regime(action, context) -> str`.

### graduation.py

Generates a graduation checklist dict for a given capability proposal. Returns a dict with `evidence_requirements` (list of {id, description, status}), `approval_requirements` (list of {id, assigned_to, status}), `external_actions` (list of {id, blast_radius, review_regime}), and `summary`. Writes the checklist to `state/graduation-checklists/<timestamp>-<agent>-<capability>.yaml` when called.

### state/kb/beekeeping.md

Initial seeded KB entry — a condensed structured version of the primer, formatted as Librarian would have written it (with provenance header, topic tags, cross-references). This makes the first `teacher.serve` call work from cycle one.

Frontmatter format:

```yaml
---
topic: beekeeping
source: corpus/beekeeping/primer.md
provenance: seeded at colony init
cross_references: []
last_updated: 2026-04-14
---
```

### run.py

CLI entry point. Accepts `--substrate={claude-code|managed-agents}` and optional `--reset` to wipe `state/` before running. Instantiates the chosen adapter, runs the nine-step lifecycle deterministically, prints a summary table at the end. Uses `argparse`.

The lifecycle driver in `run.py` calls the substrate adapter's eight operations in the correct sequence and emits expected events. The driver is substrate-independent — it is the test that portability is real.

### requirements.txt

```
anthropic>=0.40.0
pyyaml>=6.0
jsonschema>=4.0
```

(Sub-agent C may add dependencies specific to Managed Agents.)

### README.md

Top-level example README. Include:

1. Lens header: **Audience lens: Beekeeper** — with a Newcomer entry path pointing at `../../knowledge-base/writings/2026-04-12-it-takes-a-village.md` and the top-level `examples/README.md` lens map
2. What this is: one-paragraph summary
3. Why this exists: one-paragraph motivation (portability claim + Comprehension Contract exercise)
4. The six agents: short table
5. How to run: `python run.py --substrate=claude-code`
6. Links to each substrate adapter's README
7. Known limitations and deferrals
8. Links to the spec and this plan

### Final step for sub-agent A

After writing all files, run:

```bash
python -c "
import yaml, json, jsonschema
schema = json.load(open('schemas/agent-mirror-v0.2.0.json'))
import glob
for f in sorted(glob.glob('examples/teaching-colony/colony/mirrors/*.yaml')):
    mirror = yaml.safe_load(open(f))
    try:
        jsonschema.validate(mirror, schema)
        print(f'{f}: OK')
    except Exception as e:
        print(f'{f}: FAIL — {e}')
"
```

All six must report OK. If any fail, fix the Mirror (not the schema) and re-validate. Do not proceed until all Mirrors validate.

---

## Sub-agent B — Claude Code substrate adapter

**Working directory:** `/Users/david.oliver/Documents/GitHub/agent-colony-pattern`

**Write scope (all files must be inside this directory):**

- `examples/teaching-colony/substrates/claude-code/adapter.py`
- `examples/teaching-colony/substrates/claude-code/README.md`
- `examples/teaching-colony/substrates/claude-code/tests/__init__.py`
- `examples/teaching-colony/substrates/claude-code/tests/test_cycle.py`

**Inputs and assumptions:**

- `examples/teaching-colony/contract.py` will exist (sub-agent A is writing it) with a `SubstrateContract` ABC. Subclass it.
- `examples/teaching-colony/colony/` will exist with the colony definition. You may read any file under that path.
- You are NOT writing Mirrors, corpus, classifier — only the Claude Code adapter.

**Key design constraints:**

1. The adapter uses the `anthropic` Python SDK directly. The adapter itself runs OUTSIDE Claude Code — it is a normal Python program that makes API calls to Claude, orchestrating the colony. It is called "Claude Code substrate" because it mirrors the Claude Code idiom of sub-agent dispatch via the Task tool.
2. For `dispatch_agent`, the adapter makes an API call with the agent's Mirror loaded as context (system prompt or structured input). The model should be selectable — default `claude-haiku-4-5-20251001` for cost.
3. For `co_sign`, the adapter dispatches a separate Sentinel agent call and verifies the response shape before returning a Signature.
4. The adapter MUST be runnable offline for tests — include a `--mock` mode that swaps real API calls for deterministic canned responses so tests don't require API keys or network.
5. Every public method must return the exact type declared in the contract.

**README.md should include:**

- Lens header: Beekeeper
- Prerequisites (Python 3.10+, `ANTHROPIC_API_KEY` env var unless `--mock`)
- `pip install -r requirements.txt`
- `python run.py --substrate=claude-code` (run the full cycle against real Claude)
- `python run.py --substrate=claude-code --mock` (offline deterministic run)
- Estimated token cost for a full cycle (document what you measure)
- How the adapter maps each of the eight contract operations to a Claude API call or local file operation (a simple table)

**tests/test_cycle.py** must:

- Run the full nine-step lifecycle using the adapter in `--mock` mode
- Assert that Teacher's Mirror before the cycle has capabilities = `['teach_beekeeping']`
- Assert that after the graduation step, Teacher's Mirror capabilities include `'teach_agent_colony_pattern'`
- Assert that the event log has exactly one `graduation.approved` event
- Assert that the Sentinel co-sign was recorded in the audit entry
- Use pytest. Include a `conftest.py` that wipes and restores `state/` between tests.

**Final step for sub-agent B:** run `pytest examples/teaching-colony/substrates/claude-code/tests/ -v` and report the output. Do not mark yourself done until the tests pass in mock mode.

---

## Sub-agent C — Managed Agents API research + scaffolding

**Working directory:** `/Users/david.oliver/Documents/GitHub/agent-colony-pattern`

**Write scope:**

- `examples/teaching-colony/substrates/managed-agents/api-research.md`
- `examples/teaching-colony/substrates/managed-agents/adapter.py` (scaffolding only — stubs with `NotImplementedError` where the API mapping is uncertain)
- `examples/teaching-colony/substrates/managed-agents/README.md` (scaffolding, to be completed by sub-agent D)
- `examples/teaching-colony/substrates/managed-agents/tests/__init__.py`
- `examples/teaching-colony/substrates/managed-agents/tests/test_cycle.py` (scaffolding)

**This sub-agent has two distinct phases.**

### Phase 1 — Research

Research the current Anthropic Managed Agents API surface as of 2026-04. Specific questions to answer:

1. Does the Anthropic platform currently offer a "Managed Agents" product or API? Under what name? (It may be called "Agent SDK", "Managed Agents", "Agents API", "Agent Skills", or something else as of 2026-04.)
2. Can multiple named agents be defined in one session or across sessions? How are they identified?
3. Is inter-agent dispatch natively supported (one agent can call another) or must it be simulated via an orchestrator agent with a dispatch tool?
4. How is persistent state handled? Per-session only, per-agent persistent, or fully stateless with externally-managed state?
5. How are tools defined? Can a tool wrap arbitrary Python code that reads/writes local files on the machine running the adapter?
6. What SDK package would a Python adapter import? (Probably `anthropic`, `anthropic-agents`, or similar — find out the exact name and version.)
7. What are the auth requirements? Just `ANTHROPIC_API_KEY`, or does Managed Agents need an additional account setup?
8. What are the rate limit and cost implications of running the demo cycle (9 steps, ~15 LLM calls)?
9. Is streaming required, or can the demo run with batch (non-streaming) responses?
10. Are there any features (e.g., Claude "computer use", "file access", "persistent memory") that would simplify the implementation?

Use the `WebFetch` and `WebSearch` tools to research Anthropic's current documentation. Key URLs to check:

- `https://docs.anthropic.com/` (root of docs)
- `https://docs.anthropic.com/en/api/` (API reference)
- `https://docs.anthropic.com/en/docs/agents/` if it exists
- `https://www.anthropic.com/news/` for announcements
- `https://github.com/anthropics/anthropic-sdk-python` for SDK

Write findings to `api-research.md` with the following structure:

```markdown
# Managed Agents API Research — 2026-04-14

## Summary

One-paragraph finding: does a Managed Agents product exist, and in what shape?

## Questions and answers

### Q1. Does the Anthropic platform offer a Managed Agents API?

[answer with primary source URLs]

### Q2. Multiple named agents?

[answer]

... (nine more)

## Mapping to the substrate contract

| Contract operation | Managed Agents mechanism | Status |
|---|---|---|
| dispatch_agent | [...] | supported / simulated / gap |
| read_mirror | [...] | supported / simulated / gap |
| ... | ... | ... |

## Overall verdict

Can the Managed Agents adapter be built in v1.6.0? What is realistic, what must be deferred?

## Dependencies to add

[Python package(s) + version]
```

### Phase 2 — Scaffolding

Based on research, write an `adapter.py` file that:

1. Subclasses `SubstrateContract` from `examples/teaching-colony/contract.py`
2. Implements each of the eight operations with EITHER a real implementation OR a `raise NotImplementedError("Gap — see api-research.md Q<N>")` if Phase 1 concluded the operation cannot be natively supported
3. Includes a `--mock` mode analogous to sub-agent B's adapter so that tests can run offline
4. Does NOT attempt to run real Managed Agents calls in Phase 2 — the goal is to leave a buildable scaffolding for sub-agent D

Write a basic `tests/test_cycle.py` that runs the adapter in `--mock` mode through the lifecycle. Expect it to raise NotImplementedError at specific points; document those in `gaps.md` (which sub-agent D will consolidate).

Write a README.md skeleton with lens header, prerequisites placeholder, and a note at the top: "⚠️ Work in progress — this substrate is being researched and implemented in v1.6.0. See api-research.md for the current findings."

**Final step for sub-agent C:** report to the controller (1) whether the research succeeded (confidence in findings, primary sources used), (2) the overall verdict from api-research.md, (3) the number of contract operations that are fully supported, simulated, or gapped. Do not mark yourself done until these three facts are in your final message.

---

## Sub-agent D — Managed Agents adapter completion (Batch 2)

**Working directory:** `/Users/david.oliver/Documents/GitHub/agent-colony-pattern`

**Write scope:**

- `examples/teaching-colony/substrates/managed-agents/adapter.py` (complete implementation where possible)
- `examples/teaching-colony/substrates/managed-agents/gaps.md` (consolidated gap report)
- `examples/teaching-colony/substrates/managed-agents/README.md` (complete)
- `examples/teaching-colony/substrates/managed-agents/tests/test_cycle.py` (complete)

**Inputs:**

- Sub-agent C's `api-research.md` is the ground truth for what Managed Agents supports
- Sub-agent A's colony definition
- Sub-agent B's adapter as a reference pattern

**Task:**

1. Read sub-agent C's research output and sub-agent B's adapter
2. For each gapped operation in sub-agent C's scaffolding, either implement it using the Managed Agents primitives (if research supports it) or write a clear gap entry in `gaps.md` explaining why it cannot be implemented in v1.6
3. If the adapter cannot pass its mock-mode cycle test, document the specific blockers in `gaps.md` and set the adapter's status to `partial` — do not pretend it works
4. Complete the README with honest run instructions (which may be "this substrate is partial; see gaps.md for what does and does not work")

**Success criteria:**

- `gaps.md` exists and lists every unsupported operation with a reason
- `python examples/teaching-colony/run.py --substrate=managed-agents --mock` either runs the full cycle OR fails with a clear error message pointing at gaps.md
- The README does not claim more than the adapter delivers

---

## Sub-agent E — Portability test + top-level documentation (Batch 2)

**Working directory:** `/Users/david.oliver/Documents/GitHub/agent-colony-pattern`

**Write scope:**

- `examples/teaching-colony/tests/__init__.py`
- `examples/teaching-colony/tests/test_portability.py`
- `examples/teaching-colony/README.md` (amendments only — sub-agent A wrote the initial version)
- `examples/README.md` (add teaching-colony to the lens map)
- `README.md` at repo root (bump version, add v1.6.0 roadmap entry, mention teaching-colony in the examples list if present)
- `CHANGELOG.md` (prepend v1.6.0 entry)
- `CITATION.cff` (bump to v1.6.0, date 2026-04-14)

**Inputs:**

- Both substrate adapters (working or partial) from sub-agents B and D
- All existing Batch 1 outputs

**Task:**

1. Write `tests/test_portability.py` that runs the Claude Code cycle and the Managed Agents cycle in `--mock` mode, collects their event logs and final Mirror states, and diffs them.
2. The portability diff must exclude: timestamps, execution IDs, substrate-specific metadata fields (`substrate_name`, `adapter_version`). Everything else must match.
3. If the Managed Agents adapter is partial (sub-agent D marked it so), the test should `skip` with a clear reason rather than fail — but must document in its skip message that the portability claim is partial for v1.6.0.
4. Update `examples/README.md` to add a `teaching-colony` section with:
   - **Audience lens:** Beekeeper (with Newcomer entry path)
   - One-paragraph description
   - Link to run instructions
   - Note on v1.6.0 status if partial
5. Update the repo-root `README.md`:
   - Bump version badge to v1.6.0
   - Add v1.6.0 row to the roadmap table: "Teaching Colony — first substrate-portable example; first exercise of Comprehension Contract in running code"
   - Update citation to v1.6.0
6. Prepend to `CHANGELOG.md` a v1.6.0 entry with Added, Why, and Known gap sections (see the spec for exact text to include)
7. Bump `CITATION.cff` to v1.6.0 / 2026-04-14

**Success criteria:**

- `pytest examples/teaching-colony/tests/test_portability.py -v` runs (either passes or skips with clear reason)
- `examples/README.md` has a teaching-colony section at the correct position
- Repo-level README, CHANGELOG, CITATION all point at v1.6.0
- Report your status to the controller with a summary of: tests passing/skipping, Claude Code status, Managed Agents status

---

## Controller checklist (after both batches)

1. Run sub-agent A, B, C in parallel (one Agent tool call with three Agent invocations)
2. Review each sub-agent's final message for blockers and errors
3. Run sub-agent D
4. Review sub-agent D's output
5. Run sub-agent E
6. Run final verification: `pytest examples/teaching-colony/ -v` from repo root
7. `git status` — review all changes
8. Single commit with message: `feat(v1.6.0): Teaching Colony — first substrate-portable example`
9. `git tag v1.6.0`
10. `git push origin main --tags`
11. `gh release create v1.6.0 ...` with text derived from the CHANGELOG v1.6.0 entry
12. Mark task #63 complete

## Rollback plan

If Batch 1 sub-agents fail catastrophically (contract inconsistent across sub-agents, tests unrunnable), roll back all uncommitted changes and report the failure:

```bash
cd /Users/david.oliver/Documents/GitHub/agent-colony-pattern
git status
git restore --staged .
git restore examples/teaching-colony/ || true
rm -rf examples/teaching-colony/
```

Do NOT commit partial work. v1.6.0 either ships or it doesn't.

If Sub-agent D concludes the Managed Agents adapter cannot be implemented in v1.6.0 at all (research reveals a fundamental incompatibility), v1.6.0 still ships with the Claude Code substrate working and the Managed Agents substrate documented as a gap — and v1.7.0 becomes the follow-up when the blockers resolve.
