"""Helper to assemble an AuditRecord from a finished GraphState (docs/10 §10.5)."""
from __future__ import annotations

from core.audit import AuditRecord
from rag.state import GraphState


def build_audit_record(
    *, request_id: str, user: str, state: GraphState, prompt_version: str,
    latency_ms: float,
) -> AuditRecord:
    a = state.answer
    return AuditRecord(
        request_id=request_id,
        user=user,
        user_role=state.user_role,
        kb_version=state.kb_version,
        query=state.query,
        capability_area=state.analysis.capability_area if state.analysis else None,
        cybercrime_categories=state.analysis.cybercrime_categories if state.analysis else [],
        doc_type_filter=state.analysis.doc_type_filter if state.analysis else [],
        retrieved=[{"chunk_id": rc.chunk.chunk_id, "score": rc.score} for rc in state.retrieved],
        reranked=[{"chunk_id": rc.chunk.chunk_id, "score": rc.score} for rc in state.reranked],
        model=state.model_used,
        prompt_version=prompt_version,
        raw_output=state.draft_answer,
        verifier_report=state.verifier_report,
        final_answer=a.text if a else None,
        citations=[c.to_dict() for c in (a.citations if a else [])],
        confidence=a.confidence if a else None,
        abstained=a.abstained if a else False,
        refused=a.refused if a else False,
        latency_ms=latency_ms,
    )
