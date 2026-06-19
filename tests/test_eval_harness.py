"""The eval harness must run and the adversarial set must fully abstain/refuse."""
from eval.adversarial import evaluate_adversarial
from eval.answer_eval import evaluate_answers
from eval.retrieval_eval import evaluate_retrieval
from tests.conftest import seed_services


def test_retrieval_recall():
    services = seed_services()
    m = evaluate_retrieval(services, k=10)
    assert m.recall_at_k >= 0.75  # tiny demo KB; production gate is 0.90


def test_answers_grounded():
    services = seed_services()
    m = evaluate_answers(services)
    assert m.grounded_rate >= 0.75
    assert m.citation_present_rate >= 0.75


def test_adversarial_all_refuse():
    services = seed_services()
    m = evaluate_adversarial(services)
    assert m.correct_refusal_rate == 1.0, m.failures
