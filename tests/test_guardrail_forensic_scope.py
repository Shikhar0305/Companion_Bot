"""Guardrail accepts forensic-tool and telecom/service-provider questions.

Regression guard for the scope-vocabulary fix: queries like "write blocker",
"SIM card", and "IP logs from an ISP" are legitimate cybercrime-investigation
questions but were previously refused *before retrieval* because the scope
vocabulary lacked forensic-acquisition and telecom-record terms. Refusing them
at the guardrail meant they could never be answered regardless of the embedder;
letting them through lets the retriever (e5) rank the right SOP section. The
negative controls confirm the additions did not broaden scope into off-domain.
"""
from __future__ import annotations

import pytest

from rag.nodes.guardrail import guardrail
from rag.state import GraphState


def _run(query: str) -> GraphState:
    state = GraphState(query=query, user_role="officer", kb_version="kb_v1")
    return guardrail(state, services=None)  # guardrail does not use services


FORENSIC_TELECOM_IN_DOMAIN = [
    # forensic acquisition tools & media
    "What is a write blocker used for?",
    "How to extract data from a SIM card?",
    "How to image a hard disk forensically?",
    "How do I clone a seized USB drive?",
    "Bitstream acquisition of a mobile device?",
    # telecom / service-provider records
    "How to request IP logs from an ISP?",
    "How to get CDR from the telecom operator?",
    "How do I preserve IPDR records?",
    "What is a tower dump?",
    "How to extract the IMEI and IMSI of a phone?",
]


@pytest.mark.parametrize("query", FORENSIC_TELECOM_IN_DOMAIN)
def test_forensic_telecom_queries_are_in_domain(query):
    state = _run(query)
    assert state.refusal is None, f"wrongly refused: {query!r}"
    assert getattr(state, "in_scope", True) is not False


OFF_DOMAIN = [
    "What is the weather today?",
    "How do I bake a chocolate cake?",
    "Who won the cricket match last night?",
    "Recommend a good movie to watch.",
    "Best recipe for chicken biryani?",
]


@pytest.mark.parametrize("query", OFF_DOMAIN)
def test_off_domain_still_refused(query):
    state = _run(query)
    assert state.refusal is not None, f"should have refused off-domain: {query!r}"
