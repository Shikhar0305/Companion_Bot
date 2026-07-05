# Companion Bot Architecture

## High Level Flow

User Query
↓
Guardrail
↓
Query Analysis
↓
Retrieval
↓
Reranking
↓
Generation
↓
Verification
↓
Confidence Scoring
↓
Final Response

---

## Detailed Pipeline

### 1. Guardrail

Responsibilities:

- Scope Detection
- Prompt Injection Detection
- Refusal Handling

Output:

- In Scope
- Out Of Scope
- Refused

---

### 2. Query Analysis

Responsibilities:

- Capability Classification
- Query Expansion
- Repository Selection

Repositories:

- SOP
- Legal
- Recovery
- Decision Tree

---

### 3. Retrieval

Responsibilities:

- Vector Search
- Candidate Selection

Embedder:

- E5

Store:

- In-Memory Vector Store

---

### 4. Reranking

Responsibilities:

- Candidate Ordering
- Relevance Improvement

Output:

Top Passages

---

### 5. Generation

Model:

- Gemma 3 4B (Ollama)

Responsibilities:

- Generate Answer
- Add Citations

---

### 6. Verification

Responsibilities:

- Citation Validation
- Hallucination Detection
- Grounding Enforcement

Possible Outcomes:

- Answer Accepted
- Abstain
- Refuse

---

### 7. Confidence

Responsibilities:

- Confidence Calculation
- Confidence Labels

Output:

- High
- Medium
- Low

---

## Knowledge Sources

### SOP Repository

Cybercrime investigation procedures.

### Legal Repository

- IT Act
- BNS
- BNSS
- BSA

### Recovery Repository

Financial recovery procedures.

### Decision Trees

Investigation workflows.

---

## Evaluation Framework

### Automated Regression

41 Cases

Categories:

- Legal
- SOP
- Recovery
- Decision Tree
- Adversarial

---

### Manual Evaluation

20 Cases

Focus:

- Real Investigator Queries
- Hindi/Hinglish
- Safety
- Grounding

---

## Current Branch

integration-v1

Current Score:

87.8%

Tests:

150/150 Passing