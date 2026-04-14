"""Structural Classifier — pure function, no LLM.

Given an action and a context, return a ``Classification`` describing the
action's blast radius, the actor's trust tier, the action class, and the
review regime that must be applied. This is the mechanical enforcement of
the Comprehension Contract (specification §7).

The ``REVIEW_TABLE`` is the authoritative matrix mapping
``(trust_tier, blast_radius) -> review_regime``.
"""
from __future__ import annotations

from typing import Any

try:
    from examples.teaching_colony.contract import Classification
except ImportError:  # fallback when run from inside examples/teaching_colony/
    from contract import Classification  # type: ignore


REVIEW_TABLE: dict[str, dict[str, str]] = {
    'Observing': {
        'Local': 'Event-line',
        'Inter-agent': 'Peer Review',
        'Colony-wide': 'Governance Council',
        'Boundary-crossing': 'Governance Council',
    },
    'Sandboxed': {
        'Local': 'Event-line',
        'Inter-agent': 'Peer Review',
        'Colony-wide': 'Governance Council',
        'Boundary-crossing': 'Governance Council',
    },
    'Bounded': {
        'Local': 'Event-line',
        'Inter-agent': 'Event-line',
        'Colony-wide': 'Peer Review',
        'Boundary-crossing': 'Governance Council',
    },
    'Self-Directed': {
        'Local': 'Event-line',
        'Inter-agent': 'Event-line',
        'Colony-wide': 'Peer Review',
        'Boundary-crossing': 'Peer Review',
    },
}


# Action class → default blast radius when the caller has not specified one.
ACTION_BLAST_RADIUS: dict[str, str] = {
    'mirror_capability_add': 'Colony-wide',
    'mirror_capability_remove': 'Colony-wide',
    'mirror_patch_application': 'Colony-wide',
    'kb_write': 'Inter-agent',
    'kb_read': 'Local',
    'agent_dispatch': 'Local',
    'event_record': 'Local',
    'graduation_cosign': 'Colony-wide',
    'patch_application_cosign': 'Colony-wide',
    'external_api_call': 'Boundary-crossing',
}


# Action classes that are "Constitutional" per §7.4 — always route to
# Governance Council regardless of tier/blast-radius lookup.
CONSTITUTIONAL_ACTIONS: set[str] = {
    'mirror_patch_application',  # security patch to a Mirror
    'external_api_call',         # crosses the Coexistence Boundary
}

# Action classes that are "Novel" per §7.4 — route to Peer Review regardless
# of tier. This covers the first time a capability is added to an agent
# (a structural Mirror change that cannot be event-lined and should not
# require Governance Council for every instance).
NOVEL_ACTIONS: set[str] = {
    'mirror_capability_add',
    'mirror_capability_remove',
}

# Action classes that are "Pre-registered" per §7.4 — route to Event-line
# provided the actor's policy for that class is current. The context dict
# must then carry ``preauthorised_policies`` with a matching entry.
PRE_REGISTERED_ACTIONS: set[str] = {
    'graduation_cosign',
    'patch_application_cosign',
}


def classify_action(action: dict, context: dict) -> Classification:
    """Classify an action per §7.4 review regime formula.

    The formula short-circuits in a specific order:

    1. Constitutional → Governance Council
    2. Novel → Peer Review
    3. Pre-registered + current + low blast → Event-line
    4. Otherwise → REVIEW_TABLE[trust_tier][blast_radius]

    Parameters
    ----------
    action : dict
        Must contain ``class`` (the action class). Optionally ``blast_radius``.
    context : dict
        Must contain ``actor_trust_tier``. Optionally ``actor``,
        ``preauthorised_policies`` (list of dicts with ``action_class``
        and ``freshness`` fields).

    Returns
    -------
    Classification
    """
    action_class = action.get('class', 'unknown')
    actor_trust_tier = context.get('actor_trust_tier', 'Observing')

    # Fix 6 — gate caller-supplied blast_radius.
    # If the action class is in ACTION_BLAST_RADIUS, the table wins
    # regardless of what the caller passes. Callers cannot downgrade
    # the blast radius of a known action class (the §7 Comprehension
    # Contract property "callers cannot classify their own actions").
    # Caller override only applies for action classes the table does
    # not know about — in which case we still prefer the over-report
    # default of 'Local' if nothing is supplied.
    if action_class in ACTION_BLAST_RADIUS:
        blast_radius = ACTION_BLAST_RADIUS[action_class]
    else:
        blast_radius = action.get('blast_radius') or 'Local'

    # Step 1 — Constitutional
    if action_class in CONSTITUTIONAL_ACTIONS:
        review_regime = 'Governance Council'

    # Step 2 — Novel
    elif action_class in NOVEL_ACTIONS:
        review_regime = 'Peer Review'

    # Step 3 — Pre-registered with current policy and low blast radius
    elif action_class in PRE_REGISTERED_ACTIONS:
        policies = context.get('preauthorised_policies') or []
        current = any(
            p.get('action_class') == action_class
            and p.get('freshness', 'current') == 'current'
            for p in policies
        )
        if current and blast_radius in ('Local', 'Inter-agent'):
            review_regime = 'Event-line'
        else:
            tier_row = REVIEW_TABLE.get(actor_trust_tier, REVIEW_TABLE['Observing'])
            review_regime = tier_row.get(blast_radius, 'Governance Council')

    # Step 4 — Otherwise: REVIEW_TABLE lookup
    else:
        tier_row = REVIEW_TABLE.get(actor_trust_tier, REVIEW_TABLE['Observing'])
        review_regime = tier_row.get(blast_radius, 'Governance Council')

    return Classification(
        blast_radius=blast_radius,
        review_regime=review_regime,
        action_class=action_class,
        actor_trust_tier=actor_trust_tier,
    )
