"""Stage 2 — cleaning / normalization (docs/04 §4.2). Pure stdlib."""
from __future__ import annotations

import re

_MULTISPACE = re.compile(r"[ \t]+")
_MULTINEWLINE = re.compile(r"\n{3,}")
_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")
_PAGE_NUM_LINE = re.compile(r"^\s*(page\s+)?\d+\s*$", re.IGNORECASE | re.MULTILINE)
# Academic footnote reference markers like "[42]" litter the SOP source. They are
# not knowledge content, and — critically — the grounding verifier parses "[n]"
# as a citation marker, so a passage quoted verbatim (by the LLM or the dev stub)
# smuggles the source's footnote numbers into the answer and trips the gate. Strip
# them here. The negative lookarounds spare "[[PAGE n]]" chunker markers.
_FOOTNOTE_MARK = re.compile(r"(?<!\[)\[\d{1,4}\](?!\])")

# Common OCR repairs (extend as the corpus dictates).
_OCR_FIXES = {
    "Sec1ion": "Section",
    "Sect1on": "Section",
    "lnformation": "Information",
    "0ffence": "Offence",
}


def clean_text(text: str) -> str:
    for bad, good in _OCR_FIXES.items():
        text = text.replace(bad, good)
    text = _HYPHEN_BREAK.sub(r"\1\2", text)        # de-hyphenate across line breaks
    text = _PAGE_NUM_LINE.sub("", text)             # strip bare page-number lines
    text = _FOOTNOTE_MARK.sub("", text)             # strip "[n]" footnote references
    text = _MULTISPACE.sub(" ", text)
    text = _MULTINEWLINE.sub("\n\n", text)
    return text.strip()


def strip_repeated_lines(pages_text: list[str], min_repeat: int = 3) -> list[str]:
    """Remove headers/footers that repeat across many pages."""
    from collections import Counter

    counts: Counter[str] = Counter()
    for pt in pages_text:
        for line in pt.splitlines():
            s = line.strip()
            if 3 <= len(s) <= 80:
                counts[s] += 1
    boilerplate = {line for line, c in counts.items() if c >= min_repeat}
    cleaned = []
    for pt in pages_text:
        kept = [ln for ln in pt.splitlines() if ln.strip() not in boilerplate]
        cleaned.append("\n".join(kept))
    return cleaned
