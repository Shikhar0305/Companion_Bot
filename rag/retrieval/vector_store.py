"""Vector stores.

`InMemoryVectorStore` runs hybrid retrieval (dense cosine + lexical overlap fused
with RRF) with zero external services — used for dev/tests and as the reference
implementation.  `QdrantVectorStore` is the production store (docs/05 §5.3),
imported lazily.  Both honour metadata filters.
"""
from __future__ import annotations

import math
import re
from typing import Optional, Protocol

from core.types import Chunk, RetrievedChunk
from rag.retrieval.embeddings import Embedder
from rag.retrieval.fusion import reciprocal_rank_fusion

_TOKEN = re.compile(r"[a-z0-9]+")


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def _matches_filter(chunk: Chunk, filters: Optional[dict]) -> bool:
    if not filters:
        return True
    for key, allowed in filters.items():
        value = getattr(chunk, key, None)
        if allowed is None:
            continue
        allowed_set = set(allowed) if isinstance(allowed, (list, tuple, set)) else {allowed}
        if isinstance(value, list):
            if not (set(value) & allowed_set):
                return False
        else:
            if value not in allowed_set:
                return False
    return True


class VectorStore(Protocol):
    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...

    def search(
        self, query_text: str, query_vector: list[float], k: int = 20,
        filters: Optional[dict] = None,
    ) -> list[RetrievedChunk]: ...

    def get(self, chunk_id: str) -> Optional[Chunk]: ...

    def count(self) -> int: ...


class InMemoryVectorStore:
    """Hybrid in-memory store (dense + lexical, fused with RRF)."""

    def __init__(self) -> None:
        self._chunks: dict[str, Chunk] = {}
        self._vectors: dict[str, list[float]] = {}
        self._tokens: dict[str, set[str]] = {}

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        for chunk, vec in zip(chunks, vectors):
            self._chunks[chunk.chunk_id] = chunk
            self._vectors[chunk.chunk_id] = vec
            self._tokens[chunk.chunk_id] = set(_TOKEN.findall(chunk.text.lower()))

    def get(self, chunk_id: str) -> Optional[Chunk]:
        return self._chunks.get(chunk_id)

    def count(self) -> int:
        return len(self._chunks)

    def search(
        self, query_text: str, query_vector: list[float], k: int = 20,
        filters: Optional[dict] = None,
    ) -> list[RetrievedChunk]:
        candidates = [c for c in self._chunks.values() if _matches_filter(c, filters)]
        if not candidates:
            return []
        q_tokens = set(_TOKEN.findall(query_text.lower()))

        dense_ranked = sorted(
            candidates,
            key=lambda c: _cosine(query_vector, self._vectors[c.chunk_id]),
            reverse=True,
        )
        sparse_ranked = sorted(
            candidates,
            key=lambda c: len(q_tokens & self._tokens[c.chunk_id]),
            reverse=True,
        )
        fused = reciprocal_rank_fusion(
            [[c.chunk_id for c in dense_ranked], [c.chunk_id for c in sparse_ranked]]
        )
        ordered = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:k]
        return [RetrievedChunk(chunk=self._chunks[cid], score=score, source="hybrid")
                for cid, score in ordered]


class QdrantVectorStore:
    """Production store backed by Qdrant. Heavy deps imported lazily."""

    def __init__(self, url: str, collection: str, embedder: Embedder) -> None:
        from qdrant_client import QdrantClient  # lazy

        self._client = QdrantClient(url=url)
        self._collection = collection
        self._embedder = embedder

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        from qdrant_client.models import PointStruct  # lazy

        points = [
            PointStruct(id=i, vector=vec, payload=chunk.to_dict())
            for i, (chunk, vec) in enumerate(zip(chunks, vectors))
        ]
        self._client.upsert(collection_name=self._collection, points=points)

    def get(self, chunk_id: str) -> Optional[Chunk]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue  # lazy

        res = self._client.scroll(
            collection_name=self._collection,
            scroll_filter=Filter(must=[FieldCondition(key="chunk_id", match=MatchValue(value=chunk_id))]),
            limit=1,
        )
        points = res[0]
        return Chunk.from_dict(points[0].payload) if points else None

    def count(self) -> int:
        return self._client.count(collection_name=self._collection).count

    def search(
        self, query_text: str, query_vector: list[float], k: int = 20,
        filters: Optional[dict] = None,
    ) -> list[RetrievedChunk]:
        qfilter = self._build_filter(filters)
        hits = self._client.search(
            collection_name=self._collection, query_vector=query_vector,
            limit=k, query_filter=qfilter,
        )
        return [RetrievedChunk(chunk=Chunk.from_dict(h.payload), score=float(h.score))
                for h in hits]

    @staticmethod
    def _build_filter(filters: Optional[dict]):
        if not filters:
            return None
        from qdrant_client.models import Filter, FieldCondition, MatchAny  # lazy

        must = []
        for key, allowed in filters.items():
            if allowed is None:
                continue
            values = list(allowed) if isinstance(allowed, (list, tuple, set)) else [allowed]
            must.append(FieldCondition(key=key, match=MatchAny(any=values)))
        return Filter(must=must) if must else None


def build_vector_store(name: str, embedder: Embedder, **kw):
    if name == "qdrant":
        return QdrantVectorStore(
            url=kw.get("url", "http://localhost:6333"),
            collection=kw.get("collection", "kb"),
            embedder=embedder,
        )
    return InMemoryVectorStore()
