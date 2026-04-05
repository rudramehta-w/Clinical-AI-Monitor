import os
import faiss
import numpy as np
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from sentence_transformers import SentenceTransformer
from database import SessionLocal, ClinicalPaper

# Load a medical-friendly embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def update_vector_index() -> None:
    db = SessionLocal()
    papers = db.query(ClinicalPaper).all()
    
    if not papers:
        logging.info("No papers in database to index.")
        return

    logging.info(f"Encoding {len(papers)} papers into vectors...")
    
    texts = [f"{p.title} {p.abstract}" for p in papers]
    embeddings = model.encode(texts)
    
    dimension = embeddings.shape[1] 
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    # 1. UPDATED SAVE PATH
    faiss.write_index(index, "data/clinical_vector_index.bin")
    
    # 2. UPDATED TXT SAVE PATH
    with open("data/paper_ids.txt", "w") as f:
        for p in papers:
            f.write(f"{p.id}\n")
            
    logging.info("Vector index updated and saved to 'data/clinical_vector_index.bin'.")
    db.close()

def semantic_search(query: str, k: int = 3) -> list:
    """Finds the 'k' most relevant papers for any natural language question."""
    
    # 3. UPDATED PATH CHECK
    if not os.path.exists("data/clinical_vector_index.bin"):
        logging.warning("No index found. Run update_vector_index() first.")
        return []

    # 4. UPDATED READ PATH
    index = faiss.read_index("data/clinical_vector_index.bin")
    query_vector = model.encode([query])
    
    distances, indices = index.search(np.array(query_vector).astype('float32'), k)
    
    # 5. UPDATED TXT READ PATH
    with open("data/paper_ids.txt", "r") as f:
        all_ids = [line.strip() for line in f.readlines()]
    
    result_ids = [all_ids[i] for i in indices[0]]
    
    db = SessionLocal()
    results = db.query(ClinicalPaper).filter(ClinicalPaper.id.in_(result_ids)).all()
    db.close()
    
    return results

if __name__ == "__main__":
    update_vector_index()