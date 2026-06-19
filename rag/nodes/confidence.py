"""Node 7 — confidence scoring (docs/03 §3.3 node 7).

confidence = f(top rerank score, score margin, #supporting passages, verifier).
"""
from __future__ import annotations

from rag.services import Services
from rag.state import GraphState


def score_confidence(top_score: float, margin: float, n_support: int, verifier_passed: bool) -> str:
    if not verifier_passed:
        return "low"
    if top_score >= 0.6 and n_support >= 2 and margin >= 0.1:
        return "high"
    if top_score >= 0.35 and n_support >= 1:
        return "medium"
    return "low"


def confidence(state: GraphState, services: Services) -> GraphState:
    passages = state.reranked
    top = passages[0].score if passages else 0.0
    margin = (passages[0].score - passages[1].score) if len(passages) >= 2 else top
    n_support = len(state.citations)
    passed = state.verifier_report.get("passed", False)
    state.confidence = score_confidence(top, margin, n_support, passed)
    return state
