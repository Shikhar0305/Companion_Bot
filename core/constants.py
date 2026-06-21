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
              "bns", "bnss", "ipc", "crpc", "provision", "bailable", "cognizable"),
    "forensics": ("seizure", "chain of custody", "preservation", "acquisition",
                  "forensic", "hash", "imaging", "device", "evidence", "hard disk"),
    "osint": ("osint", "ip address", "domain", "whois", "username", "geolocation",
              "social media", "open source"),
    "financial": ("upi", "transaction", "freeze", "bank", "account", "money trail",
                  "npci", "rbi", "refund", "ledger", "beneficiary"),
    "investigation": ("procedure", "steps", "checklist", "fir", "investigation",
                      "next step", "how to investigate", "sop"),
}

# Statute aliases used in query expansion (docs/03-rag-architecture.md §3.3 node 2).
STATUTE_ALIASES: dict[str, tuple[str, ...]] = {
    "bns": ("bharatiya nyaya sanhita",),
    "bnss": ("bharatiya nagarik suraksha sanhita",),
    "bsa": ("bharatiya sakshya adhiniyam",),
    "it act": ("information technology act", "it act 2000"),
}

# Default abstention message — must be returned verbatim when unsupported.
ABSTENTION_MESSAGE = "Information not found in approved knowledge sources."

# Mandatory disclaimer appended to every grounded answer.
DISCLAIMER = (
    "This is decision-support guidance. Verify against the cited source and "
    "applicable law before taking any investigative or legal action."
)
