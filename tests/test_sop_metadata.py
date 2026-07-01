"""Phase 3 — SOP metadata enrichment + query-aware conceptual demotion.

The demotion's real-world lift is e5-specific (hash retrieval doesn't over-surface
conceptual content), so the ranking effect is proven here with a deterministic
unit test on the weighting function, plus ingestion/sidecar coverage.
"""
from __future__ import annotations

import os

import pytest

from core.types import Chunk, RetrievedChunk
from ingestion.sop_classify import classify
from rag.nodes.rerank import _CONCEPTUAL_QUERY, _apply_sop_priority
from rag.services import PipelineConfig


# --- heading-anchored classification ----------------------------------------

def test_classify_conceptual_heading():
    m = classify("1.1", "Introduction: Understanding Cybercrime")
    assert m["section_type"] == "conceptual" and m["priority"] == 1


def test_classify_operational_heading():
    m = classify("8.16", "Write Blockers and Their Evidentiary Significance")
    assert m["section_type"] == "forensic_procedure" and m["priority"] == 5


def test_classify_conceptual_cue_wins_over_topic():
    # "Introduction to Chain of Custody" is background despite naming a procedure.
    assert classify("7.1", "Introduction to Chain of Custody")["section_type"] == "conceptual"


# --- weighting function (the demotion mechanism) ----------------------------

def _sop(priority, score, cid):
    return RetrievedChunk(
        Chunk(chunk_id=cid, doc_id="sopcchq", doc_type="sop", title="SOP",
              text="x", priority=priority), score, "rerank")


def test_operational_query_demotes_conceptual_below_operational():
    cfg = PipelineConfig()  # penalty 0.5, boost 1.0
    # Conceptual chunk out-scores operational before demotion (the e5 failure mode).
    ranked = [_sop(1, 0.40, "concept"), _sop(5, 0.30, "oper")]
    out = _apply_sop_priority("how to seize a mobile phone", ranked, cfg)
    assert out[0].chunk.chunk_id == "oper"  # 0.40*0.5=0.20 < 0.30 -> operational wins


def test_conceptual_query_is_exempt():
    cfg = PipelineConfig()
    ranked = [_sop(1, 0.40, "concept"), _sop(5, 0.30, "oper")]
    out = _apply_sop_priority("what is chain of custody", ranked, cfg)
    assert out[0].chunk.chunk_id == "concept"  # not demoted for a definitional query


def test_non_sop_chunks_untouched():
    cfg = PipelineConfig()
    recovery = RetrievedChunk(
        Chunk(chunk_id="r1", doc_id="rec", doc_type="recovery", title="R", text="x"),
        0.35, "rerank")
    ranked = [_sop(5, 0.30, "oper"), recovery]
    out = _apply_sop_priority("how to freeze a bank account", ranked, cfg)
    # Recovery stays top (0.35 > 0.30): no boost inflates SOP over other repos.
    assert out[0].chunk.chunk_id == "r1"


def test_conceptual_query_regex():
    assert _CONCEPTUAL_QUERY.search("what is cybercrime")
    assert _CONCEPTUAL_QUERY.search("define electronic evidence")
    assert not _CONCEPTUAL_QUERY.search("how to seize a mobile phone")


# --- ingestion coverage ------------------------------------------------------

ARTIFACT = "data/corpus/sop_repository/SOPCCHQ.sop.txt"

@pytest.mark.skipif(not os.path.isfile(ARTIFACT), reason="SOP artifact absent")
def test_all_sop_chunks_have_metadata():
    from ingestion.discovery import discover_corpus
    from ingestion.pipeline import process_textfile
    src = [s for s in discover_corpus("data/corpus")[0] if s.spec.doc_type == "sop"][0]
    chunks = process_textfile(src.spec)
    assert all(c.section_type and c.priority for c in chunks)


@pytest.mark.skipif(not os.path.isfile(ARTIFACT), reason="SOP artifact absent")
def test_sidecar_override_applied():
    from ingestion.discovery import discover_corpus
    from ingestion.pipeline import process_textfile
    from ingestion.sidecar import enrich_chunks, load_sidecar_index
    srcs, sidecars = discover_corpus("data/corpus")
    src = [s for s in srcs if s.spec.doc_type == "sop"][0]
    chunks = process_textfile(src.spec)
    enrich_chunks(chunks, "SOPCCHQ.sop.txt", load_sidecar_index(sidecars))
    c = next(x for x in chunks if x.sop_section == "8.16")
    assert c.topic == "write_blocker" and c.section_type == "forensic_procedure"
