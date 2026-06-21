# 4. Knowledge Base Design

The knowledge base (KB) is the single source of truth. Its quality bounds the
quality of every answer. This document specifies how raw documents become a
production-ready, queryable, citable KB.

## 4.1 Source taxonomy

| `doc_type` | Examples in/for this project | Chunking strategy |
|---|---|---|
| `act` | IT Act 2000 (`it_act_2000_updated.pdf`) | by section/clause |
| `sanhita` | BNS (`BNS.pdf`), BNSS (`BNSS.pdf`), Bharatiya Sakshya Adhiniyam | by section/clause |
| `sop` | Cyber Crime SOP (`SOPCCHQ.pdf`), investigation SOPs | by heading/procedure/step |
| `manual` | Digital forensics manuals, investigation manuals | by heading hierarchy |
| `playbook` | Cyber-fraud playbooks, OSINT methodologies | by workflow/step |
| `advisory` | CERT-In, I4C, RBI, NPCI guidelines | by numbered item/paragraph |
| `circular` | Police circulars | by paragraph |

## 4.2 End-to-end conversion pipeline

For each capability question — "how do I convert SOP PDFs / manuals / legal
documents / handbooks into a production KB?" — the answer is the same five-stage
pipeline, with type-specific settings.

### Stage 1 — Extraction
- **Native-text PDFs** (BNS, BNSS, IT Act): extract with **PyMuPDF**, keeping
  page numbers, font/size hints (to detect headings), and reading order.
- **Scanned/mixed PDFs** (the large `SOPCCHQ.pdf`): run **OCRmyPDF/Tesseract
  `eng+hin`**; use **PaddleOCR PP-Structure** or **Docling** for tables,
  multi-column layouts, and figures. Retain page + bounding-box for citations.
- **Output:** structured per-page text + layout JSON, with provenance.

### Stage 2 — Cleaning
- Remove repeating headers/footers, watermarks, page numbers, gazette boilerplate.
- De-hyphenate across line breaks; normalize Unicode, spacing, quotes, bullets.
- OCR repair: regex + dictionary + (optional) small-LLM correction on
  low-confidence pages only, always reviewable.
- Language tag per block (`en`/`hi`), preserving Hindi where present.

### Stage 3 — Chunking (structure-aware)
Detect document structure first (regex for "Section \d+", "(\d+)", chapter
headings, SOP heading patterns), then chunk on those boundaries:

- **Legal:** one chunk per section (with its sub-clauses). Never split a section
  across chunks; if a section is very long, split by sub-clause but stamp every
  child with the parent `section_number`.
- **SOP/manual:** chunk per procedure or step-group under a heading; keep a
  procedure's steps together where size permits.
- **Tables:** one chunk each (markdown), plus a one-line text summary for recall.
- **Parent-child:** index a small "retrieval chunk" but keep a pointer to the
  full "context chunk" (whole section / whole procedure) used at generation time.
- Token target 300–600; overlap only across non-atomic boundaries.

### Stage 4 — Metadata creation
Attach the canonical metadata schema (§4.3) to every chunk. Capability area and
cybercrime categories are assigned by rules + a classifier and **reviewed**.

### Stage 5 — Validation
- **Schema** validation (required fields present, types correct).
- **Completeness:** for acts/sanhitas, assert every section number in the
  document appears exactly once (no gaps, no dupes).
- **Citation integrity:** sample chunks; verify `section_number`/`page` match the
  text.
- **Golden-question retrieval test** before promotion (see [RAG §3.2.7](03-rag-architecture.md)).
- **Sign-off:** a legal/SME reviewer approves the KB version before it goes live.

## 4.3 Chunk metadata schema

```jsonc
{
  "chunk_id": "bns_sec_318_c2",
  "doc_id": "bns_2023",
  "doc_type": "sanhita",                 // act|sanhita|sop|manual|playbook|advisory|circular
  "title": "Bharatiya Nyaya Sanhita, 2023",
  "issuing_authority": "Government of India",
  "version": "2023",
  "effective_date": "2024-07-01",
  "language": "en",
  "chapter": "Chapter XVII — Offences Against Property",
  "section_number": "318",
  "section_title": "Cheating",
  "sop_section": null,                    // for SOP/manual chunks
  "procedure_name": null,
  "step_range": null,
  "capability_area": ["legal"],          // legal|investigation|forensics|osint|financial
  "cybercrime_categories": ["upi_fraud", "ecommerce_fraud", "identity_theft"],
  "jurisdiction": "IN",
  "page_start": 142,
  "page_end": 143,
  "parent_chunk_id": "bns_sec_318_full", // small-to-big pointer
  "source_hash": "sha256:…",
  "text": "..."                          // cleaned chunk text
}
```

## 4.4 Cybercrime-category facet

The 20 supported categories (Phishing … Online Gaming Fraud) are an enumerated
facet on every chunk. This enables:
- **Category-scoped retrieval** (a UPI-fraud question prioritizes UPI/financial chunks).
- **Per-category playbooks** assembled from the relevant SOP/advisory chunks.
- **Coverage analytics** — which categories are under-documented in the KB.

## 4.5 Versioning & lifecycle

- KB is **immutable + versioned**. Each ingestion produces `kb_vN`.
- Promotion is gated by the validation suite; switch via a collection alias.
- Every answer records the `kb_version` it used → historical reproducibility.
- Law/SOP updates (amendments, new advisories) trigger a delta-ingest and a new
  version; superseded provisions are marked `deprecated` but retained.

## 4.6 Handling the actual seed corpus

| File | Notes for ingestion |
|---|---|
| `it_act_2000_updated.pdf` (~0.8 MB) | Native text; section-boundary chunking; tag amendments. |
| `BNS.pdf` (~1.3 MB) | Native text; section/chapter chunking; map common IPC→BNS equivalents in metadata for query expansion. |
| `BNSS.pdf` (~2.0 MB) | Native text; procedural sections; map CrPC→BNSS equivalents. |
| `SOPCCHQ.pdf` (~26 MB) | Large; **OCR required** for scanned pages, tables, screenshots; heading/procedure chunking; rich `cybercrime_categories` + `capability_area` tagging; this is the primary procedural/forensic/OSINT/financial source. |

To add later: **Bharatiya Sakshya Adhiniyam** (evidence law — critical for
admissibility answers), digital-forensics manuals, OSINT playbooks, and
CERT-In / I4C / RBI / NPCI advisories.

## 4.7 Quality bar

A chunk is "production-ready" only if: it is a coherent semantic unit, has
complete and correct metadata, carries a verifiable citation locator, and
retrieves correctly for its golden question. The validation suite enforces all
four before any version is promoted.
