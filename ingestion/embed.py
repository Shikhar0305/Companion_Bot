"""Embed + load chunks into a vector store (docs/04 §4.2 stage 6/8).

Kept separate from the pure-stdlib pipeline so embedding/vector-store deps are
only pulled in when actually loading a KB version.
"""
from __future__ import annotations

from core.types import Chunk
from rag.retrieval.embeddings import Embedder
from rag.retrieval.vector_store import VectorStore


def embed_and_load(chunks: list[Chunk], embedder: Embedder, store: VectorStore,
                   batch_size: int = 64) -> int:
    """Embed chunk text in batches and upsert into the store. Returns count."""
    loaded = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        vectors = embedder.embed([c.text for c in batch])
        store.upsert(batch, vectors)
        loaded += len(batch)
    return loaded
