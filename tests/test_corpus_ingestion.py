"""Markdown ingestion, corpus auto-discovery, sidecar metadata, and routing."""
from __future__ import annotations

import os

from core.constants import DOC_TYPES
from ingestion.chunk import chunk_document, chunk_legal
from ingestion.discovery import discover_corpus
from ingestion.extract import extract_markdown
from ingestion.pipeline import SourceSpec, process_markdown, process_text
from ingestion.sidecar import enrich_chunks, load_sidecar_index
from rag.nodes.query_analysis import _AREA_DOC_TYPES

LEGAL_MD = """# IT Act — Repository

Intro front-matter.

### IT Act, 2000 Section 66C — Punishment for identity theft

**Section Number:** 66C

**Description:**
Whoever fraudulently uses another person's password or unique ID feature.

### IT Act, 2000 Section 66D — Cheating by personation

**Section Number:** 66D

**Description:**
Cheating by personation using a computer resource.
"""

TREE_MD = """# UPI / Banking Fraud

## Initial Triage

```
IF complaint received THEN register FIR
```

## Escalation Decisions

```
IF cross-state THEN escalate to nodal officer
```
"""

SIDECAR_YAML = """schema_version: 1
sections:
  - point_id: 1
    statute_code: IT_ACT
    section_number: "66C"
    section_name: "Punishment for identity theft"
    legal_stage: charging
    cognizable: true
    bailable: true
    crime_categories: ["Identity Theft"]
    doc_ref: "data/corpus/legal_repository/IT_Act.md"
"""


# 1. Markdown ingestion -------------------------------------------------------
def test_extract_markdown_reads_file(tmp_path):
    p = tmp_path / "IT_Act.md"
    p.write_text(LEGAL_MD, encoding="utf-8")
    assert extract_markdown(str(p)).startswith("# IT Act")


def test_process_markdown_legal_extracts_sections(tmp_path):
    p = tmp_path / "IT_Act.md"
    p.write_text(LEGAL_MD, encoding="utf-8")
    spec = SourceSpec(path=str(p), doc_id="it_act", title="IT Act", doc_type="act")
    chunks = process_markdown(spec)
    secs = {c.section_number for c in chunks if c.section_number}
    assert {"66C", "66D"} <= secs
    # Section text is grounded (number appears in its own chunk).
    c66c = next(c for c in chunks if c.section_number == "66C")
    assert "66C" in c66c.text


def test_process_markdown_decision_tree_keeps_branches(tmp_path):
    p = tmp_path / "01_upi.md"
    p.write_text(TREE_MD, encoding="utf-8")
    spec = SourceSpec(path=str(p), doc_id="upi", title="UPI Fraud", doc_type="decision_tree")
    chunks = process_markdown(spec)
    names = {c.procedure_name for c in chunks if c.procedure_name}
    assert "Initial Triage" in names and "Escalation Decisions" in names


# 2. Auto-discovery -----------------------------------------------------------
def test_discovery_classifies_and_skips_yaml(tmp_path):
    root = tmp_path / "corpus"
    (root / "legal_repository").mkdir(parents=True)
    (root / "decision_trees").mkdir()
    (root / "recovery_repository").mkdir()
    (root / "legal_repository" / "IT_Act.md").write_text(LEGAL_MD, encoding="utf-8")
    (root / "legal_repository" / "BNS.md").write_text(LEGAL_MD, encoding="utf-8")
    (root / "legal_repository" / "legal_metadata.yaml").write_text(SIDECAR_YAML, encoding="utf-8")
    (root / "decision_trees" / "01_upi.md").write_text(TREE_MD, encoding="utf-8")
    (root / "recovery_repository" / "freeze.md").write_text("# Freeze\n\n## Steps\nx", encoding="utf-8")

    sources, sidecars = discover_corpus(str(root))
    by_path = {os.path.basename(s.spec.path): s for s in sources}

    assert len(sidecars) == 1 and sidecars[0].endswith("legal_metadata.yaml")
    assert by_path["IT_Act.md"].spec.doc_type == "act"
    assert by_path["BNS.md"].spec.doc_type == "sanhita"      # sanhita refinement
    assert by_path["01_upi.md"].spec.doc_type == "decision_tree"
    assert by_path["freeze.md"].spec.doc_type == "recovery"
    assert all(s.fmt == "md" for s in sources)
    # title derived from first H1 heading
    assert by_path["01_upi.md"].spec.title == "UPI / Banking Fraud"


