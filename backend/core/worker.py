# backend/core/worker.py (Final Locked-in Version)
import json
from .database import SessionLocal, Document
from .parser import extract_text_from_pdf
from .models import nlp, summarizer, embedding_models, summarizer_tokenizer
from .analysis import extract_entities, extract_keywords, generate_semantic_extractive_summary
from keybert import KeyBERT

def analyze_entire_document(filename: str, doc_id: int):
    print(f"BACKGROUND WORKER: Starting full analysis for doc_id: {doc_id} ({filename})")
    db = SessionLocal()
    db_document = db.query(Document).filter(Document.id == doc_id).first()
    
    try:
        if not db_document: return

        file_path = f"./uploads/{filename}"
        full_text = extract_text_from_pdf(file_path)

        if len(full_text) < 250:
            db_document.status = "complete"
            db_document.analysis_results = json.dumps({"error": "Document too short for a meaningful analysis."})
            db.commit()
            return

        # --- NER, Keywords, and KeyBERT (Unchanged) ---
        print(f"Performing NER, Keywords, and KeyBERT for {filename}...")
        full_ner = extract_entities(full_text)
        full_keywords = extract_keywords(full_text)
        default_embedding_model = embedding_models.get('all-MiniLM-L6-v2')
        keybert_keywords = []
        if default_embedding_model:
            kw_model = KeyBERT(model=default_embedding_model)
            keybert_keywords_with_scores = kw_model.extract_keywords(full_text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=15)
            keybert_keywords = [kw[0] for kw in keybert_keywords_with_scores]
        
        print(f"Performing final summarization for {filename}...")
        
        # === Extractive Summary (Using our best method) ===
        extractive_summary = generate_semantic_extractive_summary(full_text, num_sentences=12)

        # === Abstractive Summary (Using the robust "Intro + Conclusion" method) ===
        abstractive_summary = "Could not generate abstractive summary."
        if summarizer and summarizer_tokenizer:
            intro_text = full_text[:2000]
            conclusion_text = full_text[-2000:]
            
            prompt = f"Based on the following introduction and conclusion from a long document, please write a comprehensive, fluent summary paragraph that captures the main arguments and themes.\n\nINTRODUCTION:\n{intro_text}\n\nCONCLUSION:\n{conclusion_text}"

            tokens = summarizer_tokenizer.encode(prompt)
            if len(tokens) > 1024:
                tokens = tokens[:1020]
            truncated_prompt = summarizer_tokenizer.decode(tokens, skip_special_tokens=True)

            final_summary_list = summarizer(truncated_prompt, 
                                            max_length=400,
                                            min_length=100, 
                                            do_sample=False,
                                            repetition_penalty=1.2)
            if final_summary_list:
                abstractive_summary = final_summary_list[0]['summary_text']
        
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
        if db_document: db_document.status = "failed"; db.commit()
    finally:
        db.close()
        print(f"BACKGROUND WORKER: DB session closed for doc_id {doc_id}.")