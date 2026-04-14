# The Substrate Contract

> **Audience lens:** Architect. This document is the load-bearing artefact for
> anyone evaluating whether the Agent Colony pattern is substrate-portable or
> whether its guarantees quietly depend on a particular runtime.

The Agent Colony pattern defines four layers:

| Layer | Owns |
|-------|------|
| L1 Agent | A single narrow capability, declared in its Agent Mirror |
| L2 Colony | Registry, Chronicler, Equilibrium, Sentinel — structural agents |
| L3 Domain | Agents that deliver user value (here: Librarian, Teacher) |
| L4 Substrate | Execution environment, memory, and governance primitives |

The Substrate Contract is the interface L4 must expose upwards. Everything
L1–L3 does is expressed in terms of the eight operations below, and nothing
more. Any execution environment that implements these operations honestly
can host the colony.

## The eight operations

| Operation | Returns | Purpose |
|-----------|---------|---------|
| `dispatch_agent(agent_id, input)` | `dict` | Execute an agent by id. |
| `read_mirror(agent_id)` | `Mirror` | Load an agent's Mirror YAML. |
| `update_mirror(agent_id, changes, co_signer)` | `AuditEntry` | Apply a change to a Mirror, under co-signature. |
| `record_event(event)` | `None` | Append to Event Memory. |
| `read_kb(query)` | `list[Document]` | Query the colony knowledge base. |
| `write_kb(topic, content, provenance)` | `None` | Write a topic entry to the KB. |
| `co_sign(action_class, actor, co_signer)` | `Signature` | Obtain a co-signature for an action class. |
| `classify_action(action, context)` | `Classification` | Classify blast radius + review regime. |

## Why exactly eight

Fewer than eight and the contract leaks concerns into the caller. If we
dropped `classify_action`, every caller would have to classify its own
actions, which means every caller would have to be audited for honest
classification — the contract would stop being enforceable.

More than eight and the contract starts duplicating itself. Earlier drafts
included a separate `read_event` operation alongside `record_event`; we
removed it because Event Memory queries are a specialised form of
`read_kb` in every substrate we tried. We resisted splitting `update_mirror`
into `propose_mirror_change` and `commit_mirror_change` for the same
reason: the co-signer argument is what makes an update legitimate, and
splitting the operation lets callers forget to co-sign.

Eight is the smallest set that lets an Agent Colony run end-to-end —
dispatch work, remember what happened, read and write its knowledge, change
itself under governance, and enforce review regimes — without any
additional hidden primitives.

## Why classification lives inside the substrate

The Comprehension Contract (specification §7) requires that every action
above the Local blast radius pass through a review regime appropriate to
the actor's trust tier. If the caller classified its own actions, a
malicious or confused agent could simply declare all its actions "Local".
The Structural Classifier therefore belongs to L4. Callers hand the
substrate an action and a context; the substrate decides what review is
required. The `classifier_version` field on every Mirror records which
classifier version its trust tier assumes, so a classifier change is
itself a Colony-wide event requiring governance review.

## How `update_mirror` enforces the Comprehension Contract

`update_mirror` takes a `co_signer` argument. The adapter must:

1. Call `classify_action({'class': 'mirror_capability_add', ...}, context)`
   to determine the review regime.
2. Reject the call if the change violates the agent's `blast_radius_ceiling`
   or its `self_evolution_scope.forbidden` list.
3. Verify the co-signer's Mirror has a fresh pre-registered policy for
   the action class, or escalate to the required review regime.
4. Compute `pre_state_hash` (e.g. sha256 of the YAML file).
5. Apply the change and compute `post_state_hash`.
6. Emit an `AuditEntry` and also record an event via `record_event`.

The caller never bypasses this sequence because it cannot write to the
Mirror directly — the substrate owns Mirror storage.

## Two substrates, two implementations

The same colony runs on two substrates in this example:

- **Claude Code** — a local-file substrate. Agents are subprocess calls
  with prompt files; events are JSONL lines; the KB is a directory of
  markdown files; co-signing is enforced by the adapter running a second
  subprocess against the co-signer's Mirror.
- **Managed Agents API** — a remote substrate. Agents are Anthropic
  Managed Agents; events are messages appended to a shared thread;
  the KB is a set of uploaded files; co-signing is enforced by a separate
  API call to the co-signer's agent.

Both adapters satisfy the same eight operations. Neither one leaks into
the colony definition — `colony/`, `contract.py`, and `run.py` have no
substrate-specific imports. A third substrate (say, a cloud function
runtime) would need only its own adapter; everything above L4 would run
unchanged.

That is the portability claim, and the Substrate Contract is where that
claim is either honoured or quietly broken.
