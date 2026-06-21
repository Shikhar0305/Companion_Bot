"""Stage 5 — validation QA gate before load (docs/04 §4.2/§4.7).

Schema, completeness, and citation-integrity checks. A new KB version is not
promoted unless these pass (plus golden-question retrieval, run by scripts).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.constants import DOC_TYPES
from core.types import Chunk


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def validate_chunks(chunks: list[Chunk]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not chunks:
        return ValidationResult(ok=False, errors=["no chunks produced"])

    ids = set()
    for c in chunks:
        if not c.chunk_id:
            errors.append("chunk with empty chunk_id")
        if c.chunk_id in ids:
            errors.append(f"duplicate chunk_id: {c.chunk_id}")
        ids.add(c.chunk_id)
        if c.doc_type not in DOC_TYPES:
            errors.append(f"{c.chunk_id}: invalid doc_type {c.doc_type!r}")
        if not c.text.strip():
            errors.append(f"{c.chunk_id}: empty text")
        if not c.title:
            warnings.append(f"{c.chunk_id}: missing title")

    # Completeness for legal docs: every section present exactly once.
    legal = [c for c in chunks if c.doc_type in ("act", "sanhita") and c.section_number]
    seen: dict[str, int] = {}
    for c in legal:
        key = (c.doc_id, c.section_number)
        seen[str(key)] = seen.get(str(key), 0) + 1
    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        errors.append(f"duplicate legal sections: {dupes}")

    # Citation integrity: section_number should appear in its own text.
    bad_cite = [
        c.chunk_id for c in legal
        if c.section_number and c.section_number.lower() not in c.text.lower()
    ]
    if bad_cite:
        warnings.append(f"section_number not found in text for: {bad_cite[:10]}")

    stats = {
        "total_chunks": len(chunks),
        "legal_chunks": len(legal),
        "tagged_with_category": sum(1 for c in chunks if c.cybercrime_categories),
    }
    return ValidationResult(ok=not errors, errors=errors, warnings=warnings, stats=stats)
