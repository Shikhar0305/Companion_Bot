"""Embedding models.

`HashingEmbedder` is a dependency-free, deterministic bag-of-words hashing
embedder used for dev/tests — it gives lexical-similarity vectors good enough to
exercise the full pipeline without a GPU.  `BGEM3Embedder` is the production
model (multilingual dense+sparse, docs/05 §5.4); it is imported lazily.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_one(self, text: str) -> list[float]: ...


class HashingEmbedder:
    """Deterministic, no-dependency embedder for dev and tests."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in _tokenize(text):
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def embed_one(self, text: str) -> list[float]:
        return self._vector(text)


class BGEM3Embedder:
    """Production embedder (BAAI/bge-m3). Heavy deps imported lazily."""

    def __init__(self, model_name: str = "BAAI/bge-m3", device: str | None = None) -> None:
        from FlagEmbedding import BGEM3FlagModel  # lazy

        self._model = BGEM3FlagModel(model_name, use_fp16=True, device=device)
        self.dim = 1024

    def embed(self, texts: list[str]) -> list[list[float]]:
        out = self._model.encode(texts, return_dense=True, return_sparse=False)
        return [list(map(float, v)) for v in out["dense_vecs"]]

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]

    def embed_sparse(self, texts: list[str]) -> list[dict[int, float]]:
        out = self._model.encode(texts, return_dense=False, return_sparse=True)
        return out["lexical_weights"]


class E5SmallEmbedder:
    """``intfloat/multilingual-e5-small`` (384-d) — the mobile-target embedder.

    E5 is an **asymmetric** retriever: corpus passages must be encoded as
    ``"passage: " + text`` and queries as ``"query: " + text``. Omitting the
    prefixes silently collapses retrieval quality, so they are applied **here**,
    not by callers — the protocol mapping used across the codebase is:

    * ``embed()``     → corpus passages (``ingestion.embed.embed_and_load``)
    * ``embed_one()`` → a single query (``rag.nodes.retrieve``)

    Embeddings are L2-normalized (E5 expects cosine over unit vectors). Heavy
    deps (sentence-transformers / torch) are imported lazily so the dev profile
    and tests load without them.
    """

    QUERY_PREFIX = "query: "
    PASSAGE_PREFIX = "passage: "

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        import os

        from sentence_transformers import SentenceTransformer  # lazy

        name = model_name or os.environ.get("E5_MODEL", "intfloat/multilingual-e5-small")
        self._model = SentenceTransformer(name, device=device)
        self.dim = 384

    def _encode(self, texts: list[str]) -> list[list[float]]:
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, v)) for v in vecs]

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Encode corpus passages (applies the ``passage:`` prefix)."""
        return self._encode([self.PASSAGE_PREFIX + t for t in texts])

    def embed_one(self, text: str) -> list[float]:
        """Encode a single query (applies the ``query:`` prefix)."""
        return self._encode([self.QUERY_PREFIX + text])[0]


def build_embedder(name: str) -> Embedder:
    if name == "e5":
        return E5SmallEmbedder()
    if name == "bge":
        return BGEM3Embedder()
    return HashingEmbedder()
