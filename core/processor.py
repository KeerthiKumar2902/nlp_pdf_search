# core/processor.py
import spacy
import re

# Load the spaCy model once as a global object.
# This is efficient as it avoids reloading the model on every function call.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def preprocess_and_chunk(text: str, chunk_size_sentences: int = 5) -> list[str]:
    """
    Cleans, segments, and chunks text.

    Args:
        text: The raw text string.
        chunk_size_sentences: The number of sentences to include in each chunk.

    Returns:
        A list of clean text chunks.
    """
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