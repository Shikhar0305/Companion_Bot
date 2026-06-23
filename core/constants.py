"""Controlled vocabularies used across ingestion, retrieval, and answering.

Kept as plain tuples/dicts (no third-party deps) so every layer can import them.
"""
from __future__ import annotations

# Document types in the approved knowledge base (see docs/04-knowledge-base-design.md)
DOC_TYPES = (
    "act",        # e.g. IT Act 2000
    "sanhita",    # BNS, BNSS, Bharatiya Sakshya Adhiniyam
    "sop",        # Cyber Crime Investigation SOP
    "manual",     # forensic / investigation manuals
    "playbook",   # fraud / OSINT playbooks
    "advisory",   # CERT-In, I4C, RBI, NPCI
    "circular",   # police circulars
    "decision_tree",  # crime-type investigation decision trees
    "recovery",       # fund-recovery / escalation repositories
    "forensics",      # digital-forensics procedures (device/mobile/disk/CDR)
    "procedure",      # generic investigation procedures (intake/FIR/preservation)
)

# Capability areas the assistant supports (see docs/02-solution-architecture.md)
CAPABILITY_AREAS = (
    "legal",
    "investigation",
    "forensics",
    "osint",
    "financial",
)

# The 20 supported cybercrime categories (docs/01-problem-statement.md §1.5)
CYBERCRIME_CATEGORIES = (
    "phishing",
    "smishing",
    "vishing",
    "upi_fraud",
    "qr_code_fraud",
    "credit_card_fraud",
    "identity_theft",
    "social_media_impersonation",
    "sextortion",
    "business_email_compromise",
    "cryptocurrency_fraud",
    "investment_scam",
    "job_scam",
    "ecommerce_fraud",
    "malware",
    "ransomware",
    "cyber_stalking",
    "data_theft",
    "account_takeover",
    "online_gaming_fraud",
)

# Keyword cues used to tag chunks / classify queries by cybercrime category.
CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "phishing": ("phishing", "spoofed email", "fake login", "credential harvest"),
    "smishing": ("smishing", "sms fraud", "fraudulent sms", "text message scam"),
    "vishing": ("vishing", "voice call fraud", "fake call", "phone scam"),
    "upi_fraud": ("upi", "unified payments", "collect request", "vpa", "@upi"),
    "qr_code_fraud": ("qr code", "qr scan", "scan to pay"),
    "credit_card_fraud": ("credit card", "debit card", "card skimming", "cvv"),
    "identity_theft": ("identity theft", "kyc fraud", "impersonation of identity", "stolen identity"),
    "social_media_impersonation": ("fake profile", "impersonation", "fake account", "social media"),
    "sextortion": ("sextortion", "obscene", "nude", "morphed image", "blackmail"),
    "business_email_compromise": ("business email compromise", "bec", "ceo fraud", "invoice fraud"),
    "cryptocurrency_fraud": ("cryptocurrency", "crypto", "bitcoin", "wallet address", "blockchain"),
    "investment_scam": ("investment scam", "ponzi", "fake trading", "high return"),
    "job_scam": ("job scam", "fake job", "work from home fraud", "task fraud"),
    "ecommerce_fraud": ("e-commerce", "ecommerce", "online shopping fraud", "fake seller"),
    "malware": ("malware", "trojan", "spyware", "malicious software"),
    "ransomware": ("ransomware", "encrypted files", "ransom note", "decryption key"),
    "cyber_stalking": ("cyber stalking", "stalking", "harassment online"),
    "data_theft": ("data theft", "data breach", "exfiltration", "leak of data"),
    "account_takeover": ("account takeover", "ato", "credential stuffing", "unauthorized access"),
    "online_gaming_fraud": ("gaming fraud", "online game", "in-game", "gaming scam"),
}

# Capability-area cues for query classification.
CAPABILITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "legal": ("section", "punishment", "offence", "offense", "law", "act", "sanhita",
              "bns", "bnss", "ipc", "crpc", "provision", "bailable", "cognizable",
              "certificate", "admissibility", "admissible", "electronic record",
              "proof of", "evidence act", "sakshya", "statute", "penal"),
    "forensics": ("seizure", "chain of custody", "preservation", "acquisition",
                  "forensic", "hash", "imaging", "device", "evidence", "hard disk",
                  "mobile", "extraction", "write blocker", "disk", "volatile"),
    "osint": ("osint", "ip address", "domain", "whois", "username", "geolocation",
              "social media", "open source"),
    "financial": ("upi", "transaction", "freeze", "bank", "account", "money trail",
                  "npci", "rbi", "refund", "ledger", "beneficiary",
                  "1930", "ncrp", "recall", "reversal", "chargeback", "mule",
                  "nodal", "wallet", "recovery", "helpline", "trace", "trail",
                  "fund", "remittance", "proceeds"),
    "investigation": ("procedure", "steps", "checklist", "fir", "investigation",
                      "next step", "how to investigate", "sop", "intake",
                      "complainant", "complaint", "initial report"),
}

