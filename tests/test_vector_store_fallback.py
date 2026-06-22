"""build_vector_store fallback behaviour (no Qdrant required)."""
from __future__ import annotations

import pytest

import rag.retrieval.vector_store as vs
from rag.retrieval.embeddings import HashingEmbedder


def _boom(*args, **kwargs):
    raise RuntimeError("qdrant unreachable")


def test_memory_is_default():
    store = vs.build_vector_store("memory", HashingEmbedder(dim=32))
    assert isinstance(store, vs.InMemoryVectorStore)


def test_qdrant_falls_back_to_memory(monkeypatch):
    monkeypatch.setattr(vs, "QdrantVectorStore", _boom)
    store = vs.build_vector_store("qdrant", HashingEmbedder(dim=32), url="http://localhost:6333")
    assert isinstance(store, vs.InMemoryVectorStore)


def test_no_fallback_raises_when_disabled(monkeypatch):
    monkeypatch.setattr(vs, "QdrantVectorStore", _boom)
    with pytest.raises(RuntimeError):
        vs.build_vector_store("qdrant", HashingEmbedder(dim=32), allow_fallback=False)
