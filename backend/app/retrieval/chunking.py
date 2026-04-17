from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class CVChunk:
    chunk_id: str
    section: str
    text: str


SECTION_HEADERS = [
    "experience",
    "work experience",
    "projects",
    "skills",
    "education",
    "certifications",
    "summary",
]


def detect_section(line: str) -> str | None:
    lowered = line.strip().lower()
    for section in SECTION_HEADERS:
        if lowered == section:
            return section.replace(" ", "_")
    return None


def section_aware_chunk_cv(cv_text: str, candidate_id: str, max_chars: int = 800) -> List[CVChunk]:
    lines = cv_text.splitlines()
    section = "general"
    buffer: List[str] = []
    chunks: List[CVChunk] = []
    chunk_index = 0

    for line in lines:
        detected = detect_section(line)
        if detected:
            if buffer:
                text = "\n".join(buffer).strip()
                if text:
                    chunks.append(CVChunk(f"{candidate_id}:{chunk_index}", section, text))
                    chunk_index += 1
                buffer = []
            section = detected
            continue

        buffer.append(line)
        if sum(len(x) for x in buffer) >= max_chars:
            text = "\n".join(buffer).strip()
            if text:
                chunks.append(CVChunk(f"{candidate_id}:{chunk_index}", section, text))
                chunk_index += 1
            buffer = []

    if buffer:
        text = "\n".join(buffer).strip()
        if text:
            chunks.append(CVChunk(f"{candidate_id}:{chunk_index}", section, text))

    return chunks


def expand_query_terms(query: str) -> List[str]:
    synonyms = {
        "llmops": ["model deployment", "inference pipeline", "serving"],
        "kubernetes": ["k8s", "container orchestration"],
        "rag": ["retrieval augmented generation", "vector search", "bm25"],
    }
    tokens = re.findall(r"[a-zA-Z0-9\+\-]+", query.lower())
    expanded = [query]
    for token in tokens:
        if token in synonyms:
            expanded.extend(synonyms[token])
    return expanded
