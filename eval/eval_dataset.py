"""Labelled end-to-end evaluation dataset for the API QA harness.

Each case carries the query, its category, the expected repository, and (for
decision-tree cases) the specific tree expected. Categories:
  legal         -> answer should cite the legal repository (act/sanhita)
  recovery      -> answer should cite the recovery repository
  decision_tree -> answer should cite the matching crime decision tree
  refusal       -> query is out of domain and must be refused
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalCase:
    query: str
    category: str               # legal | recovery | decision_tree | refusal
    expected_repo: str          # legal | recovery | decision_tree | refused
    expected_doc: str | None = None   # for decision_tree: substring of the tree doc_id


EVAL_CASES: list[EvalCase] = [
    # --- Legal -------------------------------------------------------------
    EvalCase("What legal provisions apply to unauthorized computer access?", "legal", "legal"),
    EvalCase("What legal provisions apply to malware deployment?", "legal", "legal"),
    EvalCase("What legal provisions apply to phishing attacks?", "legal", "legal"),
    EvalCase("What legal provisions apply to online sexual exploitation?", "legal", "legal"),
    EvalCase("What is the punishment for identity theft under the IT Act?", "legal", "legal"),
    EvalCase("Which section covers cheating by personation using a computer resource?", "legal", "legal"),
    EvalCase("What is the certificate requirement for electronic evidence?", "legal", "legal"),
    EvalCase("What does the law say about criminal breach of trust?", "legal", "legal"),
    EvalCase("What are the mandatory reporting provisions for child sexual abuse material?", "legal", "legal"),
    EvalCase("What are the penalties under the data protection law?", "legal", "legal"),
    # --- Recovery ----------------------------------------------------------
    EvalCase("What is the 1930 helpline used for?", "recovery", "recovery"),
    EvalCase("How do I freeze a beneficiary account?", "recovery", "recovery"),
    EvalCase("How does fund recall work?", "recovery", "recovery"),
    EvalCase("How do I trace a mule account chain?", "recovery", "recovery"),
    EvalCase("How can crypto assets be recovered?", "recovery", "recovery"),
    EvalCase("What is the NCRP workflow for a fraud complaint?", "recovery", "recovery"),
    EvalCase("How is beneficiary tracing carried out?", "recovery", "recovery"),
    # --- Decision trees ----------------------------------------------------
    EvalCase("What are the steps to investigate UPI banking fraud?", "decision_tree", "decision_tree", "01_upi_banking_fraud"),
    EvalCase("What is the decision tree for romance scam?", "decision_tree", "decision_tree", "10_romance_scam"),
    EvalCase("How to investigate fake loan application fraud?", "decision_tree", "decision_tree", "05_loan_app_fraud"),
    EvalCase("How to investigate fake trading platform fraud?", "decision_tree", "decision_tree", "04_trading_scam"),
    EvalCase("How do I investigate a sextortion case?", "decision_tree", "decision_tree", "06_sextortion"),
    EvalCase("What is the investigation flow for ransomware?", "decision_tree", "decision_tree", "14_ransomware"),
    EvalCase("How to investigate a SIM swap fraud?", "decision_tree", "decision_tree", "16_sim_swap_fraud"),
    EvalCase("How to handle a digital arrest scam?", "decision_tree", "decision_tree", "02_digital_arrest_scam"),
    EvalCase("How to investigate business email compromise?", "decision_tree", "decision_tree", "15_business_email_compromise_bec"),
    EvalCase("How to investigate crypto fraud?", "decision_tree", "decision_tree", "17_crypto_fraud"),
    # --- Refusals ----------------------------------------------------------
    EvalCase("What is the weather today?", "refusal", "refused"),
    EvalCase("Who won the cricket match?", "refusal", "refused"),
    EvalCase("Recommend a good movie.", "refusal", "refused"),
    EvalCase("Best travel destinations in Europe?", "refusal", "refused"),
    EvalCase("How do I cook biryani?", "refusal", "refused"),
    EvalCase("Tell me a joke.", "refusal", "refused"),
    EvalCase("What is the capital of France?", "refusal", "refused"),
    EvalCase("What is the stock price of Tesla?", "refusal", "refused"),
]
