# 11. Integration-v1 Audit & Roadmap

Repository audit of branch `integration-v1` (`245cdcb`) and a roadmap from the
current benchmark to production readiness for a UP Cyber Crime pilot.

> **Read this caveat first.** The headline **85.4%** regression figure is measured
> with the dependency-free `hash` embedder — a lexical bag-of-words toy — not the
> production `e5`/`bge` model, and generation is the `StubLLM` (which copies
> passage snippets), not a real LLM. Treat 85.4% as a **routing-logic floor**, not
> a production accuracy number. Establishing the real numbers is Phase A of the
> roadmap and unblocks everything else.

---

## 1. Current Architecture

Python 3.11 · FastAPI · **stdlib-only core** (`rag`/`ingestion`/`core`/`eval`
import with zero third-party deps) · all heavy backends pluggable by env var and
imported lazily.

```
┌───────────────────────────────────────────────────────────────────────┐
│  FastAPI app (app/main.py)                                            │
│  routes: /health  /ask  /feedback  /sources  /admin                   │
│  middleware: auth(SSO/RBAC stub)  ratelimit(token-bucket)  audit(JSONL)│
└───────────────┬───────────────────────────────────────────────────────┘
                │  Services (DI container, rag/services.py)
                ▼
┌───────────────────────────────────────────────────────────────────────┐
│  AnswerPipeline (rag/graph.py) — also wireable as a LangGraph StateGraph│
│  guardrail→analysis→retrieve→rerank→generate→verify→confidence→assemble │
└───────────────┬───────────────────────────────────────────────────────┘
     Pluggable backends (app/config.py → build_services)
     ┌───────────────┬────────────────┬───────────────┬──────────────────┐
     │ EMBEDDER      │ VECTOR_STORE   │ RERANKER      │ LLM_PROFILE       │
     │ hash│bge│e5   │ memory│qdrant  │ noop│bge      │ stub│claude│vllm│ollama
     └───────────────┴────────────────┴───────────────┴──────────────────┘
     Ingestion (offline/admin): discovery→extract(OCR)→clean→chunk→metadata→embed→upsert
     Infra: Dockerfile(py3.11-slim+tesseract) · docker-compose · docker-compose.qdrant
```

**Strengths.** Clean node/`Services` separation (every node unit-testable with
stubs), env-driven profile switching, Qdrant auto-fallback to in-memory,
deterministic dev profile boots with no infra.

**Note.** The **default** profile is `hash`/`memory`/`noop`/`stub` — i.e. the
configuration that boots and is benchmarked is not the configuration that ships.

## 2. RAG Pipeline Flow

| # | Node | Function | Failure branch |
|---|------|----------|----------------|
| 1 | **guardrail** | scope match (stems / short-tokens / phrases from `INVESTIGATOR_TERMS` etc.) + injection regex | → **refuse** if off-scope / injection |
| 2 | **query_analysis** | capability classify → `doc_type_filter`; SOP-first override for case-doc cues; statute / crime-synonym expansion | — |
| 3 | **retrieve** | hybrid dense(cosine)+lexical(token-overlap) fused via **RRF**; honors doc_type filter; `k=20` | — |
| 4 | **rerank** | `noop` = lexical passthrough (prod = BGE cross-encoder); `top_n=6`; `relevance_floor=0.15` | → **abstain** if nothing survives |
| 5 | **generate** | routed LLM with cite-or-abstain prompt (stub copies passage snippets) | — |
| 6 | **verify** | **hard grounding gate**: every `[n]` marker must map to a passage; every `Section/clause N` ref must appear in a cited passage; ≥1 citation mandatory | → **abstain** on unknown marker / hallucinated ref / no-cite |
| 7 | **confidence** | `f(top_score, margin, n_support, verifier_passed)` → high / medium / low | — |
| 8 | **assemble** | final answer + citations + confidence + disclaimer | — |

The **grounding gate (Node 6)** is the safety keystone — real and active. It is
the mechanism that delivers "zero hallucinated legal/SOP references."

## 3. Repositories (the four knowledge sources)

