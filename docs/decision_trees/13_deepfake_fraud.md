# Deepfake Fraud

> **Source:** CCHQ_formatted.docx — Chapter 13: Deepfake Fraud. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** Very High | **Priority:** P1

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Preserve original content; Record URLs; Preserve screenshots; Record account details; Preserve communications; Report through Cyber Helpline; Register complaint on NCRP

IF FIR criteria satisfied
THEN register FIR and assign investigating officer
```

## Evidence Collection Decisions

```
IF victim holds screenshots / chats / messages
THEN preserve them and record hash + chain of custody

IF chat-app or social-media communication exists (WhatsApp / Telegram / DMs)
THEN preserve chat records, profile URLs and account identifiers

IF physical device is available (mobile / computer / storage)
THEN perform mobile forensics, network forensics, media forensics with write blockers, forensic imaging and hash verification

IF original media / source files exist
THEN seize originals (not copies) and preserve metadata
```

## Financial Investigation Decisions

```
```

## Platform Investigation Decisions

```
IF crime conducted via an online platform / website / app
THEN issue preservation request to the platform for login history, IP logs and device information

IF social-media / messaging profile involved
THEN coordinate with the platform for account metadata, registration and access logs

IF IP / domain / server lead obtained
THEN perform attribution (IP tracing, domain/server investigation) and onward telecom/ISP follow-up
```

## Escalation Decisions

```
IF additional third-party records required
THEN issue preservation / production requests to banks, telecom operators and platforms

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
THEN prepare charge sheet including: Documentary Evidence, Complaint records, Platform responses, URLs, Screenshots, Digital Evidence, Original media files, Upload records, IP logs, Device reports

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: Creation or use of manipulated content; False representation of identity; Intent to deceive, harm, or obtain benefit; Distribution of fabricated content; Digital linkage between accused and content; Harm suffered by victim; Benefit obtained by accused
```
