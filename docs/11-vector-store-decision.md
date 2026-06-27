# 11 — Vector Store Decision (Mobile-First)

**Status:** Accepted
**Context:** Final deployment is an **offline Android application** for investigating
officers on **low-end (4 GB RAM) devices**. No mobile data, no server reachability
during normal use. Case data (PII, transaction IDs) must never leave the device.

## Decision

**On the device, do not run a vector database. Use an embedded flat index
(brute-force cosine + BM25), persisted as a single `sqlite-vec` file bundled in
the APK.** Qdrant is retained only as an *optional, server-side* store for an
online "HQ workstation" mode — it is never shipped to the phone.

## Rationale

### 1. Scale does not justify an ANN index or a DB server
The approved corpus (SOPCCHQ + IT Act, BNS, BNSS, BSA, DPDP, POCSO + decision
trees + recovery repo) produces on the order of **~1,700–3,000 chunks**.

* Brute-force cosine over a few thousand 384-d vectors is **< 20 ms** on a phone.
* Approximate-nearest-neighbour indexes (HNSW/IVF, as used by FAISS/Qdrant/Milvus)
  exist to avoid scanning **hundreds of thousands to millions** of vectors. At our
  scale they add memory, build complexity, and recall-tuning for **no latency
  benefit**.

### 2. Server vector DBs are architecturally incompatible with offline mobile
Qdrant, Milvus, and Weaviate are **server processes** (run via Docker). They cannot
be embedded in an Android app and would require network reachability — violating
the offline + data-privacy requirement.

### 3. SQLite (`sqlite-vec` + FTS5) is the right embedded store
* A **single file** holds vectors **+** chunk metadata **+** a BM25/FTS5 lexical
  index — exactly the hybrid retrieval the system already performs.
* Runs **natively on Android**, no server, no Docker, fully offline.
* KB updates are an **atomic file swap** of a signed, versioned bundle.
* It mirrors the existing `InMemoryVectorStore` logic (dense cosine + lexical,
  fused with RRF), so on-device retrieval is the **same algorithm**, just persisted.

## Options considered

| Option | Embeddable on 4 GB Android | Verdict |
|---|---|---|
| Qdrant / Milvus / Weaviate | No — server / Docker | Optional **server-only** (HQ mode) |
| FAISS (HNSW) | Heavy (JNI), ANN overkill at this scale | Rejected |
| Flat brute-force cosine | Yes | **Adopted** (reference algorithm) |
| **sqlite-vec + FTS5** | Yes (native, single file) | **Adopted** (device persistence) |

## Architecture by tier

| Tier | Vector store |
|---|---|
| **Mobile (product)** | Embedded flat index → `sqlite-vec` artifact bundled in the APK. No server. |
| **Build-time (factory)** | Same flat store; embed corpus, export the bundled artifact. |
| **Optional HQ server** | Qdrant (`VECTOR_STORE=qdrant`), opt-in. Never on the phone. |

## Implications for the codebase

* **Default stays `VECTOR_STORE=memory`** (the flat store) — already the product default
  (`app/config.py`). Qdrant remains opt-in and is **demoted to optional server-only**.
* **To build (Phase 1 / Phase 5):** add a persistable `SqliteVecStore` that mirrors
  `InMemoryVectorStore`'s hybrid retrieval, plus an export step that writes the bundled
  KB artifact (`chunks + int8 vectors + BM25 index + embedder version`).
* The embedder version is pinned in the artifact metadata so the bundled KB and the
  on-device query encoder (`multilingual-e5-small`) can never silently drift.

## Resource impact (4 GB device)

| Resource | Estimate |
|---|---|
| KB store (sqlite-vec, ~1.7k chunks) | vectors ~0.7 MB (int8) + text ~1.5 MB + BM25 ~1 MB ≈ **~4 MB** |
| Retrieval latency | flat cosine < 20 ms + BM25 < 10 ms (dominated by query embedding, not search) |

Storage and latency are negligible; **RAM (the embedding model), not the vector
store, is the binding constraint** — see `docs/05` and the deployment analysis.
