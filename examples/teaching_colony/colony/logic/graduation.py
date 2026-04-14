"""Graduation checklist generator.

When Librarian proposes that Teacher should acquire a new capability
(``teach_agent_colony_pattern``), the colony cannot just hand it over.
The Comprehension Contract requires a graduation checklist — evidence
of coverage, approvals from structural agents, and a recorded event.

The function below generates the checklist as a dict matching the
hello-colony graduation-checklist YAML structure.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import yaml

try:
    from examples.teaching_colony.contract import Classification
except ImportError:  # fallback when run from inside examples/teaching_colony/
    from contract import Classification  # type: ignore


def generate_checklist(
    agent_id: str,
    capability: str,
    coverage_evidence: dict,
    classification: Classification,
) -> dict:
    """Generate a graduation checklist dict for a capability proposal.

    Parameters
    ----------
    agent_id : str
        The agent acquiring the new capability (e.g. ``teacher-agent``).
    capability : str
        The capability being added (e.g. ``teach_agent_colony_pattern``).
    coverage_evidence : dict
        Librarian-supplied evidence. Expected keys:
        ``coverage_score`` (float 0..1), ``corpus_files`` (list[str]),
        ``concepts_extracted`` (list[str]).
    classification : Classification
        The structural classifier's verdict on this capability add.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    coverage_score = coverage_evidence.get('coverage_score', 0.0)
    corpus_files = coverage_evidence.get('corpus_files', [])
    concepts = coverage_evidence.get('concepts_extracted', [])

    evidence_requirements = [
        {
            'id': 'corpus_coverage',
            'description': 'Corpus coverage score >= 0.80 across required pattern documents',
            'status': 'complete' if coverage_score >= 0.80 else 'in_progress',
            'evidence': (
                f"Coverage score {coverage_score:.2f} across "
                f"{len(corpus_files)} corpus files: {', '.join(corpus_files) or 'none'}"
            ),
            'estimated_completion': now if coverage_score >= 0.80 else None,
        },
        {
            'id': 'concept_extraction',
            'description': 'Librarian has extracted named concepts from the corpus',
            'status': 'complete' if concepts else 'pending',
            'evidence': (
                f"{len(concepts)} concepts extracted: "
                f"{', '.join(concepts[:5])}{'...' if len(concepts) > 5 else ''}"
            ),
            'estimated_completion': now if concepts else None,
        },
        {
            'id': 'structural_classification',
            'description': 'Structural Classifier has determined review regime for this capability add',
            'status': 'complete',
            'evidence': (
                f"Classified as {classification.action_class} — blast radius "
                f"{classification.blast_radius}, review regime "
                f"{classification.review_regime}"
            ),
            'estimated_completion': now,
        },
    ]

    approval_requirements = [
        {
            'id': 'sentinel_cosign',
            'description': 'Sentinel Agent co-signs the capability addition (graduation_cosign action class)',
            'status': 'pending',
            'assigned_to': 'sentinel-agent',
            'requested': False,
        },
        {
            'id': 'equilibrium_overlap_check',
            'description': 'Equilibrium Agent confirms new capability does not push overlap above 0.25',
            'status': 'pending',
            'assigned_to': 'equilibrium-agent',
            'requested': False,
        },
    ]

    # Per the REVIEW_TABLE, an Observing-tier agent adding a Colony-wide
    # capability requires Governance Council review. Reflect that here.
    if classification.review_regime == 'Governance Council':
        approval_requirements.append(
            {
                'id': 'human_governance_review',
                'description': (
                    'Human governance review required: Observing-tier agent, '
                    'Colony-wide blast radius'
                ),
                'status': 'pending',
                'assigned_to': 'governance_council',
                'requested': False,
            }
        )

    external_actions = [
        {
            'id': 'mirror_registry_update',
            'description': f'Push updated Mirror for {agent_id} to the Registry',
            'status': 'pending',
            'blast_radius': classification.blast_radius,
            'review_regime': classification.review_regime,
            'notes': 'Registry Agent will validate schema compliance before accepting',
        },
        {
            'id': 'chronicler_event',
            'description': 'Record graduation event to Colony Event Memory',
            'status': 'pending',
            'blast_radius': 'Local',
            'review_regime': 'Event-line',
        },
    ]

    total = len(evidence_requirements) + len(approval_requirements) + len(external_actions)
    complete = sum(
        1
        for item in evidence_requirements + approval_requirements + external_actions
        if item.get('status') == 'complete'
    )
    pending = sum(
        1
        for item in evidence_requirements + approval_requirements + external_actions
        if item.get('status') == 'pending'
    )
    in_progress = sum(
        1
        for item in evidence_requirements + approval_requirements + external_actions
        if item.get('status') == 'in_progress'
    )

    return {
        'agent_id': agent_id,
        'capability_added': capability,
        'generated': now,
        'classification': {
            'action_class': classification.action_class,
            'blast_radius': classification.blast_radius,
            'review_regime': classification.review_regime,
            'actor_trust_tier': classification.actor_trust_tier,
        },
        'evidence_requirements': evidence_requirements,
        'approval_requirements': approval_requirements,
        'external_actions': external_actions,
        'summary': {
            'total_items': total,
            'complete': complete,
            'in_progress': in_progress,
            'pending': pending,
            'blockers': 0,
        },
    }


def write_checklist(checklist_dict: dict, state_dir: str) -> str:
    """Write a checklist to ``state/graduation-checklists/<ts>-<agent>-<cap>.yaml``.

    Returns the written path.
    """
    out_dir = os.path.join(state_dir, 'graduation-checklists')
    os.makedirs(out_dir, exist_ok=True)

    ts = (
        checklist_dict.get('generated', '')
        .replace(':', '')
        .replace('-', '')
        .replace('T', '-')
        .replace('Z', '')
    ) or datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')

    filename = f"{ts}-{checklist_dict['agent_id']}-{checklist_dict['capability_added']}.yaml"
    path = os.path.join(out_dir, filename)

    with open(path, 'w') as f:
        yaml.safe_dump(checklist_dict, f, sort_keys=False, default_flow_style=False)

    return path
