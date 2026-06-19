"""Self-hosted Llama 3.3 client for air-gapped deployments (docs/05 §5.5).

Talks to a local vLLM OpenAI-compatible endpoint. No data leaves premises.
The `openai` client is imported lazily.
"""
from __future__ import annotations

import os

from core.types import RetrievedChunk
from rag.llm.base import format_sources


class VLLMLlama:
    def __init__(
        self,
        model: str = "meta-llama/Llama-3.3-70B-Instruct",
        base_url: str | None = None,
        max_tokens: int = 1500,
    ) -> None:
        self.name = model
        self.model = model
        self.base_url = base_url or os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
        self.max_tokens = max_tokens
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from openai import OpenAI  # lazy

            self._client = OpenAI(base_url=self.base_url, api_key=os.environ.get("VLLM_API_KEY", "EMPTY"))
        return self._client

    def generate(self, query: str, passages: list[RetrievedChunk], system_prompt: str) -> str:
        client = self._ensure_client()
        sources = format_sources(passages)
        user = (
            f"SOURCE PASSAGES:\n{sources}\n\nQUESTION: {query}\n\n"
            "Answer only from the passages. Cite every statement with its [n] "
            'marker. If unsupported, reply exactly: "Information not found in '
            'approved knowledge sources."'
        )
        resp = client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""
