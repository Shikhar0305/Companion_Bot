"""Node 3 — hybrid retrieval with metadata filtering (docs/03 §3.3)."""
from __future__ import annotations

from rag.services import Services
from rag.state import GraphState


def retrieve(state: GraphState, services: Services) -> GraphState:
    analysis = state.analysis
    query = analysis.rewritten_query if analysis else state.query

    # Metadata filter: prefer the capability area's doc types; the store treats
    # an empty/None filter as "no constraint".
    filters = {}
    if analysis and analysis.doc_type_filter:
        filters["doc_type"] = analysis.doc_type_filter

    qvec = services.embedder.embed_one(query)
    results = services.vector_store.search(
        query_text=query, query_vector=qvec,
        k=services.config.retrieve_k, filters=filters or None,
    )
    # Fallback: if the doc_type filter is too narrow, retry unfiltered.
    if not results and filters:
        results = services.vector_store.search(
            query_text=query, query_vector=qvec, k=services.config.retrieve_k,
        )
    state.retrieved = results
    return state
