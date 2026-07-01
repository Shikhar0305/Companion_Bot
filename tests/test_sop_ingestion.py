"""The SOP (SOPCCHQ) is the backbone of the KB — guard its ingestion.

Verifies the pre-extracted, page-tagged SOP artifact is discovered as a ``sop``
source and chunks cleanly: every chunk page-numbered, ids unique, validation
clean, and authoritative content present. Pure stdlib — no PyMuPDF needed.
"""
from __future__ import annotations

import os
from collections import Counter

import pytest

from ingestion.discovery import discover_corpus
from ingestion.pipeline import process_textfile, validate

ARTIFACT = "data/corpus/sop_repository/SOPCCHQ.sop.txt"

pytestmark = pytest.mark.skipif(
    not os.path.isfile(ARTIFACT), reason="SOP artifact not present (run scripts/extract_sop.py)"
)


def _sop_source():
    sources, _ = discover_corpus("data/corpus")
    sop = [s for s in sources if s.spec.doc_type == "sop"]
    assert sop, "SOP source not discovered under data/corpus/sop_repository"
    return sop[0]


def test_sop_discovered_as_text_sop():
    src = _sop_source()
    assert src.fmt == "text"            # ingested via the no-PyMuPDF text path
    assert src.spec.doc_type == "sop"


def test_sop_chunks_are_clean_and_page_numbered():
    chunks = process_textfile(_sop_source().spec)
    assert len(chunks) > 1000           # 812-page manual → hundreds+ of sections

    # Every chunk carries a page number (citations need it).
    assert all(c.page_start for c in chunks)

    # No Table-of-Contents / heading-only fragments survived.
    assert not [c for c in chunks if len(c.text.strip()) < 120]

    # No giant unsplit chunks.
    assert max(len(c.text) for c in chunks) <= 4200

    # chunk_ids are unique (TOC duplicates and recap collisions resolved).
    dups = {k: n for k, n in Counter(c.chunk_id for c in chunks).items() if n > 1}
    assert not dups, f"duplicate chunk ids: {list(dups)[:5]}"


def test_sop_validates_and_has_authoritative_content():
    chunks = process_textfile(_sop_source().spec)
    result = validate(chunks)
    assert result.ok, f"validation errors: {result.errors[:5]}"

    corpus = " ".join(c.text.lower() for c in chunks)
    # Hallmark content that must come from the real SOP, not the demo stub.
    for needle in ("chain of custody", "bharatiya sakshya", "first responder"):
        assert needle in corpus, f"expected SOP content missing: {needle!r}"
