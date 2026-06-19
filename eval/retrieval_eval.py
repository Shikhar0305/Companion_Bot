"""Retrieval metrics: recall@k and MRR (docs/03 §3.6)."""
from __future__ import annotations

from dataclasses import dataclass

from eval.datasets import GOLDEN, GoldenCase
from rag.services import Services


@dataclass
class RetrievalMetrics:
    recall_at_k: float
    mrr: float
    k: int
    n: int


def evaluate_retrieval(services: Services, cases: list[GoldenCase] | None = None,
                       k: int = 10) -> RetrievalMetrics:
    cases = cases or GOLDEN
    hits = 0
    rr_sum = 0.0
    for case in cases:
        qvec = services.embedder.embed_one(case.query)
        results = services.vector_store.search(case.query, qvec, k=k)
        ids = [r.chunk.chunk_id for r in results]
        rank = next((i for i, cid in enumerate(ids, start=1)
                     if cid in case.expected_chunk_ids), None)
        if rank:
            hits += 1
            rr_sum += 1.0 / rank
    n = len(cases) or 1
    return RetrievalMetrics(recall_at_k=hits / n, mrr=rr_sum / n, k=k, n=len(cases))
