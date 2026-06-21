"""Document-level sidecar binding for recovery metadata (audit Defect 1)."""
from __future__ import annotations

import os

from ingestion.pipeline import SourceSpec, process_markdown
from ingestion.sidecar import enrich_chunks, load_sidecar_index

RECOVERY_MD = """# NCRP Workflow

## Purpose
Register a complaint on NCRP.

## Step-by-Step Procedure
Call 1930 and file on NCRP.

## Escalation Path
Escalate to the state cyber nodal officer.
"""

RECOVERY_YAML = """schema_version: 1
collection: cchq_recovery_kb
sections:
  - point_id: 1
    doc_code: NCRP_WORKFLOW
    doc_title: "NCRP Workflow"
    recovery_stage: reporting
    channels: ["NCRP", "I4C", "1930"]
    asset_types: ["bank_funds", "upi"]
    crime_categories: ["UPI/Banking Fraud"]
    applicable_statutes: ["BNSS_173", "IT_ACT_66D"]
    escalation_to: ["state_cyber_nodal_officer", "i4c"]
    time_critical: true
    golden_hour: true
    cross_border: false
    source_grounded: true
    doc_ref: "data/corpus/recovery_repository/NCRP_Workflow.md"
"""

# A legal-style section sidecar, to prove section-level join still works.
LEGAL_MD = """# IT Act

### Section 66C — Identity theft

**Section Number:** 66C

Whoever fraudulently uses another's password.
"""
LEGAL_YAML = """schema_version: 1
sections:
  - point_id: 1
    statute_code: IT_ACT
    section_number: "66C"
    section_name: "Punishment for identity theft"
    cognizable: true
    doc_ref: "data/corpus/legal_repository/IT_Act.md"
"""

REQUIRED_FIELDS = [
    "recovery_stage", "channels", "asset_types", "crime_categories",
    "applicable_statutes", "time_critical", "golden_hour", "cross_border",
    "escalation_to",
]


def _ingest(tmp_path, md_name, md_text, yaml_text, doc_type):
    md = tmp_path / md_name
    md.write_text(md_text, encoding="utf-8")
    yml = tmp_path / "meta.yaml"
    yml.write_text(yaml_text, encoding="utf-8")
    spec = SourceSpec(path=str(md), doc_id="d", title="t", doc_type=doc_type)
    chunks = process_markdown(spec)
    index = load_sidecar_index([str(yml)])
    n = enrich_chunks(chunks, os.path.basename(md), index)
    return chunks, n


# 1. Document-level join by basename ------------------------------------------
def test_index_builds_document_level_bucket(tmp_path):
    yml = tmp_path / "meta.yaml"
    yml.write_text(RECOVERY_YAML, encoding="utf-8")
    index = load_sidecar_index([str(yml)])
    bucket = index["ncrp_workflow.md"]
    assert bucket["document"] is not None
    assert bucket["document"]["doc_code"] == "NCRP_WORKFLOW"
    assert bucket["sections"] == {}


# 2. Attach to EVERY recovery chunk -------------------------------------------
def test_every_recovery_chunk_enriched(tmp_path):
    chunks, n = _ingest(tmp_path, "NCRP_Workflow.md", RECOVERY_MD, RECOVERY_YAML, "recovery")
    assert n == len(chunks) > 1, "all recovery chunks should be enriched"
    for c in chunks:
        for field in REQUIRED_FIELDS:
            assert field in c.extra_metadata, f"{field} missing on {c.chunk_id}"


# 3. Metadata values land inside the chunk payload ----------------------------
def test_required_field_values(tmp_path):
    chunks, _ = _ingest(tmp_path, "NCRP_Workflow.md", RECOVERY_MD, RECOVERY_YAML, "recovery")
    c = chunks[0]
    md = c.extra_metadata
    assert md["recovery_stage"] == "reporting"
    assert "NCRP" in md["channels"]
    assert md["time_critical"] is True
    assert md["golden_hour"] is True
    assert md["cross_border"] is False
    assert "state_cyber_nodal_officer" in md["escalation_to"]
    assert "doc_ref" not in md  # dropped


# 4. to_dict() carries the payload (verifiable inside chunk record) -----------
def test_payload_serializes(tmp_path):
    chunks, _ = _ingest(tmp_path, "NCRP_Workflow.md", RECOVERY_MD, RECOVERY_YAML, "recovery")
    d = chunks[0].to_dict()
    assert d["extra_metadata"]["doc_code"] == "NCRP_WORKFLOW"


# 5. Backward compatibility: legal section-level join still works --------------
def test_legal_section_level_still_joins(tmp_path):
    chunks, n = _ingest(tmp_path, "IT_Act.md", LEGAL_MD, LEGAL_YAML, "act")
    enriched = [c for c in chunks if c.extra_metadata]
    assert n >= 1
    c66c = next(c for c in chunks if c.section_number == "66C")
    assert c66c.extra_metadata["statute_code"] == "IT_ACT"
    assert c66c.extra_metadata["cognizable"] is True


# 6. Real shipped corpus ------------------------------------------------------
def test_real_recovery_corpus_binds():
    md = "data/corpus/recovery_repository/NCRP_Workflow.md"
    yml = "data/corpus/recovery_repository/recovery_metadata.yaml"
    if not (os.path.exists(md) and os.path.exists(yml)):
        return
    chunks = process_markdown(SourceSpec(path=md, doc_id="ncrp", title="NCRP", doc_type="recovery"))
    index = load_sidecar_index([yml])
    n = enrich_chunks(chunks, "NCRP_Workflow.md", index)
    assert n == len(chunks) >= 1
    assert chunks[0].extra_metadata.get("doc_code") == "NCRP_WORKFLOW"
