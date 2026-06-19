"""Claude LLM client (docs/05 §5.5).

Default model: Claude Opus 4.8 (best grounding). Budget tier: Claude Haiku 4.5.
Uses adaptive thinking off (low effort) for fast, grounded, deterministic-style
extraction over already-retrieved passages. The anthropic SDK is imported lazily
so this module loads without the dependency installed.
"""
from __future__ import annotations

import os

from core.types import RetrievedChunk
from rag.llm.base import format_sources


class ClaudeLLM:
    def __init__(self, model: str = "claude-opus-4-8", max_tokens: int = 1500) -> None:
        self.name = model
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            import anthropic  # lazy

            self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        return self._client

    def generate(self, query: str, passages: list[RetrievedChunk], system_prompt: str) -> str:
        client = self._ensure_client()
        sources = format_sources(passages)
        user = (
            f"SOURCE PASSAGES:\n{sources}\n\n"
            f"QUESTION: {query}\n\n"
            "Answer using only the passages above. Cite every factual or legal "
            "statement with the matching [n] marker. If the passages do not "
            'contain the answer, reply exactly: "Information not found in '
            'approved knowledge sources."'
        )
        # Low effort + adaptive thinking: fast, grounded extraction.
        resp = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
            thinking={"type": "adaptive"},
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
