# Ransomware

> **Source:** CCHQ_formatted.docx — Chapter 14: Ransomware. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** Critical | **Priority:** P1

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF victim at immediate risk / active incident
THEN incident assessment as first action

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Isolate affected systems; Disconnect compromised devices from the network; Preserve volatile evidence; Preserve logs; Preserve ransom notes; Avoid deleting malware artefacts; Report through Cyber Helpline

IF FIR criteria satisfied
THEN register FIR and assign investigating officer
```

## Evidence Collection Decisions

```
IF victim holds screenshots / chats / messages
THEN preserve them and record hash + chain of custody

IF physical device is available (mobile / computer / storage)
THEN perform network forensics, cloud/platform forensics, malware analysis with write blockers, forensic imaging and hash verification

IF original media / source files exist
THEN seize originals (not copies) and preserve metadata
```

## Financial Investigation Decisions

```
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

IF cross-border element identified (international transfer / foreign infrastructure)
THEN escalate for cross-border coordination through documented nodal/reporting channels

IF case severity is Critical (priority P1)
THEN prioritise investigation and flag for senior/specialised-unit oversight

IF suspect not yet attributable
THEN continue technical attribution (device, telecom, IP, financial linkage) before closure/escalation
```

## Arrest & Prosecution Decisions

```

IF seized devices / records obtained
THEN complete forensic examination and evidence correlation

IF evidentiary chain established
THEN prepare charge sheet including: Documentary Evidence, Complaint records, Incident reports, Network records, Preservation responses, Digital Evidence, Malware samples, System logs, Network logs, Device reports

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: Unauthorized deployment of ransomware; Unauthorized access to victim systems; Encryption, disruption, or exfiltration of data; Extortion demand by accused; Digital linkage between accused and attack infrastructure; Harm suffered by victim; Benefit sought or obtained by accused
```
