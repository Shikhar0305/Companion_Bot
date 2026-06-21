# 5. Technology Stack Recommendation

Selection criteria, in priority order: **(1) data sovereignty / on-prem
capability, (2) answer quality & grounding, (3) auditability, (4) operational
maturity, (5) cost.**

## 5.1 Backend — FastAPI ✅

FastAPI is the right backend: async (good for I/O-bound retrieval + LLM calls),
Pydantic validation (enforces strict request/response and chunk schemas),
first-class in the Python ML/RAG ecosystem, easy OpenAPI + auth middleware, and
production-proven with Uvicorn/Gunicorn. Pair with Pydantic v2, `httpx`, and an
async task runner (Celery/RQ or `arq`) for ingestion jobs.

## 5.2 RAG framework — LangGraph ✅ (on LangChain primitives)

| Framework | Strengths | Weaknesses | Fit |
|---|---|---|---|
| **LangChain** | Huge connector ecosystem, quick to prototype | Chain abstraction is opaque/hard to audit for complex control flow | Use its loaders/splitters/clients as primitives |
| **LangGraph** | Explicit **stateful graph**, per-node control, retries, branching, checkpoints; ideal for guardrail→retrieve→rerank→generate→verify with **auditable state** | Slightly more boilerplate | **Recommended orchestrator** |
| **LlamaIndex** | Excellent retrieval/indexing abstractions, query engines, rerankers | Orchestration/guardrails less explicit than LangGraph | Optional: use its retrieval components inside LangGraph |

**Recommendation:** **LangGraph** as the orchestrator because this system's
defining requirement — a verifiable, auditable, multi-stage answer pipeline with
a hard grounding gate and abstention branch — maps directly onto a state graph.
Reuse LangChain loaders/clients and (optionally) LlamaIndex retrievers as
components. The graph's explicit state is also what makes every answer
reconstructable for audit.

## 5.3 Vector database — Qdrant ✅

| DB | Self-host | Hybrid (dense+sparse) | Metadata filtering | Notes |
|---|---|---|---|---|
| **Qdrant** | ✅ open-source, easy on-prem | ✅ native | ✅ rich, fast payload filters | Rust, performant, simple ops |
| **Weaviate** | ✅ | ✅ | ✅ | Capable; heavier, module model |
| **Chroma** | ✅ | partial | basic | Great for dev/POC, weaker at scale |
| **Pinecone** | ❌ managed/cloud only | ✅ | ✅ | Strong SaaS, but **off-prem — disqualifying for sensitive police data** as the default |

**Recommendation:** **Qdrant**, self-hosted. It satisfies the non-negotiable
on-prem requirement, supports the hybrid search and heavy metadata filtering the
RAG design depends on, and is operationally simple. Chroma is fine for local
development; Pinecone is excluded as the primary store because the data cannot
leave premises.

## 5.4 Embedding model — BGE-M3 ✅

| Model | Self-host | Multilingual (Hindi/Indic) | Hybrid | Notes |
|---|---|---|---|---|
| **BGE-M3** (`bge-m3`) | ✅ | ✅ strong | ✅ dense+sparse+ColBERT in one | **Recommended** |
| **E5 / multilingual-e5-large** | ✅ | ✅ | dense only | Strong alternative |
| **OpenAI text-embedding-3-large** | ❌ API | ✅ | dense only | Sends KB text off-prem — avoid for sensitive corpus |

**Recommendation:** **BGE-M3** — self-hostable (data stays on-prem), excellent
English + Hindi + Indic coverage (the corpus mixes English statutes with Hindi
in SOPs/advisories), and it emits **dense + sparse** vectors from one model,
which directly powers the hybrid retrieval in the RAG design. Pair with
**BGE-reranker-v2** (cross-encoder) for the rerank node.

## 5.5 LLM — recommendations by tier

Model facts (Anthropic, current):

| Model | ID | Context | Input $/1M | Output $/1M |
|---|---|---|---|---|
| Claude Opus 4.8 | `claude-opus-4-8` | 1M | $5.00 | $25.00 |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M | $3.00 | $15.00 |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200K | $1.00 | $5.00 |

Comparison across the requested candidates:

| Model | Grounding / instruction-following | Citations | Hosting | Verdict |
|---|---|---|---|---|
| **Claude Opus 4.8** | Best-in-class; excellent at "answer only from context / abstain" | **Native citation support** in the API | Cloud (no-retention org settings) | **Best quality** |
| **Claude Sonnet 4.6** | Excellent, ~Opus-class for grounded extraction | Native citations | Cloud | Strong mid-tier |
| **Claude Haiku 4.5** | Very good for grounded, templated answers | Native citations | Cloud | **Best budget** |
| GPT-5 | Strong general reasoning | Manual citation handling | Cloud | Capable alternative; weigh procurement/data terms |
| DeepSeek V3 | Strong, low-cost | Manual | Cloud or self-host | Good budget/self-host option |
| DeepSeek R1 | Strong reasoning | Manual | Cloud or self-host | Reasoning-heavy; higher latency |
| **Llama 3.3 70B Instruct** | Good with strong RAG prompting | Manual | **Self-host (vLLM)** | **Best self-hosted / air-gapped** |

**Recommendations:**
- **Best quality:** **Claude Opus 4.8** — the strongest at staying inside the
  provided context, refusing when unsupported, and producing verifiable
  citations (its native `citations` feature maps cited text to exact source
  spans, which the grounding verifier exploits). Use with no-retention settings
  for sensitive deployments.
- **Best budget:** **Claude Haiku 4.5** — cheap and fast; for grounded,
  template-shaped answers over already-retrieved passages, it is sufficient for
  the majority of queries. Route hard/ambiguous queries up to Opus 4.8.
- **Best self-hosted:** **Llama 3.3 70B Instruct** on local GPUs via **vLLM** —
  for fully air-gapped deployments where no data may leave premises. (DeepSeek
  V3 is a viable self-host alternative.) Accept a modest quality trade-off and
  lean harder on the retrieval + verification guardrails.

**Default production setup:** Haiku 4.5 for routine queries, **escalate to Opus
4.8** for low-confidence/complex ones (cost-aware routing). Offer the Llama 3.3
self-hosted profile for jurisdictions that mandate on-prem inference.

## 5.6 Supporting components

| Concern | Choice |
|---|---|
| OCR | OCRmyPDF + Tesseract (`eng+hin`); PaddleOCR PP-Structure / Docling for tables |
| PDF parsing | PyMuPDF |
| Reranker | BGE-reranker-v2 (cross-encoder) |
| Self-host LLM serving | vLLM |
| Object storage | MinIO (on-prem, S3-compatible) |
| Relational/audit store | PostgreSQL |
| Cache / rate limit | Redis |
| Async ingestion jobs | Celery / arq |
| Observability | OpenTelemetry + Prometheus + Grafana; LangSmith/Langfuse (self-host Langfuse for on-prem) |
| Secrets | HashiCorp Vault |
| Containerization | Docker + (optionally) Kubernetes |
| Eval | RAGAS + custom legal/SOP citation checks |

## 5.7 Stack summary

```
FastAPI  ──  LangGraph (orchestration)
            ├─ BGE-M3 embeddings + BGE-reranker
            ├─ Qdrant (hybrid vector search, metadata filters)
            ├─ LLM: Claude Opus 4.8 / Haiku 4.5  (or Llama 3.3 via vLLM, air-gapped)
            ├─ PostgreSQL (audit) · MinIO (docs) · Redis (cache)
            └─ OCR: Tesseract/PaddleOCR · Eval: RAGAS
```

Everything except the optional cloud LLM runs on-premises.
