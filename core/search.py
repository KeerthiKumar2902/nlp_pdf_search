# core/search.py
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. In-memory storage for document chunks and their embeddings.
# The structure will be:
# {
#   "filename.pdf": {
#       "chunks": ["chunk1 text", "chunk2 text", ...],
#       "embeddings": numpy.ndarray([...])
#   },
#   ...
# }
document_store = {}

# 2. Load the pre-trained Sentence Transformer model.
# This model is optimized for semantic search.
# It will be loaded only once when the application starts.
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("SentenceTransformer model loaded successfully.")
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    # Depending on the desired behavior, you might want to exit or handle this differently
    model = None


# core/search.py (add this function below the existing code)

def generate_and_store_embeddings(doc_id: str, chunks: list[str]):
    """
    Generates embeddings for a list of text chunks and stores them.

    Args:
        doc_id: The identifier for the document (e.g., filename).
        chunks: A list of text chunks from the document.
    """
    if model is None:
        print("Model not loaded, cannot generate embeddings.")
        return

    print(f"Generating embeddings for {len(chunks)} chunks in document: {doc_id}")

    # Use the model to encode all chunks at once. This is highly efficient.
    embeddings = model.encode(chunks, show_progress_bar=True)

    # Store the chunks and their corresponding embeddings in our in-memory store.
    document_store[doc_id] = {
        "chunks": chunks,
        "embeddings": embeddings
    }

    print(f"Successfully generated and stored embeddings for {doc_id}")
    print(f"Shape of embeddings array: {embeddings.shape}")

# core/search.py (add this function below the existing code)
from sklearn.metrics.pairwise import cosine_similarity

def semantic_search(doc_id: str, query: str, top_k: int = 3):
    """
    Performs semantic search for a query within a specific document.

    Args:
        doc_id: The identifier for the document (e.g., filename).
        query: The user's search query.
        top_k: The number of top results to return.

    Returns:
        A list of dictionaries, each containing a result chunk and its score.
    """
    if model is None:
        print("Model not loaded, cannot perform search.")
        return []

    # 1. Check if the document exists in our store
    if doc_id not in document_store:
        print(f"Error: Document '{doc_id}' not found in store.")
        return []

    # 2. Retrieve the stored chunks and embeddings for the document
    doc_data = document_store[doc_id]
    doc_chunks = doc_data["chunks"]
    doc_embeddings = doc_data["embeddings"]

    # 3. Generate an embedding for the user's query
    query_embedding = model.encode([query]) # The model expects a list

    # 4. Calculate cosine similarity between the query and all chunks
    # The result is a 2D array, so we take the first row.
    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]

    # 5. Find the indices of the top_k most similar chunks
    # np.argsort returns indices that would sort the array. We reverse it for descending order.
    top_k_indices = np.argsort(similarities)[::-1][:top_k]

    # 6. Format the results
    results = []
    for idx in top_k_indices:
        results.append({
            "chunk": doc_chunks[idx],
            "score": float(similarities[idx]) # Convert numpy float to standard float
        })

    return results