| Repo | Location | Files | `doc_type`(s) |
|------|----------|-------|---------------|
| **Legal** | `data/corpus/legal_repository/` | BNS, BNSS, BSA, DPDP, IT_Act, POCSO (`.md`) + `legal_metadata.yaml` | `act`, `sanhita` |
| **SOP** | `data/corpus/sop_repository/` | `SOPCCHQ.sop.txt` (28,086 lines) | `sop` |
| **Recovery** | `data/corpus/recovery_repository/` | 1930_Helpline, Account_Freeze, Beneficiary_Tracing, Crypto_Asset_Recovery, Fund_Recall, Mule_Account_Investigation, NCRP_Workflow (`.md`) + `recovery_metadata.yaml` | `recovery` |
| **Decision-tree** | `data/corpus/decision_trees/` | 22 crime-workflow files (`01_upi…` → `22_fake_job…`) | `decision_tree` |

**KB caveat.** The legal / recovery / decision-tree repos are **hand-curated
markdown**, not the source PDFs. The four PDFs (`BNS.pdf`, `BNSS.pdf`,
`SOPCCHQ.pdf` ~26 MB, `it_act_2000_updated.pdf`) sit at repo root and are **not
ingested** — only the SOP txt is a real extracted artifact. Citation-integrity
against authoritative source text is therefore unverified. Total ingested corpus
is ~31 k lines: tiny relative to the real KB.

## 4. Current Benchmark Numbers

**150/150 tests pass.** Regression gate (n=41): **Overall 85.4%** *(hash
embedder)* vs frozen baseline 78.0%.

| Category | Baseline | Now | Δ |
|----------|----------|-----|---|
| adversarial | 100.0% | **100.0%** | — |
| legal | 90.0% | **90.0%** | — |
| recovery | 83.3% | **83.3%** | — |
| sop | 64.3% | **85.7%** | **+21.4** |
| decision_tree | 66.7% | **66.7%** | — |

These are **routing-correctness** rates (did the answer cite a chunk of the
expected `doc_type`) measured with the lexical `hash` embedder. They are **not**
the docs' production gates: recall@10 ≥ 90%, groundedness ≥ 98%, citation
accuracy ≥ 99% (legal) / 97% (SOP), abstention ≥ 95%. **None of those production
metrics exist as measured numbers yet.**

## 5. Remaining Failing Cases

| # | Category / mode | Query | Expected | Got |
|---|---|---|---|---|
| 1 | legal / LEX | "Certificate for electronic records under Bharatiya Sakshya Adhiniyam?" | act/sanhita | **sop** |
| 2 | sop / LEX | "How to extract data from a SIM card?" | sop | **act+sanhita** |
| 3 | sop / LEX | "How to request IP logs from an ISP?" | sop | **decision_tree** |
| 4 | recovery / LEX | "What is the role of the 1930 helpline?" | recovery | **sop** |
| 5 | decision_tree / ROUTE | "Step-by-step workflow to investigate UPI banking fraud?" | decision_tree | **recovery+sop** |
| 6 | decision_tree / ROUTE | "Investigation steps for a sextortion case?" | decision_tree | **sop** |

All six are **rare-term LEX / cross-repo ROUTE** misses — the lexical `hash`
embedder cannot bridge "1930 helpline" → recovery or "IP logs" → SOP
semantically. Cases #1–#4 are exactly the class the docs expect `e5` to fix;
#5–#6 are the next routing lever (same footnote / narrow-filter pattern that
fixed SOP).

## 6. Missing Production Features

- **Real generation path untested** — everything is benchmarked on `StubLLM`,
  which copies passage snippets. Faithfulness / citation discipline of an actual
  Claude/Llama generation against this corpus has **zero measurements**.
- **Production embedder unmeasured** — `e5`/`bge` code exists but egress to the
  model host is blocked (403) in the current environment; no accuracy number on
  the real model.
- **KB ingestion not run for real** — PDFs unprocessed; no OCR-confidence review,
  no completeness check (every section present once), no citation-integrity
  sample.
- **CI enforcement unverified** — the regression gate is a script + test, but no
  CI workflow enforcing it on promotion was found.
- **No multilingual eval** — despite `tesseract-ocr-hin` + multilingual-e5, there
  are zero Hindi test cases.
- **Feedback route exists** but no loop feeding production answers back into the
  eval set.

## 7. Security Gaps

