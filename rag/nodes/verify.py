"""Node 6 — grounding & citation verifier: the hard gate (docs/03 §3.3, §3.4).

Zero tolerance for hallucinated legal sections / SOP references. Steps:
  1. Parse [n] citation markers; every marker must map to a supplied passage.
  2. Extract every legal/SOP reference (Section/Sec/u/s/clause N) from the answer.
  3. Each extracted reference MUST appear in a cited passage; otherwise abstain.
  4. Build verified Citation objects for the markers actually used.
"""
from __future__ import annotations

import re

from core.constants import ABSTENTION_MESSAGE
from core.types import Citation
from rag.services import Services
from rag.state import GraphState

_MARKER = re.compile(r"\[(\d+)\]")
# Captures "Section 66D", "Sec. 318", "u/s 43", "clause 4.2", section ids w/ dots.
_LEGAL_REF = re.compile(
    r"(?:section|sec\.?|u/s|clause)\s+(\d+[A-Za-z]?(?:\.\d+)*)",
    re.IGNORECASE,
)


def _normalize(ref: str) -> str:
    return ref.lower().strip()


def extract_legal_refs(text: str) -> set[str]:
    """Public helper: normalized legal/SOP section references found in `text`."""
    return {_normalize(m) for m in _LEGAL_REF.findall(text)}


# Backwards-compatible internal alias.
_refs_in_text = extract_legal_refs


def _passage_contains_ref(passage_text: str, section_number: str | None, ref: str) -> bool:
    if section_number and _normalize(section_number) == ref:
        return True
    # The reference token must appear in the passage as a section-style mention.
    pattern = re.compile(
        r"(?:section|sec\.?|u/s|clause)?\s*" + re.escape(ref) + r"\b", re.IGNORECASE
    )
    return bool(pattern.search(passage_text))


def verify(state: GraphState, services: Services) -> GraphState:
    answer = state.draft_answer or ""
    report: dict = {"hallucinated_refs": [], "unknown_markers": [], "passed": True}

    # Explicit abstention from the model.
    if answer.strip() == ABSTENTION_MESSAGE:
        state.abstain = True
        state.abstain_reason = "model_abstained"
        report["model_abstained"] = True
        state.verifier_report = report
        return state

    passages = state.reranked
    n_passages = len(passages)

    # 1. Markers must reference real passages.
    used_markers = sorted({int(m) for m in _MARKER.findall(answer)})
    valid_markers = [m for m in used_markers if 1 <= m <= n_passages]
    report["unknown_markers"] = [m for m in used_markers if m not in valid_markers]

    # 2/3. Every legal/SOP reference in the answer must be supported by a passage.
    answer_refs = _refs_in_text(answer)
    all_passage_text = " ".join(p.chunk.text for p in passages)
    for ref in answer_refs:
        supported = any(
            _passage_contains_ref(p.chunk.text, p.chunk.section_number, ref) for p in passages
        ) or _passage_contains_ref(all_passage_text, None, ref)
        if not supported:
            report["hallucinated_refs"].append(ref)

    # Hard gate: any unsupported legal/SOP reference OR unknown marker → abstain.
    if report["hallucinated_refs"] or report["unknown_markers"]:
        report["passed"] = False
        state.abstain = True
        state.abstain_reason = "grounding_gate_failed"
        state.verifier_report = report
        return state

    # Citations are mandatory: any non-abstention answer must carry >=1 valid one.
    if not valid_markers:
        report["passed"] = False
        state.abstain = True
        state.abstain_reason = "no_citations"
        state.verifier_report = report
        return state

    # 4. Build verified citations.
    citations = []
    for m in valid_markers:
        c = passages[m - 1].chunk
        citations.append(
            Citation(
                marker=m, chunk_id=c.chunk_id, doc_id=c.doc_id, title=c.title,
                doc_type=c.doc_type,
                section=c.section_number or c.sop_section or c.procedure_name,
                page_start=c.page_start, page_end=c.page_end,
            )
        )
    state.citations = citations
    state.verifier_report = report
    return state
