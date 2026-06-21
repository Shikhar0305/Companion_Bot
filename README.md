# Cyber Crime Investigation Companion Bot

A production-grade, **source-grounded Retrieval-Augmented Generation (RAG)** chatbot
that assists Cyber Crime Investigation Officers, Police Personnel, Cyber Cells,
Digital Forensic Analysts, and Investigation Supervisors.

The system answers investigation, legal, forensic, OSINT, and financial-fraud
questions **only from an approved knowledge base** (SOPs, the IT Act 2000, BNS,
BNSS, Bharatiya Sakshya Adhiniyam, forensic manuals, and government advisories).
It is **not** a general-purpose chatbot — every answer is grounded in retrieved
source passages, cites those sources, declares a confidence level, and returns
**"Information not found in approved knowledge sources"** when the corpus does
not support an answer.

> ⚠️ **Decision-support tool, not a legal authority.** Outputs assist trained
> officers. Legal sufficiency, sanction, and charge framing remain with the
> investigating officer and prosecution. Every answer is auditable.

## Source corpus (already in this repository)

| File | Document | Role |
|---|---|---|
| `it_act_2000_updated.pdf` | Information Technology Act, 2000 (updated) | Legal provisions |
| `BNS.pdf` | Bharatiya Nyaya Sanhita | Substantive criminal law |
| `BNSS.pdf` | Bharatiya Nagarik Suraksha Sanhita | Procedural law |
| `SOPCCHQ.pdf` | Cyber Crime Investigation SOP (CCHQ) | Investigation procedures |

These are the seed documents for Phase 1 of the knowledge base. The
Bharatiya Sakshya Adhiniyam, forensic manuals, OSINT playbooks, and
CERT-In / I4C / RBI / NPCI advisories are added in later ingestion passes.

## Deliverables

The full design is documented in [`docs/`](docs/):

1. [Problem Statement](docs/01-problem-statement.md)
2. [Solution Architecture](docs/02-solution-architecture.md)
3. [RAG Architecture](docs/03-rag-architecture.md)
4. [Knowledge Base Design](docs/04-knowledge-base-design.md)
5. [Technology Stack Recommendation](docs/05-technology-stack.md)
6. [Development Roadmap](docs/06-development-roadmap.md)
7. [Folder Structure](docs/07-folder-structure.md)
8. [Cost Estimation](docs/08-cost-estimation.md)
9. [Risk Assessment](docs/09-risk-assessment.md)
10. [Production Readiness Checklist](docs/10-production-readiness-checklist.md)

## Running the code

The implementation lives alongside the docs (see [docs/07](docs/07-folder-structure.md)).
The testable core (`core/`, `rag/`, `ingestion/`, `eval/`) runs on **pure stdlib**;
production backends (Qdrant, BGE, Claude/Llama, FastAPI) are lazily imported and
selected via env vars. Default profile = `stub` LLM + in-memory store + hashing
embedder, so it boots with zero external services.

```bash
# Tests (pure stdlib + pytest)
pip install pytest && python -m pytest -q

# Evaluation harness against a seeded demo KB (enforces the release gate)
PYTHONPATH=. python scripts/run_eval.py

# Run the API (dev profile — no external services)
pip install fastapi uvicorn pydantic
uvicorn app.main:app --reload
#   POST /ask        {"query": "..."}
#   GET  /health  /ready  /sources/{chunk_id}   POST /feedback  /admin/ingest

# Ingest the real seed PDFs into a KB version (needs the ocr extra)
pip install ".[ocr,vectordb,embeddings]"
EMBEDDER=bge VECTOR_STORE=qdrant python scripts/ingest_seed_corpus.py
```

Switch to production backends with env vars (see `.env.example`):
`EMBEDDER=bge VECTOR_STORE=qdrant RERANKER=bge LLM_PROFILE=claude` (or
`LLM_PROFILE=vllm` for the air-gapped Llama 3.3 profile). Full local stack:
`docker compose -f infra/docker-compose.yml up`.

The safety guarantees from the design are enforced in code: the grounding
hard-gate verifier (`rag/nodes/verify.py`) abstains on any hallucinated
legal/SOP reference, queries naming a section the KB lacks abstain, off-domain
and injection inputs are refused, and every answer is written to an audit trail.

## Headline design choices

| Area | Choice | Why |
|---|---|---|
| RAG framework | **LangGraph** (on LangChain primitives) | Auditable, stateful graph with explicit guardrail / grounding / citation nodes |
| Vector DB | **Qdrant** (self-hosted) | On-prem data sovereignty, hybrid search, strong metadata filtering |
| Embeddings | **BGE-M3** (`bge-m3`) | Self-hostable, multilingual (English + Hindi + Indic), dense+sparse hybrid |
| LLM — quality | **Claude Opus 4.8** (`claude-opus-4-8`) | Best grounding/instruction-following; native citation support |
| LLM — budget | **Claude Haiku 4.5** (`claude-haiku-4-5`) | Cheap, fast, sufficient for grounded extraction |
| LLM — self-hosted | **Llama 3.3 70B Instruct** | Air-gapped deployments where data cannot leave premises |
| Backend | **FastAPI** | Async Python, first-class with the ML/RAG ecosystem |

See [docs/05-technology-stack.md](docs/05-technology-stack.md) for the full
comparison and rationale.
