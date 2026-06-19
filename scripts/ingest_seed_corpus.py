#!/usr/bin/env python3
"""Ingest the seed corpus (BNS, BNSS, IT Act, Cyber Crime SOP) into a KB version.

Usage:
    python scripts/ingest_seed_corpus.py            # process + validate + (optionally) load

Requires PyMuPDF for PDF extraction (and OCR deps for the scanned SOP). The
process/validate stages are pure stdlib; embedding+load uses the configured
embedder/vector store.
"""
from __future__ import annotations

import sys

from app.config import get_settings
from ingestion.embed import embed_and_load
from ingestion.pipeline import SourceSpec, process_pdf, validate
from rag.services import build_services

SEED = [
    SourceSpec("it_act_2000_updated.pdf", "itact2000",
               "Information Technology Act, 2000", "act",
               issuing_authority="Government of India", version="2000"),
    SourceSpec("BNS.pdf", "bns2023", "Bharatiya Nyaya Sanhita, 2023", "sanhita",
               issuing_authority="Government of India", version="2023"),
    SourceSpec("BNSS.pdf", "bnss2023", "Bharatiya Nagarik Suraksha Sanhita, 2023",
               "sanhita", issuing_authority="Government of India", version="2023"),
    SourceSpec("SOPCCHQ.pdf", "sopcchq", "Cyber Crime Investigation SOP", "sop",
               issuing_authority="CCHQ", version="2023"),
]


def main() -> int:
    settings = get_settings()
    all_chunks = []
    for spec in SEED:
        print(f"[ingest] {spec.path} ({spec.doc_type}) …")
        try:
            chunks = process_pdf(spec)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! failed to process {spec.path}: {exc}")
            continue
        print(f"  -> {len(chunks)} chunks")
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
