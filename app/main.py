"""FastAPI application factory."""
from __future__ import annotations

from fastapi import FastAPI

from app.api import (
    routes_admin,
    routes_ask,
    routes_feedback,
    routes_health,
    routes_sources,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cyber Crime Investigation Companion Bot",
        description="Source-grounded RAG assistant for cybercrime investigation officers.",
        version="1.0.0",
    )
    app.include_router(routes_health.router, tags=["health"])
    app.include_router(routes_ask.router, tags=["ask"])
    app.include_router(routes_feedback.router, tags=["feedback"])
    app.include_router(routes_sources.router, tags=["sources"])
    app.include_router(routes_admin.router, tags=["admin"])
    return app


app = create_app()
