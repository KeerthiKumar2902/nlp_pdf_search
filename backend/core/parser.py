# core/parser.py
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a given PDF file and concatenates it.

    Args:
        file_path: The full path to the PDF file.

    Returns:
        A single string containing all the text from the PDF.
    """
    doc = fitz.open(file_path)
    all_text = []
    for page in doc:
        all_text.append(page.get_text())

    doc.close() # It's good practice to close the document
    return "".join(all_text)