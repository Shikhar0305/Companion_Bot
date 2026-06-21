# QR Code Fraud

> **Source:** CCHQ_formatted.docx — Chapter 21: QR Code Fraud. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** High | **Priority:** P2

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Preserve QR code image; Preserve transaction records; Record beneficiary details; Preserve screenshots; Notify bank immediately; Report through Cyber Helpline; Register complaint on NCRP

IF FIR criteria satisfied
THEN register FIR and assign investigating officer
```

## Evidence Collection Decisions

```
IF victim holds screenshots / chats / messages
THEN preserve them and record hash + chain of custody

IF physical device is available (mobile / computer / storage)
THEN perform mobile forensics, network forensics with write blockers, forensic imaging and hash verification

IF original media / source files exist
THEN seize originals (not copies) and preserve metadata
```

## Financial Investigation Decisions

```
IF transaction IDs / UTR / payment records available
THEN conduct financial trail analysis

IF beneficiary account identified
THEN initiate account freeze (debit + credit) and request transaction-trail preservation from the bank

IF recoverable funds / assets still held
THEN pursue documented recovery measures: Fund tracing, Beneficiary identification, Transaction analysis
```

## Platform Investigation Decisions

```
IF IP / domain / server lead obtained
THEN perform attribution (IP tracing, domain/server investigation) and onward telecom/ISP follow-up
```

## Escalation Decisions

```
IF additional third-party records required
THEN issue preservation / production requests to banks, telecom operators and platforms

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
THEN prepare charge sheet including: Documentary Evidence, Complaint records, Transaction records, Merchant details, Platform responses, Digital Evidence, QR code records, UPI logs, Communication records, Device reports

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: Fraudulent QR code creation or use; Intentional deception of the victim; Unauthorized financial transaction; Financial loss suffered by victim; Financial benefit obtained by accused; Digital linkage between accused and QR code; Criminal intent and unlawful gain
```
