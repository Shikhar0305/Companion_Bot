#!/usr/bin/env python3
"""Run the full evaluation harness against a seeded KB (docs/06 Phase 4).

In the dev profile this seeds the in-memory demo KB and evaluates retrieval,
answers, and the adversarial suite — enforcing the release gate thresholds.
"""
from __future__ import annotations

import sys

from app.deps import get_services
from eval.adversarial import evaluate_adversarial
from eval.answer_eval import evaluate_answers
from eval.retrieval_eval import evaluate_retrieval

# Release-gate thresholds (docs/10 §10.2).
THRESHOLDS = {
    "recall_at_10": 0.90,
    "grounded_rate": 0.95,
    "section_hit_rate": 0.95,
    "correct_refusal_rate": 0.95,
}


def main() -> int:
    services = get_services()

    r = evaluate_retrieval(services, k=10)
    a = evaluate_answers(services)
    adv = evaluate_adversarial(services)

    print(f"retrieval: recall@{r.k}={r.recall_at_k:.2f} mrr={r.mrr:.2f} (n={r.n})")
    print(f"answers:   grounded={a.grounded_rate:.2f} citation_present={a.citation_present_rate:.2f} "
          f"section_hit={a.section_hit_rate:.2f} (n={a.n})")
    print(f"adversarial: correct_refusal={adv.correct_refusal_rate:.2f} (n={adv.n})")
    if adv.failures:
        print(f"  FAILURES: {adv.failures}")

    checks = {
        "recall_at_10": r.recall_at_k,
        "grounded_rate": a.grounded_rate,
        "section_hit_rate": a.section_hit_rate,
        "correct_refusal_rate": adv.correct_refusal_rate,
    }
    passed = True
    for name, threshold in THRESHOLDS.items():
        ok = checks[name] >= threshold
        passed = passed and ok
        print(f"  gate {name}: {checks[name]:.2f} >= {threshold} -> {'PASS' if ok else 'FAIL'}")

    print("RELEASE GATE:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
