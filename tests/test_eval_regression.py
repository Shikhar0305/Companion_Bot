"""Regression tests for the evaluation failures (refusals, legal & DT routing).

Covers every query from the failed evaluation set: valid investigator queries
must not be refused, legal queries must reach the legal repository, decision-tree
queries must hit the right crime tree, and unrelated domains must still refuse.
"""
from __future__ import annotations

import os

import pytest

from ingestion.discovery import discover_corpus
from ingestion.embed import embed_and_load
from ingestion.pipeline import process_markdown
from ingestion.sidecar import enrich_chunks, load_sidecar_index
from rag.graph import AnswerPipeline
from rag.nodes.guardrail import _in_scope
from rag.services import build_services

LEGAL_DOCS = {"it_act", "bns", "bnss", "bsa", "dpdp", "pocso"}


@pytest.fixture(scope="module")
def corpus_pipeline():
    if not os.path.isdir("data/corpus"):
        pytest.skip("corpus not present")
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


# --- Guardrail: investigator terminology is in-scope (fast, no corpus) -------
VALID_QUERIES = [
    "What legal provisions apply to unauthorized computer access?",
    "What legal provisions apply to online sexual exploitation?",
    "What records should be preserved from service providers?",
    "What information should be collected from the complainant during initial reporting?",
    "How should investigators trace funds across multiple transactions?",
    "What legal provisions apply to malware deployment?",
    "What legal provisions apply to phishing attacks?",
]


@pytest.mark.parametrize("q", VALID_QUERIES)
def test_valid_investigator_queries_in_scope(q):
    assert _in_scope(q), f"wrongly out-of-scope: {q!r}"


REFUSE_QUERIES = [
    "What is the weather today?",
    "Who won the cricket match?",
    "Recommend a good movie.",
    "Best travel destinations in Europe?",
    "How do I cook biryani?",
    "Tell me a joke.",
    "What is the capital of France?",
]


@pytest.mark.parametrize("q", REFUSE_QUERIES)
def test_unrelated_domains_refused(q):
    assert not _in_scope(q), f"wrongly in-scope: {q!r}"


# --- End-to-end: valid queries are never refused ----------------------------
@pytest.mark.parametrize("q", VALID_QUERIES)
def test_valid_queries_not_refused_end_to_end(corpus_pipeline, q):
    ans = corpus_pipeline.run(q).answer
    assert not ans.refused, f"refused valid query: {q!r}"


# --- Legal queries reach the legal repository -------------------------------
@pytest.mark.parametrize("q", [
    "What legal provisions apply to malware deployment?",
    "What legal provisions apply to phishing attacks?",
    "What legal provisions apply to unauthorized computer access?",
    "What legal provisions apply to online sexual exploitation?",
])
def test_legal_queries_reach_legal_repository(corpus_pipeline, q):
    ans = corpus_pipeline.run(q).answer
    assert ans.citations, f"no citations for {q!r}"
    assert any(c.doc_id in LEGAL_DOCS for c in ans.citations), \
        f"{q!r} did not reach legal repo: {[c.doc_id for c in ans.citations]}"


# --- Decision-tree queries hit the right crime tree -------------------------
@pytest.mark.parametrize("q,expected", [
    ("What is the decision tree for romance scam?", "10_romance_scam"),
    ("How to investigate fake loan application fraud?", "05_loan_app_fraud"),
    ("How to investigate fake trading platform fraud?", "04_trading_scam"),
])
def test_decision_tree_queries_hit_correct_tree(corpus_pipeline, q, expected):
    ans = corpus_pipeline.run(q).answer
    assert any(expected in c.doc_id for c in ans.citations), \
        f"{q!r} expected {expected}, got {[c.doc_id for c in ans.citations]}"


# --- Unrelated domains still refused end-to-end -----------------------------
@pytest.mark.parametrize("q", REFUSE_QUERIES)
def test_unrelated_refused_end_to_end(corpus_pipeline, q):
    assert corpus_pipeline.run(q).answer.refused, f"should refuse: {q!r}"
