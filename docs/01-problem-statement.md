# 1. Problem Statement

## 1.1 Context

Cybercrime in India has grown faster than the investigative capacity to handle
it. Investigation officers face four compounding pressures:

1. **Legal complexity.** A single cyber case can span the IT Act 2000, the
   Bharatiya Nyaya Sanhita (BNS), the Bharatiya Nagarik Suraksha Sanhita
   (BNSS), the Bharatiya Sakshya Adhiniyam, and sectoral rules/advisories
   (RBI, NPCI, CERT-In, I4C). Officers must map a fact pattern to the correct
   provisions quickly and accurately.
2. **Procedural rigor.** Digital evidence is fragile and easily challenged in
   court. Seizure, preservation, chain-of-custody, and acquisition must follow
   SOPs precisely or the evidence becomes inadmissible.
3. **Speed.** In financial fraud (UPI, QR, BEC, card fraud) the first hours
   determine whether money can be frozen and traced. Officers cannot spend
   that time searching PDFs.
4. **Knowledge dispersion.** The required knowledge is scattered across
   hundreds of pages of SOPs, manuals, statutes, and circulars — much of it
   in scanned PDFs that are not searchable.

## 1.2 The core problem

> Investigation officers need **fast, accurate, legally-correct, procedure-
> grounded answers** to cybercrime investigation questions — but the knowledge
> is locked in long, unstructured, partly-scanned documents, and a general LLM
> cannot be trusted to cite the correct legal section or SOP step.

A naive ChatGPT-style assistant is unacceptable here because:

- **Hallucinated legal sections** can derail a prosecution or mislead an
  officer into an unlawful action (e.g. an improper search/seizure).
- **Hallucinated SOP steps** can break chain of custody and render evidence
  inadmissible.
- **No source attribution** means an officer cannot verify or defend the
  guidance — and supervisors cannot audit it.

## 1.3 What the system must do

Build a **source-grounded RAG assistant** that:

- Answers only from an **approved, version-controlled knowledge base**.
- **Cites the exact source** (document, section/clause, page) for every claim.
- States a **confidence level** and **abstains** ("Information not found in
  approved knowledge sources") rather than guessing.
- Covers five capability areas: **investigation guidance, legal assistance,
  digital forensics, OSINT, and financial-fraud investigation**.
- Is **auditable and explainable** — every answer logs the query, retrieved
  passages, model, prompt, and citations.

## 1.4 Target users

| User | Primary need |
|---|---|
| Cyber Crime Investigation Officer | Next steps, applicable law, evidence procedure |
| Police Personnel (first responders) | Immediate do/don't, scene & device handling |
| Cyber Cells | Fraud workflows, escalation, account tracing |
| Digital Forensic Analysts | Acquisition workflows, chain of custody, tooling |
| Investigation Supervisors | Verification, completeness, audit of guidance |

## 1.5 Supported cybercrime categories

Phishing · Smishing · Vishing · UPI Fraud · QR Code Fraud · Credit Card Fraud ·
Identity Theft · Social Media Impersonation · Sextortion · Business Email
Compromise · Cryptocurrency Fraud · Investment Scam · Job Scam · E-Commerce
Fraud · Malware · Ransomware · Cyber Stalking · Data Theft · Account Takeover ·
Online Gaming Fraud.

Each category is a **metadata facet** in the knowledge base (see
[Knowledge Base Design](04-knowledge-base-design.md)), enabling category-scoped
retrieval and category-specific playbooks.

## 1.6 Explicit non-goals

- Not a replacement for legal counsel, the prosecution, or judicial judgment.
- Not an autonomous agent that takes investigative actions.
- Not a general-purpose chatbot — off-domain questions are politely refused.
- No mobile app or end-user front-end design in this document set (the focus is
  the AI core: chatbot, RAG pipeline, knowledge base, grounded answering).

## 1.7 Success criteria

| Metric | Target |
|---|---|
| Groundedness (answers fully supported by cited passages) | ≥ 98% |
| Citation accuracy (cited section/SOP actually says it) | ≥ 99% (legal), ≥ 97% (SOP) |
| Correct abstention on out-of-corpus questions | ≥ 95% |
| Hallucinated legal section / SOP reference | **0 tolerated** (hard gate) |
| Retrieval recall@10 on the eval set | ≥ 90% |
| P95 answer latency (cloud LLM) | ≤ 6 s |
| Full auditability of every answer | 100% |
