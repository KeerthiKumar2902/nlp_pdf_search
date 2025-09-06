# core/search.py (Corrected Version)
# Import the shared embedding_model instance from our new models.py file
from .models import embedding_model 
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

document_store = {}

def generate_and_store_embeddings(doc_id: str, chunks: list[str]):
    """
    Generates embeddings for a list of text chunks and stores them.
    """
    # Use the imported 'embedding_model'
    if embedding_model is None:
        print("Model not loaded, cannot generate embeddings.")
        return

    print(f"Generating embeddings for {len(chunks)} chunks in document: {doc_id}")

    # Use the imported 'embedding_model'
    embeddings = embedding_model.encode(chunks, show_progress_bar=True)

    document_store[doc_id] = {
        "chunks": chunks,
        "embeddings": embeddings
    }

    print(f"Successfully generated and stored embeddings for {doc_id}")
    print(f"Shape of embeddings array: {embeddings.shape}")

def semantic_search(doc_id: str, query: str, top_k: int = 3):
    """
    Performs semantic search for a query within a specific document.
    """
    # Use the imported 'embedding_model'
    if embedding_model is None:
        print("Model not loaded, cannot perform search.")
        return []

    if doc_id not in document_store:
        print(f"Error: Document '{doc_id}' not found in store.")
        return []

    doc_data = document_store[doc_id]
    doc_chunks = doc_data["chunks"]
    doc_embeddings = doc_data["embeddings"]

    # Use the imported 'embedding_model'
    query_embedding = embedding_model.encode([query])

    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_k_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_k_indices:
        results.append({
            "chunk": doc_chunks[idx],
            "score": float(similarities[idx])
        })

    return results