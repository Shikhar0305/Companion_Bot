"""Node 3 — hybrid retrieval with metadata filtering (docs/03 §3.3)."""
from __future__ import annotations

from core.types import RetrievedChunk
from rag.nodes.verify import extract_legal_refs
from rag.services import Services
from rag.state import GraphState

_LEGAL_DOC_TYPES = {"act", "sanhita"}


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

    # Legal section-number fast-path: when the query names a section (e.g. "BSA
    # section 63"), pin the exact statute chunk regardless of how the query was
    # classified — dense/lexical ranking can otherwise miss or mis-route it.
    refs = extract_legal_refs(state.query)
    if refs and hasattr(services.vector_store, "by_section"):
        existing = {r.chunk.chunk_id for r in results}
        pins = [
            RetrievedChunk(chunk=c, score=1.0, source="section")
            for c in services.vector_store.by_section(refs, _LEGAL_DOC_TYPES)
            if c.chunk_id not in existing
        ]
        results = pins + results

    state.retrieved = results
    return state
