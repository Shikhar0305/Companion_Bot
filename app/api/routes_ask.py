"""POST /ask — the grounded answer endpoint."""
from __future__ import annotations

import time

from fastapi import APIRouter, Header, HTTPException

from app.config import get_settings
from app.deps import get_audit_store, get_pipeline
from app.middleware.audit import build_audit_record
from app.middleware.auth import authenticate
from app.middleware.ratelimit import RateLimiter
from app.schemas import AskRequest, AskResponse, CitationModel
from core.audit import new_request_id
from rag.prompts import GROUNDED_ANSWER_VERSION

router = APIRouter()
_limiter = RateLimiter(get_settings().rate_limit_per_min)


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, authorization: str | None = Header(default=None)) -> AskResponse:
    principal = authenticate(authorization)
    if not _limiter.allow(principal.user):
        raise HTTPException(status_code=429, detail="rate limit exceeded")

    request_id = new_request_id()
    started = time.perf_counter()
    state = get_pipeline().run(req.query, user_role=req.user_role)
    latency_ms = (time.perf_counter() - started) * 1000.0

    record = build_audit_record(
        request_id=request_id, user=principal.user, state=state,
        prompt_version=GROUNDED_ANSWER_VERSION, latency_ms=latency_ms,
    )
    get_audit_store().write(record)

    ans = state.answer
    return AskResponse(
        request_id=request_id,
        answer=ans.text,
        citations=[CitationModel(**c.to_dict()) for c in ans.citations],
        confidence=ans.confidence,
        abstained=ans.abstained,
        refused=ans.refused,
        kb_version=ans.kb_version,
        disclaimer=ans.disclaimer,
        model=state.model_used,
        latency_ms=round(latency_ms, 2),
    )
