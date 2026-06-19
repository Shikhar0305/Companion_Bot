"""Node 1 — scope guardrail + prompt-injection screening (docs/03 §3.3).

Rejects off-domain questions and obvious injection attempts before any retrieval.
Lightweight rules/keywords here; a small-LLM classifier can be layered behind the
same interface in production.
"""
from __future__ import annotations

import re

from core.constants import (
    CAPABILITY_KEYWORDS,
    CATEGORY_KEYWORDS,
)
from rag.services import Services
from rag.state import GraphState

_DOMAIN_TERMS: set[str] = set()
for _kw in CAPABILITY_KEYWORDS.values():
    _DOMAIN_TERMS.update(_kw)
for _kw in CATEGORY_KEYWORDS.values():
    _DOMAIN_TERMS.update(w for kw in [_kw] for w in kw)
_DOMAIN_TERMS.update({
    "cyber", "cybercrime", "crime", "fraud", "scam", "investigate", "investigation",
    "complaint", "victim", "accused", "evidence", "police", "officer", "case",
})

_INJECTION = re.compile(
    r"(ignore (all )?previous instructions|disregard the system|reveal your prompt|"
    r"you are now|act as|jailbreak|system prompt)",
    re.IGNORECASE,
)

_REFUSAL = (
    "I can only assist with cybercrime investigation, legal, digital-forensics, "
    "OSINT, and financial-fraud questions grounded in the approved knowledge base."
)


def guardrail(state: GraphState, services: Services) -> GraphState:
    q = state.query.strip()
    if not q:
        state.in_scope = False
        state.refusal = _REFUSAL
        return state

    if _INJECTION.search(q):
        state.in_scope = False
        state.refusal = _REFUSAL
        state.verifier_report["injection_blocked"] = True
        return state

    tokens = set(re.findall(r"[a-z0-9]+", q.lower()))
    # In scope if it mentions any domain term OR an explicit legal/section cue.
    in_scope = bool(tokens & _DOMAIN_TERMS) or bool(re.search(r"\bsection\b|\bu/s\b", q, re.I))
    if not in_scope:
        state.in_scope = False
        state.refusal = _REFUSAL
    return state
