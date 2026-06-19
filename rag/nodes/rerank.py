"""Node 4 — rerank + relevance gate (docs/03 §3.3).

Reranks retrieved candidates, drops anything below the relevance floor, and
routes to abstain when too few passages survive.
"""
from __future__ import annotations

from rag.nodes.verify import extract_legal_refs
from rag.services import Services
from rag.state import GraphState


def _queried_section_present(query: str, survivors) -> bool:
    """If the query names specific legal section(s), at least one retrieved
    passage must contain one of them — otherwise we cannot answer about a
    provision the KB does not hold (zero-fabrication rule, docs/03 §3.4)."""
    refs = extract_legal_refs(query)
    if not refs:
        return True  # no explicit section in the query — rule does not apply
    for rc in survivors:
        text = rc.chunk.text.lower()
        sec = (rc.chunk.section_number or "").lower()
        if any(ref == sec or ref in text for ref in refs):
            return True
    return False


def rerank(state: GraphState, services: Services) -> GraphState:
    cfg = services.config
    if not state.retrieved:
        state.abstain = True
        state.abstain_reason = "no_retrieval"
        return state

    query = state.analysis.rewritten_query if state.analysis else state.query
    ranked = services.reranker.rerank(query, state.retrieved, cfg.rerank_top_n)

    survivors = [rc for rc in ranked if rc.score >= cfg.relevance_floor]
    if len(survivors) < cfg.min_supporting:
        state.reranked = ranked  # keep for audit
        state.abstain = True
        state.abstain_reason = "below_relevance_floor"
        return state

    # Hard rule: a question about a specific section we do not hold must abstain.
    if not _queried_section_present(state.query, survivors):
        state.reranked = survivors
        state.abstain = True
        state.abstain_reason = "queried_section_not_in_kb"
        return state

    state.reranked = survivors
    return state
