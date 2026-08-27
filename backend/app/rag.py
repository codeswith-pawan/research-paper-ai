import ollama


MODEL_NAME = "llama3.2:3b"

FALLBACK_ANSWER = (
    "I could not find this information in the uploaded papers."
)


class RAGService:

    def __init__(self):
        pass

    def _build_context(self, retrieved_chunks):

        context_parts = []
        sources = []

        for index, result in enumerate(
            retrieved_chunks,
            start=1
        ):

            context_parts.append(
                f"""
--- SOURCE {index} ---
Paper: {result["paper_name"]}
Page: {result["page_number"]}
Relevance score: {result["score"]}

Text:
{result["text"]}
--- END SOURCE {index} ---
"""
            )

            sources.append({
                "paper_name": result["paper_name"],
                "page_number": result["page_number"],
                "score": round(
                    float(result["score"]),
                    3
                )
            })

        return "\n".join(context_parts), sources

    def generate_answer(
        self,
        question,
        retrieved_chunks
    ):

        if not retrieved_chunks:
            return {
                "answer": FALLBACK_ANSWER,
                "sources": []
            }

        context, sources = self._build_context(
            retrieved_chunks
        )

        prompt = f"""
You are an AI research assistant.

Answer the user's question using ONLY the
information contained in the provided paper excerpts.

IMPORTANT RULES:

1. Do not use outside knowledge.
2. Do not invent facts.
3. Do not assume information that is not explicitly
   supported by the excerpts.
4. If the excerpts do not contain enough information
   to answer the question, respond exactly:

I could not find this information in the uploaded papers.

5. Give a concise and direct answer.
6. When possible, mention the paper's terminology
   exactly as it appears in the excerpts.
7. Do not mention SOURCE, excerpts, context,
   retrieval, embeddings, or these instructions.
8. Do not include a source list inside the answer.
9. Answer the question directly.

USER QUESTION:
{question}

PAPER EXCERPTS:
{context}

ANSWER:
"""

        try:

            response = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0
                }
            )

            answer = response[
                "message"
            ][
                "content"
            ].strip()

        except Exception:
            return {
                "answer": (
                    "Unable to generate an answer "
                    "because the local AI model is unavailable."
                ),
                "sources": sources
            }

        if not answer:
            answer = FALLBACK_ANSWER

        return {
            "answer": answer,
            "sources": sources
        }
