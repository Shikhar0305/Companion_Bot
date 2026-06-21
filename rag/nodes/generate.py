"""Node 5 — grounded generation (docs/03 §3.3).

Builds the strict cite-or-abstain prompt with only the surviving passages and
calls the routed LLM. Output uses [n] markers verified downstream.
"""
from __future__ import annotations

from rag.services import Services
from rag.state import GraphState


def generate(state: GraphState, services: Services) -> GraphState:
    text, model = services.router.generate(
        query=state.query,
        passages=state.reranked,
        system_prompt=services.system_prompt,
    )
    state.draft_answer = text.strip()
    state.model_used = model
    return state
