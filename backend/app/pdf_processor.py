import pymupdf
import pytesseract
from PIL import Image


def extract_text_from_pdf(file_path: str):
    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        # First try normal PDF text extraction
        text = page.get_text("text").strip()

        # If the page has no selectable text, use OCR
        if not text:

            print(
                f"Page {page_number}: No embedded text found. "
                "Running OCR..."
            )

            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2)
            )

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            text = pytesseract.image_to_string(
                image,
                lang="eng"
            ).strip()

            print(
                f"Page {page_number}: OCR extracted "
                f"{len(text)} characters"
            )

        else:

            print(
                f"Page {page_number}: Extracted "
                f"{len(text)} characters from embedded text"
            )

        pages.append({
            "page_number": page_number,
            "text": text
        })

    document.close()

    return pages
