# Hello Colony — A Worked Example

This directory contains a minimal worked example of the Agent Colony pattern. It demonstrates how five agents work together as a coherent colony, each described by a filled Agent Mirror YAML file.

This is a fictional example, not a running system. It exists to make the abstract specification concrete — to show what the pattern looks like in practice, what internally consistent cross-references between agents look like, and how self-evolution is recorded.

---

## The Five Agents

### Registry Agent (`agents/registry-agent.yaml`)

The colony's catalogue. Every agent registers here on first deployment. The Registry Agent provides three core services: discovery (find agents by capability), dependency graphing (what breaks if this agent goes away), and health summary (colony-wide agent status). It is a dependency of almost every other agent in the colony — the first agent to deploy and the last to retire.

### Equilibrium Agent (`agents/equilibrium-agent.yaml`)

The colony's self-regulator. The Equilibrium Agent continuously computes three indices: the Overlap Index (are two agents doing the same thing?), the Concentration Index (is one agent doing too much?), and the Vitality Index (is the colony growing, retiring, and evolving at a healthy rate?). When the Overlap Index breaches the watch threshold (15-40%), it flags for review. Above 40%, it proposes a merger. It proposes — it never decides. Decisions belong to humans at this colony's current trust stage.

### Sentinel Agent (`agents/sentinel-agent.yaml`)

The colony's immune system. The Sentinel Agent runs continuous threat detection, anomaly monitoring, and vulnerability scanning across all registered agents. Critically, it watches for drift between what an Agent Mirror declares and what an agent actually does — a compromised agent's Mirror will lie, but its behaviour patterns may not. The Sentinel has the highest availability SLA in the colony (99.99%) and depends on no other agent for its security posture. If it goes silent, the silence is itself a signal.

### Chronicler Agent (`agents/chronicler-agent.yaml`)

The colony's memory. The Chronicler Agent records all significant colony events into Event Memory. It is intentionally a terminal dependency — it depends on nothing else in the colony to avoid circular recording chains. Everything else depends on it. The Chronicler is what allows future agents to learn from past decisions, prevents the same mistakes from being repeated, and provides the audit trail that makes the colony's autonomy accountable. Its Event Memory is append-only; past events cannot be modified.

### Domain Agent — Finance (`agents/domain-agent-finance.yaml`)

The only L3 agent in this example, representative of the agent mesh where the actual work happens. The Finance domain agent handles invoice processing, payment validation, budget tracking, and financial reporting. It owns the finance capability surface and will delegate to specialist agents (invoice-agent, payment-agent) as the mesh grows. Note the `watch`-zone overlap with the Equilibrium Agent in its overlap_map — the Finance agent has accreted some self-monitoring capabilities that brush against Equilibrium's territory. This is intentional: it demonstrates how the pattern surfaces real governance signals.

---

## How to Read This Example

**Start with `colony-snapshot.yaml`.** It gives you the colony-wide view: all five agents, the full overlap matrix, vitality metrics, and the dependency graph summary. The `watch`-zone overlap between `equilibrium-agent` and `domain-agent-finance` (score: 0.24) is the most interesting governance signal in the snapshot.

**Then read individual agent files.** Each agent's Mirror is self-contained — you can read any one of them and understand that agent's identity, what it does, what it depends on, and how it defends itself. The cross-references in `relationships` will point you to related agents.

**Pay attention to `security`.** Every agent has a threat model, detection capabilities, and an escalation process. The Sentinel Agent's threat model is the most interesting — it models its own compromise as the highest-priority scenario.

**Compare `registry-agent.yaml` with `registry-agent.v1.1.yaml`** to see self-evolution in practice (described below).

---

## Self-Evolution in Practice: `registry-agent.v1.1.yaml`

The pair of Registry Agent files demonstrates what a self-evolution step looks like in the Agent Mirror record.

Between v1.0.0 and v1.1.0, two things happened:

1. **A capability addition (triggered by self):** The Equilibrium Agent observed that registering domain agents during colony bootstrap required four sequential round-trips. The Registry Agent identified the missing `bulk_register` capability and added it. This is a non-breaking addition — a new endpoint, no changes to existing contracts. It consumed one slot from the `evolution_budget` (5 remaining → 4 remaining).

2. **A security patch (triggered by Sentinel Agent):** The Sentinel Agent's anomaly scan of submission logs discovered CVE-2026-0441 — a timing-window bypass in the signature verification logic. The Registry Agent applied the patch immediately under preauthorised security upgrade authority. Security patches do not consume the evolution budget.

Both events are recorded in full in:
- `lineage` — the human-readable version history entry
- `evolution_log` — the machine-readable record of every self-modification

Notice that `human_approved: false` appears on both evolution log entries. The capability addition was within the declared `self_evolution_scope.allowed` list (non-breaking capability addition). The security patch was preauthorised by the colony's mutual defence principle. Neither required a governance checkpoint — but both are permanently on record.

---

## Validating Against the Schema

Once the Agent Mirror schema is available at `schemas/agent-mirror-v0.1.json`, you can validate all agent files against it using `ajv-cli` with YAML support:

```bash
# Install ajv-cli with YAML support if needed
npm install -g ajv-cli ajv-formats

# Validate all agent files
for f in agents/*.yaml; do
  echo "Validating $f..."
  ajv validate -s ../../schemas/agent-mirror-v0.1.json -d "$f"
done
```

---

## Known Limitations

- **This is a fictional colony.** No agents are running. The Mirrors describe what a real colony of this shape would look like, but there is no infrastructure, no runtime, and no actual event log.

- **Schemas are placeholders.** The `input_schema` and `output_schema` URLs in each agent's contracts point to `https://example.com/schemas/...`. These do not exist. In a real colony, these would be hosted schema URLs.

- **The Agent Mirror schema may evolve.** The specification is at v1.0 and the schema at v0.1. As the standard matures, some field names and structures in these example files may need updating.

- **Lifecycle Agent is not included.** The specification describes a Lifecycle Agent as part of L1 governance. It is intentionally absent here to keep the example minimal. The `colony-snapshot.yaml` overlap matrix includes one cross-reference to a `lifecycle-agent` to demonstrate how cross-colony references work in a real deployment.

- **The overlap score between `equilibrium-agent` and `domain-agent-finance` (0.24, watch zone) is real, not a mistake.** It reflects a genuine pattern: domain agents that self-monitor tend to accrete equilibrium-adjacent capabilities. The example preserves this signal rather than smoothing it away.
