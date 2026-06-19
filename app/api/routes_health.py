"""GET /health and /ready."""
from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.deps import get_services
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    services = get_services()
    return HealthResponse(
        status="ok",
        kb_version=settings.kb_version,
        chunks_loaded=services.vector_store.count(),
        llm_profile=settings.llm_profile,
    )


@router.get("/ready")
def ready() -> dict:
    services = get_services()
    return {"ready": services.vector_store.count() > 0}
