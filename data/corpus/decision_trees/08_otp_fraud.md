# OTP Fraud

> **Source:** CCHQ_formatted.docx — Chapter 8: OTP Fraud. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** High | **Priority:** P2

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response Preserve SMS messages. • Preserve transaction records. • Preserve call logs. • Contact bank immediately. • Request account blocking/freezing. • Report through Cyber Helpline; • Register complaint on NCRP. • Preserve all communications

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

IF funds routed through layered / mule accounts
THEN trace mule-account chain and freeze downstream accounts

IF recoverable funds / assets still held
THEN pursue documented recovery measures: Fund freezing • Transaction tracing • Beneficiary identification, Bank Assistance, Account security restoration • Credential reset • Fraud dispute process, Victim Support, Banking guidance • Cyber awareness counselling
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
THEN prepare charge sheet including: Documentary Evidence, Complaint records • Bank responses • Transaction statements • Communication records, Digital Evidence, OTP messages • Login records • IP logs • Device reports, Expert Reports, Digital forensic report • Financial trail analysis report • Attribution report

IF charge sheet to be framed
THEN apply relevant statutory provisions — NOTE: source chapter does not enumerate a Relevant Laws section; confirm applicable IT Act / BNS / BSA / BNSS sections

IF prosecution proceeds
THEN establish: Unauthorized acquisition or misuse of OTP; Deception or inducement of victim; Unauthorized access or transaction; Financial loss or attempted loss; Digital linkage between accused and transaction; Benefit obtained by accused; Financial trail connecting accused
```
