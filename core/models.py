# core/models.py
import spacy
from sentence_transformers import SentenceTransformer
import pytextrank
from transformers import pipeline

print("Loading NLP models...")

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("textrank")
    print("spaCy model 'en_core_web_sm' with pytextrank loaded successfully.")
except OSError:
    print("spaCy model not found. Please run 'python -m spacy download en_core_web_sm'")
    nlp = None

# Load the Sentence Transformer model
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("SentenceTransformer model 'all-MiniLM-L6-v2' loaded successfully.")
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    embedding_model = None


# --- NEW: Load the Summarization model ---
try:
    # Using a well-known model for summarization from Facebook (now Meta)
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    print("Summarization model 'facebook/bart-large-cnn' loaded successfully.")
except Exception as e:
    print(f"Error loading summarization model: {e}")
    summarizer = None
    

print("NLP models are ready.")