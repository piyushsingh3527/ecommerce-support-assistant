from pathlib import Path
from docx import Document
import pymupdf


def read_text_file(file_path: str) -> str:
    path = Path(file_path)
    return path.read_text(encoding="utf-8")


def read_pdf_file(file_path: str) -> str:
    document = pymupdf.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text

def read_docx_file(file_path: str) -> str:
    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:
        text.append(paragraph.text)

    return "\n".join(text)


def read_document(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension in {".txt", ".md"}:
        return read_text_file(file_path)

    if extension == ".pdf":
        return read_pdf_file(file_path)

    if extension == ".docx":
        return read_docx_file(file_path)

    raise ValueError("Unsupported document type")