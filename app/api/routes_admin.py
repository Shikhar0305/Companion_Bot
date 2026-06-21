"""Admin endpoints (RBAC: admin) — ingestion trigger (docs/02 §2.1)."""
from __future__ import annotations

from fastapi import APIRouter, Header

from app.middleware.auth import authenticate, require_role

router = APIRouter()


@router.post("/admin/ingest")
def trigger_ingest(authorization: str | None = Header(default=None)) -> dict:
    principal = authenticate(authorization)
    require_role(principal, "admin")
    # Production: enqueue an async ingestion job (Celery/arq) that runs the
    # pipeline, validates, and promotes a new KB version. Returns a job id.
    return {"status": "queued", "detail": "ingestion job enqueued"}
