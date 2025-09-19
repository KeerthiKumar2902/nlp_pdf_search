# main.py (Final MVP Version)
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware # NEW IMPORT
from sqlalchemy.orm import Session
import uvicorn
import os
import json
import numpy as np
from pydantic import BaseModel # Import Pydantic
from typing import List, Optional
from datetime import datetime
from enum import Enum

# --- Our core logic imports ---
from core.parser import extract_text_from_pdf
from core.processor import preprocess_and_chunk
# --- IMPORT our new search function ---
from core.search import generate_and_store_embeddings, document_store, semantic_search
from core.analysis import extract_entities, extract_keywords, generate_summary # --- NEW analysis import ---
from core.worker import analyze_entire_document
# --- NEW DATABASE IMPORTS ---
from core import database
from core.database import SessionLocal, engine

UPLOAD_DIRECTORY = "./uploads"

database.create_db_and_tables()
app = FastAPI(title="NLP Search Engine API")

# --- CORS MIDDLEWARE CONFIGURATION ---
# This is the new section that allows your React app to talk to the backend.
origins = [
    "http://localhost:5173", # The default port for Vite React apps
    "http://localhost:3000", # The default port for Create React App (just in case)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

class AnalysisTask(str, Enum):
    ner = "ner"
    keywords = "keywords" 
    summary = "summary" # <-- THIS IS THE FIX. ADD THIS LINE.

class AnalysisRequest(BaseModel):
    text: str
    tasks: List[AnalysisTask]

# --- NEW Pydantic Response Model for Status ---
class DocumentStatusResponse(BaseModel):
    doc_id: int
    filename: str
    status: str
    created_at: datetime
    analysis_results: Optional[dict] = None # Results are optional

    class Config:
        from_attributes = True # Formerly orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ... (root, upload, and process endpoints remain the same) ...
@app.get("/")
async def root():
    return {"message": "Server is running successfully!"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            while content := await file.read(1024):
                buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There was an error uploading the file: {e}")
    finally:
        await file.close()
    return {"filename": file.filename, "status": "File uploaded successfully"}


# Note the new 'db: Session = Depends(get_db)' and 'background_tasks: BackgroundTasks'
# backend/main.py (This is the corrected function to use)

# Find your existing /process endpoint and REPLACE it with this new version
@app.post("/process/{filename}")
async def process_document(
    filename: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    # --- THIS IS THE NEW LOGIC ---
    # Step 1: Check if the document already exists in the database.
    db_document = db.query(database.Document).filter(database.Document.filename == filename).first()

    if db_document:
        # Step 2a: If it exists, update it to be re-processed.
        print(f"Document '{filename}' already exists. Re-processing.")
        db_document.status = "processing"
        db_document.analysis_results = None # Clear old results
        db.commit()
    else:
        # Step 2b: If it does not exist, create a new record.
        print(f"Document '{filename}' not found in DB. Creating new record.")
        db_document = database.Document(filename=filename, status="processing")
        db.add(db_document)
        db.commit()
        db.refresh(db_document) # Refresh to get the new ID

    # Step 3: Trigger the background task (this part is the same)
    background_tasks.add_task(analyze_entire_document, filename=filename, doc_id=db_document.id)
    
    # Run fast, in-memory embedding for immediate searchability
    raw_text = extract_text_from_pdf(file_path)
    chunks = preprocess_and_chunk(raw_text)
    generate_and_store_embeddings(doc_id=filename, chunks=chunks)

    # Return a response to the user IMMEDIATELY
    return {
        "message": "Document processing and full analysis started in the background.",
        "filename": filename,
        "doc_id": db_document.id,
        "status": db_document.status
    }

# --- ENDPOINT TO CHECK DOCUMENT STATUS ---
@app.get("/document/{filename}/status", response_model=DocumentStatusResponse)
async def get_document_status(filename: str, db: Session = Depends(get_db)):
    """
    Polls for the status of a document's full analysis.
    """
    print(f"Polling status for: {filename}")

    # Step 1: Find the document in the database
    db_document = db.query(database.Document).filter(database.Document.filename == filename).first()

    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Step 2: Check if analysis results exist and parse them
    parsed_results = None
    if db_document.status == "complete" and db_document.analysis_results:
        parsed_results = json.loads(db_document.analysis_results)

    # Step 3: Return the structured response
    return DocumentStatusResponse(
        doc_id=db_document.id,
        filename=db_document.filename,
        status=db_document.status,
        created_at=db_document.created_at,
        analysis_results=parsed_results
    )


# --- FINAL NEW ENDPOINT FOR SEARCH ---
@app.get("/search/{filename}")
async def search_in_document(filename: str, query: str):
    """
    Performs semantic search within a specified document.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")

    # Call our core search function
    results = semantic_search(doc_id=filename, query=query, top_k=3)

    if not results:
        raise HTTPException(status_code=404, detail="No relevant results found or document not processed.")

    return {
        "filename": filename,
        "query": query,
        "results": results
    }



# --- NEW /analyze ENDPOINT ---
@app.post("/analyze/")
async def analyze_text(request: AnalysisRequest):
    """
    Performs one or more analysis tasks on a given text.
    """
    results = {}

    if AnalysisTask.ner in request.tasks:
        results["ner"] = extract_entities(request.text)
    
    if AnalysisTask.keywords in request.tasks:
        results["keywords"] = extract_keywords(request.text)
    
    if AnalysisTask.summary in request.tasks:
        results["summary"] = generate_summary(request.text)

    # We will add more "if" blocks here for other tasks later

    if not results:
        raise HTTPException(status_code=400, detail="No valid tasks requested.")

    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)