# Recovery-domain terminology (financial-fraud recovery workflow). Used by the
# scope guardrail so recovery questions are recognised as in-domain, and as
# category cues for the recovery repository. Mix of single tokens and phrases.
RECOVERY_KEYWORDS: tuple[str, ...] = (
    "1930", "ncrp", "account freeze", "fund recall", "beneficiary tracing",
    "mule account", "chargeback", "transaction reversal", "bank nodal officer",
    "crypto asset recovery", "wallet tracing", "fund recovery",
    # single-token aliases that may appear standalone in queries
    "freeze", "recall", "reversal", "beneficiary", "nodal", "helpline", "mule",
)

# Statute aliases used in query expansion (docs/03-rag-architecture.md §3.3 node 2).
STATUTE_ALIASES: dict[str, tuple[str, ...]] = {
    "bns": ("bharatiya nyaya sanhita",),
    "bnss": ("bharatiya nagarik suraksha sanhita",),
    "bsa": ("bharatiya sakshya adhiniyam",),
    "it act": ("information technology act", "it act 2000"),
}

# Investigator/legal/forensic/financial terminology used by the scope guardrail
# to recognise in-domain questions. These are matched as stems (prefix) so plural
# and inflected forms are covered (e.g. "provision" -> "provisions", "record" ->
# "records", "transaction" -> "transactions", "investigat" -> "investigators").
INVESTIGATOR_TERMS: tuple[str, ...] = (
    # legal
    "legal", "law", "statut", "section", "clause", "provision", "offen", "penal",
    "punish", "bailable", "cognizable", "prosecut", "charg", "warrant",
    "jurisdiction", "liabilit", "convict", "accus", "suspect",
    # unauthorised access / computer crime
    "unauthor", "intrus", "hack", "breach", "access", "computer", "network",
    "contaminant", "virus", "exfiltrat", "tamper",
    # sexual / child exploitation
    "sexual", "exploit", "obscene", "pornograph", "csam", "minor", "child",
    "pocso", "harass", "stalk", "sextort", "voyeur", "morph",
    # records / preservation / service providers / forensics
    "record", "preserv", "retention", "subscriber", "service", "provid",
    "platform", "telecom", "metadata", "seiz", "custod", "forens", "acquisition",
    "imaging", "device", "digital", "intermediar",
    # complainant / reporting
    "complain", "victim", "report", "register", "intake", "statement", "witness",
    "informant",
    # financial / recovery
    "trace", "trail", "fund", "money", "transaction", "transfer", "remittance",
    "beneficiar", "freeze", "recall", "reversal", "chargeback", "mule", "account",
    "bank", "payment", "wallet", "ledger", "recover", "launder", "nodal",
    "helpline", "proceeds",
    # investigation general
    "investigat", "evidence", "arrest", "procedure", "checklist", "escalat",
    "modus", "attribut",
    # crime types
    "phish", "vish", "smish", "malware", "ransom", "extort", "impersonat",
    "deepfake", "crypto", "romance", "loan", "trading", "gambling", "identity",
    "espionage", "ecommerce", "investment", "fraud", "scam", "fake", "cyber",
    "offence", "spoof", "skimming",
)

# Crime-term synonyms used to expand the query so lexical retrieval can bridge
# everyday phrasing to the wording used in statutes/SOPs.
CRIME_SYNONYMS: dict[str, tuple[str, ...]] = {
    "malware": ("malicious software", "computer contaminant", "virus", "trojan"),
    "phishing": ("spoofed", "fraudulent", "fake login", "identity theft", "cheating by personation"),
    "unauthorized access": ("unauthorised access", "hacking", "computer related offence", "without permission"),
    "unauthorised access": ("hacking", "computer related offence", "without permission"),
    "sexual exploitation": ("obscene", "pornographic", "csam", "child", "sexually explicit"),
    "service provider": ("intermediary", "platform", "telecom", "subscriber", "ip logs"),
    "trace funds": ("money trail", "transaction trail", "beneficiary", "financial trail"),
    "mule account": ("mule account investigation", "layered account", "downstream account"),
    "mule": ("mule account investigation",),
    "trace funds": ("beneficiary tracing", "money trail", "transaction trail"),
    "trace": ("beneficiary tracing", "transaction trail"),
    "trading scam": ("fake trading platform", "investment fraud"),
    "loan app": ("instant loan", "loan application fraud"),
    # Bare crime-name cues that steer decision-tree queries to the right tree.
    "trading": ("trading scam",),
    "romance": ("romance scam",),
    "loan": ("loan app fraud", "loan application"),
    "gambling": ("online gambling fraud",),
    "deepfake": ("deepfake fraud",),
    "sextortion": ("sextortion",),
    # Job-fraud aliases -> Fake Job Scam decision tree.
    "job fraud": ("fake job scam", "job scam"),
    "online job": ("fake job scam", "job scam"),
    "employment fraud": ("fake job scam", "job scam"),
    "work from home": ("fake job scam", "job scam"),
    "job offer": ("fake job scam", "job scam"),
    # Evidence-law cues -> BSA admissibility/certificate.
    "electronic evidence": ("admissibility", "certificate", "electronic record", "section 63"),
    "digital evidence certificate": ("admissibility", "section 63"),
}

# Default abstention message — must be returned verbatim when unsupported.
ABSTENTION_MESSAGE = "Information not found in approved knowledge sources."

# Mandatory disclaimer appended to every grounded answer.
DISCLAIMER = (
    "This is decision-support guidance. Verify against the cited source and "
    "applicable law before taking any investigative or legal action."
)
