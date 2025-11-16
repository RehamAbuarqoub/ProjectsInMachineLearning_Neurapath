from pathlib import Path
import pdfplumber

# Try to import python-docx safely
try:
    import docx  # provided by the 'python-docx' package
except ImportError:
    docx = None  # we'll handle this gracefully below


def extract_text(file_path: Path) -> str:
    """
    Extract text from a file based on its extension.
    Supports: .txt, .md, .csv, .docx, .pdf
    Falls back to plain text read for unknown extensions.
    """
    suffix = file_path.suffix.lower()

    # Simple text-like files
    if suffix in [".txt", ".md", ".csv"]:
        return file_path.read_text(encoding="utf-8", errors="ignore")

    # DOCX files
    if suffix == ".docx":
        return _from_docx(file_path)

    # PDF files
    if suffix == ".pdf":
        return _from_pdf(file_path)

    # Fallback: just read as text
    return file_path.read_text(encoding="utf-8", errors="ignore")


def _from_docx(p: Path) -> str:
    """
    Extract text from a .docx file.
    Requires the 'python-docx' package.
    """
    if docx is None:
        # This prevents the whole backend from crashing on import
        raise RuntimeError(
            "DOCX support requires the 'python-docx' package. "
            "Install it with: pip install python-docx"
        )

    d = docx.Document(str(p))
    return "\n".join(para.text for para in d.paragraphs)


def _from_pdf(p: Path) -> str:
    """
    Extract text from a .pdf file using pdfplumber.
    """
    text_chunks = []
    with pdfplumber.open(str(p)) as pdf:
        for page in pdf.pages:
            text_chunks.append(page.extract_text() or "")
    return "\n".join(text_chunks)
