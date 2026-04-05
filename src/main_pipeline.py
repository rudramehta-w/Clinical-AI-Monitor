import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

from database import init_db
from fetch_pubmed import fetch_latest_papers
from ai_agents import process_unsummarized_papers
from email_reporter import send_daily_digest
from vector_store import update_vector_index

def run() -> None:
    logging.info("Running Autonomous Clinical Pipeline...")
    init_db()
    
    # 1. Scraping (Ingest new data)
    query = os.getenv("PUBMED_QUERY", "Cardiovascular Health")
    limit = int(os.getenv("PUBMED_MAX_RESULTS", 5))
    fetch_latest_papers(query=query, max_results=limit)
    
    # 2. AI Processing (Extract factors and score)
    process_unsummarized_papers()
    
    # 3. Reporting (Send the email digest)
    send_daily_digest()
    
    # 4. Knowledge Base Update (Save to FAISS for RAG)
    logging.info("PHASE 4: UPDATING VECTOR KNOWLEDGE BASE")
    update_vector_index()

if __name__ == "__main__":
    run()