# Crypto Asset Recovery — Cybercrime Recovery Repository

> **Repository:** Cybercrime Recovery Repository (CCHQ) — RAG-ready.
> **Process:** Tracing and recovering cryptocurrency assets in fraud cases.
> **Provenance:** Grounded in the in-repo decision trees (Financial Investigation: "initiate blockchain tracing and coordinate with the exchange for KYC and account preservation", recovery measures "Asset tracing, Exchange coordination, Wallet monitoring, Recovery proceedings", `decision_trees/17_crypto_fraud.md`) and legal repository (`legal_repository/`). VDA-specific authorities, MLAT routing, and FIU-IND/VASP obligations must be verified per case.
> **Generated:** 2026-06-21

---
## Purpose

To trace defrauded cryptocurrency across the blockchain, coordinate with exchanges/VASPs to freeze and obtain KYC on destination wallets/accounts, and pursue recovery proceedings — recognising that crypto recovery is harder and more time-sensitive than bank-based recovery.

## When Used

- When loss involves cryptocurrency transfers and a wallet address or transaction hash is identified.
- When funds are moving toward an exchange off-ramp where a freeze + KYC request can intercept them.
- As the asset-recovery step for crypto-fraud cases (`decision_trees/17_crypto_fraud.md`).

## Required Inputs

- Wallet addresses and transaction hashes (preserve immediately).
- Exchange/platform details and any account identifiers.
- Communication records, screenshots, and investment/transfer evidence.
- FIR/NCRP reference and IO authorization.

## Step-by-Step Procedure

1. Preserve wallet addresses, transaction hashes, exchange details, and communications (hash + chain of custody).
2. Initiate blockchain tracing to follow funds across wallets toward exchange/off-ramp endpoints.
3. Coordinate with the exchange/VASP for KYC, account preservation, and freeze of destination accounts/wallets.
4. Monitor identified wallets for further movement.
5. Where assets reach a regulated exchange, pursue recovery proceedings against the held balance.
6. For cross-border infrastructure, escalate through international/MLAT channels.
7. Maintain certified electronic evidence (BSA S.63) of blockchain and exchange records.

## Escalation Path

- Exchange unresponsive / foreign VASP → escalate via I4C and international coordination / MLAT.
- Priority P1 severity → flag for senior/specialised-unit oversight (per crypto decision tree).
- Laundering / proceeds-of-crime pattern → coordinate with FIU-IND / ED (verify applicability).

## Expected Timeline

- Tracing & exchange request: immediate — crypto moves fast and irreversibly.
- Exchange/VASP response and cross-border steps: variable and often slow. *(Indicative — confirm current SLAs.)*

## Investigator Checklist

- [ ] Wallet addresses and transaction hashes preserved.
- [ ] Blockchain tracing initiated toward off-ramp endpoints.
- [ ] Exchange/VASP coordination for KYC + freeze done.
- [ ] Identified wallets under monitoring.
- [ ] Recovery proceedings pursued for held balances.
- [ ] Cross-border escalation / MLAT initiated where needed.
- [ ] Blockchain/exchange records certified (BSA S.63).

## Recovery Limitations

- On-chain transfers are irreversible; recovery depends on funds reaching a cooperating, regulated exchange.
- Non-KYC wallets, mixers/tumblers, and privacy coins break traceability.
- Foreign/unregulated VASPs and cross-border infrastructure sharply limit recovery.

## Applicable Authorities

- **IT Act S.66 / S.66D** — computer-related offences / cheating by personation.
- **BNS S.318 / S.319 / S.316** — cheating / cheating by personation / criminal breach of trust.
- **BNSS S.94** — production of exchange/account records.
- **BSA S.63 / S.57** — admissibility and proof of electronic records (blockchain/exchange data).
- *(Verify VDA-specific obligations, FIU-IND VASP reporting, and MLAT routing for cross-border assets.)*
- **Framework:** I4C; FIU-IND; international law-enforcement coordination (MLAT).
