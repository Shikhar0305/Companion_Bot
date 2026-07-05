# Current Handoff

## Current Objective

Freeze the backend before mobile development begins.

---

## Immediate Task

Fix Windows UTF-8 issue in:

scripts/run_regression.py

All report files should be written using UTF-8 encoding.

---

## Validation Phase

Run:

### Regression Suite

41-case regression benchmark.

Target:

- Legal >= 90%
- SOP >= 85%
- Recovery >= 83%
- No regressions

---

### Manual Evaluation Suite

20 investigator-focused queries.

Measure:

- Citation Discipline
- Grounding Compatibility
- Abstention Behavior
- Hindi/Hinglish Support
- Legal Accuracy
- SOP Accuracy
- Recovery Accuracy

---

## Current Model Choice

LLM:
- Gemma 3 4B via Ollama

Embedding:
- E5

Reason:
- Offline
- Non-Chinese
- Reasonable Hardware Requirements
- Good RAG Performance

---

## Remaining Tasks

1. Fix UTF-8 issue
2. Run Gemma + E5 regression
3. Run manual investigator evaluation
4. Add FastAPI API tests
5. Validate Hindi/Hinglish
6. Verify citations
7. Freeze backend
8. Begin Flutter mobile development

---

## Important Constraints

- Do not redesign architecture.
- Do not remove evaluation infrastructure.
- Do not merge branches automatically.
- Always run tests before commits.
- Grounded answers only.