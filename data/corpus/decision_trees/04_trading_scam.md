# Trading Scam

> **Source:** CCHQ_formatted.docx — Chapter 4: Trading Scam. Decision tree converts the documented Investigation Flow into conditional steps. **All THEN actions are SOP-supported** (drawn from the chapter's Investigation Flow, Evidence Hierarchy, Digital Forensics, Preservation Requests, Immediate Response, Charge Sheet and Prosecution sections).

> **Risk level:** Very High | **Priority:** P1

## Initial Triage

```
IF complaint received
THEN record complaint and verify it discloses a cognizable cyber offence

IF financial loss is recent (immediate window)
THEN execute immediate response: First Hour Response; Preserve trading records; Save screenshots; Download account statements; Preserve communication records; Report to Cyber Helpline; Notify the bank; Preserve website information

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

IF cryptocurrency wallet / transaction hash identified
THEN initiate blockchain tracing and coordinate with the exchange for KYC and account preservation

IF recoverable funds / assets still held
THEN pursue documented recovery measures: Account freezing, Fund trail analysis, Asset identification, Exchange coordination
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
THEN prepare charge sheet including: Documentary Evidence, Trading account records, Transaction records, Website ownership records, Domain registration records, Digital Evidence, Device reports, Communication logs, Trading platform logs, Screenshots

IF charge sheet to be framed
THEN apply the chapter's documented Relevant Laws (IT Act / BNS / BSA / BNSS and special statutes)

IF prosecution proceeds
THEN establish: False trading representation; Intentional deception; Fraudulent inducement; Collection of funds through misrepresentation; Artificial display of profits; Financial loss suffered by victims; Digital linkage between accused and fraudulent platform
```
