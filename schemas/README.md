# Agent Colony Schemas

## What Is the Agent Mirror?

The **Agent Mirror** is the proposed standard for complete, self-describing agent identity within an Agent Colony. An agent looks at its Mirror and knows what it is, what it can do, how it has changed, and what it is responsible for.

The Mirror is *descriptive*, not *prescriptive* — it reflects what the agent is, not what it should be. When the Mirror and an agent's actual behaviour diverge, that divergence is a signal: potential drift, compromise, or an outdated record.

The Mirror covers six sections: **identity** (who the agent is and its version history), **capabilities** (what it does and what consumers can rely on), **autonomy** (what it can decide for itself), **security** (what it defends against and how it escalates), **lifecycle** (its current stage and health), and **relationships** (its declared overlap with other agents and who depends on it).

For the full conceptual treatment — the gap it fills, how it fits into the four-layer colony architecture, and its role in the equilibrium system — read the main [specification.md](../specification.md), specifically Section 2.

## Why v0.1?

This is the earliest stable revision of the schema. The version carries an intentional signal:

- **v0.x** indicates the schema is not yet frozen. Breaking changes (field renames, type changes, required field additions) may occur between v0.x releases as the community tests it against real implementations.
- **v1.0** will be declared only after the first production reference implementation has been built against the schema, and after at least one round of community review has resolved the open design questions.

If you adopt v0.1 in an experiment or prototype, expect to migrate when v0.2 is released.

## Validating an Agent Mirror

The schema is a standard [JSON Schema draft 2020-12](https://json-schema.org/specification) document, compatible with any compliant validator. Agent Mirror files may be written in JSON or YAML.

```bash
# Install ajv-cli with format support
npm install -g ajv-cli ajv-formats

# Validate a JSON Agent Mirror
ajv validate -s schemas/agent-mirror-v0.1.json -d my-agent.json

# Validate a YAML Agent Mirror (ajv-cli supports YAML natively)
ajv validate -s schemas/agent-mirror-v0.1.json -d my-agent.yaml
```

A valid Agent Mirror will produce no output and exit 0. Validation errors are reported with the failing JSON path and a description of the constraint violated.

## Worked Examples

The `examples/hello-colony/` directory contains a complete set of worked Agent Mirror files for a minimal colony — Registry Agent, Equilibrium Agent, and a simple domain agent — showing how the sections relate to each other in practice (cross-referenced dependency and consumer lists, overlap declarations that mirror each other, evolution budgets in context).

The `examples` property in `agent-mirror-v0.1.json` itself also contains a single complete example for a Registry Agent, giving validators and tooling a concrete instance to test against.

## Relationship to Existing Standards

The Agent Mirror is a proposed extension to fill gaps that existing standards do not address:

| Standard | What it contributes | Gap the Mirror fills |
|----------|--------------------|--------------------|
| **A2A Agent Cards** | Capabilities and endpoints for discovery | Lifecycle, autonomy level, evolution history, security posture |
| **AGNTCY / OASF** | Agent identity, capabilities, I/O | Evolution history, lifecycle stage, self-migration properties |
| **MCP** | Tool interfaces | Agent identity, governance, autonomy |
| **OpenAPI** | HTTP API contracts | Purpose, lifecycle, autonomy, relationships |

The Mirror is not a replacement for any of these — an active agent will typically have an A2A Agent Card *and* an MCP tool definition *and* an Agent Mirror. The Mirror is the identity layer that the others lack.

See [Section 7 of the specification](../specification.md) for the full gap analysis.

## Proposing Changes

The schema is versioned and community input is welcome. To propose a change:

1. Open an issue at [github.com/DavidROliverBA/agent-colony-pattern/issues](https://github.com/DavidROliverBA/agent-colony-pattern/issues) describing the field, the use case it addresses, and any schema you have drafted.
2. Breaking changes (removing required fields, changing types) require a version increment and a documented migration path.
3. Additive changes (new optional fields) can be proposed as minor version increments.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contribution process.
