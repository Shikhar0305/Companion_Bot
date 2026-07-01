"""Stage 4 — metadata tagging (docs/04 §4.2/§4.4). Pure stdlib.

Assigns capability areas and cybercrime categories from keyword cues. In
production a classifier augments this and an SME reviews the output.
"""
from __future__ import annotations

from core.constants import CAPABILITY_KEYWORDS, CATEGORY_KEYWORDS
from core.types import Chunk

# doc_type → default capability area when no keyword cue is present.
_DEFAULT_AREA = {
    "act": "legal", "sanhita": "legal",
    "sop": "investigation", "manual": "forensics",
    "playbook": "osint", "advisory": "financial", "circular": "investigation",
    "decision_tree": "investigation", "recovery": "financial",
    "forensics": "forensics", "procedure": "investigation",
}


def detect_categories(text: str) -> list[str]:
    low = text.lower()
    return [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(kw in low for kw in kws)]


def detect_capability_areas(text: str, doc_type: str) -> list[str]:
    low = text.lower()
    hits = [area for area, kws in CAPABILITY_KEYWORDS.items() if any(kw in low for kw in kws)]
    if not hits:
        hits = [_DEFAULT_AREA.get(doc_type, "investigation")]
    return hits


def tag_chunk(chunk: Chunk, *, issuing_authority: str = "", version: str = "",
              effective_date: str = "", language: str = "en") -> Chunk:
    chunk.cybercrime_categories = detect_categories(chunk.text)
    chunk.capability_area = detect_capability_areas(chunk.text, chunk.doc_type)
    chunk.issuing_authority = issuing_authority
    chunk.version = version
    chunk.effective_date = effective_date
    chunk.language = language
    return chunk
