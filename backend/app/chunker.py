import re


def clean_text(text: str) -> str:
    # Replace all whitespace (spaces, tabs, newlines) with one space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def create_chunks(
    pages,
    chunk_size: int = 1000,
    overlap: int = 200
):
    chunks = []

    chunk_id = 0

    for page in pages:

        text = clean_text(page["text"])

        # Skip empty pages
        if not text:
            continue

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append({
                    "chunk_id": chunk_id,
                    "page_number": page["page_number"],
                    "text": chunk_text
                })

                chunk_id += 1

            start += chunk_size - overlap

    return chunks
