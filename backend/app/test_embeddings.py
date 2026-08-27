from pathlib import Path

from pdf_processor import extract_text_from_pdf
from chunker import create_chunks
from embeddings import generate_embeddings


pdf_files = list(Path("../uploads").glob("*.pdf"))

if not pdf_files:
    raise FileNotFoundError("No PDF found in uploads folder.")


pdf_path = pdf_files[0]

pages = extract_text_from_pdf(str(pdf_path))

chunks = create_chunks(pages)

texts = [chunk["text"] for chunk in chunks]

embeddings = generate_embeddings(texts)


print("Model: all-MiniLM-L6-v2")
print("Number of chunks:", len(chunks))
print("Embedding shape:", embeddings.shape)
print("Embedding dimension:", embeddings.shape[1])
print("First embedding:")
print(embeddings[0])
