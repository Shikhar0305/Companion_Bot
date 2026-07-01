"""Stage 3 — structure-aware chunking (docs/04 §4.2/§4.3). Pure stdlib.

Legal acts/sanhitas chunk on section boundaries (never split a section).
SOPs/manuals chunk on heading hierarchy. A page-marker map (``[[PAGE n]]``)
emitted by extraction is used to recover citation page numbers.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from core.types import Chunk
from ingestion.sop_classify import classify as _classify_sop

_PAGE_MARK = re.compile(r"\[\[PAGE (\d+)\]\]")
# Markdown ATX heading: capture level (#) and heading text.
_MD_HEADING = re.compile(r"(?m)^(#{1,6})\s+(.+?)\s*#*$")
# "**Section Number:** 66C" inside the legal-repository markdown.
_MD_SECNO = re.compile(r"\*\*Section Number:\*\*\s*([0-9]+[A-Za-z]{0,3})", re.IGNORECASE)
# "... Section 66C — Title" embedded in a heading line (legal repository).
_MD_HEAD_SECNO = re.compile(r"Section\s+([0-9]+[A-Za-z]{0,3})\b", re.IGNORECASE)
# "Section 66D. Title" / "66A. Title" / "Section 4." etc.
_SECTION = re.compile(
    r"(?:^|\n)\s*(?:Section\s+)?(\d+[A-Z]{0,2})\.\s+(.{0,120}?)(?=\n)",
    re.IGNORECASE,
)
# SOP heading: "4.2 Device Seizure", "4 Investigation Procedure", or ALLCAPS line.
_SOP_HEADING = re.compile(
    r"(?:^|\n)\s*(\d+(?:\.\d+){0,2})\s+([A-Z][^\n]{3,90})",
)
# A section needs at least this much prose (beyond its heading line) to be kept;
# heading-only / Table-of-Contents fragments fall below it and are dropped.
_SOP_MIN_PROSE = 80
# Sections longer than this are split into overlapping windows for retrieval.
_SOP_MAX_CHARS = 4000


def _window(text: str, size: int, overlap: int = 200) -> list[str]:
    """Split long text into overlapping windows, preferring whitespace breaks."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        end = min(i + size, n)
        if end < n:  # back off to the nearest whitespace so we don't cut a word
            ws = text.rfind(" ", i + size - overlap, end)
            if ws > i:
                end = ws
        out.append(text[i:end].strip())
        if end >= n:
            break
        i = max(end - overlap, i + 1)
    return [w for w in out if w]


def _hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


def _page_for_offset(text: str, offset: int) -> int | None:
    last = None
    for m in _PAGE_MARK.finditer(text):
        if m.start() <= offset:
            last = int(m.group(1))
        else:
            break
    return last


def _strip_page_marks(text: str) -> str:
    return _PAGE_MARK.sub("", text).strip()


@dataclass
class _Span:
    start: int
    end: int
    label: str
    title: str


def chunk_legal(text: str, doc_id: str, title: str, doc_type: str = "act") -> list[Chunk]:
    """One chunk per section; section number/title carried as metadata."""
    matches = list(_SECTION.finditer(text))
    chunks: list[Chunk] = []
    if not matches:
        return _chunk_fallback(text, doc_id, title, doc_type)
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = _strip_page_marks(text[start:end])
        sec_no = m.group(1).strip()
        sec_title = m.group(2).strip().rstrip(".")
        page = _page_for_offset(text, start)
        cid = f"{doc_id}_sec_{sec_no.lower()}"
        chunks.append(
            Chunk(
                chunk_id=cid, doc_id=doc_id, doc_type=doc_type, title=title,
                text=body, section_number=sec_no, section_title=sec_title,
                page_start=page, page_end=page,
                parent_chunk_id=f"{doc_id}_sec_{sec_no.lower()}_full",
                source_hash=_hash(body),
            )
        )
    return chunks


def chunk_sop(text: str, doc_id: str, title: str, doc_type: str = "sop") -> list[Chunk]:
    """Chunk by numbered-heading hierarchy; keep a procedure's steps together.

    Robust against real-world manuals: a multi-page Table of Contents and
    parent headings whose body is only their child subsections both yield
    "heading-only" fragments (no prose) — these are dropped, which also removes
    the duplicate section numbers the TOC would otherwise inject. Oversized
    sections (e.g. a chapter conclusion running into un-numbered annexures) are
    split into overlapping windows. chunk_ids are guaranteed unique.
    """
    matches = list(_SOP_HEADING.finditer(text))
    if not matches:
        return _chunk_fallback(text, doc_id, title, doc_type)
    chunks: list[Chunk] = []
    seen: set[str] = set()
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = _strip_page_marks(text[start:end])
        # Prose below the heading line — TOC entries and bare parent headings
        # have (almost) none, so we skip them to avoid noise + duplicate ids.
        nl = body.find("\n")
        prose = body[nl + 1:].strip() if nl != -1 else ""
        if len(prose) < _SOP_MIN_PROSE:
            continue
        sec = m.group(1).strip()
        name = m.group(2).strip()
        page_start = _page_for_offset(text, start)
        page_end = _page_for_offset(text, max(start, end - 1)) or page_start
        base = f"{doc_id}_sop_{sec.replace('.', '_')}"
        meta = _classify_sop(sec, name)  # heading-anchored section_type/priority/...
        pieces = _window(body, _SOP_MAX_CHARS) if len(body) > _SOP_MAX_CHARS else [body]
        for j, piece in enumerate(pieces):
            cid = base if len(pieces) == 1 else f"{base}_p{j + 1}"
            if cid in seen:
                # A section number that recurs with prose (e.g. body + a later
                # recap). Disambiguate with a "__rN" suffix — the double
                # underscore cannot collide with a real subsection slug, which
                # only ever uses single underscores.
                k = 2
                while f"{cid}__r{k}" in seen:
                    k += 1
                cid = f"{cid}__r{k}"
            seen.add(cid)
            chunks.append(
                Chunk(
                    chunk_id=cid, doc_id=doc_id, doc_type=doc_type, title=title,
                    text=piece, sop_section=sec, procedure_name=name,
                    page_start=page_start, page_end=page_end,
                    parent_chunk_id=f"{base}_full", source_hash=_hash(piece),
                    section_type=meta["section_type"], priority=meta["priority"],
                    procedure_type=meta["procedure_type"], topic=meta["topic"],
                    keywords=meta["keywords"],
                )
            )
    return chunks or _chunk_fallback(text, doc_id, title, doc_type)


