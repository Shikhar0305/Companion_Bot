"""GET /sources/{chunk_id} — return the full source chunk for verification."""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from app.deps import get_services
from app.middleware.auth import authenticate

router = APIRouter()


@router.get("/sources/{chunk_id}")
def get_source(chunk_id: str, authorization: str | None = Header(default=None)) -> dict:
    authenticate(authorization)
    chunk = get_services().vector_store.get(chunk_id)
    if chunk is None:
        raise HTTPException(status_code=404, detail="source not found")
    return chunk.to_dict()
