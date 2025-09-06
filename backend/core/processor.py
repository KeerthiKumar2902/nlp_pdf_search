# core/processor.py (Corrected Version)
import re
# Import the shared nlp instance from our new models.py file
from .models import nlp

def preprocess_and_chunk(text: str, chunk_size_sentences: int = 5) -> list[str]:
    """
    Cleans, segments, and chunks text.

    Args:
        text: The raw text string.
        chunk_size_sentences: The number of sentences to include in each chunk.

    Returns:
        A list of clean text chunks.
    """
    # This function will now use the imported 'nlp' object
    if nlp is None:
        # Handle case where model failed to load
        print("SpaCy model not available. Cannot process text.")
        return []

    # 1. Basic Cleaning
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple whitespaces with a single space

    # 2. Process text with spaCy for sentence segmentation
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]

    # 3. Group sentences into chunks
    chunks = []
    for i in range(0, len(sentences), chunk_size_sentences):
        chunk = " ".join(sentences[i:i + chunk_size_sentences])
        chunks.append(chunk)

    return chunks