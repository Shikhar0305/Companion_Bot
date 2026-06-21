"""Sidecar metadata enrichment (docs/04 §4.4).

`legal_metadata.yaml` is a hand-curated payload (one entry per statutory section:
statute_code, section_number, cognizable/bailable, crime_categories, legal_stage,
…). It is **not** a content source — it is attached to the chunks produced from
the corresponding Markdown so retrieval can filter on it.

The index is keyed by the source file's basename (taken from each entry's
``doc_ref``) plus the section number, so a chunk from ``IT_Act.md`` §66 is joined
to the matching metadata regardless of where the file physically lives.
"""
from __future__ import annotations

import os
from typing import Any

from core.types import Chunk

# Keys lifted into convenience fields; the full entry is kept in extra_metadata.
_SECTION_NAME_KEYS = ("section_name",)


def load_sidecar_index(yaml_paths: list[str]) -> dict[str, dict[str, dict[str, Any]]]:
    """Build {basename_lower: {section_number: metadata}} from sidecar YAML files."""
    import yaml  # lazy; only needed when a sidecar is present

    index: dict[str, dict[str, dict[str, Any]]] = {}
    for path in yaml_paths:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        for entry in data.get("sections", []) or []:
            sec_no = str(entry.get("section_number", "")).strip()
            doc_ref = str(entry.get("doc_ref", "")).strip()
            if not sec_no or not doc_ref:
                continue
            base = os.path.basename(doc_ref).lower()
            index.setdefault(base, {})[sec_no.lower()] = entry
    return index


def enrich_chunks(chunks: list[Chunk], file_basename: str,
                  index: dict[str, dict[str, dict[str, Any]]]) -> int:
    """Attach sidecar metadata to chunks of one source file. Returns #enriched."""
    by_section = index.get(file_basename.lower())
    if not by_section:
        return 0
    enriched = 0
    for c in chunks:
        if not c.section_number:
            continue
        meta = by_section.get(c.section_number.lower())
        if not meta:
            continue
        # Keep the full payload for Qdrant-style filtering; do not overwrite text.
        c.extra_metadata.update({k: v for k, v in meta.items() if k != "doc_ref"})
        if not c.section_title:
            for k in _SECTION_NAME_KEYS:
                if meta.get(k):
                    c.section_title = str(meta[k])
                    break
        enriched += 1
    return enriched
