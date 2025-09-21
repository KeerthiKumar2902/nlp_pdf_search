# backend/main.py (Updated /search endpoint)
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
import json
import numpy as np
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

from core.parser import extract_text_from_pdf
from core.processor import preprocess_and_chunk
from core.search import generate_and_store_embeddings, document_store, semantic_search
from core.analysis import extract_entities, extract_keywords, generate_summary
from core.worker import analyze_entire_document
from core import database
from core.database import SessionLocal, engine

database.create_db_and_tables()
app = FastAPI(title="NLP Search Engine API")

# --- CORS MIDDLEWARE ... (This section is unchanged)
origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Pydantic Models ... (This section is unchanged)
class AnalysisTask(str, Enum):
    ner = "ner"
    keywords = "keywords"
    summary = "summary"

class AnalysisRequest(BaseModel):
    text: str
    tasks: List[AnalysisTask]

class DocumentStatusResponse(BaseModel):
    doc_id: int
    filename: str
    status: str
    created_at: datetime
    analysis_results: Optional[dict] = None
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "Server is running successfully!"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # ... (This endpoint is unchanged)
    UPLOAD_DIRECTORY = "./uploads"
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type.")
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename, "status": "File uploaded successfully"}

@app.post("/process/{filename}")
async def process_document(filename: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # ... (This endpoint is unchanged)
    UPLOAD_DIRECTORY = "./uploads"
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    db_document = db.query(database.Document).filter(database.Document.filename == filename).first()
    if not db_document:
        db_document = database.Document(filename=filename, status="processing")
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
    else:
        db_document.status = "processing"
        db_document.analysis_results = None
        db.commit()
    
    background_tasks.add_task(analyze_entire_document, filename=filename, doc_id=db_document.id)
    raw_text = extract_text_from_pdf(file_path)
    chunks = preprocess_and_chunk(raw_text)
    generate_and_store_embeddings(doc_id=filename, chunks=chunks)
    
    return {"message": "...", "filename": filename, "doc_id": db_document.id, "status": db_document.status}

# In backend/main.py, replace the existing get_document_status function with this:

@app.get("/document/{filename}/status", response_model=DocumentStatusResponse)
async def get_document_status(filename: str, db: Session = Depends(get_db)):
    """
    Polls for the status of a document's full analysis.
    """
    print(f"Polling status for: {filename}")
    
    db_document = db.query(database.Document).filter(database.Document.filename == filename).first()

    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found.")

    parsed_results = None
    if db_document.status == "complete" and db_document.analysis_results:
        # Safely parse the JSON string from the database
        try:
            parsed_results = json.loads(db_document.analysis_results)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for document {filename}")
            # This will ensure the app doesn't crash if the JSON is malformed
            parsed_results = {"error": "Failed to decode analysis results."}


    # --- THIS IS THE DEFINITIVE FIX for Pydantic V2 ---
    # 1. Manually create a clean dictionary from the database object's attributes.
    response_data = {
        "doc_id": db_document.id,
        "filename": db_document.filename,
        "status": db_document.status,
        "created_at": db_document.created_at,
        "analysis_results": parsed_results # Use our safely parsed results
    }
    
    # 2. Use the dictionary to create and return the Pydantic response model.
    #    This is the modern and most robust way to do this.
    return DocumentStatusResponse(**response_data)

# --- UPDATED /search ENDPOINT ---
@app.get("/search/{filename}")
async def search_in_document(filename: str, query: str, model_name: str = 'all-MiniLM-L6-v2'):
    """
    Performs semantic search, optionally with a specified model.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")
    
    try:
        results = semantic_search(doc_id=filename, query=query, model_name=model_name, top_k=5)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not results:
        raise HTTPException(status_code=404, detail="No relevant results found.")

    return {"filename": filename, "query": query, "model_used": model_name, "results": results}

@app.post("/analyze/")
async def analyze_text(request: AnalysisRequest):
    # ... (This endpoint is unchanged)
    results = {}
    if AnalysisTask.ner in request.tasks:
        results["ner"] = extract_entities(request.text)
    if AnalysisTask.keywords in request.tasks:
        results["keywords"] = extract_keywords(request.text)
    if AnalysisTask.summary in request.tasks:
        results["summary"] = generate_summary(request.text)
    if not results:
        raise HTTPException(status_code=400, detail="No valid tasks requested.")
    return results

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)