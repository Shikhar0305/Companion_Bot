# Beneficiary Tracing — Cybercrime Recovery Repository

> **Repository:** Cybercrime Recovery Repository (CCHQ) — RAG-ready.
> **Process:** Tracing the money trail to the beneficiary and through layered accounts.
> **Provenance:** Grounded in the in-repo decision trees (Financial Investigation: "conduct financial trail analysis", "trace mule-account chain"; Platform/Telecom preservation, e.g. `decision_trees/01_upi_banking_fraud.md`) and legal repository (`legal_repository/BNSS.md`, `legal_repository/BSA.md`).
> **Generated:** 2026-06-21

---
## Purpose

To follow the financial trail from the victim's debit to the ultimate beneficiary, identifying each account/VPA in the layering chain so that freezes, recalls, and attribution can be executed.

## When Used

- Whenever transaction IDs/UTR/payment records are available and the destination of funds must be established.
- After the first beneficiary is frozen, to map downstream mule accounts.
- To build the financial-linkage element of the prosecution (accused ↔ beneficiary account).

## Required Inputs

- Transaction identifiers: UTR / RRN / transaction IDs, amounts, timestamps.
- Beneficiary account/VPA and bank/PSP at each hop.
- Bank statements and KYC for identified accounts (via production requests).
- Telecom/platform identifiers where accounts were operated remotely.

## Step-by-Step Procedure

1. Conduct financial-trail analysis from the victim debit using UTR/RRN/transaction IDs.
2. Identify the first-level beneficiary account/VPA and holding bank.
3. Issue production/preservation requests for statements and KYC (BNSS S.94).
4. Map onward transfers to downstream/mule accounts and repeat tracing at each hop.
5. Correlate with telecom (CDR/subscriber) and platform (login/IP) records for account operators.
6. Preserve all records as certified electronic evidence (BSA S.63) with hash + chain of custody.
7. Document the complete beneficiary chain and feed freeze/recall actions.

## Escalation Path

- Banks/PSPs slow to produce records → escalate to nodal officers / I4C.
- Telecom/platform records needed → issue preservation + production requests.
- Cross-border hops → escalate for international coordination through nodal channels.

## Expected Timeline

- Initial tracing: begins immediately with the freeze workflow.
- Record production: per bank/telecom/platform cooperation timelines. *(Indicative — confirm current SLAs.)*

## Investigator Checklist

- [ ] Financial-trail analysis conducted from victim debit.
- [ ] First-level beneficiary identified.
- [ ] Production/preservation requests issued (BNSS S.94).
- [ ] Downstream/mule chain mapped at each hop.
- [ ] Telecom/platform records correlated to operators.
- [ ] Records certified (BSA S.63) with hash + chain of custody.
- [ ] Beneficiary chain documented and linked to freeze/recall.

## Recovery Limitations

- Rapid layering across many accounts outpaces tracing and disperses funds.
- KYC on mule accounts is often fraudulent, limiting attribution to real controllers.
- Cross-border and crypto hops break the domestic bank trail.

## Applicable Authorities

- **BNSS S.94** — Summons to produce documents (bank/telecom/platform records).
- **BNSS S.176** — Procedure for investigation of cognizable offence.
- **BSA S.63** — Admissibility of electronic records (certificate requirement).
- **BSA S.57** — Proof of electronic and digital records.
- **IT Act S.66D** / **BNS S.318, S.319, S.316, S.303(2)** — substantive offences.
- **Framework:** I4C coordination; RBI/NPCI; telecom (CDR) and platform preservation.
