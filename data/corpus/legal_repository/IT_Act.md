# IT Act — Cybercrime Legal Repository

> **Repository:** Cybercrime Legal Repository (CCHQ) — RAG-ready.
> **Statute:** The Information Technology Act, 2000 (as amended)
> **Provenance:** Grounded in the provided `it_act_2000_updated.pdf` (section text verified) and CCHQ SOP references.
> **Scope:** Only sections **referenced by the CCHQ SOP** are included.
> **Generated:** 2026-06-21

Sections of the IT Act, 2000 referenced by the CCHQ SOP, in RAG-ready format.

---
### IT Act, 2000 Section 43 — Penalty and compensation for damage to computer, computer system, etc.

**Section Number:** 43
**Section Name:** Penalty and compensation for damage to computer, computer system, etc.

**Description:**
Imposes civil liability (penalty and compensation) on any person who, without permission of the owner, accesses, downloads, copies, extracts, introduces a contaminant/virus, damages, disrupts, denies access, or tampers with a computer, computer system or network or the data held in it.

**Applicability:**
Foundational unauthorised-access provision. Applies wherever a device/account/server is accessed or data is extracted or damaged without authorisation. Frequently read with S.66 to convert the civil wrong into a criminal offence.

**Evidence Requirements:**
Certified electronic records under BSA S.63 with S.63(4) certificate; hash values (SHA-256); chain of custody; forensic image of device/server; preservation of original media. Access/authentication logs, IP logs, login records, malware/contaminant samples, and proof of absence of authorisation.

**Related Crime Categories:** UPI/Banking Fraud, Loan App Fraud, Ransomware, SIM Swap Fraud, Dark Web Crime

**Investigator Notes:**
S.43 is civil (compensation before the Adjudicating Officer); pair with S.66 for criminal prosecution. Establish 'without permission of the owner' explicitly.

**Common Investigation Mistakes:**
Charging S.43 alone for a criminal case (it is compensatory); failing to document that access was unauthorised; not preserving volatile logs before they rotate.

---
### IT Act, 2000 Section 66 — Computer related offences

**Section Number:** 66
**Section Name:** Computer related offences

**Description:**
If any person dishonestly or fraudulently does any act referred to in S.43, they are punishable with imprisonment up to three years or fine up to five lakh rupees or both.

**Applicability:**
Criminal counterpart to S.43. Applies to dishonest/fraudulent unauthorised access, data theft, hacking, contaminant introduction and disruption — the backbone for hacking/ransomware/account-compromise cases.

**Evidence Requirements:**
Certified electronic records under BSA S.63 with S.63(4) certificate; hash values (SHA-256); chain of custody; forensic image of device/server; preservation of original media. Evidence of mens rea (dishonest/fraudulent intent), attribution to the accused (device, IP, account), and the underlying S.43 act.

**Related Crime Categories:** UPI/Banking Fraud, Trading Scam, Loan App Fraud, Ransomware, Dark Web Crime

**Investigator Notes:**
Requires proof of dishonest/fraudulent intent (mens rea) over and above the S.43 act. Cognizable and bailable.

**Common Investigation Mistakes:**
Treating intent as presumed; weak attribution linking the act to the accused; omitting the linkage to a specific S.43 sub-clause.

---
### IT Act, 2000 Section 66C — Punishment for identity theft

**Section Number:** 66C
**Section Name:** Punishment for identity theft

**Description:**
Whoever fraudulently or dishonestly makes use of the electronic signature, password or any other unique identification feature of any other person is punishable with imprisonment up to three years and fine up to one lakh rupees.

**Applicability:**
Core provision wherever stolen credentials, OTPs, passwords, Aadhaar/PAN, biometric or other unique identifiers are misused — identity theft, account takeover, SIM swap, phishing, impersonation.

**Evidence Requirements:**
Certified electronic records under BSA S.63 with S.63(4) certificate; hash values (SHA-256); chain of custody; forensic image of device/server; preservation of original media. Proof of the genuine owner's identifier, records showing its fraudulent use, login/authentication trails, and linkage of the misuse to the accused.

