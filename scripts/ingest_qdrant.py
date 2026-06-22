#!/usr/bin/env python3
"""Ingest the corpus into Qdrant (production vector store).

Reuses the standard ingestion path (discovery -> process -> sidecar enrich ->
embed/load) but forces the Qdrant store and disables the in-memory fallback, so
the run fails loudly if Qdrant is unreachable instead of silently loading into a
throwaway store. The collection is created automatically on first connect.

Usage:
    docker compose -f infra/docker-compose.qdrant.yml up -d
    EMBEDDER=bge python scripts/ingest_qdrant.py
    QDRANT_URL=http://localhost:6333 QDRANT_COLLECTION=kb python scripts/ingest_qdrant.py
"""
from __future__ import annotations

import os
import sys

from app.config import get_settings
from ingestion.discovery import DEFAULT_CORPUS_ROOT, discover_corpus
from ingestion.embed import embed_and_load
from ingestion.pipeline import process_markdown, process_pdf, validate
from ingestion.sidecar import enrich_chunks, load_sidecar_index
from rag.services import build_services


def main() -> int:
    settings = get_settings()
    root = os.environ.get("CORPUS_ROOT", DEFAULT_CORPUS_ROOT)

    sources, sidecar_paths = discover_corpus(root)
    if not sources:
        print(f"[ingest] no ingestible files found under {root!r}.")
        return 1
    index = load_sidecar_index(sidecar_paths)
    print(f"[discover] {len(sources)} sources, {len(sidecar_paths)} sidecar file(s) under {root!r}")

    all_chunks = []
    for src in sources:
        spec, fmt = src.spec, src.fmt
        try:
            chunks = process_markdown(spec) if fmt == "md" else process_pdf(spec)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! failed to process {spec.path}: {exc}")
            continue
        enrich_chunks(chunks, os.path.basename(spec.path), index)
        all_chunks.extend(chunks)
    print(f"[process] {len(all_chunks)} chunks")

    result = validate(all_chunks)
    print(f"[validate] ok={result.ok} stats={result.stats}")
    if not result.ok:
        for e in result.errors:
            print(f"  ERROR: {e}")
        print("[ingest] validation failed — not loading.")
        return 1

    # Force Qdrant; do NOT fall back to in-memory (we want a hard failure if down).
    services = build_services(
        embedder_name=settings.embedder,
        vector_store_name="qdrant",
        reranker_name=settings.reranker,
        llm_profile="stub",  # ingestion does not call the LLM
        vector_store_kwargs={
            "url": settings.qdrant_url,
            "collection": settings.qdrant_collection,
            "allow_fallback": False,
        },
    )
    loaded = embed_and_load(all_chunks, services.embedder, services.vector_store)
    total = services.vector_store.count()
    print(f"[load] embedded + upserted {loaded} chunks into Qdrant "
          f"collection {settings.qdrant_collection!r} (now {total} points)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
