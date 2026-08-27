# Research Paper AI

AI-powered research paper search and question-answering system using semantic search, hybrid retrieval, FAISS, and Retrieval-Augmented Generation (RAG).

## Overview

Research Paper AI allows users to upload research papers in PDF format and ask questions about their content.

The backend processes uploaded PDFs, extracts their text, divides the text into chunks, generates semantic embeddings, stores them in a FAISS vector index, and retrieves relevant sections for answering user questions.

The system combines:

- PDF text extraction
- Text chunking
- Semantic embeddings
- FAISS vector search
- Keyword-based retrieval
- Section-aware reranking
- Local LLM-based RAG
- Source and page tracking

## Current Status

### Backend MVP — Completed

- [x] PDF upload
- [x] Duplicate PDF detection using SHA-256 hash
- [x] SQLite paper metadata storage
- [x] PDF text extraction
- [x] Text chunking with overlap
- [x] Sentence Transformer embeddings
- [x] FAISS vector search
- [x] Hybrid semantic + keyword retrieval
- [x] Section-aware reranking
- [x] Quality penalties for weak retrieval sections
- [x] RAG-based question answering
- [x] Source/page references
- [x] Paper listing
- [x] Paper deletion
- [x] API documentation with FastAPI / Swagger

### Next

- [ ] Frontend interface
- [ ] Paper library UI
- [ ] Upload interface
- [ ] Search interface
- [ ] Chat interface
- [ ] Source/page display
- [ ] Better document-level retrieval
- [ ] Deployment

## Architecture

```text
                    Research Paper AI
                           |
                           v
                    PDF Upload API
                           |
                           v
                    SHA-256 Hash
                    /           \
             Duplicate?          New PDF
                |                   |
                v                   v
              Return          Save PDF + SQLite
                                    |
                                    v
                            PDF Text Extraction
                               (PyMuPDF)
                                    |
                                    v
                              Text Chunking
                           (1000 chars / overlap)
                                    |
                                    v
                         Sentence Transformer
                           Embeddings
                                    |
                                    v
                              FAISS Index
                                    |
                                    v
                              User Query
                                    |
                                    v
                         Query Embedding
                                    |
                                    v
                         Candidate Retrieval
                                    |
                                    v
                    Hybrid Retrieval / Reranking
                    ┌──────────┬──────────┐
                    │          │          │
                Semantic   Keyword    Section
                  Score      Score      Score
                    └──────────┴──────────┘
                             |
                             v
                       Relevant Chunks
                             |
                             v
                         RAG Service
                             |
                             v
                     Local LLM (Ollama)
                             |
                             v
                      Answer + Sources
```

## RAG Pipeline

The question-answering pipeline works as follows:

1. User submits a question.
2. The question is converted into an embedding.
3. FAISS retrieves candidate chunks using semantic similarity.
4. Candidate chunks are reranked using:
   - semantic similarity
   - keyword overlap
   - section relevance
   - quality penalties
5. The most relevant chunks are provided to the local LLM.
6. The LLM generates an answer using the retrieved paper content.
7. The API returns the answer together with paper names and page numbers.

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

### Document Processing

- PyMuPDF

### Embeddings

- Sentence Transformers
- `all-MiniLM-L6-v2`

### Vector Search

- FAISS
- Inner Product similarity with normalized embeddings

### RAG / LLM

- Ollama
- `llama3.2:3b`

### Database

- SQLite

### Containerization

- Docker
- Docker Compose

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/papers/upload` | Upload a research paper |
| GET | `/papers` | List uploaded papers |
| DELETE | `/papers/{paper_id}` | Delete a paper |
| POST | `/search` | Search relevant paper sections |
| POST | `/chat` | Ask questions about uploaded papers |

## Example: Upload Paper

```bash
curl -X POST \
  "http://127.0.0.1:8000/papers/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@paper.pdf;type=application/pdf"
```

## Example: Search

```json
{
  "query": "What is the main objective of the project?",
  "top_k": 5
}
```

## Example: Chat

```json
{
  "question": "What is the main objective of SmartTalk?",
  "top_k": 5
}
```

Example response:

```json
{
  "question": "What is the main objective of SmartTalk?",
  "answer": "The main objective of SmartTalk is to develop a reliable, user-friendly mobile interface that allows users to enter queries and receive meaningful, context-aware responses in real time.",
  "sources": [
    {
      "paper_name": "Pdf unlocked.pdf",
      "page_number": 16,
      "score": 0.552
    }
  ]
}
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/codeswith-pawan/research-paper-ai.git
cd research-paper-ai
```

### 2. Create a virtual environment

```bash
cd backend

python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and run Ollama

The RAG service uses a local Ollama model.

Make sure Ollama is installed and running, then pull the model:

```bash
ollama pull llama3.2:3b
```

### 5. Start the FastAPI server

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## Project Structure

```text
research-paper-ai/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── embeddings.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── pdf_processor.py
│   │   ├── rag.py
│   │   ├── recommendation.py
│   │   ├── schemas.py
│   │   ├── search.py
│   │   ├── services.py
│   │   └── vector_store.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .gitignore
│
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Retrieval Strategy

The search system does not rely only on vector similarity.

Retrieved candidates are reranked using a hybrid scoring approach:

```text
Final Score =
    Semantic Score
    + Keyword Score
    + Section Relevance
    - Quality Penalty
```

This helps improve retrieval for questions related to specific sections such as:

- objectives
- methodology
- limitations
- future scope
- project overview

The system also penalizes chunks containing weak sources such as references, appendices, and table-of-contents sections.

## Data Privacy

Uploaded PDFs, local databases, environment files, and other runtime data are excluded from version control through `.gitignore`.

The RAG model runs locally through Ollama.

## Limitations

The current MVP has several limitations:

- Retrieval quality depends on PDF text extraction quality.
- Fixed-size chunking may split information across chunks.
- The current embedding model is lightweight and general-purpose.
- Local LLM response quality depends on the selected Ollama model.
- Complex tables and scanned/image-only PDFs may require additional processing.
- The current system is primarily designed for English research documents.

## Future Improvements

Planned improvements include:

- Frontend web application
- Better document-level retrieval
- Metadata-aware search
- Improved chunking based on document structure
- Table and figure extraction
- OCR support for scanned PDFs
- Conversation history
- Authentication
- Persistent vector database
- Research paper recommendations
- Citation-aware answers
- Multi-document comparison
- Deployment to cloud infrastructure

## License

This project is currently intended as a learning and portfolio project.
