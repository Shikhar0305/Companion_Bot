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
    INVESTIGATOR_TERMS,
    RECOVERY_KEYWORDS,
)
from rag.services import Services
from rag.state import GraphState

# Domain vocabulary for scope detection. Single-word terms are matched as stems
# (a query token is in scope when it *starts with* a domain stem, so plurals and
# inflections — "provisions", "records", "investigators" — are covered without a
# full stemmer). Multi-word terms are matched as substrings. This mirrors the
# substring matching the classifier uses, so anything classifiable is in scope.
_DOMAIN_STEMS: set[str] = set()   # len >= 4, matched by prefix
_DOMAIN_SHORT: set[str] = set()   # len < 4, matched exact (acronyms: fir, sop, otp)
_DOMAIN_PHRASES: set[str] = set()  # contain a space, matched as substrings

_EXTRA_TERMS = (
    "cyber", "cybercrime", "crime", "fraud", "scam", "investigate", "investigation",
    "complaint", "victim", "accused", "evidence", "police", "officer", "case",
)


def _add_term(term: str) -> None:
    term = term.lower().strip()
    if not term:
        return
    if " " in term:
        _DOMAIN_PHRASES.add(term)
    elif len(term) >= 4:
        _DOMAIN_STEMS.add(term)
    else:
        _DOMAIN_SHORT.add(term)


for _src in (CAPABILITY_KEYWORDS.values(), CATEGORY_KEYWORDS.values()):
    for _kw in _src:
        for _t in _kw:
            _add_term(_t)
for _t in (*RECOVERY_KEYWORDS, *INVESTIGATOR_TERMS, *_EXTRA_TERMS):
    _add_term(_t)


def _in_scope(query: str) -> bool:
    low = query.lower()
    tokens = re.findall(r"[a-z0-9]+", low)
    if any(t in _DOMAIN_SHORT for t in tokens):
        return True
    if any(t.startswith(stem) for t in tokens for stem in _DOMAIN_STEMS):
        return True
    if any(phrase in low for phrase in _DOMAIN_PHRASES):
        return True
    return bool(re.search(r"\bsection\b|\bu/s\b", query, re.I))

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

    if not _in_scope(q):
        state.in_scope = False
        state.refusal = _REFUSAL
    return state
