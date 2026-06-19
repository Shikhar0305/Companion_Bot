# 6. Development Roadmap

Five phases over ~20 weeks (single small team: 1 ML/RAG engineer, 1 backend
engineer, part-time DevOps, plus a domain SME/legal reviewer). Timelines are
indicative; the **gates** between phases are the hard requirement.

## Phase 1 — Knowledge Base Creation (Weeks 1–5)

**Goal:** a validated, versioned KB from the seed corpus.

Milestones
- M1.1 Ingestion + OCR pipeline for the 4 seed PDFs (incl. OCR of `SOPCCHQ.pdf`).
- M1.2 Cleaning + structure-aware chunking (section-boundary for legal,
  procedure-boundary for SOP).
- M1.3 Metadata schema implemented; capability-area & cybercrime-category
  tagging (rules + classifier + SME review).
- M1.4 Validation suite (schema, completeness, citation integrity, golden
  questions) + SME sign-off → `kb_v1`.

Deliverables: ingestion code, `kb_v1` (chunk store), metadata schema, golden-
question set, validation report.

**Gate:** completeness check passes (every legal section present once);
citation-integrity sample ≥ 99%; SME sign-off.

Risks: OCR quality on `SOPCCHQ.pdf`; table extraction; Hindi text. *Mitigation:*
human review of low-confidence pages; PP-Structure/Docling for tables.

## Phase 2 — RAG Implementation (Weeks 5–9)

**Goal:** retrieval + grounded generation working with citations and abstention.

Milestones
- M2.1 BGE-M3 embedding + Qdrant load (dense+sparse, payload filters).
- M2.2 Hybrid retrieval + RRF + metadata filtering.
- M2.3 BGE-reranker + relevance floor + small-to-big parent expansion.
- M2.4 Grounded generation node (frozen prompt, native citations) + abstention.
- M2.5 Grounding/citation **verifier** (hard gate on legal/SOP references).

Deliverables: LangGraph answer graph, retrieval + generation services, verifier.

**Gate:** on the eval set — recall@10 ≥ 90%, groundedness ≥ 95% (interim),
zero hallucinated sections on the adversarial set.

Risks: low recall, weak abstention. *Mitigation:* query expansion, reranker
tuning, threshold calibration.

## Phase 3 — Chatbot Development (Weeks 9–13)

**Goal:** production API around the RAG core.

Milestones
- M3.1 FastAPI endpoints (`/ask`, `/feedback`, `/sources`, `/health`,
  `/admin/ingest`); strict Pydantic schemas.
- M3.2 Scope guardrail + injection screening node.
- M3.3 AuthN/AuthZ (SSO + RBAC), rate limiting, audit middleware.
- M3.4 Cost-aware model routing (Haiku 4.5 default → Opus 4.8 escalation);
  self-hosted Llama 3.3 profile behind a config flag.
- M3.5 Confidence scoring + response assembly (citations, confidence,
  disclaimer) + structured audit logging to PostgreSQL.

Deliverables: deployable API, auth, audit store, routing config.

**Gate:** end-to-end answer with citations + confidence + audit record; auth &
RBAC enforced; P95 latency within target on staging.

## Phase 4 — Evaluation & Testing (Weeks 13–17)

**Goal:** prove safety, accuracy, and robustness.

Milestones
- M4.1 Full eval harness (RAGAS + custom citation checks); expand labelled set
  to ≥ 300 Q→chunk pairs across all 5 capability areas and 20 categories.
- M4.2 Adversarial suite: out-of-corpus, near-miss sections, injection,
  multilingual — must abstain/refuse.
- M4.3 SME/legal review of a stratified answer sample; sign-off.
- M4.4 Load/perf testing; security review (see [Risk Assessment](09-risk-assessment.md)).
- M4.5 UAT with a pilot cyber cell.

Deliverables: eval report, adversarial results, security review, UAT findings.

**Gate (release gate):** all targets in [§1.7](01-problem-statement.md) met,
incl. **zero hallucinated legal/SOP references** and ≥ 95% correct abstention;
SME sign-off; security review passed.

## Phase 5 — Production Deployment (Weeks 17–20)

**Goal:** controlled rollout with monitoring and governance.

Milestones
- M5.1 Hardened deployment (containers, secrets in Vault, TLS/mTLS, backups,
  DR runbook).
- M5.2 Observability live (metrics, traces, dashboards, alerts).
- M5.3 Pilot rollout to one unit; feedback loop wired to eval set.
- M5.4 KB-update process operationalized (delta-ingest → validate → promote).
- M5.5 Phased wider rollout + on-call/runbooks + training for officers.

Deliverables: production environment, runbooks, monitoring, governance process,
training material.

**Gate:** [Production Readiness Checklist](10-production-readiness-checklist.md)
fully satisfied.

## Timeline at a glance

```
Wk:  1   3   5   7   9   11  13  15  17  19  20
P1  [=========]
P2          [========]
P3                  [=========]
P4                          [=========]
P5                                  [=======]
```

## Cross-phase deliverables
- Frozen, versioned grounded-answer prompt.
- Versioned KB with rollback.
- Continuously-growing eval + adversarial sets.
- Audit log of every answer from day one of staging.

## Top program risks (see [Risk Assessment](09-risk-assessment.md) for full register)
1. OCR/extraction quality of large scanned SOPs → bad chunks → bad answers.
2. Any hallucinated legal section reaching an officer → trust + legal exposure.
3. Data-residency/compliance for the LLM → resolved by on-prem Llama profile.
4. Stale KB after a law/SOP amendment → governed update process.
