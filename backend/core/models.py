# core/models.py
import spacy
from sentence_transformers import SentenceTransformer
import pytextrank
from transformers import pipeline, AutoTokenizer

print("Loading NLP models...")

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe("textrank")
    print("spaCy model 'en_core_web_trf' with pytextrank loaded successfully.")
except OSError:
    print("spaCy model not found. Please run 'python -m spacy download en_core_web_trf'")
    nlp = None

# Load the Sentence Transformer model
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("SentenceTransformer model 'all-MiniLM-L6-v2' loaded successfully.")
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    embedding_model = None


# --- NEW: Load Summarizer and its Tokenizer ---
summarizer = None
summarizer_tokenizer = None
try:
    # We define the model name here to reuse it
    summarizer_model_name = "google/pegasus-xsum" 
    summarizer = pipeline("summarization", model=summarizer_model_name)
    summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_model_name)
    print(f"Summarization model '{summarizer_model_name}' and its tokenizer loaded successfully.")
except Exception as e:
    print(f"Error loading summarization model/tokenizer: {e}")
    

print("NLP models are ready.")