from ingestion.chunk import chunk_document, chunk_legal, chunk_sop

LEGAL = """Section 43A. Compensation for failure to protect data. Where a body
corporate is negligent, it shall be liable to pay damages.

Section 66. Computer related offences. If any person dishonestly or
fraudulently does any act referred to in section 43, he shall be punishable."""

# Real-manual layout: each numbered heading on its own line, followed by prose.
# (Heading-only / Table-of-Contents fragments are intentionally dropped by
# chunk_sop, so a realistic section needs a body paragraph beneath the heading.)
SOP = """4.1 Device Seizure
Isolate the device from all networks and photograph the screen before doing
anything else. Record the make, model, and state, then log the seizure and
maintain chain of custody from this point onward.

4.2 Acquisition
Create a forensic image of the seized media and record the hash value so the
integrity of the evidence can be verified later before the court."""


def test_legal_chunks_on_section_boundaries():
    chunks = chunk_legal(LEGAL, "itact", "IT Act", "act")
    assert len(chunks) == 2
    secs = {c.section_number for c in chunks}
    assert secs == {"43A", "66"}
    # Section number appears within its own chunk (citation integrity).
    for c in chunks:
        assert c.section_number.lower() in c.text.lower()
        assert c.parent_chunk_id  # small-to-big pointer set


def test_legal_chunk_not_split_midsection():
    chunks = chunk_legal(LEGAL, "itact", "IT Act", "act")
    s66 = next(c for c in chunks if c.section_number == "66")
    assert "section 43" in s66.text.lower()  # body kept intact


def test_sop_chunks_on_headings():
    chunks = chunk_sop(SOP, "sop", "SOP", "sop")
    assert len(chunks) == 2
    assert {c.sop_section for c in chunks} == {"4.1", "4.2"}
    assert all(c.procedure_name for c in chunks)


def test_chunk_document_dispatches_by_type():
    assert chunk_document(LEGAL, "d", "t", "sanhita")[0].section_number == "43A"
    assert chunk_document(SOP, "d", "t", "manual")[0].sop_section == "4.1"
