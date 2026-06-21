"""Ollama client integration: wiring + end-to-end grounding via the pipeline.

These tests never touch the network — the HTTP transport (`_post`) is replaced
with a fake so we can assert the request shape and prove that retrieval,
verification and citations all keep working when Ollama is the answering model.
"""
from __future__ import annotations

from rag.graph import AnswerPipeline
from rag.llm.ollama import OllamaLLM
from rag.llm.router import build_router

from tests.conftest import seed_services


def test_build_router_selects_ollama():
    router = build_router("ollama")
    assert isinstance(router.default, OllamaLLM)
    assert router.escalation is router.default


def test_config_defaults_and_overrides(monkeypatch):
    c = OllamaLLM()
    assert c.model == "qwen3:8b"
    assert c.base_url == "http://localhost:11434"

    monkeypatch.setenv("OLLAMA_MODEL", "qwen3:14b")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://gpu-box:11434/")
    c2 = OllamaLLM()
    assert c2.model == "qwen3:14b"
    assert c2.base_url == "http://gpu-box:11434"  # trailing slash trimmed


def test_strips_think_block_and_builds_payload():
    client = OllamaLLM()
    captured = {}

    def fake_post(payload):
        captured.update(payload)
        return {"message": {"content": "<think>reasoning here</think>The answer is X [1]"}}

    client._post = fake_post  # type: ignore[method-assign]
    out = client.generate("q", [], "SYS")

    assert out == "The answer is X [1]"           # <think> stripped
    assert captured["model"] == "qwen3:8b"
    assert captured["stream"] is False
    assert captured["think"] is False
    assert captured["options"]["temperature"] == 0.0
    assert captured["messages"][0] == {"role": "system", "content": "SYS"}


def test_pipeline_grounds_and_cites_with_ollama():
    """Full graph with the real retrieval/verify path, Ollama as the model."""
    services = seed_services()

    # Build a grounded, cited answer from the actual retrieved passages so the
    # verifier's hard-gate passes legitimately (no fabricated sections).
    def fake_post(payload):
        user = payload["messages"][1]["content"]
        # Cite [1]; include Section 66C only if the retrieved passages mention it.
        section = "Section 66C" if "66C" in user else ""
        return {"message": {"content": f"{section} addresses identity theft. [1]"}}

    ollama = OllamaLLM()
    ollama._post = fake_post  # type: ignore[method-assign]
    services.router.default = ollama
    services.router.escalation = ollama

    state = AnswerPipeline(services).run(
        "What is the punishment for identity theft under the IT Act?"
    )
    ans = state.answer
    assert not ans.abstained and not ans.refused
    assert ans.citations, "expected at least one grounded citation"
    assert state.model_used == "qwen3:8b"


def test_pipeline_abstains_when_model_hallucinates_section():
    """If the model cites a section absent from the KB, the verifier abstains."""
    services = seed_services()

    def fake_post(payload):
        return {"message": {"content": "Under Section 420 IPC the accused is liable. [1]"}}

    ollama = OllamaLLM()
    ollama._post = fake_post  # type: ignore[method-assign]
    services.router.default = ollama
    services.router.escalation = ollama

    ans = AnswerPipeline(services).run("punishment for cheating online").answer
    assert ans.abstained or ans.refused
