# Child Sexual Abuse Material (CSAM)

> **Source:** CCHQ_formatted.docx — Chapter 18: Child Sexual Abuse Material (CSAM). Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** Critical | **Priority:** P1

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF victim is a minor / child involved
THEN initiate child safeguarding before further questioning

IF victim at immediate risk / active incident
THEN child safeguarding as first action

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Ensure child safety immediately; Preserve digital evidence; Preserve account information; Preserve profile URLs; Record platform details; Report through Cyber Helpline; Register complaint on NCRP

IF FIR criteria satisfied
THEN register FIR and assign investigating officer
```

## Evidence Collection Decisions

```
IF victim holds screenshots / chats / messages
THEN preserve them and record hash + chain of custody

IF OTP / SMS / call communication involved
THEN collect SMS logs, OTP records and call logs from device

IF chat-app or social-media communication exists (WhatsApp / Telegram / DMs)
THEN preserve chat records, profile URLs and account identifiers

IF physical device is available (mobile / computer / storage)
THEN perform mobile forensics, network forensics, cloud/platform forensics, media forensics with write blockers, forensic imaging and hash verification

IF original media / source files exist
THEN seize originals (not copies) and preserve metadata
```

## Financial Investigation Decisions

_No financial component documented for this crime in the source SOP — not applicable._

## Platform Investigation Decisions

```
IF crime conducted via an online platform / website / app
THEN issue preservation request to the platform for login history, IP logs and device information

IF telecom identifiers involved (number / SIM / VoIP)
THEN conduct telecom analysis and request CDR + subscriber-detail preservation

IF social-media / messaging profile involved
THEN coordinate with the platform for account metadata, registration and access logs

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

IF child-protection offence confirmed
THEN route to designated child-protection reporting channels on priority

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
THEN prepare charge sheet including: Documentary Evidence, Complaint records, Platform responses, Child protection records, Preservation responses, Digital Evidence, Media files, Chat records, Upload records, Device reports

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: Involvement of a child victim; Creation, possession, transmission, or distribution of CSAM; Intentional exploitation of a child; Digital linkage between accused and content; Harm suffered by the child victim; Knowledge and control of the material; Criminal benefit or exploitative purpose
```
