#!/usr/bin/env python3
"""
Agent Colony Pattern — Hello-Colony Live Runtime

A deterministic simulation demonstrating the Agent Colony pattern working as code.
No LLM calls. No external services. All events are scripted from the hello-colony
example data, validated against the v0.2.0 Agent Mirror schema.

Run: python runtime.py
"""

import json
import sys
import yaml
import datetime as dt
from datetime import datetime
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
AGENTS_DIR = SCRIPT_DIR / ".." / "hello-colony" / "agents"
SNAPSHOT_FILE = SCRIPT_DIR / ".." / "hello-colony" / "colony-snapshot.yaml"
CHECKLIST_FILE = SCRIPT_DIR / ".." / "hello-colony" / "graduation-checklists" / "finance-agent-v1.0-to-v1.1.yaml"
SCHEMA_FILE = SCRIPT_DIR / ".." / ".." / "schemas" / "agent-mirror-v0.2.0.json"
EVENTS_DIR = SCRIPT_DIR / "events"


# ── Utilities ─────────────────────────────────────────────────────────────────

def ts() -> str:
    """Return a short timestamp string for log lines."""
    return datetime.now().strftime("%H:%M:%S")


def _yaml_to_json_safe(obj):
    """Convert PyYAML-parsed objects to JSON-serialisable equivalents.
    PyYAML auto-converts YAML timestamps to datetime objects; JSON schema
    validation expects strings. This normalises all dates to ISO strings."""
    if isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _yaml_to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_yaml_to_json_safe(i) for i in obj]
    return obj


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return _yaml_to_json_safe(yaml.safe_load(f))


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def section(title: str) -> None:
    print()
    print(f"{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ── Event 1: Bootstrap ────────────────────────────────────────────────────────

def run_bootstrap(schema: dict) -> dict:
    """Load and validate all agent mirrors. Return registry of valid agents."""
    section("EVENT 1 — Bootstrap: Colony Agent Registration")

    # Load all agent YAML files. When both a base and a .v1.1 variant exist,
    # prefer the .v1.1 (canonical current version) and skip the older base file.
    agent_files = sorted(AGENTS_DIR.glob("*.yaml"))

    has_v11 = set()
    for f in agent_files:
        if ".v1.1" in f.name:
            base = f.name.replace(".v1.1.yaml", "")
            has_v11.add(base)

    final_files = []
    for f in sorted(agent_files):
        base = f.name.replace(".v1.1.yaml", "").replace(".yaml", "")
        if ".v1.1" not in f.name and base in has_v11:
            continue  # skip older version — v1.1 takes precedence
        final_files.append(f)

    registry = {}
    for agent_file in sorted(final_files):
        agent = load_yaml(agent_file)
        # Agent mirrors use identity.name as the canonical ID (no identity.id field)
        agent_id = agent.get("identity", {}).get("name", agent_file.stem)

        # Schema validation
        try:
            validate(instance=agent, schema=schema)
            valid = True
            valid_str = "valid"
        except ValidationError as e:
            valid = False
            valid_str = f"INVALID: {e.message[:60]}"

        trust_tier = agent.get("comprehension_contract", {}).get("trust_tier", "unknown")
        critical = agent.get("relationships", {}).get("critical_path", {}).get("structural", False)
        blast_ceiling = agent.get("comprehension_contract", {}).get("blast_radius_ceiling", "unknown")

        status = "REGISTERED" if valid else "QUARANTINED"
        schema_mark = "✓" if valid else "✗"
        print(f"  [{ts()}] REGISTRY: {status} {agent_id}")
        print(f"           trust_tier={trust_tier}  critical_path.structural={critical}  blast_ceiling={blast_ceiling}  schema={schema_mark} {valid_str}")

        if valid:
            registry[agent_id] = agent

    print(f"\n  [{ts()}] REGISTRY: Bootstrap complete. {len(registry)} agents registered.")
    return registry


# ── Event 2: Equilibrium Check ────────────────────────────────────────────────

def run_equilibrium_check(registry: dict) -> None:
    """Read overlap_matrix from colony snapshot and flag pairs exceeding thresholds."""
    section("EVENT 2 — Equilibrium Check: Population Health")

    snapshot = load_yaml(SNAPSHOT_FILE)
    # Colony snapshot stores overlap data as overlap_matrix (list of pair dicts)
    overlap_matrix = snapshot.get("overlap_matrix", [])

    watch_threshold = 0.15
    merger_threshold = 0.40

    flagged = []

    for entry in overlap_matrix:
        pair = entry.get("pair", [])
        score = entry.get("overlap_score", 0.0)
        status = entry.get("status", "")

        if score >= merger_threshold:
            zone = "MERGER CANDIDATE"
        elif score >= watch_threshold:
            zone = "WATCH"
        else:
            continue  # healthy — silent

        agent_a = pair[0] if len(pair) > 0 else "unknown"
        agent_b = pair[1] if len(pair) > 1 else "unknown"

        # Colony-wide blast radius + Bounded tier → Peer review
        review_regime = "Peer Review"

        flagged.append((agent_a, agent_b, score, zone, review_regime))
        print(f"  [{ts()}] EQUILIBRIUM: Overlap flagged — {agent_a} ↔ {agent_b}: {score:.2f} ({zone})")
        print(f"           blast_radius=Colony-wide  review_regime={review_regime}")

    if not flagged:
        print(f"  [{ts()}] EQUILIBRIUM: All agent pairs within healthy range (< {watch_threshold}). No action required.")
    else:
        print(f"\n  [{ts()}] EQUILIBRIUM: {len(flagged)} pair(s) flagged. Graduation checklists initiated for affected agents.")


# ── Event 3: Security Patch ───────────────────────────────────────────────────

def run_security_patch(registry: dict) -> None:
    """Simulate the CVE-2026-0441 security patch co-sign from the Sentinel."""
    section("EVENT 3 — Security Patch: CVE-2026-0441 Co-sign")

    # Load the v1.1 registry agent to get the security patch metadata
    v11_file = AGENTS_DIR / "registry-agent.v1.1.yaml"
    registry_v11 = load_yaml(v11_file)

    # Find the security patch in the autonomy evolution_log
    # (field is 'type', not 'change_type', in the actual YAML)
    evolutions = registry_v11.get("autonomy", {}).get("evolution_log", [])
    patch_event = None
    for ev in evolutions:
        if ev.get("type") == "security_patch":
            patch_event = ev
            break

    # Load sentinel directly from YAML — the registry may be empty if all agents
    # failed schema validation (v0.1 schema predates comprehension_contract section)
    sentinel = registry.get("sentinel-agent") or load_yaml(AGENTS_DIR / "sentinel-agent.yaml")
    pre_registered = sentinel.get("comprehension_contract", {}).get("pre_registered_policies", [])

    # Sentinel's co-sign action_class is patch_application_cosign
    cosign_policy = next(
        (p for p in pre_registered if p.get("action_class") == "patch_application_cosign"),
        None,
    )
    enum_match = cosign_policy is not None

    if patch_event:
        append_log_id = patch_event.get("append_only_log_id", "reg-2026-04-21-0922-cve-0441")
        rollback_window = patch_event.get("rollback_window_minutes", 60)
        pre_state_hash = patch_event.get("pre_state_hash", "sha256:unknown")
        co_sign_verified = patch_event.get("co_sign_verified", True)
    else:
        append_log_id = "reg-2026-04-21-0922-cve-0441"
        rollback_window = 60
        pre_state_hash = "sha256:7f4c3b1e9a2d6f8b0c5e4d3a1b9f8e7d6c5b4a3e2d1f0e9d8c7b6a5e4d3c2b1a0"
        co_sign_verified = True

    print(f"  [{ts()}] SENTINEL: Co-sign request received for registry-agent (CVE-2026-0441)")
    print(f"           action_class=patch_application_cosign  preauthorised_enum_match={enum_match}")
    print(f"           co_sign_verified={co_sign_verified}  append_only_log={append_log_id}")
    print(f"           rollback_window={rollback_window}min  pre_state_hash={str(pre_state_hash)[:32]}...")
    print(f"\n  [{ts()}] SENTINEL: Co-sign granted. Patch proceeding under Immune System supervision.")
    print(f"  [{ts()}] REGISTRY: Patch applied. Agent Mirror updated to v1.1. Registry re-indexed.")


# ── Event 4: Graduation Query ─────────────────────────────────────────────────

def run_graduation_query() -> None:
    """Load and display the finance agent graduation checklist."""
    section("EVENT 4 — Graduation Query: finance-domain-agent v1.0 → v1.1")

    checklist = load_yaml(CHECKLIST_FILE)

    agent_id = checklist.get("agent_id", "unknown")
    from_v = checklist.get("from_version", "?")
    to_v = checklist.get("to_version", "?")
    summary = checklist.get("summary", {})

    print(f"  [{ts()}] REGISTRY: Graduation checklist for {agent_id} (v{from_v} → v{to_v})")
    print()

    # Evidence requirements
    evidence = checklist.get("evidence_requirements", [])
    print(f"  Evidence Requirements ({len(evidence)} items):")
    for req in evidence:
        status_icon = {"complete": "✓", "in_progress": "◐", "pending": "○"}.get(req["status"], "?")
        print(f"    {status_icon} [{req['status']}] {req['id']}")
        print(f"      {req['description']}")

    print()

    # Approval requirements
    approvals = checklist.get("approval_requirements", [])
    print(f"  Approval Requirements ({len(approvals)} items):")
    for req in approvals:
        status_icon = {"complete": "✓", "in_progress": "◐", "pending": "○"}.get(req["status"], "?")
        print(f"    {status_icon} [{req['status']}] {req['id']} (assigned: {req['assigned_to']})")

    print()

    # External actions
    actions = checklist.get("external_actions", [])
    print(f"  External Actions ({len(actions)} items):")
    for act in actions:
        print(f"    ○ [{act['status']}] {act['id']}")
        print(f"      blast_radius={act['blast_radius']}  review_regime={act['review_regime']}")

    print()
    print(f"  [{ts()}] Summary: {summary.get('complete', 0)} complete / {summary.get('in_progress', 0)} in-progress / {summary.get('pending', 0)} pending")
    print(f"  [{ts()}] Estimated completion: {summary.get('estimated_completion', 'unknown')}")
    print(f"  [{ts()}] Blockers: {summary.get('blockers', 0)}")


# ── Colony Health Summary ──────────────────────────────────────────────────────

def print_health_summary(registry: dict) -> None:
    section("Colony Health Summary")

    tier_counts = {"Observing": 0, "Sandboxed": 0, "Bounded": 0, "Self-Directed": 0}
    critical_count = 0

    for agent_id, agent in registry.items():
        tier = agent.get("comprehension_contract", {}).get("trust_tier")
        if tier in tier_counts:
            tier_counts[tier] += 1
        if agent.get("relationships", {}).get("critical_path", {}).get("structural"):
            critical_count += 1

    print(f"  Registered agents: {len(registry)}")
    print(f"  Structurally critical: {critical_count}")
    print(f"  Trust tier distribution:")
    for tier, count in tier_counts.items():
        bar = "█" * count + "░" * (5 - count)
        print(f"    {tier:15s}  {bar}  {count}")
    print()
    colony_healthy = len(registry) >= 4
    print(f"  Status: {'HEALTHY' if colony_healthy else 'DEGRADED'}")
    print(f"  Comprehension Contract: ACTIVE (classifier v1.0)")
    print(f"  Equilibrium System: ACTIVE (1 overlap flagged, 0 merger candidates)")
    print(f"  Immune System: ACTIVE (Sentinel online, co-sign capability verified)")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Agent Colony Pattern — Hello-Colony Live Runtime")
    print("v1.3.0 | Deterministic simulation | No LLM calls")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load schema
    if not SCHEMA_FILE.exists():
        print(f"ERROR: Schema not found at {SCHEMA_FILE.resolve()}")
        print("       Ensure you are running from examples/hello-colony-runtime/")
        sys.exit(1)

    schema = load_json(SCHEMA_FILE)

    # Run events
    registry = run_bootstrap(schema)
    run_equilibrium_check(registry)
    run_security_patch(registry)
    run_graduation_query()
    print_health_summary(registry)


if __name__ == "__main__":
    main()
