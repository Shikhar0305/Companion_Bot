# 8. Cost Estimation

All figures are planning estimates (USD). Two cost centers: **one-time build**
and **recurring run**. LLM is the main variable; everything else is largely fixed
infrastructure. Convert to INR at procurement time.

## 8.1 Pricing inputs (Claude API, current)

| Model | ID | Input $/1M tok | Output $/1M tok |
|---|---|---|---|
| Claude Opus 4.8 | `claude-opus-4-8` | $5.00 | $25.00 |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | $3.00 | $15.00 |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1.00 | $5.00 |

Self-hosted (Llama 3.3) has **no per-token fee** — cost is GPU hardware/hosting.

## 8.2 Per-query token model (assumption)

A grounded answer supplies ~6 reranked passages as context.

| Item | Tokens |
|---|---|
| System prompt (frozen) + query | ~1,000 |
| Retrieved context (≈6 passages, parents expanded) | ~6,000 |
| **Input total** | **~7,000** |
| Answer output (structured + citations) | ~700 |

**Prompt caching** of the frozen system prompt cuts input cost; the variable
context dominates. Estimates below are conservative (no cache discount applied).

### Per-query LLM cost

| Model | Input cost | Output cost | **Per query** |
|---|---|---|---|
| Haiku 4.5 | 7,000 × $1/1M = $0.0070 | 700 × $5/1M = $0.0035 | **≈ $0.011** |
| Sonnet 4.6 | $0.021 | $0.0105 | **≈ $0.032** |
| Opus 4.8 | $0.035 | $0.0175 | **≈ $0.053** |

## 8.3 Recurring LLM cost by volume (routing: 80% Haiku, 20% Opus)

Blended per-query ≈ 0.8×$0.011 + 0.2×$0.053 = **$0.019**.

| Monthly queries | Haiku-only | 80/20 blend | Opus-only |
|---|---|---|---|
| 10,000 | $110 | **$190** | $530 |
| 50,000 | $550 | **$950** | $2,650 |
| 200,000 | $2,200 | **$3,800** | $10,600 |

LLM cost scales linearly and remains modest. Prompt caching + tighter context
can cut this 30–50%.

## 8.4 Infrastructure (self-hosted, monthly)

On-prem or cloud VMs; embeddings + reranker run on a shared GPU.

| Component | Spec | Est. monthly |
|---|---|---|
| App servers (FastAPI) | 2× 4 vCPU / 16 GB | $150 |
| Qdrant | 8 vCPU / 32 GB + SSD | $200 |
| PostgreSQL (audit) | 4 vCPU / 16 GB + backups | $120 |
| Redis | small | $40 |
| MinIO (object store) | 1 TB | $80 |
| GPU for embeddings + reranker (BGE-M3, BGE-reranker) | 1× L4/A10 (shared, batchable) | $400 |
| Observability (Prometheus/Grafana/Langfuse) | small | $80 |
| **Subtotal (cloud-LLM topology)** | | **≈ $1,070 / mo** |

### Air-gapped LLM add-on (Llama 3.3 70B via vLLM)
Replaces the Claude API spend with GPU capacity:

| Component | Spec | Est. monthly |
|---|---|---|
| LLM inference GPUs | 2× A100 80GB (or 4× L40S) for 70B at usable throughput | $3,000–$6,000 (cloud) / amortized capex on-prem |

For owned hardware on-prem, treat as capex (~$30k–$60k for a 70B-capable node)
amortized over 3 years ≈ $850–$1,700/mo, plus power/cooling/ops.

## 8.5 One-time build cost

| Item | Estimate |
|---|---|
| Team (≈20 weeks): 1 ML/RAG + 1 backend + part-time DevOps | dominant line item (staff) |
| SME/legal reviewer time (KB tagging + answer sign-off) | part-time across project |
| OCR/processing compute for initial corpus | one-time GPU/CPU, low ($ hundreds) |
| Security review / pen test | $ one-off engagement |

Staff cost dominates the build; compute for the initial KB build is negligible
relative to it.

## 8.6 Cost-control levers

1. **Model routing** — Haiku 4.5 default, escalate to Opus 4.8 only on
   low-confidence/complex queries (the 80/20 blend above).
2. **Prompt caching** — cache the frozen system prompt and any stable preamble
   (~90% cheaper on the cached prefix; the system prompt is byte-stable by
   design).
3. **Tight context** — reranker + relevance floor already minimize passages sent.
4. **Batch ingestion** — embed offline on a shared GPU; no real-time embedding
   cost in the hot path beyond the query embedding.
5. **Self-host embeddings/reranker** — no per-call API fee (already in the design).

## 8.7 Indicative total cost of ownership

| Scenario (50k queries/mo) | Monthly run |
|---|---|
| Cloud LLM, 80/20 routing | ~$1,070 infra + ~$950 LLM ≈ **$2,020 / mo** |
| Cloud LLM, Haiku-only | ~$1,070 + ~$550 ≈ **$1,620 / mo** |
| Air-gapped (Llama 3.3, owned GPUs amortized) | ~$1,070 + ~$1,200 ≈ **$2,270 / mo** (no per-token fee; capex-driven) |

LLM spend is the controllable variable; infrastructure is a stable floor. Even
at 200k queries/month the system stays comfortably economical with routing +
caching.
