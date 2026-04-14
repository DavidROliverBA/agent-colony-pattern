"""Substrate Contract — the eight operations L4 owes L1-L3.

Every substrate adapter (Claude Code, Managed Agents API, or any future
substrate) must implement this abstract base class. The lifecycle driver
in ``run.py`` is substrate-independent; it talks only to ``SubstrateContract``.

The eight operations
====================

==============================  =====================================================
Operation                       Purpose
==============================  =====================================================
``dispatch_agent``              Execute an agent by id with structured input.
``read_mirror``                 Load an agent's Agent Mirror YAML from the substrate.
``update_mirror``               Apply a change to a Mirror, with co-signer + audit.
``record_event``                Append an event to the colony Event Memory.
``read_kb``                     Query the colony knowledge base for documents.
``write_kb``                    Write a topic entry to the colony knowledge base.
``co_sign``                     Obtain a co-signature for a given action class.
``classify_action``             Classify blast radius + review regime for an action.
==============================  =====================================================

Design notes
------------
* Classification happens *inside* the substrate (see ``classify_action``) so
  that callers cannot bypass the Comprehension Contract's review regime.
* ``update_mirror`` returns an ``AuditEntry`` — substrates that do not produce
  a pre/post state hash must still emit one (e.g. sha256 of the YAML text).
* All operations are intentionally small and synchronous. Any batching or
  streaming is an adapter concern, not a contract concern.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Mirror:
    agent_id: str
    data: dict  # Full YAML-loaded mirror content


@dataclass
class Event:
    type: str
    actor: str
    payload: dict
    timestamp: str = ""
    substrate: str = ""


@dataclass
class Document:
    path: str
    topic: str
    content: str
    provenance: str = ""
    cross_references: list[str] = field(default_factory=list)


@dataclass
class AuditEntry:
    action: str
    actor: str
    co_signer: str
    pre_state_hash: str
    post_state_hash: str
    timestamp: str
    rollback_window_minutes: int = 60


@dataclass
class Signature:
    action_class: str
    actor: str
    co_signer: str
    granted: bool
    timestamp: str
    reason: str = ""


@dataclass
class Classification:
    blast_radius: str  # 'Local' | 'Inter-agent' | 'Colony-wide' | 'Boundary-crossing'
    review_regime: str  # 'Event-line' | 'Peer Review' | 'Governance Council'
    action_class: str
    actor_trust_tier: str


class SubstrateContract(ABC):
    """Abstract contract every substrate adapter must implement.

    The eight operations below are what L4 (Substrate) owes L1-L3 in the
    Agent Colony four-layer architecture (L1 Agent, L2 Colony, L3 Domain,
    L4 Substrate).
    """

    @abstractmethod
    def dispatch_agent(self, agent_id: str, input: dict) -> dict:
        ...

    @abstractmethod
    def read_mirror(self, agent_id: str) -> Mirror:
        ...

    @abstractmethod
    def update_mirror(self, agent_id: str, changes: dict, co_signer: str) -> AuditEntry:
        ...

    @abstractmethod
    def record_event(self, event: Event) -> None:
        ...

    @abstractmethod
    def read_kb(self, query: str) -> list[Document]:
        ...

    @abstractmethod
    def write_kb(self, topic: str, content: str, provenance: str) -> None:
        ...

    @abstractmethod
    def co_sign(self, action_class: str, actor: str, co_signer: str) -> Signature:
        ...

    @abstractmethod
    def classify_action(self, action: dict, context: dict) -> Classification:
        ...