**Related Crime Categories:** UPI/Banking Fraud, Investment Scam, Trading Scam, Loan App Fraud, Sextortion, Social Media Impersonation, Online Shopping Fraud, Identity Theft, Cyber Stalking & Harassment, Deepfake Fraud, Ransomware, BEC, SIM Swap Fraud, Crypto Fraud, CSAM, Dark Web Crime, Online Gambling Fraud, QR Code Fraud, Fake Job Scam

**Investigator Notes:**
The 'unique identification feature' is read broadly (passwords, OTPs, biometrics, digital signatures). Almost always charged together with S.66D.

**Common Investigation Mistakes:**
Failing to prove the identifier belonged to a real, identified person; not capturing the authentication logs that show the misuse; conflating S.66C with S.66D without distinguishing identity misuse from personation.

---
### IT Act, 2000 Section 66D — Punishment for cheating by personation by using computer resource

**Section Number:** 66D
**Section Name:** Punishment for cheating by personation by using computer resource

**Description:**
Whoever, by means of any communication device or computer resource, cheats by personation is punishable with imprisonment up to three years and fine up to one lakh rupees.

**Applicability:**
The primary cyber-fraud charge: phishing, vishing, fake profiles, fraudulent payment requests, fake sellers/recruiters, impersonation of banks/officials and most financial scams.

**Evidence Requirements:**
Certified electronic records under BSA S.63 with S.63(4) certificate; hash values (SHA-256); chain of custody; forensic image of device/server; preservation of original media. Communication records (calls, SMS, chats, emails), the personation content, the deception, the victim's resulting transfer/act, and the money/data trail.

**Related Crime Categories:** UPI/Banking Fraud, Investment Scam, Trading Scam, Loan App Fraud, Social Media Impersonation, Online Shopping Fraud, Identity Theft, Deepfake Fraud, Ransomware, BEC, SIM Swap Fraud, Crypto Fraud, Dark Web Crime, Online Gambling Fraud, QR Code Fraud, Fake Job Scam

**Investigator Notes:**
Establish all ingredients of cheating (deception + dishonest inducement + delivery/act) AND that it was done by personation via a computer resource/communication device.

**Common Investigation Mistakes:**
Proving deception but not personation (or vice versa); missing the inducement-to-loss causal link; not preserving the communication channel that carried the personation.

---
### IT Act, 2000 Section 66E — Punishment for violation of privacy

**Section Number:** 66E
**Section Name:** Punishment for violation of privacy

**Description:**
Punishes intentionally or knowingly capturing, publishing or transmitting the image of a private area of any person without consent, under circumstances violating privacy — imprisonment up to three years or fine up to two lakh rupees, or both.

**Applicability:**
Voyeurism/privacy-violation cases: sextortion, non-consensual intimate imagery, hidden-camera content, image-based abuse, and cyber-stalking involving private images.

**Evidence Requirements:**
Certified electronic records under BSA S.63 with S.63(4) certificate; hash values (SHA-256); chain of custody; forensic image of device/server; preservation of original media. The offending image/video with metadata, proof of capture/publication/transmission, absence of consent, and the victim's reasonable expectation of privacy.

**Related Crime Categories:** Sextortion, Cyber Stalking & Harassment, Deepfake Fraud, CSAM

**Investigator Notes:**
Focus on 'private area' and 'circumstances violating privacy' as defined in the Explanation. Handle victim content with strict confidentiality and minimal copies.

**Common Investigation Mistakes:**
Mishandling/over-copying sensitive victim imagery; failing to establish lack of consent; not preserving upload/transmission metadata that proves publication.

---
### IT Act, 2000 Section 67 — Punishment for publishing or transmitting obscene material in electronic form

**Section Number:** 67
**Section Name:** Punishment for publishing or transmitting obscene material in electronic form

**Description:**
Punishes publishing or transmitting in electronic form any material that is lascivious or appeals to prurient interest or tends to deprave and corrupt — first conviction up to three years and fine up to five lakh rupees; enhanced on subsequent conviction.

**Applicability:**
General electronic-obscenity offences; in the SOP, applied to sextortion where obscene (non-child) material is circulated.

