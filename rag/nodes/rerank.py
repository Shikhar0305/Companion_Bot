"""Node 4 — rerank + relevance gate (docs/03 §3.3).

Reranks retrieved candidates, drops anything below the relevance floor, and
routes to abstain when too few passages survive.
"""
from __future__ import annotations

import re

from core.types import RetrievedChunk
from rag.nodes.verify import extract_legal_refs
from rag.services import Services
from rag.state import GraphState

# A query with conceptual intent ("what is X", "define X") must NOT trigger the
# conceptual-demotion — otherwise legitimate definitional questions break.
_CONCEPTUAL_QUERY = re.compile(
    r"\b(what is|what are|what does|define|definition|meaning of|explain|"
    r"concept of|overview of|introduction to|difference between)\b",
    re.IGNORECASE,
)
# ...but an operational cue overrides the exemption: "what is the ROLE of / the
# PROCEDURE for" is an operational question and must still demote conceptual
# background (e.g. "what is the role of the 1930 helpline" -> the recovery repo,
# not the SOP's conceptual overview of 1930).
_OPERATIONAL_CUE = re.compile(
    r"\b(role of|procedure|steps|process|how to|how do|obtain|request|freeze|"
    r"trace|seize|collect|prepare|workflow|investigate|recover|maintain|conduct)\b",
    re.IGNORECASE,
)


def _is_conceptual_query(query: str) -> bool:
    return bool(_CONCEPTUAL_QUERY.search(query)) and not _OPERATIONAL_CUE.search(query)


def _apply_sop_priority(query: str, ranked: list[RetrievedChunk], cfg) -> list[RetrievedChunk]:
    """Query-aware SOP conceptual-demotion / operational-boost (Phase 3).

    Only SOP chunks are touched (legal/decision-tree/recovery are untouched).
    Conceptual-intent queries are exempt so definitional questions still work.
    Returns a re-sorted list.
    """
    if _is_conceptual_query(query):
        return ranked
    adjusted: list[RetrievedChunk] = []
    for rc in ranked:
        w = 1.0
        c = rc.chunk
        if c.doc_type == "sop" and c.priority is not None:
            if c.priority <= 1:
                w = cfg.sop_conceptual_penalty      # demote background
            elif c.priority >= 4:
                w = cfg.sop_operational_boost        # boost operational procedures
        adjusted.append(RetrievedChunk(c, rc.score * w, rc.source))
    adjusted.sort(key=lambda r: r.score, reverse=True)
    return adjusted


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
    # Rerank the full candidate pool, apply SOP priority weighting, then take the
    # top-N — so a demoted conceptual chunk can yield its slot to an operational
    # one that was ranked just outside the cut. (For non-SOP results this is
    # identical to reranking straight to top-N.)
    ranked = services.reranker.rerank(query, state.retrieved, len(state.retrieved))
    ranked = _apply_sop_priority(query, ranked, cfg)[: cfg.rerank_top_n]

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
