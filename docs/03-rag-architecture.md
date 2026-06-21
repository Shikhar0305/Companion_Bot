# 3. RAG Architecture

This is the heart of the system. The pipeline has two halves: an **offline
ingestion pipeline** that builds the knowledge base, and an **online retrieval +
generation pipeline** that answers questions. Both are described here; the
ingestion details are expanded in [Knowledge Base Design](04-knowledge-base-design.md).

## 3.1 Why RAG (and not fine-tuning)

| Requirement | RAG | Fine-tuning |
|---|---|---|
| Cite exact source for every claim | ✅ native | ❌ |
| Update when a law/SOP changes | ✅ re-ingest | ❌ retrain |
| Abstain when unknown | ✅ (empty retrieval) | ❌ confident-wrong |
| Auditability | ✅ retrieved chunks logged | ❌ opaque weights |
| Zero hallucinated sections | ✅ verifiable | ❌ |

RAG is mandatory here. Fine-tuning is optional later, only for *style/format*
of answers — never for facts.

## 3.2 Offline ingestion pipeline

```
PDF/source ─▶ Document ─▶ OCR ─▶ Clean ─▶ Structure-aware ─▶ Metadata ─▶ Embed ─▶ Validate ─▶ Load
              ingestion    (if      &       chunking          tagging      (dense   (QA gate)   (Qdrant,
                          scanned) normalize                              +sparse)            versioned)
```

### 3.2.1 Document ingestion
- Register each source with provenance: title, issuing authority, version/date,
  `doc_type` (`act` | `sanhita` | `sop` | `manual` | `advisory` | `circular`),
  jurisdiction, and a content hash.
- Store the raw file immutably in object storage.

### 3.2.2 OCR pipeline
- Detect whether a PDF has a usable text layer. The repository's `BNS.pdf`,
  `BNSS.pdf`, and `it_act_2000_updated.pdf` are mostly digital text;
  `SOPCCHQ.pdf` (26 MB) is large and likely contains scanned pages, tables, and
  screenshots — it needs OCR.
- Engine: **PyMuPDF** for native text; **OCRmyPDF + Tesseract** (English +
  Hindi: `eng+hin`) for scanned pages; a layout/table model
  (**PaddleOCR PP-Structure** or **Docling**) for tables and multi-column SOP
  pages.
- Preserve page numbers and bounding boxes — these become citation locators.
- Flag low-confidence OCR pages for human review (do not silently trust them).

### 3.2.3 Data cleaning
- Strip headers/footers, watermarks, repeated boilerplate, page-number noise.
- Normalize whitespace, ligatures, hyphenation across line breaks.
- Repair OCR artifacts with a dictionary + regex pass (e.g. "Sec1ion" → "Section").
- Keep an original ↔ cleaned mapping so citations still point to true pages.

### 3.2.4 Structure-aware chunking (the most important step)
Generic fixed-size chunking destroys legal/SOP meaning. Use **document-type-aware
chunking**:

- **Legal acts/sanhitas** — chunk by **section/clause boundary**, never split a
  section mid-sentence. One chunk ≈ one section (with sub-clauses), carrying
  `section_number`, `section_title`, `chapter`. Long sections are split into
  sub-clause chunks that retain the parent section reference.
- **SOPs/manuals** — chunk by **heading hierarchy** (procedure → step group),
  keeping a step list intact within a chunk where possible; carry
  `sop_section`, `procedure_name`, `step_range`.
- **Advisories/circulars** — chunk by labelled paragraph / numbered item.
- **Tables** — keep a table as one chunk (markdown), with a text caption.
- Target ~300–600 tokens/chunk with ~15% overlap **only across non-atomic
  boundaries**; atomic units (a legal section, a single SOP step) are never split.
- **Parent-child indexing:** embed small precise chunks for retrieval but store a
  pointer to the larger parent (full section / full procedure) so generation
  receives complete context ("small-to-big" retrieval).

### 3.2.5 Metadata tagging
Each chunk carries (see full schema in [KB Design](04-knowledge-base-design.md)):
`doc_id, doc_type, title, issuing_authority, version, effective_date,
section_number, section_title, chapter, page_start, page_end, capability_area,
cybercrime_categories[], jurisdiction, language, source_hash`.

Metadata powers **filtered retrieval** (e.g. legal queries → `doc_type in
{act,sanhita}`) and **precise citations**.

### 3.2.6 Embedding generation
- **BGE-M3** for dense vectors (multilingual, English+Hindi+Indic, 1024-dim) and
  its sparse (lexical) output for hybrid search in one model.
- Batch on GPU; store dense + sparse vectors + payload (metadata + chunk text +
  parent pointer) in Qdrant.

