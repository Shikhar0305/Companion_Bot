from rag.nodes.confidence import score_confidence


def test_high_confidence():
    assert score_confidence(0.8, 0.2, 2, True) == "high"


def test_medium_confidence():
    assert score_confidence(0.4, 0.05, 1, True) == "medium"


def test_low_when_verifier_failed():
    assert score_confidence(0.9, 0.5, 5, False) == "low"


def test_low_when_weak_retrieval():
    assert score_confidence(0.1, 0.0, 1, True) == "low"
