"""Self-hosted Ollama client for on-prem / air-gapped deployments (docs/05 §5.5).

Talks to a local Ollama server over its native chat API. Nothing leaves the
premises, and Ollama ships small instruct models (e.g. Qwen3) that run on a
single commodity GPU — a much lighter on-prem option than a 70B vLLM stack.

Uses only the standard library (urllib + json) so the module loads with no extra
dependency; the contract matches every other client, so the grounding verifier
(rag/nodes/verify) enforces citations regardless of which model answers.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

from core.types import RetrievedChunk
from rag.llm.base import format_sources

# Reasoning models (Qwen3) may emit a <think>...</think> block; strip it so only
# the grounded, citable answer reaches the verifier.
_THINK = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


class OllamaLLM:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        max_tokens: int = 1500,
        timeout: float = 120.0,
    ) -> None:
        self.model = model or os.environ.get("OLLAMA_MODEL", "qwen3:8b")
        self.name = self.model
        self.base_url = (base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.max_tokens = max_tokens
        self.timeout = timeout

    def _post(self, payload: dict) -> dict:
        """POST to the Ollama chat endpoint. Isolated for easy testing."""
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310 (trusted local URL)
            return json.loads(resp.read().decode("utf-8"))

    def generate(self, query: str, passages: list[RetrievedChunk], system_prompt: str) -> str:
        sources = format_sources(passages)
        valid_markers = ", ".join(f"[{i}]" for i in range(1, len(passages) + 1))
        user = (
            f"SOURCE PASSAGES:\n{sources}\n\nQUESTION: {query}\n\n"
            "Answer only from the SOURCE PASSAGES.\n\n"
            "Citation rules:\n"
            f"- Use only these exact citation markers: {valid_markers}.\n"
            "- Do not write placeholder or alternate markers such as [n], [n 1], "
            "[source 1], footnotes, or any marker not listed above.\n"
            "- Every answer sentence must end with one or more valid markers.\n"
            "- If you cannot answer using valid listed markers, reply exactly: "
            '"Information not found in approved knowledge sources."\n\n'
            "Output contract:\n"
            "- Do not acknowledge these instructions.\n"
            '- Do not say "Here", "Okay", "Sure", "Below", or similar setup text.\n'
            "- Start directly with the answer.\n"
            "- Your entire response must be either a cited answer or exactly: "
            '"Information not found in approved knowledge sources."'
        )
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,  # disable chain-of-thought for thinking models (Qwen3)
            "options": {"temperature": 0.0, "num_predict": self.max_tokens},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user},
            ],
        }
        resp = self._post(payload)
        content = (resp.get("message") or {}).get("content", "") or ""
        return _THINK.sub("", content).strip()