def _chunk_fallback(text: str, doc_id: str, title: str, doc_type: str,
                    target_chars: int = 1800, overlap: int = 200) -> list[Chunk]:
    """Sliding-window fallback when no structure is detected."""
    clean = _strip_page_marks(text)
    chunks: list[Chunk] = []
    i = 0
    idx = 0
    while i < len(clean):
        body = clean[i:i + target_chars]
        cid = f"{doc_id}_w{idx}"
        chunks.append(
            Chunk(chunk_id=cid, doc_id=doc_id, doc_type=doc_type, title=title,
                  text=body, source_hash=_hash(body))
        )
        i += target_chars - overlap
        idx += 1
    return chunks


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:48] or "x"


_MD_BLOCKQUOTE = re.compile(r"(?m)^\s*>.*$")   # provenance/risk metadata lines
_MD_HRULE = re.compile(r"(?m)^\s*-{3,}\s*$")    # horizontal rules


def _clean_md_body(text: str) -> str:
    """Strip non-content markdown noise (provenance blockquotes, rules) so the
    document front-matter does not surface as a retrievable/citable chunk."""
    text = _MD_BLOCKQUOTE.sub("", text)
    text = _MD_HRULE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_markdown(text: str, doc_id: str, title: str, doc_type: str) -> list[Chunk]:
    """Heading-aware chunking for Markdown corpus files.

    Splits on the finest heading level that delimits the body (e.g. ``###`` per
    statutory section in the legal repository, ``##`` per decision branch in a
    decision tree), keeping each section intact. Legal section numbers are read
    from the ``**Section Number:**`` line (or the heading) so downstream sidecar
    metadata can join on them.
    """
    headings = list(_MD_HEADING.finditer(text))
    if not headings:
        return _chunk_fallback(text, doc_id, title, doc_type)

    # Pick the split level: prefer the deepest level that occurs >=2 times.
    levels = [len(m.group(1)) for m in headings]
    repeated = sorted({lvl for lvl in levels if levels.count(lvl) >= 2}, reverse=True)
    split_level = repeated[0] if repeated else min(levels)

    # Chunk at the section level only; the shallower title/preamble block above
    # the first section is intentionally dropped (it is provenance boilerplate).
    boundaries = [m for m in headings if len(m.group(1)) == split_level]
    if not boundaries:
        return _chunk_fallback(text, doc_id, title, doc_type)
    is_legal = doc_type in ("act", "sanhita")
    chunks: list[Chunk] = []
    for i, m in enumerate(boundaries):
        start = m.start()
        end = boundaries[i + 1].start() if i + 1 < len(boundaries) else len(text)
        section = _clean_md_body(text[start:end])
        if len(section) < 20:
            continue
        heading = m.group(2).strip()
        # Carry the document title into the chunk text so section-level chunks
        # retain the document's topical keywords for retrieval.
        body = f"{title}\n\n{section}"
        kwargs: dict = {}
        if is_legal:
            mn = _MD_SECNO.search(section) or _MD_HEAD_SECNO.search(heading)
            sec_no = mn.group(1) if mn else None
            kwargs["section_number"] = sec_no
            kwargs["section_title"] = heading
            cid = f"{doc_id}_sec_{sec_no.lower()}" if sec_no else f"{doc_id}_md{i}"
        else:
            kwargs["procedure_name"] = heading
            cid = f"{doc_id}_{_slug(heading)}"
        chunks.append(
            Chunk(
                chunk_id=cid, doc_id=doc_id, doc_type=doc_type, title=title,
                text=body, source_hash=_hash(body),
                parent_chunk_id=f"{doc_id}_full", **kwargs,
            )
        )
    return chunks or _chunk_fallback(text, doc_id, title, doc_type)


def chunk_document(text: str, doc_id: str, title: str, doc_type: str,
                   *, is_markdown: bool = False) -> list[Chunk]:
    if is_markdown:
        return chunk_markdown(text, doc_id, title, doc_type)
    if doc_type in ("act", "sanhita"):
        return chunk_legal(text, doc_id, title, doc_type)
    if doc_type in ("sop", "manual", "playbook"):
        return chunk_sop(text, doc_id, title, doc_type)
    return _chunk_fallback(text, doc_id, title, doc_type)
