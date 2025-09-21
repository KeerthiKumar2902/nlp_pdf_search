# backend/core/worker.py (Final Corrected Version)
import json
from .database import SessionLocal, Document
from .parser import extract_text_from_pdf
from .models import nlp, summarizer, embedding_models, summarizer_tokenizer
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
            return

        file_path = f"./uploads/{filename}"
        full_text = extract_text_from_pdf(file_path)

        if not full_text.strip():
            db_document.status = "error"
            db.commit()
            return

        print(f"Performing NER, Keywords, and KeyBERT for {filename}...")
        full_ner = extract_entities(full_text)
        full_keywords = extract_keywords(full_text)
        default_embedding_model = embedding_models.get('all-MiniLM-L6-v2')
        if default_embedding_model:
            kw_model = KeyBERT(model=default_embedding_model)
            keybert_keywords_with_scores = kw_model.extract_keywords(full_text,
                                                                     keyphrase_ngram_range=(1, 3),
                                                                     stop_words='english',
                                                                     top_n=15)
            keybert_keywords = [kw[0] for kw in keybert_keywords_with_scores]
        else:
            keybert_keywords = []
        
        print(f"Performing summarization for {filename}...")
        doc = nlp(full_text)
        
        # --- THIS IS THE CORRECTED SUMMARIZATION LOGIC ---
        top_sentences_text = [sent.text for sent in doc._.textrank.summary(limit_sentences=25)]

        # Extractive summary is the top 5 of the ranked sentences
        extractive_summary = " ".join(top_sentences_text[:5])

        # Build the input for the abstractive summary, respecting token limits
        text_to_summarize = ""
        TOKEN_LIMIT = 500
        sentences_to_include = []
        for sentence in top_sentences_text:
            # Join the raw strings, NOT s.text
            temp_text = " ".join(sentences_to_include + [sentence])
            tokens = summarizer_tokenizer.encode(temp_text)

            if len(tokens) > TOKEN_LIMIT:
                break
            sentences_to_include.append(sentence)
        
        text_to_summarize = " ".join(sentences_to_include)
        
        if text_to_summarize.strip() and summarizer:
            final_summary_list = summarizer(text_to_summarize, max_length=300, min_length=75, do_sample=False, repetition_penalty=1.2)
            abstractive_summary = final_summary_list[0]['summary_text'] if final_summary_list else "Could not generate abstractive summary."
        else:
            abstractive_summary = "Not enough content to generate an abstractive summary."
        # --- END OF CORRECTED LOGIC ---
        
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