"""API request/response models (Pydantic v2). Imported only when serving."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    user_role: str = Field("officer", pattern="^(officer|analyst|supervisor|admin)$")


class CitationModel(BaseModel):
    marker: int
    chunk_id: str
    doc_id: str
    title: str
    doc_type: str
    section: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None


class AskResponse(BaseModel):
    request_id: str
    answer: str
    citations: list[CitationModel]
    confidence: str
    abstained: bool
    refused: bool
    kb_version: str
    disclaimer: str
    model: Optional[str] = None
    latency_ms: float


class FeedbackRequest(BaseModel):
    request_id: str
    helpful: bool
    note: Optional[str] = Field(None, max_length=2000)


class HealthResponse(BaseModel):
    status: str
    kb_version: str
    chunks_loaded: int
    llm_profile: str
