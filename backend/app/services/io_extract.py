from pathlib import Path
import pdfplumber
import docx

def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix in [".txt", ".md", ".csv"]:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    if suffix in [".docx"]:
        return _from_docx(file_path)
    if suffix in [".pdf"]:
        return _from_pdf(file_path)
    return file_path.read_text(encoding="utf-8", errors="ignore")

def _from_docx(p: Path) -> str:
    d = docx.Document(str(p))
    return "\n".join([para.text for para in d.paragraphs])

def _from_pdf(p: Path) -> str:
    text = []
    with pdfplumber.open(str(p)) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)
