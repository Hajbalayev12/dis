import pdfplumber
import docx
import io
import re
from typing import Dict

SECTION_HEADERS = {
    "experience": [
        "experience", "work experience", "employment history",
        "professional experience", "career history", "work history"
    ],
    "education": [
        "education", "academic background", "qualifications",
        "academic qualifications", "educational background"
    ],
    "skills": [
        "skills", "technical skills", "core competencies",
        "competencies", "technologies", "tech stack", "tools"
    ],
    "summary": [
        "summary", "profile", "objective", "about me",
        "professional summary", "career objective"
    ],
    "projects": [
        "projects", "personal projects", "key projects", "portfolio"
    ],
    "certifications": [
        "certifications", "certificates", "courses", "training"
    ],
    "languages": [
        "languages", "spoken languages"
    ],
}


def parse_cv(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        text = _parse_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        text = _parse_docx(file_bytes)
    else:
        text = ""

    return _clean_text(text)


def parse_cv_sections(file_bytes: bytes, filename: str) -> Dict[str, str]:
    """Parse CV and return a dict with detected sections."""
    full_text = parse_cv(file_bytes, filename)
    sections  = _split_sections(full_text)
    sections["full"] = full_text
    return sections


def _parse_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def _parse_docx(file_bytes: bytes) -> str:
    doc  = docx.Document(io.BytesIO(file_bytes))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def _clean_text(text: str) -> str:
    lines   = text.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if len(line) > 1:
            cleaned.append(line)
    return "\n".join(cleaned)


def _split_sections(text: str) -> Dict[str, str]:
    """Detect and split CV into named sections."""
    lines   = text.split("\n")
    sections = {key: "" for key in SECTION_HEADERS}
    current_section = "summary"

    for line in lines:
        line_lower = line.strip().lower()

        matched_section = None
        for section_key, headers in SECTION_HEADERS.items():
            if any(line_lower == h or line_lower.startswith(h) for h in headers):
                matched_section = section_key
                break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section] += line + "\n"

    # Clean each section
    for key in sections:
        sections[key] = sections[key].strip()

    return sections