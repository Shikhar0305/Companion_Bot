"""Structured logging with light PII redaction (docs/09 §S4)."""
from __future__ import annotations

import json
import logging
import re
import sys
from typing import Any

# Patterns redacted from logs before persistence.
_REDACTIONS = [
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL]"),
    (re.compile(r"\b(?:\+?\d[\d -]{8,}\d)\b"), "[PHONE]"),
    (re.compile(r"\b\d{12,19}\b"), "[CARD/ACCT]"),
    (re.compile(r"\b[\w.-]+@(?:upi|okhdfcbank|okaxis|ybl|paytm|ibl)\b", re.I), "[VPA]"),
]


def redact(text: str) -> str:
    """Mask common PII so it never lands in logs or the audit store verbatim."""
    if not text:
        return text
    for pattern, repl in _REDACTIONS:
        text = pattern.sub(repl, text)
    return text


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.__dict__.get("extra_fields"):
            payload.update(record.__dict__["extra_fields"])
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = "companion_bot") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
