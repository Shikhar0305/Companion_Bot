"""Answer-graph state (docs/03 §3.3).

A single dataclass threaded through the nodes. Each node reads and writes fields;
the audit logger serializes the whole object after the run.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from core.types import Answer, Citation, QueryAnalysis, RetrievedChunk


@dataclass
class GraphState:
    query: str
    user_role: str = "officer"
    kb_version: str = "kb_v1"

    # guardrail
    in_scope: bool = True
    refusal: Optional[str] = None

    # analysis
    analysis: Optional[QueryAnalysis] = None

    # retrieval / rerank
    retrieved: list[RetrievedChunk] = field(default_factory=list)
    reranked: list[RetrievedChunk] = field(default_factory=list)

    # generation
    draft_answer: Optional[str] = None
    model_used: Optional[str] = None

    # verification
    citations: list[Citation] = field(default_factory=list)
    verifier_report: dict = field(default_factory=dict)

    # outcome
    abstain: bool = False
    abstain_reason: Optional[str] = None
    confidence: str = "low"
    answer: Optional[Answer] = None
