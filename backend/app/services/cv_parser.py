import io
import os
import time
import logging
from typing import List, Dict, Any
import fitz  # PyMuPDF
import pymupdf4llm


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Text Cleaning
# ---------------------------------------------------------------------------

def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace('\x00', '')
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join([line for line in lines if line])


# ---------------------------------------------------------------------------
# Primary Extraction — pymupdf4llm (Built-in layout/table extraction)
# ---------------------------------------------------------------------------

def _extract_text_pymupdf4llm(file_bytes: bytes) -> str:
    """
    Primary extraction using the built-in pymupdf4llm library.
    It natively handles markdown formatting, tables, and attempts to group columns.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        md_text = pymupdf4llm.to_markdown(doc)
        doc.close()
        return md_text
    except Exception as e:
        logger.error(f"pymupdf4llm extraction failed: {e}")
        return ""

# ---------------------------------------------------------------------------
# Hyperlink Extraction — PyMuPDF (fitz)
# ---------------------------------------------------------------------------

def _extract_hyperlinks(file_bytes: bytes) -> str:
    """
    Extract hyperlinks from PDF annotations using PyMuPDF (fitz).
    These are URLs hidden behind clickable text (e.g., "LinkedIn" linking to a profile URL).
    """
    try:
        all_links = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        for page_num, page in enumerate(doc, 1):
            page_links = []
            seen_uris = set()
            
            for link in page.links():
                uri = link.get("uri", "")
                if uri and uri.startswith(("http", "mailto", "www")) and uri not in seen_uris:
                    seen_uris.add(uri)
                    page_links.append(uri)
                    
            if page_links:
                all_links.append(f"\n--- Hyperlinks Found on Page {page_num} ---")
                all_links.append("\n".join(page_links))
                
        doc.close()
        return "\n".join(all_links)
    except Exception as e:
        logger.error(f"Hyperlink extraction failed: {e}")
        return ""

# ---------------------------------------------------------------------------
# Debug Dump
# ---------------------------------------------------------------------------

def _dump_extracted_text(text: str, original_filename: str):
    """Saves extracted text to a file for comparison/debugging."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        dump_dir = os.path.join(project_root, "Playground", "cv_extractions")
        os.makedirs(dump_dir, exist_ok=True)

        timestamp = int(time.time())
        safe_filename = original_filename.replace(" ", "_").replace("/", "_")
        dump_path = os.path.join(dump_dir, f"{timestamp}_{safe_filename}.txt")

        with open(dump_path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"Saved extracted CV raw text to: {dump_path}")
    except Exception as e:
        logger.error(f"Failed to dump extracted text: {e}")

# ---------------------------------------------------------------------------
# Public Entry Point
# ---------------------------------------------------------------------------

def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Unified entry point for CV text extraction.
    """
    ext = filename.lower().split('.')[-1]

    if ext != 'pdf':
        logger.warning(f"Unsupported file extension: {ext}. Only PDF is supported.")
        return ""

    # 1. Primary: Built-in library (pymupdf4llm)
    text = _extract_text_pymupdf4llm(file_bytes)

    # 2. Enrich: Add hidden hyperlinks
    links = _extract_hyperlinks(file_bytes)

    # 3. Combine
    parts = [p for p in [text, links] if p.strip()]
    combined = "\n\n".join(parts)

    # 4. Clean and Dump
    final_text = _clean_text(combined)
    if final_text:
        _dump_extracted_text(final_text, filename)

    return final_text
