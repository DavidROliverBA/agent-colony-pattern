"""Teaching Colony lifecycle driver — substrate-independent.

Usage::

    python run.py --substrate=claude-code --mock
    python run.py --substrate=managed-agents
    python run.py --substrate=claude-code --reset

The driver runs the 9-step lifecycle:

    1. boot — load Mirrors, verify Registry and Sentinel ready
    2. initial serve — Teacher answers a beekeeping question
    3. learn — Librarian reads the pattern corpus, extracts concepts,
       writes KB entries (repeats for a few cycles)
    4. detect — Equilibrium checks overlap, Librarian computes coverage
    5. classify — Structural Classifier determines the review regime
    6. graduate — graduation checklist generated, Sentinel co-signs
    7. acquire — Teacher's Mirror is updated with the new capability
    8. serve (new capability) — Teacher answers an Agent Colony question
    9. snapshot — write colony-snapshot.yaml summarising final state

The driver calls adapter methods but imports no substrate code directly.
The adapter is injected through ``--substrate``.
"""
from __future__ import annotations

import argparse
import importlib
import os
import shutil
import sys
from datetime import datetime, timezone

# Make sibling modules importable when this script is run directly.
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from contract import Event, SubstrateContract  # noqa: E402
from colony.logic.classifier import classify_action  # noqa: E402
from colony.logic.graduation import generate_checklist, write_checklist  # noqa: E402


SUBSTRATE_MODULES = {
    "claude-code": "substrates.claude_code.adapter",
    "managed-agents": "substrates.managed_agents.adapter",
}


def load_adapter(substrate: str, mock: bool) -> SubstrateContract:
    module_path = SUBSTRATE_MODULES[substrate]
    module = importlib.import_module(module_path)
    # Try in order: generic Adapter, generic SubstrateAdapter, any class whose
    # name ends in "Adapter" (ClaudeCodeAdapter, ManagedAgentsAdapter, ...).
    adapter_cls = getattr(module, "Adapter", None) or getattr(module, "SubstrateAdapter", None)
    if adapter_cls is None:
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and name.endswith("Adapter") and name != "SubstrateContract":
                adapter_cls = obj
                break
    if adapter_cls is None:
        raise RuntimeError(f"No Adapter class found in {module_path}")
    # Adapters use repo_root=; keep colony_root= as a backwards-compat alias
    # so that older callers that passed colony_root still work.
    try:
        return adapter_cls(repo_root=HERE, mock=mock)
    except TypeError:
        return adapter_cls(colony_root=HERE, mock=mock)


