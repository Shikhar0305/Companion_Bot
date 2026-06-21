"""API startup loads the real corpus (audit: startup wiring gap).

Exercises the actual API dependency path (app.deps.get_services / get_pipeline),
which is what routes_ask calls. The lru_caches are cleared per test, and
CORPUS_ROOT (read live by _load_corpus) selects the real corpus vs. an empty dir
to prove the demo fallback.
"""
from __future__ import annotations

import app.deps as deps


def _reset():
    deps.get_services.cache_clear()
    deps.get_pipeline.cache_clear()


def _use_corpus(monkeypatch, root: str | None):
    _reset()
    if root is None:
        monkeypatch.delenv("CORPUS_ROOT", raising=False)
    else:
        monkeypatch.setenv("CORPUS_ROOT", root)


def test_startup_loads_real_corpus(monkeypatch):
    _use_corpus(monkeypatch, None)  # default data/corpus
    services = deps.get_services()
    # Far more than the 2-doc demo (real corpus is ~269 chunks).
    assert services.vector_store.count() > 100


def test_recovery_doc_types_present_at_startup(monkeypatch):
    _use_corpus(monkeypatch, None)
    services = deps.get_services()
    # The startup store contains recovery chunks (not just demo legal/sop).
    store = services.vector_store
    doc_types = {c.doc_type for c in store._chunks.values()}  # in-memory introspection
    assert "recovery" in doc_types
    assert {"act", "sanhita", "decision_tree"} <= doc_types


def test_1930_query_returns_citations(monkeypatch):
    _use_corpus(monkeypatch, None)
    ans = deps.get_pipeline().run("What is the 1930 helpline used for?").answer
    assert not ans.abstained and not ans.refused
    assert ans.citations, "expected citations for the 1930 query"


def test_mule_account_query_returns_citations(monkeypatch):
    _use_corpus(monkeypatch, None)
    ans = deps.get_pipeline().run("How do I trace a mule account?").answer
    assert not ans.abstained and not ans.refused
    assert ans.citations, "expected citations for the mule-account query"


def test_demo_fallback_when_no_corpus(monkeypatch, tmp_path):
    empty = tmp_path / "empty_corpus"
    empty.mkdir()
    _use_corpus(monkeypatch, str(empty))
    services = deps.get_services()
    # Fallback demo KB is small but functional.
    assert 0 < services.vector_store.count() < 20
    # Demo contains IT Act 66D, so a legal query still answers...
    legal = deps.get_pipeline().run("punishment for cheating by personation using computer resource").answer
    assert not legal.abstained and legal.citations
    # ...but recovery content is absent, so the 1930 query has nothing to cite.
    recovery = deps.get_pipeline().run("What is the 1930 helpline used for?").answer
    assert not recovery.citations


def test_caches_reset_for_isolation(monkeypatch):
    # Leave caches clean so later tests/modules get a fresh, default-corpus state.
    _use_corpus(monkeypatch, None)
    deps.get_services()
    _reset()
