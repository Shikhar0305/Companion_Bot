# SIM Swap Fraud

> **Source:** CCHQ_formatted.docx — Chapter 16: SIM Swap Fraud. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** Critical | **Priority:** P1

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Contact telecom provider immediately; Block unauthorized SIM activation; Secure banking accounts; Change account passwords; Preserve SMS and call records; Notify affected banks; Report through Cyber Helpline

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
THEN pursue documented recovery measures: Account freezing, Transaction tracing, Beneficiary identification, Victim Support, Legal guidance, Cyber awareness counselling, Account security recommendations
```

## Platform Investigation Decisions

```
IF crime conducted via an online platform / website / app
THEN issue preservation request to the platform for login history, IP logs and device information

IF telecom identifiers involved (number / SIM / VoIP)
THEN conduct telecom analysis and request CDR + subscriber-detail preservation

IF IP / domain / server lead obtained
THEN perform attribution (IP tracing, domain/server investigation) and onward telecom/ISP follow-up
```

## Escalation Decisions

```
IF additional third-party records required
THEN issue preservation / production requests to banks, telecom operators and platforms

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
THEN prepare charge sheet including: Documentary Evidence, Complaint records, Telecom records, Banking records, Subscriber documents, Digital Evidence, Login logs, Authentication records, Device reports, IP records

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: Fraudulent SIM replacement or activation; Unauthorized control of victim's mobile number; Use of intercepted authentication mechanisms; Unauthorized access to victim accounts; Financial benefit obtained by accused; Digital linkage between accused and SIM activity; Harm suffered by victim
```
