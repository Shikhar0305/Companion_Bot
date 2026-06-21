"""Frozen, version-controlled prompt loader (docs/03 §3.5)."""
from __future__ import annotations

import os

_DIR = os.path.dirname(__file__)
GROUNDED_ANSWER_VERSION = "grounded_answer.v1"


def load_grounded_answer_prompt() -> str:
    with open(os.path.join(_DIR, "grounded_answer.v1.txt"), encoding="utf-8") as fh:
        return fh.read()
