"""LLM client interface and a dependency-free stub for dev/tests.

All clients implement `generate(...)` returning answer text that uses `[n]`
markers referencing the numbered source passages. The verifier (rag/nodes/verify)
maps markers back to passages and enforces the grounding hard-gate, so the
contract is uniform across Claude, vLLM/Llama, and the stub.
"""
from __future__ import annotations

from typing import Protocol

from core.constants import ABSTENTION_MESSAGE
from core.types import RetrievedChunk


def format_sources(passages: list[RetrievedChunk]) -> str:
    """Render numbered SOURCE PASSAGES for the prompt."""
    lines = []
    for i, rc in enumerate(passages, start=1):
        c = rc.chunk
        loc = c.section_number or c.sop_section or c.procedure_name or ""
        head = f"[{i}] {c.title}"
        if loc:
            head += f" — {loc}"
        if c.page_start:
            head += f" (p.{c.page_start})"
        lines.append(f"{head}\n{c.text.strip()}")
    return "\n\n".join(lines)


class LLMClient(Protocol):
    name: str

    def generate(self, query: str, passages: list[RetrievedChunk], system_prompt: str) -> str: ...


class StubLLM:
    """Deterministic grounded generator for dev/tests.

    Produces a citable answer that quotes the top passage(s) and references their
    real section identifiers, so the grounding verifier passes legitimately.
    Abstains (verbatim message, no markers) when given no passages.
    """

    name = "stub"

    def generate(self, query: str, passages: list[RetrievedChunk], system_prompt: str) -> str:
        if not passages:
            return ABSTENTION_MESSAGE
        parts = []
        for i, rc in enumerate(passages[:2], start=1):
            c = rc.chunk
            snippet = " ".join(c.text.strip().split())
            snippet = snippet[:240] + ("…" if len(snippet) > 240 else "")
            ref = ""
            if c.section_number:
                ref = f"Section {c.section_number} of {c.title} states: "
            elif c.sop_section or c.procedure_name:
                ref = f"As per {c.title} ({c.sop_section or c.procedure_name}): "
            parts.append(f"{ref}{snippet} [{i}]")
        return " ".join(parts)
