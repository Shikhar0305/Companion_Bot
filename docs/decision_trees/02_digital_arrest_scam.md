# Digital Arrest Scam

> **Source:** CCHQ_formatted.docx — Chapter 2: Digital Arrest Scam. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** Very High | **Priority:** P1

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Disconnect communication with fraudsters; Inform family members; Contact Cyber Helpline; Notify the bank immediately; Freeze beneficiary accounts; Preserve screenshots; Preserve call recordings

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
THEN perform mobile forensics, cloud/platform forensics with write blockers, forensic imaging and hash verification

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
THEN pursue documented recovery measures: Immediate account freezing, Transaction recall, Inter-bank coordination, Fund trail tracing, Victim Support, Legal guidance, Psychological support, Digital security counselling
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

IF case severity is Very High (priority P1)
THEN prioritise investigation and flag for senior/specialised-unit oversight

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
THEN prepare charge sheet including: Documentary Evidence, Bank statements, KYC documents, Fake notices, Screenshots, Digital Evidence, Call recordings, Chat logs, Device reports, Platform records

IF charge sheet to be framed
THEN apply relevant statutory provisions — NOTE: source chapter does not enumerate a Relevant Laws section; confirm applicable IT Act / BNS / BSA / BNSS sections

IF prosecution proceeds
THEN establish: False representation of authority; Intentional deception; Fear-based coercion; Financial inducement; Victim reliance on false representation; Monetary loss; Digital linkage between accused and fraudulent communication
```
