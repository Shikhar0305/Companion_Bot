"""Dependency container assembled from settings and passed to every node.

Keeps the answer graph free of global state and makes each node unit-testable
with stub/in-memory backends.
"""
from __future__ import annotations

from dataclasses import dataclass

from rag.llm.router import LLMRouter, build_router
from rag.prompts import GROUNDED_ANSWER_VERSION, load_grounded_answer_prompt
from rag.retrieval.embeddings import Embedder, build_embedder
from rag.retrieval.reranker import Reranker, build_reranker
from rag.retrieval.vector_store import VectorStore, build_vector_store


@dataclass
class PipelineConfig:
    kb_version: str = "kb_v1"
    retrieve_k: int = 20
    rerank_top_n: int = 6
    relevance_floor: float = 0.15      # min normalized rerank score to keep a passage
    min_supporting: int = 1            # min passages required to attempt an answer
    # SOP conceptual-demotion weights (Phase 3): applied to SOP chunks on
    # operational queries only. conceptual (priority 1) scaled DOWN so operational
    # procedures surface above background. The operational boost defaults to 1.0
    # (off): boosting SOP operational chunks was measured to make them outrank the
    # purpose-built recovery/decision-tree repos on financial queries. Demotion
    # alone achieves operational-over-conceptual without breaking cross-repo routing.
    sop_conceptual_penalty: float = 0.5
    sop_operational_boost: float = 1.0


class Services:
    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        reranker: Reranker,
        router: LLMRouter,
        config: PipelineConfig,
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
        self.reranker = reranker
        self.router = router
        self.config = config
        self.system_prompt = load_grounded_answer_prompt()
        self.prompt_version = GROUNDED_ANSWER_VERSION


def build_services(
    *,
    embedder_name: str = "hash",
    vector_store_name: str = "memory",
    reranker_name: str = "noop",
    llm_profile: str = "stub",
    config: PipelineConfig | None = None,
    vector_store_kwargs: dict | None = None,
) -> Services:
    embedder = build_embedder(embedder_name)
    vector_store = build_vector_store(vector_store_name, embedder, **(vector_store_kwargs or {}))
    reranker = build_reranker(reranker_name)
    router = build_router(llm_profile)
    return Services(embedder, vector_store, reranker, router, config or PipelineConfig())
