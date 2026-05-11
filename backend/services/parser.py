import pdfplumber
import docx
import io

def parse_cv(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        text = _parse_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        text = _parse_docx(file_bytes)
    else:
        text = ""

    return _clean_text(text)


def _parse_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def _parse_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def _clean_text(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if len(line) > 1:
            cleaned.append(line)
    return "\n".join(cleaned)