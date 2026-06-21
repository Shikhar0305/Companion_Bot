# Cyber Stalking & Harassment

> **Source:** CCHQ_formatted.docx — Chapter 12: Cyber Stalking & Harassment. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** High | **Priority:** P2

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF victim at immediate risk / active incident
THEN victim safeguarding as first action

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Preserve all communications; Capture screenshots; Record profile URLs; Preserve call records; Avoid deleting messages; Block accounts only after evidence preservation; Report through Cyber Helpline

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
THEN perform mobile forensics, network forensics, media forensics with write blockers, forensic imaging and hash verification

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
THEN prepare charge sheet including: Documentary Evidence, Complaint records, Platform responses, Communication records, Profile details, Digital Evidence, Chat logs, Call records, Account logs, Device reports

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: Repeated unwanted conduct; Intent to harass, intimidate, or threaten; Digital communications linking accused and victim; Psychological impact on victim; Unauthorized surveillance or monitoring; Digital linkage between accused and communications; Harm suffered by victim
```
