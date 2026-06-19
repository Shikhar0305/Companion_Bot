# 9. Risk Assessment

Risks are scored **Likelihood × Impact** (Low/Med/High). The defining risk class
for this system is **incorrect legal/procedural guidance**, because the cost of
error is wrongful action, inadmissible evidence, or a derailed prosecution.

## 9.1 Accuracy & safety risks

| # | Risk | L | I | Mitigation |
|---|---|---|---|---|
| A1 | **Hallucinated legal section** reaches an officer | Med | **High** | Source-grounded RAG; **section-reference hard-gate verifier** (zero tolerance); native citations; abstain over guess; SME sign-off; adversarial near-miss eval |
| A2 | **Hallucinated / wrong SOP step** breaks chain of custody | Med | **High** | SOP-step verifier; procedure-boundary chunking; parent-context expansion; confidence labels; eval gate |
| A3 | Over-confident answer on weak evidence | Med | High | Reranker relevance floor; confidence scoring; "verify before acting" disclaimer |
| A4 | Fails to abstain on out-of-corpus question | Med | High | Relevance floor → abstain branch; adversarial abstention tests (≥95% target) |
| A5 | Stale KB after a law/SOP amendment | High | High | Versioned KB + governed delta-ingest; `effective_date`/`deprecated` metadata; answer cites version |
| A6 | OCR errors corrupt legal text → wrong citation | Med | High | Native-text first; human review of low-confidence OCR; citation-integrity validation; `eng+hin` |
| A7 | Retrieval misses the correct provision (low recall) | Med | High | Hybrid (dense+sparse) + RRF + query/alias expansion (IPC↔BNS, CrPC↔BNSS); recall@10 ≥ 90% gate |

## 9.2 Security & privacy risks

| # | Risk | L | I | Mitigation |
|---|---|---|---|---|
| S1 | Sensitive case data sent to external LLM | Med | **High** | On-prem default; no-retention LLM org settings; **air-gapped Llama 3.3 profile**; PII minimization in prompts |
| S2 | Unauthorized access to the assistant / KB | Med | High | SSO + RBAC (officer/analyst/supervisor/admin); mTLS; network isolation |
| S3 | Prompt injection (via query or via poisoned document) | Med | Med | Input guardrail/injection screening; KB is **curated & validated** (no open ingestion); treat retrieved text as data, not instructions |
| S4 | PII leakage into logs | Med | High | Structured logging with PII redaction; encrypted audit store; access controls on logs |
| S5 | Data at rest exposure | Low | High | Encryption at rest (Qdrant/Postgres/MinIO); secrets in Vault; backups encrypted |
| S6 | Insider misuse / unauditable actions | Low | High | Full per-answer audit trail; immutable logs; supervisor review |

## 9.3 Operational & data-quality risks

| # | Risk | L | I | Mitigation |
|---|---|---|---|---|
| O1 | Poor extraction of large scanned SOP (`SOPCCHQ.pdf`) | High | Med | PP-Structure/Docling for tables; manual review; golden-question validation before promote |
| O2 | Incorrect metadata tagging → wrong filters | Med | Med | Rules + classifier + SME review; validation suite |
| O3 | KB promotion regresses quality | Med | High | Promotion gated by golden-question + full eval; collection-alias rollback |
| O4 | LLM provider outage / latency | Med | Med | Model router fallback (Haiku↔Opus, or to self-host); retries with backoff; health checks |
| O5 | Hindi/multilingual content mishandled | Med | Med | BGE-M3 multilingual; `eng+hin` OCR; multilingual eval cases |
| O6 | Vector DB scaling / latency under load | Low | Med | Qdrant tuning, sharding; load tests; caching |

## 9.4 Compliance, legal & adoption risks

| # | Risk | L | I | Mitigation |
|---|---|---|---|---|
| C1 | Data-residency / procurement non-compliance | Med | High | On-prem architecture; air-gapped LLM option; documented data flows |
| C2 | Output mistaken for legal authority | Med | High | Mandatory disclaimer; confidence labels; training; "decision-support, not decision" framing |
| C3 | Officer over-reliance / deskilling | Med | Med | Citations force verification; supervisor review; positioned as assistant |
| C4 | Low adoption / distrust | Med | Med | Transparency (always show sources), pilot + UAT, accuracy track record, training |

## 9.5 Highest-priority risks (act first)

1. **A1/A2 — hallucinated legal/SOP references.** The hard-gate verifier +
   abstention + zero-tolerance eval is the single most important control.
2. **S1/C1 — data sovereignty.** On-prem default + air-gapped LLM resolves it;
   must be settled before any sensitive data is processed.
3. **A5/O1 — KB freshness & extraction quality.** Governed versioning + OCR
   review keep the source of truth correct.

## 9.6 Residual risk & governance

No system eliminates risk entirely. Residual risk is managed by: mandatory human
verification of cited sources before action, supervisor review of guidance in
significant cases, full auditability, and a continuous eval + feedback loop. A
named owner approves each KB version and reviews accuracy metrics on a schedule.
