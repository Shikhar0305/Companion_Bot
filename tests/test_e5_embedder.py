"""E5 embedder: the mandatory query:/passage: prefixes must be applied.

These are the #1 footgun for E5 — omitting them silently collapses retrieval.
The tests inject a fake encoder (bypassing __init__/model download) so they run
without sentence-transformers installed and assert the exact prefixed strings
that reach the model.
"""
from __future__ import annotations

from rag.retrieval.embeddings import E5SmallEmbedder


class _FakeST:
    def __init__(self) -> None:
        self.seen: list[str] = []

    def encode(self, texts, normalize_embeddings=True):
        self.seen.extend(texts)
        return [[0.0] * 384 for _ in texts]


def _embedder() -> tuple[E5SmallEmbedder, _FakeST]:
    e = E5SmallEmbedder.__new__(E5SmallEmbedder)  # bypass model load
    fake = _FakeST()
    e._model = fake
    e.dim = 384
    return e, fake


def test_passage_prefix_applied_to_corpus():
    e, fake = _embedder()
    e.embed(["chain of custody", "write blocker"])
    assert fake.seen == ["passage: chain of custody", "passage: write blocker"]


def test_query_prefix_applied_to_query():
    e, fake = _embedder()
    e.embed_one("how to seize a mobile phone")
    assert fake.seen == ["query: how to seize a mobile phone"]


def test_query_and_passage_use_different_prefixes():
    e, fake = _embedder()
    e.embed(["a passage"])
    e.embed_one("a query")
    assert "passage: a passage" in fake.seen
    assert "query: a query" in fake.seen
    assert "query: a passage" not in fake.seen


def test_dim_is_384():
    e, _ = _embedder()
    assert e.dim == 384
