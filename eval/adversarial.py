"""Adversarial suite: out-of-corpus / injection / non-existent section.

Every case MUST abstain or refuse — the zero-hallucination guarantee.
"""
from __future__ import annotations

from dataclasses import dataclass

from eval.datasets import ADVERSARIAL, AdversarialCase
from rag.graph import AnswerPipeline
from rag.services import Services


@dataclass
class AdversarialMetrics:
    correct_refusal_rate: float
    failures: list[str]
    n: int


def evaluate_adversarial(services: Services,
                         cases: list[AdversarialCase] | None = None) -> AdversarialMetrics:
    cases = cases or ADVERSARIAL
    pipeline = AnswerPipeline(services)
    correct = 0
    failures: list[str] = []
    for case in cases:
        ans = pipeline.run(case.query).answer
        if ans and (ans.abstained or ans.refused):
            correct += 1
        else:
            failures.append(case.query)
    n = len(cases) or 1
    return AdversarialMetrics(correct_refusal_rate=correct / n, failures=failures, n=len(cases))
