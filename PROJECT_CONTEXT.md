# Companion Bot

## Project Overview

Companion Bot is a Cybercrime Investigation Companion designed for investigating officers.

The system provides grounded, citation-backed answers using Retrieval-Augmented Generation (RAG) over cybercrime SOPs, legal documents, recovery procedures, and investigation decision trees.

The objective is to provide investigators with fast, reliable, explainable guidance while preventing hallucinations.

---

## Current Branch

integration-v1

---

## Current Backend Status

Prototype Backend

Regression Score: 87.8%

Categories:

- Legal: 100%
- SOP: 85.7%
- Recovery: 83.3%
- Decision Tree: 66.7%
- Adversarial: 100%

Tests:

- 150/150 passing

Corpus:

- 1712 chunks loaded

---

## Technology Stack

Backend:
- FastAPI
- Python

RAG:
- Custom Retrieval Pipeline
- Grounding Verification
- Confidence Scoring

Embeddings:
- E5

LLM:
- Ollama
- Gemma 3 4B

Vector Store:
- In-memory vector store

---

## Knowledge Sources

### SOP Repository
Cybercrime investigation SOPs.

### Legal Repository
IT Act
BNS
BNSS
BSA

### Recovery Repository
Financial fraud recovery procedures.

### Decision Trees
Investigation workflows for common cybercrime categories.

---

## Core Principles

1. Grounded Answers Only
2. Mandatory Citations
3. Hallucination Prevention
4. Safe Refusal
5. Explainability
6. Investigator-Oriented Responses

---

## Completed Work

### Retrieval

- E5 Embedder Integration
- Hybrid Retrieval
- SOP Routing Improvements
- Legal Routing Improvements

### Safety

- Guardrail Vocabulary
- Grounding Verification
- Hallucination Detection
- Refusal Handling

### Evaluation

- 41-case Regression Suite
- 20-case Manual Investigator Suite
- Automated Reporting

### Knowledge Base

- SOP Corpus
- Legal Corpus
- Recovery Corpus
- Decision Tree Corpus

---

## Remaining Work

### P0

- Gemma 3 4B Validation
- E5 Validation
- API Boundary Tests

### P1

- Citation Integrity Sampling
- Hindi/Hinglish Validation
- Baseline Refresh

### P2

- Mobile Application
- Production Infrastructure
- Authentication
- Monitoring

---

## Freeze Criteria

Backend is considered frozen when:

- Real Gemma Validation Complete
- E5 Validation Complete
- API Contract Tested
- Citation Integrity Verified
- Hindi/Hinglish Evaluated
- Regression Stable