from pathlib import Path

from pdf_processor import extract_text_from_pdf
from chunker import create_chunks


pdf_files = list(Path("../uploads").glob("*.pdf"))

if not pdf_files:
    raise FileNotFoundError("No PDF found in uploads folder.")


pdf_path = pdf_files[0]

pages = extract_text_from_pdf(str(pdf_path))

print(f"PDF: {pdf_path.name}")
print(f"Total pages: {len(pages)}")


chunks = create_chunks(pages)

print(f"Total chunks: {len(chunks)}")


for chunk in chunks:

    print("\\n" + "=" * 60)
    print(f"CHUNK {chunk["chunk_id"]}")
    print(f"PAGE: {chunk["page_number"]}")
    print("=" * 60)
    print(chunk["text"])
