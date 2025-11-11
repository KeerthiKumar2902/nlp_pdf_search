
# NLP PDF Search & Analysis Engine

This project is a full-stack, intelligent document workspace that allows you to upload PDF documents, perform deep semantic search, and generate a comprehensive NLP analysis report. It's built with a modern Python (FastAPI) backend and a React frontend.

<img width="1871" height="846" alt="image" src="https://github.com/user-attachments/assets/c5107cae-5bb9-4619-abb0-35fcab12f257" />
<img width="1090" height="641" alt="image" src="https://github.com/user-attachments/assets/0288f973-52b3-4d96-9011-a8c71d740d9e" />
<img width="1090" height="463" alt="image" src="https://github.com/user-attachments/assets/54a13a2a-0917-4bb8-a102-d8305bcca9a0" />
<img width="1090" height="590" alt="image" src="https://github.com/user-attachments/assets/a075795f-c22c-4eee-9c2d-2fc6d0057592" />



-----

## Core Features

This application moves beyond simple keyword matching to provide a rich, interactive analysis experience.

  * **⚡ Semantic Search:** Ask questions in natural language and find the most relevant passages, even if the keywords don't match.
  * **🔄 User-Selectable Search Models:** Instantly switch between a **"Fast Model"** (`all-MiniLM-L6-v2`) for speed and a **"High Quality Model"** (`all-mpnet-base-v2`) for accuracy.
  * **🧠 Comprehensive Analysis Report:** A background worker generates a full report for each document, including:
      * **Hybrid Keywords:** Statistical (**TF-IDF**), contextual (**TextRank**), and semantic (**KeyBERT**) keywords.
      * **Dual Summaries:** Both **Extractive** (key sentences) and **Abstractive** (AI-generated) summaries.
      * **Named Entity Recognition (NER):** Automatic detection of people, places, and organizations.
  * **🔍 Interactive Chunk Analysis:** Found a key search result? Click **"Analyze Chunk"** to instantly run an on-demand analysis (NER, Keywords, Summary) on just that passage.
  * **⚙️ Asynchronous Processing:** A FastAPI background worker handles the heavy NLP analysis, so the UI remains fast and responsive.

-----

## Architecture Overview

The project uses a modern, decoupled architecture:

  * **Frontend:** A **React (Vite)** Single Page Application (SPA) that manages the user interface and all user interactions.
  * **Backend:** A **FastAPI (Python)** server that acts as a central API gateway. It handles file uploads, serves search requests, and orchestrates the NLP tasks.
  * **NLP Worker:** An **asynchronous background task** managed by FastAPI. It performs the slow, intensive analysis (summarization, KeyBERT, etc.) without blocking the main server.
  * **Database:** A simple **SQLite** database (managed with **SQLAlchemy**) to store document metadata, processing status, and the final JSON analysis results.

*(**Note:** You can use one of the PlantUML codes I provided earlier to generate and insert an architecture diagram here.)*

-----

## 🛠 Tech Stack

| Area | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+ | Core programming language |
| | FastAPI | Modern web framework for building the API |
| | Uvicorn | ASGI server to run the FastAPI app |
| | `sentence-transformers` | For generating semantic search embeddings |
| | `transformers` (Hugging Face) | For the abstractive (BART) summarization model |
| | `spaCy` (`en_core_web_trf`) | For NER, sentence segmentation, and TextRank |
| | `keybert` | For semantic keyword extraction |
| | `pymupdf` (fitz) | For high-speed PDF text extraction |
| | `sqlalchemy` | ORM for database interaction |
| | `sqlite` | Lightweight database for results & metadata |
| **Frontend**| React | JavaScript library for building the UI |
| | Vite | Frontend build tool and dev server |
| | Tailwind CSS | Utility-first CSS framework for styling |
| | Axios | For making HTTP requests to the backend API |
| | `react-router-dom` | For client-side routing |

-----

## 🚀 Getting Started: Reproducibility

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

  * **Python 3.10+** and `pip`
  * **Node.js v18+** and `npm`

### 1\. Backend Setup

The backend server runs on `http://localhost:8000`.

```bash
# 1. Clone the repository
git clone https://github.com/KeerthiKumar2902/nlp_pdf_search.git
cd nlp_pdf_search/backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. CRITICAL: Download the spaCy NLP model
python -m spacy download en_core_web_trf

# 5. Run the backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Note:** The first time you run the backend, the `sentence-transformers` and `transformers` libraries will automatically download and cache their pre-trained models. This may take a few minutes.

### 2\. Frontend Setup

The frontend application runs on `http://localhost:5173`.

```bash
# 1. Open a new terminal
# (Leave the backend server running in its own terminal)
cd nlp_pdf_search/frontend

# 2. Install JavaScript dependencies
npm install

# 3. Run the frontend development server
npm run dev

# 4. Open the application in your browser
Your browser should automatically open to http://localhost:5173
```

-----

## 📈 Project Workflow

1.  **Upload:** On the homepage, select a PDF and click "Upload & Process".
2.  **Processing:** The app navigates you to the "Document Workspace". In the background, the backend starts two jobs:
      * **Immediate:** Fast text extraction, chunking, and embedding for search.
      * **Background:** The full, slow analysis (summaries, NER, etc.).
3.  **Search:** You can start using the **"Interactive Search"** tab immediately.
4.  **View Analysis:** Click the **"Full Analysis"** tab. The app will poll the backend until the background job is "complete" and then display the full report.
