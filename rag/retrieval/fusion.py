"""Reciprocal Rank Fusion for hybrid (dense + sparse) retrieval.

docs/03-rag-architecture.md §3.3 node 3.
"""
from __future__ import annotations

from typing import Iterable


def reciprocal_rank_fusion(
    ranked_lists: Iterable[list[str]], k: int = 60
) -> dict[str, float]:
    """Fuse multiple ranked ID lists into a single score map.

    score(d) = sum over lists of 1 / (k + rank(d)), rank starting at 1.
    Higher is better. Robust to differing score scales across retrievers.
    """
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return scores


def fuse_and_order(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """Return doc IDs ordered by fused RRF score (descending)."""
    scores = reciprocal_rank_fusion(ranked_lists, k=k)
    return [doc_id for doc_id, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
