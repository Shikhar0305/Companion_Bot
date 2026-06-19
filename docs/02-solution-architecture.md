# 2. Solution Architecture

## 2.1 Architectural principles

1. **Source-grounded by construction.** The LLM never answers from parametric
   memory alone. If the retriever returns nothing relevant, the system abstains.
2. **Citations are mandatory, not cosmetic.** Every sentence of substance maps
   to a retrieved passage with a verifiable locator (document → section → page).
3. **Defense in depth against hallucination.** Guardrails at input, retrieval,
   generation, and post-generation verification stages (see
   [RAG Architecture](03-rag-architecture.md)).
4. **Data sovereignty first.** Police/legal data is sensitive. The default
   deployment keeps the knowledge base, vector DB, and logs on-premises; the LLM
   is the only optionally-external component, and a fully air-gapped variant
   exists.
5. **Auditable and explainable.** Every answer is reconstructable from logs:
   query, retrieved chunks, prompt, model+version, citations, confidence.
6. **Human-in-command.** The bot supports the officer; it never decides.

## 2.2 Logical layers

```
┌──────────────────────────────────────────────────────────────────────┐
│  CLIENTS (web console / internal portal — out of scope for this doc)   │
└───────────────────────────────┬──────────────────────────────────────┘
                                 │ HTTPS (mTLS / SSO)
┌───────────────────────────────▼──────────────────────────────────────┐
│  API LAYER  — FastAPI                                                   │
│  • AuthN/AuthZ (SSO + RBAC: officer / analyst / supervisor / admin)     │
│  • Rate limiting, request validation, audit middleware                  │
│  • Endpoints: /ask  /feedback  /sources  /health  /admin/ingest         │
└───────────────────────────────┬──────────────────────────────────────┘
                                 │
┌───────────────────────────────▼──────────────────────────────────────┐
│  ORCHESTRATION  — LangGraph state machine (the "answer graph")          │
│   ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│   │ Guardrail│→│ Query     │→│ Hybrid   │→│ Rerank   │→│ Grounded   │  │
│   │ / scope  │ │ analysis  │ │ retrieval│ │ + filter │ │ generation │  │
│   └──────────┘ └───────────┘ └──────────┘ └──────────┘ └─────┬──────┘  │
│                                       ┌──────────────┐ ┌──────▼──────┐  │
│                                       │ Audit logger │←│ Grounding & │  │
│                                       │              │ │ citation    │  │
│                                       └──────────────┘ │ verifier    │  │
│                                                         └─────────────┘  │
└──────┬───────────────────────┬───────────────────────────┬────────────┘
       │                       │                            │
┌──────▼──────┐      ┌─────────▼─────────┐        ┌─────────▼──────────┐
│  Vector DB  │      │  Embedding +      │        │  LLM provider       │
│  (Qdrant)   │      │  Reranker service │        │  Claude API  OR     │
│  + metadata │      │  (BGE-M3 / BGE-   │        │  self-hosted vLLM   │
│  filtering  │      │   reranker)       │        │  (Llama 3.3)        │
└──────┬──────┘      └───────────────────┘        └────────────────────┘
       │
┌──────▼───────────────────────────────────────────────────────────────┐
│  KNOWLEDGE BASE PIPELINE (offline / admin-triggered)                    │
│  ingest → OCR → clean → structure-aware chunk → metadata tag →          │
│  embed → validate → load (versioned)                                    │
└───────────────────────────────────────────────────────────────────────┘
       ▲
┌──────┴──────┐
│  Object store (raw PDFs, processed JSON, chunk store, versions)         │
└─────────────┘
```

## 2.3 Request flow (the `/ask` path)

1. **Authenticate & authorize.** SSO identity, RBAC role, workspace.
2. **Audit-open.** A request record is created (request_id, user, timestamp).
3. **Guardrail / scope check.** Is this an in-domain cybercrime-investigation
   question? Off-domain (jokes, general chat, unrelated law) → polite refusal.
   Also screens prompt-injection attempts.
4. **Query analysis.** Classify capability area (legal / SOP / forensic / OSINT
   / financial), detect cybercrime category, expand query (synonyms, statute
   aliases, e.g. "BNS" ↔ "Bharatiya Nyaya Sanhita"), and decide metadata
   filters.
5. **Hybrid retrieval.** Dense (BGE-M3) + sparse (BM25/SPLADE) over Qdrant,
   filtered by `doc_type`, `category`, and `jurisdiction`.
6. **Rerank & filter.** Cross-encoder reranker (BGE-reranker) reorders; a
   relevance-score floor drops weak passages. If nothing clears the floor →
   abstain.
7. **Grounded generation.** Build a strict, cite-or-abstain prompt with only the
   surviving passages; call the LLM with low effort/temperature and **native
   citations enabled**.
8. **Grounding & citation verification.** Programmatically check that every
   citation maps to a real passage and that legal sections / SOP step numbers
   mentioned in the answer appear in the retrieved text. Any unverifiable
   legal/SOP reference → strip or abstain (hard gate).
9. **Confidence scoring.** Combine retrieval scores, reranker margin, and
   verification results into High / Medium / Low.
10. **Audit-close & respond.** Persist the full trace; return answer +
    citations + confidence + "verify before action" notice.

## 2.4 Capability modules

All five capability areas share one pipeline; they differ in **query
classification, metadata filters, and answer templates**:

| Module | Filters to | Answer template emphasizes |
|---|---|---|
| Investigation Guidance | SOPs, manuals | procedure, checklist, next steps |
| Legal Assistance | IT Act, BNS, BNSS, Sakshya | provision text, applicability, requirements |
| Digital Forensics | forensic manuals, SOP forensic sections | seizure, preservation, chain of custody, acquisition |
| OSINT | OSINT playbooks, manuals | domain/IP/email/social/username workflows |
| Financial Fraud | SOPs + RBI/NPCI/I4C advisories | freeze/trace workflow, transaction analysis, escalation |

## 2.5 Deployment topologies

| Topology | LLM | When to use |
|---|---|---|
| **On-prem + Cloud LLM** (recommended default) | Claude API over TLS, no-retention org settings | KB and logs stay on-prem; best answer quality |
| **Fully on-prem / air-gapped** | Llama 3.3 70B on local GPUs (vLLM) | Strict data-residency mandates; no external calls |
| **Hybrid** | Haiku 4.5 for routine, Opus 4.8 for hard | Cost/quality balance at scale |

Everything except the LLM (vector DB, embeddings, reranker, orchestration,
audit store) runs on-premises in all topologies.

## 2.6 Cross-cutting concerns

- **Security:** mTLS/SSO, RBAC, encryption at rest and in transit, secrets in a
  vault, PII redaction in logs. See [Risk Assessment](09-risk-assessment.md).
- **Observability:** structured logs, traces per graph node, retrieval/grounding
  metrics, dashboards, alerting.
- **Versioning:** KB is immutable + versioned; every answer records the KB
  version it used, so historical answers are reproducible.
- **Feedback loop:** officer/supervisor feedback feeds the eval set and
  retrieval tuning.
