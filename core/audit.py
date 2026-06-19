"""Per-answer audit trail (docs/02 §2.6, docs/10 §10.5).

Every answer is fully reconstructable: query, filters, retrieved IDs+scores,
prompt, model+version, raw output, verifier results, final answer, citations,
confidence, latency, user, kb_version.

The default backend writes append-only JSONL to disk; production swaps in the
PostgreSQL-backed store (same interface).
"""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Protocol

from core.logging import redact


@dataclass
class AuditRecord:
    request_id: str
    user: str
    user_role: str
    kb_version: str
    query: str
    timestamp: float = field(default_factory=time.time)
    capability_area: Optional[str] = None
    cybercrime_categories: list[str] = field(default_factory=list)
    doc_type_filter: list[str] = field(default_factory=list)
    retrieved: list[dict[str, Any]] = field(default_factory=list)   # {chunk_id, score}
    reranked: list[dict[str, Any]] = field(default_factory=list)
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    raw_output: Optional[str] = None
    verifier_report: dict[str, Any] = field(default_factory=dict)
    final_answer: Optional[str] = None
    citations: list[dict[str, Any]] = field(default_factory=list)
    confidence: Optional[str] = None
    abstained: bool = False
    refused: bool = False
    latency_ms: Optional[float] = None

    def redacted(self) -> dict[str, Any]:
        d = asdict(self)
        d["query"] = redact(self.query)
        if self.raw_output:
            d["raw_output"] = redact(self.raw_output)
        if self.final_answer:
            d["final_answer"] = redact(self.final_answer)
        return d


class AuditStore(Protocol):
    def write(self, record: AuditRecord) -> None: ...


class JsonlAuditStore:
    """Append-only JSONL audit store (default / dev)."""

    def __init__(self, path: str = "data/audit/audit.jsonl") -> None:
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def write(self, record: AuditRecord) -> None:
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.redacted(), ensure_ascii=False) + "\n")


def new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:24]}"