**Evidence Requirements:**
Certified electronic records under BSA S.63 with S.63(4) certificate; hash values (SHA-256); chain of custody; forensic image of device/server; preservation of original media. The material, publication/transmission proof, and platform/account attribution.

**Related Crime Categories:** Sextortion

**Investigator Notes:**
For sexually explicit (not merely obscene) content use S.67A; for any child content use S.67B. Charge the correct tier.

**Common Investigation Mistakes:**
Charging S.67 where S.67A/67B applies; failing to attribute the publishing account to the accused.

---
### IT Act, 2000 Section 67A — Punishment for publishing or transmitting of material containing sexually explicit act, etc., in electronic form

**Section Number:** 67A
**Section Name:** Punishment for publishing or transmitting of material containing sexually explicit act, etc., in electronic form

**Description:**
Punishes publishing/transmitting electronic material containing a sexually explicit act or conduct — first conviction up to five years and fine up to ten lakh rupees; enhanced on subsequent conviction.

**Applicability:**
Sextortion and deepfake cases involving sexually explicit (adult) content distributed or threatened to be distributed electronically.

**Evidence Requirements:**
Certified electronic records under BSA S.63 with S.63(4) certificate; hash values (SHA-256); chain of custody; forensic image of device/server; preservation of original media. The explicit material with metadata, distribution/threat evidence, and account/device attribution.

**Related Crime Categories:** Sextortion, Deepfake Fraud, CSAM

**Investigator Notes:**
Where the depicted person is (or appears to be) a child, S.67B and POCSO apply and take precedence.

**Common Investigation Mistakes:**
Failing to verify the age of the depicted person (which determines S.67A vs 67B/POCSO); weak attribution of the distributing account.

---
### IT Act, 2000 Section 67B — Punishment for publishing or transmitting of material depicting children in sexually explicit act, etc., in electronic form (CSAM)

**Section Number:** 67B
**Section Name:** Punishment for publishing or transmitting of material depicting children in sexually explicit act, etc., in electronic form (CSAM)

**Description:**
Criminalises publishing, transmitting, creating, collecting, browsing, downloading, advertising, exchanging or distributing material depicting children in a sexually explicit act, and related conduct (incl. online grooming) — first conviction up to five years and fine up to ten lakh rupees; enhanced on subsequent conviction.

**Applicability:**
All child sexual abuse material (CSAM) and online child-grooming offences. Always charged together with the POCSO Act, 2012.

**Evidence Requirements:**
Strictly controlled handling of CSAM (minimal access, hashed, sealed); device/cloud forensic images; upload/download/IP logs; grooming chats; victim age verification. Coordinate with NCMEC/NCRP CSAM reporting pipelines.

**Related Crime Categories:** Sextortion, CSAM

**Investigator Notes:**
Possession/browsing itself is an offence. Mandatory reporting obligations apply. Handle exclusively through authorised personnel; never duplicate content beyond evidentiary necessity.

**Common Investigation Mistakes:**
Improper or excessive handling of CSAM; charging only IT Act and omitting POCSO; failing to preserve grooming communications; not invoking mandatory-reporting and child-protection workflows.

---
### IT Act, 2000 Section 72 — Penalty for breach of confidentiality and privacy

**Section Number:** 72
**Section Name:** Penalty for breach of confidentiality and privacy

**Description:**
Punishes any person who, having secured access to electronic records/information under powers conferred by the Act, discloses it to another without consent — imprisonment up to two years or fine up to one lakh rupees, or both.

**Applicability:**
Unauthorised disclosure/leak of personal data accessed under the Act's powers; in the SOP, applied to loan-app data-misuse and privacy violations.

**Evidence Requirements:**
Certified electronic records under BSA S.63 with S.63(4) certificate; hash values (SHA-256); chain of custody; forensic image of device/server; preservation of original media. Proof of access secured under the Act, the disclosure, and absence of consent.

**Related Crime Categories:** Loan App Fraud

**Investigator Notes:**
S.72 is narrow (access secured under the Act's powers). For broader data-misuse by private apps, read with BNS provisions and the DPDP Act, 2023.

**Common Investigation Mistakes:**
Over-extending S.72 to ordinary private data theft; not establishing how access was originally secured.

