"""Cost-aware model routing (docs/05 §5.5, docs/08 §8.6).

Default: a cheap/fast model for routine queries, escalate to a stronger model for
complex or low-confidence ones. Profiles: stub | claude | vllm.
"""
from __future__ import annotations

from core.types import RetrievedChunk
from rag.llm.base import LLMClient, StubLLM


class LLMRouter:
    def __init__(self, default: LLMClient, escalation: LLMClient | None = None) -> None:
        self.default = default
        self.escalation = escalation or default

    def select(self, query: str, passages: list[RetrievedChunk]) -> LLMClient:
        # Escalate when retrieval is weak/ambiguous or the question is long/complex.
        weak_top = (passages[0].score < 0.55) if passages else True
        complex_q = len(query.split()) > 28 or query.count("?") > 1
        return self.escalation if (weak_top or complex_q) else self.default

    def generate(self, query: str, passages: list[RetrievedChunk], system_prompt: str) -> tuple[str, str]:
        client = self.select(query, passages)
        return client.generate(query, passages, system_prompt), client.name


def build_router(profile: str) -> LLMRouter:
    if profile == "claude":
        from rag.llm.claude import ClaudeLLM

        return LLMRouter(default=ClaudeLLM("claude-haiku-4-5"),
                         escalation=ClaudeLLM("claude-opus-4-8"))
    if profile == "vllm":
        from rag.llm.vllm_llama import VLLMLlama

        client = VLLMLlama()
        return LLMRouter(default=client, escalation=client)
    stub = StubLLM()
    return LLMRouter(default=stub, escalation=stub)
