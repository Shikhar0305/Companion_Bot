"""Phase 4 — Okapi BM25 lexical channel + legal section-number fast-path.

BM25's end-to-end benefit needs a semantic dense channel (e5) to agree with it,
so it is opt-in (HYBRID_SPARSE=bm25) and validated on e5. These tests prove the
BM25 scoring itself (IDF, rare-term ranking, keyword boost) and the fast-path
exact-section pin — both embedder-independent.
"""
from __future__ import annotations

from core.types import Chunk
from rag.retrieval.bm25 import BM25Index
from rag.retrieval.vector_store import InMemoryVectorStore


# --- BM25 scoring ------------------------------------------------------------

def test_rare_term_ranks_target_first():
    idx = BM25Index()
    idx.add("d1", "the write blocker prevents changes to the seized disk")
    idx.add("d2", "the officer recorded the statement in the case diary")
    idx.add("d3", "general procedure for the seizure of electronic devices")
    scores = idx.score("write blocker", ["d1", "d2", "d3"])
    assert max(scores, key=scores.get) == "d1"


def test_keyword_boost_increases_score():
    idx = BM25Index()
    idx.add("d1", "forensic acquisition of storage media", keywords=["write blocker"])
    idx.add("d2", "forensic acquisition of storage media")  # identical text, no keyword
    scores = idx.score("write blocker", ["d1", "d2"])
    assert scores.get("d1", 0.0) > scores.get("d2", 0.0)


def test_idf_downweights_common_terms():
    idx = BM25Index()
    for i in range(10):
        idx.add(f"c{i}", "seizure procedure evidence common general")
    idx.add("rare", "the ipdr subscriber record from the operator")
    scores = idx.score("ipdr", ["rare"] + [f"c{i}" for i in range(10)])
    assert max(scores, key=scores.get) == "rare"


def test_no_match_scores_nothing():
    idx = BM25Index()
    idx.add("d1", "chain of custody documentation")
    assert idx.score("cryptocurrency wallet", ["d1"]) == {}


# --- legal section-number fast-path -----------------------------------------

def _chunk(cid, dtype, sec):
    return Chunk(chunk_id=cid, doc_id=cid, doc_type=dtype, title=cid,
                 text=f"section {sec} text", section_number=sec)


def test_by_section_exact_lookup():
    store = InMemoryVectorStore()
    store.upsert([_chunk("s63", "sanhita", "63"), _chunk("s66", "act", "66C")],
                 [[0.1] * 4, [0.1] * 4])
    got = store.by_section({"63"}, {"act", "sanhita"})
    assert [c.chunk_id for c in got] == ["s63"]


def test_by_section_respects_doc_types():
    store = InMemoryVectorStore()
    store.upsert([_chunk("sopish", "sop", "63")], [[0.1] * 4])
    assert store.by_section({"63"}, {"act", "sanhita"}) == []  # SOP not a legal type


def test_retrieve_pins_named_legal_section():
    from ingestion.embed import embed_and_load
    from rag.nodes.query_analysis import query_analysis
    from rag.nodes.retrieve import retrieve
    from rag.services import PipelineConfig, build_services
    from rag.state import GraphState

    svc = build_services(embedder_name="hash", vector_store_name="memory",
                         reranker_name="noop", llm_profile="stub", config=PipelineConfig())
    chunks = [
        Chunk(chunk_id="it_66c", doc_id="itact", doc_type="act", title="IT Act",
              text="Punishment for identity theft is three years.", section_number="66C"),
        Chunk(chunk_id="sop_x", doc_id="sop", doc_type="sop", title="SOP",
              text="general investigation notes on identity fraud", sop_section="1.1", priority=5),
    ]
    embed_and_load(chunks, svc.embedder, svc.vector_store)
    st = GraphState(query="What is the punishment under section 66C?")
    query_analysis(st, svc)
    retrieve(st, svc)
    assert "it_66c" in [r.chunk.chunk_id for r in st.retrieved]  # pinned by fast-path
