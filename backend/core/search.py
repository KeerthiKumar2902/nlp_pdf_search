# backend/core/search.py (Corrected)
from .models import embedding_models # Import the dictionary of models
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# This store now holds the DEFAULT embeddings only (from MiniLM)
document_store = {}

def generate_and_store_embeddings(doc_id: str, chunks: list[str]):
    """
    Generates and stores embeddings using the FAST, DEFAULT model.
    """
    default_model_name = 'all-MiniLM-L6-v2'
    if default_model_name not in embedding_models:
        print(f"Default model {default_model_name} not loaded.")
        return
    
    # --- FIX: Select the default model from the dictionary ---
    default_model = embedding_models[default_model_name]
    print(f"Generating default embeddings for {len(chunks)} chunks using {default_model_name}")

    embeddings = default_model.encode(chunks, show_progress_bar=True)

    document_store[doc_id] = {
        "chunks": chunks,
        "embeddings": embeddings,
        "model_name": default_model_name # Track which model was used
    }
    print(f"Successfully stored default embeddings for {doc_id}")

def semantic_search(doc_id: str, query: str, model_name: str, top_k: int = 5):
    """
    Performs semantic search using a SPECIFIED model.
    """
    if model_name not in embedding_models:
        raise ValueError(f"Model '{model_name}' is not available.")
    
    if doc_id not in document_store:
        print(f"Error: Document '{doc_id}' not found in store.")
        return []

    # Select the requested model from the dictionary
    selected_model = embedding_models[model_name]
    
    doc_data = document_store[doc_id]
    doc_chunks = doc_data["chunks"]
    
    if model_name == doc_data.get("model_name"):
        print(f"Performing search with pre-calculated '{model_name}' embeddings.")
        doc_embeddings = doc_data["embeddings"]
    else:
        print(f"Performing on-the-fly re-embedding and search with '{model_name}'.")
        doc_embeddings = selected_model.encode(doc_chunks, show_progress_bar=False)
    
    query_embedding = selected_model.encode([query])
    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_k_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_k_indices:
        results.append({
            "chunk": doc_chunks[idx],
            "score": float(similarities[idx])
        })
    return results