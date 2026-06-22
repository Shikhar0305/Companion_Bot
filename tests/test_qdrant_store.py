"""QdrantVectorStore against an embedded (:memory:) Qdrant — no server/docker.

Skipped automatically when qdrant-client is not installed.
"""
from __future__ import annotations

import pytest

pytest.importorskip("qdrant_client")

from core.types import Chunk
from rag.retrieval.embeddings import HashingEmbedder
from rag.retrieval.vector_store import (
    InMemoryVectorStore,
    QdrantVectorStore,
    build_vector_store,
)


def _store(collection="test_kb"):
    emb = HashingEmbedder(dim=64)
    return QdrantVectorStore(url=":memory:", collection=collection, embedder=emb), emb


def _chunks():
    return [
        Chunk(chunk_id="a1", doc_id="itact", doc_type="act", title="IT Act",
              text="Section 66C punishment for identity theft password unique id",
              section_number="66C", extra_metadata={"cognizable": True, "statute_code": "IT_ACT"}),
        Chunk(chunk_id="r1", doc_id="ncrp", doc_type="recovery", title="NCRP Workflow",
              text="National cyber crime reporting portal NCRP and 1930 helpline reporting",
              procedure_name="Purpose",
              extra_metadata={"recovery_stage": "reporting", "channels": ["NCRP", "1930"]}),
    ]


def _load(store, emb, chunks):
    store.upsert(chunks, emb.embed([c.text for c in chunks]))


def test_collection_created_automatically():
    store, _ = _store()
    assert store.count() == 0  # collection exists and is queryable


def test_upsert_stores_embeddings_and_metadata():
    store, emb = _store()
    _load(store, emb, _chunks())
    assert store.count() == 2
    got = store.get("a1")
    assert got is not None
    assert got.doc_type == "act" and got.section_number == "66C"
    # full metadata payload round-trips, including the sidecar extra_metadata
    assert got.extra_metadata["cognizable"] is True
    assert got.extra_metadata["statute_code"] == "IT_ACT"


def test_search_returns_relevant_chunk():
    store, emb = _store()
    _load(store, emb, _chunks())
    hits = store.search("identity theft password", emb.embed_one("identity theft password"), k=5)
    assert hits, "expected at least one hit"
    assert any(h.chunk.chunk_id == "a1" for h in hits)
    assert all(0.0 <= h.score for h in hits)


def test_search_honours_metadata_filter():
    store, emb = _store()
    _load(store, emb, _chunks())
    hits = store.search("reporting portal", emb.embed_one("reporting portal"),
                        k=5, filters={"doc_type": ["recovery"]})
    assert hits and all(h.chunk.doc_type == "recovery" for h in hits)


def test_upsert_is_idempotent():
    store, emb = _store()
    chunks = _chunks()
    _load(store, emb, chunks)
    _load(store, emb, chunks)  # same chunk_ids → overwrite, not duplicate
    assert store.count() == 2


def test_build_vector_store_returns_qdrant_when_available():
    emb = HashingEmbedder(dim=64)
    store = build_vector_store("qdrant", emb, url=":memory:", collection="built_kb")
    assert isinstance(store, QdrantVectorStore)
    assert not isinstance(store, InMemoryVectorStore)
