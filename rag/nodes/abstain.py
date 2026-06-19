"""Abstain / assemble terminal nodes (docs/03 §3.3).

`abstain` builds the verbatim "Information not found…" answer.
`assemble` builds the final grounded Answer with citations, confidence, and the
mandatory disclaimer.
"""
from __future__ import annotations

from core.constants import ABSTENTION_MESSAGE, DISCLAIMER
from core.types import Answer
from rag.services import Services
from rag.state import GraphState


def abstain(state: GraphState, services: Services) -> GraphState:
    state.answer = Answer(
        text=ABSTENTION_MESSAGE,
        citations=[],
        confidence="low",
        abstained=True,
        kb_version=state.kb_version,
        disclaimer=DISCLAIMER,
    )
    return state


def refuse(state: GraphState, services: Services) -> GraphState:
    state.answer = Answer(
        text=state.refusal or "Out of scope.",
        citations=[],
        confidence="low",
        refused=True,
        kb_version=state.kb_version,
        disclaimer="",
    )
    return state


def assemble(state: GraphState, services: Services) -> GraphState:
    state.answer = Answer(
        text=state.draft_answer or "",
        citations=state.citations,
        confidence=state.confidence,
        abstained=False,
        kb_version=state.kb_version,
        disclaimer=DISCLAIMER,
    )
    return state
