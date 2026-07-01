"""Build-time extraction of the authoritative SOP into a page-tagged text file.

The SOP (SOPCCHQ.pdf) is the backbone of the knowledge base. Rather than parse
25 MB of PDF on every API boot (and force PyMuPDF as a *runtime* dependency),
we extract it **once** here into a reviewable, version-controlled text artifact
under ``data/corpus/sop_repository/``. The artifact keeps the ``[[PAGE n]]``
markers so the chunker can recover page numbers for citations, and the original
numbered headings so ``chunk_sop`` can split on section boundaries.

This is a build-time step (online/offline both fine — it only touches the
public SOP, never case data). Run it whenever the source SOP changes:

    python scripts/extract_sop.py
"""
from __future__ import annotations

import os
import sys

from ingestion.clean import strip_repeated_lines
from ingestion.extract import extract_pdf, pages_to_text

SOURCE_PDF = os.environ.get("SOP_PDF", "SOPCCHQ.pdf")
OUT_PATH = os.environ.get(
    "SOP_OUT", "data/corpus/sop_repository/SOPCCHQ.sop.txt"
)


def build(source_pdf: str = SOURCE_PDF, out_path: str = OUT_PATH) -> int:
    if not os.path.isfile(source_pdf):
        print(f"[extract_sop] source PDF not found: {source_pdf}", file=sys.stderr)
        return 1
    print(f"[extract_sop] extracting {source_pdf} ...")
    pages = extract_pdf(source_pdf)  # native text layer; OCR only if needed
    deboiled = strip_repeated_lines([p.text for p in pages])
    for p, t in zip(pages, deboiled):
        p.text = t
    raw = pages_to_text(pages)  # interleaves [[PAGE n]] markers
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(raw)
    print(
        f"[extract_sop] wrote {out_path}  "
        f"({len(pages)} pages, {len(raw):,} chars)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