### 3.2.7 Validation (QA gate before load)
- Schema validation on every chunk's metadata.
- Coverage check: every section of every act/sanhita present exactly once.
- Spot-check retrieval: a fixed set of "golden questions" must retrieve the
  correct chunk before the new KB version is promoted.
- Section-citation integrity test: random sample of chunks — does
  `section_number` actually match the chunk text?

### 3.2.8 Load & versioning
- Load into a **new Qdrant collection version** (`kb_v3`), run the golden-question
  eval, then atomically switch an alias. Old versions retained for rollback and
  for reproducing historical answers.

## 3.3 Online retrieval + generation (LangGraph)

The answer graph nodes (each is independently testable and logged):

### Node 1 — Guardrail / scope
- Reject off-domain and prompt-injection inputs. Lightweight: classifier +
  rules, optionally a small LLM call. Returns a refusal for non-cybercrime-
  investigation questions.

### Node 2 — Query analysis & rewriting
- Classify capability area + cybercrime category.
- Expand statute aliases ("IPC→BNS mapping", "Sec 66D IT Act"), spelling, Hindi
  terms.
- Produce: rewritten query, metadata filter set, and (optionally) a multi-query
  fan-out for recall.

### Node 3 — Hybrid retrieval
- Qdrant hybrid search: dense (BGE-M3) + sparse, fused with **Reciprocal Rank
  Fusion**, constrained by metadata filters. Retrieve top-k (e.g. 20).

### Node 4 — Rerank & relevance gate
- **BGE-reranker** cross-encoder reorders the 20 → keep top-n (e.g. 6).
- **Relevance floor:** drop any passage below a calibrated score. If fewer than
  *m* passages survive → route to **Abstain**.
- Expand survivors to their **parent chunks** (small-to-big).

### Node 5 — Grounded generation
- Strict system prompt (see §3.4) + only the surviving passages.
- LLM call with **native citations enabled** (Claude `citations`), low effort,
  `max_tokens` sized for structured answers.
- Output: answer text with inline citation references to the supplied passages.

### Node 6 — Grounding & citation verifier (hard gate)
- Verify every citation references a real supplied passage.
- Extract every **legal section** and **SOP step/section** mentioned in the
  answer; confirm each appears in a cited passage. Any unsupported legal/SOP
  reference → **strip the claim or abstain** (zero-tolerance rule).
- Optional NLI/LLM-judge entailment check: does each answer sentence follow from
  its cited passage?

### Node 7 — Confidence + assembly
- Confidence = f(reranker top score, score margin, # supporting passages,
  verifier pass rate) → High / Medium / Low.
- Attach citations (doc, section, page), confidence, KB version, and the
  standard "verify before acting" disclaimer.

### Node 8 — Audit logger
- Persist the entire trace (query, filters, retrieved IDs+scores, prompt,
  model+version, raw output, verifier results, final answer, citations,
  confidence, latency) keyed by request_id.

## 3.4 Hallucination-reduction mechanisms (defense in depth)

| Stage | Mechanism |
|---|---|
| Input | Scope guardrail; injection screening |
| Retrieval | Hybrid search + metadata filters → high recall of the *right* docs |
| Filtering | Reranker + relevance floor → only strongly-relevant context |
| Prompting | "Answer **only** from context; if absent, say *Information not found in approved knowledge sources*; cite every claim; never invent sections" |
| Generation | Low temperature/effort; native citations; supply only vetted passages |
| Verification | Citation-existence check + **section/SOP-reference verification (hard gate)** + optional NLI entailment |
| Output | Confidence label; mandatory disclaimer; abstain over guess |
| Offline | Golden-question eval before every KB promotion; continuous eval set |

## 3.5 The grounded-answer prompt (essence)

System prompt (abridged):

> You are an assistant for cybercrime investigation officers. Answer **only**
> using the numbered SOURCE PASSAGES provided. For every factual statement,
> legal provision, or procedural step, cite the source passage it comes from.
> **Never** state a legal section number, Act/Sanhita name, or SOP step that is
> not present in the provided passages. If the passages do not contain the
> answer, respond exactly: "Information not found in approved knowledge
> sources." Do not use outside knowledge. Be precise and procedural. End with a
> reminder that the officer must verify against the cited source before acting.

This prompt is **frozen and version-controlled** (it is part of the audit trail
and prompt cache key).

## 3.6 Evaluation harness

- **Retrieval:** recall@k, MRR, nDCG on a labelled query→chunk set.
- **Answer:** groundedness/faithfulness, citation accuracy, answer relevance,
  correct-abstention rate (RAGAS-style + custom legal/SOP citation checks).
- **Adversarial:** out-of-corpus questions, near-miss sections, injection
  attempts — must abstain/refuse.
- **Regression gate:** no KB version or prompt/model change ships unless eval
  scores meet thresholds in [Problem Statement §1.7](01-problem-statement.md).
