"""Node 2 — query analysis, classification, and expansion (docs/03 §3.3)."""
from __future__ import annotations

import re

from core.constants import (
    CAPABILITY_KEYWORDS,
    CATEGORY_KEYWORDS,
    CRIME_SYNONYMS,
    SOP_PROCEDURAL_CUES,
    STATUTE_ALIASES,
)
from core.types import QueryAnalysis
from rag.services import Services
from rag.state import GraphState

# Capability area → doc_type filter (docs/02 §2.4).
_AREA_DOC_TYPES = {
    "legal": ["act", "sanhita"],
    "forensics": ["sop", "manual", "decision_tree"],
    "osint": ["playbook", "manual", "sop"],
    "financial": ["sop", "advisory", "recovery", "decision_tree"],
    "investigation": ["sop", "manual", "decision_tree", "recovery"],
}


def _classify_capability(q: str) -> str:
    scores = {area: 0 for area in CAPABILITY_KEYWORDS}
    low = q.lower()
    for area, kws in CAPABILITY_KEYWORDS.items():
        scores[area] = sum(1 for kw in kws if kw in low)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "investigation"


def _is_sop_procedural(q: str) -> bool:
    low = q.lower()
    return any(cue in low for cue in SOP_PROCEDURAL_CUES)


def _detect_categories(q: str) -> list[str]:
    low = q.lower()
    hits = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in low for kw in kws):
            hits.append(cat)
    return hits


def _expand(q: str) -> list[str]:
    low = q.lower()
    expansions: list[str] = []
    for alias, full in STATUTE_ALIASES.items():
        if alias in low:
            expansions.extend(full)
    # Crime-term synonyms bridge everyday phrasing to statute/SOP wording so
    # lexical retrieval can match (e.g. "malware" -> "computer contaminant").
    for term, syns in CRIME_SYNONYMS.items():
        if term in low:
            expansions.extend(syns)
    return expansions


def query_analysis(state: GraphState, services: Services) -> GraphState:
    q = state.query
    area = _classify_capability(q)
    categories = _detect_categories(q)
    expansions = _expand(q)
    rewritten = q if not expansions else q + " (" + "; ".join(expansions) + ")"

    doc_types = _AREA_DOC_TYPES.get(area, [])
    # Case-documentation / intake questions land in the weak-signal "investigation"
    # bucket, whose broad filter lets clean decision-tree / recovery passages
    # out-rank the correct SOP section. Narrow those to SOP-first so the right
    # repository wins; only applied to the default bucket, never over-riding a
    # confident legal/financial/osint classification.
    if area in ("investigation", "forensics", "osint") and _is_sop_procedural(q):
        doc_types = ["sop", "manual"]

    state.analysis = QueryAnalysis(
        rewritten_query=rewritten,
        capability_area=area,
        cybercrime_categories=categories,
        expansions=expansions,
        doc_type_filter=doc_types,
    )
    return state
