"""The grounding hard-gate is the most safety-critical component (docs/03 §3.4)."""
from core.types import Chunk, RetrievedChunk
from rag.nodes.verify import verify
from rag.services import build_services
from rag.state import GraphState


def _state_with_passages(draft, passages):
    s = GraphState(query="q")
    s.draft_answer = draft
    s.reranked = passages
    return s


def _services():
    return build_services()


def _passage(section, text, cid="c1"):
    return RetrievedChunk(
        chunk=Chunk(chunk_id=cid, doc_id="itact2000", doc_type="act",
                    title="IT Act", text=text, section_number=section),
        score=0.9,
    )


def test_supported_section_passes():
    p = _passage("66D", "Section 66D. Punishment for cheating by personation ...")
    s = _state_with_passages("Cheating by personation is punishable. [1]", [p])
    s = verify(s, _services())
    assert not s.abstain
    assert s.verifier_report["passed"] is True
    assert len(s.citations) == 1
    assert s.citations[0].section == "66D"


def test_hallucinated_section_triggers_abstain():
    p = _passage("66D", "Section 66D. Punishment for cheating by personation ...")
    # Answer cites a section NOT present in the passages -> hard gate must fire.
    s = _state_with_passages("This is covered under Section 420 of the law. [1]", [p])
    s = verify(s, _services())
    assert s.abstain is True
    assert s.abstain_reason == "grounding_gate_failed"
    assert "420" in s.verifier_report["hallucinated_refs"]


def test_unknown_marker_triggers_abstain():
    p = _passage("66D", "Section 66D. Punishment for cheating by personation ...")
    s = _state_with_passages("Some grounded claim. [2]", [p])  # only [1] exists
    s = verify(s, _services())
    assert s.abstain is True
    assert 2 in s.verifier_report["unknown_markers"]


def test_substantive_answer_without_citation_abstains():
    p = _passage("66D", "Section 66D ...")
    s = _state_with_passages(
        "You should immediately freeze the account and trace the beneficiary today now.",
        [p],
    )
    s = verify(s, _services())
    assert s.abstain is True
    assert s.abstain_reason == "no_citations"


def test_explicit_model_abstention_preserved():
    p = _passage("66D", "Section 66D ...")
    s = _state_with_passages("Information not found in approved knowledge sources.", [p])
    s = verify(s, _services())
    assert s.abstain is True
    assert s.abstain_reason == "model_abstained"
