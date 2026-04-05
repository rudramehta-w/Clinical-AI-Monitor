import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import requests
import xml.etree.ElementTree as ET
from database import SessionLocal, ClinicalPaper

# US Government PubMed API Endpoints
SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def fetch_latest_papers(query: str = "Cardiovascular disease", max_results: int = 5) -> None:
    logging.info(f"Searching live PubMed database for latest '{query}' papers...")
    
    # --- PHASE 1: SEARCH FOR IDs ---
    # We ask PubMed for the IDs of the {max_results} newest papers matching our query.
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "date" # This ensures we get the absolute newest research
    }
    
    response = requests.get(SEARCH_URL, params=search_params)
    data = response.json()
    paper_ids = data.get("esearchresult", {}).get("idlist", [])
    
    if not paper_ids:
        logging.warning("No papers found.")
        return
        
    logging.info(f"Found {len(paper_ids)} papers. Ripping abstracts...")
    
    # --- PHASE 2: FETCH THE FULL TEXT ---
    # Now we send those IDs back to PubMed to get the actual Titles and Abstracts
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(paper_ids),
        "retmode": "xml" # PubMed formats heavy text best in XML
    }
    
    fetch_resp = requests.get(FETCH_URL, params=fetch_params)
    
    # Parse the XML string into a readable Python object
    root = ET.fromstring(fetch_resp.content)
    
    # Open a connection to our SQLite database
    db = SessionLocal()
    saved_count = 0
    
    # --- PHASE 3: PARSE AND SAVE TO DATABASE ---
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")
        
        # Abstracts are sometimes split into paragraphs, so we join them
        abstract_texts = article.findall(".//AbstractText")
        abstract = " ".join([txt.text for txt in abstract_texts if txt.text])
        
        # Only save the paper if it actually has an abstract we can analyze later
        if pmid and title and abstract:
            
            # Check if this paper is already in our database
            existing_paper = db.query(ClinicalPaper).filter_by(pubmed_id=pmid).first()
            
            if not existing_paper:
                # Create a new row for our database
                new_paper = ClinicalPaper(
                    pubmed_id=pmid,
                    title=title,
                    abstract=abstract
                )
                db.add(new_paper)
                saved_count += 1
                logging.info(f"Saved to DB: {title[:60]}...")
    
    # Commit the changes to permanently save them to the disk
    db.commit()
    db.close()
    logging.info(f"Success! Pipeline ingested {saved_count} new papers.")

if __name__ == "__main__":
    # Let's test it by pulling the 5 newest cardiovascular papers
    fetch_latest_papers(query="Cardiovascular", max_results=5)