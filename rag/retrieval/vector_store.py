"""Vector stores.

`InMemoryVectorStore` runs hybrid retrieval (dense cosine + lexical overlap fused
with RRF) with zero external services — used for dev/tests and as the reference
implementation.  `QdrantVectorStore` is the production store (docs/05 §5.3),
imported lazily.  Both honour metadata filters.
"""
from __future__ import annotations

import math
import os
import re
import uuid
from typing import Optional, Protocol

from core.types import Chunk, RetrievedChunk
from rag.retrieval.bm25 import BM25Index
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
    """Hybrid in-memory store: dense cosine + a lexical channel, fused with RRF.

    The lexical channel is selectable via ``HYBRID_SPARSE``:
    * ``overlap`` (default) — query-term overlap count (the original behaviour);
    * ``bm25`` — Okapi BM25 (IDF-weighted), which retrieves rare distinctive
      terms the dense channel misses. BM25's benefit requires a *semantic* dense
      channel (e5) to agree with it; under the hashing dev embedder the noisy
      dense channel dilutes it in RRF, so it is off by default until validated
      on e5.
    """

    def __init__(self) -> None:
        self._chunks: dict[str, Chunk] = {}
        self._vectors: dict[str, list[float]] = {}
        self._tokens: dict[str, set[str]] = {}
        self._bm25 = BM25Index()
        self._sparse_mode = os.environ.get("HYBRID_SPARSE", "overlap").lower()

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        for chunk, vec in zip(chunks, vectors):
            self._chunks[chunk.chunk_id] = chunk
            self._vectors[chunk.chunk_id] = vec
            self._tokens[chunk.chunk_id] = set(_TOKEN.findall(chunk.text.lower()))
            self._bm25.add(chunk.chunk_id, chunk.text, chunk.keywords)

    def get(self, chunk_id: str) -> Optional[Chunk]:
        return self._chunks.get(chunk_id)

    def count(self) -> int:
        return len(self._chunks)

    def by_section(self, refs: set[str], doc_types: set[str]) -> list[Chunk]:
        """Exact section-number lookup (legal fast-path). Returns matching chunks
        whose section_number is one of ``refs`` and doc_type is in ``doc_types``."""
        refs = {r.lower() for r in refs}
        return [
            c for c in self._chunks.values()
            if c.section_number and c.section_number.lower() in refs
            and c.doc_type in doc_types
        ]

    def search(
        self, query_text: str, query_vector: list[float], k: int = 20,
        filters: Optional[dict] = None,
    ) -> list[RetrievedChunk]:
        candidates = [c for c in self._chunks.values() if _matches_filter(c, filters)]
        if not candidates:
            return []
        cand_ids = [c.chunk_id for c in candidates]

        dense_ranked = sorted(
            cand_ids,
            key=lambda cid: _cosine(query_vector, self._vectors[cid]),
            reverse=True,
        )
        if self._sparse_mode == "bm25":
            bm25_scores = self._bm25.score(query_text, cand_ids)
            sparse_ranked = sorted(
                cand_ids, key=lambda cid: bm25_scores.get(cid, 0.0), reverse=True
            )
        else:  # overlap (default)
            q_tokens = set(_TOKEN.findall(query_text.lower()))
            sparse_ranked = sorted(
                cand_ids, key=lambda cid: len(q_tokens & self._tokens[cid]), reverse=True
            )
        fused = reciprocal_rank_fusion([dense_ranked, sparse_ranked])
        ordered = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:k]
        return [RetrievedChunk(chunk=self._chunks[cid], score=score, source="hybrid")
                for cid, score in ordered]


class QdrantVectorStore:
    """Production store backed by Qdrant. Heavy deps imported lazily.

    Creates the collection automatically (vector size from the embedder, cosine
    distance) and stores each chunk's full metadata as the point payload. Point
    ids are deterministic UUIDs derived from chunk_id, so re-ingestion upserts in
    place (idempotent) instead of duplicating.
    """

    # Stable namespace so the same chunk_id always maps to the same point id.
    _NS = uuid.UUID("6f9619ff-8b86-d011-b42d-00cf4fc964ff")
    # Payload fields worth indexing for fast metadata filtering.
    _INDEX_FIELDS = ("doc_type", "doc_id", "capability_area", "cybercrime_categories")

    def __init__(self, url: str, collection: str, embedder: Embedder) -> None:
        from qdrant_client import QdrantClient  # lazy

        # ":memory:" runs an embedded Qdrant (no server) — used by tests.
        if url == ":memory:":
            self._client = QdrantClient(location=":memory:")
        else:
            self._client = QdrantClient(url=url)
        self._collection = collection
        self._embedder = embedder
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        from qdrant_client.models import Distance, VectorParams  # lazy

        existing = {c.name for c in self._client.get_collections().collections}
        if self._collection in existing:
            return
        self._client.create_collection(
            collection_name=self._collection,
            vectors_config=VectorParams(size=self._embedder.dim, distance=Distance.COSINE),
        )
        for field in self._INDEX_FIELDS:
            try:
                self._client.create_payload_index(
                    collection_name=self._collection, field_name=field, field_schema="keyword",
                )
            except Exception:  # noqa: BLE001 - index is an optimisation, not required
                pass

    def _point_id(self, chunk_id: str) -> str:
        return str(uuid.uuid5(self._NS, chunk_id))

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        from qdrant_client.models import PointStruct  # lazy

        points = [
            PointStruct(id=self._point_id(chunk.chunk_id), vector=vec, payload=chunk.to_dict())
            for chunk, vec in zip(chunks, vectors)
        ]
        if points:
            self._client.upsert(collection_name=self._collection, points=points)

    def get(self, chunk_id: str) -> Optional[Chunk]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue  # lazy

        res = self._client.scroll(
            collection_name=self._collection,
            scroll_filter=Filter(must=[FieldCondition(key="chunk_id", match=MatchValue(value=chunk_id))]),
            limit=1,
            with_payload=True,
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
        # query_points is the current API; fall back to search on older clients.
        if hasattr(self._client, "query_points"):
            res = self._client.query_points(
                collection_name=self._collection, query=query_vector,
                limit=k, query_filter=qfilter, with_payload=True,
            )
            hits = res.points
        else:  # pragma: no cover - legacy client path
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
    """Build a vector store. Qdrant falls back to in-memory when unavailable
    (missing client or unreachable server) unless allow_fallback=False."""
    if name == "qdrant":
        allow_fallback = kw.get("allow_fallback", True)
        try:
            return QdrantVectorStore(
                url=kw.get("url", "http://localhost:6333"),
                collection=kw.get("collection", "kb"),
                embedder=embedder,
            )
        except Exception as exc:  # noqa: BLE001 - connection/import failure
            if not allow_fallback:
                raise
            print(f"[vector_store] Qdrant unavailable ({exc}); falling back to in-memory.")
            return InMemoryVectorStore()
    return InMemoryVectorStore()