def reset_state(state_dir: str) -> None:
    """Wipe runtime state but keep seeded files (managed by .gitignore)."""
    for name in ("events.jsonl", "colony-snapshot.yaml"):
        p = os.path.join(state_dir, name)
        if os.path.exists(p):
            os.remove(p)
    grad = os.path.join(state_dir, "graduation-checklists")
    if os.path.isdir(grad):
        shutil.rmtree(grad)


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_lifecycle(adapter: SubstrateContract) -> dict:
    """Execute the 9-step lifecycle against the injected adapter.

    Returns a dict summary used by the CLI to print a final table.
    """
    summary = {
        "agents": [],
        "capability_changes": [],
        "events_emitted": 0,
        "substrate": type(adapter).__module__,
    }

    def emit(event_type: str, actor: str, payload: dict) -> None:
        adapter.record_event(
            Event(
                type=event_type,
                actor=actor,
                payload=payload,
                timestamp=now(),
                substrate=type(adapter).__module__,
            )
        )
        summary["events_emitted"] += 1

    # 1. Boot
    for agent_id in (
        "registry-agent",
        "chronicler-agent",
        "equilibrium-agent",
        "sentinel-agent",
        "librarian-agent",
        "teacher-agent",
    ):
        mirror = adapter.read_mirror(agent_id)
        summary["agents"].append(
            {
                "id": agent_id,
                "version": mirror.data.get("identity", {}).get("version"),
                "capabilities": [
                    c["name"]
                    for c in mirror.data.get("capabilities", {}).get("capabilities", [])
                ],
            }
        )
        emit("agent_boot", agent_id, {"phase": "boot"})

    # 2. Initial serve — Teacher answers a beekeeping question
    answer = adapter.dispatch_agent(
        "teacher-agent",
        {"topic": "beekeeping", "question": "What are the three types of bee?"},
    )
    emit("agent_serve", "teacher-agent", {"topic": "beekeeping", "answer": answer})

    # 3. Learn — Librarian reads the pattern corpus and writes KB entries
    corpus_files = [
        "manifesto.md",
        "thesis.md",
        "specification.md",
        "it-takes-a-village.md",
        "dark-code.md",
        "prior-art.md",
        "indy-dev-dan-six-ideas.md",
    ]
    concepts_extracted: list[str] = []
    for cycle, corpus_file in enumerate(corpus_files, start=1):
        learn_input = {"corpus_file": f"colony/corpus/pattern/{corpus_file}"}
        learning = adapter.dispatch_agent("librarian-agent", learn_input)
        concepts_extracted.extend(learning.get("concepts", []) or [])
        adapter.write_kb(
            topic="agent-colony-pattern",
            content=learning.get("kb_content", f"[seed for cycle {cycle}]"),
            provenance=f"corpus/pattern/{corpus_file}",
        )
        emit(
            "kb_write",
            "librarian-agent",
            {"topic": "agent-colony-pattern", "provenance": corpus_file},
        )

    # 4. Detect — Equilibrium checks overlap, Librarian computes coverage
    equilibrium_result = adapter.dispatch_agent("equilibrium-agent", {"action": "scan"})
    emit("overlap_scan", "equilibrium-agent", equilibrium_result)
    coverage_result = adapter.dispatch_agent(
        "librarian-agent", {"action": "compute_coverage", "topic": "agent-colony-pattern"}
    )
    coverage_score = coverage_result.get("coverage_score", 0.85)
    emit("coverage_report", "librarian-agent", coverage_result)

    # 5. Classify — structural classifier decides review regime
    teacher_mirror = adapter.read_mirror("teacher-agent")
    actor_trust_tier = (
        teacher_mirror.data.get("comprehension_contract", {}).get("trust_tier")
        or "Observing"
    )
    classification = classify_action(
        action={"class": "mirror_capability_add"},
        context={"actor_trust_tier": actor_trust_tier},
    )
    emit(
        "classification",
        "substrate",
        {
            "action_class": classification.action_class,
            "blast_radius": classification.blast_radius,
            "review_regime": classification.review_regime,
            "actor_trust_tier": classification.actor_trust_tier,
        },
    )

    # 6. Graduate — generate checklist, Sentinel co-signs
    checklist = generate_checklist(
        agent_id="teacher-agent",
        capability="teach_agent_colony_pattern",
        coverage_evidence={
            "coverage_score": coverage_score,
            "corpus_files": corpus_files,
            "concepts_extracted": concepts_extracted,
        },
        classification=classification,
    )
    checklist_path = write_checklist(checklist, os.path.join(HERE, "state"))
    emit(
        "graduation_checklist",
        "registry-agent",
        {"path": os.path.relpath(checklist_path, HERE)},
    )

    signature = adapter.co_sign(
        action_class="graduation_cosign",
        actor="librarian-agent",
        co_signer="sentinel-agent",
    )
    emit(
        "cosign",
        "sentinel-agent",
        {
            "action_class": signature.action_class,
            "granted": signature.granted,
            "reason": signature.reason,
        },
    )

    # 7. Acquire — Teacher's Mirror is updated with the new capability
    if signature.granted:
        audit = adapter.update_mirror(
            agent_id="teacher-agent",
            changes={
                "capability_add": {
                    "name": "teach_agent_colony_pattern",
                    "description": "Teach the Agent Colony pattern using beekeeping as a metaphor.",
                    "maturity": "experimental",
                }
            },
            co_signer="sentinel-agent",
        )
        emit(
            "mirror_update",
            "teacher-agent",
            {
                "action": audit.action,
                "pre": audit.pre_state_hash,
                "post": audit.post_state_hash,
            },
        )
        summary["capability_changes"].append(
            {
                "agent": "teacher-agent",
                "added": "teach_agent_colony_pattern",
                "cosigned_by": "sentinel-agent",
            }
        )

    # 8. Serve with the new capability
    answer2 = adapter.dispatch_agent(
        "teacher-agent",
        {
            "topic": "agent-colony-pattern",
            "question": "Why is the colony structured like a beehive?",
        },
    )
    emit(
        "agent_serve",
        "teacher-agent",
        {"topic": "agent-colony-pattern", "answer": answer2},
    )

    # 9. Snapshot
    snapshot_path = os.path.join(HERE, "state", "colony-snapshot.yaml")
    try:
        import yaml

        with open(snapshot_path, "w") as f:
            yaml.safe_dump(
                {"generated": now(), "summary": summary},
                f,
                sort_keys=False,
            )
        emit("snapshot", "substrate", {"path": os.path.relpath(snapshot_path, HERE)})
    except Exception as e:  # pragma: no cover
        emit("snapshot_failed", "substrate", {"error": str(e)})

    return summary


def print_summary(summary: dict) -> None:
    print()
    print("=" * 60)
    print("Teaching Colony — run summary")
    print("=" * 60)
    print(f"Substrate:        {summary['substrate']}")
    print(f"Events emitted:   {summary['events_emitted']}")
    print()
    print("Agents:")
    for agent in summary["agents"]:
        caps = ", ".join(agent["capabilities"]) or "(none)"
        print(f"  - {agent['id']} v{agent['version']}: {caps}")
    print()
    if summary["capability_changes"]:
        print("Capability changes:")
        for change in summary["capability_changes"]:
            print(
                f"  - {change['agent']} acquired '{change['added']}' "
                f"(co-signed by {change['cosigned_by']})"
            )
    else:
        print("Capability changes: none")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Teaching Colony lifecycle.")
    parser.add_argument(
        "--substrate",
        choices=sorted(SUBSTRATE_MODULES.keys()),
        required=True,
        help="Which substrate adapter to use.",
    )
    parser.add_argument("--reset", action="store_true", help="Wipe runtime state first.")
    parser.add_argument("--mock", action="store_true", help="Run adapter in offline mock mode.")
    args = parser.parse_args(argv)

    state_dir = os.path.join(HERE, "state")
    if args.reset:
        reset_state(state_dir)

    try:
        adapter = load_adapter(args.substrate, mock=args.mock)
    except ModuleNotFoundError as e:
        print(f"error: could not load substrate '{args.substrate}': {e}", file=sys.stderr)
        return 2

    summary = run_lifecycle(adapter)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
