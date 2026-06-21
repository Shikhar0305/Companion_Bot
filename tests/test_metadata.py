from core.types import Chunk
from ingestion.metadata import detect_capability_areas, detect_categories, tag_chunk


def test_detect_categories():
    cats = detect_categories("This concerns a UPI fraud with a fraudulent VPA collect request")
    assert "upi_fraud" in cats


def test_detect_capability_legal():
    areas = detect_capability_areas("Punishment under section 66D of the act", "act")
    assert "legal" in areas


def test_detect_capability_default_when_no_cue():
    areas = detect_capability_areas("xyzzy plover", "manual")
    assert areas == ["forensics"]


def test_tag_chunk_populates_fields():
    c = Chunk(chunk_id="x", doc_id="d", doc_type="sop", title="SOP",
              text="Issue a freeze request to the beneficiary bank for the UPI transaction.")
    tag_chunk(c, issuing_authority="CCHQ", version="2023")
    assert c.issuing_authority == "CCHQ"
    assert "upi_fraud" in c.cybercrime_categories
    assert c.capability_area  # non-empty
