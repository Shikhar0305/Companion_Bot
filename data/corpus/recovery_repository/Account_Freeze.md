# Account Freeze — Cybercrime Recovery Repository

> **Repository:** Cybercrime Recovery Repository (CCHQ) — RAG-ready.
> **Process:** Freezing the beneficiary (and downstream) accounts to preserve defrauded funds.
> **Provenance:** Grounded in the in-repo decision trees (Financial Investigation: "initiate account freeze (debit + credit)", "freeze downstream accounts", e.g. `decision_trees/01_upi_banking_fraud.md`) and legal repository (`legal_repository/BNSS.md`). Exact bank SLAs and the precise BNSS attachment provision must be verified against current law/RBI circulars.
> **Generated:** 2026-06-21

---
## Purpose

To stop withdrawal or further layering of defrauded money by placing a freeze (debit and, where warranted, credit) on the beneficiary account and any identified downstream/mule accounts, preserving funds for recall and restitution.

## When Used

- As soon as a beneficiary account/VPA is identified in a financial-fraud case.
- After 1930/NCRP reporting, to convert a provisional hold into a documented freeze.
- When funds are traced into layered or mule accounts that must be frozen downstream.

## Required Inputs

- Beneficiary account number / VPA and bank/PSP.
- Transaction trail: UTR/RRN/transaction IDs linking victim debit to beneficiary credit.
- FIR / NCRP reference and IO authorization.
- Identified downstream accounts (for chain freezing).

## Step-by-Step Procedure

1. Identify the beneficiary account/VPA and the holding bank/PSP from the transaction trail.
2. Issue a freeze request (debit + credit as warranted) to the beneficiary bank, with the FIR/NCRP reference.
3. Request transaction-trail preservation and account statements from the bank (BNSS S.94 — production).
4. Where funds are layered, trace the mule-account chain and freeze downstream accounts (see `Mule_Account_Investigation.md`).
5. Record freeze confirmations, frozen amounts, and timestamps in the case file.
6. Proceed to fund recall/restitution for the held amounts (see `Fund_Recall.md`).

## Escalation Path

- Bank delays/declines freeze → escalate to the bank nodal officer, then the State Cyber Nodal Officer / I4C.
- Multi-bank layering → coordinate simultaneous freezes across beneficiary banks.
- Proceeds suspected as money laundering → flag for FIU-IND / ED coordination (verify applicability).

## Expected Timeline

- Freeze request: immediately on beneficiary identification (golden hour).
- Bank action: per I4C/RBI cooperation timelines. *(Indicative — confirm current SLAs.)*

## Investigator Checklist

- [ ] Beneficiary account/VPA and bank identified.
- [ ] Transaction trail (UTR/RRN) documented.
- [ ] Freeze request issued with FIR/NCRP reference.
- [ ] Transaction-trail preservation requested (BNSS S.94).
- [ ] Downstream/mule accounts traced and frozen.
- [ ] Freeze confirmations and amounts recorded.

## Recovery Limitations

- Only the balance still present can be frozen; withdrawn/converted funds cannot be held.
- Freezing without prompt recall may still allow legal challenges by the account holder.
- Crypto off-ramps and cash-out via ATMs/mules defeat bank-level freezes.

## Applicable Authorities

- **BNSS S.94** — Summons to produce document or other thing (incl. electronic records / bank records).
- **BNSS S.176** — Procedure for investigation of cognizable offence.
- **IT Act S.66D** / **BNS S.318, S.319, S.316, S.303(2)** — substantive financial-fraud offences.
- *(Verify the applicable BNSS provision for attachment/seizure of proceeds of crime for formal attachment.)*
- **Framework:** I4C, RBI / NPCI payment-system and fraud-management guidelines.
