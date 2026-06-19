"""Cross-encoder reranking + relevance gate (docs/03 §3.3 node 4).

`PassthroughReranker` (dev/tests) keeps retrieval order but normalizes scores to
[0,1].  `BGEReranker` is the production cross-encoder (BAAI/bge-reranker-v2),
imported lazily.
"""
from __future__ import annotations

import re
from typing import Protocol

from core.types import RetrievedChunk

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are",
    "what", "which", "how", "do", "i", "under", "by", "with", "at", "be", "as",
    "this", "that", "it", "should", "can", "my", "me", "we", "you", "about",
}


class Reranker(Protocol):
    def rerank(self, query: str, candidates: list[RetrievedChunk], top_n: int) -> list[RetrievedChunk]: ...


def _content_tokens(text: str) -> set[str]:
    return {t for t in _TOKEN.findall(text.lower()) if t not in _STOP}


class PassthroughReranker:
    """Dev/test reranker scoring by ABSOLUTE query-term coverage.

    score = fraction of the query's content tokens that appear in the passage.
    Unlike min-max normalization (which always forces the top score to 1.0), this
    yields a low score for genuinely irrelevant passages, so the relevance floor
    correctly filters out-of-corpus queries. The production BGEReranker gives a
    real absolute cross-encoder score with the same property.
    """

    def rerank(self, query: str, candidates: list[RetrievedChunk], top_n: int) -> list[RetrievedChunk]:
        q = _content_tokens(query)
        scored: list[RetrievedChunk] = []
        for c in candidates:
            if q:
                passage = _content_tokens(c.chunk.text)
                coverage = len(q & passage) / len(q)
            else:
                coverage = c.score
            scored.append(RetrievedChunk(c.chunk, coverage, "rerank"))
        return sorted(scored, key=lambda c: c.score, reverse=True)[:top_n]


class BGEReranker:
    """Production cross-encoder reranker. Heavy deps imported lazily."""

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3") -> None:
        from FlagEmbedding import FlagReranker  # lazy

        self._model = FlagReranker(model_name, use_fp16=True)

    def rerank(self, query: str, candidates: list[RetrievedChunk], top_n: int) -> list[RetrievedChunk]:
        if not candidates:
            return []
        pairs = [[query, c.chunk.text] for c in candidates]
        scores = self._model.compute_score(pairs, normalize=True)
        if not isinstance(scores, list):
            scores = [scores]
        scored = [RetrievedChunk(c.chunk, float(s), "rerank") for c, s in zip(candidates, scores)]
        return sorted(scored, key=lambda c: c.score, reverse=True)[:top_n]


def build_reranker(name: str) -> Reranker:
    if name == "bge":
        return BGEReranker()
    return PassthroughReranker()
