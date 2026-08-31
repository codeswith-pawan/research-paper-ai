from pathlib import Path

from app.pdf_processor import extract_text_from_pdf
from app.chunker import create_chunks


UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"


def get_pdf_files():
    return list(UPLOAD_DIR.glob("*.pdf"))


def test_pdf_extraction_returns_pages():
    pdf_files = get_pdf_files()

    assert pdf_files, "No PDF found in uploads directory."

    pages = extract_text_from_pdf(str(pdf_files[0]))

    assert isinstance(pages, list)
    assert len(pages) > 0

    for page in pages:
        assert "page_number" in page
        assert "text" in page


def test_pdf_extraction_and_chunking_produce_text():
    pdf_files = get_pdf_files()

    assert pdf_files, "No PDF found in uploads directory."

    pages = extract_text_from_pdf(str(pdf_files[0]))
    chunks = create_chunks(pages)

    assert len(chunks) > 0

    for chunk in chunks:
        assert chunk["text"].strip()
        assert chunk["page_number"] >= 1
