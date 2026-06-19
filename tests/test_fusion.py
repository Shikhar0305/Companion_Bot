from rag.retrieval.fusion import fuse_and_order, reciprocal_rank_fusion


def test_rrf_rewards_consensus_top_ranks():
    a = ["x", "y", "z"]
    b = ["x", "z", "y"]
    scores = reciprocal_rank_fusion([a, b])
    assert scores["x"] > scores["y"]
    assert scores["x"] > scores["z"]


def test_fuse_and_order_returns_descending():
    a = ["d1", "d2", "d3"]
    b = ["d2", "d1", "d4"]
    order = fuse_and_order([a, b])
    assert order[0] in ("d1", "d2")
    assert set(order) == {"d1", "d2", "d3", "d4"}


def test_rrf_empty():
    assert reciprocal_rank_fusion([]) == {}
