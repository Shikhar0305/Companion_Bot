"""Orchestrates the 5-stage ingestion pipeline (docs/04 §4.2).

extract → clean → chunk → tag metadata → validate → (embed + load done by the
caller via Services, so this module stays free of ML deps).
"""
from __future__ import annotations

from dataclasses import dataclass

from core.types import Chunk
from ingestion.chunk import chunk_document
from ingestion.clean import clean_text
from ingestion.metadata import tag_chunk
from ingestion.validate import ValidationResult, validate_chunks


@dataclass
class SourceSpec:
    path: str
    doc_id: str
    title: str
    doc_type: str
    issuing_authority: str = ""
    version: str = ""
    effective_date: str = ""
    language: str = "en"


def process_text(raw_text: str, spec: SourceSpec, *, is_markdown: bool = False) -> list[Chunk]:
    """Run clean → chunk → tag on already-extracted text. Pure stdlib."""
    cleaned = clean_text(raw_text)
    chunks = chunk_document(cleaned, spec.doc_id, spec.title, spec.doc_type,
                            is_markdown=is_markdown)
    return [
        tag_chunk(
            c, issuing_authority=spec.issuing_authority, version=spec.version,
            effective_date=spec.effective_date, language=spec.language,
        )
        for c in chunks
    ]


def process_markdown(spec: SourceSpec) -> list[Chunk]:
    """Full pipeline from a Markdown path. Pure stdlib (no PyMuPDF/OCR)."""
    from ingestion.extract import extract_markdown

    raw = extract_markdown(spec.path)
    return process_text(raw, spec, is_markdown=True)


def process_textfile(spec: SourceSpec) -> list[Chunk]:
    """Full pipeline from a pre-extracted, page-tagged ``.txt`` artifact.

    Pure stdlib (no PyMuPDF). The file is expected to carry ``[[PAGE n]]``
    markers and the source's native headings, so the structure-aware chunker
    (e.g. ``chunk_sop`` for the SOP) recovers section numbers and page numbers
    just as it would from the original PDF.
    """
    with open(spec.path, encoding="utf-8") as fh:
        raw = fh.read()
    return process_text(raw, spec, is_markdown=False)


def process_pdf(spec: SourceSpec, ocr_lang: str = "eng+hin") -> list[Chunk]:
    """Full pipeline from a PDF path (requires PyMuPDF; imported lazily)."""
    from ingestion.extract import extract_pdf, pages_to_text
    from ingestion.clean import strip_repeated_lines

    pages = extract_pdf(spec.path, ocr_lang=ocr_lang)
    deboiled = strip_repeated_lines([p.text for p in pages])
    for p, t in zip(pages, deboiled):
        p.text = t
    raw = pages_to_text(pages)
    return process_text(raw, spec)


def validate(chunks: list[Chunk]) -> ValidationResult:
    return validate_chunks(chunks)
