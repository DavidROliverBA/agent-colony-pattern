# Changelog

All notable changes to the Agent Colony Pattern are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.2] — 2026-04-14

### Live browser viewer for the Teaching Colony

v1.8.2 adds a browser-based live visualisation of a running Teaching Colony session. A new `viewer.py` module embeds a tiny asyncio HTTP server with Server-Sent Events that streams `state/events.jsonl` to a single-file `viewer.html` page. `chat.py` gains a `--view` flag that starts the viewer server alongside the REPL loop — one command, one URL, zero new dependencies.

Running `python -m examples.teaching_colony.chat --view` opens a browser at `http://127.0.0.1:8765`. The page renders the colony as: User node on the left, L1/L2/L3 agent bands with Registry/Chronicler/Equilibrium/Sentinel/Librarian/Teacher, Knowledge Base cells (one seeded with beekeeping), an "INTERNET (v1.9)" placeholder box, a rolling event log on the right, a live token budget gauge at the top, and a streaming answer panel at the bottom. Dispatches animate agent nodes in real time; KB reads pulse the matched topic cells; co-signs flash Sentinel; mirror updates flash the target agent. The viewer is read-only in v1.8.2 — commands are still typed in the terminal; browser input is v1.8.3 or v2.0.

### Added

- **`examples/teaching_colony/viewer.py`** — ~320 lines. Pure-stdlib asyncio HTTP server with two endpoints: `GET /` serves the HTML page, `GET /events` is the Server-Sent Events stream. Binds to `127.0.0.1` only (contract-checked). Tails `state/events.jsonl` via a background polling task (100ms). On SSE connect, sends a `viewer.initial_state` event (current budget, agent roster, KB topics) then replays the last 500 events from the log, then subscribes the connection for live updates. Heartbeats every 15s so proxies don't drop the connection. Shutdown notifies all subscribers with a sentinel so `server.wait_closed()` returns within a second.
- **`examples/teaching_colony/viewer.html`** — single-file HTML/CSS/JS/SVG page (~500 lines). Renders the merged wireframe from the v1.8.2 brainstorm: User node, L1/L2/L3 bands, six agent nodes with layer-coloured borders, KB cells, Internet placeholder labelled `v1.9`, event log strip, answer panel, token budget gauge. Connects via `EventSource('/events')`. Handles `dispatch.start`, `dispatch.complete`, `kb.read`, `kb.written`, `cosign.granted`, `mirror.updated` events with distinct CSS animations. Auto-reconnect on disconnect with 2s backoff and a "disconnected" banner. **All event-data assignments use `textContent`, never `innerHTML`** — structural XSS hygiene for when v1.9's real web-fetch content starts flowing through.
- **`examples/teaching_colony/chat.py`** — three new flags: `--view` (start viewer), `--view-port N` (default 8765, 0 for OS-picked), `--no-open` (suppress auto-open). When `--view` is set, the REPL imports viewer, starts it as an asyncio task, prints the URL, and opens the browser unless `--no-open`. Viewer shuts down cleanly on REPL exit.
- **Two new adapter events:**
  - `dispatch.start` — emitted at the top of `dispatch_agent` before the API call. The viewer uses this to animate the dispatch arrow's start edge.
  - `kb.read` — emitted from `read_kb` with the matched topic names. The viewer uses this to pulse the matched KB cells.
  Both substrates (Claude Code and Managed Agents mock path) emit the same two events.
