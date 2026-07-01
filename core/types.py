"""Core data structures shared across the pipeline.

Implemented with stdlib dataclasses (no pydantic) so ingestion, retrieval, and
the answer graph stay importable without web/ML dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class Chunk:
    """A production-ready knowledge-base unit (see docs/04 §4.3)."""

    chunk_id: str
    doc_id: str
    doc_type: str
    title: str
    text: str
    issuing_authority: str = ""
    version: str = ""
    effective_date: str = ""
    language: str = "en"
    chapter: Optional[str] = None
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    sop_section: Optional[str] = None
    procedure_name: Optional[str] = None
    step_range: Optional[str] = None
    # SOP metadata enrichment (Phase 3). Populated for doc_type == "sop" only,
    # from heading-auto classification + sidecar overrides. priority drives the
    # query-aware conceptual-demotion weighting in rerank.
    section_type: Optional[str] = None
    topic: Optional[str] = None
    procedure_type: Optional[str] = None
    priority: Optional[int] = None
    keywords: list[str] = field(default_factory=list)
    capability_area: list[str] = field(default_factory=list)
    cybercrime_categories: list[str] = field(default_factory=list)
    jurisdiction: str = "IN"
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    parent_chunk_id: Optional[str] = None
    source_hash: str = ""
    # Sidecar-supplied payload (e.g. legal_metadata.yaml) for retrieval filtering.
    extra_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Chunk":
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**known)


@dataclass
class RetrievedChunk:
    """A chunk returned by retrieval/rerank, carrying its relevance score."""

    chunk: Chunk
    score: float
    source: str = "hybrid"  # dense | sparse | hybrid | rerank


@dataclass
class Citation:
    """A verifiable source locator attached to an answer."""

    marker: int               # the [n] marker used in the answer text
    chunk_id: str
    doc_id: str
    title: str
    doc_type: str
    section: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QueryAnalysis:
    """Output of the query-analysis node."""

    rewritten_query: str
    capability_area: str
    cybercrime_categories: list[str] = field(default_factory=list)
    expansions: list[str] = field(default_factory=list)
    doc_type_filter: list[str] = field(default_factory=list)


@dataclass
class Answer:
    """The final, source-grounded response returned to the officer."""

    text: str
    citations: list[Citation] = field(default_factory=list)
    confidence: str = "low"           # high | medium | low
    abstained: bool = False
    refused: bool = False
    kb_version: str = ""
    disclaimer: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["citations"] = [c.to_dict() for c in self.citations]
        return d
