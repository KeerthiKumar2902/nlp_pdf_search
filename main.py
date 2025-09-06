# main.py (Final MVP Version)
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import os
import numpy as np
from pydantic import BaseModel # Import Pydantic
from typing import List
from enum import Enum

# --- Our core logic imports ---
from core.parser import extract_text_from_pdf
from core.processor import preprocess_and_chunk
# --- IMPORT our new search function ---
from core.search import generate_and_store_embeddings, document_store, semantic_search
from core.analysis import extract_entities, extract_keywords, generate_summary # --- NEW analysis import ---

UPLOAD_DIRECTORY = "./uploads"

app = FastAPI(title="NLP Search Engine API")

class AnalysisTask(str, Enum):
    ner = "ner"
    keywords = "keywords" 
    summary = "summary" # <-- THIS IS THE FIX. ADD THIS LINE.

class AnalysisRequest(BaseModel):
    text: str
    tasks: List[AnalysisTask]


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

@app.post("/process/{filename}")
async def process_document(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    try:
        raw_text = extract_text_from_pdf(file_path)
        chunks = preprocess_and_chunk(raw_text)
        generate_and_store_embeddings(doc_id=filename, chunks=chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

    embedding_shape = document_store.get(filename, {}).get("embeddings", np.array([])).shape
    return {
        "filename": filename, "status": "Processing complete and embeddings stored",
        "total_chunks": len(chunks), "embedding_shape": list(embedding_shape),
        "sample_chunk": chunks[0] if chunks else "No text could be extracted."
    }


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