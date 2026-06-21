"""Stage 1 — extraction (docs/04 §4.2).

Native-text PDFs via PyMuPDF; scanned pages via OCR (OCRmyPDF/Tesseract +
PaddleOCR/Docling for tables). Heavy deps imported lazily so the rest of the
pipeline (and tests) load without them. Output: per-page text with provenance.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Page:
    page_number: int
    text: str
    needs_ocr: bool = False


def extract_pdf(path: str, ocr_lang: str = "eng+hin") -> list[Page]:
    """Extract text per page; OCR pages that lack a usable text layer."""
    import fitz  # PyMuPDF, lazy

    pages: list[Page] = []
    doc = fitz.open(path)
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text") or ""
        if len(text.strip()) < 40:  # likely scanned → OCR
            text = _ocr_page(page, ocr_lang)
            pages.append(Page(i, text, needs_ocr=True))
        else:
            pages.append(Page(i, text, needs_ocr=False))
    doc.close()
    return pages


def _ocr_page(page, ocr_lang: str) -> str:
    """OCR a single rasterized page. Lazy imports keep this optional."""
    import io

    import pytesseract  # lazy
    from PIL import Image  # lazy

    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang=ocr_lang)


def pages_to_text(pages: list[Page]) -> str:
    """Join pages with page markers used to recover citation page numbers."""
    return "\n".join(f"[[PAGE {p.page_number}]]\n{p.text}" for p in pages)


def extract_markdown(path: str) -> str:
    """Read a Markdown (.md) file as raw text. Pure stdlib — no page markers.

    Markdown is already structured text, so there is no OCR/extraction step;
    the heading hierarchy is preserved for the structure-aware chunker.
    """
    with open(path, encoding="utf-8") as fh:
        return fh.read()
