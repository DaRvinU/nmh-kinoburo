
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 15 * 1024 * 1024


def validate_file(uploaded_file):
    if uploaded_file is None:
        raise ValueError("Файл не выбран")

    extension = Path(uploaded_file.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Поддерживаются только PDF, DOCX и TXT")

    content = uploaded_file.getvalue()

    if not content:
        raise ValueError("Файл пустой")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Размер файла не должен превышать 15 МБ")

    return content, extension


def extract_text(uploaded_file):
    content, extension = validate_file(uploaded_file)

    if extension == ".pdf":
        reader = PdfReader(BytesIO(content))
        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)

        result = "\n".join(pages)

    elif extension == ".docx":
        document = Document(BytesIO(content))
        result = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

    else:
        result = content.decode("utf-8-sig", errors="replace")

    result = result.strip()

    if not result:
        raise ValueError(
            "Не удалось извлечь текст. Возможно, PDF состоит из сканов."
        )

    return result
