from pathlib import Path

from pdf_processor import extract_text_from_pdf
from chunker import create_chunks
from embeddings import generate_embeddings
from vector_store import VectorStore


pdf_files = list(Path("../uploads").glob("*.pdf"))

if not pdf_files:
    raise FileNotFoundError("No PDF found in uploads folder.")


pdf_path = pdf_files[0]

pages = extract_text_from_pdf(str(pdf_path))

chunks = create_chunks(pages)

texts = [chunk["text"] for chunk in chunks]

embeddings = generate_embeddings(texts)


dimension = embeddings.shape[1]

vector_store = VectorStore(dimension)

vector_store.add(
    embeddings,
    chunks
)


query = "What is this document about?"

query_embedding = generate_embeddings([query])[0]

results = vector_store.search(
    query_embedding,
    top_k=3
)


print("\\nQuery:", query)
print("Results:", len(results))


for i, result in enumerate(results, start=1):

    print("\\n" + "=" * 60)
    print(f"RESULT {i}")
    print("=" * 60)
    print("Similarity:", result["score"])
    print("Page:", result["chunk"]["page_number"])
    print("Text:", result["chunk"]["text"])
