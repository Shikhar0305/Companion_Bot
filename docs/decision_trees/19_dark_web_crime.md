# Dark Web Crime

> **Source:** CCHQ_formatted.docx — Chapter 19: Dark Web Crime. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** Critical | **Priority:** P1

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF victim at immediate risk / active incident
THEN preliminary assessment as first action

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Preserve digital evidence; Record marketplace details; Preserve wallet addresses; Preserve communication records; Record infrastructure identifiers; Report through Cyber Helpline; Register complaint on NCRP

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
THEN perform network forensics, cloud/platform forensics with write blockers, forensic imaging and hash verification

IF original media / source files exist
THEN seize originals (not copies) and preserve metadata
```

## Financial Investigation Decisions

```

IF cryptocurrency wallet / transaction hash identified
THEN initiate blockchain tracing and coordinate with the exchange for KYC and account preservation

IF recoverable funds / assets still held
THEN pursue documented recovery measures: Asset tracing, Transaction analysis, Exchange coordination
```

## Platform Investigation Decisions

```
IF telecom identifiers involved (number / SIM / VoIP)
THEN conduct telecom analysis and request CDR + subscriber-detail preservation

IF IP / domain / server lead obtained
THEN perform attribution (IP tracing, domain/server investigation) and onward telecom/ISP follow-up
```

## Escalation Decisions

```
IF additional third-party records required
THEN issue preservation / production requests to banks, telecom operators and platforms

IF cross-border element identified (international transfer / foreign infrastructure)
THEN escalate for cross-border coordination through documented nodal/reporting channels

IF case severity is Critical (priority P1)
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
THEN prepare charge sheet including: Documentary Evidence, Complaint records, Infrastructure records, Transaction records, Platform records, Digital Evidence, Device reports, Communication records, Wallet records, Access logs

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: Participation in dark web criminal activity; Possession or operation of criminal infrastructure; Criminal intent and unlawful purpose; Digital linkage between accused and activity; Financial or criminal benefit obtained; Knowledge and control of criminal operations; Evidence correlation across platforms and services
```
