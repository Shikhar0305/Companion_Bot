"""SOP-first routing + footnote sanitization (regression for SOP-SEM misses).

Two SOP-procedural queries — "What details to collect from a complainant?" and
"How to prepare a charge sheet for cybercrime?" — used to miss the SOP repository:

* the SOP source carries academic footnote markers ("[42]") that the grounding
  verifier mis-parses as citation markers, so any verbatim-quoted SOP passage
  tripped the gate and abstained; and
* both queries fall into the weak-signal "investigation" bucket, whose broad
  filter let clean decision-tree / recovery passages out-rank the SOP section.

`clean_text` now strips the footnote markers; `query_analysis` routes SOP
case-documentation queries SOP-first. These tests lock in both, and guard that
non-SOP routing and the chunker's own "[[PAGE n]]" markers are untouched.
"""
from __future__ import annotations

import os

from ingestion.clean import clean_text
from ingestion.discovery import discover_corpus
from ingestion.embed import embed_and_load
from ingestion.pipeline import process_markdown, process_textfile
from ingestion.sidecar import enrich_chunks, load_sidecar_index
from rag.graph import AnswerPipeline
from rag.nodes.query_analysis import query_analysis
from rag.services import build_services
from rag.state import GraphState


# 1. Sanitization: footnote markers go, page markers stay ----------------------
def test_clean_text_strips_footnote_markers():
    assert clean_text("Chain of custody must be maintained [42].") == \
        "Chain of custody must be maintained ."
    assert clean_text("First [1] then [23] then [100].") == "First then then ."


def test_clean_text_preserves_page_markers():
    # The structure-aware chunker relies on "[[PAGE n]]"; it must survive cleaning.
    assert "[[PAGE 7]]" in clean_text("[[PAGE 7]]\nSection 4.2 preservation [3].")


# 2. Routing: SOP-procedural queries narrow to SOP-first, others unchanged -----
def _filter_for(query: str) -> list[str]:
    state = GraphState(query=query, user_role="officer", kb_version="kb_v1")
    return query_analysis(state, services=None).analysis.doc_type_filter


def test_sop_procedural_queries_route_sop_first():
    for q in ("What details to collect from a complainant?",
              "How to prepare a charge sheet for cybercrime?",
              "What goes into the case diary?"):
        assert _filter_for(q) == ["sop", "manual"], q


def test_non_sop_routing_is_unchanged():
    # A confident legal query still routes to the legal repository...
    assert set(_filter_for("Punishment under IT Act Section 66C?")) == {"act", "sanhita"}
    # ...a recovery query is not hijacked SOP-first...
    assert "recovery" in _filter_for("How to freeze a fraudulent bank account?")
    # ...and a decision-tree crime query keeps decision_tree in scope.
    assert "decision_tree" in _filter_for("Workflow to investigate UPI banking fraud?")


# 3. End-to-end: both target queries now cite the SOP repository ---------------
def _corpus_pipeline() -> AnswerPipeline:
    services = build_services(embedder_name="hash", vector_store_name="memory",
                              reranker_name="noop", llm_profile="stub")
    sources, sidecars = discover_corpus("data/corpus")
    index = load_sidecar_index(sidecars)
    chunks = []
    for s in sources:
        if s.fmt == "md":
            ch = process_markdown(s.spec)
        elif s.fmt == "text":
            ch = process_textfile(s.spec)
        else:
            continue
        enrich_chunks(ch, os.path.basename(s.spec.path), index)
        chunks += ch
    embed_and_load(chunks, services.embedder, services.vector_store)
    return AnswerPipeline(services)


def test_sop_procedural_queries_cite_sop_end_to_end():
    if not os.path.isdir("data/corpus/sop_repository"):
        return  # corpus not present in this checkout
    pipe = _corpus_pipeline()
    for q in ("What details to collect from a complainant?",
              "How to prepare a charge sheet for cybercrime?"):
        a = pipe.run(q).answer
        assert not a.abstained and not a.refused, q
        assert any(c.doc_type == "sop" for c in a.citations), \
            (q, [(c.doc_id, c.doc_type) for c in a.citations])
