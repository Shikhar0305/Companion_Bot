# Evaluation Summary — Cybercrime Investigation Companion Bot

Endpoint: `http://127.0.0.1:8000/ask`  |  Cases: **35**  |  Passed: **33/35**

## Overall metrics

| Metric | Accuracy |
|---|---|
| Overall | 94.3% |
| Legal | 90.0% |
| Recovery | 85.7% |
| Decision-tree | 100.0% |
| Refusal | 100.0% |

## Category-wise results

| Category | Passed | Total |
|---|---|---|
| legal | 9 | 10 |
| recovery | 6 | 7 |
| decision_tree | 10 | 10 |
| refusal | 8 | 8 |

## Failed queries

| Category | Query | Expected | Actual | Cited |
|---|---|---|---|---|
| legal | What is the certificate requirement for electronic evidence? | legal | decision_tree | 06_sextortion|14_ransomware |
| recovery | How do I trace a mule account chain? | recovery | decision_tree | 01_upi_banking_fraud|08_otp_fraud |

## Root cause analysis

- **Retrieval mis-routing:** 2 query(ies) retrieved the wrong repository/doc (capability routing or lexical ranking under the dev embedder).

## Retrieval issues

- `What is the certificate requirement for electronic evidence?` → expected **legal**, got **decision_tree** (06_sextortion|14_ransomware).
- `How do I trace a mule account chain?` → expected **recovery**, got **decision_tree** (01_upi_banking_fraud|08_otp_fraud).

*Primary lever: the dev profile uses the lexical HashingEmbedder; switching `EMBEDDER=bge` (BGE-M3 semantic) sharpens ranking across overlapping documents without code changes.*

## Guardrail issues

- None — guardrail correctly admitted all valid queries and refused all unrelated ones.
