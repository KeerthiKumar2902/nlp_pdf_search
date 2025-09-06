# core/analysis.py
import spacy
from .models import nlp, summarizer # Import our shared spaCy model instance
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_entities(text: str) -> list[dict]:
    """
    Extracts Named Entities from a given text using the spaCy model.

    Args:
        text: The input string to process.

    Returns:
        A list of dictionaries, where each dictionary represents an entity.
    """
    if nlp is None:
        return []

    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "explanation": spacy.explain(ent.label_)
        })
    return entities

def extract_keywords(text: str) -> dict:
    """
    Extracts keywords and keyphrases using two methods: TextRank and TF-IDF.

    Args:
        text: The input string to process.

    Returns:
        A dictionary containing lists of keywords from both methods.
    """
    if nlp is None:
        return {}

    results = {
        "textrank": [],
        "tfidf": []
    }

    # --- Method 1: TextRank for contextual keyphrases ---
    doc = nlp(text)
    # Access the top 10 ranked phrases from the custom '._.' attribute
    for phrase in doc._.phrases[:10]:
        results["textrank"].append({
            "text": phrase.text,
            "rank": phrase.rank
        })

    # --- Method 2: TF-IDF for statistically significant keywords ---
    # Note: TF-IDF is best on a corpus, but we can adapt it for a single document
    # by treating sentences or paragraphs as "documents". For simplicity, we run on the whole text.
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2), # Consider both single words and two-word phrases
            max_features=10 # Limit to top 10 features
        )
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # Create a list of (score, feature) tuples and sort it
        tfidf_results = sorted(zip(scores, feature_names), reverse=True)

        for score, feature in tfidf_results:
            if score > 0: # Only include features with a score > 0
                results["tfidf"].append({
                    "text": feature,
                    "score": score
                })
    except ValueError:
        # This can happen if the text is too short or has no features after stopword removal
        print("TF-IDF could not be calculated for the given text.")

    return results


# core/analysis.py (This is the corrected function to use)

def generate_summary(text: str, num_extractive_sentences: int = 3) -> dict:
    """
    Generates both extractive and abstractive summaries for a given text.

    Args:
        text: The input string to process.
        num_extractive_sentences: The number of sentences for the extractive summary.

    Returns:
        A dictionary containing both summary types.
    """
    results = {
        "extractive": "",
        "abstractive": ""
    }

    # --- Extractive Summary using pytextrank ---
    if nlp:
        doc = nlp(text)
        # --- THIS IS THE FIX: Access summary through 'doc._.textrank' ---
        try:
            extracted_sentences = [sent.text for sent in doc._.textrank.summary(limit_sentences=num_extractive_sentences)]
            results["extractive"] = " ".join(extracted_sentences)
        except AttributeError:
             print("Could not generate extractive summary. Is 'pytextrank' in the spaCy pipeline?")
             results["extractive"] = "Could not be generated."


    # --- Abstractive Summary using transformers ---
    if summarizer:
        max_chunk_length = 1024
        truncated_text = text[:max_chunk_length*4] 

        try:
            summary_list = summarizer(truncated_text, max_length=150, min_length=30, do_sample=False)
            if summary_list:
                results["abstractive"] = summary_list[0]['summary_text']
        except Exception as e:
            print(f"Error during abstractive summarization: {e}")
            results["abstractive"] = "Could not be generated."
    
    return results