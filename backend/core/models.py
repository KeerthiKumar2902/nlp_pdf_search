# backend/core/models.py (Updated with Multiple Search Models)
import spacy
from sentence_transformers import SentenceTransformer
import pytextrank
from transformers import pipeline, AutoTokenizer

print("Loading NLP models...")

# SpaCy Model (using the better transformer version)
try:
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe("textrank")
    print("spaCy model 'en_core_web_trf' with pytextrank loaded successfully.")
except OSError:
    print("spaCy model not found. Please run 'python -m spacy download en_core_web_trf'")
    nlp = None

# --- NEW: Load a dictionary of embedding models ---
embedding_models = {}
try:
    # The fast, default model
    embedding_models['all-MiniLM-L6-v2'] = SentenceTransformer('all-MiniLM-L6-v2')
    # The slower, higher-quality model
    embedding_models['all-mpnet-base-v2'] = SentenceTransformer('all-mpnet-base-v2')
    print("All SentenceTransformer models loaded successfully.")
except Exception as e:
    print(f"Error loading SentenceTransformer models: {e}")

# Summarizer and Tokenizer
summarizer = None
summarizer_tokenizer = None
try:
    summarizer_model_name = "facebook/bart-large-cnn"
    summarizer = pipeline("summarization", model=summarizer_model_name)
    summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_model_name)
    print(f"Summarization model '{summarizer_model_name}' and its tokenizer loaded successfully.")
except Exception as e:
    print(f"Error loading summarization model/tokenizer: {e}")

print("NLP models are ready.")