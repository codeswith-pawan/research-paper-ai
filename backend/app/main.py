from pathlib import Path
import hashlib
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from .database import (
    init_database,
    add_paper,
    get_paper_by_hash,
    get_all_papers,
    get_paper,
    delete_paper as delete_paper_db,
    update_paper_chunks
)

from .search import ResearchSearchEngine


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="Research Paper AI",
    description="AI-powered research paper recommendation and literature analysis platform",
    version="1.0.0"
)


search_engine = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.on_event("startup")
def startup_event():
    global search_engine

    init_database()
    search_engine = ResearchSearchEngine()


@app.get("/")
def root():
    return {
        "message": "Research Paper AI API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/papers/upload")
async def upload_paper(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    file_hash = hashlib.sha256(contents).hexdigest()

    existing_paper = get_paper_by_hash(file_hash)

    if existing_paper:
        return {
            "message": "Duplicate PDF already exists",
            "duplicate": True,
            "paper": existing_paper
        }

    paper_id = str(uuid4())

    unique_filename = f"{paper_id}_{file.filename}"

    file_path = UPLOAD_DIR / unique_filename

    file_path.write_bytes(contents)

    add_paper(
        paper_id=paper_id,
        original_filename=file.filename,
        saved_filename=unique_filename,
        file_size=len(contents),
        file_hash=file_hash,
        chunks=0
    )

    global search_engine

    index_info = search_engine.rebuild_index()

    paper_chunks = sum(
        1
        for chunk in search_engine.chunks
        if chunk["paper_id"] == paper_id
    )

    update_paper_chunks(
        paper_id,
        paper_chunks
    )

    paper = get_paper(paper_id)

    return {
        "message": "PDF uploaded and indexed successfully",
        "duplicate": False,
        "paper": paper,
        "index": index_info
    }


@app.get("/papers")
def list_papers():

    papers = get_all_papers()

    return {
        "count": len(papers),
        "papers": papers
    }


@app.delete("/papers/{paper_id}")
def delete_paper(paper_id: str):

    paper = get_paper(paper_id)

    if paper is None:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    file_path = UPLOAD_DIR / paper["saved_filename"]

    if file_path.exists():
        file_path.unlink()

    deleted = delete_paper_db(paper_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )

    global search_engine

    index_info = search_engine.rebuild_index()

    return {
        "message": "Paper deleted successfully",
        "deleted_paper": paper,
        "index": index_info
    }


@app.post("/search")
def search_papers(request: SearchRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    if request.top_k < 1 or request.top_k > 20:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20"
        )

    results = search_engine.search(
        request.query,
        request.top_k
    )

    return {
        "query": request.query,
        "result_count": len(results),
        "results": results
    }


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5


@app.post("/chat")
def chat_with_papers(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    if request.top_k < 1 or request.top_k > 10:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 10"
        )

    from .rag import RAGService

    retrieved_chunks = search_engine.search(
        request.question,
        request.top_k
    )

    rag_service = RAGService()

    result = rag_service.generate_answer(
        request.question,
        retrieved_chunks
    )

    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }