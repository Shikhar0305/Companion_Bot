"""Sidecar metadata enrichment (docs/04 §4.4).

Sidecar YAML files carry hand-curated payloads attached to the chunks produced
from the corresponding Markdown so retrieval can filter on them. They are **not**
content sources. Two join granularities are supported:

* **Section-level** (e.g. ``legal_metadata.yaml``): one entry per statutory
  section, joined by source-file basename **+ section number** — a chunk from
  ``IT_Act.md`` §66 gets the matching section metadata.
* **Document-level** (e.g. ``recovery_metadata.yaml``): one entry per document
  (no section number), joined by source-file basename — every chunk of
  ``NCRP_Workflow.md`` gets the ``NCRP_WORKFLOW`` metadata.

An entry is treated as document-level when it has a ``doc_ref`` but no
``section_number``. The index is opaque to callers; only ``enrich_chunks`` reads
it.
"""
from __future__ import annotations

import os
from typing import Any

from core.types import Chunk

# Keys lifted into convenience fields; the full entry is kept in extra_metadata.
_SECTION_NAME_KEYS = ("section_name",)
# Keys never copied into chunk payloads.
_DROP_KEYS = {"doc_ref"}


def load_sidecar_index(yaml_paths: list[str]) -> dict[str, dict[str, Any]]:
    """Build the join index from sidecar YAML files.

    Returns ``{basename_lower: {"sections": {sec_no_lower: entry}, "document": entry|None}}``.
    """
    import yaml  # lazy; only needed when a sidecar is present

    index: dict[str, dict[str, Any]] = {}
    for path in yaml_paths:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        for entry in data.get("sections", []) or []:
            doc_ref = str(entry.get("doc_ref", "")).strip()
            if not doc_ref:
                continue
            base = os.path.basename(doc_ref).lower()
            bucket = index.setdefault(base, {"sections": {}, "document": None})
            sec_no = str(entry.get("section_number", "")).strip()
            if sec_no:
                bucket["sections"][sec_no.lower()] = entry
            else:
                # Document-level metadata (first entry wins if duplicated).
                if bucket["document"] is None:
                    bucket["document"] = entry
    return index


def _payload(entry: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in entry.items() if k not in _DROP_KEYS}


# Sidecar fields whose values are worth making lexically searchable (so a chunk
# can be retrieved by crime type / offence tag, not just its own prose).
_SEARCHABLE_KEYS = ("section_name", "crime_categories", "offence_tags", "channels")


def _searchable_suffix(meta: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in _SEARCHABLE_KEYS:
        val = meta.get(key)
        if not val:
            continue
        if isinstance(val, (list, tuple)):
            parts.append(", ".join(str(v) for v in val))
        else:
            parts.append(str(val))
    return (" Related: " + "; ".join(parts) + ".") if parts else ""


def enrich_chunks(chunks: list[Chunk], file_basename: str,
                  index: dict[str, dict[str, Any]]) -> int:
    """Attach sidecar metadata to chunks of one source file. Returns #enriched.

    Document-level metadata is applied to every chunk; section-level metadata is
    applied to chunks whose section number matches. A chunk counts once even if
    both apply.
    """
    bucket = index.get(file_basename.lower())
    if not bucket:
        return 0
    doc_meta = bucket.get("document")
    by_section = bucket.get("sections") or {}
    doc_payload = _payload(doc_meta) if doc_meta else None

    enriched = 0
    for c in chunks:
        touched = False
        suffix = ""
        # 1. Document-level: applies to every chunk of the file.
        if doc_meta:
            c.extra_metadata.update(doc_payload)
            touched = True
        # 2. Section-level: applies when the chunk's section number matches.
        if c.section_number:
            meta = by_section.get(c.section_number.lower())
            if meta:
                c.extra_metadata.update(_payload(meta))
                # Make legal section metadata searchable (crime categories /
                # offence tags / section name) so a section can be retrieved by
                # crime type. NOTE: only for section-level (legal) chunks — doing
                # this for document-level recovery docs makes them over-match
                # crime-type queries and crowd out the crime decision trees.
                suffix += _searchable_suffix(meta)
                if not c.section_title:
                    for k in _SECTION_NAME_KEYS:
                        if meta.get(k):
                            c.section_title = str(meta[k])
                            break
                touched = True
        if suffix and "Related:" not in c.text:
            c.text = c.text.rstrip() + "\n" + suffix.strip()
        if touched:
            enriched += 1
    return enriched