def test_discovery_routes_pdf_without_extracting(tmp_path):
    """A .pdf is discovered and marked fmt=pdf (existing PDF path preserved)."""
    root = tmp_path / "corpus"
    (root / "legal_repository").mkdir(parents=True)
    (root / "legal_repository" / "BNSS.pdf").write_bytes(b"%PDF-1.4 dummy")
    sources, _ = discover_corpus(str(root))
    pdf = next(s for s in sources if s.spec.path.endswith(".pdf"))
    assert pdf.fmt == "pdf"
    assert pdf.spec.doc_type == "sanhita"


def test_discovery_empty_root_is_safe(tmp_path):
    sources, sidecars = discover_corpus(str(tmp_path / "missing"))
    assert sources == [] and sidecars == []


# 3. Metadata attachment ------------------------------------------------------
def test_sidecar_enrichment_attaches_metadata(tmp_path):
    yml = tmp_path / "legal_metadata.yaml"
    yml.write_text(SIDECAR_YAML, encoding="utf-8")
    index = load_sidecar_index([str(yml)])

    md = tmp_path / "IT_Act.md"
    md.write_text(LEGAL_MD, encoding="utf-8")
    chunks = process_markdown(SourceSpec(path=str(md), doc_id="it_act",
                                         title="IT Act", doc_type="act"))
    n = enrich_chunks(chunks, "IT_Act.md", index)
    assert n == 1
    c = next(c for c in chunks if c.section_number == "66C")
    assert c.extra_metadata.get("statute_code") == "IT_ACT"
    assert c.extra_metadata.get("cognizable") is True
    assert "doc_ref" not in c.extra_metadata          # sidecar-only key dropped
    # Unmatched section gets nothing attached.
    assert next(c for c in chunks if c.section_number == "66D").extra_metadata == {}


def test_real_corpus_sidecar_join():
    """Integration: the shipped legal_metadata.yaml joins to IT_Act chunks."""
    md_path = "data/corpus/legal_repository/IT_Act.md"
    yaml_path = "data/corpus/legal_repository/legal_metadata.yaml"
    if not (os.path.exists(md_path) and os.path.exists(yaml_path)):
        return  # corpus not present in this checkout
    index = load_sidecar_index([yaml_path])
    chunks = process_markdown(SourceSpec(path=md_path, doc_id="it_act",
                                         title="IT Act", doc_type="act"))
    assert enrich_chunks(chunks, "IT_Act.md", index) >= 1


# 4. Retrieval routing --------------------------------------------------------
def test_new_doc_types_registered():
    assert "decision_tree" in DOC_TYPES and "recovery" in DOC_TYPES


def test_routing_includes_new_doc_types():
    assert "decision_tree" in _AREA_DOC_TYPES["investigation"]
    assert "recovery" in _AREA_DOC_TYPES["financial"]


# 6. Backward compatibility ---------------------------------------------------
def test_pdf_text_path_unchanged():
    """Non-markdown legal text still chunks via the section-based chunk_legal."""
    text = ("Section 66C. Punishment for identity theft.\n"
            "Whoever fraudulently uses another person's password shall be punished.\n")
    spec = SourceSpec(path="", doc_id="itact", title="IT Act", doc_type="act")
    via_doc = chunk_document(text, "itact", "IT Act", "act")  # is_markdown=False default
    via_legal = chunk_legal(text, "itact", "IT Act", "act")
    assert [c.section_number for c in via_doc] == [c.section_number for c in via_legal]
    assert any(c.section_number == "66C" for c in via_doc)


def test_process_text_default_is_not_markdown():
    spec = SourceSpec(path="", doc_id="itact", title="IT Act", doc_type="act")
    chunks = process_text("Section 1. Short title.\nThis Act may be called the IT Act.\n", spec)
    assert chunks and chunks[0].section_number == "1"
