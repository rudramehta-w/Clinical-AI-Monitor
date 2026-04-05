# 🧬 Clinical AI Monitor

An autonomous, end-to-end AI pipeline designed to fetch, evaluate, and synthesize medical research from PubMed. This system uses Google's Gemini AI to grade clinical relevance, maintains a local Retrieval-Augmented Generation (RAG) knowledge base, sends automated email digests, and features a live web dashboard.

## 🚀 Features

* **Automated Data Ingestion:** Scrapes live medical abstracts directly from the PubMed database.
* **LLM-as-a-Judge Evaluation:** Uses `gemini-2.5-flash` to extract study types, sample sizes, and generate a 1-10 clinical relevance score with an AI confidence metric.
* **Resilient Architecture:** Implements exponential backoff to gracefully handle cloud API rate limits (429 errors) and utilizes standard Python logging.
* **RAG Knowledge Base:** Converts medical abstracts into vector embeddings using `all-MiniLM-L6-v2` and FAISS for semantic search.
* **Interactive CLI Assistant:** A terminal-based chatbot that answers clinical questions strictly using context retrieved from the local vector database.
* **CI/CD Orchestration:** Utilizes GitHub Actions to automate the pipeline and send an HTML-formatted "Intelligence Briefing" email every morning.
* **Web Dashboard:** A Streamlit-powered UI for visualizing the database of evaluated research.

## 🛠️ Tech Stack

* **Language:** Python 3.12+ (Managed via `uv`)
* **LLM:** Google Gemini (`gemini-2.5-flash`)
* **Vector Database:** FAISS
* **Embedding Model:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
* **Relational Database:** SQLite (SQLAlchemy)
* **Frontend:** Streamlit
* **Automation:** GitHub Actions

## 📂 Project Structure

```
Clinical-Ai-Monitor/
├── .github/
│   └── workflows/
│       └── morning_digest.yml      # CI/CD automation schedule
├── data/                           # Local storage for databases
│   ├── clinical_monitor.db         # SQLite relational database
│   ├── clinical_vector_index.bin   # FAISS vector index
│   └── paper_ids.txt               # ID mapping for vector store
├── src/                            # Source code
    ├── main_pipeline.py            # Master orchestrator script
    ├── ai_agents.py                # Gemini evaluation & failure handling
    ├── database.py                 # SQLite schema & models
    ├── email_reporter.py           # Automated email formatting/sending
    ├── fetch_pubmed.py             # PubMed scraping logic
    ├── rag_assistant.py            # CLI chatbot for semantic search
    └── vector_store.py             # FAISS embedding and indexing

## ⚙️ Installation & Setup

Clone the repository and enter the directory:

```
git clone https://github.com/yourusername/Clinical-Ai-Monitor.git
cd Clinical-Ai-Monitor
```

Sync dependencies and create the virtual environment:

```
uv sync
```

Activate the virtual environment:

- **Windows:** `.venv\Scripts\activate`
- **Mac/Linux:** `source .venv/bin/activate`

Configure Environment Variables:
Create a `.env` file in the root directory and add your credentials:

```env
GEMINI_API_KEY=your_google_ai_studio_key
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
PUBMED_QUERY="Cardiovascular Health"
PUBMED_MAX_RESULTS=3
```

## 🖥️ Usage Guide

This project is designed to run completely autonomously in the cloud, but can also be tested locally.

### 1. Cloud Automation
The primary pipeline is fully automated via GitHub Actions (`.github/workflows/morning_digest.yml`).
- **Trigger**: Runs daily at 07:00 AM UTC.
- **Execution**: Spins up an Ubuntu runner, installs dependencies via `uv`, executes the LLM evaluation, and securely utilizes repository secrets to format and send the HTML email digest.
- **Zero-Touch**: Requires no local hardware to operate.

### 2. Local Execution
If you have cloned this repository and added your own `.env` file, you can manually test the pipeline:

```
# Run the scraping, evaluation, and email sequence
python src/main_pipeline.py
```

### 3. Medical RAG Assistant CLI
Chat with the FAISS vector database to query clinical papers:

```
python src/rag_assistant.py
```

## 🤝 Next Steps / Roadmap

- [ ] Refactor procedural scraper code into an Object-Oriented "Registry Pattern" to easily scale to dozens of medical journal sources.
- [ ] Transition from Cloud APIs to local open-source models (e.g., Llama 3 8B via Ollama) to remove external dependencies and respect HIPAA constraints.
- [ ] Expand the RAG pipeline to ingest full PDF documents instead of just abstracts.