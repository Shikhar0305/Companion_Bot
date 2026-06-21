"""Knowledge-base version helpers (docs/04 §4.5).

KB is immutable + versioned. Each ingestion produces kb_vN; promotion switches
an alias after the validation suite passes, enabling rollback and reproducible
historical answers.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class KbVersion:
    version: str          # e.g. "kb_v1"
    collection: str       # underlying vector-store collection name
    created_at: str
    chunk_count: int
    validated: bool = False


def next_version(existing: list[str]) -> str:
    nums = [int(v.split("_v")[-1]) for v in existing if v.startswith("kb_v") and v.split("_v")[-1].isdigit()]
    return f"kb_v{(max(nums) + 1) if nums else 1}"


class VersionRegistry:
    """Tracks KB versions and the live alias on disk."""

    def __init__(self, path: str = "data/kb_registry.json") -> None:
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not os.path.exists(path):
            self._save({"live": None, "versions": {}})

    def _load(self) -> dict:
        with open(self.path, encoding="utf-8") as fh:
            return json.load(fh)

    def _save(self, data: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def register(self, ver: KbVersion) -> None:
        data = self._load()
        data["versions"][ver.version] = ver.__dict__
        self._save(data)

    def promote(self, version: str) -> None:
        """Switch the live alias — only after validation passes."""
        data = self._load()
        if version not in data["versions"]:
            raise KeyError(f"unknown version {version}")
        if not data["versions"][version].get("validated"):
            raise ValueError(f"refusing to promote unvalidated version {version}")
        data["live"] = version
        self._save(data)

    def live(self) -> str | None:
        return self._load().get("live")
