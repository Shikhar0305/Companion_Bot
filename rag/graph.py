"""The answer graph (docs/03 §3.3).

`AnswerPipeline` runs the nodes in sequence with the documented branching
(guardrail → analysis → retrieve → rerank → generate → verify → confidence →
assemble, with abstain/refuse branches). It depends only on the node functions
and `Services`, so it runs with stub/in-memory backends and no external
dependencies.

`build_langgraph(services)` wires the same node functions into a LangGraph
`StateGraph` for production deployments where langgraph is installed; it is
optional and imported lazily.
"""
from __future__ import annotations

from rag.nodes.abstain import abstain, assemble, refuse
from rag.nodes.confidence import confidence
from rag.nodes.generate import generate
from rag.nodes.guardrail import guardrail
from rag.nodes.query_analysis import query_analysis
from rag.nodes.rerank import rerank
from rag.nodes.retrieve import retrieve
from rag.nodes.verify import verify
from rag.services import Services
from rag.state import GraphState


class AnswerPipeline:
    def __init__(self, services: Services) -> None:
        self.services = services

    def run(self, query: str, user_role: str = "officer") -> GraphState:
        s = self.services
        state = GraphState(query=query, user_role=user_role, kb_version=s.config.kb_version)

        state = guardrail(state, s)
        if state.refusal:
            return refuse(state, s)

        state = query_analysis(state, s)
        state = retrieve(state, s)
        state = rerank(state, s)
        if state.abstain:
            return abstain(state, s)

        state = generate(state, s)
        state = verify(state, s)
        if state.abstain:
            return abstain(state, s)

        state = confidence(state, s)
        return assemble(state, s)


def build_langgraph(services: Services):
    """Build a LangGraph StateGraph using the same node functions (optional)."""
    from langgraph.graph import END, START, StateGraph  # lazy

    def _wrap(fn):
        return lambda state: fn(state, services)

    g = StateGraph(GraphState)
    g.add_node("guardrail", _wrap(guardrail))
    g.add_node("query_analysis", _wrap(query_analysis))
    g.add_node("retrieve", _wrap(retrieve))
    g.add_node("rerank", _wrap(rerank))
    g.add_node("generate", _wrap(generate))
    g.add_node("verify", _wrap(verify))
    g.add_node("confidence", _wrap(confidence))
    g.add_node("assemble", _wrap(assemble))
    g.add_node("abstain", _wrap(abstain))
    g.add_node("refuse", _wrap(refuse))

    g.add_edge(START, "guardrail")
    g.add_conditional_edges(
        "guardrail",
        lambda s: "refuse" if s.refusal else "query_analysis",
        {"refuse": "refuse", "query_analysis": "query_analysis"},
    )
    g.add_edge("query_analysis", "retrieve")
    g.add_edge("retrieve", "rerank")
    g.add_conditional_edges(
        "rerank",
        lambda s: "abstain" if s.abstain else "generate",
        {"abstain": "abstain", "generate": "generate"},
    )
    g.add_edge("generate", "verify")
    g.add_conditional_edges(
        "verify",
        lambda s: "abstain" if s.abstain else "confidence",
        {"abstain": "abstain", "confidence": "confidence"},
    )
    g.add_edge("confidence", "assemble")
    g.add_edge("assemble", END)
    g.add_edge("abstain", END)
    g.add_edge("refuse", END)
    return g.compile()