- **`dispatch.complete` payload extended** — now carries the Anthropic usage block (`input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `model`) plus the Teacher answer text (capped at 2000 chars). Lets the viewer update the budget gauge and answer panel purely from the event stream, without peeking at adapter internals.
- **Tests** — 15 new tests in three modules:
  - `tests/test_viewer_server.py` — 8 tests covering `/health`, `/` serving the HTML, `/events` initial state, existing-log replay, live tail picking up new writes, 127.0.0.1-only binding, 405 on POST, unknown path returning 404. Uses a raw socket + explicit timeout for SSE reads (urllib's `resp.read()` hangs on bodies with no Content-Length).
  - `tests/test_viewer_html.py` — 6 structural checks: required SVG ids present, all six agent nodes present, required JS function names present, `.innerHTML` not used anywhere (XSS guard), EventSource connects to `/events`, v1.9 deferrals honestly labelled.
  - `tests/test_chat_view_flag.py` — subprocess end-to-end smoke: runs `chat.py --mock --view --no-open --view-port 0`, reads the URL from stdout, fetches `/`, asserts 200 + `<svg` in the body.

### Changed

- **`examples/teaching_colony/README.md`** — new "The live viewer (v1.8.2)" subsection with the `--view` command, what the viewer shows, the read-only scope, the localhost-only security note, and the clean shutdown behaviour.
- **`CHANGELOG.md`, `CITATION.cff`, repo-root `README.md`** — v1.8.2.

### Test results

```
91 passed, 3 deselected (live), 2 xfailed in 2.24s
```

15 more tests than v1.8.1. The full suite still runs in under three seconds — adding a live HTTP server to a Python package didn't bloat the test time once the shutdown path was tightened.

### Known gaps after v1.8.2

- **No browser input.** The user still types commands in the terminal. Bidirectional browser-to-REPL control is v1.8.3 or v2.0.
- **No research walk animation.** The Internet node is a static dashed placeholder. v1.9's `fetch_url` events will animate it without a v1.8.2 layout change.
- **No past-session replay.** The viewer shows the current live session only. Replay is v2.0.
- **No mobile layout.** Desktop browser only, wireframe is ~900px wide.
- **No theme switching.** Dark only.
- **No mid-stream token counter.** The budget gauge updates on `dispatch.complete`, not as tokens are being spent. True streaming token counts require Anthropic streaming API hooks, which is v2.0.

### Why this shipped as v1.8.2

v1.8.0 was "live Claude dispatch". v1.8.1 was "§7 enforcement hole closed after review". v1.8.2 is "a reader can now see the mechanism work". Each increment is its own commit-test-tag-release cycle. The merged-wireframe brainstorm with the visual companion produced a shape that was approved before a single line of code was written, which is why the implementation was a straight-line sequence of seven files and two adapter edits.

---

## [1.8.1] — 2026-04-14

### DSL dual-key bypass closed — §7 enforcement hardened

v1.8.1 closes a latent bypass in the semantic change DSL that the external review of v1.8.0 flagged. Before this patch, `_apply_changes` had a backwards-compat fallthrough that silently deep-merged any unknown top-level key as a literal YAML patch. A caller passing the legacy `capability_add` name (singular — the v1.6.x bug key) bypassed the DSL entirely: the change was classified as `mirror_patch` (Local blast radius), the blast-radius-ceiling check passed trivially, the forbidden-list keyword match missed, and the new capability ended up as a floating top-level YAML stanza. The exact v1.6.x failure mode the DSL was meant to kill.

v1.8.1 replaces the fallthrough with a hard whitelist.

### Changed

- **`examples/teaching_colony/substrates/claude_code/adapter.py`** — `_apply_changes` now raises `ValueError` for any top-level key not in the `KNOWN_DSL_KEYS` set (`{"add_capability", "remove_capability", "patch"}`). Legacy names that look like DSL keys get a "did you mean …" hint in the exception message.
- **`examples/teaching_colony/substrates/managed_agents/adapter.py`** — same check in the Managed Agents adapter's mock-mode inline DSL handler. Both substrates reject unknown keys identically.
- **`examples/teaching_colony/tests/test_contract_enforcement.py`** — four new regression tests:
  - `test_legacy_capability_add_key_is_rejected` — provokes the exact v1.6.x bypass from the review
  - `test_random_unknown_dsl_key_is_rejected` — generalises to any non-DSL key
  - `test_patch_key_still_works_for_legitimate_literal_updates` — confirms the explicit `patch` escape hatch survives
  - `test_mixed_dsl_and_legacy_key_rejects_entire_change` — atomic gate: a mix of valid and invalid keys rejects the whole change before any mutation

### Existing tests migrated

Four tests were using the pre-DSL nested-dict form `{"capabilities": {"capabilities": [...]}}` to update capabilities. That form was unknown to the DSL and used to fall through to deep-merge — now it raises. Migrated to the semantic `add_capability` key:

- `substrates/claude_code/tests/test_cycle.py::test_update_mirror_records_audit_and_hashes`
- `substrates/claude_code/tests/test_cycle.py::test_full_lifecycle_mock` (inline lifecycle)
- `substrates/managed_agents/tests/test_cycle.py::test_update_mirror_mock_returns_audit`
- `tests/test_portability.py::_run_lifecycle` + `_ma_persists_mirror_updates` probe

### Test results

```
76 passed, 3 deselected (live), 2 xfailed
```

Four more tests than v1.8.0 (the new regression suite). Every pre-existing mock-mode test still green. The live tests and Managed Agents xfails are unchanged.

### Why this was a real bug and not just a style preference

The §7 Comprehension Contract has three structural invariants (closed action enum, co-sign, append-only audit log). v1.7.0 made them real in `update_mirror` — but the enforcement ran against a *classified* action class, and classification came from `_change_action_class` which inferred from the DSL keys. Unknown keys fell through to `mirror_patch`, which had a default blast radius of `Local`, which any agent's ceiling trivially accepts, which meant the forbidden-list check also missed because its keyword matching relied on DSL-aware descriptions. The review's exact words: *"the Comprehension Contract enforcement can still be fully bypassed by a caller using the legacy key name."*

v1.8.1 removes the conditional. The enforcement story no longer has a qualifier.

### Why ship this as v1.8.1 rather than fold it into v1.9

The review landed after v1.8.0 shipped and after v1.8.0's memory was written. Folding this into v1.9 would mean releasing v1.8 with a known governance hole for however long v1.9 takes. That repeats the v1.6.x failure mode. Tiny targeted patch, ship now, keep v1.9 a clean increment.

---

## [1.8.0] — 2026-04-14

### Teaching Colony runs on real Claude for the first time

v1.8.0 is the first increment of the Teaching Colony's interactive v2.x arc. It adds a long-running REPL (`chat.py`) and fills in the Claude Code adapter's live-mode dispatch path with real Anthropic API calls, prompt caching, and model tiering. After v1.8.0 ships, a reader can type `ask what do you know about beekeeping` at a colony prompt and receive a real Claude-generated answer grounded in the seeded primer.

**This is the first release of the Agent Colony pattern that costs money to use.** The README's Teaching Colony section explains the cost envelope in detail: roughly $2-5 for a full default-budget session (500,000 tokens) with the recommended model tiering.

### Added

- **`examples/teaching_colony/chat.py`** — asyncio-based interactive REPL. Commands in v1.8.0: `ask <question>`, `help`, `quit`. Forward-looking commands (`research`, `status`, `cancel`, `knows`, `capabilities`) are routed helpfully to a "coming in v1.9+" message.
- **Live-mode `ClaudeCodeAdapter.dispatch_agent`** — fills in the `_real_dispatch` method with:
  - **Prompt caching** via `cache_control: {"type": "ephemeral"}` on the agent's Mirror system prompt. Repeat dispatches of the same agent within 5 minutes pay ~10% of the system-prompt cost.
  - **Model tiering** via the new `AGENT_MODELS` dict — `claude-sonnet-4-6` for Teacher/Librarian (real reasoning), `claude-haiku-4-5-20251001` for the four supervisory agents (structured decisions).
  - **Prose-vs-JSON system prompts** — Teacher and Librarian get flexible pedagogical prompts; Registry, Chronicler, Equilibrium, and Sentinel get JSON-strict prompts with explicit schemas and a one-retry fallback for malformed responses.
  - **`last_response_usage`** attribute exposed so tests can inspect the cache-hit state directly.
- **`examples/teaching_colony/colony/logic/budget.py`** — `Budget` class tracking all four Anthropic usage counters (input, output, cache-creation, cache-read). Warning threshold at 80%, hard stop at 100%. `TEACHING_COLONY_TOKEN_BUDGET` env var with safe fallback to 500,000 on invalid values.
- **`examples/teaching_colony/tests/test_budget.py`** — 27 unit tests covering construction, env var parsing, usage recording, thresholds, and formatting. Over-tested relative to the class's size because a subtle off-by-one in these checks would silently allow overspend.
- **`examples/teaching_colony/tests/test_repl_smoke.py`** — 9 subprocess tests that run `chat.py` in mock mode and verify: banner renders, help lists commands, `ask beekeeping` fires the canned "worker" answer, unknown commands route helpfully without traceback, empty lines are ignored, budget overrides work via both env var and `--budget` flag, ask+quit produces a final budget line.
- **`examples/teaching_colony/tests/test_live_dispatch.py`** — 3 gated tests that actually call Claude: teacher dispatch with real beekeeping content; prompt cache hit on the second dispatch (directly verifies `cache_read_input_tokens > 0`); sentinel dispatch returns parseable JSON. Gated behind `@pytest.mark.live` and `ANTHROPIC_API_KEY` — never run in default CI.
- **`examples/teaching_colony/pytest.ini`** — registers the `live` marker so `pytest -m "not live"` skips the gated tests cleanly.
- **Interactive-mode section in `examples/teaching_colony/README.md`** — prerequisites, start commands, command list, v1.9+ deferrals, budget override instructions, cost table.

### Changed

- **`examples/teaching_colony/substrates/claude_code/adapter.py`** — `ClaudeCodeAdapter.__init__` accepts an optional `budget: Budget` parameter. `_real_dispatch` completely rewritten for v1.8.0 requirements. New module-level constants `AGENT_MODELS` and `PROSE_AGENTS`.
- **`examples/teaching_colony/README.md`** — restructured to cover both the scripted v1.7 walkthrough and the new v1.8 interactive REPL side-by-side. The scripted walkthrough is preserved unchanged under a "Scripted walkthrough — v1.7.0" section.
- **`CHANGELOG.md`, `CITATION.cff`, repo-root `README.md`** — v1.8.0.

### Test results

```
72 passed, 3 deselected (live tests), 2 xfailed
```

The 3 deselected are the live Claude-API tests (run with `pytest -m live` and `ANTHROPIC_API_KEY` set). The 2 xfails are unchanged from v1.7.0 — live-mode Managed Agents `dispatch_agent` and `update_mirror`, still v1.x+ future work.

### Known gaps after v1.8.0

- The REPL uses a single-shot "pick the best KB entry and send it" retrieval, not real RAG. Fine while the KB has one entry; revisit when v1.9's research walks start adding more.
- `ask` dispatches to Teacher only. It cannot yet dispatch to other agents by name. `ask sentinel co-sign this` kind of syntax is v2.0.
- Tokens-used display is updated only after a dispatch completes, not mid-stream. Streaming responses would give a live counter but that's v2.0 polish.
- No research walks yet. `research`, `status`, `cancel`, `knows`, `capabilities` are all v1.9+.
- Managed Agents substrate live-mode `dispatch_agent` and `update_mirror` still raise `NotImplementedError` (2 xfails). Requires research-preview allowlist.

### Why increment v1.8 rather than shipping the whole v2.0 arc at once

The review at v1.7.0 — where a whole example went out with the central claim false on the happy path — is still fresh. Shipping live-mode dispatch on its own means I can verify it works against a real model before layering research walks on top, and it means the roadmap moves by one rung (from "v2.0 planned" to "v1.8 shipped, v1.9 planned"). Each increment is its own commit-test-tag-release cycle. v1.9 adds research walks; v2.0 adds the full command set and session persistence.

---

## [1.7.0] — 2026-04-14

### Honest Teaching Colony — response to external review

v1.7.0 is a correctness release for the Teaching Colony example. It responds to an external review ([`examples/teaching_colony/docs/review-2026-04-14.md`](examples/teaching_colony/docs/review-2026-04-14.md)) which found six concrete bugs in v1.6.x and described the v1.6.x example as *"a 4,300-line artefact whose headline demonstration doesn't hold up under a single run-and-inspect"*. Every finding is addressed.

### What was broken in v1.6.x

1. **The mock dispatch path was dead code.** `run.py` called the adapter with one input shape; the adapter's canned responses keyed on a different shape. Both Teacher dispatches returned `{ok: True}`. The README's headline claim — "Teacher answers a question it could not have answered at boot time" — was false.
2. **The capability addition landed in the wrong place in the Mirror.** The driver passed `{"capability_add": {...}}` and the adapter's deep-merge wrote a new top-level YAML key instead of appending to `capabilities.capabilities[]`. A reader who followed the README's instruction to `cat colony/mirrors/teacher-agent.yaml` saw Teacher still only teaching beekeeping.
3. **The Comprehension Contract was not enforced anywhere.** `substrate-contract.md` promised `update_mirror` would check `blast_radius_ceiling`, `self_evolution_scope.forbidden`, and co-signer policy freshness. None of those checks existed in the adapter. The demonstration the §7 contract was supposed to make — that governance *bites* — was ceremonial.
4. **The event stream was duplicated.** Driver emitted `kb_write`/`cosign`/`mirror_update`; adapter emitted `kb.written`/`cosign.granted`/`mirror.updated`. Same logical actions, two names each.
5. **Mirror writes polluted git-tracked files.** The adapter wrote to `colony/mirrors/`, so every run left `teacher-agent.yaml` modified in the reader's working copy.
6. **The classifier accepted caller-supplied `blast_radius` overrides.** A confused or malicious caller could downgrade a Colony-wide action to Local.

### What v1.7.0 changes

**Fix 6 — Classifier gate.** For any action class in `ACTION_BLAST_RADIUS`, the table wins regardless of caller input. Caller override only applies to action classes the table doesn't know. Closes the §7 property "callers cannot classify their own actions".

**Fix 2 — Semantic change DSL.** `update_mirror` now accepts `{add_capability: {...}}`, `{remove_capability: "name"}`, `{patch: {...}}` as explicit semantic instructions. The adapter interprets these as operations on `capabilities.capabilities[]`, not as literal YAML keys. Unrecognised top-level keys fall through to deep-merge for backwards compatibility.

**Fix 1 — Wire the mock dispatch path.** `_mock_response` normalises the agent id (strips `-agent` suffix) and keys on the actual input shape the lifecycle driver sends. The canned beekeeping and Agent Colony answers now fire. Their texts include the words "worker" and "Mirror" respectively — the words the new end-to-end test asserts against.

**Fix 3 — Comprehension Contract enforcement in `update_mirror`.** Adapters now perform six checks before writing: co-signer presence, classifier invocation, blast-radius-ceiling check, forbidden-list check, co-signer policy freshness, and only then hash-merge-write. Each check raises a specific `ContractViolation` subclass (`BlastRadiusViolation`, `ForbiddenEvolution`, `UnauthorisedCoSign`). Four new tests in `tests/test_contract_enforcement.py` provoke each check in turn. Teacher's `forbidden` list wording and `blast_radius_ceiling` were updated so the happy-path graduation succeeds under valid Peer Review co-sign — the previous wording contradicted the demo.

**Fix 4 — Single event ownership.** Adapters own adapter-internal events (`kb.written`, `mirror.updated`, `cosign.granted`, `dispatch.complete`). The driver stopped emitting duplicates (`kb_write`, `cosign`, `mirror_update`). Both substrates now emit the same event types in the same order for the same lifecycle — which is what makes the portability parity tests *finally* viable.

**Fix 5 — Mirror writes land in `state/mirrors/`.** `colony/mirrors/` is read-only-at-rest. Both adapters prefer a `state/mirrors/<agent>.yaml` overlay when reading and always write to the overlay. `--reset` wipes `state/mirrors/` along with events and checklists. Running the example no longer pollutes git-tracked files.

### New tests (the v1.7.0 testing innovation)

- **`tests/test_walkthrough.py`** — end-to-end test that runs the lifecycle driver and asserts observable properties of `state/events.jsonl` and the Teacher Mirror. Seven assertions covering the README's walkthrough promises: beekeeping answer contains "worker"; Agent Colony answer contains "Mirror"; Teacher has both capabilities under `capabilities.capabilities[]`; no floating `capability_add` key; classification event with `review_regime: Peer Review`; `cosign.granted` event with `granted: True`; `mirror.updated` event with differing pre/post hashes. **This test is the mechanism that prevents tests-vs-demo drift in future releases.**
- **`tests/test_contract_enforcement.py`** — five tests: happy-path graduation succeeds; `BlastRadiusViolation` raised when ceiling is exceeded; `ForbiddenEvolution` raised when the forbidden list names the change; `UnauthorisedCoSign` raised when co-signer has no matching pre-registered policy; `UnauthorisedCoSign` raised when `co_signer` is empty.

### Portability parity — v1.6.x skips become v1.7.0 passes

The two portability tests that were marked `skip` in v1.6.x — `test_event_log_types_match` and `test_teacher_mirror_final_state_matches` — now pass. Both substrates produce byte-identical event sequences and Mirror final states in mock mode. The 42-vs-22 event-count gap from v1.6.1's honest note is gone: both substrates now emit 22 events (the adapter-owned set).

### Other changes

- `examples/teaching_colony/docs/review-2026-04-14.md` — the external review preserved verbatim as the before-state that v1.7.0 corrects.
- `examples/teaching_colony/colony/corpus/README.md` — new snapshot note explaining why the corpus is a copy (not a symlink), what it contains, how to refresh it, and what the snapshot date is.
- `examples/teaching_colony/substrate-contract.md` — the enforcement paragraph is rewritten to name the six checks, and the change DSL gets its own section. The "Event Memory queries are a specialised form of `read_kb` in every substrate we tried" claim (which was aspirational — neither adapter implemented it) is replaced with an honest statement that direct JSONL scans are fine for v1.7.0 and that a v2 substrate with a real event store may want to add `read_event` back.
- `CHANGELOG.md`, `CITATION.cff`, repo-root `README.md` — v1.7.0.

### Known gaps after v1.7.0

- Live-mode Managed Agents `dispatch_agent` and `update_mirror` still raise `NotImplementedError` (2 xfails in the test suite). These require the Managed Agents research-preview allowlist and real API calls — v1.7.x or v1.8+. Mock-mode portability parity is fully achieved.
- The Managed Agents live-mode `write_kb` and `co_sign` were previously xfailed but v1.7.0 turns them into colony-policy operations that work in both modes (KB writes are local file ops; co-sign is pre-registered-policy lookup). These two xfails are removed and replaced with positive tests.

### Verification

```
36 passed, 2 xfailed in 0.74s
```

The 2 xfails are the remaining live-mode `dispatch_agent` and `update_mirror` operations — honest future work. Everything else is green.

---

## [1.6.1] — 2026-04-14

### Added
- **`examples/teaching_colony/docs/design-spec.md`** — copy of the working design spec from the author's vault, now committed in the public repo so readers have the Architect-lens view of the example. Includes provenance header.
- **`examples/teaching_colony/docs/implementation-plan.md`** — copy of the implementation plan that produced v1.6.0, including the five-sub-agent parallel execution strategy, write-scope boundaries, and coordination rules.
- **`examples/teaching_colony/README.md`** — a complete "How to use this example" walkthrough with three progressive run scenarios: (1) first run on Claude Code to see the full lifecycle; (2) reset and re-run to verify determinism; (3) run on Managed Agents to see the portability claim concretely. Each scenario states what to run, what to expect, where to look, and how to verify. The walkthrough is honest about the event-count difference between substrates (Claude Code ~42, Managed Agents ~22) and points at `gaps.md` for the known reason.

### Changed
- `examples/teaching_colony/README.md` — replaced the thin "How to run" section with the three-scenario walkthrough, replaced the broken vault-path links to spec/plan with links to the newly-committed copies under `docs/`, and fixed the `substrates/claude-code/` → `substrates/claude_code/` link (and similarly for managed_agents).
- `examples/teaching_colony/substrates/claude_code/README.md` — added a "Design context" line pointing at the design spec and implementation plan under `../../docs/`.
- `examples/teaching_colony/substrates/managed_agents/README.md` — same.
- `README.md` at repo root — version badge v1.6.0 → v1.6.1.
- `CITATION.cff` — version v1.6.1.

### Why

Two things were missing from v1.6.0 that a first-time reader would immediately notice. First, the Architect-lens artefacts — the design spec and the implementation plan — lived only in the author's private vault. The example claimed to serve all five lenses but the Architect lens was a broken link. Copying both documents into `examples/teaching_colony/docs/` closes that gap. Second, the top-level README had the commands but not a walkthrough — a reader had no guided way to actually *use* the example, see what it produces, and check that the graduation actually happened. The three-scenario walkthrough gives a clean path: first run to see the lifecycle, second run to verify determinism, third run to see portability concretely. This is a docs-only patch; no code changes.

### No code changes

- Adapters unchanged
- Colony definition unchanged
- Tests unchanged (26 passed, 2 skipped, 4 xfailed — identical to v1.6.0)
- No version bump to any dependency

---

## [1.6.0] — 2026-04-14

### Added
- **`examples/teaching_colony/`** — a six-agent substrate-portable Agent Colony that teaches the Agent Colony pattern, using beekeeping as the running pedagogical example. Six agents (Registry, Chronicler, Equilibrium, Sentinel, Librarian, Teacher), a colony knowledge base, a structural classifier, a graduation checklist generator, and a CLI lifecycle driver (`run.py`).
- **`examples/teaching_colony/contract.py`** — `SubstrateContract` ABC defining the eight operations L4 owes L1–L3: `dispatch_agent`, `read_mirror`, `update_mirror`, `record_event`, `read_kb`, `write_kb`, `co_sign`, `classify_action`. This is the first time the substrate contract is formalised in code.
- **`examples/teaching_colony/substrates/claude_code/`** — Claude Code substrate adapter, working in mock mode. Implements all eight contract operations with deep-merge-and-hash mirror updates, JSONL event logging, and a deterministic mock dispatcher. Unit tests plus a full lifecycle test.
- **`examples/teaching_colony/substrates/managed_agents/`** — Managed Agents API substrate adapter scaffolding. Mock-mode dispatch, co-sign, classify and event-log writes are working; live-mode operations are gated behind `NotImplementedError` pending v1.7+. Includes `api-research.md` — the first honest adequacy report of a real substrate against the Agent Colony contract.
- **First running exercise of the Comprehension Contract (§7)** — Librarian detects KB coverage crossing a threshold, proposes Teacher acquire a new capability, the structural classifier fires with the trust-tier × blast-radius review regime, Sentinel co-signs, Teacher's Mirror is updated with an append-only audit trail including pre/post state hashes. Until v1.6.0 §7 had only ever been described on paper.
- **`examples/teaching_colony/tests/test_portability.py`** — cross-substrate portability test. Asserts (unconditionally) that classifier output is substrate-independent; that Claude Code completes the minimal lifecycle end to end in mock mode; and that Managed Agents completes every mock-implemented operation. Full event-sequence and Teacher-Mirror parity tests are skipped in v1.6.0 with a reason pointing at `gaps.md` — live-mode parity is v1.7+.
- **Lens-mapped READMEs** at `examples/teaching_colony/`, each substrate subdirectory, and the repository-level `examples/README.md` — every level names its audience lens (Beekeeper) and the Principle 7 framing.

### Changed
- **`examples/README.md`** — added teaching-colony to the lens map and the example list; Beekeeper row now points to hello-colony → hello-colony-runtime → teaching-colony.
- **`README.md`** — version v1.5.0 → v1.6.0; Examples row updated to mention teaching-colony; Status section rewritten for v1.6.0; roadmap entry added for v1.6.0; v1.6+ renamed v1.7+; citation line updated.
- **`CITATION.cff`** — version v1.6.0, date 2026-04-14.

### Why

Principle 2 (*Identity over implementation*) and Principle 4 (*Longevity by design*) were paper claims until v1.6.0. The teaching colony demonstrates both in running code for the first time: the *same* colony, with the *same* six Agent Mirrors and the *same* structural classifier, runs behind two substrate contracts that differ in almost every implementation detail. The Comprehension Contract (§7) had been fully specified in v1.4.0 but had never done real work — v1.6.0 shows the classifier firing, the co-sign being issued, and the append-only audit trail being written as a graduation actually happens. The teaching mission is Principle 7 (*Accessibility through abstraction*) in action: the colony's purpose is to help other people learn the pattern, and the beekeeping metaphor serves as the running pedagogical example throughout the lifecycle — a worker Librarian foraging the KB corpus, a Sentinel guarding the hive entrance, a queen-less colony that decides together. Beekeeping is the metaphor the Newcomer can hold; the substrate contract is what the Architect argues about; the same colony serves both lenses.

### Known gap

The Managed Agents substrate adapter ships with mock-mode fully working — dispatch, co-sign, classify, read/write of the local event log — and all live-mode operations gated behind `NotImplementedError`. The mock `update_mirror` returns a zeroed `AuditEntry` without persisting the change, and the mock `write_kb` is a no-op. Consequently the portability parity tests for full event-sequence equality and Teacher-Mirror final-state equality are *skipped* in v1.6.0 with a reason pointing at [`examples/teaching_colony/substrates/managed_agents/gaps.md`](examples/teaching_colony/substrates/managed_agents/gaps.md) — the honest adequacy report documenting which contract operations the Managed Agents API can and cannot support. Live-mode completion is targeted for v1.7+.

---

## [1.5.0] — 2026-04-14

### Added
- **Principle 7 — Accessibility through abstraction** added to the core set in `manifesto.md`, `thesis.md` §3, `specification.md` §1, and `README.md`. The principle states that the colony must be understandable at every audience's depth, no deeper; complexity is an investment paid once upfront so that each audience sees only what it needs. Corollary: *ease is earned* — the simple surface is the output of hard substrate work, not the absence of it.
- **`specification.md` §1 — Audience Lenses** — new subsection of §1 Definition and Core Principles, parallel in shape to Scales of Application. Defines the canonical realisation of Principle 7 as a five-lens model: Newcomer → Observer → Operator → Beekeeper → Architect. Each lens has a canonical artefact in this repository. Lenses are a *view* over the full colony, not a *configuration* that simplifies it — all mechanisms are present and enforced at every lens. Sequential by default with re-entry always possible; pacing can compress; artefact mapping is required for conformance; lenses can be collapsed or split per context.
- **`specification.md` §8.5.1** — one new conformance anti-pattern: **lens inversion** (forcing low-depth audiences to read high-depth artefacts to use the colony at all).
- **`diagrams/lens-traversal.svg`** — new diagram visually representing the five sequential lenses, their canonical artefacts, and the re-entry arrow from any lens back to Newcomer.

### Changed
- **`README.md`** — six principles → seven; version badge v1.4.0 → v1.5.0; roadmap entry added for v1.5.0; status section rewritten; citation line updated.
- **`CITATION.cff`** — version v1.5.0, date 2026-04-14.
- **`manifesto.md`** — "Six Principles" heading → "Seven Principles"; new Principle 7 section added with the beekeeper framing and the ease-is-earned corollary.
- **`thesis.md`** — "Six Principles" heading → "Seven Principles"; new Principle 7 subsection added to §3.

### Why

Principle 7 formalises what the pattern had always been doing implicitly. The repository already has artefacts pitched at different depths — the village article on Medium, the equilibrium playground, the hello-colony-runtime, the specification, the thesis — but until v1.5.0 this stratification was ad-hoc. Naming the lenses makes it explicit, testable, and conformance-relevant. The beekeeper analogy captures the correct disposition: most people understand what a beehive is and what the queen bee does, but will never understand the processes, jobs, and roles all the bees perform unless they become beekeepers. Most audiences for an Agent Colony need a metaphor and an outcome, not a mechanism. Forcing them to read the specification to benefit from the pattern was a violation of a principle that had not yet been named.

### Known gap

The existing six mechanism diagrams (four-layer architecture, equilibrium system, maturity model, agent mirror, memory cycle, evolutionary context) are pitched at the Beekeeper/Architect level. By Principle 7's own test, the Newcomer and Observer lenses are under-served in diagram form — they would need companion "village-level" visual explanations that do not yet exist. This is deferred to v1.6+ rather than shipping v1.5.0 pretending the existing diagrams already serve all five lenses.

---

## [1.4.0] — 2026-04-13

### Added
- **`specification.md` §7 — The Comprehension Contract** — new first-class mechanism formalising the requirement that no action executes without a comprehension artefact matching the agent's trust tier and blast radius. Fourteen sub-sections covering: the dark code problem (Jones 2026), the contract invariant, three timescales of comprehension (Structural Classifier, quarantine/composed actions, audit/Lesson Memory feedback), the review regime formula with trust-tier × blast-radius table, three load-bearing properties, the classifier as Constitutional, honest limits (delayed-consequence residual), Agent Mirror changes (v0.2.0 fields), relationship to existing mechanisms, critical path position (§7.10), NFRs in the Mirror (§7.11), multi-perspective valuation (§7.12), the Graduation Checklist (§7.13), and false comprehension artefacts / micro-misalignment (§7.14, IndyDevDan 2026).
- **`specification.md` §8.5.1** — two new conformance anti-patterns: actions without comprehension artefacts; Structural Classifier rules not in Constitutional Memory.

### Changed
- **`specification.md`** — §7 Standards Landscape → §8; §7.5 Conformance → §8.5 (sub-sections renumbered accordingly); §8 Deliverables → §9. Specification status updated to v1.4.0.
- **`thesis.md`** — §3 extended with Comprehension Contract as the fourth mechanism alongside Equilibrium, Memory, and Epistemic Discipline.

### Why

The Comprehension Contract was designed and implemented as a Mirror schema extension (v0.2.0) and hello-colony example in v1.3.0. v1.4.0 makes it a formal specification section — the mechanism is now fully described, its relationship to all existing mechanisms documented, and its conformance implications stated. The dark code response (Jones 2026) is now not just named in the knowledge base but answered in the specification itself.

## [1.3.0] — 2026-04-13

### Added
- **`schemas/agent-mirror-v0.2.0.json`** — updated Agent Mirror schema adding four new optional sections: `comprehension_contract` (trust tier, pre-registered policies, audit rate, blast radius ceiling, classifier version), `nfrs` (inherited colony NFRs plus agent-specific commitments), `valuation` (self / peer / audit / human multi-perspective scoring), and `critical_path` inside the `relationships` object (structural and dynamic critical path flags). Previous `agent-mirror-v0.1.json` kept intact — both versions coexist.
- **`examples/hello-colony/graduation-checklists/finance-agent-v1.0-to-v1.1.yaml`** — the first graduation checklist. Records the finance domain agent's path from v1.0 to v1.1 (suppressing accreted self-monitoring capabilities that caused an overlap score of 0.24 with equilibrium-agent). Three evidence requirements, two approval requirements, three external actions — each pre-classified with blast radius and review regime.
- **`examples/hello-colony/graduation-checklists/README.md`** — explains what graduation checklists are, who maintains them (Registry Agent), and what each field means.
- **`examples/hello-colony-runtime/`** — Level 1 demonstration: a deterministic Python simulation that loads the hello-colony YAML files, validates them against the v0.2.0 schema, and simulates four colony events (bootstrap, equilibrium check, security patch co-sign, graduation query). No LLM calls, no external services. Run with `python runtime.py` after `pip install -r requirements.txt`.
- **`examples/equilibrium-playground/`** — Level 1 demonstration: a self-contained HTML visualisation of the Equilibrium System. D3.js overlap matrix heatmap colour-coded by threshold zones. Threshold sliders, add/remove agent controls, inject-workload button, three live index gauges (Overlap, Concentration, Vitality). No build step — open `index.html` in any browser.

### Changed
- **All 6 hello-colony agent YAML files** — extended with `comprehension_contract:`, `nfrs:`, and `valuation:` top-level sections, and `critical_path:` inside `relationships:`. Values reflect each agent's real position in the colony: Sentinel has two pre-registered policies (cosign + threat escalation); finance domain agent is Observing tier with 100% audit rate; v1.1 registry agent shows three peer interactions (calibrating).
- **`examples/hello-colony/colony-snapshot.yaml`** — new `comprehension_contract_overview:` section added at the bottom, capturing trust tier distribution, structural critical path agents, and a pointer to the active finance graduation checklist.
- **`examples/hello-colony/README.md`** — new section "New in v1.3.0: Comprehension Contract fields" added, explaining each new Mirror section.
- **`examples/README.md`** — new file (or updated) listing all three example directories with usage instructions.
- **`schemas/README.md`** — updated to document v0.2.0 alongside v0.1.

### Why

The pattern was previously articulated but not demonstrated. The Comprehension Contract (§7 of the forthcoming v1.3.0 specification) introduces the most significant new mechanism since v1.0: every action produces a pre-action comprehension artefact matched to the agent's trust tier and blast radius. The hello-colony examples now show what an agent's Mirror looks like when it carries this information. The live runtime shows the event logic running — schema validation, equilibrium flagging, security co-sign verification, graduation query — as deterministic code rather than description. The equilibrium playground makes the three indices interactive so the pattern's dynamics are visceral rather than abstract. The pattern now demonstrates what it describes.

## [1.2.2] — 2026-04-13

### Added
- **`knowledge-base/references/dark-code.md`** — captures Nate B Jones's 2026 framing of *dark code* (code that was never understood by anyone at any point in its lifecycle), its two structural breaks (runtime tool selection; velocity outpacing comprehension), the Amazon Kiro / retail outage incident record as public preview, and Jones's three prescribed layers (spec-driven development, context engineering, comprehension gates). The file maps each of Jones's layers onto Agent Colony mechanisms — Agent Mirror, Colony Memory, Equilibrium System, Coexistence Boundary — and records where the pattern extends beyond his framing (lifecycle identity across technology generations, population dynamics, mutual coexistence).

### Changed
- **`manifesto.md`** — new paragraph in "What Is an Agent Colony?" introducing dark code as the contemporary name for the failure mode the pattern exists to prevent, with the Amazon Kiro incident as public preview and the core reframing: *discipline that lives only in human habit erodes under velocity pressure; discipline that lives in the architecture erodes more slowly*. Links to the full reference in the knowledge base.
- **`thesis.md`** — new paragraph in §1 "The Problem" citing Jones (2026) as corroborating practitioner evidence for the comprehension gap claim, with the explicit argument that Jones's three layers are necessary but insufficient at the population level and that the Agent Colony raises each layer from per-module to per-agent-and-per-generation, per-colony-lifetime, and population-dynamics scope respectively.
- **`knowledge-base/references/README.md`** — adds dark-code.md to the structure listing.

### Why

The manifesto and thesis both argue *historically* — every shift in distributed systems has faced the same question. That framing is correct but abstract; a reviewer from an engineering org under AI adoption pressure reads it as a philosophical observation rather than as a description of their present liability. Jones's *Dark Code* gives the same argument a contemporary name, a documented incident catalogue, and a regulatory deadline (the EU AI Act enforcement date in August 2026). Adding it to the knowledge base is not decoration — it changes the answer to *"what happens if we do not build this?"* from a hypothetical to a case study. It also strengthens the lesson *acknowledgment-is-not-mitigation* by showing that Jones independently reached the same conclusion ("observability is retrospective; guardrails are reactive; adding layers makes it worse") from the practitioner side.

## [1.2.1] — 2026-04-13

### Added
- **`knowledge-base/writings/`** — new subfolder for things written *about* the pattern. Articles, blog posts, talks. Each entry is preserved verbatim with a link to the canonical published version.
- **First article: *It takes a village — the Agent Colony definition*** by David R Oliver, published on Medium 2026-04-12. The lay-audience introduction to the pattern, using the metaphor of a village for the six principles, the colony memory layers, and the epistemic discipline. Captured at [`knowledge-base/writings/2026-04-12-it-takes-a-village.md`](knowledge-base/writings/2026-04-12-it-takes-a-village.md). [Read on Medium](https://medium.com/@davidroliver/it-takes-a-village-the-agent-colony-definition-32b9bd714bb8).

### Changed
- **`README.md`** — surfaces the article in two places: a callout near the top ("New here? Start with the lay-audience article"), and as the first entry in the "Scope and audiences" section, recognising that not every reader is a technical practitioner.
- **`knowledge-base/README.md`** — structure listing now includes the `writings/` subfolder with a note on how it complements the other three (incoming feedback, outgoing writings, distilled lessons, inherited references).

### Why

The article is the first time the Agent Colony pattern has been written for a non-technical audience. It belongs in the knowledge base alongside the feedback and lessons because it is part of the pattern's evolution — specifically, the moment the pattern moved from "thing the author thinks about" to "thing the author has explained to someone else's family". Preserving it in-repo (not just linking to Medium) means future contributors can trace what was said to whom and when, even if the live URL changes.

## [1.2.0] — 2026-04-13

### Added
- **`knowledge-base/`** — new top-level folder capturing the pattern's own evolution. Three subfolders:
  - **`feedback/`** — peer review captured as it arrives. Four rounds so far, one file per round, each with: key points raised, verdict, what changed in response, and what has not changed and why. Negative feedback kept alongside positive.
  - **`lessons/`** — insights extracted from feedback and development. Each lesson carries an evidence grade (empirical / corroborated / theoretical / inherited / anecdotal) and a note on whether it has graduated to a specification rule. Four lessons so far: *acknowledgment is not mitigation*, *diagrams must run on rules not taste*, *scale slippage is a feature when stated*, *worked examples must track the spec*.
  - **`references/`** — prior art (MAPE-K, FIPA, KQML, MOISE+ / OperA / Jason, Constitutional AI, stigmergy, holonics, Agentic Hives) and active standards watch (A2A, MCP, AGNTCY / OASF, NIST Agent Standards Initiative, AGENTS.md, IEEE P3119, ISO/IEC 42001 family). Working notes behind the thesis literature review, including concessions and disagreements the formal prose compresses.
- **`examples/demonstration-options.md`** — a design memo of ten options for building a visual demonstration of the pattern, organised against four purposes (demonstrate, educate, evaluate, prove). Includes a purpose-fit matrix, three recommended combinations at different ambition levels, and honest trade-offs. This is the first forward-looking design memo captured in the repo.

### Changed
- **`README.md`** — "What's in this repository" now lists the knowledge base and renames "Example" to "Examples" (to reflect that `examples/` now has more than just hello-colony).

### Why

The manifesto asks for interrogation, not agreement. The repo had no visible mechanism for capturing that interrogation — feedback arrived, was acted on, and disappeared into commit messages. The knowledge base closes that loop. Every substantive critique received in v1.0.0 through v1.1.6 is now a first-class artefact with traceable lineage: feedback → lesson → rule (where the lesson graduated). The pattern's own epistemic principles (evidence grades, mandatory dissent, lessons become rules) are now applied to the pattern's own development. The process the pattern prescribes for colonies is the process that built the pattern itself.

## [1.1.6] — 2026-04-13

### Added
- **`diagrams/README.md`** — shared colour palette and style conventions across all six diagrams. Explains what blue / green / purple / red / orange / yellow mean and where each is used, so the set reads as coherent rather than as six different authors.
- **`Agent Colony v1.1.6 — design, not validated`** footer stamp on every diagram. Prevents the common misreading that the diagrams describe a real running system. Matches the intellectual honesty of the prose.
- **Four-layer architecture: inter-layer arrows.** Previously the diagram was a static stack with no dynamics. Now shows: Sentinel → Mesh (monitors), Patch → Mesh (applies patches), Mesh → Response Coordinator (reports anomalies), Sentinel ↔ Patch (co-signs security upgrades — v1.1.1 reference), Mesh → Chronicler (events recorded, via left gutter), Response Coordinator → Coexistence Boundary (escalates, via right gutter).
- **Equilibrium diagram: index → failure mapping.** Each of the three detection indices now carries a small annotation mapping it to the failure mode it detects — Overlap and Concentration detect consolidation, Vitality detects either extreme.
- **Maturity model: labelled trust gates** — each column's gates now carry a specific criterion ("honest observation", "intellectual honesty") instead of the generic "trust gate". **Row independence annotation** — explicit note that a colony can be Proven in Governance while still Seeded in Funding. **Earned Autonomy tagline** — "You graduate by proving you can — you do not graduate by waiting."
- **Agent Mirror: v1.1.1 co-sign annotation.** The Immune System reader description now explicitly mentions co-signing preauthorised security upgrades. The Governance reader description now lists all the agents that read relationship data (Registry, Equilibrium, Lifecycle, Constitutional) instead of only the first two.

### Fixed
- **Evolutionary context: singular/plural consistency.** Unit fields are now "Services", "Microservices", "Agents" (plural) to match the paradigm-level framing. Only "Application" remains singular because monoliths have exactly one per era.

## [1.1.5] — 2026-04-13

### Fixed

- **Agent Mirror diagram: equal-length arrows on both sides.** Previous v1.1.4 had the left arrows at 180px and the right arrows at 40px stubs. Rebuilt with exactly 120px arrows on every side, labels positioned symmetrically around the card midpoint at x=640, `textAlign: right` on left labels and `textAlign: left` on right labels so the text pushes toward the arrow.
- **Equilibrium diagram: centre-line alignment across all columns.** The three columns (Consolidation / Equilibrium / Fragmentation) now have every element — top label, subtitle, main box, super-agent blob, bottom gauge, gauge heading, gauge description — aligned on the same vertical centre lines at x=240/800/1360. Previously the gauge headings drifted (250/700/1310) and subtitle labels drifted by ±20px.
- **Colony Memory Reflection Cycle: rebuilt from scratch with proper circular geometry.** Previous diagram had scattered node positions, inconsistent shape sizes, mismatched colours, floating annotations, and ambiguous arrow direction. Rebuilt with six nodes sitting on a geometric circle (radius 320, centre 640,500) at exact 60° angular spacing. All three memory stores are identical rectangles (240×120), all three transitions are identical ellipses (200×100). Arrows are uniform in stroke width and colour. Memory colours now form a progression (light blue → medium blue → dark blue) showing the distillation from events to lessons to constitutional rules. Annotations moved out of the ring — the centre is now a short "Colony Memory / The reflection cycle" heading, and the summary caption sits below the diagram as a figure caption.

### Changed

- Upstream excalidraw-diagram skill updated with three new rule sections:
  - **Centre-Line Alignment** — elements in a shared column or row must share cx or cy exactly
  - **Cycle Diagrams** — nodes on a cycle must sit on a geometric circle with equal angular spacing, peer nodes share size and shape, arrow styling is uniform
  - **Annotations and Floating Text** — every text element must have a clear anchor; long explanations belong in figure captions below the diagram
- Five new validation table rows catch these defects automatically in future diagrams.

## [1.1.4] — 2026-04-13

### Fixed
- **Agent Mirror diagram: mirror-symmetric layout and perfectly horizontal arrows.** The diagram previously had the "Self" label with two zig-zag arrows reaching across multiple sections, and the right-side arrows were slightly off-horizontal (10px drift). Rebuilt with strict bilateral symmetry: three labels on the left (Registry Agent → Core Identity, Self → Autonomy, Lifecycle Agent → Lifecycle) and three on the right (Other Agents → Capabilities, Immune System → Security, Governance → Relationships). Every arrow is a single horizontal segment with `y_start == y_end` at the target section's y-centre. Every section now has exactly one external reader.
- The underlying excalidraw-diagram skill has been updated with explicit Arrow Straightness and Symmetric Layout rules so future diagrams follow the same discipline by default.

## [1.1.3] — 2026-04-13

### Fixed
- **Arrows in diagrams are now straight.** The SVG exporter was preserving intermediate waypoints from the Excalidraw source, causing some arrows (most visibly the "Self" arrows in the Agent Mirror diagram) to zig-zag. The exporter now draws arrows as direct lines from the first point to the last point, ignoring intermediate waypoints. Lines (non-arrows) keep their polyline shape because they often draw borders or underlines where the shape matters.

## [1.1.2] — 2026-04-13

### Added
- **Scale calibration in `examples/hello-colony/`** — `colony-snapshot.yaml` now declares `scale: 5-agent-team` with an explanatory `scale_notes` block tying the example to the specification's Scales of Application table. README opens with a Scale Calibration section making the same point.
- **Preauthorised security upgrade fields in `registry-agent.v1.1.yaml`** — the security_patch evolution log entry now shows all three v1.1.1 invariants concretely: `preauthorised_action_class: patch_application` (closed enum), `co_signer: sentinel-agent` + `co_sign_verified: true` (Immune System co-sign), `pre_state_hash`, `rollback_window_minutes`, `rollback_deadline`, `append_only_log_id` (append-only audit log). `last_security_upgrade` in the security section is enriched with the same metadata.
- **Hello-colony README section** walking through the preauthorisation fields and showing how the canonical attack (exfiltration-as-security-upgrade) fails at the enum, the co-sign, and the log.

### Changed
- **Trust Ledger row** in the Scales of Application table: 5-agent cell changed from "Informal; spreadsheet or markdown table" to "Human memory plus a retro; the team itself is the ledger" — honest about what the ledger actually is at that scale. Mirrored in thesis.

## [1.1.1] — 2026-04-13

### Added
- **Scales of application** subsection in `specification.md` §1 — explicit table showing how each principle/mechanism adapts at three scales (5-agent team, 50-agent org estate, 5,000-agent ecosystem). Reframes unit-of-analysis "slippage" as scale-adaptive application.
- **Security upgrade preauthorisation** strengthened with three concrete invariants: closed enum of preauthorised action classes, Immune System co-sign requirement, append-only log with bounded rollback. Turns the corollary from acknowledged risk into a mitigation with defence in depth.
- **Preauthorised-security abuse failure mode** in Conformance section (§7.5) now shows six-layer defence (three structural from the new invariants, three behavioural from Sentinel/Patch/Response).

### Changed
- `thesis.md` — mirrors the scale-adaptive table and strengthened preauthorisation treatment (shorter summaries, pointer to specification for full detail).

## [1.1.0] — 2026-04-13

### Added
- Agent Mirror JSON Schema (`schemas/agent-mirror-v0.1.json`)
- Worked example: `examples/hello-colony/` with 5 agent definitions, a pre/post-evolution pair, and a colony snapshot
- Conformance section in `specification.md` with anti-patterns, health signals, and failure modes
- `CONTRIBUTING.md` — contribution guide applying the paper's own epistemic principles
- `CITATION.cff` — Citation File Format metadata
- Issue templates for challenges and refinements
- SVG exports of all 6 diagrams for native GitHub rendering

### Changed
- README now includes a "Scope and audiences" section routing practitioners, researchers, and implementers to the appropriate documents
- Thesis paper diagrams now reference `.svg` files (rendered inline on GitHub) instead of `.excalidraw` source files

### Fixed
- Diagrams now render on GitHub — previously the `.excalidraw` references showed as broken image links
- License contradiction in `specification.md` — removed any ownership statement that conflicted with the repo-level CC BY 4.0 licence

## [1.0.0] — 2026-04-11

### Added
- The Agent Colony Manifesto
- The thesis paper: "The Agent Colony: A Pattern Language for Self-Governing AI Agent Ecosystems"
- v1.0 Specification with four-layer architecture, Agent Mirror schema, colony dynamics, and maturity model
- 6 Excalidraw source diagrams
- CC BY 4.0 licence