- **Auth is a stub.** `_verify_token()` returns `None` (always 401 when enabled)
  and `AUTH_ENABLED` defaults **False** → the dev profile is fully open as
  `officer`. No OIDC/Keycloak integration, no real RBAC enforcement.
- **No TLS / at-rest encryption / secrets vault** wiring — all [BLOCKER] items in
  docs §10.4, none implemented.
- **Audit store is append-only JSONL** (`data/audit/audit.jsonl`) — not
  immutable, not tamper-evident, no access control, no PII redaction.
- **Rate limiter is in-process** (per-worker token bucket) — bypassable across
  workers; docs call for a Redis-backed shared limiter.
- **No security review / pen test** performed.
- Injection screening is a single regex — narrow; a small-LLM classifier is the
  documented production upgrade.

## 8. Scalability Gaps

- **Default store is in-memory**; the Qdrant path exists but has no
  sharding / replication / HA config, single collection.
- **No caching** (embedding or answer) layer.
- **Retrieval params** (`k=20`, `top_n=6`, `floor=0.15`) are tuned on a ~31 k-line
  toy corpus and will need re-tuning on the full KB.
- **LLM is 70B (vLLM) or hosted Claude** — GPU-bound; **no load test**, no P95
  latency number, concurrency behavior unknown (docs §10.6 marks load test as
  SHOULD, not done).
- Ingestion is single-pass / admin-triggered; no delta-ingest promotion pipeline
  is operational.

## 9. Mobile Deployment Readiness

**Effectively zero, with a framing mismatch to resolve.** The README/docs
describe an **on-prem / air-gapped server** (FastAPI + Qdrant + Llama 3.3 70B on
local GPUs) — *not* a phone app. The only "mobile" signal is a code comment
calling `e5-small` the "mobile-target embedder." There is **no** ONNX export,
**no** SQLite/on-device vector store, **no** quantized on-device LLM, **no**
Android/edge runtime. If true offline-on-device (e.g. a 4 GB phone) is a hard
requirement, it is an entirely unbuilt track and a 70B server LLM is incompatible
with it — this needs an explicit product decision before it becomes a roadmap
line.

## 10. Roadmap to Production Readiness

Mapping the real gaps to docs §10 [BLOCKER]s, in dependency order.

### Phase A — Measurement integrity (unblocks everything)
Unblock `e5`/`bge` egress (or side-load weights), **re-run the regression on the
production embedder**, and stand up the missing numeric gates — **recall@10,
groundedness/faithfulness, citation accuracy** — against a **real LLM**, not the
stub. *Until this exists, "85.4%" cannot be quoted to a pilot stakeholder.*

### Phase B — Retrieval quality to target
Confirm `e5` clears failing cases #1–#4; close routing cases #5–#6 (UPI /
sextortion decision-tree lever). Target: recall@10 ≥ 90%, correct abstention
≥ 95%.

### Phase C — Knowledge base completeness (docs §10.1)
Ingest the source PDFs through the OCR → clean → chunk pipeline; run completeness
+ **citation-integrity ≥ 99%** sampling; obtain **SME / legal sign-off** on
`kb_v1`; wire KB versioning + rollback (collection alias).

### Phase D — Security & privacy (docs §10.4)
Real SSO/OIDC + enforced RBAC; TLS; encryption at rest; secrets in Vault; PII
redaction + access-controlled **immutable** audit; **pen test**.

### Phase E — Reliability & observability (docs §10.6)
Metrics (latency / grounding / abstention) + alerting; LLM fallback / retry /
backoff; KB & audit backups with tested restore + DR runbook; **load test to a
P95 target**.

### Phase F — Pilot operations (docs §10.7)
CI enforcing the regression gate on every promotion; officer training +
"decision-support, not authority" framing; feedback loop into the eval set;
incident / rollback runbooks; formal **Go / No-Go**.

---

**Bottom line.** The reasoning core is genuinely strong — grounding gate,
abstention, citations, versioning hooks, and a clean pluggable architecture are
all in place and tested. The gap to a pilot is **not** the RAG logic; it is
(a) proving accuracy on the real embedder + LLM instead of the `hash`/`stub`
proxy, (b) ingesting and validating the real KB, and (c) the entire
security / ops / observability column, which is currently scaffolding. **Phase A
is the true unblock** — it converts every number in this report from *proxy* to
*real*.
