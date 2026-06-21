# NCRP Workflow — Cybercrime Recovery Repository

> **Repository:** Cybercrime Recovery Repository (CCHQ) — RAG-ready.
> **Process:** Reporting and case intake via the National Cyber Crime Reporting Portal (NCRP).
> **Provenance:** Grounded in the in-repo decision trees (Immediate Response / Initial Triage steps, e.g. `decision_trees/01_upi_banking_fraud.md`) and legal repository (`legal_repository/`), aligned to the I4C NCRP framework. Exact portal field names and SLAs must be verified against the current NCRP / I4C operating guidelines.
> **Generated:** 2026-06-21

---
## Purpose

To register a cyber-crime complaint on the National Cyber Crime Reporting Portal (NCRP, `cybercrime.gov.in`) so that it enters the I4C reporting and case-management system, is routed to the correct jurisdiction, and — for financial fraud — triggers the downstream freeze and recall workflow.

## When Used

- Immediately on receipt of any cyber-crime complaint, especially financial fraud where money has moved.
- When a victim walks in, calls, or reports online and a structured intake is required before or alongside FIR registration.
- As the entry point that feeds the **1930 helpline**, **account freeze**, and **fund recall** procedures.

## Required Inputs

- Complainant identity and contact details (name, mobile, email).
- Incident description, date/time, and modus operandi.
- Financial details where applicable: transaction IDs / UTR / RRN, amount, debit account, suspected beneficiary VPA/account.
- Supporting evidence: screenshots, SMS/OTP logs, chat records, call logs (preserve with hash + chain of custody).
- Jurisdiction indicators (victim location, where loss occurred).

## Step-by-Step Procedure

1. Record the complaint and verify it discloses a cognizable cyber offence.
2. Register the complaint on NCRP (`cybercrime.gov.in`) under the correct category (Financial Fraud vs. Other Cyber Crime).
3. For financial fraud, ensure the complaint is filed through the **Citizen Financial Cyber Fraud Reporting and Management System** so the banking/PSP chain is alerted.
4. Capture and preserve all uploaded evidence; record hash values and chain of custody.
5. Confirm jurisdiction; if unclear, coordinate jurisdiction verification before FIR routing.
6. Convert the NCRP report to FIR where criteria are satisfied (BNSS S.173) and assign an investigating officer.
7. Link the NCRP acknowledgement number to the case file for traceability across freeze/recall actions.

## Escalation Path

- Unattended/unactioned NCRP report → escalate to the State/District Cyber Nodal Officer.
- Cross-state element → coordinate through documented nodal/reporting channels.
- Cross-border element → escalate for international coordination via I4C / designated nodal channels.

## Expected Timeline

- Registration: immediate (within the **golden hour** for financial fraud).
- FIR conversion: as per BNSS S.173 on disclosure of a cognizable offence.
- *(Indicative — confirm current SLAs against I4C/NCRP guidelines.)*

## Investigator Checklist

- [ ] Complaint recorded and offence cognizability confirmed.
- [ ] NCRP report filed under the correct category; acknowledgement number captured.
- [ ] Financial fraud filed through the Citizen Financial Cyber Fraud Reporting system.
- [ ] Evidence preserved with hash + chain of custody.
- [ ] Jurisdiction confirmed or verification coordinated.
- [ ] FIR registered (BNSS S.173) and IO assigned where warranted.
- [ ] NCRP number linked to freeze/recall actions.

## Recovery Limitations

- NCRP registration alone does **not** freeze funds — it must be paired with the freeze/recall workflow.
- Delay beyond the golden hour sharply reduces recoverability once funds are layered or withdrawn.
- Portal routing depends on accurate jurisdiction/category selection; misclassification delays action.

## Applicable Authorities

- **BNSS S.173** — Information in cognizable cases (FIR registration).
- **BNSS S.176** — Procedure for investigation of cognizable offence.
- **IT Act S.66C / S.66D** — Identity theft / cheating by personation using a computer resource.
- **BNS S.318 / S.319** — Cheating / cheating by personation.
- **Framework:** Indian Cyber Crime Coordination Centre (I4C), NCRP, Citizen Financial Cyber Fraud Reporting and Management System.
