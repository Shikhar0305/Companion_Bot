"""Runtime settings (env-driven). Plain dataclass — no pydantic dependency.

Defaults select the dependency-free dev profile (stub LLM, in-memory store,
hashing embedder) so the service boots without external infrastructure.
Production sets PROFILE-style env vars to wire Qdrant / BGE / Claude or Llama.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _b(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes")


@dataclass
class Settings:
    # Backends: hash|bge, memory|qdrant, noop|bge, stub|claude|vllm|ollama
    embedder: str = os.environ.get("EMBEDDER", "hash")
    vector_store: str = os.environ.get("VECTOR_STORE", "memory")
    reranker: str = os.environ.get("RERANKER", "noop")
    llm_profile: str = os.environ.get("LLM_PROFILE", "stub")

    qdrant_url: str = os.environ.get("QDRANT_URL", "http://localhost:6333")
    qdrant_collection: str = os.environ.get("QDRANT_COLLECTION", "kb")

    # Ollama (on-prem) — used when LLM_PROFILE=ollama.
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.environ.get("OLLAMA_MODEL", "qwen3:8b")

    kb_version: str = os.environ.get("KB_VERSION", "kb_v1")
    retrieve_k: int = int(os.environ.get("RETRIEVE_K", "20"))
    rerank_top_n: int = int(os.environ.get("RERANK_TOP_N", "6"))
    relevance_floor: float = float(os.environ.get("RELEVANCE_FLOOR", "0.15"))
    min_supporting: int = int(os.environ.get("MIN_SUPPORTING", "1"))

    auth_enabled: bool = _b("AUTH_ENABLED", False)
    rate_limit_per_min: int = int(os.environ.get("RATE_LIMIT_PER_MIN", "60"))
    audit_path: str = os.environ.get("AUDIT_PATH", "data/audit/audit.jsonl")


def get_settings() -> Settings:
    return Settings()
