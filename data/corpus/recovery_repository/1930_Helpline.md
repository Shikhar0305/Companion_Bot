# 1930 Helpline — Cybercrime Recovery Repository

> **Repository:** Cybercrime Recovery Repository (CCHQ) — RAG-ready.
> **Process:** Immediate financial-fraud reporting via the national cyber-crime helpline **1930**.
> **Provenance:** Grounded in the in-repo decision trees (Immediate Response: "Call Cyber Helpline 1930", e.g. `decision_trees/01_upi_banking_fraud.md`, `decision_trees/17_crypto_fraud.md`) and aligned to the I4C Citizen Financial Cyber Fraud Reporting and Management System. SLAs/timelines are indicative — verify against current I4C/RBI guidance.
> **Generated:** 2026-06-21

---
## Purpose

To stop the flow of defrauded money as early as possible by reporting financial cyber fraud to the **1930** helpline, which feeds the Citizen Financial Cyber Fraud Reporting and Management System and alerts the banks/payment intermediaries in the money trail for provisional hold.

## When Used

- The moment a victim reports financial loss — the **golden hour** immediately after a fraudulent transfer.
- In parallel with NCRP registration; 1930 is the fastest channel to trigger a provisional hold.
- For UPI/bank/card fraud, crypto-to-fiat off-ramps, and mule-routed transfers.

## Required Inputs

- Victim mobile number and identity.
- Transaction details: amount, date/time, debit account/card/UPI, transaction IDs / UTR / RRN.
- Suspected beneficiary details if known (VPA, account number, wallet/exchange).
- Brief modus operandi.

## Step-by-Step Procedure

1. Call **1930** immediately (or assist the victim to call) and report the financial fraud.
2. Provide transaction identifiers so the system can flag the destination account/PSP.
3. Ensure a corresponding complaint is filed on NCRP and capture the acknowledgement number.
4. Notify the victim's bank immediately and request an account freeze on the beneficiary leg (see `Account_Freeze.md`).
5. Preserve all evidence (screenshots, SMS/OTP, chats) with hash + chain of custody.
6. Record the 1930 reference and link it to the case file and any freeze/recall requests.

## Escalation Path

- No provisional hold placed → escalate to the bank nodal officer and State Cyber Nodal Officer.
- Multi-bank layering → coordinate across beneficiary banks via the I4C system.
- Cross-border off-ramp → escalate for international coordination through nodal channels.

## Expected Timeline

- Reporting: immediate; effectiveness is highest within the **golden hour** before withdrawal/layering.
- Provisional hold: dependent on PSP/bank response under the I4C system. *(Indicative — confirm current SLAs.)*

## Investigator Checklist

- [ ] 1930 call placed and reference captured.
- [ ] Transaction identifiers (UTR/RRN/txn IDs) supplied.
- [ ] NCRP complaint filed and number linked.
- [ ] Bank notified and freeze requested on the beneficiary leg.
- [ ] Evidence preserved with hash + chain of custody.

## Recovery Limitations

- A 1930 report triggers a *provisional* hold, not a guaranteed recovery; funds already withdrawn cannot be held.
- Effectiveness drops steeply with delay and with each layer of mule accounts.
- Cross-border off-ramps and crypto conversion limit what the domestic banking chain can hold.

## Applicable Authorities

- **IT Act S.66C / S.66D** — Identity theft / cheating by personation using a computer resource.
- **BNS S.318 / S.319** — Cheating / cheating by personation.
- **BNS S.303(2) / S.316** — Theft of digital assets / criminal breach of trust (as applicable).
- **Framework:** I4C, national helpline 1930, Citizen Financial Cyber Fraud Reporting and Management System; RBI/NPCI payment-system guidelines.
