# Fund Recall — Cybercrime Recovery Repository

> **Repository:** Cybercrime Recovery Repository (CCHQ) — RAG-ready.
> **Process:** Recalling / reversing frozen defrauded funds back to the victim.
> **Provenance:** Grounded in the in-repo decision trees (Financial Investigation: "Transaction reversal, Fund recall requests, Inter-bank coordination", e.g. `decision_trees/01_upi_banking_fraud.md`). Reversal mechanics and timelines depend on RBI/NPCI rules and court process — verify against current circulars.
> **Generated:** 2026-06-21

---
## Purpose

To recover frozen/held defrauded money to the victim through documented recovery measures — transaction reversal, fund recall requests, inter-bank coordination, and, where required, restitution through the court.

## When Used

- After funds have been successfully frozen/held in a beneficiary or downstream account.
- When recoverable funds or assets are still held in the money trail.
- As the restitution step following `Account_Freeze.md`.

## Required Inputs

- Confirmation of frozen amount and holding account/bank.
- Complete transaction trail (victim debit → beneficiary credit; UTR/RRN).
- FIR/NCRP reference and IO authorization.
- Court directions for release/restitution where required.

## Step-by-Step Procedure

1. Confirm the frozen/held amount with the holding bank.
2. Initiate a fund recall / transaction-reversal request through inter-bank coordination, citing FIR/NCRP.
3. Where reversal is not automatic, pursue restitution/release through the competent court.
4. Coordinate across all banks in the layering chain for partial recoveries at each hop.
5. Document recovered amounts, the channel used, and credit back to the victim.
6. Update the case file and the victim on recovery status.

## Escalation Path

- Bank refuses recall/reversal → escalate to bank nodal officer, then State Cyber Nodal Officer / I4C.
- Disputed entitlement → seek court direction for release/restitution.
- Multi-bank / cross-border funds → coordinate via I4C / international channels.

## Expected Timeline

- Recall request: immediately after freeze confirmation.
- Reversal/restitution: governed by RBI/NPCI rules and, where applicable, court timelines. *(Indicative — confirm current SLAs.)*

## Investigator Checklist

- [ ] Frozen amount confirmed with holding bank.
- [ ] Recall / reversal request initiated with FIR/NCRP reference.
- [ ] Inter-bank coordination completed across the layering chain.
- [ ] Court direction obtained where required.
- [ ] Recovered amount credited to victim and documented.
- [ ] Victim updated on status.

## Recovery Limitations

- Only frozen/held balances are recoverable; withdrawn or converted funds are typically unrecoverable.
- Reversal is not guaranteed and may require court process and contested hearings.
- Partial recovery is common where funds were split across many mule accounts.

## Applicable Authorities

- **BNSS S.94** — production of bank records supporting the recall.
- **BNSS S.176 / S.193** — investigation procedure and final report supporting restitution.
- **IT Act S.66D** / **BNS S.318, S.319, S.316** — substantive offences underpinning recovery.
- *(Verify the applicable BNSS provision for disposal/restitution of property to the rightful owner.)*
- **Framework:** RBI / NPCI fund-recall and chargeback mechanisms; I4C coordination.
