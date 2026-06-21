# 10. Production Readiness Checklist

The release gate. Ship only when every **[BLOCKER]** is satisfied; **[SHOULD]**
items are strongly recommended before wide rollout.

## 10.1 Knowledge base

- [ ] **[BLOCKER]** All in-scope sources ingested (IT Act, BNS, BNSS, Bharatiya
      Sakshya Adhiniyam, Cyber Crime SOP, forensic/OSINT/financial advisories).
- [ ] **[BLOCKER]** Completeness check passes (every legal section present
      exactly once; no gaps/dupes).
- [ ] **[BLOCKER]** Citation-integrity sample ≥ 99% (section/page matches text).
- [ ] **[BLOCKER]** SME/legal reviewer sign-off on `kb_vN`.
- [ ] **[BLOCKER]** KB is versioned with rollback (collection alias) and every
      answer records `kb_version`.
- [ ] [SHOULD] OCR low-confidence pages reviewed; tables validated.
- [ ] [SHOULD] Cybercrime-category & capability-area coverage report reviewed.

## 10.2 RAG quality (eval gate)

- [ ] **[BLOCKER]** Retrieval recall@10 ≥ 90% on the labelled set.
- [ ] **[BLOCKER]** Groundedness/faithfulness ≥ 98%.
- [ ] **[BLOCKER]** Citation accuracy ≥ 99% (legal), ≥ 97% (SOP).
- [ ] **[BLOCKER]** **Zero hallucinated legal/SOP references** on the adversarial
      set (hard requirement).
- [ ] **[BLOCKER]** Correct abstention ≥ 95% on out-of-corpus questions.
- [ ] **[BLOCKER]** Grounding/citation **verifier hard-gate** active in the path.
- [ ] [SHOULD] Multilingual (English/Hindi) eval cases pass.
- [ ] [SHOULD] Eval harness runs in CI; regression gate blocks bad promotions.

## 10.3 Application & API

- [ ] **[BLOCKER]** Frozen, version-controlled grounded-answer prompt in use.
- [ ] **[BLOCKER]** Scope guardrail + prompt-injection screening active.
- [ ] **[BLOCKER]** Every response returns citations + confidence + disclaimer.
- [ ] **[BLOCKER]** Strict request/response schema validation (Pydantic).
- [ ] [SHOULD] Cost-aware model routing (Haiku→Opus) configured & tested.
- [ ] [SHOULD] Self-hosted Llama 3.3 profile validated for air-gapped sites.

## 10.4 Security & privacy

- [ ] **[BLOCKER]** SSO + RBAC (officer/analyst/supervisor/admin) enforced.
- [ ] **[BLOCKER]** TLS in transit; encryption at rest (Qdrant, Postgres, MinIO).
- [ ] **[BLOCKER]** Secrets in Vault; none in code/images/logs.
- [ ] **[BLOCKER]** PII redaction in logs; audit store access-controlled.
- [ ] **[BLOCKER]** Data-residency decision documented; LLM data-handling terms
      (no-retention) confirmed, or air-gapped profile selected.
- [ ] **[BLOCKER]** Security review / pen test passed.
- [ ] [SHOULD] Network isolation between tiers; rate limiting active.

## 10.5 Auditability & explainability

- [ ] **[BLOCKER]** Every answer logs: query, filters, retrieved IDs+scores,
      prompt, model+version, raw output, verifier results, final answer,
      citations, confidence, latency, user, `kb_version`.
- [ ] **[BLOCKER]** Audit records immutable and retained per policy.
- [ ] [SHOULD] Admin tooling to replay/inspect any historical answer.

## 10.6 Observability & reliability

- [ ] **[BLOCKER]** Health/readiness endpoints; metrics (latency, retrieval,
      grounding, abstention rate); alerting on error/latency/abstention spikes.
- [ ] **[BLOCKER]** LLM provider failure handling (fallback/retry/backoff).
- [ ] **[BLOCKER]** Backups (KB, audit DB) + tested restore; DR runbook.
- [ ] [SHOULD] Per-node tracing (LangGraph) wired to dashboards.
- [ ] [SHOULD] Load test meets P95 latency target at expected concurrency.

## 10.7 Governance & operations

- [ ] **[BLOCKER]** Named owner approves each KB version.
- [ ] **[BLOCKER]** KB-update process operational (delta-ingest → validate →
      promote → record).
- [ ] **[BLOCKER]** Incident & rollback runbooks (KB rollback, model rollback).
- [ ] [SHOULD] Feedback loop (officer/supervisor) feeds the eval set.
- [ ] [SHOULD] Scheduled accuracy review of sampled production answers.
- [ ] [SHOULD] Officer training delivered; "decision-support, not authority"
      framing communicated.

## 10.8 Documentation

- [ ] [SHOULD] Architecture, runbooks, API reference, KB-update SOP, and on-call
      guide complete and current.
- [ ] [SHOULD] User guide covering how to read citations, confidence, and the
      abstention response.

## 10.9 Go / No-Go

**GO** only when: all KB, RAG-quality, application, security, auditability, and
observability **[BLOCKER]** items pass; SME and security sign-offs are in hand;
and the adversarial suite shows **zero hallucinated legal/SOP references** with
≥ 95% correct abstention. Otherwise **NO-GO**.
