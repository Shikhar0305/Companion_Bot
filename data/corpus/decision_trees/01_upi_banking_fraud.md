# UPI / Banking Fraud

> **Source:** CCHQ_formatted.docx — Chapter 1: UPI / Banking Fraud. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** High | **Priority:** P2

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF jurisdiction confirmed
THEN proceed to FIR registration (else coordinate jurisdiction verification)

IF financial loss is recent (immediate window)
THEN execute immediate response: Within First Hour:; Call Cyber Helpline 1930; Report on NCRP portal; Notify bank immediately; Request account freeze; Preserve screenshots; Preserve messages; Avoid deleting data

IF FIR criteria satisfied
THEN register FIR and assign investigating officer
```

## Evidence Collection Decisions

```
IF victim holds screenshots / chats / messages
THEN preserve them and record hash + chain of custody

IF OTP / SMS / call communication involved
THEN collect SMS logs, OTP records and call logs from device

IF physical device is available (mobile / computer / storage)
THEN perform mobile forensics, network forensics, cloud/platform forensics with write blockers, forensic imaging and hash verification

IF original media / source files exist
THEN seize originals (not copies) and preserve metadata
```

## Financial Investigation Decisions

```
IF transaction IDs / UTR / payment records available
THEN conduct financial trail analysis

IF beneficiary account identified
THEN initiate account freeze (debit + credit) and request transaction-trail preservation from the bank

IF funds routed through layered / mule accounts
THEN trace mule-account chain and freeze downstream accounts

IF recoverable funds / assets still held
THEN pursue documented recovery measures: Account freezing, Transaction reversal, Fund recall requests, Inter-bank coordination
```

## Platform Investigation Decisions

```
IF crime conducted via an online platform / website / app
THEN issue preservation request to the platform for login history, IP logs and device information

IF telecom identifiers involved (number / SIM / VoIP)
THEN conduct telecom analysis and request CDR + subscriber-detail preservation
```

## Escalation Decisions

```
IF additional third-party records required
THEN issue preservation / production requests to banks, telecom operators and platforms

IF cross-border element identified (international transfer / foreign infrastructure)
THEN escalate for cross-border coordination through documented nodal/reporting channels

IF suspect not yet attributable
THEN continue technical attribution (device, telecom, IP, financial linkage) before closure/escalation
```

## Arrest & Prosecution Decisions

```
IF suspect identified
THEN conduct search and seizure and effect arrest as warranted

IF seized devices / records obtained
THEN complete forensic examination and evidence correlation

IF evidentiary chain established
THEN prepare charge sheet including: Documentary Evidence, Bank records, Transaction records, KYC documents, Digital Evidence, Device examination reports, Log records, IP information, Expert Reports, Digital forensic report

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: Fraudulent intention; Dishonest inducement; Unauthorized access or misuse; Financial loss suffered by victim; Linkage between accused and beneficiary account; Digital attribution through logs, devices, and records
```
