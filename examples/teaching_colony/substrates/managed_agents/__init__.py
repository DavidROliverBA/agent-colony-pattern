"""Managed Agents substrate adapter for the Teaching Colony.

Work in progress — see api-research.md and README.md. The working live
path is scheduled for v1.6.0 Batch 2 (Sub-agent D). Mock mode is
complete enough to run the lifecycle offline.
"""

from .adapter import ManagedAgentsAdapter

__all__ = ["ManagedAgentsAdapter"]
