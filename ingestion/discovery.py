"""Corpus auto-discovery (docs/04 §4.2).

Walks ``data/corpus/`` recursively and turns every ingestible file into a
``SourceSpec`` — no hardcoded SEED list. Conventions:

* folder name → ``doc_type`` (``legal_repository`` → act/sanhita,
  ``decision_trees`` → decision_tree, ``recovery_repository`` → recovery);
* ``.md`` files are chunked as Markdown, ``.pdf`` files via the existing PDF path
  (backward compatible);
* ``.yaml`` / ``.yml`` files are treated as **sidecar metadata** and are never
  chunked.

doc_id/title are derived from the filename (title falls back to the first
Markdown ``# `` heading), so dropping a new file into the right folder makes it
ingest automatically.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

from ingestion.pipeline import SourceSpec

DEFAULT_CORPUS_ROOT = "data/corpus"

# Folder name → default doc_type. Unknown folders fall back to "manual".
_FOLDER_DOC_TYPE = {
    "legal_repository": "act",
    "decision_trees": "decision_tree",
    "recovery_repository": "recovery",
}
# Slugs within legal_repository that are sanhitas/adhiniyams rather than "act".
_SANHITA_SLUGS = {"bns", "bnss", "bsa"}

_MD_EXTS = {".md", ".markdown"}
_PDF_EXTS = {".pdf"}
_YAML_EXTS = {".yaml", ".yml"}
_FIRST_H1 = re.compile(r"(?m)^#\s+(.+?)\s*$")


@dataclass
class DiscoveredSource:
    spec: SourceSpec
    fmt: str  # "md" | "pdf"


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "doc"


def _doc_type(folder: str, slug: str) -> str:
    base = _FOLDER_DOC_TYPE.get(folder, "manual")
    if folder == "legal_repository" and slug in _SANHITA_SLUGS:
        return "sanhita"
    return base


def _title_from_markdown(path: str, fallback: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            head = fh.read(4000)
    except OSError:
        return fallback
    m = _FIRST_H1.search(head)
    return m.group(1).strip() if m else fallback


def discover_corpus(root: str = DEFAULT_CORPUS_ROOT) -> tuple[list[DiscoveredSource], list[str]]:
    """Return (sources, sidecar_yaml_paths) found recursively under ``root``."""
    sources: list[DiscoveredSource] = []
    sidecars: list[str] = []
    if not os.path.isdir(root):
        return sources, sidecars

    for dirpath, _dirs, files in os.walk(root):
        folder = os.path.basename(dirpath)
        for fname in sorted(files):
            ext = os.path.splitext(fname)[1].lower()
            path = os.path.join(dirpath, fname)
            if ext in _YAML_EXTS:
                sidecars.append(path)
                continue
            if ext not in _MD_EXTS and ext not in _PDF_EXTS:
                continue
            stem = os.path.splitext(fname)[0]
            slug = _slug(stem)
            doc_type = _doc_type(folder, slug)
            fmt = "md" if ext in _MD_EXTS else "pdf"
            title = _title_from_markdown(path, stem) if fmt == "md" else stem.replace("_", " ")
            spec = SourceSpec(path=path, doc_id=slug, title=title, doc_type=doc_type)
            sources.append(DiscoveredSource(spec=spec, fmt=fmt))
    return sources, sidecars
