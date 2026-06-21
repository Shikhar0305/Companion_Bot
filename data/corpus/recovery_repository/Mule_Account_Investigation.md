# Mule Account Investigation — Cybercrime Recovery Repository

> **Repository:** Cybercrime Recovery Repository (CCHQ) — RAG-ready.
> **Process:** Investigating mule accounts used to layer and cash out defrauded funds.
> **Provenance:** Grounded in the in-repo decision trees (Financial Investigation: "funds routed through layered / mule accounts → trace mule-account chain and freeze downstream accounts", e.g. `decision_trees/01_upi_banking_fraud.md`, `decision_trees/16_sim_swap_fraud.md`) and legal repository (`legal_repository/`). PMLA/FIU applicability must be verified per case.
> **Generated:** 2026-06-21

---
## Purpose

To identify, freeze, and attribute mule accounts in the layering chain — the intermediary accounts through which defrauded money is moved and withdrawn — and to reach the controllers behind them.

## When Used

- When the trail shows funds routed through layered or intermediary accounts.
- When a frozen beneficiary account shows rapid pass-through to further accounts.
- When recovering funds requires freezing multiple downstream accounts quickly.

## Required Inputs

- Beneficiary and downstream account numbers/VPAs and banks.
- Transaction trail across hops (UTR/RRN, amounts, timestamps).
- KYC and account-opening records for each mule account (via production).
- Device/telecom/IP identifiers used to operate the accounts.

## Step-by-Step Procedure

1. From the beneficiary account, map pass-through transfers to downstream/mule accounts.
2. Freeze downstream accounts holding recoverable balances (see `Account_Freeze.md`).
3. Issue production requests for KYC, account-opening, and operation records (BNSS S.94).
4. Identify how each account was operated (device, IP, telecom) and correlate operators.
5. Distinguish witting controllers from recruited/duped account holders.
6. Preserve records as certified electronic evidence (BSA S.63) with chain of custody.
7. Build attribution linking controllers to the fraud and feed arrest/charge-sheet steps.

## Escalation Path

- Large mule networks → flag for specialised-unit oversight and inter-bank coordination via I4C.
- Proceeds of crime / laundering pattern → coordinate with FIU-IND / ED (verify applicability).
- Cross-border cash-out → escalate for international coordination through nodal channels.

## Expected Timeline

- Downstream freezing: immediate, in parallel with beneficiary freeze.
- Operator attribution: dependent on bank/telecom/platform record production. *(Indicative — confirm current SLAs.)*

## Investigator Checklist

- [ ] Pass-through transfers mapped from beneficiary to mule accounts.
- [ ] Downstream accounts with balances frozen.
- [ ] KYC / account-opening records requested (BNSS S.94).
- [ ] Operation identifiers (device/IP/telecom) correlated.
- [ ] Witting vs. duped account holders distinguished.
- [ ] Records certified (BSA S.63) with chain of custody.
- [ ] Controller attribution documented.

## Recovery Limitations

- Mule accounts are emptied quickly; recoverable balances are often small per account.
- Fraudulent/borrowed KYC obscures the real controllers.
- Recruited holders may be victims themselves, complicating attribution.

## Applicable Authorities

- **BNSS S.94** — production of KYC/account records.
- **BNSS S.185 / S.186** — search and seizure (incl. beyond local limits).
- **BNS S.316 / S.318 / S.319** — criminal breach of trust / cheating / cheating by personation.
- **IT Act S.66D** — cheating by personation using a computer resource.
- **BSA S.63** — admissibility of electronic records.
- *(Verify PMLA / FIU-IND applicability where proceeds-of-crime laundering is indicated.)*
- **Framework:** I4C; RBI/NPCI; inter-bank coordination.
