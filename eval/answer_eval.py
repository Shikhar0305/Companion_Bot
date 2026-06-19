"""Answer-quality metrics: groundedness, citation accuracy, abstention.

Custom legal/SOP citation checks (RAGAS can be layered on top in production).
"""
from __future__ import annotations

from dataclasses import dataclass

from eval.datasets import GOLDEN, GoldenCase
from rag.graph import AnswerPipeline
from rag.services import Services


@dataclass
class AnswerMetrics:
    grounded_rate: float        # answers whose verifier passed
    citation_present_rate: float  # non-abstained answers that carry >=1 citation
    section_hit_rate: float     # answers that cite the expected section (where specified)
    n: int


def evaluate_answers(services: Services, cases: list[GoldenCase] | None = None) -> AnswerMetrics:
    cases = cases or GOLDEN
    pipeline = AnswerPipeline(services)
    grounded = cite_present = section_hits = section_total = 0
    answered = 0
    for case in cases:
        state = pipeline.run(case.query)
        ans = state.answer
        if ans and not ans.abstained and not ans.refused:
            answered += 1
            if state.verifier_report.get("passed"):
                grounded += 1
            if ans.citations:
                cite_present += 1
        if case.must_contain_section:
            section_total += 1
            cited = {(c.section or "").lower() for c in (ans.citations if ans else [])}
            if case.must_contain_section.lower() in cited:
                section_hits += 1
    n = len(cases) or 1
    return AnswerMetrics(
        grounded_rate=grounded / n,
        citation_present_rate=(cite_present / answered) if answered else 0.0,
        section_hit_rate=(section_hits / section_total) if section_total else 1.0,
        n=len(cases),
    )
