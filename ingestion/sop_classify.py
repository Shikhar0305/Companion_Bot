"""Heading-anchored SOP section classification (Phase 3, layer 1).

Assigns ``section_type`` / ``priority`` / ``procedure_type`` / ``topic`` /
``keywords`` to an SOP chunk **from its heading**, never its body: operational
keywords bleed into conceptual prose (measured — e.g. an "Introduction" section
that merely mentions "preservation"), so body-keyword classification is too
noisy. A curated sidecar (``sop_metadata.yaml``) overrides these defaults where
needed (layer 2). Pure stdlib.
"""
from __future__ import annotations

import re

from core.constants import SOP_TYPE_PRIORITY

# A heading that *announces background* — checked first so an "Introduction to
# Chain of Custody" is conceptual even though it names an operational topic.
_CONCEPTUAL = re.compile(
    r"\b(conceptual|introduction|introductory|preface|prefatory|definition|"
    r"meaning|nature of|evolution|overview|typolog|classification|understanding|"
    r"purpose and role|scope (&|and) objectiv|foundation|positioning of chapter|"
    r"why )\b",
    re.I,
)

# Operational heading cues, most specific first (first match wins).
_HEADING_TYPE: list[tuple[str, str]] = [
    ("recovery_procedure", r"1930|ncrp|account freez|fund recall|\bmule\b|beneficiary|chargeback|refund|\blien\b"),
    ("telecom_investigation", r"\bcdr\b|\bipdr\b|call detail|telecom|\bisp\b|subscriber|ip address|cell tower"),
    ("financial_investigation", r"money trail|financial|banking|transaction|money mule|\bupi\b|proceeds|fund flow|freezing"),
    ("forensic_procedure", r"forensic|acquisition|imaging|write[ -]?block|\bhash\b|disk|\bssd\b|\bhdd\b|\bram\b|volatile|mobile|\bsim\b|cloud|extraction|malware|clon"),
    ("evidence_collection", r"seiz|preserv|chain of custody|crime scene|first responder|collection|panch|labelling|bag and tag"),
    ("prosecution", r"charge ?sheet|prosecut|\btrial\b|conviction|arrest|final report|closure|admissibil"),
    ("investigation_procedure", r"investigation|\bfir\b|case diary|checklist|intake|complain|jurisdiction|\bnotice\b|procedure"),
    ("legal_reference", r"legal framework|section \d+|statut|penal|offence|\bbnss\b|\bbns\b|\bbsa\b|it act|article \d+"),
]

# Chapter → default type when the heading is inconclusive (from SOP chapter titles).
_CHAPTER_DEFAULT: dict[int, str] = {
    1: "conceptual", 2: "conceptual", 3: "legal_reference",
    4: "investigation_procedure", 5: "evidence_collection", 6: "evidence_collection",
    7: "evidence_collection", 8: "forensic_procedure", 9: "forensic_procedure",
    10: "forensic_procedure", 11: "forensic_procedure", 12: "forensic_procedure",
    15: "financial_investigation", 17: "forensic_procedure", 18: "forensic_procedure",
    19: "legal_reference", 20: "prosecution", 21: "investigation_procedure",
    22: "investigation_procedure", 25: "investigation_procedure",
}

_PROCEDURE_TYPE: list[tuple[str, str]] = [
    ("request", r"request|preservation letter|\bnotice\b|summon|requisition"),
    ("acquisition", r"acquisition|imaging|clon|extraction"),
    ("analysis", r"analys|examin|\breview\b"),
    ("escalation", r"escalat|nodal|freez|recall"),
    ("filing", r"charge ?sheet|final report|closure|filing"),
    ("collection", r"seiz|preserv|custody|scene|collect"),
]

_TOPIC_MAP: list[tuple[str, str]] = [
    ("chain of custody", "chain_of_custody"), ("first responder", "first_responder"),
    ("write block", "write_blocker"), ("mobile", "mobile_forensics"),
    ("sim", "sim_forensics"), ("cloud", "cloud_forensics"), ("cdr", "cdr_request"),
    ("preservation request", "preservation_request"), ("account freez", "account_freeze"),
    ("1930", "helpline_1930"), ("mule", "mule_account"), ("charge", "charge_sheet"),
    ("crime scene", "crime_scene"), ("imaging", "disk_imaging"), ("seiz", "seizure"),
]

_STOP = {"the", "of", "and", "for", "with", "from", "into", "their", "this", "that"}


def _chapter(sop_section: str | None) -> int:
    m = re.match(r"(\d+)", sop_section or "")
    return int(m.group(1)) if m else 0


def _keywords(heading: str) -> list[str]:
    toks = re.findall(r"[A-Za-z0-9]+", (heading or "").lower())
    return [t for t in toks if len(t) > 3 and t not in _STOP][:8]


def _topic(heading: str, stype: str) -> str:
    low = (heading or "").lower()
    for kw, topic in _TOPIC_MAP:
        if kw in low:
            return topic
    return stype


def classify(sop_section: str | None, heading: str) -> dict:
    """Return heading-derived metadata for one SOP section."""
    h = heading or ""
    if _CONCEPTUAL.search(h):
        stype = "conceptual"
    else:
        stype = next((name for name, pat in _HEADING_TYPE if re.search(pat, h, re.I)), None)
        if stype is None:
            stype = _CHAPTER_DEFAULT.get(_chapter(sop_section), "conceptual")
    ptype = next((name for name, pat in _PROCEDURE_TYPE if re.search(pat, h, re.I)), None)
    return {
        "section_type": stype,
        "priority": SOP_TYPE_PRIORITY.get(stype, 1),
        "procedure_type": ptype,
        "topic": _topic(h, stype),
        "keywords": _keywords(h),
    }
