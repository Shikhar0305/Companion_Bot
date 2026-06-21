# 7. Folder Structure

A production layout for the AI core (backend + RAG + KB pipeline + eval). Frontend
is intentionally omitted per scope.

```
Companion_Bot/
├── README.md
├── docs/                              # the 10 deliverables (this set)
│   ├── 01-problem-statement.md
│   ├── 02-solution-architecture.md
│   ├── 03-rag-architecture.md
│   ├── 04-knowledge-base-design.md
│   ├── 05-technology-stack.md
│   ├── 06-development-roadmap.md
│   ├── 07-folder-structure.md
│   ├── 08-cost-estimation.md
│   ├── 09-risk-assessment.md
│   └── 10-production-readiness-checklist.md
│
├── data/                             # NOT committed (gitignored); mounted from MinIO
│   ├── raw/                          # original source PDFs (BNS, BNSS, IT Act, SOPCCHQ, …)
│   ├── interim/                      # OCR + cleaned page JSON
│   ├── chunks/                       # chunked + metadata-tagged JSON, per kb_version
│   └── eval/                         # golden questions, labelled Q→chunk sets, adversarial
│
├── app/                              # FastAPI service (the chatbot API)
│   ├── main.py                       # app factory, router mounting
│   ├── config.py                     # settings (env-driven; LLM profile, thresholds)
│   ├── api/
│   │   ├── routes_ask.py             # POST /ask
│   │   ├── routes_feedback.py        # POST /feedback
│   │   ├── routes_sources.py         # GET /sources/{id}
│   │   ├── routes_admin.py           # POST /admin/ingest (RBAC: admin)
│   │   └── routes_health.py          # GET /health, /ready
│   ├── middleware/
│   │   ├── auth.py                   # SSO + RBAC
│   │   ├── audit.py                  # request/answer audit logging
│   │   └── ratelimit.py
│   ├── schemas/                      # Pydantic request/response + chunk models
│   └── deps.py                       # DI: vector store, llm, reranker, db
│
├── rag/                              # the answer graph (LangGraph)
│   ├── graph.py                      # assembles the state graph
│   ├── state.py                      # graph state (typed)
│   ├── nodes/
│   │   ├── guardrail.py              # scope + injection screening
│   │   ├── query_analysis.py         # classify, expand, build filters
│   │   ├── retrieve.py               # hybrid retrieval (Qdrant)
│   │   ├── rerank.py                 # BGE-reranker + relevance floor + parent expand
│   │   ├── generate.py              # grounded generation (frozen prompt, citations)
│   │   ├── verify.py                 # citation + section/SOP hard-gate verifier
│   │   ├── confidence.py             # confidence scoring
│   │   └── abstain.py                # "Information not found…" path
│   ├── prompts/
│   │   └── grounded_answer.v1.txt    # frozen, versioned system prompt
│   ├── retrievers/                   # hybrid search, RRF, filters
│   ├── rerankers/
│   └── llm/
│       ├── client.py                 # provider abstraction
│       ├── claude.py                 # Claude Opus 4.8 / Haiku 4.5 (+ native citations)
│       ├── vllm_llama.py             # self-hosted Llama 3.3 profile
│       └── router.py                 # cost-aware routing
│
├── ingestion/                        # offline KB pipeline
│   ├── pipeline.py                   # orchestrates the 5 stages
│   ├── extract/                      # PyMuPDF + OCR (Tesseract/PaddleOCR/Docling)
│   ├── clean/                        # normalization, OCR repair, header/footer strip
│   ├── chunk/                        # structure-aware chunkers per doc_type
│   ├── metadata/                     # schema, tagging rules, category classifier
│   ├── embed/                        # BGE-M3 embedding + Qdrant loader (versioned)
│   └── validate/                     # schema, completeness, citation-integrity, golden tests
│
├── eval/                             # evaluation harness
│   ├── retrieval_eval.py             # recall@k, MRR, nDCG
│   ├── answer_eval.py                # groundedness, citation accuracy, abstention (RAGAS+custom)
│   ├── adversarial.py                # out-of-corpus, near-miss, injection
│   └── report.py
│
├── core/                             # shared
│   ├── logging.py                    # structured logging, PII redaction
│   ├── audit_store.py                # PostgreSQL audit persistence
│   ├── security.py                   # crypto, redaction helpers
│   └── versioning.py                 # kb_version + collection alias management
│
├── infra/
│   ├── docker/                       # Dockerfiles (api, ingestion-worker, vllm)
│   ├── docker-compose.yml            # local: qdrant, postgres, redis, minio, app
│   ├── k8s/                          # manifests/helm for production
│   └── observability/                # otel, prometheus, grafana, langfuse configs
│
├── scripts/
│   ├── ingest_seed_corpus.py         # one-shot: ingest the 4 seed PDFs → kb_v1
│   ├── run_eval.py
│   └── promote_kb_version.py         # validate → switch alias
│
├── tests/                            # unit + integration (per node, per pipeline stage)
├── .env.example
├── pyproject.toml                    # deps, tooling (ruff, mypy, pytest)
└── .gitignore                        # excludes data/, secrets, model weights
```

## Notes

- **`data/` is never committed.** Source PDFs and chunk stores live in MinIO;
  only code + configs + docs are versioned. (The seed PDFs currently in the repo
  root would move into `data/raw/` and be gitignored in a real deployment.)
- **`rag/nodes/` mirrors the answer graph** in [RAG Architecture §3.3](03-rag-architecture.md)
  one file per node — keeping each node independently testable and auditable.
- **`rag/prompts/` is versioned and frozen** — prompt changes are reviewed like
  code and recorded in the audit trail.
- **`ingestion/` mirrors the 5-stage pipeline** in [KB Design §4.2](04-knowledge-base-design.md).
- **Separation of online vs offline:** `app/` + `rag/` serve requests;
  `ingestion/` + `eval/` run offline. They share `core/` and the schemas.
