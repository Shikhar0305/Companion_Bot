"""Shared test fixtures: a seeded, dependency-free pipeline."""
from __future__ import annotations

import pytest

from ingestion.embed import embed_and_load
from ingestion.pipeline import SourceSpec, process_text
from rag.graph import AnswerPipeline
from rag.services import build_services

LEGAL = """Section 66C. Punishment for identity theft. Whoever, fraudulently or
dishonestly makes use of the electronic signature, password or any other unique
identification feature of any other person, shall be punished with imprisonment
which may extend to three years and shall also be liable to fine.

Section 66D. Punishment for cheating by personation by using computer resource.
Whoever, by means of any communication device or computer resource cheats by
personation, shall be punished with imprisonment which may extend to three years
and shall also be liable to fine."""

SOP = """4.1 Preservation of Digital Evidence. Do not operate the suspect device.
Isolate it from networks, photograph the screen, and maintain chain of custody
from the point of seizure.

4.2 UPI Fraud Money Trail. Identify the beneficiary VPA and bank, and issue a
freeze request to the beneficiary bank without delay. Record all transaction IDs."""


def seed_services():
    services = build_services(
        embedder_name="hash", vector_store_name="memory",
        reranker_name="noop", llm_profile="stub",
    )
    chunks = process_text(LEGAL, SourceSpec(
        path="", doc_id="itact2000", title="Information Technology Act, 2000",
        doc_type="act", issuing_authority="GoI", version="2000"))
    chunks += process_text(SOP, SourceSpec(
        path="", doc_id="sopcchq", title="Cyber Crime Investigation SOP",
        doc_type="sop", issuing_authority="CCHQ", version="2023"))
    embed_and_load(chunks, services.embedder, services.vector_store)
    return services


@pytest.fixture()
def services():
    return seed_services()


@pytest.fixture()
def pipeline(services):
    return AnswerPipeline(services)
