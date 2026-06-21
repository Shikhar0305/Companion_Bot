#!/usr/bin/env python3
"""Ingest the corpus into a KB version via auto-discovery (docs/04 §4.2).

Walks ``data/corpus/`` recursively — no hardcoded file list. Markdown is chunked
structurally, PDFs go through the existing PyMuPDF/OCR path (backward compatible),
and ``legal_metadata.yaml`` is attached to chunks as sidecar metadata (never
chunked). The process/validate stages are pure stdlib; embedding+load uses the
configured embedder/vector store.

Usage:
    python scripts/ingest_seed_corpus.py            # discover + validate + load
    CORPUS_ROOT=data/corpus python scripts/ingest_seed_corpus.py
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
        print(f"[ingest] {spec.path} ({spec.doc_type}, {fmt}) …")
        try:
            chunks = process_markdown(spec) if fmt == "md" else process_pdf(spec)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! failed to process {spec.path}: {exc}")
            continue
        n_meta = enrich_chunks(chunks, os.path.basename(spec.path), index)
        print(f"  -> {len(chunks)} chunks ({n_meta} enriched from sidecar)")
        all_chunks.extend(chunks)

    result = validate(all_chunks)
    print(f"[validate] ok={result.ok} stats={result.stats}")
    for e in result.errors:
        print(f"  ERROR: {e}")
    for w in result.warnings[:10]:
        print(f"  warn: {w}")
    if not result.ok:
        print("[ingest] validation failed — not loading.")
        return 1

    services = build_services(
        embedder_name=settings.embedder,
        vector_store_name=settings.vector_store,
        reranker_name=settings.reranker,
        llm_profile=settings.llm_profile,
        vector_store_kwargs={"url": settings.qdrant_url, "collection": settings.qdrant_collection},
    )
    loaded = embed_and_load(all_chunks, services.embedder, services.vector_store)
    print(f"[load] embedded + loaded {loaded} chunks into {settings.vector_store}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
