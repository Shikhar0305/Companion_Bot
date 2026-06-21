"""Dependency wiring for the API: build Services + audit store from Settings,
and load the approved corpus (data/corpus) at startup so the endpoint answers
from the real knowledge base. Falls back to a tiny demo KB only when no corpus
is present (so the service still boots with zero content on disk).
"""
from __future__ import annotations

import os
from functools import lru_cache

from app.config import Settings, get_settings
from core.audit import JsonlAuditStore
from ingestion.embed import embed_and_load
from ingestion.pipeline import SourceSpec, process_text
from rag.graph import AnswerPipeline
from rag.services import PipelineConfig, Services, build_services


def _build_services(settings: Settings) -> Services:
    config = PipelineConfig(
        kb_version=settings.kb_version,
        retrieve_k=settings.retrieve_k,
        rerank_top_n=settings.rerank_top_n,
        relevance_floor=settings.relevance_floor,
        min_supporting=settings.min_supporting,
    )
    return build_services(
        embedder_name=settings.embedder,
        vector_store_name=settings.vector_store,
        reranker_name=settings.reranker,
        llm_profile=settings.llm_profile,
        config=config,
        vector_store_kwargs={"url": settings.qdrant_url, "collection": settings.qdrant_collection},
    )


_DEMO_LEGAL = """Section 66C. Punishment for identity theft. Whoever, fraudulently
or dishonestly makes use of the electronic signature, password or any other
unique identification feature of any other person, shall be punished with
imprisonment of either description for a term which may extend to three years
and shall also be liable to fine.

Section 66D. Punishment for cheating by personation by using computer resource.
Whoever, by means of any communication device or computer resource cheats by
personation, shall be punished with imprisonment of either description for a
term which may extend to three years and shall also be liable to fine."""

_DEMO_SOP = """4.1 Preservation of Digital Evidence. On reaching the scene, do not
operate the suspect device. Isolate it from networks, photograph the screen,
and document the state. Maintain chain of custody from the point of seizure.

4.2 UPI Fraud Money Trail. Obtain the victim transaction reference, identify the
beneficiary VPA and bank, and issue a freeze request to the beneficiary bank
without delay. Record all transaction IDs for the money trail."""


def _seed_demo_kb(services: Services) -> None:
    """Seed a minimal demo KB for the dev (memory) profile only."""
    if services.vector_store.count() > 0:
        return
    chunks = process_text(_DEMO_LEGAL, SourceSpec(
        path="", doc_id="itact2000", title="Information Technology Act, 2000",
        doc_type="act", issuing_authority="Government of India", version="2000"))
    chunks += process_text(_DEMO_SOP, SourceSpec(
        path="", doc_id="sopcchq", title="Cyber Crime Investigation SOP",
        doc_type="sop", issuing_authority="CCHQ", version="2023"))
    embed_and_load(chunks, services.embedder, services.vector_store)


def _load_corpus(services: Services) -> int:
    """Ingest data/corpus into the store at startup. Returns #chunks loaded.

    Reuses the production ingestion path (discovery → process → sidecar enrich →
    embed/load), so the API answers from the same corpus that
    scripts/ingest_seed_corpus.py builds. Returns 0 when no corpus is present.
    """
    from ingestion.discovery import discover_corpus
    from ingestion.pipeline import process_markdown, process_pdf
    from ingestion.sidecar import enrich_chunks, load_sidecar_index

    root = os.environ.get("CORPUS_ROOT", "data/corpus")
    sources, sidecars = discover_corpus(root)
    if not sources:
        return 0
    index = load_sidecar_index(sidecars)
    all_chunks = []
    for src in sources:
        try:
            chunks = process_markdown(src.spec) if src.fmt == "md" else process_pdf(src.spec)
        except Exception:  # noqa: BLE001 - skip unreadable file, keep loading the rest
            continue
        enrich_chunks(chunks, os.path.basename(src.spec.path), index)
        all_chunks += chunks
    if not all_chunks:
        return 0
    return embed_and_load(all_chunks, services.embedder, services.vector_store)


@lru_cache(maxsize=1)
def get_services() -> Services:
    settings = get_settings()
    services = _build_services(settings)
    # Qdrant is populated out-of-band by scripts/ingest_seed_corpus.py; only the
    # in-memory profile loads the corpus at startup.
    if settings.vector_store == "memory" and services.vector_store.count() == 0:
        if _load_corpus(services) == 0:
            _seed_demo_kb(services)  # fallback only when no corpus on disk
    return services


@lru_cache(maxsize=1)
def get_pipeline() -> AnswerPipeline:
    return AnswerPipeline(get_services())


@lru_cache(maxsize=1)
def get_audit_store() -> JsonlAuditStore:
    return JsonlAuditStore(get_settings().audit_path)
