"""Exceptions raised by the Comprehension Contract enforcement layer.

v1.7.0 introduces these to make update_mirror's enforcement clauses
visible and testable. See specification.md §7 and the spec
``2026-04-14-honest-teaching-colony-design.md`` for context.
"""


class ContractViolation(Exception):
    """Base class for all Comprehension Contract violations.

    Raised by substrate adapters when a proposed Mirror change would
    violate the §7 Comprehension Contract in a way the classifier,
    blast-radius ceiling, forbidden list, or co-signer policy can detect.
    """


class BlastRadiusViolation(ContractViolation):
    """A proposed change's blast radius exceeds the target agent's declared
    ``comprehension_contract.blast_radius_ceiling``.

    Example: Teacher declares ``blast_radius_ceiling: Inter-agent`` but the
    classifier returns ``blast_radius: Colony-wide`` for the proposed action.
    """


class ForbiddenEvolution(ContractViolation):
    """A proposed change matches an entry in the target agent's
    ``autonomy.self_evolution_scope.forbidden`` list.

    The forbidden list names changes the agent is NEVER allowed to make,
    even with a co-sign. Adapters must check every change against this
    list before writing.
    """


class UnauthorisedCoSign(ContractViolation):
    """The co-signer does not have a fresh pre-registered policy for the
    action class being co-signed.

    Per §7.4 the co-signer must carry a ``pre_registered_policies`` entry
    with the matching ``action_class`` and ``freshness: current``. If the
    entry is stale, missing, or belongs to a different action class, the
    co-sign is unauthorised.
    """
