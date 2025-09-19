# backend/core/worker.py (Definitive Final Version 2.0)
import json
from .database import SessionLocal, Document
from .parser import extract_text_from_pdf
from .models import nlp, summarizer, embedding_model, summarizer_tokenizer
from .analysis import extract_entities, extract_keywords
from keybert import KeyBERT

def analyze_entire_document(filename: str, doc_id: int):
    """
    A long-running background task to analyze the entire document.
    """
    print(f"BACKGROUND WORKER: Starting full analysis for doc_id: {doc_id} ({filename})")
    db = SessionLocal()
    db_document = db.query(Document).filter(Document.id == doc_id).first()
    
    try:
        if not db_document:
            print(f"ERROR: Document with id {doc_id} not found.")
            return

        file_path = f"./uploads/{filename}"
        full_text = extract_text_from_pdf(file_path)

        if not full_text.strip():
            db_document.status = "error"
            db.commit()
            return

        # --- Analysis steps remain the same ---
        print(f"Performing NER, Keywords, and KeyBERT for {filename}...")
        full_ner = extract_entities(full_text)
        full_keywords = extract_keywords(full_text)
        kw_model = KeyBERT(model=embedding_model)
        keybert_keywords_with_scores = kw_model.extract_keywords(full_text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=15)
        keybert_keywords = [kw[0] for kw in keybert_keywords_with_scores]
        
        print(f"Performing final, tuned summarization for {filename}...")
        doc = nlp(full_text)
        
        # --- NEW DEFINITIVE SUMMARY LOGIC ---

        # 1. Get the top-ranked sentences directly from pytextrank's summary method
        # This method already yields the sentences in order of importance.
        top_sentences = [sent.text for sent in doc._.textrank.summary(limit_sentences=25)]

        # 2. Use the top 5 of these for the extractive summary
        extractive_summary = " ".join(top_sentences[:5])

        # 3. Use the top sentences to build a context-rich prompt for the abstractive model,
        #    while respecting the token limit.
        text_to_summarize = ""
        TOKEN_LIMIT = 500 # Stay just under the 512 limit
        
        for sentence in top_sentences:
            # Check the token count of the *current* text plus the *new* sentence
            current_tokens = summarizer_tokenizer.encode(text_to_summarize + sentence)
            if len(current_tokens) > TOKEN_LIMIT:
                break # Stop if adding the next sentence exceeds the limit
            text_to_summarize += sentence + " "
        
        # 4. Generate the abstractive summary
        if text_to_summarize.strip() and summarizer:
            final_summary_list = summarizer(text_to_summarize, max_length=300, min_length=75, do_sample=False)
            abstractive_summary = final_summary_list[0]['summary_text'] if final_summary_list else "Could not generate abstractive summary."
        else:
            abstractive_summary = "Not enough content to generate an abstractive summary."
        # --- END OF DEFINITIVE LOGIC ---
        
        analysis_results = {
            "ner": full_ner,
            "keywords": full_keywords,
            "keybert_keywords": keybert_keywords,
            "summary": {"extractive": extractive_summary, "abstractive": abstractive_summary }
        }
        
        db_document.analysis_results = json.dumps(analysis_results)
        db_document.status = "complete"
        db.commit()
        print(f"BACKGROUND WORKER: Full analysis complete for doc_id: {doc_id}. Status updated to 'complete'.")

    except Exception as e:
        print(f"BACKGROUND WORKER FAILED for doc_id {doc_id}: {e}")
        db.rollback()
        if db_document:
            db_document.status = "failed"
            db.commit()
    finally:
        db.close()
        print(f"BACKGROUND WORKER: DB session closed for doc_id {doc_id}.")