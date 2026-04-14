"""Thin wrapper exposing ``determine_review_regime``.

This module exists so callers that only care about the review regime (and
not the full Classification) have a one-call convenience API.
"""
from __future__ import annotations

from .classifier import classify_action


def determine_review_regime(action: dict, context: dict) -> str:
    """Return the review regime string for the given action + context."""
    return classify_action(action, context).review_regime
