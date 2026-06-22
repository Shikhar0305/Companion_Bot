"""Decision-tree routing + markdown chunk hygiene (regression for the UPI bug)."""
from __future__ import annotations

import os

from ingestion.chunk import chunk_markdown
from ingestion.discovery import discover_corpus
from ingestion.embed import embed_and_load
from ingestion.pipeline import process_markdown
from ingestion.sidecar import enrich_chunks, load_sidecar_index
from rag.graph import AnswerPipeline
from rag.nodes.query_analysis import _AREA_DOC_TYPES
from rag.services import build_services

DT_MD = """# UPI / Banking Fraud

> **Source:** CCHQ_formatted.docx — Chapter 1: UPI / Banking Fraud.
> **Provenance:** Grounded in the SOP.
> **Risk level:** High | **Priority:** P2

## Initial Triage

IF complaint received THEN register FIR and assign an investigating officer.

## Escalation Decisions

IF cross-state THEN escalate to the nodal officer.
"""


# 1. Routing: money-flavoured crime queries can reach decision trees ----------
def test_financial_and_investigation_reach_decision_trees():
    assert "decision_tree" in _AREA_DOC_TYPES["financial"]
    assert "decision_tree" in _AREA_DOC_TYPES["investigation"]


# 2. Chunk hygiene: provenance/title boilerplate is not chunked ---------------
def test_markdown_chunking_strips_boilerplate_and_keeps_title_context():
    chunks = chunk_markdown(DT_MD, "upi", "UPI / Banking Fraud", "decision_tree")
    names = {c.procedure_name for c in chunks}
    assert names == {"Initial Triage", "Escalation Decisions"}  # no title/preamble chunk

    blob = " ".join(c.text for c in chunks)
    assert "Provenance:" not in blob
    assert "Source:" not in blob
    assert "Risk level:" not in blob

    # document title is carried into each section chunk for retrieval context
    assert all("UPI / Banking Fraud" in c.text for c in chunks)


# 3. End-to-end: the reported query now cites the UPI decision tree -----------
def _corpus_pipeline():
    services = build_services(embedder_name="hash", vector_store_name="memory",
                             reranker_name="noop", llm_profile="stub")
    sources, sidecars = discover_corpus("data/corpus")
    index = load_sidecar_index(sidecars)
    chunks = []
    for s in sources:
        if s.fmt != "md":
            continue
        ch = process_markdown(s.spec)
        enrich_chunks(ch, os.path.basename(s.spec.path), index)
        chunks += ch
    embed_and_load(chunks, services.embedder, services.vector_store)
    return AnswerPipeline(services)


def test_upi_investigation_query_cites_decision_tree():
    if not os.path.isdir("data/corpus/decision_trees"):
        return  # corpus not present in this checkout
    pipe = _corpus_pipeline()
    a = pipe.run("What are the steps to investigate UPI banking fraud?").answer
    assert not a.abstained and not a.refused
    assert any(c.doc_type == "decision_tree" for c in a.citations), \
        [(c.doc_id, c.doc_type) for c in a.citations]
